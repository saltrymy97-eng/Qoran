"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - خدمات الذكاء الاصطناعي والإحصائيات          ║
║  المطور: سالم التريمي                                       ║
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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

DATA_FILE = "data.json"
LOGS_FILE = "logs.json"

# ==========================================
# 2. إدارة البيانات
# ==========================================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data.get("majors"), str) and data["majors"]:
                    data["majors"] = convert_majors_to_dict(data["majors"])
                return data
        except json.JSONDecodeError:
            pass

    return {
        "info": "", "schedules": "", "exams": "", "fees": "", "contacts": "",
        "majors": {}, "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def convert_majors_to_dict(majors_text):
    majors_dict = {}
    text = majors_text.strip()
    if not text:
        return majors_dict

    parts = re.split(r'\n(?=تخصص|\bقسم\b|\bكلية\b)', text)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        first_line = part.split('\n')[0].strip()
        name = re.sub(r'^(تخصص|قسم|كلية)\s*', '', first_line).strip()
        name = name.rstrip(':').strip()

        if name:
            detail_lines = part.split('\n')[1:]
            details = ' '.join([line.strip() for line in detail_lines if line.strip()])

            if not details:
                details_match = re.match(r'^(?:تخصص|قسم|كلية)\s*.+?:\s*(.*)', first_line)
                if details_match:
                    details = details_match.group(1).strip()

            if name not in majors_dict:
                majors_dict[name] = details if details else first_line
            else:
                if details:
                    majors_dict[name] += " " + details

    return majors_dict

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي (برومبت مفصل لكل تبويب)
# ==========================================
SYSTEM_PROMPT = """أنت موظف استقبال محترف في جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير بحضرموت.

[هويتك وأخلاقياتك]
- أنت خبير في شؤون الجامعة، تجيب بدقة ووضوح.
- تتحدث العربية الفصحى الميسرة بلمسة حضرمية لطيفة.
- لا تستخدم الإيموجي. لا تكرر التحية بعد الرد الأول.
- لا تبدأ إجابتك بعبارة "بناءً على المعلومات المتاحة". أجب مباشرة.

[قاعدة المعرفة الحالية]
{context}

[آلية التفكير والسيناريوهات]

*** السيناريو 1: سؤال عن تخصص واحد محدد ***
مثال: "اشرح تخصص المحاسبة"، "هل يوجد تخصص تقنية معلومات"، "كم رسوم تخصص القرآن"، "تفاصيل تخصص الشريعة"
- ابحث عن اسم التخصص في [قاعدة المعرفة].
- إذا وجدته: قدم تفاصيله كاملة (الوصف، المواد، الرسوم، المدة، فرص العمل). لا تذكر أي تخصص آخر.
- إذا لم تجده: قل "هذا التخصص غير موجود في سجلاتي. يرجى التواصل مع شؤون الطلاب."

*** السيناريو 2: سؤال عام عن جميع التخصصات ***
مثال: "ما هي التخصصات"، "التخصصات المتاحة"، "كم عدد التخصصات"
- قدم قائمة بأسماء التخصصات فقط، بدون تفاصيل.
- ثم اسأل: "هل تريد شرحاً مفصلاً عن أي منها؟"

*** السيناريو 3: سؤال عن الرسوم والمالية ***
مثال: "كم رسوم الفصل"، "هل يوجد تقسيط"، "كم رسوم التسجيل"، "هل هناك منح"
- ابحث في قسم "الرسوم" فقط.
- إذا وجدت الإجابة: قدمها بدقة مع ذكر المبلغ.
- إذا لم تجد: قل "تفاصيل الرسوم غير متوفرة لدي. يرجى التواصل مع الإدارة المالية."

*** السيناريو 4: سؤال عن الامتحانات والتقييم ***
مثال: "متى تبدأ الامتحانات"، "ما هو نظام التقييم"، "كيف أحسب المعدل"، "متى تظهر النتائج"
- ابحث في قسم "الامتحانات" فقط.
- قدم التواريخ والإجراءات المحددة إن وجدت.
- إذا لم تجد: قل "تفاصيل الامتحانات غير متوفرة لدي. يرجى التواصل مع شؤون الطلاب."

*** السيناريو 5: سؤال عن الجداول والمحاضرات ***
مثال: "متى تبدأ المحاضرات"، "ما هو نظام الدوام"، "كم عدد ساعات الدراسة"
- ابحث في قسم "الجداول" فقط.
- قدم المواعيد والأوقات المحددة إن وجدت.
- إذا لم تجد: قل "تفاصيل الجداول غير متوفرة لدي. يرجى التواصل مع شؤون الطلاب."

*** السيناريو 6: سؤال عن التواصل والعنوان ***
مثال: "أين تقع الجامعة"، "رقم الهاتف"، "كيف أتواصل مع الإدارة"، "ساعات العمل"
- ابحث في قسم "التواصل" فقط.
- قدم معلومات الاتصال كاملة إن وجدت.
- إذا لم تجد: قل "معلومات التواصل غير متوفرة لدي."

*** السيناريو 7: سؤال عام عن الجامعة ***
مثال: "متى تأسست الجامعة"، "هل الجامعة معتمدة"، "ما هي رؤية الجامعة"
- ابحث في قسم "المعلومات العامة" فقط.
- أجب من المعلومات المتاحة.
- إذا لم تجد: قل "هذه المعلومة غير متوفرة لدي."

*** السيناريو 8: قاعدة المعرفة فارغة ***
- قل: "لا تتوفر لدي بيانات حالياً. يرجى التواصل مع إدارة الجامعة مباشرة."

[محظورات]
- لا تخترع تخصصاً غير موجود. لا تخمن. لا تقل "قد يكون هناك".
- لا تقدم إجابة إذا لم تكن متأكداً منها 100%.
- لا تخلط بين الأقسام. كل سؤال له قسمه الخاص.
- لا تبدأ الرد بتحية إذا سبق لك الرد.
"""

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

def log_question(question, category):
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
# 5. البحث عن أفضل تطابق
# ==========================================
def find_best_match(question, majors_dict):
    if not majors_dict or not isinstance(majors_dict, dict):
        return None, None

    question_lower = question.lower()

    for major_name, major_data in majors_dict.items():
        if major_name.lower() in question_lower:
            return major_name, major_data

    for major_name, major_data in majors_dict.items():
        name_parts = major_name.split()
        if any(part.lower() in question_lower for part in name_parts):
            return major_name, major_data

    return None, None

# ==========================================
# 6. الذكاء الاصطناعي
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    if chat_history is None:
        chat_history = []

    data = load_data()

    if category == "majors":
        majors_dict = data.get("majors", {})
        major_name, major_data = find_best_match(question, majors_dict)

        if major_name and major_data:
            context = f"تخصص {major_name}: {major_data}"
        else:
            all_majors = []
            for name, desc in majors_dict.items():
                all_majors.append(f"تخصص {name}: {desc}")
            context = "\n".join(all_majors) if all_majors else "لا توجد تخصصات مسجلة بعد."

        if any(w in question for w in ["رسوم", "سعر", "تكلفة", "تكاليف"]):
            fees_data = data.get("fees", "")
            if fees_data:
                context += f"\n\nالرسوم: {fees_data}"
    elif category and category in data and category != "last_updated" and data[category]:
        context = data[category]
    else:
        context = build_full_context(data)

    if not context or not context.strip():
        context = "لا توجد بيانات متاحة بعد. يرجى رفع ملف البيانات من لوحة الإدارة."

    log_question(question, category or "info")

    system_prompt = SYSTEM_PROMPT.format(context=context[:1500])

    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages.extend(chat_history[-4:])
    messages.append({"role": "user", "content": question})

    if not client:
        return context[:500]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception:
        return context[:500]

def build_full_context(data):
    parts = []
    if data.get("info"):
        parts.append(data['info'])
    if data.get("majors"):
        if isinstance(data['majors'], dict) and data['majors']:
            all_majors = []
            for name, desc in data['majors'].items():
                all_majors.append(f"تخصص {name}: {desc}")
            parts.append("التخصصات:\n" + "\n".join(all_majors))
        elif data['majors']:
            parts.append(f"التخصصات: {data['majors']}")
    if data.get("schedules"):
        parts.append(f"الجداول: {data['schedules']}")
    if data.get("exams"):
        parts.append(f"الامتحانات: {data['exams']}")
    if data.get("fees"):
        parts.append(f"الرسوم: {data['fees']}")
    if data.get("contacts"):
        parts.append(f"التواصل: {data['contacts']}")
    return "\n\n".join(parts) if parts else "لا توجد بيانات."

# ==========================================
# 7. التصنيف الذكي
# ==========================================
def smart_classify(question):
    q = question.lower()

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
# 8. دوال الترحيب والمساعدة
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
