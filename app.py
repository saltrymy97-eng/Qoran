import streamlit as st
import json
import os
from services import ask_ai, smart_classify
from config import *
from datetime import datetime

# ======== إعداد الصفحة ========
st.set_page_config(
    page_title=f"{APP_TITLE} - {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== CSS فخم جداً - زجاجي مبهر ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    
    * {{ font-family: 'El Messiri', sans-serif; }}

    .stApp {{
        background: linear-gradient(135deg, #020812 0%, #07101e 25%, #030d1a 50%, #07101e 75%, #020812 100%);
        background-size: 400% 400%;
        animation: bgMove 20s ease infinite;
    }}
    @keyframes bgMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* جزيئات ذهبية */
    .particles {{
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        z-index: 0;
    }}

    .main-wrapper {{
        position: relative;
        z-index: 1;
        max-width: 850px;
        margin: 40px auto;
        padding: 35px 30px;
        background: rgba(18, 25, 40, 0.5);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 35px;
        box-shadow: 
            0 25px 60px rgba(0, 0, 0, 0.7),
            0 0 80px rgba(212, 175, 55, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }}

    .basmala {{
        text-align: center;
        font-family: 'Amiri', serif;
        font-size: 2.6em;
        font-weight: 700;
        background: linear-gradient(135deg, #d4af37, #f5e6a3, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
        animation: goldShine 3s ease-in-out infinite;
    }}
    @keyframes goldShine {{
        0%, 100% {{ filter: brightness(1); }}
        50% {{ filter: brightness(1.5); }}
    }}

    .main-title {{
        text-align: center;
        font-size: 2.4em;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 0 40px rgba(212, 175, 55, 0.3);
        margin: 5px 0;
    }}

    .sub-title {{
        text-align: center;
        font-size: 1.1em;
        color: #d4af37;
        letter-spacing: 5px;
        margin-bottom: 25px;
        opacity: 0.8;
    }}

    .divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(212,175,55,0.4), transparent);
        margin: 20px 0;
    }}

    .chat-message {{
        padding: 16px 22px;
        border-radius: 20px;
        margin: 12px 0;
        font-size: 1.05em;
        line-height: 1.9;
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        animation: fadeIn 0.3s ease;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .user-message {{
        background: rgba(212, 175, 55, 0.1);
        border: 1px solid rgba(212, 175, 55, 0.25);
        color: #f5e6a3;
        text-align: right;
    }}

    .bot-message {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
    }}

    .stChatInput {{
        margin-top: 20px;
    }}

    .stChatInput textarea {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 25px !important;
        color: #ffffff !important;
        padding: 15px 20px !important;
        font-size: 1.05em !important;
        transition: all 0.3s !important;
    }}

    .stChatInput textarea:focus {{
        border-color: #d4af37 !important;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.2) !important;
    }}

    .stChatInput textarea::placeholder {{
        color: rgba(255, 255, 255, 0.35) !important;
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(10, 15, 25, 0.85) !important;
        backdrop-filter: blur(35px) !important;
        border-left: 1px solid rgba(212, 175, 55, 0.25) !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #d4af37, #b8941f) !important;
        color: #000 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 10px 25px !important;
        border: none !important;
        transition: all 0.3s !important;
        letter-spacing: 1px;
    }}

    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(212, 175, 55, 0.4) !important;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ======== دوال البيانات ========
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"info": "", "schedules": "", "fees": "", "contacts": "", "majors": ""}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======== بدء المحادثة ========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======== الواجهة ========
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

st.markdown('<div class="basmala">بسم الله الرحمن الرحيم</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🕌 جامعة القرآن الكريم والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# الدردشة
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message user-message">🧑‍🎓 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("✍️ اكتب سؤالك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    cat = smart_classify(prompt)
    reply = ask_ai(prompt, cat)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ======== لوحة الإدارة ========
with st.sidebar:
    st.markdown("## 🔐 الإدارة")
    password = st.text_input("كلمة المرور", type="password")
    
    if password == "admin123":
        st.success("تم الدخول")
        data = load_data()
        
        info = st.text_area("📋 معلومات عامة:", value=data.get("info", ""), height=120)
        schedules = st.text_area("📚 الجداول:", value=data.get("schedules", ""), height=120)
        fees = st.text_area("💰 الرسوم:", value=data.get("fees", ""), height=100)
        contacts = st.text_area("📞 التواصل:", value=data.get("contacts", ""), height=100)
        majors = st.text_area("🎓 التخصصات:", value=data.get("majors", ""), height=100)
        
        if st.button("💾 حفظ", use_container_width=True):
            save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts, "majors": majors})
            st.success("تم الحفظ!")
            st.rerun()
    elif password:
        st.error("كلمة مرور خاطئة")
