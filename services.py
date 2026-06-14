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
import difflib
import time
from groq import Groq

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

DATA_FILE = "data.json"
LOGS_FILE = "logs.json"
MEMORY_FILE = "training_data.json"

MEMORY_MATCH_THRESHOLD = 0.8
MAX_MEMORY_SIZE = 15000

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

# ==========================================
# 4. توليد بيانات التدريب (دفعة واحدة)
# ==========================================
def extract_qa_pairs(text):
    """
    يستقبل أي نص من Groq وينظفه ويستخرج الأسئلة والأجوبة.
    """
    qa_pairs = []
    text = text.strip()
    
    # طريقة 1: س: ... ج: ...
    pattern1 = re.findall(r'[سس]\s*[:.\-–]\s*(.+?)\s*\n\s*[جج]\s*[:.\-–]\s*(.+?)(?=\n\s*[سس]|\Z)', text, re.DOTALL)
    qa_pairs.extend(pattern1)
    
    # طريقة 2: سؤال: ... جواب: ...
    pattern2 = re.findall(r'سؤال\s*[:.\-–]\s*(.+?)\s*\n\s*جواب\s*[:.\-–]\s*(.+?)(?=\n\s*سؤال|\Z)', text, re.DOTALL)
    qa_pairs.extend(pattern2)
    
    # طريقة 3: Q: ... A: ...
    pattern3 = re.findall(r'[Qq]\s*[:.\-–]\s*(.+?)\s*\n\s*[Aa]\s*[:.\-–]\s*(.+?)(?=\n\s*[Qq]|\Z)', text, re.DOTALL)
    qa_pairs.extend(pattern3)
    
    # طريقة 4: نمط مرقم
    pattern4 = re.findall(r'\d+[\.\-)]\s*(.+?)\s*\n\s*(?:الجواب|الاجابة|جواب|إجابة|اجابة)\s*[:.\-–]\s*(.+?)(?=\n\s*\d+[\.\-)]|\Z)', text, re.DOTALL)
    qa_pairs.extend(pattern4)
    
    # طريقة 5: أي سطر يبدأ بـ س أو ج
    lines = text.split('\n')
    current_q = None
    for line in lines:
        line = line.strip()
        if re.match(r'^[سس][:.\s\-–]', line):
            current_q = re.sub(r'^[سس][:.\s\-–]*', '', line).strip()
        elif re.match(r'^[جج][:.\s\-–]', line):
            if current_q:
                answer = re.sub(r'^[جج][:.\s\-–]*', '', line).strip()
                qa_pairs.append((current_q, answer))
                current_q = None
    
    # طريقة 6: أي جملة استفهامية متبوعة بجملة
    if not qa_pairs:
        for i in range(len(lines) - 1):
            if lines[i].endswith('؟') or lines[i].endswith('?'):
                qa_pairs.append((lines[i], lines[i+1]))
    
    # تنظيف وإزالة التكرار
    seen = set()
    clean_pairs = []
    for q, a in qa_pairs:
        q = q.strip()
        a = a.strip()
        if q and a and len(q) > 3 and len(a) > 3 and q not in seen:
            clean_pairs.append((q, a))
            seen.add(q)
    
    return clean_pairs

def generate_training_data(num_questions=10000, progress_callback=None):
    """
    توليد الأسئلة دفعة واحدة. إذا نجح، يرجع الذاكرة. إذا فشل، يصرخ بالسبب.
    """
    # 1. التحقق من البيانات
    data = load_data()
    if not data:
        raise Exception("❌ فشل: ملف data.json غير موجود أو تالف. ارفع ملف وورد أولاً.")

    context = build_full_context(data)
    if not context or context == "لا توجد بيانات.":
        raise Exception("❌ فشل: بيانات الجامعة فارغة. ارفع ملف وورد يحتوي على معلومات.")

    # 2. التحقق من Groq
    if not client:
        raise Exception("❌ فشل: مفتاح Groq غير موجود. تأكد من إضافته في Secrets.")

    # 3. محاولة التوليد دفعة واحدة
    prompt = f"""أنت مولد بيانات تدريب. قم بتوليد {num_questions} سؤالاً وإجابة متنوعة باللغة العربية عن الجامعة.

معلومات الجامعة:
{context[:3000]}

اكتب الأسئلة والأجوبة بأي صيغة تريد. المهم أن يكون كل سؤال متبوعاً بجوابه."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        result = response.choices[0].message.content
        
        if not result or len(result) < 50:
            raise Exception("❌ فشل: رد Groq فارغ أو قصير جداً. حاول مرة أخرى.")
        
        qa_pairs = extract_qa_pairs(result)
        
        if not qa_pairs or len(qa_pairs) == 0:
            raise Exception(f"❌ فشل: لم يتم استخراج أي سؤال من رد Groq. الرد كان:\n{result[:300]}")
        
        memory = load_memory()
        for question, answer in qa_pairs:
            memory.append({
                "question": question,
                "answer": answer,
                "created": datetime.datetime.now().isoformat()
            })
        save_memory(memory)
        
        if progress_callback:
            progress_callback(1.0)
        
        return memory
        
    except Exception as e:
        error_msg = str(e)
        if "❌" not in error_msg:
            error_msg = f"❌ فشل الاتصال بـ Groq: {error_msg}"
        raise Exception(error_msg)

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
- ابحث عن اسم التخصص. إذا وجدته: قدم تفاصيله كاملة. لا تذكر أي تخصص آخر.
- إذا لم تجده: قل "هذا التخصص غير موجود في سجلاتي."

*** السيناريو 2: سؤال عام عن جميع التخصصات ***
- قدم قائمة بأسماء التخصصات فقط، بدون تفاصيل.

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
- قل: "لا تتوفر لدي بيانات حالياً."

[محظورات]
- لا تخترع تخصصاً غير موجود. لا تخمن.
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
# 9. بناء السياق الكامل
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
