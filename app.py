import streamlit as st
import json
import os
from services import ask_ai, smart_classify

# إعداد الصفحة (يجب أن يكون أول أمر Streamlit)
st.set_page_config(
    page_title="جامعة القرآن الكريم والعلوم الإسلامية",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- إدارة البيانات (data.json) ---
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "info": "معلومات عامة عن الجامعة...",
            "schedules": "لا توجد جداول متاحة حالياً.",
            "exams": "مواعيد الامتحانات لم تحدد بعد.",
            "fees": "يرجى مراجعة شؤون الطلاب للرسوم.",
            "contacts": "رقم الهاتف: 0000000",
            "majors": "القرآن وعلومه، المحاسبة، الإدارة..."
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- إدراج كود التصميم CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Tajawal:wght@400;500;700&display=swap');

    /* إعدادات الاتجاه والخلفية المتحركة */
    .stApp {
        direction: rtl;
        background: linear-gradient(-45deg, #0a0a0a, #1c1c1c, #111111, #252525);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
        font-family: 'Tajawal', sans-serif;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* الحاوية الزجاجية الرئيسية */
    .block-container {
        background: rgba(15, 15, 15, 0.5);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 30px;
        padding: 3rem !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
        border: 1px solid rgba(255, 215, 0, 0.15);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* إزالة الخطوط السفلية */
    h1, h2, h3, h4, h5, h6, a {
        text-decoration: none !important;
        border-bottom: none !important;
    }

    /* النصوص والعناوين */
    .basmala {
        font-family: 'Amiri', serif;
        text-align: center;
        font-size: 2.2em;
        color: #FFD700;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
        margin-bottom: 5px;
    }
    .uni-title {
        text-align: center;
        font-size: 2.8em;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 0px;
        padding-bottom: 10px;
    }
    .branch-title {
        text-align: center;
        font-size: 1.4em;
        color: #e0e0e0;
        margin-top: -10px;
        margin-bottom: 20px;
        font-weight: 500;
    }
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.8), transparent);
        margin: 25px 0;
        opacity: 0.7;
    }

    /* تصميم بطاقات الخدمات (الأزرار) */
    .stButton > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 15px !important;
        color: white !important;
        padding: 15px 5px !important;
        font-size: 1.1em !important;
        font-weight: bold !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton > button:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 10px 20px rgba(255, 215, 0, 0.4) !important;
        border-color: #FFD700 !important;
        background: rgba(255, 215, 0, 0.1) !important;
    }

    /* تصميم منطقة الدردشة */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stChatMessage"]:nth-child(even) {
        border-right: 4px solid #FFD700 !important; /* لون المساعد */
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        border-right: 4px solid #C0C0C0 !important; /* لون المستخدم */
    }

    /* حقل إدخال الدردشة */
    .stChatInputContainer {
        background: rgba(10, 10, 10, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 25px !important;
        padding: 5px !important;
    }
    .stChatInputContainer:focus-within {
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.6) !important;
        border-color: #FFD700 !important;
    }
    .stChatInputContainer textarea {
        color: #ffffff !important;
        font-size: 1.1em !important;
    }

    /* إخفاء حقوق Streamlit أسفل الصفحة لتنظيف الواجهة */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- ترويسة التطبيق ---
st.markdown("<div class='basmala'>بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>", unsafe_allow_html=True)
st.markdown("<div class='uni-title'>جامعة القرآن الكريم والعلوم الإسلامية</div>", unsafe_allow_html=True)
st.markdown("<div class='branch-title'>المساعد الذكي - فرع غيل باوزير</div>", unsafe_allow_html=True)
st.markdown("<div class='gold-divider'></div>", unsafe_allow_html=True)

# --- حالة الجلسة للدردشة ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "أهلاً بك في المساعد الذكي للجامعة. كيف يمكنني خدمتك اليوم؟"}]

# --- بطاقات الخدمات (أزرار الزجاج) ---
col1, col2, col3, col4, col5 = st.columns(5)
card_clicked_text = None

with col1:
    if st.button("جداول المحاضرات"): card_clicked_text = "أريد تفاصيل عن جداول المحاضرات"
with col2:
    if st.button("الامتحانات"): card_clicked_text = "متى تبدأ الامتحانات وما هي الجداول؟"
with col3:
    if st.button("الرسوم الدراسية"): card_clicked_text = "أريد تفاصيل عن الرسوم الدراسية وطرق السداد"
with col4:
    if st.button("جهات الاتصال"): card_clicked_text = "كيف يمكنني التواصل مع إدارة الفرع؟"
with col5:
    if st.button("التخصصات"): card_clicked_text = "ما هي التخصصات الأكاديمية المتاحة؟"

st.markdown("<br>", unsafe_allow_html=True)

# --- عرض سجل المحادثة ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- استقبال المدخلات (سواء من البطاقات أو من حقل النص) ---
user_input = st.chat_input("اكتب استفسارك هنا...")
prompt = card_clicked_text or user_input

if prompt:
    # إضافة وعرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # المعالجة عبر الذكاء الاصطناعي
    category = smart_classify(prompt)
    db_data = load_data()
    context_data = db_data.get(category, db_data.get("info", ""))
    
    response = ask_ai(prompt, category, context_data)
    
    # إضافة وعرض رسالة المساعد
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# --- لوحة الإدارة (في الشريط الجانبي) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#FFD700;'>لوحة الإدارة ⚙️</h2>", unsafe_allow_html=True)
    admin_password = st.text_input("كلمة المرور", type="password")
    
    if admin_password == "admin123":
        st.success("تم تسجيل الدخول بصلاحيات المدير")
        current_data = load_data()
        
        with st.form("admin_dashboard"):
            st.markdown("### تحديث بيانات الجامعة")
            new_info = st.text_area("معلومات عامة", value=current_data.get("info", ""))
            new_schedules = st.text_area("الجداول الدراسية", value=current_data.get("schedules", ""))
            new_exams = st.text_area("الامتحانات", value=current_data.get("exams", ""))
            new_fees = st.text_area("الرسوم الدراسية", value=current_data.get("fees", ""))
            new_contacts = st.text_area("جهات الاتصال", value=current_data.get("contacts", ""))
            new_majors = st.text_area("التخصصات المتاحة", value=current_data.get("majors", ""))
            
            if st.form_submit_button("حفظ البيانات في قاعدة JSON"):
                updated_data = {
                    "info": new_info,
                    "schedules": new_schedules,
                    "exams": new_exams,
                    "fees": new_fees,
                    "contacts": new_contacts,
                    "majors": new_majors
                }
                save_data(updated_data)
                st.success("تم التحديث بنجاح!")
    elif admin_password:
        st.error("كلمة المرور غير صحيحة")
