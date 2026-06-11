import streamlit as st
import json
import os
from datetime import datetime
import time

# ======== الإعدادات الأساسية لمعلومات الجامعة ========
APP_TITLE = "المساعد الأكاديمي الذكي"
APP_SUBTITLE = "جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير"
APP_ICON = "📖"

def ask_ai(q, c): 
    time.sleep(0.5) 
    return f"بناءً على قاعدة بيانات الجامعة، هذا رد مخصص لسؤالك حول قسم: {c}. نحن في فرع غيل باوزير نسعد بخدمتك."

def smart_classify(q): 
    return "استفسار_عام"

# ======== إعداد الصفحة ========
st.set_page_config(
    page_title=f"جامعة القرآن الكريم - غيل باوزير",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== CSS المصحح (آمن للموبايل ولا يكسر الشريط الجانبي) ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    
    /* 1. تعيين الخطوط لجميع العناصر */
    html, body, [class*="st-"] {{
        font-family: 'El Messiri', sans-serif;
    }}

    /* 2. إصلاح اتجاه النص (RTL) بطريقة لا تكسر واجهة Streamlit على الجوال */
    .stApp {{
        direction: rtl;
        background: linear-gradient(135deg, #020b06 0%, #061c10 40%, #031208 100%) !important;
        background-attachment: fixed !important;
    }}
    
    /* استثناء الشريط العلوي (الهامبرغر) من الانعكاس ليعمل بشكل صحيح */
    header[data-testid="stHeader"] {{
        direction: ltr;
        background-color: transparent !important;
    }}
    
    /* إصلاح محاذاة عناصر الشريط الجانبي بحيث لا تتداخل */
    [data-testid="stSidebar"] {{
        direction: rtl;
        background-color: #04120a !important;
        border-left: 1px solid rgba(212,175,55,0.2) !important;
    }}
    
    /* إخفاء القوائم الافتراضية */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    /* تخصيص شريط التمرير */
    ::-webkit-scrollbar {{ width: 6px; background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: #d4af37; border-radius: 10px; }}

    /* تأثير النص الذهبي الفاخر */
    .gold-foil-text {{
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 15px rgba(212,175,55,0.25);
    }}

    /* العناوين والبسملة */
    .basmala {{
        text-align: center; font-family: 'Amiri', serif; font-size: 2.2em;
        font-weight: 700; margin-bottom: 5px; margin-top: -30px;
    }}
    .main-title {{
        text-align: center; font-size: 2.2em; font-weight: 700; color: #ffffff;
        letter-spacing: 0px; margin-bottom: 5px; text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }}
    .sub-title {{
        text-align: center; font-size: 1.1em; color: #a0b6a8;
        margin-bottom: 30px; font-weight: 400;
    }}

    /* فاصل ذهبي */
    .gold-divider {{
        border: 0; height: 1px;
        background: linear-gradient(90deg, rgba(212,175,55,0) 0%, rgba(212,175,55,0.7) 50%, rgba(212,175,55,0) 100%);
        margin: 25px 0; box-shadow: 0 0 10px rgba(212,175,55,0.3);
    }}

    /* أزرار الخدمات (الكروت الزجاجية) */
    div[data-testid="stVerticalBlock"] div.stButton > button {{
        background: linear-gradient(145deg, rgba(10, 30, 20, 0.7), rgba(5, 15, 10, 0.9)) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 15px !important;
        height: auto !important;
        min-height: 100px;
        width: 100% !important;
        color: #e2e8f0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        white-space: normal !important; /* للسماح بالتفاف النص في الجوال */
    }}
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {{
        border-color: #d4af37 !important;
        color: #fcf6ba !important;
    }}
    div[data-testid="stVerticalBlock"] div.stButton > button p {{
        font-size: 1.1em !important; font-weight: 600; line-height: 1.4;
    }}

    /* تصميم واجهة المحادثة */
    [data-testid="stChatMessage"] {{
        background: rgba(8, 20, 14, 0.8) !important;
        border: 1px solid rgba(212,175,55,0.1) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
    }}
    
    [data-testid="stChatMessage"]:nth-child(even) {{
        border-right: 3px solid #d4af37 !important;
    }}
    
    [data-testid="stChatMessage"]:nth-child(odd) {{
        border-right: 3px solid #10b981 !important;
    }}

    /* حقل إدخال الدردشة */
    [data-testid="stChatInput"] {{ 
        background: transparent !important; 
    }}
    [data-testid="stChatInput"] textarea {{
        background: rgba(5, 12, 8, 0.95) !important;
        border: 1px solid rgba(212,175,55,0.5) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        direction: rtl;
    }}
    [data-testid="stChatInputSubmitButton"] {{
        color: #d4af37 !important; 
    }}
</style>
""", unsafe_allow_html=True)

# ======== إدارة قاعدة البيانات المعرفية ========
DATA_FILE = "quran_university_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "admission": "", "majors": "", "student_affairs": "", 
        "fees": "", "about_branch": ""
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======== إدارة الجلسة ========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك في بوابتك الذكية لجامعة القرآن الكريم وعلومه (فرع غيل باوزير). كيف يمكنني مساعدتك اليوم؟"}
    ]

# ======== الواجهة الرئيسية ========
st.markdown('<div class="basmala gold-foil-text">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">{APP_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">✦ {APP_SUBTITLE} ✦</div>', unsafe_allow_html=True)

# ======== أزرار الوصول السريع ========
st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #e2e8f0; font-weight: 600; text-align:right;'>📌 وصول سريع للخدمات</h4>", unsafe_allow_html=True)

services = [
    ("📝\nالقبول", "admission", "شروط القبول والتسجيل"),
    ("📚\nالتخصصات", "majors", "التخصصات المتاحة"),
    ("👨‍🎓\nشؤون الطلاب", "student_affairs", "خدمات شؤون الطلاب"),
    ("💰\nالرسوم", "fees", "النظام المالي والرسوم"),
    ("🕌\nعن الفرع", "about_branch", "نبذة عن فرع غيل باوزير")
]

# استخدام الأعمدة بحيث تتناسب مع الموبايل (نظام Streamlit سيقوم بترتيبها تلقائياً أسفل بعضها على الشاشات الصغيرة)
cols = st.columns(len(services))
for col, (label, category, name) in zip(cols, services):
    with col:
        if st.button(label, key=f"btn_{category}", use_container_width=True):
            question = f"أريد تفاصيل عن {name}"
            st.session_state.messages.append({"role": "user", "content": question})
            reply = ask_ai(question, category) 
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

# ======== عرض المحادثة ========
for msg in st.session_state.messages:
    avatar = "👨‍🎓" if msg["role"] == "user" else "📖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ======== حقل إدخال المستخدم ========
if prompt := st.chat_input("✍️ اكتب استفسارك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👨‍🎓"):
        st.markdown(prompt)
        
    cat = smart_classify(prompt)
    reply = ask_ai(prompt, cat)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="📖"):
        st.markdown(reply)

# ======== لوحة تحكم الإدارة (الشريط الجانبي) ========
with st.sidebar:
    st.markdown("<h2 class='gold-foil-text' style='text-align:center;'>🔐 إدارة المعرفة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#a0b6a8;'>تحديث بيانات فرع غيل باوزير</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    password = st.text_input("مفتاح الدخول", type="password", placeholder="••••••••")
    
    if password == "admin123": 
        st.success("✅ تم تسجيل الدخول بصلاحيات الإدارة")
        st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
        
        data = load_data()
        
        st.markdown("### 📝 تحديث قواعد البيانات:")
        about = st.text_area("🕌 نبذة عن فرع غيل باوزير:", value=data.get("about_branch", ""), height=100)
        admission = st.text_area("📝 القبول والتسجيل:", value=data.get("admission", ""), height=100)
        majors = st.text_area("📚 التخصصات والمقررات:", value=data.get("majors", ""), height=100)
        student_affairs = st.text_area("👨‍🎓 شؤون الطلاب والجداول:", value=data.get("student_affairs", ""), height=100)
        fees = st.text_area("💰 الرسوم والنظام المالي:", value=data.get("fees", ""), height=100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 حفظ التحديثات", use_container_width=True):
            save_data({
                "about_branch": about, 
                "admission": admission, 
                "majors": majors, 
                "student_affairs": student_affairs, 
                "fees": fees
            })
            st.success("✅ تم حفظ البيانات وتحديث المساعد الذكي!")
            
    elif password:
        st.error("❌ رمز الدخول غير صحيح")
