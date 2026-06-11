import streamlit as st
import json
import os
from datetime import datetime

# استدعاء دوال الذكاء الاصطناعي الخاصة بك (تأكد من وجود ملف services.py في نفس المجلد)
try:
    from services import ask_ai, smart_classify
except ImportError:
    st.warning("⚠️ يرجى التأكد من وجود ملف `services.py` الذي يحتوي على دوال الذكاء الاصطناعي.")

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
# 2. تصميم CSS الملكي الفاخر (Royal Glassmorphism & Auto-Scroll)
# ==========================================
st.markdown("""
<style>
/* خلفية داكنة ملكية (أسود أوبسيديان مع توهج ذهبي خافت) */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1a1500 0%, #05070a 40%, #020305 100%);
    background-attachment: fixed;
    color: #e6e0d4;
}

/* الحاوية الزجاجية المركزية (تأثير الزجاج المصقول) */
.block-container {
    background: linear-gradient(145deg, rgba(20, 22, 28, 0.6), rgba(5, 7, 10, 0.8));
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
    border-radius: 30px;
    border: 1px solid rgba(212, 175, 55, 0.15);
    border-top: 1px solid rgba(255, 223, 115, 0.4);
    box-shadow: 0 40px 80px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(212, 175, 55, 0.05);
    padding: 3.5rem 2rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
}

/* النصوص الذهبية الفاخرة (تأثير الذهب السائل) */
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap');
.basmala {
    font-family: 'Amiri', serif;
    font-size: 2.8rem;
    text-align: center;
    background: linear-gradient(to bottom, #ffefaa, #d4af37, #997a15);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 10px;
    text-shadow: 0px 5px 25px rgba(212, 175, 55, 0.4);
}

.uni-title {
    font-size: 2.3rem;
    text-align: center;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 5px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
}
.uni-title span { 
    color: #d4af37; 
    filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.6));
}

.branch-title {
    font-size: 1.3rem;
    text-align: center;
    color: #b3a895;
    letter-spacing: 2px;
    margin-bottom: 30px;
    font-weight: 300;
}

/* فاصل ذهبي متوهج */
hr {
    border: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(212, 175, 55, 0.8), transparent);
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
    margin: 35px 0;
}

/* ========================================= */
/* شريط الأزرار الديناميكي (التمرير التلقائي) */
/* ========================================= */
@keyframes autoPan {
    0% { transform: translateX(10%); }
    100% { transform: translateX(-30%); }
}

@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: visible !important;
        padding-bottom: 25px !important;
        padding-top: 15px !important;
        animation: autoPan 15s ease-in-out infinite alternate;
    }
    
    [data-testid="stHorizontalBlock"]:hover, 
    [data-testid="stHorizontalBlock"]:active,
    [data-testid="stHorizontalBlock"]:focus-within {
        animation-play-state: paused !important;
    }

    [data-testid="column"] {
        min-width: 170px !important; 
        flex: 0 0 auto !important;
        width: auto !important;
        padding: 0 8px !important;
    }
}

/* تصميم أزرار الخدمات (زجاج أسود مع إطار ذهبي) */
div.stButton > button {
    background: linear-gradient(135deg, rgba(30, 35, 40, 0.6), rgba(10, 12, 15, 0.9)) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-top: 1px solid rgba(255, 230, 150, 0.6) !important;
    border-radius: 20px !important;
    color: #f4ebd8 !important;
    padding: 18px 20px !important;
    width: 100% !important;
    height: auto !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    font-size: 1.15rem !important;
    font-weight: bold !important;
    white-space: nowrap !important;
}

div.stButton > button:hover {
    transform: translateY(-8px) scale(1.02) !important;
    background: linear-gradient(135deg, rgba(40, 45, 50, 0.8), rgba(20, 25, 30, 0.9)) !important;
    border-color: #d4af37 !important;
    color: #ffffff !important;
    box-shadow: 0 15px 40px rgba(212, 175, 55, 0.35), 0 0 15px rgba(212, 175, 55, 0.2) inset !important;
}

/* رسائل الدردشة (لمسة فخمة) */
[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(15, 18, 25, 0.7), rgba(5, 8, 12, 0.9)) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-right: 4px solid #d4af37 !important;
    border-radius: 20px !important;
    padding: 1.8rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
    color: #e6e0d4 !important;
}

/* كبسولة الإدخال (حقل النص العائم) */
[data-testid="stChatInput"] {
    background: rgba(5, 7, 10, 0.9) !important;
    backdrop-filter: blur(30px) !important;
    border: 1px solid rgba(212, 175, 55, 0.4) !important;
    border-radius: 40px !important;
    box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 20px rgba(212, 175, 55, 0.1) !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #ffd700 !important;
    box-shadow: 0 0 40px rgba(212, 175, 55, 0.5) !important;
    transform: translateY(-2px) !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1.1rem !important;
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
# 5. شريط البطاقات الأفقي (Swipeable & Auto-Pan on Mobile)
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
    # 1. طباعة وحفظ رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 2. معالجة الذكاء الاصطناعي
    with st.chat_message("assistant"):
        with st.spinner("جارٍ صياغة الإجابة..."):
            try:
                # تصنيف السؤال لمعرفة القسم المناسب
                category = smart_classify(user_input)
                
                # جلب السياق المناسب من قاعدة البيانات
                context_data = st.session_state.db.get(category, st.session_state.db["info"])
                
                # سؤال المساعد مع إرفاق السياق
                ai_response = ask_ai(user_input, context_data)
            except Exception as e:
                # رسالة خطأ بديلة في حال عدم ربط ملف services بشكل صحيح
                ai_response = f"عذراً، حدث خطأ أثناء معالجة طلبك أو أن دوال الذكاء الاصطناعي غير متصلة بشكل صحيح. التفاصيل: {str(e)}"
            
            st.markdown(ai_response)
    
    # 3. حفظ رسالة المساعد
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# 7. لوحة الإدارة الجانبية
# ==========================================
with st.sidebar:
    st.header("⚙️ لوحة إدارة النظام")
    st.markdown("---")
    
    admin_password = st.text_input("كلمة المرور", type="password")
    
    # من الأفضل لاحقاً استخدام st.secrets["admin_password"] لحماية الباسوورد
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
