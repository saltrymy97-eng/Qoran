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
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي.",
        "fees": "يمكن تسديد الرسوم عبر البنك أو الدفع المباشر في الإدارة المالية.",
        "contacts": "للتواصل: هاتف الفرع أو زيارة مبنى الفرع بغيل باوزير - حضرموت.",
        "majors": "التخصصات: القرآن وعلومه، الشريعة، الدراسات الإسلامية، إدارة أعمال، محاسبة، تقنية معلومات.",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def save_data(data):
    """حفظ بيانات الجامعة"""
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي (احترافية)
# ==========================================
SYSTEM_PROMPT = """أنت المساعد الذكي الرسمي لفرع جامعة القرآن الكريم والعلوم الإسلامية في غيل باوزير - حضرموت.

هويتك:
- ممثل رسمي للجامعة، محترم، دقيق، ومهذب
- خبير في شؤون الجامعة الأكاديمية والإدارية والتقنية
- تتحدث العربية الفصحى الميسرة بلمسة حضرمية لطيفة
- مختصر جداً ومفيد (لا تتجاوز 3-4 جمل في الرد)
- لا تستخدم الإيموجي إطلاقاً

قاعدة المعرفة (آخر تحديث: {last_updated}):
{context}

قواعد ملزمة:
1. أجب فقط من المعلومات المتاحة أعلاه
2. إذا لم تجد إجابة: "عذراً، هذه المعلومة غير متوفرة حالياً. يرجى التواصل مع إدارة الفرع."
3. إذا كان السؤال خارج نطاق الجامعة: "أنا مختص بشؤون الجامعة فقط. هل لديك استفسار عن الدراسة؟"
4. عند الشكر، رد باختصار: "العفو" أو "في خدمتكم"
5. عند السلام، رد بسلام أفضل منه - مرة واحدة فقط
6. لا تبدأ أي رد بعبارة ترحيبية إذا سبق لك الرد في هذه المحادثة
7. لا تكرر التحية أبداً، حتى لو كانت أول رسالة من المستخدم"""

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
        "hour": now.hour,
        "day_of_week": now.strftime("%A"),
        "month": now.strftime("%Y-%m"),
        "week": now.isocalendar()[1],
        "response_status": response_status
    })
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_logs(logs)

def normalize_question(question):
    """توحيد شكل السؤال للمقارنة"""
    q = question.strip().lower()
    q = re.sub(r'[،,\.\!\?؟\:\;\-\(\)\[\]\{\}]', '', q)
    q = re.sub(r'[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED]', '', q)
    q = q.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    q = q.replace('ة', 'ه').replace('ى', 'ي')
    return q

def get_stats():
    """إرجاع إحصائيات متقدمة"""
    logs = load_logs()
    
    if not logs:
        return {
            "total": 0, "today": 0, "this_week": 0, "this_month": 0,
            "top_questions": [], "categories": {}, "peak_hours": {},
            "unanswered_questions": [], "daily_trend": []
        }
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_month = now.strftime("%Y-%m")
    current_week = now.isocalendar()[1]
    current_year = now.year
    
    today_count = 0
    this_week_count = 0
    this_month_count = 0
    
    question_counts = {}
    category_counts = {}
    hour_counts = {}
    daily_counts = {}
    unanswered = []
    
    for log in logs:
        q = log["question"].strip()
        q_normalized = normalize_question(q)
        question_counts[q_normalized] = question_counts.get(q_normalized, 0) + 1
        
        cat = log.get("category", "info")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        hour = log.get("hour", 0)
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if log.get("response_status") == "not_found":
            unanswered.append(q)
        
        try:
            log_date = datetime.fromisoformat(log["timestamp"])
            log_date_str = log_date.strftime("%Y-%m-%d")
            
            if log_date_str == today_str:
                today_count += 1
            if log_date.strftime("%Y-%m") == current_month:
                this_month_count += 1
            if log_date.isocalendar()[1] == current_week and log_date.year == current_year:
                this_week_count += 1
            if log_date_str not in daily_counts:
                daily_counts[log_date_str] = 0
            daily_counts[log_date_str] += 1
        except:
            pass
    
    sorted_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
    top_questions = [{"question": q, "count": c} for q, c in sorted_questions[:10]]
    peak_hours = dict(sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5])
    unique_unanswered = list(dict.fromkeys(unanswered))[:10]
    
    last_7_days = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        last_7_days.append({"date": day, "count": daily_counts.get(day, 0)})
    
    return {
        "total": len(logs),
        "today": today_count,
        "this_week": this_week_count,
        "this_month": this_month_count,
        "top_questions": top_questions,
        "categories": category_counts,
        "peak_hours": peak_hours,
        "unanswered_questions": unique_unanswered,
        "daily_trend": last_7_days
    }

# ==========================================
# 5. الذكاء الاصطناعي
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    """إرسال سؤال إلى Groq مع تاريخ المحادثة"""
    data = load_data()
    
    if category and category in data and category != "last_updated":
        context = data[category]
    else:
        context = build_full_context(data)
    
    last_updated = data.get("last_updated", "غير محدد")
    system_prompt = SYSTEM_PROMPT.format(
        context=context[:3500],
        last_updated=last_updated
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    if not chat_history or (chat_history and chat_history[-1]["content"] != question):
        messages.append({"role": "user", "content": question})
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=600
        )
        ai_response = response.choices[0].message.content
        
        if any(phrase in ai_response for phrase in ["لم أجد", "لا تتوفر", "غير متوفرة", "غير متاح"]):
            log_question(question, category or "info", "not_found")
        else:
            log_question(question, category or "info", "success")
        
        return ai_response
        
    except Exception as e:
        log_question(question, category or "info", "error")
        return generate_fallback_response(question, category, data)

