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
# 1. إعداد الصفحة الأساسية والتهيئة
# ==========================================
st.set_page_config(
    page_title="جامعة القرآن الكريم - فرع غيل باوزير",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if not SERVICES_AVAILABLE and "toast_shown" not in st.session_state:
    st.toast("⚠️ ملف services.py غير موجود، سيتم استخدام الردود التلقائية للتجربة.", icon="⚠️")
    st.session_state.toast_shown = True

# ==========================================
# 2. تصميم CSS الزمردي الملكي الفاخر (المُطوّر) 💎
# ==========================================
st.markdown("""
<style>
/* استيراد الخطوط الفاخرة: Cairo للواجهات والأزرار، و Amiri للبسملة والعناوين الكلاسيكية */
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@300;400;500;600;700;900&display=swap');

/* تطبيق الخطوط على كامل التطبيق */
html, body, [data-testid="stAppViewContainer"], .main, p, span, label {
    font-family: 'Cairo', sans-serif !important;
    overflow-x: hidden !important;
    max-width: 100vw !important;
}

/* 🟢 الخلفية الملكية: تدرج زمردي عميق جداً يحاكي السجاد والمحاريب الفاخرة 🟢 */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% -20%, #092c1a 0%, #04140c 45%, #010604 100%) !important;
    background-attachment: fixed !important;
}

/* إخفاء الهيدر الافتراضي لـ Streamlit لإضفاء طابع تطبيقي احترافي */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* 🏆 تصميم البسملة الكلاسيكية الساحرة 🏆 */
.basmala {
    font-family: 'Amiri', serif !important;
    font-size: 2.8rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(135deg, #fff3cb 0%, #e5c158 50%, #aa8216 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-top: -20px;
    margin-bottom: 5px;
    filter: drop-shadow(0px 2px 10px rgba(229, 193, 88, 0.3));
}

/* 🏛️ العنوان الرئيسي للجامعة 🏛️ */
.uni-title-container {
    text-align: center;
    margin-bottom: 8px;
}

.uni-title {
    font-size: 2.4rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.3;
    text-shadow: 0 4px 20px rgba(0,0,0,0.6);
}

.uni-title span.gold-text { 
    background: linear-gradient(135deg, #ffffff 0%, #ffe391 60%, #e5c158 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

/* 📍 عنوان الفرع السفلي 📍 */
.branch-title {
    font-size: 1.15rem;
    text-align: center;
    color: #b3c6bd;
    font-weight: 400;
    letter-spacing: 1px;
    margin-bottom: 35px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
}

.branch-title::before, .branch-title::after {
    content: "";
    display: inline-block;
    width: 40px;
    height: 1px;
    background: linear-gradient(to right, transparent, #e5c158, transparent);
}

/* ⚜️ فاصل زخرفي ذهبي انسيابي ⚜️ */
.luxury-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(229, 193, 88, 0.6) 20%, rgba(255, 243, 203, 0.9) 50%, rgba(229, 193, 88, 0.6) 80%, transparent);
    box-shadow: 0 0 20px rgba(229, 193, 88, 0.4);
    margin: 25px 0;
    border: none;
}

/* ========================================= */
/* 📱 شريط الأزرار التفاعلية الأفقي الفاخر 📱 */
/* ========================================= */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        padding: 10px 5px 25px 5px !important;
        gap: 12px !important;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
    }
    [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        display: none !important; /* إخفاء شريط التمرير المزعج بالجوال */
    }
    [data-testid="column"] {
        min-width: 135px !important; 
        flex: 0 0 auto !important;
        width: auto !important;
    }
}

/* ✨ إعادة هندسة أزرار الخدمات بالكامل لخلق تأثير بلاط زجاجي مضيء (Glassmorphic Tiles) ✨ */
div.stButton > button {
    background: linear-gradient(135deg, rgba(16, 52, 34, 0.65) 0%, rgba(6, 23, 14, 0.85) 100%) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(229, 193, 88, 0.25) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 14px !important;
    color: #f3eae1 !important;
    padding: 14px 12px !important;
    width: 100% !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    transition: all 0.35s cubic-bezier(0.25, 1, 0.5, 1) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

/* تأثيرات التحويم والضغط الاحترافية */
div.stButton > button:hover {
    transform: translateY(-5px) !important;
    border-color: rgba(229, 193, 88, 0.8) !important;
    color: #ffffff !important;
    background: linear-gradient(135deg, rgba(23, 73, 48, 0.8) 0%, rgba(10, 37, 23, 0.95) 100%) !important;
    box-shadow: 0 15px 30px rgba(229, 193, 88, 0.25) !important;
}

div.stButton > button:active {
    transform: translateY(-1px) !important;
}

/* ========================================= */
/* 💬 فقاعات الدردشة المخصصة الفاخرة 💬 */
/* ========================================= */
/* إخفاء خلفيات ستريمليت الافتراضية للدردشة لتمكين تخصيصنا الكامل */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0.2rem 0 !important;
    box-shadow: none !important;
}

/* فقاعة رد المساعد (الذكاء الاصطناعي) الراقية */
.assistant-container {
    background: rgba(10, 34, 22, 0.55) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(229, 193, 88, 0.2) !important;
    border-right: 4px solid #e5c158 !important;
    border-radius: 16px;
    padding: 20px !important;
    margin: 10px 0 25px 0 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    color: #f4eee1 !important;
    font-size: 1.05rem !important;
    line-height: 1.7 !important;
}

/* فقاعة رسالة المستخدم الأنيقة */
.user-container {
    background: rgba(255, 255, 255, 0.04) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-left: 4px solid #b3c6bd !important;
    border-radius: 16px;
    padding: 16px 20px !important;
    margin: 10px 0 25px 0 !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
    color: #ffffff !important;
    font-size: 1.05rem !important;
    line-height: 1.6 !important;
}

/* ========================================= */
/* ⌨️ كبسولة المدخلات وصندوق الكتابة السفلي ⌨️ */
/* ========================================= */
[data-testid="stChatInput"] {
    background: rgba(4, 15, 9, 0.92) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border: 1px solid rgba(229, 193, 88, 0.35) !important;
    border-radius: 24px !important;
    box-shadow: 0 12px 45px rgba(0,0,0,0.85) !important;
    padding: 8px 16px !important;
    margin-bottom: 20px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #ffe391 !important;
    box-shadow: 0 0 30px rgba(229, 193, 88, 0.35), inset 0 0 12px rgba(229, 193, 88, 0.05) !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1.05rem !important;
}

/* ========================================= */
/* ⚙️ تخصيص القائمة الجانبية (Sidebar) بالكامل ⚙️ */
/* ========================================= */
[data-testid="stSidebar"] {
    background-color: #030f0a !important;
    border-right: 1px solid rgba(229, 193, 88, 0.15) !important;
}

/* تجميل التبويبات بالداخل */
button[data-baseweb="tab"] {
    color: #b3c6bd !important;
    font-size: 1rem !important;
    transition: all 0.3s !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #e5c158 !important;
    font-weight: bold !important;
    border-bottom-color: #e5c158 !important;
}

/* تجميل حقول النص الإدارية */
.stTextArea textarea, .stTextInput input {
    background-color: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(229, 193, 88, 0.2) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #e5c158 !important;
    box-shadow: 0 0 10px rgba(229, 193, 88, 0.2) !important;
}

/* تنظيف الواجهة من شعارات ستريمليت الهيكلية */
footer {visibility: hidden !important;}
.stDeployButton {display:none !important;}
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
# 4. الواجهة الرئيسية الفاخرة (الهيدر الملكي)
# ==========================================
st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="uni-title-container"><div class="uni-title"><span class="gold-text">جامعة القرآن الكريم</span><br>والعلوم الإسلامية</div></div>', unsafe_allow_html=True)
st.markdown('<div class="branch-title">فرع غيل باوزير - حضرموت</div>', unsafe_allow_html=True)

# ==========================================
# 5. شريط الخدمات التفاعلي (مُحسّن للتصفح والموبايل)
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

st.markdown('<div class="luxury-divider"></div>', unsafe_allow_html=True)

# ==========================================
# 6. محرك الدردشة (Chat Engine المطور بصرياً)
# ==========================================
# عرض رسائل المحادثة من خلال القوالب الزجاجية الفاخرة المحددة مسبقاً
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="assistant-container">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-container">{msg["content"]}</div>', unsafe_allow_html=True)

# استقبال إدخال المستخدم عبر الكبسولة المتوهجة
user_input = st.chat_input("تفضل بطرح استفسارك الأكاديمي هنا...")

if st.session_state.auto_question:
    user_input = st.session_state.auto_question
    st.session_state.auto_question = None

# معالجة المدخلات وتوليد الردود الملكية
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f'<div class="user-container">{user_input}</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        with st.spinner("جارٍ البحث في قاعدة البيانات والمعالجة..."):
            if SERVICES_AVAILABLE:
                try:
                    category = smart_classify(user_input)
                    context_data = st.session_state.db.get(category, st.session_state.db["info"])
                    ai_response = ask_ai(user_input, context_data)
                except Exception as e:
                    ai_response = f"عذراً، حدث خطأ في النظام الداخلي: {str(e)}"
            else:
                time.sleep(1)
                ai_response = "هذا الرد يمثل نموذجاً تجريبياً ذكياً لتوضيح الواجهة الفاخرة الجديدة. سيتم تفعيل الربط الديناميكي فور ربط ملف الخدمات البرمجية (services.py)."
            
            st.markdown(f'<div class="assistant-container">{ai_response}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

# ==========================================
# 7. لوحة الإدارة الجانبية الفاخرة (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #e5c158; text-align: center; font-weight:700; text-shadow: 0 2px 8px rgba(0,0,0,0.7); margin-top:15px;'>⚙️ لوحة التحكم</h2>", unsafe_allow_html=True)
    st.markdown("<div style='height:1px; background:linear-gradient(to right, transparent, #e5c158, transparent); margin:15px 0;'></div>", unsafe_allow_html=True)
    
    admin_password = st.text_input("رمز مرور المشرف 🔒", type="password")
    correct_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    
    if admin_password == correct_password:
        st.success("🔓 تم التصريح بالدخول")
        
        tab1, tab2 = st.tabs(["📝 إدارة البيانات", "📊 التقارير والإحصاء"])
        
        with tab1:
            edit_info = st.text_area("معلومات الواجهة العامة", st.session_state.db.get("info", ""), height=90)
            edit_schedules = st.text_area("إدارة الجداول الدراسية", st.session_state.db.get("schedules", ""), height=90)
            edit_exams = st.text_area("مواعيد وترتيبات الامتحانات", st.session_state.db.get("exams", ""), height=90)
            edit_fees = st.text_area("الرسوم المالية والسداد", st.session_state.db.get("fees", ""), height=90)
            edit_contacts = st.text_area("بيانات قنوات التواصل", st.session_state.db.get("contacts", ""), height=90)
            edit_majors = st.text_area("الأقسام والتخصصات المتاحة", st.session_state.db.get("majors", ""), height=90)
            
            # زر حفظ مخصص وبارز باللون الذهبي المطفي للوحة الإدارة
            if st.button("💾 حفظ التحديثات وقاعدة المعرفة", use_container_width=True):
                st.session_state.db = {
                    "info": edit_info,
                    "schedules": edit_schedules,
                    "exams": edit_exams,
                    "fees": edit_fees,
                    "contacts": edit_contacts,
                    "majors": edit_majors
                }
                save_data(st.session_state.db)
                st.toast("🎉 تم حفظ البيانات بنجاح!", icon="✅")
        
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
                    st.markdown("### 🔥 الأسئلة الأكثر شيوعاً")
                    top_q = stats.get("top_questions", [])
                    if top_q:
                        for i, q in enumerate(top_q[:5], 1):
                            st.markdown(f"**{i}.** {q['question']}  `({q['count']} مرة)`")
                    else:
                        st.info("لا توجد أسئلة مسجلة بعد")
                    
                    st.markdown("---")
                    st.markdown("### 📊 فئات الاستفسارات")
                    categories_data = stats.get("categories", {})
                    if categories_data:
                        for cat, count in categories_data.items():
                            st.markdown(f"- **{cat}**: {count} سؤال")
                    else:
                        st.info("لا توجد بيانات فئات")
                        
                except Exception as e:
                    st.error(f"خطأ في تحميل الإحصائيات: {str(e)}")
            else:
                st.info("📊 الإحصائيات ستظهر هنا بمجرد تفعيل ملف الإحصائيات والدوال الذكية.")
            
    elif admin_password != "":
        st.error("❌ الرمز السري غير صحيح")
