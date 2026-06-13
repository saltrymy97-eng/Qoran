import streamlit as st
import json
import os
import time
import re

# استيراد مكتبات قراءة الملفات (مع معالجة عدم وجودها)
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# استدعاء دوال الذكاء الاصطناعي
try:
    from services import ask_ai, smart_classify, get_stats
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False

# ==========================================
# 1. إعداد الصفحة الأساسية
# ==========================================
st.set_page_config(
    page_title="جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if not SERVICES_AVAILABLE and "toast_shown" not in st.session_state:
    st.toast("ملف services.py غير موجود، سيتم استخدام الردود التلقائية للتجربة.", icon=":material/warning:")
    st.session_state.toast_shown = True

# ==========================================
# 2. تصميم CSS الأكاديمي الفاخر والمريح
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400;1,700&family=Tajawal:wght@400;500;700;800;900&display=swap');

html, body, [data-testid="stAppViewContainer"], .main {
    overflow-x: hidden !important;
    max-width: 100vw !important;
    scroll-behavior: smooth;
}

.stApp {
    background-color: #fbfcfb !important;
    color: #2b3a30 !important;
    font-family: 'Tajawal', sans-serif !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #0f5132; border-radius: 10px; }

.basmala {
    font-family: 'Amiri', serif !important;
    font-size: 1.8rem !important;
    text-align: center;
    color: #bfa15f !important;
    margin-bottom: 8px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.uni-title {
    font-family: 'Tajawal', sans-serif !important;
    font-size: 2.2rem !important;
    text-align: center;
    font-weight: 800;
    color: #0f5132 !important;
    margin-bottom: 5px;
    line-height: 1.3;
}

.branch-title {
    font-family: 'Tajawal', sans-serif !important;
    font-size: 1.05rem !important;
    text-align: center;
    color: #6c757d !important;
    letter-spacing: 1px;
    margin-bottom: 25px;
    font-weight: 500;
}

hr {
    border: 0 !important;
    height: 1px !important;
    background: linear-gradient(to right, transparent, #bfa15f, transparent) !important;
    margin: 25px 0 !important;
    opacity: 0.4;
}

@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        padding-bottom: 15px !important;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
    }
    [data-testid="column"] {
        min-width: 140px !important;
        flex: 0 0 auto !important;
        width: auto !important;
    }
}

div.stButton > button {
    font-family: 'Tajawal', sans-serif !important;
    background-color: #ffffff !important;
    color: #0f5132 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 12px 8px !important;
    width: 100% !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

div.stButton > button:hover, div.stButton > button:active {
    background-color: #0f5132 !important;
    color: #ffffff !important;
    border-color: #0f5132 !important;
    box-shadow: 0 4px 12px rgba(15, 81, 50, 0.15) !important;
    transform: translateY(-1px);
}

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #edf2f7 !important;
    border-right: 4px solid #0f5132 !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.01) !important;
    color: #2d3748 !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.6 !important;
}

[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
    padding: 6px 12px !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #0f5132 !important;
    box-shadow: 0 10px 25px rgba(15, 81, 50, 0.08) !important;
}

[data-testid="stChatInput"] textarea {
    color: #1e293b !important;
    font-family: 'Tajawal', sans-serif !important;
}

[data-testid="stSidebar"] {
    background-color: #f4f6f4 !important;
    border-left: 1px solid #e2e8f0 !important;
}

[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: #0f5132 !important;
    box-shadow: 0 0 0 1px #0f5132 !important;
}

[data-testid="stSidebar"] [data-baseweb="tab"] {
    color: #4a5568 !important;
    font-family: 'Tajawal', sans-serif !important;
}
[data-testid="stSidebar"] [aria-selected="true"] {
    color: #0f5132 !important;
    font-weight: bold !important;
}

/* ===== 🛡️ حماية الصفحة - إخفاء كل شيء ===== */
footer {visibility: hidden !important;}
.stDeployButton {display: none !important;}
[data-testid="stMainMenu"] {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stHeader"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}

/* ===== إخفاء الشريط السفلي نهائياً ===== */
[data-testid="stBottom"] {display: none !important;}
[data-testid="stChatInput"] + div {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. دوال معالجة اللغة العربية
# ==========================================
def remove_tashkeel(text):
    tashkeel = re.compile(r'[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED]')
    return tashkeel.sub('', text)

def normalize_arabic(text):
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ة', 'ه')
    return text

def clean_text(text):
    text = remove_tashkeel(text)
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)

# ==========================================
# 4. إدارة البيانات
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

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.type
    
    if "wordprocessingml" in file_type or uploaded_file.name.endswith('.docx'):
        if not DOCX_AVAILABLE:
            st.error("مكتبة python-docx غير مثبتة.")
            return None
        doc = Document(uploaded_file)
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())
        return clean_text('\n'.join(text_parts))
    
    elif "pdf" in file_type or uploaded_file.name.endswith('.pdf'):
        if not PDF_AVAILABLE:
            st.error("مكتبة PyPDF2 غير مثبتة.")
            return None
        reader = PdfReader(uploaded_file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return clean_text('\n'.join(text_parts))
    
    else:
        st.error("نوع الملف غير مدعوم. الرجاء رفع ملف Word (.docx) أو PDF.")
        return None

def distribute_text_to_fields(text):
    fields = {
        "info": "",
        "schedules": "",
        "exams": "",
        "fees": "",
        "contacts": "",
        "majors": ""
    }
    
    patterns = {
        "info": [
            r"معلومات عامة[:\s]*", r"معلومات اساسية[:\s]*", r"عن الجامعة[:\s]*",
            r"نبذة[:\s]*", r"تعريف[:\s]*", r"المعلومات العامة[:\s]*"
        ],
        "schedules": [
            r"الجداول[:\s]*", r"جداول المحاضرات[:\s]*", r"الجداول الدراسية[:\s]*",
            r"جدول[:\s]*", r"المحاضرات[:\s]*", r"المواعيد[:\s]*"
        ],
        "exams": [
            r"الامتحانات[:\s]*", r"الاختبارات[:\s]*", r"مواعيد الامتحانات[:\s]*",
            r"نظام الامتحانات[:\s]*", r"التقويم[:\s]*"
        ],
        "fees": [
            r"الرسوم[:\s]*", r"الرسوم الدراسية[:\s]*", r"المصاريف[:\s]*",
            r"التكاليف[:\s]*", r"الدفع[:\s]*", r"السداد[:\s]*", r"الاقساط[:\s]*"
        ],
        "contacts": [
            r"جهات الاتصال[:\s]*", r"التواصل[:\s]*", r"اتصل بنا[:\s]*",
            r"الهاتف[:\s]*", r"العنوان[:\s]*", r"الموقع[:\s]*", r"البريد[:\s]*"
        ],
        "majors": [
            r"التخصصات[:\s]*", r"التخصص[:\s]*", r"الاقسام[:\s]*",
            r"الشعب[:\s]*", r"البرامج[:\s]*", r"المسارات[:\s]*"
        ]
    }
    
    sections = {}
    current_field = "info"
    sections[current_field] = []
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        matched = False
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    current_field = field
                    line_content = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    if line_content:
                        sections.setdefault(current_field, []).append(line_content)
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            sections.setdefault(current_field, []).append(line)
    
    for field in fields:
        if field in sections:
            fields[field] = '\n'.join(sections[field]).strip()
    
    return fields

# ==========================================
# 5. الحالة السرية للإدارة
# ==========================================
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "db" not in st.session_state:
    st.session_state.db = load_data()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك في المساعد الذكي لجامعة القرآن الكريم - فرع غيل باوزير. تفضل بطرح استفسارك أو اختر من الخدمات المتاحة أعلاه."}]

if "auto_question" not in st.session_state:
    st.session_state.auto_question = None

# ==========================================
# 6. الواجهة الرئيسية (رأس الصفحة)
# ==========================================
st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="uni-title">جامعة القرآن الكريم<br>والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="branch-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)

# ==========================================
# 7. شريط الخدمات (يظهر فقط للطلاب)
# ==========================================
if not st.session_state.admin_mode:
    col1, col2, col3, col4, col5 = st.columns(5)

    if col1.button("الجداول", icon=":material/calendar_month:"):
        st.session_state.auto_question = "أريد الاستفسار عن جداول المحاضرات"
        st.rerun()
    if col2.button("الامتحانات", icon=":material/edit_document:"):
        st.session_state.auto_question = "ما هي مواعيد وترتيبات الامتحانات؟"
        st.rerun()
    if col3.button("الرسوم", icon=":material/payments:"):
        st.session_state.auto_question = "أريد معرفة تفاصيل الرسوم الدراسية وطرق السداد"
        st.rerun()
    if col4.button("التواصل", icon=":material/call:"):
        st.session_state.auto_question = "كيف يمكنني التواصل مع إدارة الفرع؟"
        st.rerun()
    if col5.button("التخصصات", icon=":material/school:"):
        st.session_state.auto_question = "ما هي التخصصات الأكاديمية المتاحة؟"
        st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)

# ==========================================
# 8. محرك الدردشة
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=":material/school:" if msg["role"] == "assistant" else ":material/person:"):
        st.markdown(msg["content"])

# ==========================================
# 9. وضع الإدارة - واجهة محسنة بنفس تصميم الرئيسية
# ==========================================
if st.session_state.admin_mode:
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h2 style="color: #0f5132; font-family: 'Tajawal', sans-serif; font-weight: 800; font-size: 2rem; margin-bottom: 5px;">
            🔐 لوحة الإدارة
        </h2>
        <p style="color: #6c757d; font-family: 'Tajawal', sans-serif; font-size: 1.05rem;">
            جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    admin_password = st.text_input("🔑 كلمة مرور المشرف", type="password", key="admin_pwd")
    correct_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    
    if admin_password == correct_password:
        st.success("✅ تم التحقق - أهلاً بك في لوحة الإدارة")
        
        tab1, tab2 = st.tabs(["📝 تحرير البيانات", "📊 الإحصائيات"])
        
        with tab1:
            st.markdown("### 📂 رفع ملف بيانات")
            uploaded_file = st.file_uploader(
                "ارفع ملف Word أو PDF بالعربية",
                type=["docx", "pdf"],
                help="الملف يدعم اللغة العربية بالكامل مع التشكيل",
                key="upload_admin"
            )
            
            if uploaded_file is not None:
                if st.button("🚀 معالجة الملف", icon=":material/upload:", key="process_admin"):
                    extracted_text = extract_text_from_file(uploaded_file)
                    if extracted_text:
                        distributed_fields = distribute_text_to_fields(extracted_text)
                        st.session_state.db = distributed_fields
                        save_data(st.session_state.db)
                        st.success("تم استخراج البيانات من الملف بنجاح!")
                        st.rerun()
            
            st.markdown("---")
            
            edit_info = st.text_area("📋 معلومات عامة", st.session_state.db.get("info", ""), height=100, key="info_admin")
            edit_schedules = st.text_area("📚 الجداول", st.session_state.db.get("schedules", ""), height=100, key="sched_admin")
            edit_exams = st.text_area("📝 الامتحانات", st.session_state.db.get("exams", ""), height=100, key="exams_admin")
            edit_fees = st.text_area("💰 الرسوم", st.session_state.db.get("fees", ""), height=100, key="fees_admin")
            edit_contacts = st.text_area("📞 جهات الاتصال", st.session_state.db.get("contacts", ""), height=100, key="contacts_admin")
            edit_majors = st.text_area("🎓 التخصصات", st.session_state.db.get("majors", ""), height=100, key="majors_admin")
            
            if st.button("💾 حفظ البيانات", icon=":material/save:", use_container_width=True, key="save_admin"):
                st.session_state.db = {
                    "info": edit_info,
                    "schedules": edit_schedules,
                    "exams": edit_exams,
                    "fees": edit_fees,
                    "contacts": edit_contacts,
                    "majors": edit_majors
                }
                save_data(st.session_state.db)
                st.success("تم تحديث قاعدة البيانات بنجاح!")
        
        with tab2:
            if SERVICES_AVAILABLE:
                try:
                    stats = get_stats()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📊 إجمالي الأسئلة", stats.get("total", 0))
                    with col2:
                        st.metric("📅 أسئلة اليوم", stats.get("today", 0))
                    
                    st.markdown("---")
                    st.markdown("### 🔍 أكثر 5 أسئلة شيوعاً")
                    top_q = stats.get("top_questions", [])
                    if top_q:
                        for i, q in enumerate(top_q[:5], 1):
                            st.markdown(f"**{i}.** {q['question']}  `({q['count']} مرة)`")
                    else:
                        st.info("لا توجد أسئلة مسجلة بعد")
                    
                    st.markdown("---")
                    st.markdown("### 📂 توزيع الفئات")
                    categories_data = stats.get("categories", {})
                    if categories_data:
                        for cat, count in categories_data.items():
                            st.markdown(f"- **{cat}**: {count} سؤال")
                    else:
                        st.info("لا توجد بيانات فئات")
                except Exception as e:
                    st.error(f"خطأ في تحميل الإحصائيات: {str(e)}")
            else:
                st.warning("الإحصائيات غير متاحة لعدم وجود ملف services.py")
                    
    elif admin_password != "":
        st.error("❌ كلمة المرور غير صحيحة")
    
    # زر الخروج من وضع الإدارة
    st.markdown("---")
    if st.button("🔙 خروج من لوحة الإدارة", icon=":material/logout:", key="logout_admin"):
        st.session_state.admin_mode = False
        st.rerun()

# ==========================================
# 10. حقل الإدخال (للطلاب فقط)
# ==========================================
if not st.session_state.admin_mode:
    user_input = st.chat_input("تفضل بطرح استفسارك هنا...")

    if st.session_state.auto_question:
        user_input = st.session_state.auto_question
        st.session_state.auto_question = None

    if user_input:
        # ===== 🎯 الكود السري الجديد =====
        if user_input.strip() == "ادارة جامعة القران الكريم وعلومه":
            st.session_state.admin_mode = True
            st.rerun()
        
        # ===== دردشة عادية =====
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(user_input)
        
        with st.chat_message("assistant", avatar=":material/school:"):
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
