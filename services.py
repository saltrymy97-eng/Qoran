"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - خدمات الذكاء الاصطناعي والإحصائيات          ║
║  المطور: سالم التريمي                                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import datetime
from groq import Groq

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

DATA_FILE = "data.json"
LOGS_FILE = "logs.json"

# ==========================================
# 2. إدارة البيانات
# ==========================================
def load_data():
    """تحميل بيانات الجامعة من الملف، أو إرجاع بيانات افتراضية إذا لم يوجد"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    
    default_data = {
        "info": "جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير، مؤسسة تعليمية رائدة تجمع بين العلوم الشرعية والإدارية والتقنية.",
        "schedules": "الجداول الدراسية تُحدث بداية كل فصل دراسي. يرجى مراجعة شؤون الطلاب للاطلاع على جدول المحاضرات والمواعيد.",
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي، والامتحانات النهائية في نهاية الفصل. تعلن النتائج بعد أسبوعين من آخر امتحان.",
        "fees": "يمكن تسديد الرسوم الدراسية عبر البنك أو الدفع المباشر في الإدارة المالية. تتوفر خيارات التقسيط للطلاب المستحقين.",
        "contacts": "للتواصل: هاتف الفرع أو زيارة مبنى الفرع بغيل باوزير - حضرموت. أوقات الدوام الرسمي من الأحد إلى الخميس.",
        "majors": "التخصصات المتاحة: القرآن وعلومه، الشريعة الإسلامية، الدراسات الإسلامية، إدارة أعمال، محاسبة، تقنية معلومات. مدة الدراسة 4 سنوات للبكالوريوس.",
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_data(default_data)
    return default_data

def save_data(data):
    """حفظ بيانات الجامعة في الملف"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي
# ==========================================
SYSTEM_PROMPT = (
    "أنت مساعد رسمي ومهذب لجامعة القرآن الكريم والعلوم الإسلامية فرع غيل باوزير - حضرموت. "
    "أجب على سؤال الطالب باستخدام المعلومات المتوفرة فقط أدناه. "
    "إذا كانت المعلومات غير كافية للإجابة بشكل دقيق، قل نصاً: 'عذراً، هذه المعلومة غير متوفرة لدي حالياً، يرجى التواصل مع شؤون الطلاب'. "
    "ممنوع اختلاق أو تخمين أي أسعار أو تواريخ أو معلومات من خارج السياق.\n\n"
    "المعلومات المتوفرة للاستناد عليها:\n{context}"
)

# ==========================================
# 4. إدارة السجل والإحصائيات
# ==========================================
def load_logs():
    """تحميل سجل الأسئلة"""
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_logs(logs):
    """حفظ سجل الأسئلة"""
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def log_question(question, category):
    """تسجيل سؤال في السجل"""
    logs = load_logs()
    logs.append({
        "question": question.strip(),
        "category": category,
        "timestamp": datetime.datetime.now().isoformat()
    })
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_logs(logs)

def get_stats():
    """إرجاع إحصائيات الأسئلة"""
    logs = load_logs()
    
    if not logs:
        return {"total": 0, "today": 0, "top_questions": [], "categories": {}}
    
    today_str = datetime.datetime.now().date().isoformat()
    today_count = sum(1 for log in logs if log["timestamp"].startswith(today_str))
    
    question_counts = {}
    category_counts = {}
    
    for log in logs:
        q = log["question"].strip()
        question_counts[q] = question_counts.get(q, 0) + 1
        cat = log.get("category", "info")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    sorted_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
    top_questions = [{"question": q, "count": c} for q, c in sorted_questions[:10]]
    
    return {
        "total": len(logs),
        "today": today_count,
        "top_questions": top_questions,
        "categories": category_counts
    }

# ==========================================
# 5. الذكاء الاصطناعي
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    """إرسال السؤال إلى Groq API مع سياق الفئة المناسبة"""
    if chat_history is None:
        chat_history = []
    
    data = load_data()
    context = data.get(category, data.get("info", "")) if category else data.get("info", "")
    
    log_question(question, category or "info")
    
    system_prompt = SYSTEM_PROMPT.format(context=context[:1000])
    
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

# ==========================================
# 6. التصنيف الذكي
# ==========================================
def smart_classify(question):
    """تصنيف السؤال إلى فئة واحدة مناسبة"""
    q = question.lower()
    
    # التخصصات + الرسوم = majors (أولوية)
    if any(w in q for w in ["تخصص", "تخصصات", "قسم", "كلية"]) and any(w in q for w in ["رسوم", "سعر", "تكلفة", "تكاليف"]):
        return "majors"
    
    # الكلمات المالية فقط = fees
    if any(w in q for w in ["رسوم", "تكاليف", "مالية", "دفع", "قسط", "سداد", "منحة", "سعر"]):
        return "fees"
    
    # الامتحانات
    if any(w in q for w in ["امتحان", "اختبار", "نتيجة", "درجات", "معدل", "نجاح", "رسوب"]):
        return "exams"
    
    # الجداول
    if any(w in q for w in ["جدول", "جداول", "جدوال", "مواعيد", "محاضرة", "دوام", "حضور", "غياب", "مدرس"]):
        return "schedules"
    
    # التواصل
    if any(w in q for w in ["تواصل", "رقم", "اتصال", "ايميل", "بريد", "عنوان", "موقع", "هاتف", "جوال", "أين", "وين"]):
        return "contacts"
    
    # التخصصات فقط
    if any(w in q for w in ["تخصص", "قسم", "كلية", "بكالوريوس", "ماجستير", "دراسة"]):
        return "majors"
    
    return "info"

# ==========================================
# 7. دوال الترحيب والمساعدة
# ==========================================
def get_greeting():
    """رسالة ترحيبية حسب الوقت"""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "صباح الخير"
    elif 12 <= hour < 17:
        return "مساء الخير"
    else:
        return "مساء الخير"

def get_welcome_message():
    """رسالة ترحيبية أولى فقط"""
    greeting = get_greeting()
    return f"{greeting}، أهلاً وسهلاً بك في المساعد الذكي لجامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير. كيف أقدر أخدمك؟"
