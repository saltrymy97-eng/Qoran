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
        "schedules": "الجداول الدراسية تُحدث بداية كل فصل دراسي. يرجى مراجعة شؤون الطلاب.",
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي، والامتحانات النهائية في نهاية الفصل.",
        "fees": "",
        "contacts": "للتواصل: هاتف الفرع أو زيارة مبنى الفرع بغيل باوزير - حضرموت. أوقات الدوام من الأحد إلى الخميس.",
        "majors": "التخصصات: القرآن وعلومه، الشريعة الإسلامية، الدراسات الإسلامية، إدارة أعمال، محاسبة، تقنية معلومات.",
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
SYSTEM_PROMPT = """أنت المساعد الذكي الرسمي لفرع جامعة القرآن الكريم والعلوم الإسلامية في غيل باوزير - حضرموت.

شخصيتك المهنية:
- ممثل رسمي للجامعة، تجمع بين الاحترافية والبساطة في الشرح
- خبير في شؤون الجامعة الأكاديمية والإدارية والتقنية
- تتحدث العربية الفصحى الميسرة بلمسة حضرمية لطيفة
- تشرح المعلومات بطريقة منظمة وواضحة وسهلة الفهم
- لا تستخدم الإيموجي مطلقاً
- لا تبدأ أي رد بتحية إذا سبق لك الرد في هذه المحادثة

قاعدة المعرفة:
{context}

أسلوب إجابتك:
- قدم المعلومات المطلوبة مباشرة
- إذا كانت المعلومة غير متوفرة: قل "عذراً، هذه المعلومة غير متوفرة حالياً. يرجى التواصل مع إدارة الفرع."
- إذا كان السؤال خارج نطاق الجامعة: قل "أنا مختص بشؤون الجامعة فقط."
- عند الشكر: رد باختصار "العفو"
- عند السلام: رد بسلام أفضل منه مرة واحدة فقط"""

# ==========================================
# 4. إدارة السجل والإحصائيات
# ==========================================
def load_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_logs(logs):
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def log_question(question, category, response_status="success"):
    logs = load_logs()
    now = datetime.now()
    logs.append({
        "question": question.strip(),
        "category": category,
        "timestamp": now.isoformat(),
        "hour": now.hour,
        "response_status": response_status
    })
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_logs(logs)

def get_stats():
    logs = load_logs()
    if not logs:
        return {"total": 0, "today": 0, "top_questions": [], "categories": {}}
    
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
    
    # 🔥 اختيار البيانات المناسبة للسؤال فقط
    if category and category in data and category != "last_updated" and data[category]:
        context = data[category]
    else:
        context = data.get("info", "")
    
    system_prompt = SYSTEM_PROMPT.format(context=context)
    
    messages = [{"role": "system", "content": system_prompt}]
    
    if chat_history:
        for msg in chat_history[-4:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": question})
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5,
            max_tokens=600
        )
        ai_response = response.choices[0].message.content
        
        if any(phrase in ai_response for phrase in ["لم أجد", "لا تتوفر", "غير متوفرة"]):
            log_question(question, category or "info", "not_found")
        else:
            log_question(question, category or "info", "success")
        
        return ai_response
        
    except Exception as e:
        log_question(question, category or "info", "error")
        return "عذراً، حدث خطأ تقني. يرجى المحاولة مرة أخرى."

# ==========================================
# 6. التصنيف الذكي
# ==========================================
def smart_classify(question):
    """تصنيف السؤال إلى فئة مناسبة"""
    q = question.strip().lower()

    if any(w in q for w in ["رسوم", "دفع", "تسديد", "قسط", "مالية", "تكلفة", "سعر"]):
        return "fees"
    if any(w in q for w in ["تواصل", "اتصال", "هاتف", "عنوان", "موقع", "بريد", "رقم", "جوال"]):
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
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "صباح الخير"
    elif 12 <= hour < 17:
        return "مساء الخير"
    else:
        return "مساء الخير"

def get_welcome_message():
    greeting = get_greeting()
    return f"{greeting}، أهلاً وسهلاً بك في المساعد الذكي لجامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير. كيف أقدر أخدمك؟"
