"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - خدمات الذكاء الاصطناعي والإحصائيات          ║
║  المطور: سالم التريمي                                       ║
║  الإصدار: 2.0                                               ║
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
FAQ_FILE = "faq_cache.json"  # ذاكرة الأسئلة المتكررة

# ==========================================
# 2. إدارة البيانات (مطورة)
# ==========================================
def load_data():
    """
    تحميل بيانات الجامعة مع دعم التحديث التلقائي.
    إذا لم يوجد الملف، ينشئ بيانات افتراضية.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # إضافة حقل آخر تحديث إذا لم يكن موجوداً
            if "last_updated" not in data:
                data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            return data
    return {
        "info": "أهلاً بك في جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير. كيف يمكنني مساعدتك؟",
        "schedules": "الجداول الدراسية تُحدث بداية كل فصل دراسي. يرجى مراجعة شؤون الطلاب.",
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي.",
        "fees": "يمكن تسديد الرسوم عبر البنك أو الدفع المباشر في الإدارة المالية.",
        "contacts": "للتواصل: هاتف الفرع أو زيارة مبنى الفرع بغيل باوزير - حضرموت.",
        "majors": "التخصصات: القرآن وعلومه، الشريعة، الدراسات الإسلامية، إدارة أعمال، محاسبة، تقنية معلومات.",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def save_data(data):
    """حفظ بيانات الجامعة مع توقيت التحديث"""
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي (مطورة)
# ==========================================
SYSTEM_PROMPT = """أنت مساعد ذكي متخصص في فرع جامعة القرآن الكريم والعلوم الإسلامية في غيل باوزير - حضرموت، اليمن.

🎯 شخصيتك وهويتك:
- خبير في شؤون الجامعة الأكاديمية والإدارية والتقنية
- ودود ومحترم ومهذب جداً، تتحلى بأخلاق القرآن الكريم
- تتكلم العربية الفصحى الميسرة الممزوجة بلهجة حضرموت اللطيفة
- مختصر ومفيد في ردودك (لا تتجاوز 4-5 جمل إلا للضرورة)
- تستخدم الإيموجي باعتدال (واحد أو اثنان في الرد) لإضفاء لمسة ودية
- تبدا ردودك بالسلام أو بعبارة ترحيبية إذا كان سؤالاً جديداً

📅 آخر تحديث للبيانات: {last_updated}

📚 قاعدة معرفتك الحالية:
{context}

⚠️ تعليمات صارمة ومهمة جداً:
1. أجب فقط من المعلومات المتاحة في قاعدة المعرفة أعلاه
2. إذا لم تجد الإجابة كاملة، قل بأدب: "لم أجد هذه المعلومة بالتفصيل حالياً. يمكنك التواصل مع إدارة الفرع 📞"
3. لا تختلق أي معلومات غير موجودة، ولا تخمن أبداً
4. إذا سألك الطالب عن شيء خارج نطاق الجامعة، أجب بلطف: "أنا متخصص في شؤون الجامعة فقط 🌿. تفضل، كيف أقدر أساعدك؟"
5. إذا قال الطالب شكراً، رد بعبارة لطيفة مثل: "العفو يا الغالي، في خدمتك دائماً 🌹"
6. إذا ألقى الطالب السلام، ارد بأحسن منه وأضف ترحيباً
7. إذا سأل عن تخصصات المحاسبة أو الإدارة أو التقنية، أجب وشجع الطالب
8. تذكر أنك تمثل جامعة القرآن الكريم، فكن مثالياً في أخلاقك وردودك
9. إذا كان السؤال غير واضح، استفسر بلطف قبل الإجابة
10. إذا كان الطالب مستعجلاً أو متوتراً، هدئه وطمئنه أولاً ثم أجب"""

FALLBACK_SYSTEM_PROMPT = """أنت مساعد ذكي لجامعة القرآن الكريم - فرع غيل باوزير.
أجب فقط من المعلومات المتاحة. إذا لم تجد الإجابة، قل: "يرجى التواصل مع الإدارة 📞"
كن مهذباً ومختصراً.

