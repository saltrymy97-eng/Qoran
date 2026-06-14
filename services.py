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
from groq import Groq

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
DATA_FILE = "data.json"
LOGS_FILE = "logs.json"

MEMORY_MATCH_THRESHOLD = 0.8

# --- عميل Groq الآمن ---
def get_client():
    key = os.getenv("GROQ_API_KEY")
    if key:
        try:
            return Groq(api_key=key)
        except Exception:
            pass
    return None

# ==========================================
# 2. إدارة البيانات الأساسية
# ==========================================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "info": "", "schedules": "", "exams": "", "fees": "", "contacts": "", "majors": {}
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. نظام الذاكرة (الأسئلة والأجوبة)
# ==========================================
def load_memory():
    memory_file = "training_data.json"
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(memory):
    with open("training_data.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def add_to_memory(question, answer):
    memory = load_memory()
    memory.append({"question": question, "answer": answer})
    save_memory(memory)

def find_best_match_memory(question, memory):
    if not memory:
        return None
    q_clean = question.strip().lower()
    best_score = 0.0
    best_match = None
    for item in memory:
        score = difflib.SequenceMatcher(None, q_clean, item["question"].strip().lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = item
    return best_match if best_score >= MEMORY_MATCH_THRESHOLD else None

def get_memory_stats():
    memory = load_memory()
    logs = load_logs()
    return {
        "total_questions": len(memory),
        "memory_responses": sum(1 for log in logs if log.get("source") == "memory"),
        "groq_responses": sum(1 for log in logs if log.get("source") == "groq")
    }

# ==========================================
# 4. نظام الذكاء الاصطناعي الهجين
# ==========================================
SYSTEM_PROMPT = """أنت موظف استقبال محترف في جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير بحضرموت.
أجب على سؤال الطالب بناءً على المعلومات التالية فقط. لا تخترع أي معلومات.
إذا كانت المعلومات لا تحتوي على إجابة السؤال، قل بالضبط: 'عذراً، هذه المعلومة غير متوفرة لدي حالياً، يرجى التواصل مع شؤون الطلاب.'

المعلومات:
{context}"""

def ask_ai(question, category=None, chat_history=None):
    if chat_history is None:
        chat_history = []

    # 1. البحث في الذاكرة
    memory = load_memory()
    match = find_best_match_memory(question, memory)
    if match:
        log_question(question, category or "info", source="memory")
        return match["answer"]

    # 2. البحث في البيانات
    data = load_data()
    context = data.get(category) if category in data else ""
    if not context:
        context = "\n\n".join([f"{k}: {v}" for k, v in data.items() if v])

    if not context.strip():
        return "لا توجد بيانات متاحة."

    # 3. إرسال إلى Groq
    client = get_client()
    if not client:
        return context[:500]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(context=context[:1500])},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=400
        )
        answer = response.choices[0].message.content
        add_to_memory(question, answer)
        log_question(question, category or "info", source="groq")
        return answer
    except Exception:
        return context[:500]

def find_best_match_major(question, majors_dict):
    if not isinstance(majors_dict, dict):
        return None, None
    question_lower = question.lower()
    for name, data in majors_dict.items():
        if name.lower() in question_lower:
            return name, data
    return None, None

# ==========================================
# 5. السجل والإحصائيات
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
    today_str = datetime.datetime.now().date().isoformat()
    today_count = sum(1 for log in logs if log["timestamp"].startswith(today_str))
    return {
        "total": len(logs),
        "today": today_count,
        "top_questions": [],
        "categories": {},
        "memory_size": len(memory),
        "memory_responses": sum(1 for log in logs if log.get("source") == "memory"),
        "groq_responses": sum(1 for log in logs if log.get("source") == "groq")
    }

# ==========================================
# 6. التصنيف الذكي
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
    return f"{get_greeting()}، أهلاً وسهلاً بك في المساعد الذكي لجامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير. كيف أقدر أخدمك؟"
