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

# CSS معدل مع إزالة المستطيلات الفارغة وتأثيرات فخمة
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    
    * {{ font-family: 'El Messiri', sans-serif; }}

    /* إخفاء أي عنصر فارغ */
    div:empty, .stMarkdown:empty, .element-container:empty {{
        display: none !important;
    }}

    .stApp {{
        background: radial-gradient(ellipse at center, #0a1324 0%, #02040a 100%);
        background-attachment: fixed;
    }}

    ::-webkit-scrollbar {{ width: 6px; background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, #d4af37, #8a6d1c);
        border-radius: 10px;
    }}

    .main-glass {{
        background: rgba(10, 15, 25, 0.5);
        backdrop-filter: blur(30px);
        border: 1px solid rgba(212, 175, 55, 0.12);
        border-radius: 30px;
        padding: 35px 30px;
        margin: 20px auto;
        max-width: 1000px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 80px rgba(212, 175, 55, 0.06);
    }}

    /* تأثير اسم الجامعة الفاخر */
    .university-name {{
        text-align: center;
        font-family: 'Amiri', serif;
        font-size: 4em;
        font-weight: 700;
        background: linear-gradient(135deg, #d4af37 0%, #f9e076 25%, #e5b83b 50%, #fdf0a6 75%, #b48a2c 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: goldShift 4s ease infinite, glowPulse 2.5s ease-in-out infinite;
        margin: 20px 0 0 0;
        line-height: 1.2;
        letter-spacing: 3px;
    }}
    
    @keyframes goldShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    @keyframes glowPulse {{
        0%, 100% {{ filter: drop-shadow(0 0 15px rgba(212,175,55,0.4)); }}
        50% {{ filter: drop-shadow(0 0 35px rgba(212,175,55,0.9)); }}
    }}

    .basmala {{
        text-align: center;
        font-family: 'Amiri', serif;
        font-size: 2.4em;
        font-weight: 700;
        background: linear-gradient(135deg, #d4af37, #f5e6a3, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
        filter: drop-shadow(0 0 15px rgba(212,175,55,0.3));
    }}

    .sub-title {{
        text-align: center; font-size: 1.3em; color: #d4af37;
        letter-spacing: 6px; font-weight: 300; margin-top: 0; margin-bottom: 30px;
    }}

    .gold-line {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(212,175,55,0.6), rgba(245,230,163,0.9), rgba(212,175,55,0.6), transparent);
        margin: 25px 0;
        box-shadow: 0 0 15px rgba(212,175,55,0.3);
    }}

    div[data-testid="column"] div.stButton > button {{
        background: linear-gradient(145deg, rgba(20, 28, 45, 0.8), rgba(8, 12, 22, 0.9)) !important;
        backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(212,175,55,0.2) !important;
        border-radius: 22px !important;
        height: 130px !important;
        width: 100% !important;
        color: #e8e8f0 !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.6);
    }}
    div[data-testid="column"] div.stButton > button:hover {{
        transform: translateY(-10px) scale(1.02) !important;
        border-color: #d4af37 !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.7), 0 0 20px rgba(212,175,55,0.3) !important;
        color: #fcf6ba !important;
    }}

    [data-testid="stChatMessage"] {{
        background: rgba(12, 18, 30, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 20px !important;
        padding: 18px 22px !important;
        margin: 12px 0 !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }}

    [data-testid="stChatInput"] textarea {{
        background: rgba(8, 12, 22, 0.9) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(212,175,55,0.25) !important;
        border-radius: 25px !important;
        color: #fff !important;
        padding: 16px 25px !important;
        font-size: 1.1em !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    }}
    [data-testid="stChatInput"] textarea:focus {{
        border-color: #d4af37 !important;
        box-shadow: 0 0 35px rgba(212,175,55,0.4);
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(4, 8, 16, 0.97) !important;
        backdrop-filter: blur(35px) !important;
        border-left: 1px solid rgba(212,175,55,0.2) !important;
    }}
</style>
""", unsafe_allow_html=True)

# دوال البيانات
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

# الواجهة الرئيسية
st.markdown('<div class="main-glass">', unsafe_allow_html=True)

st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
# اسم الجامعة بتأثير فاخر
st.markdown(f'<div class="university-name">{APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)
st.markdown("<h3 style='color: #e0e4f0; font-weight: 600; text-align: center;'>📌 الخدمات</h3>", unsafe_allow_html=True)

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

st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)
st.markdown("<h3 style='color: #e0e4f0; font-weight: 600; text-align: center;'>💬 المساعد الذكي</h3>", unsafe_allow_html=True)

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

# لوحة الإدارة
with st.sidebar:
    st.markdown("<h2 class='gold-neon' style='text-align:center;'>🔐 التحكم</h2>", unsafe_allow_html=True)
    password = st.text_input("المفتاح", type="password", placeholder="••••••••")
    
    if password == "admin123":
        st.success("✅ تم الدخول")
        st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)
        
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
