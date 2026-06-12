import streamlit as st
import json
import os
import time
import datetime
import random

# استدعاء دوال الذكاء الاصطناعي (تأكد من وجود ملف services.py الخاص بك)
try:
    from services import ask_ai, smart_classify, get_stats
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False

# ==========================================
# 1. إعداد الصفحة الأساسية
# ==========================================
st.set_page_config(
    page_title="جامعة القرآن الكريم - فرع غيل باوزير",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# عرض توست تحذيري للنسخة التجريبية
if not SERVICES_AVAILABLE and "toast_shown" not in st.session_state:
    st.toast("⚠️ النسخة التجريبية: ملف services.py غير متصل.", icon="⚠️")
    st.session_state.toast_shown = True

# ==========================================
# 2. تصميم CSS الزمردي الملكي الفائق 💎
# ==========================================
st.markdown("""
<style>
/* استيراد الخطوط الفاخرة */
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Tajawal:wght@400;500;700;900&display=swap');

/* تطبيق خط "تاجوال" على جميع نصوص التطبيق */
html, body, div, span, p, h1, h2, h3, h4, h5, h6, button, input, textarea {
    font-family: 'Tajawal', sans-serif !important;
}

/* منع الشاشة من الانزلاق الأفقي في الجوال */
html, body, [data-testid="stAppViewContainer"], .main {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}

/* 🟢 خلفية زمردية داكنة ملكية 🟢 */
.stApp {
    background: radial-gradient(circle at 50% -10%, #0a2e1c 0%, #04120a 50%, #010402 100%) !important;
    background-attachment: fixed;
    color: #f0e6d2;
}

/* ========================================= */
/* نصوص العناوين والآيات (خط الأميري) */
/* ========================================= */
.basmala {
    font-family: 'Amiri', serif !important;
    font-size: 2.8rem;
    text-align: center;
    background: linear-gradient(to bottom, #fff1b8, #d4af37, #b89115);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 5px;
    text-shadow: 0px 4px 25px rgba(212, 175, 55, 0.5);
}

.uni-title {
    font-size: 2.4rem;
    text-align: center;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 5px;
    letter-spacing: 0.5px;
    text-shadow: 0 4px 15px rgba(0,0,0,0.9);
    line-height: 1.4;
}

.uni-title span { 
    color: #ffd700; 
    filter: drop-shadow(0 0 15px rgba(255, 215, 0, 0.6));
}

.branch-title {
    font-size: 1.2rem;
    text-align: center;
    color: #c9bc9c;
    letter-spacing: 2px;
    margin-bottom: 15px;
    font-weight: 500;
    text-transform: uppercase;
}

/* 🌟 بطاقة آية اليوم الفاخرة 🌟 */
.ayah-card {
    text-align: center;
    margin: 10px auto 30px auto;
    padding: 20px 15px;
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.05), rgba(10, 46, 28, 0.4));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-left: 4px solid #d4af37;
    border-right: 4px solid #d4af37;
    border-radius: 15px;
    max-width: 700px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 15px rgba(212, 175, 55, 0.05);
}

.ayah-text {
    font-family: 'Amiri', serif !important;
    font-size: 1.6rem;
    color: #f7e296;
    line-height: 1.8;
    text-shadow: 0 2px 10px rgba(212, 175, 55, 0.3);
}

/* فاصل ذهبي متوهج */
hr {
    border: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(212, 175, 55, 0.8), transparent);
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.7);
    margin: 10px 0 30px 0;
}

/* ========================================= */
/* 💠 تصميم أزرار الخدمات (Glassmorphism) 💠 */
/* ========================================= */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        padding-bottom: 20px !important;
        padding-top: 10px !important;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none; 
    }
    [data-testid="stHorizontalBlock"]::-webkit-scrollbar { display: none !important; }
    [data-testid="column"] {
        min-width: 145px !important; 
        flex: 0 0 auto !important;
        width: auto !important;
        padding: 0 6px !important;
    }
}

div.stButton > button {
    background: linear-gradient(135deg, rgba(15, 56, 34, 0.8), rgba(5, 22, 13, 0.95)) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(212, 175, 55, 0.4) !important;
    border-top: 1px solid rgba(255, 240, 180, 0.6) !important;
    border-radius: 16px !important;
    color: #fdf5e6 !important;
    padding: 14px 10px !important;
    width: 100% !important;
    height: auto !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6), inset 0 2px 5px rgba(255,255,255,0.05) !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
}

div.stButton > button:hover, div.stButton > button:active {
    transform: translateY(-5px) scale(1.04) !important;
    background: linear-gradient(135deg, rgba(21, 76, 44, 1), rgba(10, 32, 18, 1)) !important;
    border-color: #ffd700 !important;
    color: #ffffff !important;
    box-shadow: 0 15px 30px rgba(212, 175, 55, 0.4), inset 0 0 10px rgba(212, 175, 55, 0.2) !important;
}

/* ========================================= */
/* 💬 رسائل الدردشة (البطاقات) 💬 */
/* ========================================= */
[data-testid="stChatMessage"] {
    background: rgba(6, 20, 12, 0.75) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(212, 175, 55, 0.15) !important;
    border-right: 4px solid #d4af37 !important;
    border-radius: 18px !important;
    padding: 1.8rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    color: #f0e6d2 !important;
    font-size: 1.1rem !important;
    line-height: 1.7 !important;
}

/* ========================================= */
/* ⌨️ كبسولة الكتابة العائمة (Input Field) ⌨️ */
/* ========================================= */
[data-testid="stChatInput"] {
    background: rgba(3, 10, 6, 0.95) !important;
    backdrop-filter: blur(25px) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 35px !important;
    box-shadow: 0 15px 50px rgba(0,0,0,0.9) !important;
    padding: 8px 15px !important;
    margin-bottom: 20px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #ffd700 !important;
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.5), inset 0 0 15px rgba(212, 175, 55, 0.2) !important;
    transform: translateY(-3px) !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1.1rem !important;
    font-weight: 500 !important;
}

/* ========================================= */
/* ⚙️ القائمة الجانبية (Sidebar) الملكية ⚙️ */
/* ========================================= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #05160d 0%, #010402 100%) !important;
    border-left: 1px solid rgba(212, 175, 55, 0.2) !important;
    box-shadow: -5px 0 20px rgba(0,0,0,0.8) !important;
}

[data-testid="stSidebar"] input {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(212, 175, 55, 0.4) !important;
    color: #ffd700 !important;
    border-radius: 10px !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 1.1rem !important;
}

[data-testid="stSidebar"] input:focus {
    border-color: #ffd700 !important;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.4) !important;
}

/* إخفاء الزوائد */
footer {visibility: hidden;}
.stDeployButton {display:none;}
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
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك في المساعد الذكي لجامعة القرآن الكريم - فرع غيل باوزير. تفضل بطرح استفسارك أو اختر من الخدمات المتاحة أعلاه."}]

if "auto_question" not in st.session_state:
    st.session_state.auto_question = None

# ==========================================
# 4. الواجهة الرئيسية (رأس الصفحة + آية اليوم)
# ==========================================
st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="uni-title"><span>🕌</span> جامعة القرآن الكريم<br>والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="branch-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)

# 📖 منطق اختيار آية اليوم (تتغير يومياً)
ayahs = [
    "﴿ إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾",
    "﴿ يَرْفَعِ اللَّهُ الَّذِينَ آمَنُوا مِنكُمْ وَالَّذِينَ أُوتُوا الْعِلْمَ دَرَجَاتٍ ﴾",
    "﴿ وَقُل رَّبِّ زِدْنِي عِلْمًا ﴾",
    "﴿ ن ۚ وَالْقَلَمِ وَمَا يَسْطُرُونَ ﴾",
    "﴿ وَأَن لَّيْسَ لِلْإِنسَانِ إِلَّا مَا سَعَىٰ ﴾",
    "﴿ شَهْرُ رَمَضَانَ الَّذِي أُنزِلَ فِيهِ الْقُرْآنُ هُدًى لِّلنَّاسِ ﴾",
    "﴿ وَكَذَٰلِكَ أَوْحَيْنَا إِلَيْكَ رُوحًا مِّنْ أَمْرِنَا ﴾"
]
random.seed(datetime.date.today().toordinal()) # تثبيت العشوائية لتتغير يومياً فقط
ayah_of_the_day = random.choice(ayahs)
random.seed() # إعادة تعيين العشوائية لباقي التطبيق

st.markdown(f'<div class="ayah-card"><div class="ayah-text">{ayah_of_the_day}</div></div>', unsafe_allow_html=True)

# ==========================================
# 5. شريط الخدمات (التمرير الأفقي في الجوال)
# ==========================================
col1, col2, col3, col4, col5 = st.columns(5)

if col1.button("📅 الجداول"):
    st.session_state.auto_question = "أريد الاستفسار عن جداول المحاضرات"
    st.rerun()
if col2.button("📝 الامتحانات"):
    st.session_state.auto_question = "ما هي مواعيد وترتيبات الامتحانات؟"
    st.rerun()
if col3.button("💰 الرسوم"):
    st.session_state.auto_question = "أريد معرفة تفاصيل الرسوم الدراسية وطرق السداد"
    st.rerun()
if col4.button("📞 التواصل"):
    st.session_state.auto_question = "كيف يمكنني التواصل مع إدارة الفرع؟"
    st.rerun()
if col5.button("🎓 التخصصات"):
    st.session_state.auto_question = "ما هي التخصصات الأكاديمية المتاحة؟"
    st.rerun()

st.markdown('<hr>', unsafe_allow_html=True)

# ==========================================
# 6. محرك الدردشة (Chat Engine)
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("تفضل بطرح استفسارك هنا...")

if st.session_state.auto_question:
    user_input = st.session_state.auto_question
    st.session_state.auto_question = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
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
                time.sleep(1)
                ai_response = "هذا رد تجريبي. يُرجى مراجعة إدارة الجامعة للمزيد من التفاصيل حول استفسارك."
            
            st.markdown(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# 7. لوحة الإدارة الجانبية (Sidebar Admin Panel)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #ffd700; text-align: center; font-weight: 900; text-shadow: 0 2px 10px rgba(212,175,55,0.4); margin-bottom: 20px;'>⚙️ الإدارة المركزية</h2>", unsafe_allow_html=True)
    
    admin_password = st.text_input("🔑 كلمة مرور المشرف", type="password", placeholder="أدخل الرمز السري...")
    
    correct_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    
    if admin_password == correct_password:
        st.success("✅ تم التحقق بنجاح")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📝 قاعدة المعرفة", "📊 الإحصائيات"])
        
        with tab1:
            edit_info = st.text_area("معلومات عامة", st.session_state.db.get("info", ""), height=100)
            edit_schedules = st.text_area("الجداول", st.session_state.db.get("schedules", ""), height=100)
            edit_exams = st.text_area("الامتحانات", st.session_state.db.get("exams", ""), height=100)
            edit_fees = st.text_area("الرسوم", st.session_state.db.get("fees", ""), height=100)
            edit_contacts = st.text_area("جهات الاتصال", st.session_state.db.get("contacts", ""), height=100)
            edit_majors = st.text_area("التخصصات", st.session_state.db.get("majors", ""), height=100)
            
            if st.button("💾 حفظ وتحديث البيانات", use_container_width=True):
                st.session_state.db = {
                    "info": edit_info,
                    "schedules": edit_schedules,
                    "exams": edit_exams,
                    "fees": edit_fees,
                    "contacts": edit_contacts,
                    "majors": edit_majors
                }
                save_data(st.session_state.db)
                st.success("🎉 تم التحديث بنجاح!")
        
        with tab2:
            if SERVICES_AVAILABLE:
                try:
                    stats = get_stats()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📋 إجمالي الأسئلة", stats.get("total", 0))
                    with col2:
                        st.metric("📅 أسئلة اليوم", stats.get("today", 0))
                    
                    st.markdown("### 🔥 أكثر 5 أسئلة شيوعاً")
                    top_q = stats.get("top_questions", [])
                    if top_q:
                        for i, q in enumerate(top_q[:5], 1):
                            st.markdown(f"**{i}.** {q['question']}  `({q['count']} مرة)`")
                    else:
                        st.info("لا توجد أسئلة مسجلة بعد")
                    
                    st.markdown("### 📊 توزيع الفئات")
                    categories_data = stats.get("categories", {})
                    if categories_data:
                        for cat, count in categories_data.items():
                            st.markdown(f"- **{cat}**: {count} سؤال")
                    else:
                        st.info("لا توجد بيانات فئات")
                        
                except Exception as e:
                    st.error(f"خطأ في تحميل الإحصائيات: {str(e)}")
            else:
                st.warning("⚠️ الإحصائيات معطلة في النسخة التجريبية.")
            
    elif admin_password != "":
        st.error("❌ الرمز السري غير صحيح")