def build_full_context(data):
    """بناء سياق كامل ومنظم"""
    parts = []
    if data.get('info'):
        parts.append(f"معلومات عامة:\n{data['info']}")
    if data.get('majors'):
        parts.append(f"التخصصات:\n{data['majors']}")
    if data.get('schedules'):
        parts.append(f"الجداول:\n{data['schedules']}")
    if data.get('exams'):
        parts.append(f"الامتحانات:\n{data['exams']}")
    if data.get('fees'):
        parts.append(f"الرسوم:\n{data['fees']}")
    if data.get('contacts'):
        parts.append(f"جهات الاتصال:\n{data['contacts']}")
    return "\n\n".join(parts) if parts else "لا توجد بيانات محددة بعد."

def generate_fallback_response(question, category, data):
    """رد احتياطي عند فشل الاتصال"""
    greetings = ["سلام", "مرحبا", "هلا", "أهلا", "صباح", "مساء"]
    if any(w in question for w in greetings):
        return f"{get_greeting()}، كيف أقدر أخدمك؟"
    
    thanks = ["شكرا", "شكراً", "مشكور", "جزاك", "تسلم"]
    if any(w in question for w in thanks):
        return "العفو، في خدمتكم."
    
    if category and category in data and category != "last_updated":
        context = data[category]
        if context:
            return f"المعلومات المتاحة:\n\n{context}\n\n(رد من قاعدة البيانات المحلية)"
    
    context = data.get("info", "")
    if context:
        return f"{context}\n\n(رد من قاعدة البيانات المحلية)"
    
    return "عذراً، الخدمة متوقفة مؤقتاً. يرجى التواصل مع إدارة الفرع."

# ==========================================
# 6. التصنيف الذكي
# ==========================================
def smart_classify(question):
    """تصنيف السؤال إلى فئة مناسبة"""
    q = question.strip()
    q_lower = q.lower()
    
    keywords = {
        "schedules": [
            "جدول", "جداول", "محاضرات", "محاضره", "مواد", "ماده", "مستوى",
            "دوام", "حضور", "غياب", "أستاذ", "دكتور", "مدرس", "معلم",
            "حلقة", "حلقات", "قرآن", "تفسير", "فقه", "حديث", "نحو", "بلاغة",
            "أصول", "عقيدة", "سيرة", "تلاوة", "تجويد", "دعوة", "أدب",
            "محاسبة", "إدارة", "تقنية", "نظم", "حاسوب", "برمجة", "تدريب",
            "عملي", "تطبيق", "ساعات", "معتمدة", "تراكمي", "خطة", "دراسية",
            "مجموعة", "شعبة", "قاعة", "معمل", "مختبر", "مكتبة"
        ],
        "exams": [
            "امتحان", "امتحانات", "اختبار", "اختبارات", "نصفي", "نهائي",
            "نتيجة", "نتايج", "درجة", "درجات", "نجاح", "رسوب", "معدل",
            "تقدير", "مراجعة", "تصحيح", "ورقة", "مراقب", "لجنة",
            "تقييم", "أعمال سنة", "شفوي", "تحريري", "عملي"
        ],
        "fees": [
            "رسوم", "رسومات", "فلوس", "مبلغ", "دفع", "تسديد", "قسط",
            "أقساط", "مالية", "مصاريف", "حوالة", "بنك", "فاتورة", "سعر",
            "تخفيض", "خصم", "منحة", "إعفاء", "مجاني", "تكلفة",
            "ريال", "دولار", "عملة", "حساب", "إيداع", "تحويل"
        ],
        "contacts": [
            "اتصال", "رقم", "هاتف", "جوال", "موقع", "عنوان", "وين", "أين",
            "فرع", "إدارة", "شؤون", "مكتب", "بريد", "إيميل", "واتساب",
            "ساعات العمل", "مواعيد", "دوام", "مفتوح", "مغلق",
            "خرائط", "موقع", "شارع", "حارة", "جوار", "بجانب", "قريب"
        ],
        "majors": [
            "تخصص", "تخصصات", "قسم", "أقسام", "شعبة", "شعب", "كلية",
            "دراسة", "منهج", "مقرر", "مسار", "محاسبة", "إدارة أعمال",
            "تقنية معلومات", "نظم معلومات", "بكالوريوس", "دبلوم", "تمهيدي",
            "تسجيل", "قبول", "شروط", "متطلبات", "مدة", "سنوات", "فصل"
        ]
    }
    
    for category, words in keywords.items():
        sorted_words = sorted(words, key=len, reverse=True)
        for word in sorted_words:
            if word in q_lower or word in q:
                return category
    
    greetings = ["سلام", "مرحبا", "هلا", "أهلا", "السلام", "صباح", "مساء", "حياك", "ياهلا"]
    if any(w in q_lower for w in greetings):
        return "info"
    
    thanks = ["شكرا", "شكراً", "مشكور", "جزاك", "الله يعطيك", "تسلم", "ما قصرت", "يعطيك"]
    if any(w in q_lower for w in thanks):
        return "info"
    
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
