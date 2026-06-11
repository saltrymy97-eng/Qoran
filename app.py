import streamlit as st
import json
import os
from datetime import datetime

# ======== إعدادات وهمية لتشغيل الكود (استبدلها بملفاتك) ========
# from services import ask_ai, smart_classify
# from config import APP_TITLE, APP_SUBTITLE, APP_ICON, THEME
APP_TITLE = "المساعد الأكاديمي"
APP_SUBTITLE = "بوابتك الذكية للخدمات الجامعية"
APP_ICON = "🏛️"
THEME = {'primary': '#d4af37', 'text_muted': '#8892b0'}

def ask_ai(q, c): return f"هذا رد تجريبي لسؤالك عن {c}"
def smart_classify(q): return "عام"
# ===============================================================

# ======== إعداد الصفحة ========
st.set_page_config(
    page_title=f"{APP_TITLE} - {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== CSS الفاخر جداً (Luxury Design) ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    
    * {{ font-family: 'El Messiri', sans-serif; }}

    /* تخصيص شريط التمرير (Scrollbar) ليناسب الفخامة */
    ::-webkit-scrollbar {{ width: 8px; background: #050b14; }}
    ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #d4af37, #8a6d1c); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #fcf6ba; }}

    /* خلفية التطبيق: تدرج داكن وعميق يعطي إحساساً بالفضاء أو الفخامة الملكية */
    .stApp {{
        background: linear-gradient(135deg, #02060d 0%, #0a1324 40%, #060e1a 100%) !important;
        background-attachment: fixed !important;
    }}

    /* إخفاء الشريط العلوي الافتراضي مع ترك زر القائمة المنسدلة */
    header[data-testid="stHeader"] {{ background-color: transparent !important; }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    /* تأثير النص الذهبي الفاخر (Gold Foil) */
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
        -webkit-backdrop-filter: blur(20px) !important;
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
    div[data-testid="column"] div.stButton > button p {{
        font-size: 1.2em !important;
        font-weight: 600;
        margin: 0;
        line-height: 1.6;
    }}

    /* رسائل المحادثة (تصميم زجاجي أنيق) */
    [data-testid="stChatMessage"] {{
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 20px 25px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    /* رسالة المستخدم */
    [data-testid="stChatMessage"]:nth-child(even) {{
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(0,0,0,0)) !important;
        border-right: 3px solid #d4af37 !important;
        border-left: none !important;
    }}
    
    /* رسالة الذكاء الاصطناعي */
    [data-testid="stChatMessage"]:nth-child(odd) {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)) !important;
        border-left: 3px solid #60a5fa !important;
    }}

    /* حقل الكتابة (طافي ومضيء) */
    [data-testid="stChatInput"] {{
        background: transparent !important;
        padding-bottom: 30px !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background: rgba(10, 15, 30, 0.85) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 30px !important;
        color: #ffffff !important;
        padding: 18px 30px !important;
        font-size: 1.15em !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.3s ease !important;
    }}
    [data-testid="stChatInput"] textarea:focus {{
        border-color: #d4af37 !important;
        box-shadow: 0 0 25px rgba(212,175,55,0.3), inset 0 0 10px rgba(212,175,55,0.1) !important;
        outline: none !important;
    }}

    /* تخصيص أيقونات الإرسال في حقل الكتابة */
    [data-testid="stChatInputSubmitButton"] {{
        color: #d4af37 !important;
        background: rgba(212,175,55,0.1) !important;
        border-radius: 50% !important;
        transition: all 0.3s ease !important;
    }}
    [data-testid="stChatInputSubmitButton"]:hover {{
        background: #d4af37 !important;
        color: #000 !important;
        transform: scale(1.1);
    }}

    /* شريط الإدارة الجانبي */
    section[data-testid="stSidebar"] {{
        background: rgba(5, 10, 20, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-left: 1px solid rgba(212,175,55,0.15) !important;
    }}
    .stTextInput > div > div > input, .stTextArea > div > textarea {{
        background: rgba(15, 23, 42, 0.6) !important;
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }}
    .stTextInput > div > div > input:focus, .stTextArea > div > textarea:focus {{
        border-color: #d4af37 !important;
        box-shadow: 0 0 10px rgba(212,175,55,0.2) !important;
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

# ======== جلسة المحادثة ========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======== الواجهة الرئيسية ========
# هيدر فخم
st.markdown('<div class="basmala gold-foil-text">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">{APP_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

# بطاقات الخدمات السريعة (تأثير 3D خفيف)
st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #e2e8f0; font-weight: 600;'>📌 وصول سريع</h3>", unsafe_allow_html=True)

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

st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #e2e8f0; font-weight: 600;'>💬 المساعد الذكي</h3>", unsafe_allow_html=True)

# عرض رسائل الدردشة 
for msg in st.session_state.messages:
    avatar = "🧑‍🎓" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# حقل الإدخال 
if prompt := st.chat_input("✍️ اسألني أي شيء هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
        
    cat = smart_classify(prompt)
    reply = ask_ai(prompt, cat)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="✨"):
        st.markdown(reply)

# ======== لوحة الإدارة الجانبية ========
with st.sidebar:
    st.markdown("<h2 class='gold-foil-text' style='text-align:center;'>🔐 غرفة التحكم</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    password = st.text_input("مفتاح الدخول", type="password", placeholder="••••••••")
    
    if password == "admin123":
        st.success("✅ تم التصديق")
        st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #fff;'>📝 قاعدة البيانات المعرفية</h3>", unsafe_allow_html=True)
        
        data = load_data()
        info = st.text_area("📋 نبذة عامة:", value=data.get("info", ""), height=100)
        schedules = st.text_area("📚 الجداول الزمنية:", value=data.get("schedules", ""), height=100)
        fees = st.text_area("💰 البيانات المالية:", value=data.get("fees", ""), height=100)
        contacts = st.text_area("📞 قنوات الاتصال:", value=data.get("contacts", ""), height=100)
        majors = st.text_area("🎓 التخصصات الأكاديمية:", value=data.get("majors", ""), height=100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 توثيق التحديثات", use_container_width=True):
            save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts, "majors": majors})
            st.success("✅ تمت المزامنة بنجاح!")
            
    elif password:
        st.error("❌ بيانات الاعتماد غير صالحة")

    st.markdown(f"""
    <div style="text-align:center; color:#64748b; margin-top:80px; font-size:0.85em; letter-spacing: 1px;">
        © {datetime.now().year} {APP_TITLE}<br>
        <span style="color: #d4af37;">Powered by AI</span>
    </div>
    """, unsafe_allow_html=True)

