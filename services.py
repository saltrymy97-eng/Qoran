"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - خدمات الذكاء الاصطناعي والإحصائيات          ║
║  المطور: سالم التريمي                                       ║
║  الإصدار: 6.0 (نظام القالب الموحد - بدون بيانات افتراضية)  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import re
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
# 2. إدارة البيانات (بدون بيانات افتراضية)
# ==========================================
def load_data():
    """تحميل بيانات الجامعة من data.json فقط"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # إذا كانت majors نصاً طويلاً، حاول تحويلها إلى dict باستخدام القالب
                if isinstance(data.get("majors"), str) and data["majors"]:
                    data["majors"] = parse_majors_template(data["majors"])
                return data
        except json.JSONDecodeError:
            pass

    # لا توجد بيانات - إرجاع فارغ
    return {
        "info": "", "schedules": "", "exams": "", "fees": "", "contacts": "", "majors": {}
    }

def parse_majors_template(text):
    """تحويل نص التخصصات المنسق إلى قاموس منظم"""
    majors_dict = {}
    blocks = re.split(r'\n(?=تخصص:)|\n---\n', text)
    
    for block in blocks:
        block = block.strip()
        if not block or not block.startswith("تخصص:"):
            continue
        
        name_match = re.search(r'تخصص:\s*(.+?)(?:\n|$)', block)
        if not name_match:
            continue
        name = name_match.group(1).strip()
        
        details = {}
        for field in ["الوصف", "الرسوم", "المدة", "فرص العمل"]:
            match = re.search(rf'{field}:\s*(.+?)(?:\n|$)', block)
            if match:
                details[field] = match.group(1).strip()
        
        desc_parts = []
        if "الوصف" in details:
            desc_parts.append(details["الوصف"])
        if "الرسوم" in details:
            desc_parts.append(f"رسوم التخصص: {details['الرسوم']}.")
        if "المدة" in details:
            desc_parts.append(f"مدة الدراسة: {details['المدة']}.")
        if "فرص العمل" in details:
            desc_parts.append(f"فرص العمل: {details['فرص العمل']}.")
        
        majors_dict[name] = " ".join(desc_parts) if desc_parts else block
    
    return majors_dict if majors_dict else {"تخصصات": text}

def save_data(data):
    """حفظ بيانات الجامعة"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي (نظام القالب الموحد)
