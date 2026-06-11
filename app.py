import streamlit as st
import json
import os
from datetime import datetime
from services import ask_ai, smart_classify

APP_TITLE = "جامعة القرآن الكريم والعلوم الإسلامية"
APP_SUBTITLE = "فرع غيل باوزير - حضرموت"
APP_ICON = "🕌"
THEME = {'primary': '#d4af37', 'text_muted': '#8892b0'}

st.set_page_config(
    page_title=f"{APP_TITLE} - {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    
    * {{ font-family: 'El Messiri', sans-serif; }}

    div:empty, .stMarkdown:empty, .element-container:empty {{
        display: none !important;
    }}

    .stApp {{
        background: linear-gradient(145deg, #030712 0%, #0b1522 50%, #030712 100%);
        background-attachment: fixed;
    }}

    ::-webkit-scrollbar {{ width: 5px; background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, #d4af37, #8a6d1c);
        border-radius: 12px;
    }}

    .luxury-container {{
        background: rgba(15, 22, 36, 0.55);
        backdrop-filter: blur(35px);
        -webkit-backdrop-filter: blur(35px);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: 40px;
        padding: 40px 35px;
        margin: 30px auto;
        max-width: 1050px;
        box-shadow: 0 30px 70px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        position: relative;
        overflow: hidden;
    }}

    .luxury-container::before {{
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 70%, rgba(212, 175, 55, 0.04) 0%, transparent 50%),
                    radial-gradient(circle at 70% 30%, rgba(212, 175, 55, 0.03) 0%, transparent 50%);
        pointer-events: none;
    }}

    .basmala {{
        text-align: center;
        font-family: 'Amiri', serif;
        font-size: 2.6em;
        font-weight: 700;
        background: linear-gradient(135deg, #d4af37, #f5e6a3, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
        filter: drop-shadow(0 0 12px rgba(212,175,55,0.4));
    }}

    .university-title {{
        text-align: center;
        font-size: 2.8em;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 4px;
        text-shadow: 0 0 30px rgba(212, 175, 55, 0.3), 0 0 80px rgba(212, 175, 55, 0.1);
        margin: 10px 0 5px 0;
        line-height: 1.3;
    }}

    .university-title span {{
        background: linear-gradient(135deg, #f9e076, #d4af37, #fdf0a6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .branch-name {{
        text-align: center;
        font-size: 1.2em;
        color: #a0a8b8;
        letter-spacing: 8px;
        font-weight: 300;
        margin-bottom: 35px;
        text-transform: uppercase;
    }}

    .gold-separator {{
        height: 2px;
        background: linear-gradient(90deg, transparent, #d4af37, #f5e6a3, #d4af37, transparent);
        margin: 25px 0;
        box-shadow: 0 0 20px rgba(212,175,55,0.4);
        border: none;
    }}

    .service-buttons div.stButton > button {{
        background: rgba(18, 25, 40, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        border-radius: 28px !important;
        height: 140px !important;
        width: 100% !important;
        color: #e2e6f0 !important;
        font-weight: 500 !important;
        transition: all 0.45s cubic-bezier(0.23, 1, 0.32, 1) !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
    }}
    .service-buttons div.stButton > button:hover {{
        transform: translateY(-12px) scale(1.04) !important;
        border-color: #d4af37 !important;
        box-shadow: 0 25px 45px rgba(0,0,0,0.8), 0 0 30px rgba(212,175,55,0.25) !important;
        color: #fcf6ba !important;
        background: rgba(25, 33, 50, 0.8) !important;
    }}

    .assistant-title {{
        text-align: center;
        color: #e0e4f0;
        font-size: 1.8em;
        font-weight: 600;
        margin: 20px 0 15px 0;
        position: relative;
        display: inline-block;
        width: 100%;
    }}
    .assistant-title::after {{
        content: '';
        display: block;
        width: 120px;
        height: 3px;
        background: linear-gradient(90deg, #d4af37, #f9e076, #d4af37);
        margin: 10px auto 0;
        border-radius: 3px;
        box-shadow: 0 0 12px rgba(212,175,55,0.6);
    }}

    [data-testid="stChatMessage"] {{
        background: rgba(10, 16, 28, 0.7) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 24px !important;
        padding: 18px 24px !important;
        margin: 10px 0 !important;
        box-shadow: 0 8px 22px rgba(0,0,0,0.4);
    }}

    [data-testid="stChatInput"] textarea {{
        background: rgba(8, 12, 22, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 30px !important;
        color: #fff !important;
        padding: 16px 24px !important;
        font-size: 1.1em !important;
        box-shadow: 0 8px 28px rgba(0,0,0,0.6);
    }}

    [data-testid="stChatInput"] textarea:focus {{
        border-color: #d4af37 !important;
        box-shadow: 0 0 35px rgba(212,175,55,0.5);
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(5, 10, 20, 0.97) !important;
        backdrop-filter: blur(35px) !important;
        border-left: 1px solid rgba(212,175,55,0.2) !important;
    }}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"info": "", "schedules": "", "fees": "", "contacts": "", "majors": ""}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="luxury-container">', unsafe_allow_html=True)

st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="university-title"><span>{APP_TITLE}</span></div>', unsafe_allow_html=True)
st.markdown(f'<div class="branch-name">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

st.markdown('<hr class="gold-separator">', unsafe_allow_html=True)
st.markdown("<div class='assistant-title'>📌 الخدمات</div>", unsafe_allow_html=True)

services = [
    ("📚\nالجداول", "schedules", "جداول المحاضرات"),
    ("📅\nالامتحانات", "schedules", "الامتحانات"),
    ("💰\nالرسوم", "fees", "الرسوم الدراسية"),
    ("📞\nالدعم", "contacts", "جهات الاتصال"),
    ("🎓\nالتخصصات", "majors", "التخصصات")
]

cols = st.columns(5)
for col, (label, category, name) in zip(cols, services):
    with col:
        if st.button(label, key=f"btn_{category}_{name}", use_container_width=True):
            question = f"أريد تفاصيل عن {name}"
            st.session_state.messages.append({"role": "user", "content": question})
            reply = ask_ai(question, category)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

st.markdown('<hr class="gold-separator">', unsafe_allow_html=True)
st.markdown('<div class="assistant-title">💬 المساعد الذكي</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "🧑‍🎓" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("✍️ اسألني أي شيء..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    cat = smart_classify(prompt)
    reply = ask_ai(prompt, cat)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="✨"):
        st.markdown(reply)

st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='text-align:center; color: #d4af37;'>🔐 التحكم</h2>", unsafe_allow_html=True)
    password = st.text_input("المفتاح", type="password", placeholder="••••••••")
    
    if password == "admin123":
        st.success("✅ تم الدخول")
        st.markdown('<hr class="gold-separator">', unsafe_allow_html=True)
        
        data = load_data()
        info = st.text_area("📋 عام", value=data.get("info", ""), height=80)
        schedules = st.text_area("📚 الجداول", value=data.get("schedules", ""), height=80)
        fees = st.text_area("💰 المالية", value=data.get("fees", ""), height=80)
        contacts = st.text_area("📞 الاتصال", value=data.get("contacts", ""), height=80)
        majors = st.text_area("🎓 التخصصات", value=data.get("majors", ""), height=80)
        
        if st.button("💾 حفظ", use_container_width=True):
            save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts, "majors": majors})
            st.success("✅ تم الحفظ")
    elif password:
        st.error("❌ خطأ")
