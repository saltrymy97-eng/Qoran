import streamlit as st
import json
import os
from datetime import datetime
from services import ask_ai, smart_classify

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(
    page_title="جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير - حضرموت",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. تصميم CSS الفخم
# ==========================================
st.markdown("""
<style>
/* خلفية داكنة متدرجة بطيئة الحركة */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stApp {
    background: linear-gradient(-45deg, #0a0f18, #111a28, #1a2433, #0d141e);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #ffffff;
}

/* حاوية زجاجية مركزية */
.block-container {
    background: rgba(20, 25, 35, 0.4);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(255, 215, 0, 0.15);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
    padding: 3rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
}

/* البسملة */
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap');
.basmala {
    font-family: 'Amiri', serif;
    font-size: 2.8rem;
    text-align: center;
    background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 15px;
    text-shadow: 0px 4px 10px rgba(212, 175, 55, 0.3);
}

/* اسم الجامعة */
.uni-title {
    font-size: 2.4rem;
    text-align: center;
    font-weight: 900;
    background: linear-gradient(135deg, #d4af37, #ffdf73, #d4af37);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 10px;
}

/* اسم الفرع */
.branch-title {
    font-size: 1.4rem;
    text-align: center;
    color: #e0e0e0; /* فضي */
    letter-spacing: 1px;
    margin-bottom: 25px;
}

/* فواصل ذهبية متدرجة */
hr {
    border: 0;
    height: 2px;
    background-image: linear-gradient(to right, rgba(212, 175, 55, 0), rgba(212, 175, 55, 0.8), rgba(212, 175, 55, 0));
    margin: 30px 0;
}

/* لا خطوط تحت أي عنوان */
h1, h2, h3, h4, h5, h6, a {
    text-decoration: none !important;
}

/* إخفاء العناصر الفارغة */
.empty { display: none !important; }

/* 5 بطاقات خدمات زجاجية بتفاعل hover */
div.stButton > button {
    background: rgba(30, 40, 55, 0.5) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 15px !important;
    color: white !important;
    padding: 20px 10px !important;
    width: 100% !important;
    height: 100% !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    font-size: 1.15rem !important;
    font-weight: bold !important;
}

div.stButton > button:hover {
    transform: translateY(-8px) !important;
    background: rgba(40, 50, 70, 0.7) !important;
    border-color: #fcf6ba !important;
    box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4) !important;
    color: #fcf6ba !important;
}

/* منطقة الدردشة الزجاجية */
[data-testid="stChatMessage"] {
    background: rgba(15, 25, 35, 0.6) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 18px !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
}

/* حقل الكتابة العريض الشفاف */
[data-testid="stChatInput"] {
    background: rgba(10, 15, 25, 0.7) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 20px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.7) !important;
    border-color: #fcf6ba !important;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. الدوال وإدارة البيانات
# ==========================================
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # بيانات افتراضية إذا لم يكن الملف موجوداً
    return {
        "info": "معلومات عامة عن فرع جامعة القرآن الكريم والعلوم الإسلامية بغيل باوزير.",
        "schedules": "جداول المحاضرات لجميع المستويات.",
        "fees": "الرسوم الدراسية وطرق الدفع.",
        "contacts": "أرقام التواصل وإيميل الفرع.",
        "majors": "التخصصات المتاحة في الفرع."
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تهيئة الجلسة (Session State)
if "db" not in st.session_state:
    st.session_state.db = load_data()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "auto_question" not in st.session_state:
    st.session_state.auto_question = None

# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="uni-title">🕌 جامعة القرآن الكريم والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="branch-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)

# البطاقات الزجاجية الخمس
col1, col2, col3, col4, col5 = st.columns(5)

if col1.button("📅 جداول المحاضرات"):
    st.session_state.auto_question = "أريد الاستفسار عن جداول المحاضرات"
if col2.button("📝 الامتحانات"):
    st.session_state.auto_question = "ما هي مواعيد وترتيبات الامتحانات؟"
if col3.button("💰 الرسوم الدراسية"):
    st.session_state.auto_question = "أريد معرفة تفاصيل الرسوم الدراسية وطرق السداد"
if col4.button("📞 جهات الاتصال"):
    st.session_state.auto_question = "كيف يمكنني التواصل مع إدارة الفرع؟"
if col5.button("🎓 التخصصات"):
    st.session_state.auto_question = "ما هي التخصصات الأكاديمية المتاحة للتسجيل؟"

st.markdown('<hr>', unsafe_allow_html=True)

# ==========================================
# 5. منطقة الدردشة (الواجهة والمحرك)
# ==========================================
# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# استقبال الإدخال من المستخدم (سواء عبر الكتابة أو الضغط على البطاقات)
user_input = st.chat_input("تفضل بطرح استفسارك هنا...")

# دمج السؤال التلقائي من البطاقة إن وُجد
if st.session_state.auto_question:
    user_input = st.session_state.auto_question
    st.session_state.auto_question = None  # تفريغ بعد الاستخدام

if user_input:
    # 1. طباعة وحفظ رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 2. معالجة الذكاء الاصطناعي
    with st.chat_message("assistant"):
        with st.spinner("جارٍ صياغة الإجابة..."):
            # تصنيف السؤال لمعرفة القسم المناسب
            category = smart_classify(user_input)
            
            # جلب السياق المناسب من قاعدة البيانات
            context_data = st.session_state.db.get(category, st.session_state.db["info"])
            
            # سؤال المساعد مع إرفاق السياق
            ai_response = ask_ai(user_input, context_data)
            
            st.markdown(ai_response)
    
    # 3. حفظ رسالة المساعد
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# 6. شريط جانبي للوحة الإدارة
# ==========================================
with st.sidebar:
    st.header("⚙️ لوحة إدارة النظام")
    st.markdown("---")
    
    admin_password = st.text_input("كلمة المرور", type="password")
    
    if admin_password == "admin123":
        st.success("✅ تم تسجيل الدخول كمسؤول")
        
        # حقول التعديل
        edit_info = st.text_area("معلومات عامة (info)", st.session_state.db.get("info", ""))
        edit_schedules = st.text_area("الجداول (schedules)", st.session_state.db.get("schedules", ""))
        edit_fees = st.text_area("الرسوم (fees)", st.session_state.db.get("fees", ""))
        edit_contacts = st.text_area("جهات الاتصال (contacts)", st.session_state.db.get("contacts", ""))
        edit_majors = st.text_area("التخصصات (majors)", st.session_state.db.get("majors", ""))
        
        if st.button("💾 حفظ التعديلات", use_container_width=True):
            st.session_state.db = {
                "info": edit_info,
                "schedules": edit_schedules,
                "fees": edit_fees,
                "contacts": edit_contacts,
                "majors": edit_majors
            }
            save_data(st.session_state.db)
            st.success("🎉 تم تحديث بيانات الجامعة بنجاح!")
            
    elif admin_password != "":
        st.error("❌ كلمة المرور غير صحيحة")
