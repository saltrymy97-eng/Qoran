"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - نظام الذاكرة الهجين للمساعد الذكي           ║
║  المطور: سالم التريمي                                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import re
import datetime
import difflib
from groq import Groq

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

DATA_FILE = "data.json"
LOGS_FILE = "logs.json"
MEMORY_FILE = "training_data.json"  # ملف الذاكرة (الأسئلة والأجوبة)

# إعدادات الذاكرة
MEMORY_MATCH_THRESHOLD = 0.8  # نسبة التشابه المطلوبة لاستخدام الذاكرة (80%)
MAX_MEMORY_SIZE = 15000       # الحد الأقصى لعدد الأسئلة في الذاكرة (أكبر من 10000)

# ==========================================
# 2. إدارة البيانات الأساسية
# ==========================================
def load_data():
    """تحميل بيانات الجامعة من الملف"""
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
    """تحويل نص التخصصات إلى قاموس منظم"""
    majors_dict = {}
    text = majors_text.strip()
    if not text:
        return majors_dict

    lines = text.split('\n')
    current_major = None
    current_details = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        is_new_major = False
        for prefix in ['تخصص ', 'قسم ', 'كلية ']:
            if prefix in line:
                if current_major:
                    majors_dict[current_major] = ' '.join(current_details)

                idx = line.find(prefix) + len(prefix)
                name_part = line[idx:].strip()

                if ':' in name_part:
                    name = name_part.split(':')[0].strip()
                    detail = name_part.split(':', 1)[-1].strip()
                else:
                    name = name_part
                    detail = ''

                current_major = name
                current_details = [detail] if detail else []
                is_new_major = True
                break

        if not is_new_major and current_major:
            current_details.append(line)

    if current_major:
        majors_dict[current_major] = ' '.join(current_details)

    return majors_dict if majors_dict else {"تخصصات": text}

def save_data(data):
    """حفظ بيانات الجامعة"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. نظام الذاكرة (الأسئلة والأجوبة)
# ==========================================
def load_memory():
    """تحميل الذاكرة من ملف training_data.json"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []

def save_memory(memory):
    """حفظ الذاكرة إلى الملف"""
    if len(memory) > MAX_MEMORY_SIZE:
        memory = memory[-MAX_MEMORY_SIZE:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def add_to_memory(question, answer):
    """إضافة سؤال وجواب جديد إلى الذاكرة"""
    memory = load_memory()
    for item in memory:
        if item["question"].strip() == question.strip():
            item["answer"] = answer
            item["updated"] = datetime.datetime.now().isoformat()
            save_memory(memory)
            return
    memory.append({
        "question": question.strip(),
        "answer": answer,
        "created": datetime.datetime.now().isoformat()
    })
    save_memory(memory)

def find_best_match_memory(question, memory):
    """البحث عن أفضل تطابق لسؤال في الذاكرة باستخدام تشابه النص"""
    if not memory:
        return None, 0.0
    
    q_clean = question.strip().lower()
    best_match = None
    best_score = 0.0
    
    for item in memory:
        item_q = item["question"].strip().lower()
        score = difflib.SequenceMatcher(None, q_clean, item_q).ratio()
        if score > best_score:
            best_score = score
            best_match = item
    
    if best_score >= MEMORY_MATCH_THRESHOLD:
        return best_match, best_score
    return None, best_score

def get_memory_stats():
    """إحصائيات الذاكرة"""
    memory = load_memory()
    logs = load_logs()
    memory_responses = sum(1 for log in logs if log.get("source") == "memory")
    groq_responses = sum(1 for log in logs if log.get("source") == "groq")
    
    return {
        "total_questions": len(memory),
        "memory_responses": memory_responses,
        "groq_responses": groq_responses
    }

# ==========================================
# 4. توليد بيانات التدريب (10000 سؤال)
# ==========================================
def generate_training_data(num_questions=10000, progress_callback=None):
    """توليد أسئلة وأجوبة تدريبية من بيانات الجامعة باستخدام Groq"""
    data = load_data()
    if not data:
        return []
    
    context = build_full_context(data)
    if not context or context == "لا توجد بيانات.":
        return []
    
    memory = []
    batch_size = 50
    batches = num_questions // batch_size
    
    for i in range(batches):
        if progress_callback:
            progress_callback(i / batches)
        
        prompt = f"""أنت مساعد ذكي لجامعة القرآن الكريم والعلوم الإسلامية.

        بناءً على المعلومات التالية عن الجامعة:
        {context[:3000]}

        قم بتوليد {batch_size} سؤالاً وإجابة متنوعة باللغة العربية. يجب أن تغطي الأسئلة:
        - التخصصات (تفاصيل كل تخصص، رسومه، مواده، فرص عمله)
        - الرسوم الدراسية (طرق الدفع، التقسيط، المنح)
        - الامتحانات (مواعيدها، نظام التقييم)
        - الجداول الدراسية (مواعيد المحاضرات، نظام الحضور)
        - التواصل (أرقام الهاتف، العنوان، ساعات العمل)
        - معلومات عامة عن الجامعة (التأسيس، الرؤية، الأهداف)

        أعد الرد بصيغة JSON فقط، كمصفوفة من الكائنات، كل كائن يحتوي على "question" و "answer":
        [
          {{"question": "سؤال 1", "answer": "إجابة 1"}},
          {{"question": "سؤال 2", "answer": "إجابة 2"}}
        ]

        لا تضف أي نص آخر، فقط JSON."""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "أنت مولد بيانات تدريب. أعد JSON فقط."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            result = response.choices[0].message.content
            
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                batch_data = json.loads(json_match.group())
                memory.extend(batch_data)
        except Exception as e:
            print(f"خطأ في توليد الدفعة {i}: {e}")
    
    save_memory(memory)
    return memory

# ==========================================
# 5. نظام الذكاء الاصطناعي الهجين
# ==========================================
def ask_ai(question, category=None, chat_history=None):
    if chat_history is None:
        chat_history = []

    # 1. البحث في الذاكرة
    memory = load_memory()
    best_match, score = find_best_match_memory(question, memory)
    
    if best_match:
        log_question(question, category or "info", source="memory")
        return best_match["answer"]
    
    # 2. لم نجد في الذاكرة - نستخدم Groq
    data = load_data()

    if category == "majors":
        majors_dict = data.get("majors", {})
        major_name, major_data = find_best_match_major(question, majors_dict)
        if major_name and major_data:
            context = f"تخصص {major_name}: {major_data}"
        else:
            all_majors = []
            for name, desc in majors_dict.items():
                all_majors.append(f"تخصص {name}: {desc}")
            context = "\n".join(all_majors) if all_majors else "لا توجد تخصصات."
        
        if any(w in question for w in ["رسوم", "سعر", "تكلفة", "تكاليف"]):
            fees_data = data.get("fees", "")
            if fees_data:
                context += f"\n\nالرسوم: {fees_data}"
    elif category and category in data and category != "last_updated" and data[category]:
        context = data[category]
    else:
        context = build_full_context(data)

    if not context or not context.strip():
        context = "لا توجد بيانات متاحة."

    system_prompt = SYSTEM_PROMPT.format(context=context[:1500])
    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages.extend(chat_history[-4:])
    messages.append({"role": "user", "content": question})

    if not client:
        answer = context[:500]
    else:
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
                max_tokens=400
            )
            answer = response.choices[0].message.content
        except Exception:
            answer = context[:500]

    # 3. التعلم الذاتي
    if answer and "عذراً" not in answer:
        add_to_memory(question, answer)

    log_question(question, category or "info", source="groq")
    return answer

