import os
import json
import datetime
import sqlite3
from collections import Counter
from groq import Groq

# إعداد المتغيرات والمسارات
DATA_FILE = "data.json"
DB_FILE = "logs.db"

# تهيئة عميل Groq كمتغير عام لتقليل وقت الاستجابة مع كل سؤال
API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=API_KEY) if API_KEY else None

def setup_database():
    """تهيئة قاعدة بيانات SQLite لتسجيل الأسئلة والإحصائيات بأمان"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            category TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# استدعاء دالة تهيئة قاعدة البيانات عند تشغيل السكربت
setup_database()

def load_data():
    """تحميل بيانات الجامعة من الملف، أو إرجاع بيانات افتراضية متطورة إذا لم يوجد"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            pass
    
    default_data = {
        "majors": "التخصصات المتاحة: القرآن وعلومه، الشريعة الإسلامية، الدراسات الإسلامية، إدارة أعمال، محاسبة، تقنية معلومات. مدة الدراسة 4 سنوات للبكالوريوس.",
        "fees": "يمكن تسديد الرسوم الدراسية عبر البنك أو الدفع المباشر في الإدارة المالية. تتوفر خيارات التقسيط للطلاب المستحقين.",
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي، والامتحانات النهائية في نهاية الفصل. تعلن النتائج بعد أسبوعين من آخر امتحان.",
        "schedules": "الجداول الدراسية تُحدث بداية كل فصل دراسي. يرجى مراجعة شؤون الطلاب للاطلاع على جدول المحاضرات والمواعيد.",
        "contacts": "للتواصل: هاتف الفرع أو زيارة مبنى الفرع بغيل باوزير - حضرموت. أوقات الدوام الرسمي من الأحد إلى الخميس.",
        "info": "جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير، مؤسسة تعليمية رائدة تجمع بين العلوم الشرعية والإدارية والتقنية."
    }
    save_data(default_data)
    return default_data

def save_data(data):
    """حفظ بيانات الجامعة في الملف"""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def smart_classify(question):
    """تصنيف السؤال وإرجاع فئة واحدة فقط (للتوافق مع app.py)"""
    q = question.lower()
    
    # التخصصات + الرسوم = majors
    if any(w in q for w in ["تخصص", "تخصصات", "قسم", "كلية"]) and any(w in q for w in ["رسوم", "سعر", "تكلفة", "تكاليف"]):
        return "majors"
    
    if any(w in q for w in ["رسوم", "تكاليف", "مالية", "دفع", "قسط", "سداد", "منحة", "سعر"]):
        return "fees"
    if any(w in q for w in ["امتحان", "اختبار", "نتيجة", "درجات", "معدل", "نجاح", "رسوب"]):
        return "exams"
    if any(w in q for w in ["جدول", "مواعيد", "وقت", "محاضرة", "دوام", "حضور", "غياب", "مدرس"]):
        return "schedules"
    if any(w in q for w in ["تواصل", "رقم", "اتصال", "ايميل", "بريد", "عنوان", "موقع", "هاتف", "جوال"]):
        return "contacts"
    if any(w in q for w in ["تخصص", "قسم", "كلية", "بكالوريوس", "ماجستير", "دراسة"]):
        return "majors"
    
    return "info"

def log_question(question, category):
    """تسجيل السؤال والفئة في قاعدة بيانات SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (question, category, timestamp) VALUES (?, ?, ?)",
        (question, category, datetime.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def ask_ai(question, category=None, chat_history=None):
    """إرسال السؤال إلى Groq API للحصول على إجابة مصاغة بناءً على السياق"""
    if chat_history is None:
        chat_history = []
    
    # تحميل البيانات وجلب سياق الفئة المناسبة
    data = load_data()
    context = data.get(category, data.get("info", "")) if category else data.get("info", "")
    
    # تسجيل السؤال
    log_question(question, category or "info")
    
    # بناء الـ Prompt بشكل دقيق للحد من الهلوسة
    system_prompt = (
        "أنت مساعد رسمي ومهذب لجامعة القرآن الكريم والعلوم الإسلامية فرع غيل باوزير - حضرموت. "
        "أجب على سؤال الطالب باستخدام المعلومات المتوفرة فقط أدناه. "
        "إذا كانت المعلومات غير كافية للإجابة بشكل دقيق، قل نصاً: 'عذراً، هذه المعلومة غير متوفرة لدي حالياً، يرجى التواصل مع شؤون الطلاب'. "
        "ممنوع اختلاق أو تخمين أي أسعار أو تواريخ أو معلومات من خارج السياق.\n\n"
        f"المعلومات المتوفرة للاستناد عليها: {context[:1000]}"
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages.extend(chat_history[-4:])
    messages.append({"role": "user", "content": question})
    
    if not client:
        return "عذراً، لا يمكن الاتصال بالمساعد الذكي حالياً."
        
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=400
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return "عذراً، حدث خطأ أثناء الاتصال بالنظام. يرجى المحاولة مرة أخرى لاحقاً."

def get_stats():
    """إرجاع إحصائيات متوافقة مع app.py"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM logs")
        total = cursor.fetchone()[0]
        
        today_str = datetime.datetime.now().date().isoformat()
        cursor.execute("SELECT COUNT(*) FROM logs WHERE timestamp LIKE ?", (f"{today_str}%",))
        today = cursor.fetchone()[0]
        
        cursor.execute("SELECT question FROM logs")
        all_questions = [row[0] for row in cursor.fetchall()]
        most_common = [{"question": q, "count": c} for q, c in Counter(all_questions).most_common(10)]
        
        cursor.execute("SELECT category FROM logs")
        all_categories = [row[0] for row in cursor.fetchall()]
        categories = dict(Counter(all_categories))
        
    except sqlite3.Error as e:
        return {"total": 0, "today": 0, "top_questions": [], "categories": {}}
    finally:
        conn.close()
        
    return {
        "total": total,
        "today": today,
        "top_questions": most_common,
        "categories": categories
    }

def get_greeting():
    """إرجاع رسالة ترحيبية تتناسب مع الوقت الحالي"""
    current_hour = datetime.datetime.now().hour
    
    if 5 <= current_hour < 12:
        return "صباح الخير"
    elif 12 <= current_hour < 17:
        return "مساء الخير"
    else:
        return "مساء الخير"

def get_welcome_message():
    """رسالة ترحيبية أولى فقط"""
    greeting = get_greeting()
    return f"{greeting}، أهلاً وسهلاً بك في المساعد الذكي لجامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير. كيف أقدر أخدمك؟"
