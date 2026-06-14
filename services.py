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
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # إذا كانت majors نصاً طويلاً، حولها إلى كائن منظم تلقائياً
                if isinstance(data.get("majors"), str):
                    data["majors"] = convert_majors_to_dict(data["majors"])
                return data
        except json.JSONDecodeError:
            pass

    default_data = {
        "info": "جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير، مؤسسة تعليمية رائدة تجمع بين العلوم الشرعية والإدارية والتقنية.",
        "schedules": "الجداول الدراسية تُحدث بداية كل فصل دراسي. يرجى مراجعة شؤون الطلاب للاطلاع على جدول المحاضرات والمواعيد.",
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي، والامتحانات النهائية في نهاية الفصل. تعلن النتائج بعد أسبوعين من آخر امتحان.",
        "fees": "يمكن تسديد الرسوم الدراسية عبر البنك أو الدفع المباشر في الإدارة المالية. تتوفر خيارات التقسيط للطلاب المستحقين.",
        "contacts": "للتواصل: هاتف الفرع أو زيارة مبنى الفرع بغيل باوزير - حضرموت. أوقات الدوام الرسمي من الأحد إلى الخميس.",
        "majors": {
            "القرآن وعلومه": "يدرس الطالب علوم القرآن، التفسير، التجويد، القراءات. رسوم التخصص: 5000 ريال يمني للفصل. مدة الدراسة 4 سنوات.",
            "الشريعة الإسلامية": "يدرس الطالب الفقه وأصوله، القواعد الفقهية، فقه المعاملات. رسوم التخصص: 5000 ريال يمني للفصل. مدة الدراسة 4 سنوات.",
            "الدراسات الإسلامية": "يدرس الطالب التاريخ الإسلامي، الحضارة الإسلامية، الدعوة. رسوم التخصص: 5000 ريال يمني للفصل. مدة الدراسة 4 سنوات.",
            "إدارة أعمال": "يدرس الطالب مبادئ الإدارة، التسويق، الموارد البشرية. رسوم التخصص: 7000 ريال يمني للفصل. مدة الدراسة 4 سنوات.",
            "محاسبة": "يدرس الطالب المحاسبة المالية، محاسبة التكاليف، المراجعة. رسوم التخصص: 7000 ريال يمني للفصل. مدة الدراسة 4 سنوات.",
            "تقنية معلومات": "يدرس الطالب البرمجة، قواعد البيانات، الشبكات. رسوم التخصص: 7000 ريال يمني للفصل. مدة الدراسة 4 سنوات."
        },
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_data(default_data)
    return default_data

def convert_majors_to_dict(majors_text):
    """تحويل النص الطويل إلى كائن منظم (يُستخدم مرة واحدة عند التحديث)"""
    majors_dict = {}
    current_major = None
    for line in majors_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # البحث عن اسم تخصص في بداية السطر
        for major_name in ["القرآن وعلومه", "الشريعة الإسلامية", "الدراسات الإسلامية", "إدارة أعمال", "محاسبة", "تقنية معلومات"]:
            if major_name in line:
                current_major = major_name
                # إزالة اسم التخصص من السطر
                content = line.replace(major_name, "").strip().lstrip(":").strip()
                majors_dict[current_major] = content
                break
        else:
            # إذا لم يجد اسم تخصص، أضف السطر للتخصص الحالي
            if current_major:
                majors_dict[current_major] += " " + line
    return majors_dict if majors_dict else {"تقنية معلومات": "يدرس الطالب البرمجة والشبكات."}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. شخصية المساعد الذكي
# ==========================================
SYSTEM_PROMPT = (
    "أنت مساعد رسمي لجامعة القرآن الكريم والعلوم الإسلامية فرع غيل باوزير - حضرموت.\n"
    "أعد صياغة المعلومات التالية للإجابة على سؤال الطالب بأسلوب مهذب ومختصر.\n"
    "إذا كانت المعلومات لا تحتوي على إجابة السؤال، قل بالضبط: 'عذراً، هذه المعلومة غير متوفرة لدي حالياً، يرجى التواصل مع شؤون الطلاب.'\n"
    "لا تختلق أي معلومات. لا تخمن. لا تضف شيئاً من عندك.\n\n"
    "المعلومات:\n{context}"
)

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
    """البحث عن اسم تخصص داخل السؤال وإرجاع بياناته"""
    if not majors_dict or not isinstance(majors_dict, dict):
        return None
    
    question_lower = question.lower()
    # نفحص كل مفتاح في القاموس
    for major_name, major_data in majors_dict.items():
        if major_name.lower() in question_lower:
            return major_name, major_data
    
    # إذا لم نجد تطابقاً، نبحث عن جزء من الاسم
    for major_name, major_data in majors_dict.items():
        # تقسيم الاسم إلى كلمات والبحث عن أي منها
        name_parts = major_name.split()
        if any(part.lower() in question_lower for part in name_parts):
            return major_name, major_data
    
    return None, None

# ==========================================
# 6. الذكاء الاصطناعي (معدل للاستفادة من البحث المباشر)
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    if chat_history is None:
        chat_history = []

    data = load_data()

    # التعامل مع فئة majors بشكل خاص
    if category == "majors":
        majors_dict = data.get("majors", {})
        # البحث عن تخصص محدد
        major_name, major_data = find_best_match(question, majors_dict)
        
        if major_name and major_data:
            # وجدنا تخصصاً محدداً
            context = f"تخصص {major_name}: {major_data}"
        else:
            # لم نجد تخصصاً محدداً، نعرض كل التخصصات
            all_majors = []
            for name, desc in majors_dict.items():
                all_majors.append(f"تخصص {name}: {desc}")
            context = "\n".join(all_majors)
        
        # دمج الرسوم إذا لزم الأمر
        if any(w in question for w in ["رسوم", "سعر", "تكلفة", "تكاليف"]):
            fees_data = data.get("fees", "")
            if fees_data:
                context += f"\n\nالرسوم: {fees_data}"
    elif category and category in data and category != "last_updated" and data[category]:
        context = data[category]
    else:
        context = build_full_context(data)

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
        # إذا كانت majors كائن، نحوله إلى نص
        if isinstance(data['majors'], dict):
            all_majors = []
            for name, desc in data['majors'].items():
                all_majors.append(f"تخصص {name}: {desc}")
            parts.append("التخصصات:\n" + "\n".join(all_majors))
        else:
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
# 7. التصنيف الذكي (مبسط)
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