المعلومات:
{context}"""

# ==========================================
# 4. إدارة سجل الأسئلة (مطور)
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
    """
    تسجيل سؤال في السجل مع بيانات إضافية للتحليل.
    
    response_status:
        - success: تمت الإجابة بنجاح
        - not_found: لم يجد الذكاء الاصطناعي إجابة
        - error: حدث خطأ تقني
    """
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
    # الاحتفاظ بآخر 1000 سؤال فقط
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_logs(logs)

def get_stats():
    """
    إرجاع إحصائيات الأسئلة المتقدمة.
    تشمل: الإجمالي، اليوم، الأسبوع، الشهر، الأسئلة الشائعة،
    توزيع الفئات، ساعات الذروة، الأسئلة غير المجابة.
    """
    logs = load_logs()
    
    if not logs:
        return {
            "total": 0,
            "today": 0,
            "this_week": 0,
            "this_month": 0,
            "top_questions": [],
            "categories": {},
            "peak_hours": {},
            "unanswered_questions": [],
            "daily_trend": []
        }
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_month = now.strftime("%Y-%m")
    current_week = now.isocalendar()[1]
    current_year = now.year
    
    # متغيرات العد
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
        
        # عد الأسئلة المتشابهة (مع تجاهل الفروق البسيطة)
        q_normalized = normalize_question(q)
        question_counts[q_normalized] = question_counts.get(q_normalized, 0) + 1
        
        # عد الفئات
        cat = log.get("category", "info")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # ساعات الذروة
        hour = log.get("hour", 0)
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # الأسئلة غير المجابة
        if log.get("response_status") == "not_found":
            unanswered.append(q)
        
        # إحصائيات الوقت
        try:
            log_date = datetime.fromisoformat(log["timestamp"])
            log_date_str = log_date.strftime("%Y-%m-%d")
            
            if log_date_str == today_str:
                today_count += 1
            
            if log_date.strftime("%Y-%m") == current_month:
                this_month_count += 1
            
            if log_date.isocalendar()[1] == current_week and log_date.year == current_year:
                this_week_count += 1
            
            # اتجاه يومي (آخر 7 أيام)
            if log_date_str not in daily_counts:
                daily_counts[log_date_str] = 0
            daily_counts[log_date_str] += 1
            
        except:
            pass
    
    # ترتيب الأسئلة الأكثر شيوعاً
    sorted_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
    top_questions = [{"question": q, "count": c} for q, c in sorted_questions[:10]]
    
    # ترتيب ساعات الذروة
    peak_hours = dict(sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5])
    
    # الأسئلة غير المجابة (الفريدة)
    unique_unanswered = list(dict.fromkeys(unanswered))[:10]
    
    # اتجاه آخر 7 أيام
    last_7_days = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        last_7_days.append({
            "date": day,
            "count": daily_counts.get(day, 0)
        })
    
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

def normalize_question(question):
    """توحيد شكل السؤال للمقارنة"""
    # إزالة علامات الترقيم والتشكيل
    q = question.strip().lower()
    q = re.sub(r'[،,\.\!\?؟\:\:\;\-\(\)\[\]\{\}]', '', q)
    q = re.sub(r'[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED]', '', q)
    # توحيد الحروف
    q = q.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    q = q.replace('ة', 'ه')
    q = q.replace('ى', 'ي')
    return q

# ==========================================
# 5. الذكاء الاصطناعي (مطور بالكامل)
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    """
    إرسال سؤال إلى Groq مع تاريخ المحادثة للسياق.
    
    المميزات:
    - سياق ذكي من قاعدة المعرفة
    - ذاكرة محادثة (آخر 6 رسائل)
    - كشف تلقائي للأسئلة غير المجابة
    - وضع الطوارئ عند فشل الاتصال
    """
    data = load_data()
    
    # بناء السياق من البيانات
    if category and category in data and category != "last_updated":
        context = data[category]
    else:
        # سياق كامل مع ترتيب منطقي
        context = build_full_context(data)
    
    last_updated = data.get("last_updated", "غير محدد")
    system_prompt = SYSTEM_PROMPT.format(
        context=context[:3500],  # زيادة حد السياق
        last_updated=last_updated
    )
    
    # بناء الرسائل مع تاريخ المحادثة
    messages = [{"role": "system", "content": system_prompt}]
    
    # إضافة آخر 6 رسائل من تاريخ المحادثة للسياق
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # إضافة السؤال الحالي
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
        
        # تحديد حالة الرد
        if any(phrase in ai_response for phrase in ["لم أجد", "لا تتوفر", "غير متوفرة", "غير متاح"]):
            log_question(question, category or "info", "not_found")
        else:
            log_question(question, category or "info", "success")
        
        return ai_response
        
    except Exception as e:
        # وضع الطوارئ: رد محلي ذكي
        log_question(question, category or "info", "error")
        return generate_fallback_response(question, category, data)

def build_full_context(data):
    """بناء سياق كامل ومنظم من جميع بيانات الجامعة"""
    parts = []
    
    if data.get('info'):
        parts.append(f"🔹 معلومات عامة عن الفرع:\n{data['info']}")
    if data.get('majors'):
        parts.append(f"🔹 التخصصات والبرامج الأكاديمية:\n{data['majors']}")
    if data.get('schedules'):
        parts.append(f"🔹 الجداول الدراسية والمحاضرات:\n{data['schedules']}")
    if data.get('exams'):
        parts.append(f"🔹 الامتحانات والتقييم:\n{data['exams']}")
    if data.get('fees'):
        parts.append(f"🔹 الرسوم الدراسية والمالية:\n{data['fees']}")
    if data.get('contacts'):
        parts.append(f"🔹 جهات الاتصال والتواصل:\n{data['contacts']}")
    
    return "\n\n".join(parts) if parts else "لا توجد بيانات محددة بعد."

def generate_fallback_response(question, category, data):
    """
    توليد رد احتياطي عند فشل الاتصال بـ Groq.
    يستخدم البيانات المحلية فقط.
    """
    # أسئلة الترحيب
    greetings = ["سلام", "مرحبا", "هلا", "أهلا", "صباح", "مساء"]
    if any(w in question for w in greetings):
        return f"{get_greeting()}! كيف أقدر أخدمك اليوم؟ 🌿"
    
    # أسئلة الشكر
    thanks = ["شكرا", "شكراً", "مشكور", "جزاك", "تسلم"]
    if any(w in question for w in thanks):
        return "العفو يا الغالي، حاضرين لك في أي وقت 🌹"
    
    # البحث في البيانات المحلية
    if category and category in data and category != "last_updated":
        context = data[category]
        if context:
            return f"📌 المعلومات المتاحة:\n\n{context}\n\n⚠️ *الرد من قاعدة البيانات المحلية.*"
    
    # بحث عام
    context = data.get("info", "")
    if context:
        return f"📌 {context}\n\n⚠️ *الرد من قاعدة البيانات المحلية. للاستفسار الدقيق، تواصل مع الإدارة 📞*"
    
    return "⚠️ عذراً، الخدمة متوقفة مؤقتاً. يرجى التواصل مع إدارة الفرع 📞"

# ==========================================
# 6. التصنيف الذكي (مطور - هجين)
# ==========================================
def smart_classify(question):
    """
    تصنيف ذكي متطور للسؤال (هجين).
    المرحلة 1: كلمات مفتاحية (سريعة، تغطي 90% من الحالات)
    المرحلة 2: ذكاء اصطناعي (للأسئلة المعقدة)
    """
    q = question.strip()
    q_lower = q.lower()
    
    # ===== المرحلة 1: الكلمات المفتاحية الموسعة =====
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
    
    # البحث مع ترتيب الكلمات من الأطول إلى الأقصر
    for category, words in keywords.items():
        sorted_words = sorted(words, key=len, reverse=True)
        for word in sorted_words:
            if word in q_lower or word in q:
                return category
    
    # أسئلة الترحيب والتحية
    greetings = ["سلام", "مرحبا", "هلا", "أهلا", "السلام", "صباح", "مساء", "حياك", "ياهلا"]
    if any(w in q_lower for w in greetings):
        return "info"
    
    # أسئلة الشكر والثناء
    thanks = ["شكرا", "شكراً", "مشكور", "جزاك", "الله يعطيك", "تسلم", "ما قصرت", "يعطيك"]
    if any(w in q_lower for w in thanks):
        return "info"
    
    # ===== المرحلة 2: تصنيف AI للأسئلة المعقدة =====
    complex_indicators = ["كيف", "لماذا", "متى", "هل يمكن", "ما الفرق", "اشرح", "ما هي", "كم"]
    if any(w in q for w in complex_indicators) and len(q) > 20:
        try:
            ai_category = classify_with_ai(q)
            if ai_category and ai_category in keywords:
                return ai_category
        except:
            pass
    
    return "info"

def classify_with_ai(question):
    """تصنيف السؤال باستخدام Groq (للأسئلة المعقدة فقط)"""
    prompt = f"""صنف سؤال الطالب إلى واحدة من الفئات فقط:
