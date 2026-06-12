import json
import os
from datetime import datetime
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_مفتاحك_هنا")
groq_client = Groq(api_key=GROQ_API_KEY)

DATA_FILE = "data.json"
LOGS_FILE = "logs.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"info": "", "schedules": "", "exams": "", "fees": "", "contacts": "", "majors": ""}

# ======== شخصية المساعد الذكي ========
SYSTEM_PROMPT = """أنت مساعد ذكي متخصص في فرع جامعة القرآن الكريم والعلوم الإسلامية في غيل باوزير - حضرموت، اليمن.

شخصيتك:
- خبير في شؤون الجامعة والدراسة
- ودود ومحترم ومهذب جداً
- تتكلم العربية الفصحى الميسرة الممزوجة بلهجة حضرموت اللطيفة
- مختصر ومفيد في ردودك
- تستخدم الإيموجي باعتدال لإضفاء لمسة ودية

قاعدة معرفتك الحالية:
{context}

تعليمات صارمة:
1. أجب فقط من المعلومات المتاحة في قاعدة المعرفة
2. إذا لم تجد الإجابة، قل بأدب: "لم أجد هذه المعلومة حالياً. يمكنك التواصل مع إدارة الفرع على الرقم الموجود في جهات الاتصال."
3. لا تختلق أي معلومات غير موجودة
4. إذا سألك الطالب عن شيء خارج نطاق الجامعة، أجب: "أنا متخصص في شؤون الجامعة فقط. كيف يمكنني مساعدتك في أمور الدراسة؟"
5. إذا قال الطالب شكراً، رد بعبارة لطيفة مثل: "العفو، في خدمتك دائماً 🌹"
6. إذا ألقى الطالب السلام، ارد بأحسن منه
7. تذكر دائماً أنك تمثل جامعة القرآن الكريم، فكن مثالياً في أخلاقك وردودك"""

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

def log_question(question, category):
    """تسجيل سؤال في السجل"""
    logs = load_logs()
    logs.append({
        "question": question,
        "category": category,
        "timestamp": datetime.now().isoformat()
    })
    # الاحتفاظ بآخر 1000 سؤال فقط
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_logs(logs)

def get_stats():
    """إرجاع إحصائيات الأسئلة"""
    logs = load_logs()
    
    if not logs:
        return {
            "total": 0,
            "today": 0,
            "top_questions": [],
            "categories": {}
        }
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for log in logs if log["timestamp"].startswith(today))
    
    # تجميع الأسئلة المتشابهة
    question_counts = {}
    category_counts = {}
    
    for log in logs:
        q = log["question"].strip()
        question_counts[q] = question_counts.get(q, 0) + 1
        
        cat = log["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # ترتيب الأسئلة الأكثر شيوعاً
    sorted_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
    top_questions = [{"question": q, "count": c} for q, c in sorted_questions[:10]]
    
    return {
        "total": len(logs),
        "today": today_count,
        "top_questions": top_questions,
        "categories": category_counts
    }

def ask_ai(question, category=None, chat_history=None):
    """إرسال سؤال إلى Groq مع تاريخ المحادثة للسياق"""
    data = load_data()
    
    # بناء السياق من البيانات
    if category and category in data:
        context = data[category]
    else:
        context = f"""
        معلومات عامة: {data.get('info','')}
        الجداول الدراسية: {data.get('schedules','')}
        الامتحانات: {data.get('exams','')}
        الرسوم: {data.get('fees','')}
        جهات الاتصال: {data.get('contacts','')}
        التخصصات: {data.get('majors','')}
        """
    
    system_prompt = SYSTEM_PROMPT.format(context=context[:3000])
    
    # بناء الرسائل مع تاريخ المحادثة
    messages = [{"role": "system", "content": system_prompt}]
    
    # إضافة آخر 6 رسائل من تاريخ المحادثة للسياق
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # إضافة السؤال الحالي إذا لم يكن موجوداً في التاريخ
    if not chat_history or chat_history[-1]["content"] != question:
        messages.append({"role": "user", "content": question})
    
    # تسجيل السؤال
    log_question(question, category or "info")
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ عذراً، حدث خطأ تقني بسيط. يرجى المحاولة مرة أخرى. إذا تكررت المشكلة، تواصل مع الإدارة."

def smart_classify(question):
    """تصنيف ذكي متطور للسؤال"""
    q = question.strip()
    
    # قاموس الكلمات المفتاحية الموسع
    keywords = {
        "schedules": [
            "جدول", "جداول", "محاضرات", "محاضره", "مواد", "ماده", "مستوى",
            "دوام", "حضور", "غياب", "أستاذ", "دكتور", "مدرس", "معلم",
            "حلقة", "حلقات", "قرآن", "تفسير", "فقه", "حديث", "نحو", "بلاغة",
            "أصول", "عقيدة", "سيرة", "تلاوة", "تجويد", "دعوة", "أدب"
        ],
        "exams": [
            "امتحان", "امتحانات", "اختبار", "اختبارات", "نصفي", "نهائي",
            "نتيجة", "نتايج", "درجة", "درجات", "نجاح", "رسوب", "معدل"
        ],
        "fees": [
            "رسوم", "رسومات", "فلوس", "مبلغ", "دفع", "تسديد", "قسط",
            "أقساط", "مالية", "مصاريف", "حوالة", "بنك", "فاتورة", "سعر"
        ],
        "contacts": [
            "اتصال", "رقم", "هاتف", "جوال", "موقع", "عنوان", "وين", "أين",
            "فرع", "إدارة", "شؤون", "مكتب", "بريد", "إيميل", "واتساب"
        ],
        "majors": [
            "تخصص", "تخصصات", "قسم", "أقسام", "شعبة", "شعب", "كلية",
            "دراسة", "منهج", "مقرر", "مسار"
        ]
    }
    
    q_lower = q.lower()
    
    # البحث عن الكلمات المفتاحية
    for category, words in keywords.items():
        if any(word in q_lower for word in words):
            return category
    
    # أسئلة الترحيب
    if any(w in q_lower for w in ["سلام", "مرحبا", "هلا", "أهلا", "السلام"]):
        return "info"
    
    # أسئلة الشكر
    if any(w in q_lower for w in ["شكرا", "شكراً", "مشكور", "جزاك"]):
        return "info"
    
    return "info"

def get_greeting():
    """رسالة ترحيبية ذكية حسب الوقت"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "صباح الخير 🌅"
    elif 12 <= hour < 17:
        return "مساء الخير ☀️"
    elif 17 <= hour < 21:
        return "مساء النور 🌆"
    else:
        return "مساء الخير 🌙"

def get_welcome_message():
    """رسالة ترحيبية كاملة"""
    greeting = get_greeting()
    return f"""{greeting} أهلًا وسهلًا بك في المساعد الذكي لجامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير.

📌 **الخدمات المتاحة:**
📚 جداول المحاضرات
📝 الامتحانات
💰 الرسوم الدراسية
📞 جهات الاتصال
🎓 التخصصات

كيف أقدر أخدمك اليوم؟"""
