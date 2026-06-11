"""
الخدمات الأساسية: البيانات + الذكاء الاصطناعي
"""
import json
import os
from datetime import datetime
from groq import Groq
from config import *

# ======== عميل Groq ========
# يجب وضع مفتاح Groq في متغير بيئة أو هنا
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
groq_client = Groq(api_key=GROQ_API_KEY)

# ======== دوال البيانات ========
def load_json(filepath, default={}):
    """تحميل ملف JSON"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    """حفظ ملف JSON"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======== البيانات المتخصصة ========
def get_all_info():
    """تجميع كل معلومات الجامعة"""
    info = load_json(INFO_FILE, {"info": ""})
    schedules = load_json(SCHEDULES_FILE, {"schedules": ""})
    fees = load_json(FEES_FILE, {"fees": ""})
    contacts = load_json(CONTACTS_FILE, {"contacts": ""})
    
    combined = f"""
    معلومات عامة: {info.get('info', '')}
    الجداول الدراسية: {schedules.get('schedules', '')}
    الرسوم: {fees.get('fees', '')}
    جهات الاتصال: {contacts.get('contacts', '')}
    """
    return combined

def get_specific_info(category):
    """الحصول على معلومات حسب الفئة"""
    mapping = {
        "info": INFO_FILE,
        "schedules": SCHEDULES_FILE,
        "fees": FEES_FILE,
        "contacts": CONTACTS_FILE
    }
    data = load_json(mapping.get(category, INFO_FILE))
    # استخراج القيمة الأولى
    if data:
        return list(data.values())[0] if data else ""
    return ""

def update_data(category, content):
    """تحديث بيانات فئة معينة"""
    mapping = {
        "info": (INFO_FILE, "info"),
        "schedules": (SCHEDULES_FILE, "schedules"),
        "fees": (FEES_FILE, "fees"),
        "contacts": (CONTACTS_FILE, "contacts")
    }
    filepath, key = mapping.get(category)
    save_json(filepath, {key: content})

# ======== سجل الأسئلة ========
def log_question(question, reply, user_ip="طالب"):
    """تسجيل سؤال في السجل"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "reply": reply[:100] + "...",  # ملخص
        "user": user_ip
    }
    logs = load_json(LOGS_FILE, {"logs": []})
    logs["logs"].append(log_entry)
    # الاحتفاظ بآخر 100 سؤال فقط
    logs["logs"] = logs["logs"][-100:]
    save_json(LOGS_FILE, logs)

def get_logs():
    """استرجاع السجلات"""
    return load_json(LOGS_FILE, {"logs": []}).get("logs", [])

# ======== الذكاء الاصطناعي ========
SYSTEM_PROMPT_TEMPLATE = """أنت المساعد الذكي لفرع جامعة القرآن الكريم والعلوم الإسلامية في غيل باوزير، حضرموت، اليمن.
أنت خبير في شؤون الجامعة وتعرف كل التفاصيل. أجب على أسئلة الطلاب بدقة واحترافية.

معلومات الجامعة الحالية:
{context}

تعليمات:
- أجب باللغة العربية الفصحى الميسرة أو العامية المفهومة
- كن موجزًا ومفيدًا
- إذا لم تجد الإجابة في المعلومات المتاحة، قل: "لم أجد هذه المعلومة في قاعدة البيانات. يرجى التواصل مع إدارة الفرع على الرقم الموجود في جهات الاتصال."
- لا تختلق معلومات غير موجودة
- استخدم الإيموجي باعتدال
"""

def ask_ai(question, category=None):
    """إرسال سؤال إلى Groq مع فئة محددة"""
    # إذا تم تحديد فئة، نركز على تلك المعلومات
    if category:
        context = get_specific_info(category)
    else:
        context = get_all_info()
    
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context[:3000])  # حد أقصى للسياق
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ حدث خطأ تقني: {str(e)}. يرجى المحاولة لاحقًا أو الاتصال بالإدارة."
    
    # تسجيل السؤال
    log_question(question, reply)
    return reply

def smart_classify(question):
    """تصنيف ذكي للسؤال لتحديد الفئة المناسبة"""
    question_lower = question.lower()
    if any(word in question_lower for word in ["جدول", "محاضرات", "مواد", "مستوى"]):
        return "schedules"
    elif any(word in question_lower for word in ["رسوم", "فلوس", "دفع", "قسط", "مبلغ"]):
        return "fees"
    elif any(word in question_lower for word in ["اتصال", "رقم", "هاتف", "موقع", "عنوان", "أين"]):
        return "contacts"
    else:
        return None  # عام
