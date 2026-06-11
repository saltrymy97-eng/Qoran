import streamlit as st
import json
import os
from datetime import datetime
from services import ask_ai, smart_classify

# ======== إعدادات جامعة القرآن الكريم ========
APP_TITLE = "جامعة القرآن الكريم والعلوم الإسلامية"
APP_SUBTITLE = "فرع غيل باوزير - حضرموت"
APP_ICON = "🕌"
# ===============================================

# ======== إعداد الصفحة ========
st.set_page_config(
    page_title=f"{APP_TITLE} - {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== CSS الفاخر جداً مع الإصلاحات السحابية ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    
    * {{ font-family: 'El Messiri', sans-serif; }}

    /* تخصيص شريط التمرير */
    ::-webkit-scrollbar {{ width: 8px; background: #050b14; }}
    ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #d4af37, #8a6d1c); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #fcf6ba; }}

    /* خلفية التطبيق */
    .stApp {{
        background: linear-gradient(135deg, #02060d 0%, #0a1324 40%, #060e1a 100%) !important;
        background-attachment: fixed !important;
    }}

    /* ======== إصلاحات الواجهة العلوية والسفلية (النسخة السحابية القوية) ======== */
    header[data-testid="stHeader"] {{ 
        background-color: transparent !important; 
    }}
    
    /* إخفاء أزرار Share و GitHub وزر النشر بشكل إجباري */
    .stAppDeployButton, [data-testid="stToolbar"], [data-testid="stHeaderActionElements"] {{
        display: none !important;
    }}
    
    /* إخفاء الفوتر وزر Manage app */
    #MainMenu {{ display: none !important; }}
    footer {{ display: none !important; }}

    /* تفريغ خلفية الحاوية السفلية للشات بالكامل بجميع طبقاتها */
    [data-testid="stBottom"], [data-testid="stBottom"] > div, div[data-testid="stBottomBlockContainer"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        padding-bottom: 5px !important;
    }}
    /* =================================================== */

    /* تأثير النص الذهبي الفاخر */
    .gold-foil-text {{
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 20px rgba(212,175,55,0.2);
    }}

    /* العناوين والبسملة */
    .basmala {{
        text-align: center; font-family: 'Amiri', serif; font-size: 2.4em;
        font-weight: 700; margin-bottom: 5px; margin-top: -30px;
    }}
    .main-title {{
        text-align: center; font-size: 3.2em; font-weight: 700; color: #ffffff;
        letter-spacing: 2px; margin-bottom: 5px;
    }}
    .sub-title {{
        text-align: center; font-size: 1.3em; color: #a8b2c1;
        letter-spacing: 5px; margin-bottom: 40px; font-weight: 300;
    }}

    /* فاصل ذهبي متدرج */
    .gold-divider {{
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(212,175,55,0) 0%, rgba(212,175,55,0.8) 50%, rgba(212,175,55,0) 100%);
        margin: 30px 0;
        box-shadow: 0 0 10px rgba(212,175,55,0.4);
    }}

    /* أزرار الخدمات (الكروت الزجاجية) */
    div[data-testid="column"] div.stButton > button {{
        background: linear-gradient(145deg, rgba(20, 30, 50, 0.6), rgba(10, 15, 30, 0.8)) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(212,175,55,0.15) !important;
        border-radius: 25px !important;
        height: 140px !important;
        width: 100% !important;
        color: #e2e8f0 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 2px 10px rgba(255,255,255,0.05);
    }}
    div[data-testid="column"] div.stButton > button:hover {{
        transform: translateY(-10px) scale(1.02) !important;
        border-color: #d4af37 !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.7), 0 0 20px rgba(212,175,55,0.3) !important;
        color: #fcf6ba !important;
    }}

    /* رسائل المحادثة */
    [data-testid="stChatMessage"] {{
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 20px 25px !important;
        margin-bottom: 20px !important;
    }}
    
    [data-testid="stChatMessage"]:nth-child(even) {{ border-right: 3px solid #d4af37 !important; }}
    [data-testid="stChatMessage"]:nth-child(odd) {{ border-left: 3px solid #60a5fa !important; }}

    /* حقل الكتابة الطافي */
    [data-testid="stChatInput"] textarea {{
        background: rgba(10, 15, 30, 0.85) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 30px !important;
        color: #ffffff !important;
        padding: 18px 30px !important;
    }}
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

# ======== الجلسة والواجهة ========
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="basmala gold-foil-text">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">{APP_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

# ... (باقي الكود يظل كما هو في منطق الأزرار والمحادثة)

services = [("📚 الجداول", "schedules", "جداول المحاضرات"), ("📅 الامتحانات", "schedules", "الامتحانات"), ("💰 الرسوم", "fees", "الرسوم الدراسية"), ("📞 الدعم", "contacts", "جهات الاتصال"), ("🎓 التخصصات", "majors", "التخصصات")]
cols = st.columns(5)
for col, (label, category, name) in zip(cols, services):
    with col:
        if st.button(label, key=f"btn_{category}_{name}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": f"أريد تفاصيل عن {name}"})
            st.session_state.messages.append({"role": "assistant", "content": ask_ai(f"أريد تفاصيل عن {name}", category)})
            st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "✨"):
        st.markdown(msg["content"])

if prompt := st.chat_input("✍️ اسألني أي شيء هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = ask_ai(prompt, smart_classify(prompt))
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

with st.sidebar:
    st.markdown("<h2 class='gold-foil-text' style='text-align:center;'>🔐 غرفة التحكم</h2>", unsafe_allow_html=True)
    password = st.text_input("مفتاح الدخول", type="password")
    if password == "admin123":
        data = load_data()
        info, schedules, fees, contacts, majors = [st.text_area(label, value=data.get(k, "")) for label, k in [("📋 نبذة", "info"), ("📚 جداول", "schedules"), ("💰 رسوم", "fees"), ("📞 اتصال", "contacts"), ("🎓 تخصصات", "majors")]]
        if st.button("💾 توثيق"): save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts, "majors": majors}); st.success("✅")
