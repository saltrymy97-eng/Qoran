import streamlit as st
import json
import os
from datetime import datetime

# ======== الإعدادات الأساسية لهوية الجامعة ========
APP_TITLE = "جامعة القرآن الكريم وعلومه"
APP_BRANCH = "فرع غيل باوزير - حضرموت"
APP_SUBTITLE = "المساعد الأكاديمي الذكي"
APP_ICON = "📖"

# ======== إعداد الصفحة (يجب أن يكون أول أمر Streamlit) ========
st.set_page_config(
    page_title=f"{APP_TITLE} - {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== دوال الذكاء الاصطناعي (وهمية للتجربة) ========
def ask_ai(q, c): 
    return f"هذا رد تجريبي من نظام جامعة القرآن الكريم (فرع غيل باوزير) لسؤالك المتعلق بقسم: **{c}**.\n\nالسؤال: {q}"

def smart_classify(q): 
    return "استعلام عام"

# ======== CSS الفاخر والمخصص (Luxury Islamic UI) ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Tajawal:wght@300;400;500;700&display=swap');
    
    * {{ font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }}

    /* تخصيص شريط التمرير (Scrollbar) */
    ::-webkit-scrollbar {{ width: 6px; background: #02060d; }}
    ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #d4af37, #8a6d1c); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #fcf6ba; }}

    /* خلفية التطبيق: تدرج كحلي/أسود ملكي */
    .stApp {{
        background: linear-gradient(135deg, #010409 0%, #061121 50%, #020813 100%) !important;
        background-attachment: fixed !important;
    }}

    /* إخفاء العناصر الافتراضية */
    header[data-testid="stHeader"] {{ background-color: transparent !important; }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    /* تأثير النص الذهبي الفاخر */
    .gold-foil-text {{
        background: linear-gradient(to left, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 15px rgba(212,175,55,0.15);
    }}

    /* العناوين */
    .basmala {{
        text-align: center; font-family: 'Amiri', serif; font-size: 2.8em;
        font-weight: 700; margin-bottom: 0px; margin-top: -40px;
    }}
    .main-title {{
        text-align: center; font-size: 2.8em; font-weight: 700; color: #ffffff;
        margin-bottom: 5px; font-family: 'Amiri', serif;
    }}
    .branch-title {{
        text-align: center; font-size: 1.5em; font-weight: 500; color: #d4af37;
        margin-bottom: 5px;
    }}
    .sub-title {{
        text-align: center; font-size: 1.1em; color: #8892b0;
        letter-spacing: 1px; margin-bottom: 30px; font-weight: 300;
    }}

    /* فاصل ذهبي */
    .gold-divider {{
        border: 0; height: 1px;
        background: linear-gradient(90deg, rgba(212,175,55,0) 0%, rgba(212,175,55,0.6) 50%, rgba(212,175,55,0) 100%);
        margin: 25px 0;
    }}

    /* أزرار الخدمات (الكروت الزجاجية) */
    div[data-testid="column"] div.stButton > button {{
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.7), rgba(5, 10, 20, 0.9)) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(212,175,55,0.2) !important;
        border-radius: 15px !important;
        height: 120px !important;
        width: 100% !important;
        color: #e2e8f0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }}
    div[data-testid="column"] div.stButton > button:hover {{
        transform: translateY(-5px) !important;
        border-color: #d4af37 !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6), 0 0 15px rgba(212,175,55,0.2) !important;
        color: #fcf6ba !important;
    }}

    /* رسائل المحادثة (تصميم زجاجي) */
    [data-testid="stChatMessage"] {{
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        margin-bottom: 15px !important;
    }}
    
    /* رسالة المستخدم */
    [data-testid="stChatMessage"]:nth-child(even) {{
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.05), rgba(0,0,0,0)) !important;
        border-right: 3px solid #d4af37 !important;
    }}
    
    /* رسالة النظام */
    [data-testid="stChatMessage"]:nth-child(odd) {{
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.6), rgba(5, 10, 20, 0.8)) !important;
        border-right: 3px solid #10b981 !important; /* أخضر إسلامي خفيف */
    }}

    /* حقل الكتابة */
    [data-testid="stChatInput"] {{ background: transparent !important; padding-bottom: 20px !important; }}
    [data-testid="stChatInput"] textarea {{
        background: rgba(5, 10, 20, 0.8) !important;
        border: 1px solid rgba(212,175,55,0.4) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        padding: 15px 20px !important;
    }}
    [data-testid="stChatInput"] textarea:focus {{
        border-color: #d4af37 !important;
        box-shadow: 0 0 15px rgba(212,175,55,0.2) !important;
    }}

    /* شريط الإدارة الجانبي */
    section[data-testid="stSidebar"] {{
        background: rgba(2, 6, 13, 0.95) !important;
        border-left: 1px solid rgba(212,175,55,0.2) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ======== إدارة البيانات ========
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"info": "", "schedules": "", "fees": "", "contacts": "", "majors": ""}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======== تهيئة جلسة المحادثة ========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# ======== الواجهة الرئيسية (UI) ========
# ==========================================

# الترويسة الفخمة
st.markdown('<div class="basmala gold-foil-text">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">{APP_TITLE} {APP_ICON}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="branch-title">{APP_BRANCH}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #d4af37; font-weight: bold;'>📌 خدمات الوصول السريع</h4>", unsafe_allow_html=True)

# بطاقات الخدمات
services = [
    ("🕌\nالقبول والتسجيل", "admissions", "شروط القبول"),
    ("📚\nالجداول والخطط", "schedules", "الخطط الدراسية"),
    ("🎓\nتخصصات الفرع", "majors", "التخصصات المتاحة"),
    ("💰\nالرسوم والمنح", "fees", "الرسوم والمنح"),
    ("📞\nتواصل معنا", "contacts", "أرقام الإدارة")
]

cols = st.columns(5)
for col, (label, category, name) in zip(cols, services):
    with col:
        if st.button(label, key=f"btn_{category}", use_container_width=True):
            question = f"أريد تفاصيل عن {name} في فرع غيل باوزير"
            st.session_state.messages.append({"role": "user", "content": question})
            reply = ask_ai(question, category) 
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #d4af37; font-weight: bold;'>💬 تحدث مع المساعد الأكاديمي</h4>", unsafe_allow_html=True)

# عرض الرسائل
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🏛️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# حقل الإدخال
if prompt := st.chat_input("✍️ اطرح استفسارك الأكاديمي هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        
    cat = smart_classify(prompt)
    reply = ask_ai(prompt, cat)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="🏛️"):
        st.markdown(reply)

# ==========================================
# ======== لوحة الإدارة (Sidebar) ========
# ==========================================
with st.sidebar:
    st.markdown("<h2 class='gold-foil-text' style='text-align:center;'>🔐 إدارة الفرع</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
    
    if password == "admin123":
        st.success("✅ تم تسجيل الدخول للإدارة")
        st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #d4af37;'>📝 تحديث قاعدة بيانات الفرع</h4>", unsafe_allow_html=True)
        
        data = load_data()
        info = st.text_area("📋 نبذة عن فرع غيل باوزير:", value=data.get("info", ""), height=100)
        schedules = st.text_area("📚 الجداول والخطط:", value=data.get("schedules", ""), height=100)
        fees = st.text_area("💰 الرسوم والمنح:", value=data.get("fees", ""), height=100)
        contacts = st.text_area("📞 قنوات الاتصال بالفرع:", value=data.get("contacts", ""), height=100)
        majors = st.text_area("🎓 التخصصات (قرآن، شريعة، إلخ):", value=data.get("majors", ""), height=100)
        
        if st.button("💾 حفظ وتحديث البيانات", use_container_width=True):
            save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts, "majors": majors})
            st.success("✅ تم تحديث بيانات فرع غيل باوزير بنجاح!")
            
    elif password:
        st.error("❌ كلمة المرور غير صحيحة")

    st.markdown(f"""
    <div style="text-align:center; color:#64748b; margin-top:50px; font-size:0.85em;">
        © {datetime.now().year} جميع الحقوق محفوظة<br>
        جامعة القرآن الكريم وعلومه - فرع غيل باوزير<br>
        <span style="color: #d4af37;">Developed with AI</span>
    </div>
    """, unsafe_allow_html=True)
