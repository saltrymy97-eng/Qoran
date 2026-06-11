import streamlit as st
import json
import os
from groq import Groq
from datetime import datetime

# ======== إعداد الصفحة ========
st.set_page_config(
    page_title="جامعة القرآن - غيل باوزير",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== إعداد Groq ========
GROQ_API_KEY = "gsk_مفتاحك_هنا"  # ضع مفتاحك الحقيقي
groq_client = Groq(api_key=GROQ_API_KEY)

# ======== CSS (نفس التصميم السابق) ========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@400;600;700&display=swap');
    
    * { font-family: 'El Messiri', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #030b1a 0%, #0a1a2f 25%, #0d1f3c 50%, #0a1a2f 75%, #030b1a 100%) !important;
        background-size: 400% 400% !important;
        animation: cosmicBG 30s ease infinite !important;
    }
    @keyframes cosmicBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .glass-container {
        background: rgba(20, 30, 50, 0.3);
        backdrop-filter: blur(30px);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 40px;
        padding: 40px 35px;
        margin: 30px auto;
        max-width: 900px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }

    .basmala {
        text-align: center;
        font-family: 'Amiri', serif;
        font-size: 2.2em;
        font-weight: 700;
        color: #d4af37;
        margin: 15px 0;
    }

    .main-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 40px rgba(212,175,55,0.4);
    }
    .sub-title {
        text-align: center;
        font-size: 1.3em;
        color: #d4af37;
        letter-spacing: 5px;
        margin-bottom: 25px;
    }

    /* صناديق الدردشة */
    .chat-message {
        padding: 18px 22px;
        border-radius: 20px;
        margin: 12px 0;
        font-size: 1.1em;
        line-height: 1.9;
        backdrop-filter: blur(15px);
    }
    .user-message {
        background: rgba(212, 175, 55, 0.15);
        border-left: 4px solid #d4af37;
        color: #f0e6c0;
    }
    .bot-message {
        background: rgba(20, 40, 30, 0.5);
        border-left: 4px solid #2e8b57;
        color: #e0e0e0;
    }

    .stChatInput textarea {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 30px !important;
        color: #fff !important;
        padding: 15px 20px !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.9) !important;
        backdrop-filter: blur(30px) !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

# ======== دوال الذكاء الاصطناعي ========
SYSTEM_PROMPT = """أنت مساعد ذكي لفرع جامعة القرآن الكريم والعلوم الإسلامية في غيل باوزير، حضرموت.
أجب بدقة من بيانات الجامعة. إذا لم تجد المعلومة، قل: 'لم أجد هذه المعلومة، يرجى التواصل مع الإدارة.'
كن مختصرًا ومفيدًا."""

def chat_with_ai(messages):
    """يرسل تاريخ المحادثة كاملاً إلى Groq"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages
            ],
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message.content
    except:
        return "⚠️ حدث خطأ تقني. يرجى المحاولة لاحقًا."

# ======== بدء الجلسة ========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======== الواجهة الرئيسية ========
st.markdown('<div class="glass-container">', unsafe_allow_html=True)

# البسملة والعنوان
st.markdown('<div class="basmala">بسم الله الرحمن الرحيم</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🕌 جامعة القرآن الكريم والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)

st.markdown("---")

# ======== منطقة الدردشة ========
st.markdown("### 💬 المحادثة التفاعلية")

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message user-message">🧑‍🎓 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

# حقل الإدخال (يظهر دائمًا في الأسفل)
if prompt := st.chat_input("✍️ اكتب سؤالك هنا..."):
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-message user-message">🧑‍🎓 {prompt}</div>', unsafe_allow_html=True)
    
    # جلب الرد
    with st.spinner("⏳ جاري الرد..."):
        reply = chat_with_ai(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown(f'<div class="chat-message bot-message">🤖 {reply}</div>', unsafe_allow_html=True)

st.markdown("---")

# بطاقات الخدمات السريعة
st.markdown("### 📌 الخدمات السريعة")
cols = st.columns(5)
services = [
    ("📚", "جداول", "schedules"),
    ("📅", "الامتحانات", "schedules"),
    ("💰", "الرسوم", "fees"),
    ("📞", "اتصال", "contacts"),
    ("🎓", "التخصصات", "majors")
]

for col, (icon, name, category) in zip(cols, services):
    with col:
        if st.button(f"{icon} {name}", key=f"btn_{name}", use_container_width=True):
            # إضافة سؤال تلقائي
            question = f"أريد معلومات عن {name}"
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("⏳"):
                reply = chat_with_ai(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# تذييل
st.markdown(f"""
<div style="text-align:center; color:#888; margin-top:40px; font-size:0.9em;">
    © {datetime.now().year} جامعة القرآن الكريم - جميع الحقوق محفوظة
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ======== لوحة الإدارة ========
with st.sidebar:
    st.markdown("## 🔐 الإدارة")
    password = st.text_input("كلمة المرور", type="password")
    
    if password == "admin123":
        st.success("✅ تم الدخول")
        data = load_data()
        
        info = st.text_area("📋 معلومات عامة:", value=data.get("info", ""), height=120)
        schedules = st.text_area("📚 الجداول:", value=data.get("schedules", ""), height=120)
        fees = st.text_area("💰 الرسوم:", value=data.get("fees", ""), height=100)
        contacts = st.text_area("📞 التواصل:", value=data.get("contacts", ""), height=100)
        majors = st.text_area("🎓 التخصصات:", value=data.get("majors", ""), height=100)
        
        if st.button("💾 حفظ", use_container_width=True):
            save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts, "majors": majors})
            st.success("✅ تم الحفظ!")
            st.rerun()
    elif password:
        st.error("❌ خطأ")
