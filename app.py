import streamlit as st
import json
import os
from datetime import datetime
from services import ask_ai, smart_classify

# ======== إعدادات التطبيق ========
APP_TITLE = "جامعة القرآن الكريم والعلوم الإسلامية"
APP_SUBTITLE = "فرع غيل باوزير - حضرموت"
APP_ICON = "🕌"

st.set_page_config(
    page_title=f"{APP_TITLE}", 
    page_icon=APP_ICON, 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ======== CSS الاحترافي (المدمج) ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    * {{ font-family: 'El Messiri', sans-serif; }}
    
    .stApp {{ background: linear-gradient(135deg, #02060d 0%, #0a1324 40%, #060e1a 100%) !important; }}

    /* تنظيف الواجهة من أزرار المنصة */
    .stAppDeployButton, [data-testid="stToolbar"], [data-testid="stHeaderActionElements"], #MainMenu, footer {{
        display: none !important;
    }}

    /* تنسيق القائمة المنسدلة */
    [data-testid="stSelectbox"] > div > div {{
        background: rgba(10, 15, 30, 0.85) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
    }}
    
    /* تأثير النص الذهبي */
    .gold-foil-text {{ 
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: bold;
    }}
    .main-title {{ text-align: center; font-size: 2.8em; font-weight: 700; color: #ffffff; margin-bottom: 5px; }}
    .sub-title {{ text-align: center; font-size: 1.2em; color: #a8b2c1; margin-bottom: 30px; }}
    
    /* رسائل الشات */
    [data-testid="stChatMessage"] {{ background: rgba(15, 23, 42, 0.6) !important; border-radius: 20px !important; }}
</style>
""", unsafe_allow_html=True)

# ======== دوال معالجة البيانات ========
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"info": "", "schedules": "", "fees": "", "contacts": "", "majors": ""}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======== الجلسة والواجهة ========
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown(f'<div class="main-title gold-foil-text">{APP_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

# القائمة المنسدلة
category_map = {
    "📌 عام": "info",
    "📚 الجداول والمحاضرات": "schedules",
    "💰 الرسوم الدراسية": "fees",
    "📞 جهات الاتصال": "contacts",
    "🎓 التخصصات": "majors"
}

selected_cat_name = st.selectbox("اختر نوع الاستفسار:", list(category_map.keys()))
selected_cat = category_map[selected_cat_name]

# عرض المحادثات
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "✨"):
        st.markdown(msg["content"])

# منطقة الإدخال
if prompt := st.chat_input("✍️ اسألني أي شيء هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # تحديد الفئة (إذا اختار المستخدم فئة من القائمة نعتمدها، وإلا نستخدم التصنيف الذكي)
    final_cat = selected_cat if selected_cat != "info" else smart_classify(prompt)
    reply = ask_ai(prompt, final_cat)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# الإدارة الجانبية
with st.sidebar:
    st.markdown("<h2 class='gold-foil-text' style='text-align:center;'>🔐 غرفة التحكم</h2>", unsafe_allow_html=True)
    password = st.text_input("مفتاح الدخول", type="password")
    
    if password == "admin123":
        data = load_data()
        info = st.text_area("نبذة", value=data.get("info", ""))
        schedules = st.text_area("الجداول", value=data.get("schedules", ""))
        fees = st.text_area("الرسوم", value=data.get("fees", ""))
        contacts = st.text_area("الاتصال", value=data.get("contacts", ""))
        majors = st.text_area("التخصصات", value=data.get("majors", ""))
        
        if st.button("💾 حفظ البيانات"):
            save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts, "majors": majors})
            st.success("✅ تمت المزامنة!")