# ==========================================
SYSTEM_PROMPT = """أنت موظف استقبال محترف في جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير بحضرموت.
أنت خبير في شؤون الجامعة، تجيب بدقة ووضوح. تتحدث العربية الفصحى الميسرة بلمسة حضرمية لطيفة.

[القالب الرسمي لبيانات الجامعة]
جميع بيانات الجامعة منظمة وفق القالب التالي. تعلم هذا القالب جيداً لأنه يحدد كيفية قراءتك للمعلومات:

--- بداية القالب ---
[INFO]
(معلومات عامة عن الجامعة، الرؤية، الرسالة، الأهداف)

[SCHEDULES]
(مواعيد المحاضرات، أيام الدراسة، نظام الحضور)

[EXAMS]
(مواعيد الامتحانات، نظام التقييم، المعدلات)

[FEES]
(رسوم التخصصات، طرق الدفع، التقسيط، المنح)

[CONTACTS]
(أرقام الهواتف، العنوان، الإيميل، ساعات العمل)

[MAJORS]
التخصصات:
تخصص: [اسم التخصص]
الوصف: [وصف التخصص]
الرسوم: [المبلغ]
المدة: [عدد السنوات]
فرص العمل: [فرص العمل]
---
--- نهاية القالب ---

[تعليمات عامة]
- لا تستخدم الإيموجي.
- لا تكرر التحية بعد الرد الأول.
- لا تبدأ إجابتك بعبارة "بناءً على المعلومات المتاحة". أجب مباشرة.
- كن موجزاً ومفيداً. لا تذكر معلومات لا علاقة لها بالسؤال.
- إذا كانت المعلومات فارغة أو لا تحتوي على إجابة السؤال، قل بالضبط: 'عذراً، لا تتوفر لدي بيانات حالياً. يرجى التواصل مع إدارة الجامعة.'
- لا تخترع أي معلومات. لا تخمن. لا تضف شيئاً من عندك.

[المعلومات المتاحة حالياً]
{context}

[آلية التفكير لكل سيناريو]

*** السيناريو 1: سؤال عن جميع التخصصات ***
أمثلة: "ما هي التخصصات؟"، "التخصصات المتاحة"، "كم عدد التخصصات"، "ماهي تخصصات الجامعة"
- قدم قائمة مختصرة بأسماء التخصصات فقط، بدون تفاصيل.
- مثال للرد: "التخصصات المتاحة في الجامعة هي: القرآن وعلومه، الشريعة الإسلامية، الدراسات الإسلامية، إدارة أعمال، محاسبة، تقنية معلومات."

*** السيناريو 2: سؤال عن تخصص واحد محدد (رسوم) ***
- ابحث عن اسم التخصص في [المعلومات المتاحة].
- استخرج رقم الرسوم فقط.
- أجب بجملة واحدة مختصرة.

*** السيناريو 3: سؤال عن تخصص واحد محدد (مدة) ***
- ابحث عن اسم التخصص في [المعلومات المتاحة].
- استخرج المدة فقط.
- أجب بجملة واحدة مختصرة.

*** السيناريو 4: سؤال عن تخصص واحد محدد (فرص عمل) ***
- ابحث عن اسم التخصص في [المعلومات المتاحة].
- استخرج فرص العمل فقط.
- أجب بجملة مختصرة.

*** السيناريو 5: سؤال عن تخصص واحد محدد (وصف) ***
- ابحث عن اسم التخصص في [المعلومات المتاحة].
- قدم وصفاً مختصراً (2-3 جمل).
- لا تذكر التخصصات الأخرى.

*** السيناريو 6: سؤال عن وجود تخصص ***
- ابحث عن اسم التخصص في [المعلومات المتاحة].
- أجب بنعم أو لا.

*** السيناريو 7: سؤال عن الرسوم بشكل عام ***
- ابحث في [المعلومات المتاحة] عن المعلومات المتعلقة بالرسوم فقط.
- أجب بالمعلومة المحددة.

*** السيناريو 8: سؤال عن الامتحانات ***
- ابحث في [المعلومات المتاحة] عن المعلومات المتعلقة بالامتحانات فقط.
- أجب بالمعلومة المحددة.

*** السيناريو 9: سؤال عن الجداول ***
- ابحث في [المعلومات المتاحة] عن المعلومات المتعلقة بالجداول فقط.
- أجب بالمعلومة المحددة.

*** السيناريو 10: سؤال عن التواصل ***
- ابحث في [المعلومات المتاحة] عن المعلومات المتعلقة بالتواصل فقط.
- أجب بالمعلومة المحددة.

*** السيناريو 11: سؤال عن معلومات عامة ***
- ابحث في [المعلومات المتاحة] عن المعلومات المتعلقة بالموضوع.
- أجب بالمعلومة المحددة.

*** السيناريو 12: البيانات فارغة ***
- قل: 'عذراً، لا تتوفر لدي بيانات حالياً. يرجى التواصل مع إدارة الجامعة.'

*** السيناريو 13: سؤال لا علاقة له بالجامعة ***
- قل: "أنا مختص بشؤون الجامعة فقط. كيف يمكنني مساعدتك في أمور الدراسة؟"

*** السيناريو 14: شكر أو تحية ***
- رد باختصار: "العفو"، "وعليكم السلام"، "في خدمتكم".
- لا تبدأ الرد بتحية جديدة."""

# ==========================================
# 4. الذكاء الاصطناعي
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    if chat_history is None:
        chat_history = []

    data = load_data()
    
    # بناء السياق حسب الفئة
    raw_context = None
    if category and category in data and data[category]:
        raw_context = data[category]
    
    # تحويل السياق إلى نص دائماً
    if raw_context is None:
        context = "\n\n".join([f"{k}: {v}" for k, v in data.items() if v])
    elif isinstance(raw_context, dict):
        # تحويل قاموس التخصصات إلى نص
        context = "\n".join([f"{name}: {desc}" for name, desc in raw_context.items()])
    else:
        context = str(raw_context)
    
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
            model="gemma2-9b-it",
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
