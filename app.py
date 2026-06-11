import streamlit as st
from services import ask_ai, smart_classify, get_all_info
from config import *
from datetime import datetime

# ======== إعداد الصفحة ========
st.set_page_config(
    page_title=f"{APP_TITLE} - {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== CSS متطور جداً ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@400;600;700&display=swap');
    
    * {{
        font-family: 'El Messiri', sans-serif;
    }}

    /* خلفية متحركة */
    .stApp {{
        background: linear-gradient(135deg, #030b1a 0%, #0a1a2f 25%, #0d1f3c 50%, #0a1a2f 75%, #030b1a 100%) !important;
        background-size: 400% 400% !important;
        animation: cosmicBG 30s ease infinite !important;
    }}
    @keyframes cosmicBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* تأثير النجوم */
    .stars {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        background: radial-gradient(2px 2px at 20px 30px, #fff, transparent),
                    radial-gradient(2px 2px at 40px 70px, #fff, transparent),
                    radial-gradient(1px 1px at 90px 40px, #fff, transparent),
                    radial-gradient(1px 1px at 130px 80px, #fff, transparent),
                    radial-gradient(2px 2px at 160px 30px, #fff, transparent);
        background-size: 200px 200px;
        animation: twinkle 4s infinite;
    }}
    @keyframes twinkle {{
        0% {{ opacity: 0.5; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.5; }}
    }}

    /* الحاوية الزجاجية الرئيسية */
    .glass-container {{
        background: rgba(20, 30, 50, 0.3);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 40px;
        padding: 40px 35px;
        margin: 30px auto;
        max-width: 1100px;
        position: relative;
        z-index: 1;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6), inset 0 0 30px rgba(212,175,55,0.05);
        transition: all 0.3s ease;
    }}

    /* البسملة */
    .basmala {{
        text-align: center;
        font-family: 'Amiri', serif;
        font-size: 3.2em;
        font-weight: 700;
        background: linear-gradient(135deg, #d4af37, #f5e6a3, #d4af37, #f9d976);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
        animation: goldShine 3s infinite;
    }}
    @keyframes goldShine {{
        0%, 100% {{ filter: brightness(1); }}
        50% {{ filter: brightness(1.5); text-shadow: 0 0 30px rgba(212,175,55,0.6); }}
    }}

    /* العنوان */
    .main-title {{
        text-align: center;
        font-size: 2.8em;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 40px rgba(212,175,55,0.4);
        letter-spacing: 3px;
    }}
    .sub-title {{
        text-align: center;
        font-size: 1.4em;
        color: {THEME['primary']};
        letter-spacing: 6px;
        margin-bottom: 25px;
    }}

    /* البطاقات */
    .service-card {{
        background: rgba(30, 40, 60, 0.2);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(212,175,55,0.2);
        border-radius: 30px;
        padding: 20px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1.2);
        cursor: pointer;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    .service-card:hover {{
        transform: translateY(-10px) scale(1.05);
        border-color: {THEME['primary']};
        box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 40px rgba(212,175,55,0.25);
    }}
    .service-icon {{
        font-size: 3em;
        margin-bottom: 10px;
    }}
    .service-label {{
        color: #fff;
        font-size: 1.2em;
        font-weight: 600;
    }}

    /* صندوق السؤال */
    .question-box {{
        background: rgba(0,0,0,0.2);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 30px;
        margin: 30px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    /* صندوق الرد */
    .reply-box {{
        background: rgba(20, 40, 30, 0.4);
        backdrop-filter: blur(20px);
        border-left: 6px solid {THEME['primary']};
        border-radius: 25px;
        padding: 25px;
        margin: 20px 0;
        color: #e8e8e8;
        font-size: 1.15em;
        line-height: 2;
        animation: fadeSlideIn 0.5s ease;
    }}
    @keyframes fadeSlideIn {{
        from {{ opacity: 0; transform: translateY(25px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* تخصيص الإدخال */
    .stTextInput > div > div > input {{
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 50px !important;
        padding: 18px 25px !important;
        color: #fff !important;
        font-size: 1.1em !important;
        backdrop-filter: blur(10px) !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {THEME['primary']} !important;
        box-shadow: 0 0 25px rgba(212,175,55,0.4) !important;
    }}

    /* زر الإرسال */
    .stButton > button {{
        background: linear-gradient(135deg, {THEME['primary']}, #b8941f) !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 50px !important;
        padding: 15px 35px !important;
        font-size: 1.1em !important;
        transition: all 0.3s !important;
    }}
    .stButton > button:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 10px 30px rgba(212,175,55,0.4) !important;
    }}

    /* إخفاء عناصر Streamlit الافتراضية */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* شريط جانبي للإدارة */
    section[data-testid="stSidebar"] {{
        background: rgba(10, 15, 30, 0.85) !important;
        backdrop-filter: blur(30px) !important;
        border-left: 1px solid rgba(212,175,55,0.25) !important;
    }}
</style>
<div class="stars"></div>
""", unsafe_allow_html=True)

# ======== الواجهة الرئيسية ========
st.markdown('<div class="glass-container">', unsafe_allow_html=True)

# البسملة والعنوان
st.markdown('<div class="basmala">﷽</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">{APP_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

# بطاقات الخدمات السريعة
st.markdown("---")
st.markdown("### 📌 الخدمات السريعة")
cols = st.columns(4)
services = [
    ("📚", "جداول المحاضرات", "schedules"),
    ("📅", "الامتحانات", "schedules"),
    ("💰", "الرسوم الدراسية", "fees"),
    ("📞", "جهات الاتصال", "contacts")
]

for col, (icon, name, category) in zip(cols, services):
    with col:
        st.markdown(f"""
        <div class="service-card" id="card-{name}">
            <div class="service-icon">{icon}</div>
            <div class="service-label">{name}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("", key=f"btn_{name}", use_container_width=True):
            with st.spinner("⏳ جاري تحضير الرد..."):
                reply = ask_ai(f"أريد معلومات عن {name}", category)
                st.session_state.reply = reply

# عرض الرد من البطاقات
if "reply" in st.session_state and st.session_state.reply:
    st.markdown(f'<div class="reply-box">🤖 <strong>الرد:</strong><br>{st.session_state.reply}</div>', unsafe_allow_html=True)
    del st.session_state.reply

st.markdown("---")

# صندوق السؤال المباشر
st.markdown('<div class="question-box">', unsafe_allow_html=True)
st.markdown("### 💬 اسألني مباشرة عن أي شيء يخص الجامعة")
with st.form("chat_form"):
    user_input = st.text_input("", placeholder="✍️ اكتب سؤالك هنا...")
    submitted = st.form_submit_button("🔍 إرسال السؤال")
    
    if submitted and user_input:
        # تصنيف السؤال تلقائيًا
        cat = smart_classify(user_input)
        with st.spinner("🧠 جاري البحث عن الإجابة..."):
            reply = ask_ai(user_input, cat)
        st.markdown(f'<div class="reply-box">🤖 <strong>الرد:</strong><br>{reply}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# تذييل
st.markdown(f"""
<div style="text-align:center; color:{THEME['text_muted']}; margin-top:40px; font-size:0.9em;">
    © {datetime.now().year} {APP_TITLE} - جميع الحقوق محفوظة<br>
    تم التطوير بواسطة فريق تقنية المعلومات
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ======== رابط لوحة الإدارة ========
with st.sidebar:
    st.markdown("---")
    st.markdown("## 🛠️ أدوات متقدمة")
    if st.button("🔐 لوحة الإدارة", use_container_width=True):
        st.switch_page("pages/admin.py")
    st.caption("للدخول إلى لوحة التحكم، انتقل إلى /admin")
