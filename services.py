"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - خدمات الذكاء الاصطناعي والإحصائيات          ║
║  المطور: سالم التريمي                                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import os
import re
from datetime import datetime, timedelta
from groq import Groq

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_مفتاحك_هنا")
groq_client = Groq(api_key=GROQ_API_KEY)

DATA_FILE = "data.json"
LOGS_FILE = "logs.json"

# ==========================================
# 2. إدارة البيانات
# ==========================================
def load_data():
    """تحميل بيانات الجامعة"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "last_updated" not in data:
                data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            return data
    return {
        "info": "جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير، مؤسسة تعليمية رائدة تجمع بين العلوم الشرعية والإدارية والتقنية.",
        "schedules": "الجداول الدراسية تُحدث بداية كل فصل دراسي. يرجى مراجعة شؤون الطلاب للاطلاع على جدول المحاضرات والمواعيد.",
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي، والامتحانات النهائية في نهاية الفصل. تعلن النتائج بعد أسبوعين من آخر امتحان.",
        "fees": "يمكن تسديد الرسوم الدراسية عبر البنك أو الدفع المباشر في الإدارة المالية. تتوفر خيارات التقسيط للطلاب المستحقين.",
        "contacts": "للتواصل: هاتف الفرع أو زيارة مبنى الفرع بغيل باوزير - حضرموت. أوقات الدوام الرسمي من الأحد إلى الخميس.",
        "majors": "التخصصات المتاحة: القرآن وعلومه، الشريعة الإسلامية، الدراسات الإسلامية، إدارة أعمال، محاسبة، تقنية معلومات. مدة الدراسة 4 سنوات للبكالوريوس.",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def save_data(data):
    """حفظ بيانات الجامعة"""
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي
# ==========================================
SYSTEM_PROMPT = """أنت مساعد رسمي لجامعة القرآن الكريم والعلوم الإسلامية فرع غيل باوزير - حضرموت.
أعد صياغة المعلومات التالية للإجابة على سؤال المستخدم بأسلوب مهذب ومختصر:
{context}"""

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

def log_question(question, category, response_status="success"):
    """تسجيل سؤال مع بيانات إضافية"""
    logs = load_logs()
    now = datetime.now()
    logs.append({
        "question": question.strip(),
        "category": category,
        "timestamp": now.isoformat(),
        "response_status": response_status
    })
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_logs(logs)

def get_stats():
    """إرجاع إحصائيات متقدمة"""
    logs = load_logs()
    
    if not logs:
        return {
            "total": 0, "today": 0,
            "top_questions": [], "categories": {}
        }
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    today_count = 0
    question_counts = {}
    category_counts = {}
    
    for log in logs:
        q = log["question"].strip()
        question_counts[q] = question_counts.get(q, 0) + 1
        
        cat = log.get("category", "info")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if log["timestamp"].startswith(today_str):
            today_count += 1
    
    sorted_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
    top_questions = [{"question": q, "count": c} for q, c in sorted_questions[:10]]
    
    return {
        "total": len(logs),
        "today": today_count,
        "top_questions": top_questions,
        "categories": category_counts
    }

# ==========================================
# 5. الذكاء الاصطناعي (يرسل بيانات الأيقونة المناسبة فقط)
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    """إرسال سؤال إلى Groq مع بيانات الأيقونة المناسبة فقط"""
    data = load_data()
    
    # 🔥 نأخذ بيانات الأيقونة المناسبة فقط
    if category and category in data and category != "last_updated":
        context = data[category]
    else:
        context = data.get("info", "")
    
    if not context.strip():
        context = data.get("info", "")
    
    # إرسال الطلب إلى Groq
    try:
        system_prompt = SYSTEM_PROMPT.format(context=context[:1000])
        messages = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "user", "content": question})
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5,
            max_tokens=400
        )
        ai_response = response.choices[0].message.content
        log_question(question, category or "info", "success")
        return ai_response
        
    except Exception as e:
        # إذا فشل Groq، نرجع بيانات الأيقونة مباشرة
        log_question(question, category or "info", "success")
        return context

# ==========================================
# 6. التصنيف الذكي
# ==========================================
def smart_classify(question):
    """تصنيف السؤال إلى فئة مناسبة"""
    q = question.strip().lower()

    if any(w in q for w in ["رسوم", "دفع", "تسديد", "قسط", "مالية", "تكلفة", "سعر"]):
        return "fees"
    if any(w in q for w in ["تواصل", "اتصال", "هاتف", "عنوان", "موقع", "بريد", "رقم", "جوال", "أين", "وين"]):
        return "contacts"
    if any(w in q for w in ["امتحان", "اختبار", "نتيجة", "نجاح", "رسوب", "معدل"]):
        return "exams"
    if any(w in q for w in ["جدول", "محاضرات", "دوام", "حضور", "غياب", "مدرس"]):
        return "schedules"
    if any(w in q for w in ["تخصص", "قسم", "كلية", "بكالوريوس", "دبلوم"]):
        return "majors"

    return "info"

# ==========================================
# 7. دوال الترحيب والمساعدة
# ==========================================
def get_greeting():
    """رسالة ترحيبية حسب الوقت"""
    hour = datetime.now().hour
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