schedules, exams, fees, contacts, majors, info

السؤال: {question}

الفئة (كلمة واحدة فقط):"""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        result = response.choices[0].message.content.strip().lower()
        # استخراج الكلمة الأولى فقط
        return result.split()[0] if result else "info"
    except:
        return "info"

# ==========================================
# 7. ذاكرة الأسئلة المتكررة (FAQ Cache)
# ==========================================
def load_faq_cache():
    """تحميل ذاكرة الأسئلة المتكررة"""
    if os.path.exists(FAQ_FILE):
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_faq_cache(cache):
    """حفظ ذاكرة الأسئلة المتكررة"""
    with open(FAQ_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_cached_answer(question):
    """البحث عن إجابة مخزنة لسؤال مشابه"""
    cache = load_faq_cache()
    q_normalized = normalize_question(question)
    
    # بحث بسيط عن تطابق جزئي
    for cached_q, cached_data in cache.items():
        if q_normalized in cached_q or cached_q in q_normalized:
            return cached_data.get("answer")
    
    return None

def cache_answer(question, answer):
    """تخزين إجابة سؤال متكرر"""
    cache = load_faq_cache()
    q_normalized = normalize_question(question)
    cache[q_normalized] = {
        "original_question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat(),
        "hits": cache.get(q_normalized, {}).get("hits", 0) + 1
    }
    # الاحتفاظ بآخر 500 سؤال فقط
    if len(cache) > 500:
        # حذف الأقدم
        sorted_cache = sorted(cache.items(), key=lambda x: x[1].get("timestamp", ""))
        cache = dict(sorted_cache[-500:])
    save_faq_cache(cache)

# ==========================================
# 8. دوال الترحيب والمساعدة
# ==========================================
def get_greeting():
    """رسالة ترحيبية ذكية حسب الوقت"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "صباح الخير 🌅"
    elif 12 <= hour < 15:
        return "ظهر الخير ☀️"
    elif 15 <= hour < 17:
        return "عصر الخير 🌤️"
    elif 17 <= hour < 19:
        return "مساء النور 🌆"
    elif 19 <= hour < 22:
        return "مساء الخير 🌙"
    else:
        return "مساء الخير 🌙"

