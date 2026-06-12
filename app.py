import streamlit as st
import json
import os
import time

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

# عرض توست تحذيري مخفي داخل كود التشغيل الأولي لمنع التكرار المزعج
if not SERVICES_AVAILABLE and "toast_shown" not in st.session_state:
    st.toast("⚠️ ملف services.py غير موجود، سيتم استخدام الردود التلقائية للتجربة.", icon="⚠️")
    st.session_state.toast_shown = True

# ==========================================
# 2. تصميم CSS الزمردي الملكي الفاخر (نسخة الـ VIP) 💎✨
# ==========================================
st.markdown("""
<style>
/* 🌍 إعدادات عامة ومنع الانزلاق */
html, body, [data-testid="stAppViewContainer"], .main {
    overflow-x: hidden !important;
    max-width: 100vw !important;
    scroll-behavior: smooth;
}

/* 🟢 خلفية سينمائية فائقة الفخامة 🟢 */
.stApp {
    background-color: #020905; /* أسود زمردي عميق جداً */
    background-image: 
        radial-gradient(circle at 15% 0%, rgba(20, 75, 43, 0.35), transparent 40%),
        radial-gradient(circle at 85% 80%, rgba(212, 175, 55, 0.08), transparent 45%),
        radial-gradient(circle at 50% 50%, rgba(5, 22, 13, 0.8), transparent 100%);
    background-attachment: fixed;
    color: #fdf5e6;
}

/* 📜 شريط تمرير ذهبي مخصص للكمبيوتر 📜 */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(2, 9, 5, 0.9); 
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(to bottom, #aa771c, #d4af37, #fcf6ba);
    border-radius: 10px;
}

/* 👑 النصوص بتأثير الذهب الواقعي (Metallic Gold) 👑 */
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Tajawal:wght@500;700;900&display=swap');

.basmala {
    font-family: 'Amiri', serif;
    font-size: 2.8rem;
    text-align: center;
    background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 5px;
    text-shadow: 0px 5px 25px rgba(212, 175, 55, 0.3);
    letter-spacing: 1px;
}

.uni-title {
    font-family: 'Tajawal', sans-serif;
    font-size: 2.5rem;
    text-align: center;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 5px;
    letter-spacing: 0.5px;
    text-shadow: 0 5px 20px rgba(0,0,0,0.9), 0 0 10px rgba(255,255,255,0.2);
    line-height: 1.4;
}

.uni-title span { 
    color: #fcf6ba; 
    filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.6));
}

.branch-title {
    font-family: 'Tajawal', sans-serif;
    font-size: 1.15rem;
    text-align: center;
    color: #d4c4a1;
    letter-spacing: 3px;
    margin-bottom: 30px;
    font-weight: 500;
    text-transform: uppercase;
    opacity: 0.9;
}

/* ⚔️ فاصل ذهبي متوهج كالليزر ⚔️ */
hr {
    border: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(252, 246, 186, 0.8), rgba(212, 175, 55, 1), rgba(252, 246, 186, 0.8), transparent);
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.8), 0 0 5px rgba(255, 255, 255, 0.5);
    margin: 20px 0 40px 0;
    opacity: 0.7;
}

/* ========================================= */
/* 🌟 شريط الأزرار الأفقي (سلس وعصري) 🌟 */
/* ========================================= */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        padding-bottom: 25px !important;
        padding-top: 10px !important;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none; 
    }
    
    [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        display: none !important;
    }

    [data-testid="column"] {
        min-width: 150px !important; 
        flex: 0 0 auto !important;
        width: auto !important;
        padding: 0 8px !important;
    }
}

/* 💠 أزرار الخدمات (تأثير زجاجي فائق النقاء) 💠 */
div.stButton > button {
    font-family: 'Tajawal', sans-serif !important;
    background: rgba(15, 56, 34, 0.25) !important;
    backdrop-filter: blur(25px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(25px) saturate(150%) !important;
    border: 1px solid rgba(212, 175, 55, 0.25) !important;
    border-top: 1px solid rgba(252, 246, 186, 0.4) !important;
    border-radius: 16px !important;
    color: #fdf5e6 !important;
    padding: 14px 10px !important;
    width: 100% !important;
    height: auto !important;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 2px 10px rgba(255, 255, 255, 0.05) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    white-space: nowrap !important;
}

/* تأثير التوهج عند اللمس للزر */
div.stButton > button:hover, div.stButton > button:active {
    transform: translateY(-5px) scale(1.02) !important;
    background: rgba(20, 75, 43, 0.6) !important;
    border-color: #fcf6ba !important;
    color: #ffffff !important;
    box-shadow: 0 15px 35px rgba(212, 175, 55, 0.25), 0 0 15px rgba(212, 175, 55, 0.4) !important;
}

/* ========================================= */
/* 💬 رسائل الدردشة (Premium Glass Bubbles) 💬 */
/* ========================================= */
[data-testid="stChatMessage"] {
    background: rgba(8, 20, 14, 0.5) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-right: 4px solid #d4af37 !important;
    border-radius: 20px !important;
    padding: 1.8rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
    color: #fcfcfc !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 1.1rem !important;
    line-height: 1.7 !important;
    transition: transform 0.3s ease !important;
}

[data-testid="stChatMessage"]:hover {
    background: rgba(12, 30, 20, 0.6) !important;
    border-right-color: #fcf6ba !important;
}

/* ========================================= */
/* ⌨️ كبسولة الكتابة العائمة (Neon Input Capsule) ⌨️ */
/* ========================================= */
[data-testid="stChatInput"] {
    background: rgba(3, 10, 6, 0.85) !important;
    backdrop-filter: blur(30px) saturate(200%) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 40px !important;
    box-shadow: 0 15px 50px rgba(0,0,0,0.9), 0 0 20px rgba(212, 175, 55, 0.05) !important;
    padding: 8px 15px !important;
    margin-bottom: 20px !important;
    transition: all 0.4s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #fcf6ba !important;
    background: rgba(5, 15, 9, 0.95) !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.8), 0 0 25px rgba(212, 175, 55, 0.3), inset 0 0 10px rgba(212, 175, 55, 0.1) !important;
    transform: translateY(-3px) !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 1.1rem !important;
}

/* إخفاء علامة Streamlit السفلية وزر الرفع لتنظيف الواجهة */
footer {visibility: hidden;}
.stDeployButton {display:none;}

/* 👉 إخفاء الحروف المقطوعة في زر القائمة الجانبية مع إبقاء السهم باللون الذهبي اللامع */
[data-testid="collapsedControl"] {
    color: transparent !important;
    transition: all 0.3s ease !important;
}
[data-testid="collapsedControl"]:hover {
    background: rgba(212, 175, 55, 0.1) !important;
    border-radius: 50% !important;
}
[data-testid="collapsedControl"] svg {
    color: #fcf6ba !important;
    filter: drop-shadow(0 0 5px rgba(212, 175, 55, 0.8)) !important;
}
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
# عرض الرسائل السابقة مع إضافة الرموز التعبيرية الأنيقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# استقبال إدخال المستخدم
user_input = st.chat_input("تفضل بطرح استفسارك هنا...")

if st.session_state.auto_question:
    user_input = st.session_state.auto_question
    st.session_state.auto_question = None

# توليد الرد
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    with st.chat_message("assistant", avatar="🤖"):
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
                ai_response = "هذا رد تجريبي نظراً لعدم ربط دوال الذكاء الاصطناعي. يُرجى مراجعة إدارة الجامعة للمزيد من التفاصيل حول استفسارك."
            
            st.markdown(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# 7. لوحة الإدارة الجانبية (Sidebar Admin Panel)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #fcf6ba; text-align: center; text-shadow: 0 2px 10px rgba(212,175,55,0.5); font-family: Tajawal;'>⚙️ إدارة البيانات</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    admin_password = st.text_input("كلمة مرور المشرف 🔒", type="password")
    
    correct_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    
    if admin_password == correct_password:
        st.success("✅ تم التحقق")
        
        tab1, tab2 = st.tabs(["📝 تحرير البيانات", "📊 الإحصائيات"])
        
        with tab1:
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
                st.success("🎉 تم تحديث قاعدة البيانات بنجاح!")
        
        with tab2:
            if SERVICES_AVAILABLE:
                try:
                    stats = get_stats()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📋 إجمالي الأسئلة", stats.get("total", 0))
                    with col2:
                        st.metric("📅 أسئلة اليوم", stats.get("today", 0))
                    
                    st.markdown("---")
                    st.markdown("### 🔥 أكثر 5 أسئلة شيوعاً")
                    top_q = stats.get("top_questions", [])
                    if top_q:
                        for i, q in enumerate(top_q[:5], 1):
                            st.markdown(f"**{i}.** {q['question']}  `({q['count']} مرة)`")
                    else:
                        st.info("لا توجد أسئلة مسجلة بعد")
                    
                    st.markdown("---")
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
                st.warning("⚠️ الإحصائيات غير متاحة لعدم وجود ملف services.py")
            
    elif admin_password != "":
        st.error("❌ كلمة المرور غير صحيحة")
