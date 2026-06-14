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
        "info": "جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير، مؤسسة تعليمية رائدة تجمع بين العلوم الشرعية والإدارية والتقنية. تهدف الجامعة إلى تخريج طلاب متميزين يجمعون بين العلم الشرعي والمعرفة الحديثة.",
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
# 3. شخصية المساعد الذكي (محسنة للأسئلة المختصرة)
# ==========================================
SYSTEM_PROMPT = """أنت المساعد الذكي الرسمي لفرع جامعة القرآن الكريم والعلوم الإسلامية في غيل باوزير - حضرموت.

شخصيتك المهنية:
- ممثل رسمي للجامعة، تجمع بين الاحترافية والبساطة في الشرح
- خبير في شؤون الجامعة الأكاديمية والإدارية والتقنية
- تتحدث العربية الفصحى الميسرة بلمسة حضرمية لطيفة
- تشرح المعلومات بطريقة منظمة وواضحة وسهلة الفهم
- تستخدم التنسيق (نقاط، ترقيم) عند الحاجة لتوضيح المعلومات
- لا تستخدم الإيموجي مطلقاً
- لا تبدأ أي رد بتحية إذا سبق لك الرد في هذه المحادثة
- لا تكرر عبارات مثل "أهلاً بك" أو "كيف أقدر أساعدك" بعد الرد الأول

قاعدة المعرفة الكاملة للجامعة:
{context}

تعليمات مهمة جداً:
- اقرأ قاعدة المعرفة كاملة قبل الإجابة
- أي سؤال عن الجداول أو المحاضرات: أجب من قسم "الجداول"
- أي سؤال عن الامتحانات أو الاختبارات: أجب من قسم "الامتحانات"
- أي سؤال عن التخصصات أو الأقسام: أجب من قسم "التخصصات"
- أي سؤال عن الرسوم أو التكاليف: أجب من قسم "الرسوم"
- أي سؤال عن التواصل أو الهاتف أو العنوان: أجب من قسم "التواصل"
- أي سؤال عام عن الجامعة: أجب من قسم "المعلومات العامة"

أسلوب إجابتك:
- إذا كان السؤال عن معلومات محددة: قدمها مباشرة بنقاط واضحة
- إذا كان السؤال عاماً: اشرح باختصار ثم اعرض الخيارات المتاحة
- إذا كانت المعلومة غير متوفرة: قل بالضبط "عذراً، هذه المعلومة غير متوفرة حالياً. يرجى التواصل مع إدارة الفرع."
- إذا كان السؤال خارج نطاق الجامعة: قل "أنا مختص بشؤون الجامعة فقط. هل لديك استفسار عن الدراسة؟"
- عند الشكر: رد باختصار "العفو" أو "في خدمتكم"
- عند السلام: رد بسلام أفضل منه مرة واحدة فقط

طريقة شرحك:
- ابدأ بالمعلومة الأساسية مباشرة
- استخدم جمل قصيرة وواضحة
- إذا احتاج الشرح تفصيلاً، استخدم نقاط مرقمة
- اختم بعرض المساعدة الإضافية إن لزم الأمر"""

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
# 5. الذكاء الاصطناعي (يقرأ كل شيء دائمًا)
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    """إرسال سؤال إلى Groq مع كامل قاعدة المعرفة"""
    data = load_data()
    
    # بناء سياق كامل من جميع الأيقونات
    context = build_full_context(data)
    
    last_updated = data.get("last_updated", "غير محدد")
    system_prompt = SYSTEM_PROMPT.format(
        context=context,
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
            temperature=0.5,
            max_tokens=1000
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
    """بناء سياق كامل ومنظم (مبسط لضمان الفهم)"""
    parts = []
    if data.get('info'):
        parts.append(data['info'])
    if data.get('majors'):
        parts.append(f"التخصصات: {data['majors']}")
    if data.get('schedules'):
        parts.append(f"الجداول: {data['schedules']}")
    if data.get('exams'):
        parts.append(f"الامتحانات: {data['exams']}")
    if data.get('fees'):
        parts.append(f"الرسوم: {data['fees']}")
    if data.get('contacts'):
        parts.append(f"التواصل: {data['contacts']}")
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
            return f"المعلومات المتاحة:\n\n{context}"
    
    context = data.get("info", "")
    if context:
        return context
    
    return "عذراً، الخدمة متوقفة مؤقتاً. يرجى التواصل مع إدارة الفرع."

# ==========================================
# 6. التصنيف الذكي (للإحصائيات فقط)
# ==========================================
def smart_classify(question):
    """تصنيف السؤال إلى فئة مناسبة (لأغراض إحصائية)"""
    q = question.strip()
    q_lower = q.lower()

    if any(w in q_lower for w in [
        "رسوم", "رسومات", "فلوس", "مبلغ", "دفع", "تسديد", "قسط",
        "أقساط", "مالية", "مصاريف", "حوالة", "بنك", "فاتورة", "سعر",
        "تخفيض", "خصم", "منحة", "إعفاء", "مجاني", "تكلفة", "تكاليف",
        "ريال", "دولار", "عملة", "حساب", "إيداع", "تحويل"
    ]):
        return "fees"

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
