"""
╔══════════════════════════════════════════════════════════════╗
║  جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير   ║
║  services.py - نظام الذاكرة الهجين للمساعد الذكي           ║
║  المطور: سالم التريمي                                       ║
║  الإصدار: 4.0 الاحترافي                                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import re
import datetime
import difflib
import time
import random
from groq import Groq

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
DATA_FILE = "data.json"
LOGS_FILE = "logs.json"
MEMORY_FILE = "training_data.json"

MEMORY_MATCH_THRESHOLD = 0.8
MAX_MEMORY_SIZE = 60000

# --- عميل Groq الآمن ---
_client = None

def get_client():
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if key:
            try:
                _client = Groq(api_key=key)
            except Exception:
                _client = None
    return _client

# ==========================================
# 2. إدارة البيانات الأساسية
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
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. نظام الذاكرة
# ==========================================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []

def save_memory(memory):
    if len(memory) > MAX_MEMORY_SIZE:
        memory = memory[-MAX_MEMORY_SIZE:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def add_to_memory(question, answer):
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
# 4. توليد الأسئلة بالقوالب (بدون Groq)
# ==========================================
def extract_info_from_text(text, key_words):
    """استخراج المعلومات من النص بناءً على كلمات مفتاحية"""
    info = {}
    for key, words in key_words.items():
        for word in words:
            pattern = rf'{word}\s*[:.]?\s*(.+?)(?:\n|$)'
            match = re.search(pattern, text)
            if match:
                info[key] = match.group(1).strip()
                break
    return info

def generate_questions_from_majors(majors_dict, fees_text=""):
    """توليد أسئلة من التخصصات"""
    questions = []
    
    # قوالب الأسئلة لكل تخصص
    fee_templates = [
        "كم رسوم تخصص {name}؟",
        "كم تبلغ رسوم تخصص {name}؟",
        "ما هي رسوم تخصص {name}؟",
        "كم سعر تخصص {name}؟",
        "كم تكلفة تخصص {name}؟",
        "بكم رسوم تخصص {name}؟",
        "كم اقساط تخصص {name}؟",
        "كم تدفع لتخصص {name}؟",
        "كم المصاريف الدراسية لتخصص {name}؟",
        "هل رسوم تخصص {name} مرتفعة؟",
    ]
    
    duration_templates = [
        "كم مدة دراسة تخصص {name}؟",
        "كم سنة دراسة تخصص {name}؟",
        "كم عام دراسة تخصص {name}؟",
        "ما هي مدة تخصص {name}؟",
        "كم فصل دراسي في تخصص {name}؟",
        "هل دراسة تخصص {name} طويلة؟",
        "كم تستغرق دراسة تخصص {name}؟",
    ]
    
    jobs_templates = [
        "ما هي فرص عمل تخصص {name}؟",
        "ماذا يعمل خريج تخصص {name}؟",
        "أين يتوظف خريج تخصص {name}؟",
        "هل تخصص {name} مطلوب في سوق العمل؟",
        "ما هي وظائف تخصص {name}؟",
        "هل يوجد طلب على تخصص {name}؟",
        "ما هو مستقبل تخصص {name}؟",
    ]
    
    description_templates = [
        "اشرح لي تخصص {name}",
        "ما هو تخصص {name}؟",
        "عرف لي تخصص {name}",
        "ما تعريف تخصص {name}؟",
        "ماذا يدرس طالب تخصص {name}؟",
        "ما هي مواد تخصص {name}؟",
        "ما منهج تخصص {name}؟",
        "ما مقررات تخصص {name}؟",
    ]
    
    existence_templates = [
        "هل يوجد تخصص {name}؟",
        "هل هناك تخصص {name}؟",
        "هل تخصص {name} متاح؟",
        "هل تخصص {name} موجود في الجامعة؟",
        "هل يمكنني دراسة {name}؟",
        "هل جامعة القرآن تدرس {name}؟",
    ]
    
    comparison_templates = [
        "قارن بين تخصص {name1} وتخصص {name2}",
        "أيهما أفضل {name1} أم {name2}؟",
        "الفرق بين {name1} و {name2}",
        "هل {name1} أصعب من {name2}؟",
        "أيهما له فرص عمل أكثر {name1} أم {name2}؟",
    ]
    
    if isinstance(majors_dict, dict):
        majors_list = list(majors_dict.keys())
        
        for name, details in majors_dict.items():
            # استخراج معلومات محددة من التفاصيل
            fee_match = re.search(r'رسوم[:\s]*(\d+)\s*ريال', details)
            duration_match = re.search(r'مدة[:\s]*(\d+)\s*(?:سنوات|سنة)', details)
            
            # أسئلة الرسوم
            for template in fee_templates:
                q = template.format(name=name)
                if fee_match:
                    a = f"رسوم تخصص {name} هي {fee_match.group(1)} ريال يمني للفصل الدراسي الواحد."
                else:
                    a = f"للتعرف على رسوم تخصص {name}، يرجى التواصل مع الإدارة المالية."
                questions.append({"question": q, "answer": a})
            
            # أسئلة المدة
            for template in duration_templates:
                q = template.format(name=name)
                if duration_match:
                    a = f"مدة دراسة تخصص {name} هي {duration_match.group(1)} سنوات."
                else:
                    a = f"مدة دراسة تخصص {name} هي 4 سنوات للحصول على درجة البكالوريوس."
                questions.append({"question": q, "answer": a})
            
            # أسئلة فرص العمل
            for template in jobs_templates:
                q = template.format(name=name)
                jobs_match = re.search(r'فرص العمل[:]\s*(.+?)(?:\n|$)', details)
                if jobs_match:
                    a = f"فرص عمل تخصص {name} تشمل: {jobs_match.group(1)}"
                else:
                    a = f"خريجو تخصص {name} لديهم فرص عمل متنوعة في القطاعين العام والخاص."
                questions.append({"question": q, "answer": a})
            
            # أسئلة الوصف
            for template in description_templates:
                q = template.format(name=name)
                a = f"تخصص {name}: {details[:300]}"
                questions.append({"question": q, "answer": a})
            
            # أسئلة الوجود
            for template in existence_templates:
                q = template.format(name=name)
                a = f"نعم، تخصص {name} متاح في جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير."
                questions.append({"question": q, "answer": a})
        
        # أسئلة المقارنة بين التخصصات
        for i in range(len(majors_list)):
            for j in range(i + 1, len(majors_list)):
                name1 = majors_list[i]
                name2 = majors_list[j]
                for template in comparison_templates:
                    q = template.format(name1=name1, name2=name2)
                    a = f"تخصص {name1}: {majors_dict.get(name1, '')[:200]}\n\nتخصص {name2}: {majors_dict.get(name2, '')[:200]}"
                    questions.append({"question": q, "answer": a})
    
    return questions

def generate_questions_from_general(data):
    """توليد أسئلة عامة من جميع الأيقونات"""
    questions = []
    
    # أسئلة عن الرسوم العامة
    fees_templates = [
        "كم رسوم الجامعة؟",
        "كم تبلغ رسوم الجامعة؟",
        "هل يوجد تقسيط للرسوم؟",
        "كيف اسدد الرسوم الدراسية؟",
        "هل هناك منح دراسية؟",
        "كم رسوم التسجيل في الجامعة؟",
        "هل يمكن تقسيط الرسوم؟",
        "ما هي طرق الدفع المتاحة؟",
        "هل يوجد خصم على الرسوم؟",
        "كم رسوم إعادة القيد؟",
    ]
    
    for template in fees_templates:
        a = data.get("fees", "يرجى التواصل مع الإدارة المالية للاستفسار عن الرسوم.")
        questions.append({"question": template, "answer": a[:500]})
    
    # أسئلة عن الامتحانات
    exam_templates = [
        "متى تبدأ الامتحانات؟",
        "متى تبدأ الامتحانات النصفية؟",
        "متى تبدأ الامتحانات النهائية؟",
        "كيف يتم التقييم في الجامعة؟",
        "كم درجة النجاح؟",
        "متى تظهر النتائج؟",
        "ما هو نظام الامتحانات؟",
        "كيف احسب المعدل؟",
        "متى موعد الامتحانات؟",
        "كم مدة الامتحانات؟",
    ]
    
    for template in exam_templates:
        a = data.get("exams", "يرجى التواصل مع شؤون الطلاب للاستفسار عن الامتحانات.")
        questions.append({"question": template, "answer": a[:500]})
    
    # أسئلة عن الجداول
    schedule_templates = [
        "متى تبدأ المحاضرات؟",
        "كم ساعة دراسة في اليوم؟",
        "متى يبدأ الدوام؟",
        "كم يوم دراسة في الأسبوع؟",
        "ما هو نظام الحضور؟",
        "متى تبدأ السنة الدراسية؟",
        "متى ينتهي الفصل الدراسي؟",
        "هل يوجد دراسة يوم الخميس؟",
        "كم محاضرة في الأسبوع؟",
        "ما هي ساعات الدوام الرسمي؟",
    ]
    
    for template in schedule_templates:
        a = data.get("schedules", "يرجى مراجعة شؤون الطلاب للاطلاع على الجداول الدراسية.")
        questions.append({"question": template, "answer": a[:500]})
    
    # أسئلة عن التواصل
    contact_templates = [
        "أين تقع الجامعة؟",
        "ما هو عنوان الجامعة؟",
        "رقم هاتف الجامعة",
        "كيف اتواصل مع الجامعة؟",
        "البريد الالكتروني للجامعة",
        "ساعات العمل في الجامعة",
        "متى يفتح التسجيل؟",
        "كيف أصل إلى الجامعة؟",
        "هل يوجد واتساب للجامعة؟",
        "أين موقع الجامعة؟",
    ]
    
    for template in contact_templates:
        a = data.get("contacts", "يرجى التواصل مع إدارة الفرع للاستفسار.")
        questions.append({"question": template, "answer": a[:500]})
    
    # أسئلة عن معلومات عامة
    info_templates = [
        "متى تأسست الجامعة؟",
        "هل الجامعة معتمدة؟",
        "ما هي رؤية الجامعة؟",
        "ما هي رسالة الجامعة؟",
        "ما هي أهداف الجامعة؟",
        "هل الجامعة مختلطة؟",
        "كم عدد طلاب الجامعة؟",
        "ما هي الخدمات الطلابية؟",
        "هل يوجد سكن للطلاب؟",
        "ما هي الأنشطة الطلابية؟",
    ]
    
    for template in info_templates:
        a = data.get("info", "جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير.")
        questions.append({"question": template, "answer": a[:500]})
    
    return questions

def inject_questions_to_memory(questions):
    """حقن الأسئلة في الذاكرة"""
    memory = load_memory()
    existing_questions = {item["question"].strip() for item in memory}
    
    added = 0
    for qa in questions:
        if qa["question"].strip() not in existing_questions:
            memory.append({
                "question": qa["question"].strip(),
                "answer": qa["answer"],
                "created": datetime.datetime.now().isoformat()
            })
            existing_questions.add(qa["question"].strip())
            added += 1
    
    save_memory(memory)
    return added

# ==========================================
# 5. توليد بيانات التدريب (هجين: قوالب + Groq)
# ==========================================
def generate_training_data(num_questions=50000, progress_callback=None):
    """
    توليد الأسئلة بطريقة هجينة:
    1. القوالب: تولد ~80% من الأسئلة مباشرة من البيانات
    2. Groq: يضيف ~20% أسئلة إبداعية غير موجودة في القوالب
    """
    data = load_data()
    if not data:
        raise Exception("❌ فشل: ملف data.json غير موجود. ارفع ملف وورد أولاً.")
    
    # --- المرحلة 1: التوليد بالقوالب ---
    if progress_callback:
        progress_callback(0.1)
    
    # أسئلة التخصصات
    majors_questions = generate_questions_from_majors(data.get("majors", {}), data.get("fees", ""))
    inject_questions_to_memory(majors_questions)
    
    if progress_callback:
        progress_callback(0.4)
    
    # أسئلة عامة
    general_questions = generate_questions_from_general(data)
    inject_questions_to_memory(general_questions)
    
    if progress_callback:
        progress_callback(0.6)
    
    # --- المرحلة 2: التوليد بـ Groq (أسئلة إبداعية) ---
    client = get_client()
    if client:
        context = build_full_context(data)
        memory = load_memory()
        existing_count = len(memory)
        target_from_groq = min(num_questions - existing_count, 10000)
        
        if target_from_groq > 0:
            batch_size = 50
            batches = target_from_groq // batch_size
            
            for i in range(batches):
                if progress_callback:
                    progress_callback(0.6 + (0.3 * i / batches))
                
                prompt = f"""أنت مساعد ذكي. قم بتوليد {batch_size} سؤالاً وإجابة جديدة لم تغطها الأسئلة الشائعة.

معلومات الجامعة:
{context[:3000]}

اكتب الأسئلة والأجوبة بصيغة:
س: السؤال
ج: الجواب"""
                
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=2000
                    )
                    result = response.choices[0].message.content
                    
                    qa_pairs = re.findall(r'س:\s*(.+?)\s*\n\s*ج:\s*(.+?)(?=\n\s*س:|\Z)', result, re.DOTALL)
                    
                    for q, a in qa_pairs:
                        if q.strip() and a.strip():
                            add_to_memory(q.strip(), a.strip())
                except Exception:
                    pass
    
    if progress_callback:
        progress_callback(1.0)
    
    return load_memory()

# ==========================================
# 6. نظام الذكاء الاصطناعي الهجين
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

    client = get_client()
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
# 7. شخصية المساعد الذكي
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
# 8. السجل والإحصائيات
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
# 9. التصنيف الذكي
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
# 10. بناء السياق الكامل
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
# 11. دوال الترحيب والمساعدة
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
