"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - خدمات الذكاء الاصطناعي والإحصائيات          ║
║  المطور: سالم التريمي                                       ║
║  الإصدار: 6.1 (نظام القالب النصي الثابت - أداء محسن)       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import datetime
from groq import Groq

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
DATA_FILE = "data.json"
LOGS_FILE = "logs.json"

def get_client():
    key = os.getenv("GROQ_API_KEY")
    if key:
        try:
            return Groq(api_key=key)
        except Exception:
            pass
    return None

# ==========================================
# 2. إدارة البيانات (بدون تحويل للتخصصات)
# ==========================================
def load_data():
    """تحميل بيانات الجامعة من data.json كما هي."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass

    return {
        "info": "", "schedules": "", "exams": "", "fees": "", "contacts": "", "majors": ""
    }

def save_data(data):
    """حفظ بيانات الجامعة"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي (مُحسَّنة لتجنب إظهار القالب)
# ==========================================
SYSTEM_PROMPT = """أنت موظف استقبال محترف في جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير بحضرموت.
أنت خبير في شؤون الجامعة، تجيب بدقة ووضوح. تتحدث العربية الفصحى الميسرة بلمسة حضرمية لطيفة.

[المعلومات المتاحة للجمهور]
{context}

[تعليمات عامة وملزمة]
- لا تستخدم الإيموجي.
- لا تكرر التحية بعد الرد الأول.
- أجب مباشرة دون استخدام عبارات مثل "بناءً على المعلومات المتاحة".
- كن موجزاً ومفيداً. لا تذكر معلومات لا علاقة لها بالسؤال.
- إذا كانت المعلومات فارغة أو لا تحتوي على إجابة السؤال، قل بالضبط: 'عذراً، لا تتوفر لدي بيانات حالياً. يرجى التواصل مع إدارة الجامعة.'
- لا تخترع أي معلومات. لا تخمن. لا تضف شيئاً من عندك.
- لا تكرر أبداً هيكل القالب أو الرموز مثل [INFO]، [SCHEDULES]، إلخ. هذه وصف للنظام وليست معلومات للطالب.

[آلية الرد حسب نوع السؤال]

1. سؤال عن جميع التخصصات:
   - قدم قائمة بأسماء التخصصات فقط، بدون تفاصيل.

2. سؤال عن تفاصيل تخصص محدد:
   - إذا كان السؤال عن رسومه: اذكر الرقم فقط.
   - إذا كان السؤال عن مدته: اذكر المدة فقط.
   - إذا كان السؤال عن وصفه: قدم وصفاً مختصراً (2-3 جمل).

3. أسئلة عن الرسوم، الامتحانات، الجداول، أو التواصل:
   - استخرج المعلومة المطلوبة من القسم المناسب وأجب بها فقط.

4. سؤال خارج نطاق الجامعة:
   - قل: "أنا مختص بشؤون الجامعة فقط. كيف يمكنني مساعدتك في أمور الدراسة؟"

5. شكر أو تحية:
   - رد باختصار: "العفو"، "وعليكم السلام"، "في خدمتكم". لا تبدأ الرد بتحية جديدة."""

# ==========================================
# 4. الذكاء الاصطناعي
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    if chat_history is None:
        chat_history = []

    data = load_data()
    
    # بناء السياق: نأخذ الفئة المطلوبة، أو ندمج كل الحقول المتاحة
    if category and category in data and data[category]:
        context = data[category]
    else:
        context = "\n\n".join([f"{k}: {v}" for k, v in data.items() if v])
    
    if not context or not context.strip():
        return "عذراً، لا تتوفر لدي بيانات حالياً. يرجى التواصل مع إدارة الجامعة."

    system_prompt = SYSTEM_PROMPT.format(context=context[:2000])
    messages = [{"role": "system", "content": system_prompt}]
    
    if chat_history:
        messages.extend(chat_history[-4:])
        
    messages.append({"role": "user", "content": question})

    client = get_client()
    if not client:
        return "⚠️ النظام يعمل الآن في وضع عدم الاتصال. تأكد من إعداد مفتاح GROQ_API_KEY."

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_tokens=400
        )
        answer = response.choices[0].message.content
        log_question(question, category or "info", source="groq")
        return answer
    except Exception as e:
        log_question(question, category or "info", source="error")
        return f"⚠️ عذراً، حدث خطأ تقني: {str(e)}"

# ==========================================
# 5. التصنيف الذكي
# ==========================================
def smart_classify(question):
    q = question.lower()
    
    if any(w in q for w in ["تخصص", "قسم", "كلية"]) and any(w in q for w in ["رسوم", "سعر", "تكلفة", "تكاليف"]):
        return "majors"
    
    if any(w in q for w in ["رسوم", "تكاليف", "مالية", "دفع", "قسط", "سداد", "منحة", "سعر"]):
        return "fees"
    if any(w in q for w in ["امتحان", "اختبار", "نتيجة", "درجات", "معدل", "نجاح", "رسوب"]):
        return "exams"
    if any(w in q for w in ["جدول", "جداول", "جدوال", "مواعيد", "محاضرة", "دوام", "حضور", "غياب", "مدرس"]):
        return "schedules"
    if any(w in q for w in ["تواصل", "رقم", "اتصال", "ايميل", "بريد", "عنوان", "موقع", "هاتف", "جوال", "أين", "وين"]):
        return "contacts"
    if any(w in q for w in ["تخصص", "قسم", "كلية", "بكالوريوس", "ماجستير", "دراسة"]):
        return "majors"
    
    return "info"

# ==========================================
# 6. السجل والإحصائيات
# ==========================================
def load_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_logs(logs):
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def log_question(question, category, source="groq"):
    logs = load_logs()
    logs.append({
        "question": question.strip(),
        "category": category,
        "source": source,
        "timestamp": datetime.datetime.now().isoformat()
    })
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_logs(logs)

def get_stats():
    logs = load_logs()
    
    if not logs:
        return {
            "total": 0, "today": 0, "top_questions": [], "categories": {}
        }

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
# 7. دوال الترحيب والمساعدة
# ==========================================
def get_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "صباح الخير"
    elif 12 <= hour < 17:
        return "مساء الخير"
    else:
        return "مساء الخير"

def get_welcome_message():
    greeting = get_greeting()
    return f"{greeting}، أهلاً وسهلاً بك في المساعد الذكي لجامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير. كيف أقدر أخدمك؟"
