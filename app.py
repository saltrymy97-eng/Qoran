import streamlit as st
import json
import os
import time

# استدعاء دوال الذكاء الاصطناعي (تأكد من وجود ملف services.py الخاص بك)
try:
    from services import ask_ai, smart_classify
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    st.toast("⚠️ ملف services.py غير موجود، سيتم استخدام الردود التلقائية للتجربة.", icon="⚠️")

# ==========================================
# 1. إعداد الصفحة الأساسية
# ==========================================
st.set_page_config(
    page_title="جامعة القرآن الكريم - فرع غيل باوزير",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. تصميم CSS الملكي الفاخر (شامل إصلاحات الجوال)
# ==========================================
st.markdown("""
<style>
/* 🔴 منع الشاشة بأكملها من الانزلاق لليمين واليسار في الجوال 🔴 */
html, body, [data-testid="stAppViewContainer"], .main {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}

/* خلفية داكنة ملكية (أسود أوبسيديان) */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1a1500 0%, #05070a 40%, #020305 100%);
    background-attachment: fixed;
    color: #e6e0d4;
}

/* النصوص والخطوط الذهبية */
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap');
.basmala {
    font-family: 'Amiri', serif;
    font-size: 2.8rem;
    text-align: center;
    background: linear-gradient(to bottom, #ffefaa, #d4af37, #997a15);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 10px;
    text-shadow: 0px 5px 25px rgba(212, 175, 55, 0.4);
}

.uni-title {
    font-size: 2.3rem;
    text-align: center;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 5px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    line-height: 1.4;
}

.uni-title span { 
    color: #d4af37; 
    filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.6));
}

.branch-title {
    font-size: 1.2rem;
    text-align: center;
    color: #b3a895;
    letter-spacing: 1px;
    margin-bottom: 25px;
    font-weight: 300;
}

/* فاصل ذهبي أنيق */
hr {
    border: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(212, 175, 55, 0.8), transparent);
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
    margin: 20px 0 30px 0;
}

/* ========================================= */
/* 🌟 شريط الأزرار الأفقي القابل للتمرير (للجوال) 🌟 */
/* ========================================= */
@media (max-width: 768px) {
    /* إجبار الأعمدة على البقاء في صف واحد وتفعيل التمرير الأفقي */
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        padding-bottom: 20px !important;
        padding-top: 5px !important;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch; /* لأجهزة أبل */
        /* إخفاء شريط التمرير الافتراضي */
        scrollbar-width: none; 
    }
    
    [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        display: none !important;
    }

    /* تحديد عرض ثابت لكل زر حتى لا ينضغط */
    [data-testid="column"] {
        min-width: 150px !important; 
        flex: 0 0 auto !important;
        width: auto !important;
        padding: 0 5px !important;
    }
}

/* تصميم أزرار الخدمات (زجاجي أسود وذهبي) */
div.stButton > button {
    background: linear-gradient(135deg, rgba(30, 35, 40, 0.6), rgba(10, 12, 15, 0.9)) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-top: 1px solid rgba(255, 230, 150, 0.6) !important;
    border-radius: 15px !important;
    color: #f4ebd8 !important;
    padding: 12px 10px !important;
    width: 100% !important;
    height: auto !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5) !important;
    font-size: 1rem !important;
    font-weight: bold !important;
    white-space: nowrap !important; /* منع النص من النزول لسطرين */
}

/* تأثير عند اللمس/الماوس */
div.stButton > button:hover, div.stButton > button:active {
    transform: translateY(-3px) scale(1.02) !important;
    background: linear-gradient(135deg, rgba(40, 45, 50, 0.8), rgba(20, 25, 30, 0.9)) !important;
    border-color: #d4af37 !important;
    color: #ffffff !important;
    box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4) !important;
}

/* ========================================= */
/* رسائل الدردشة وحقل الإدخال */
/* ========================================= */
[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(15, 18, 25, 0.7), rgba(5, 8, 12, 0.9)) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-right: 3px solid #d4af37 !important;
    border-radius: 15px !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
    color: #e6e0d4 !important;
}

/* كبسولة الكتابة العائمة */
[data-testid="stChatInput"] {
    background: rgba(10, 12, 15, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 30px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
    padding: 5px 10px !important;
    margin-bottom: 10px !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #ffd700 !important;
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.4) !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1rem !important;
}

/* إخفاء علامة Streamlit السفلية */
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. إدارة البيانات (قاعدة المعرفة المصغرة)
# ==========================================
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "info": "أهلاً بك في جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير. كيف يمكنني مساعدتك؟",
        "schedules": "الجداول الدراسية تُحدث بداية كل فصل دراسي. يرجى مراجعة شؤون الطلاب.",
        "exams": "تبدأ الامتحانات النصفية في الأسبوع الثامن من الفصل الدراسي.",
        "fees": "يمكن تسديد الرسوم عبر البنك أو الدفع المباشر في الإدارة المالية.",
        "contacts": "للتواصل: 053XXXXX أو زيارة مبنى الفرع بغيل باوزير.",
        "majors": "التخصصات: القرآن وعلومه، الشريعة، والدراسات الإسلامية."
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()

if "messages" not in st.session_state:
    # رسالة ترحيبية افتراضية
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك في المساعد الذكي لجامعة القرآن الكريم - فرع غيل باوزير. تفضل بطرح استفسارك أو اختر من الخدمات المتاحة أعلاه."}]

if "auto_question" not in st.session_state:
    st.session_state.auto_question = None

# ==========================================
# 4. الواجهة الرئيسية (رأس الصفحة)
# ==========================================
st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="uni-title"><span>🕌</span> جامعة القرآن الكريم<br>والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="branch-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)

# ==========================================
# 5. شريط الخدمات (التمرير الأفقي في الجوال)
# ==========================================
col1, col2, col3, col4, col5 = st.columns(5)

if col1.button("📅 الجداول"):
    st.session_state.auto_question = "أريد الاستفسار عن جداول المحاضرات"
if col2.button("📝 الامتحانات"):
    st.session_state.auto_question = "ما هي مواعيد وترتيبات الامتحانات؟"
if col3.button("💰 الرسوم"):
    st.session_state.auto_question = "أريد معرفة تفاصيل الرسوم الدراسية وطرق السداد"
if col4.button("📞 التواصل"):
    st.session_state.auto_question = "كيف يمكنني التواصل مع إدارة الفرع؟"
if col5.button("🎓 التخصصات"):
    st.session_state.auto_question = "ما هي التخصصات الأكاديمية المتاحة؟"

st.markdown('<hr>', unsafe_allow_html=True)

# ==========================================
# 6. محرك الدردشة (Chat Engine)
# ==========================================
# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# استقبال إدخال المستخدم
user_input = st.chat_input("تفضل بطرح استفسارك هنا...")

# معالجة الضغط على أزرار الخدمات
if st.session_state.auto_question:
    user_input = st.session_state.auto_question
    st.session_state.auto_question = None

# توليد الرد
if user_input:
    # حفظ وطباعة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # الرد من المساعد
    with st.chat_message("assistant"):
        with st.spinner("جارٍ معالجة استفسارك..."):
            if SERVICES_AVAILABLE:
                try:
                    category = smart_classify(user_input)
                    context_data = st.session_state.db.get(category, st.session_state.db["info"])
                    ai_response = ask_ai(user_input, context_data)
                except Exception as e:
                    ai_response = f"عذراً، حدث خطأ في النظام: {str(e)}"
            else:
                # رد وهمي في حال غياب ملف الذكاء الاصطناعي (للتجربة)
                time.sleep(1)
                ai_response = "هذا رد تجريبي نظراً لعدم ربط دوال الذكاء الاصطناعي. يُرجى مراجعة إدارة الجامعة للمزيد من التفاصيل حول استفسارك."
            
            st.markdown(ai_response)
    
    # حفظ رد المساعد
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# 7. لوحة الإدارة الجانبية (Sidebar Admin Panel)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #d4af37; text-align: center;'>⚙️ إدارة البيانات</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    admin_password = st.text_input("كلمة مرور المشرف 🔒", type="password")
    
    if admin_password == st.secrets["ADMIN_PASSWORD"]: # يفضل تغييرها واستخدام st.secrets
        st.success("✅ تم التحقق")
        
        edit_info = st.text_area("معلومات عامة", st.session_state.db.get("info", ""), height=100)
        edit_schedules = st.text_area("الجداول", st.session_state.db.get("schedules", ""), height=100)
        edit_exams = st.text_area("الامتحانات", st.session_state.db.get("exams", ""), height=100)
        edit_fees = st.text_area("الرسوم", st.session_state.db.get("fees", ""), height=100)
        edit_contacts = st.text_area("جهات الاتصال", st.session_state.db.get("contacts", ""), height=100)
        edit_majors = st.text_area("التخصصات", st.session_state.db.get("majors", ""), height=100)
        
        if st.button("💾 حفظ البيانات", use_container_width=True):
            st.session_state.db = {
                "info": edit_info,
                "schedules": edit_schedules,
                "exams": edit_exams,
                "fees": edit_fees,
                "contacts": edit_contacts,
                "majors": edit_majors
            }
            save_data(st.session_state.db)
            st.success("🎉 تم تحديث قاعدة معرفة الذكاء الاصطناعي بنجاح!")
            
    elif admin_password != "":
        st.error("❌ كلمة المرور غير صحيحة")