def find_best_match_major(question, majors_dict):
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
# 6. شخصية المساعد الذكي
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
- إذا وجدته: قدم تفاصيله كاملة. لا تذكر أي تخصص آخر.
- إذا لم تجده: قل "هذا التخصص غير موجود في سجلاتي. يرجى التواصل مع شؤون الطلاب."

*** السيناريو 2: سؤال عام عن جميع التخصصات ***
مثال: "ما هي التخصصات"، "التخصصات المتاحة"
- قدم قائمة بأسماء التخصصات فقط، بدون تفاصيل.
- ثم اسأل: "هل تريد شرحاً مفصلاً عن أي منها؟"

*** السيناريو 3: سؤال عن الرسوم ***
- ابحث في قسم "الرسوم". إذا لم تجد: قل "تفاصيل الرسوم غير متوفرة لدي."

*** السيناريو 4: سؤال عن الامتحانات ***
- ابحث في قسم "الامتحانات".

*** السيناريو 5: سؤال عن الجداول ***
- ابحث في قسم "الجداول".

*** السيناريو 6: سؤال عن التواصل ***
- ابحث في قسم "التواصل".

*** السيناريو 7: سؤال عام عن الجامعة ***
- ابحث في قسم "المعلومات العامة".

*** السيناريو 8: قاعدة المعرفة فارغة ***
- قل: "لا تتوفر لدي بيانات حالياً. يرجى التواصل مع إدارة الجامعة مباشرة."

[محظورات]
- لا تخترع تخصصاً غير موجود. لا تخمن.
- لا تقدم إجابة إذا لم تكن متأكداً منها 100%.
- لا تخلط بين الأقسام.
- لا تبدأ الرد بتحية إذا سبق لك الرد.
"""

# ==========================================
# 7. السجل والإحصائيات
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
    memory = load_memory()
    
    if not logs:
        return {
            "total": 0, "today": 0, "top_questions": [], "categories": {},
            "memory_size": len(memory),
            "memory_responses": 0,
            "groq_responses": 0
        }

    today_str = datetime.datetime.now().date().isoformat()
    today_count = sum(1 for log in logs if log["timestamp"].startswith(today_str))

    question_counts = {}
    category_counts = {}
    memory_responses = 0
    groq_responses = 0
    
    for log in logs:
        q = log["question"].strip()
        question_counts[q] = question_counts.get(q, 0) + 1
        cat = log.get("category", "info")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if log.get("source") == "memory":
            memory_responses += 1
        else:
            groq_responses += 1

    sorted_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
    top_questions = [{"question": q, "count": c} for q, c in sorted_questions[:10]]

    return {
        "total": len(logs),
        "today": today_count,
        "top_questions": top_questions,
        "categories": category_counts,
        "memory_size": len(memory),
        "memory_responses": memory_responses,
        "groq_responses": groq_responses
    }

# ==========================================
# 8. التصنيف الذكي
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
# 9. بناء السياق الكامل (للوضع الاحتياطي)
# ==========================================
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
# 10. دوال الترحيب والمساعدة
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