def get_welcome_message():
    """رسالة ترحيبية كاملة"""
    greeting = get_greeting()
    return f"""{greeting} أهلًا وسهلًا بك في المساعد الذكي لجامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير.

📌 **الخدمات المتاحة:**
📚 جداول المحاضرات والمواد
📝 الامتحانات والنتائج
💰 الرسوم الدراسية
📞 جهات الاتصال وموقع الفرع
🎓 التخصصات الأكاديمية

💡 **معلومة:** تقدر تسأل عن تخصصات المحاسبة والإدارة والتقنية أيضاً!

كيف أقدر أخدمك اليوم؟"""

def search_in_data(query):
    """بحث ذكي في جميع بيانات الجامعة"""
    data = load_data()
    results = {}
    
    query_normalized = normalize_question(query)
    
    for key, value in data.items():
        if key == "last_updated":
            continue
        value_normalized = normalize_question(value)
        if query_normalized in value_normalized:
            results[key] = value[:500]  # أول 500 حرف من كل قسم مطابق
    
    return results if results else None

# ==========================================
# 9. تحليل بسيط للمشاعر (لتكييف الرد)
# ==========================================
def analyze_sentiment(question):
    """
    تحليل بسيط لمشاعر الطالب من السؤال.
    يعيد: positive, negative, neutral, urgent
    """
    q = question.strip()
    
    # كلمات الاستعجال
    urgent_words = ["ضروري", "عاجل", "بسرعة", "الآن", "مستعجل", "لازم", "فوراً", "فورا"]
    if any(w in q for w in urgent_words):
        return "urgent"
    
    # كلمات سلبية
    negative_words = ["مشكلة", "صعب", "سيء", "مخيب", "محبط", "غاضب", "ظلم", "شكوى"]
    if any(w in q for w in negative_words):
        return "negative"
    
    # كلمات إيجابية
    positive_words = ["ممتاز", "جميل", "رائع", "شكر", "حبيت", "أحسنت", "ما شاء الله"]
    if any(w in q for w in positive_words):
        return "positive"
    
    return "neutral"

def get_emotional_prefix(sentiment):
    """بادئة عاطفية حسب مشاعر الطالب"""
    prefixes = {
        "urgent": "أفهم استعجالك، خلينا نشوف الموضوع فوراً 🏃‍♂️\n\n",
        "negative": "الله يطيب خاطرك ويسهل أمرك 🌿\n\n",
        "positive": "الله يسعدك ويفرح قلبك 🌹\n\n",
        "neutral": ""
    }
    return prefixes.get(sentiment, "")
