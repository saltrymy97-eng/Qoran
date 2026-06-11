import streamlit as st
import json
import os
from datetime import datetime
from services import ask_ai, smart_classify

# ==========================================
# 1. إعداد الصفحة
# ==========================================
st.set_page_config(
    page_title="جامعة القرآن الكريم - فرع غيل باوزير",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. تصميم CSS الفاخر (Ultra-Premium Glassmorphism)
# ==========================================
st.markdown("""
<style>
/* 1. خلفية داكنة فاخرة مع إضاءة محيطية (Ambient Glow) */
.stApp {
    background-color: #070b14;
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(212, 175, 55, 0.08), transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(16, 42, 86, 0.3), transparent 25%);
    background-attachment: fixed;
    color: #f0f0f0;
}

/* 2. الحاوية الزجاجية المركزية مع انعكاس ضوئي */
.block-container {
    background: rgba(12, 18, 28, 0.45);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-top: 1px solid rgba(212, 175, 55, 0.25); /* انعكاس ذهبي علوي */
    box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.8);
    padding: 3.5rem 2rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
}

/* 3. الطباعة والخطوط الفاخرة */
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap');
.basmala {
    font-family: 'Amiri', serif;
    font-size: 2.6rem;
    text-align: center;
    background: linear-gradient(to right, #d4af37, #ffdf73, #fff8d6, #ffdf73, #d4af37);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 5px;
    text-shadow: 0px 4px 20px rgba(212, 175, 55, 0.25);
}

.uni-title {
    font-size: 2.2rem;
    text-align: center;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 5px;
    letter-spacing: 0.5px;
}
.uni-title span { color: #d4af37; } /* تمييز الأيقونة باللون الذهبي */

.branch-title {
    font-size: 1.2rem;
    text-align: center;
    color: #a0aab5;
    letter-spacing: 1.5px;
    margin-bottom: 30px;
    font-weight: 300;
}

/* فاصل ماسي أنيق */
hr {
    border: 0;
    height: 1px;
    background-image: linear-gradient(to right, rgba(212, 175, 55, 0), rgba(212, 175, 55, 0.5), rgba(212, 175, 55, 0));
    margin: 30px 0;
}

/* ========================================= */
/* 4. سحر الجوال: تحويل الأعمدة لشريط تمرير أفقي */
/* ========================================= */
[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    padding-bottom: 15px !important;
    padding-top: 10px !important;
    -ms-overflow-style: none; /* إخفاء شريط التمرير في IE */
    scrollbar-width: none; /* إخفاء شريط التمرير في Firefox */
    scroll-behavior: smooth;
}
[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
    display: none; /* إخفاء شريط التمرير في Chrome/Safari */
}

/* 5. بطاقات الخدمات الفاخرة (تجاوبية) */
div.stButton > button {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-top: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 18px !important;
    color: #e2e8f0 !important;
    padding: 16px 20px !important;
    width: 100% !important;
    min-width: 160px !important; /* يحافظ على عرض الزر في الجوال */
    height: auto !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    white-space: nowrap !important; /* يمنع نزول النص لسطرين */
}

div.stButton > button:hover {
    transform: translateY(-6px) !important;
    background: rgba(212, 175, 55, 0.1) !important;
    border-color: rgba(212, 175, 55, 0.6) !important;
    color: #ffffff !important;
    box-shadow: 0 15px 35px rgba(212, 175, 55, 0.25) !important;
}

/* 6. رسائل الدردشة الملساء */
[data-testid="stChatMessage"] {
    background: rgba(20, 26, 38, 0.5) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
    border-right: 3px solid #d4af37 !important; /* لمسة ذهبية جانبية */
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.2rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
}

/* 7. كبسولة الإدخال العائمة */
[data-testid="stChatInput"] {
    background: rgba(10, 14, 20, 0.85) !important;
    backdrop-filter: blur(25px) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 35px !important;
    box-shadow: 0 15px 45px rgba(0,0,0,0.6) !important;
    padding: 8px 15px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #d4af37 !important;
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.35) !important;
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

if "db" not in st.session_state:
    st.session_state.db = load_data()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "auto_question" not in st.session_state:
    st.session_state.auto_question = None

# ==========================================
# 4. الواجهة الرئيسية (الهيدر)
# ==========================================
st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="uni-title"><span>🕌</span> جامعة القرآن الكريم والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="branch-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)

# ==========================================
# 5. شريط البطاقات الأفقي (Swipeable on Mobile)
# ==========================================
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
# 6. محرك الدردشة
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("تفضل بطرح استفسارك هنا...")

if st.session_state.auto_question:
    user_input = st.session_state.auto_question
    st.session_state.auto_question = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("جارٍ صياغة الإجابة..."):
            # محاكاة الاتصال بالخدمات (قم بفك التعليق عند دمج ملف services الخاص بك)
            # category = smart_classify(user_input)
            # context_data = st.session_state.db.get(category, st.session_state.db["info"])
            # ai_response = ask_ai(user_input, context_data)
            
            # إجابة مؤقتة للتجربة
            ai_response = "مرحباً بك! أنا المساعد الذكي لجامعة القرآن الكريم - فرع غيل باوزير. كيف يمكنني خدمتك اليوم؟"
            st.markdown(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# 7. لوحة الإدارة الآمنة الجانبية
# ==========================================
with st.sidebar:
    st.header("⚙️ لوحة إدارة النظام")
    st.markdown("---")
    
    admin_password = st.text_input("كلمة المرور", type="password")
    
    # يفضل استخدام st.secrets بدلاً من كتابة الباسوورد هنا لاحقاً
    if admin_password == "admin123":
        st.success("✅ تم تسجيل الدخول كمسؤول")
        
        edit_info = st.text_area("معلومات عامة", st.session_state.db.get("info", ""))
        edit_schedules = st.text_area("الجداول", st.session_state.db.get("schedules", ""))
        edit_fees = st.text_area("الرسوم", st.session_state.db.get("fees", ""))
        edit_contacts = st.text_area("جهات الاتصال", st.session_state.db.get("contacts", ""))
        edit_majors = st.text_area("التخصصات", st.session_state.db.get("majors", ""))
        
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
