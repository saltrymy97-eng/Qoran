import streamlit as st
import json
import os
import re
import base64
import requests
import datetime

# --- استيراد المكتبات الإضافية ---
try:
    from docx import Document
except ImportError:
    Document = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from services import (
        ask_ai, smart_classify, get_stats, load_data, save_data,
        generate_training_data, get_memory_stats
    )
except ImportError:
    ask_ai = smart_classify = get_stats = load_data = save_data = None
    generate_training_data = get_memory_stats = None

# ==========================================
# 1. التكوين الأساسي للصفحة
# ==========================================
st.set_page_config(
    page_title="جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- تحميل الأسرار ---
ADMIN_SECRET_CODE = st.secrets.get("ADMIN_SECRET_CODE", "ادارة جامعة القران الكريم وعلومه")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
GITHUB_REPO = st.secrets.get("GITHUB_REPO")

# ==========================================
# 2. التصميم الرسمي (CSS)
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
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" opacity="0.03"><path d="M50 10 L90 90 L10 90 Z" fill="%230f5132"/></svg>');
    background-size: 200px 200px;
    color: #2b3a30 !important;
    font-family: 'Tajawal', sans-serif !important;
}

.basmala {
    font-family: 'Amiri', serif !important;
    font-size: 3.5rem !important;
    text-align: center;
    color: #0f5132 !important;
    margin-top: 5px;
    margin-bottom: 15px;
    font-weight: 700;
    line-height: 1.6;
}

.uni-title {
    font-family: 'Tajawal', sans-serif !important;
    font-size: 2.4rem !important;
    text-align: center;
    font-weight: 800;
    color: #0f5132 !important;
    margin-top: 0px;
    margin-bottom: 5px;
    line-height: 1.3;
}

.branch-title {
    font-family: 'Tajawal', sans-serif !important;
    font-size: 1.1rem !important;
    text-align: center;
    color: #6c757d !important;
    letter-spacing: 2px;
    margin-bottom: 25px;
    font-weight: 500;
}

.quran-verse {
    font-family: 'Amiri', serif !important;
    font-size: 1.5rem !important;
    text-align: center;
    color: #bfa15f !important;
    margin: 20px 0 15px 0;
    font-weight: 600;
    border-top: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    padding: 14px 0;
    direction: rtl;
    unicode-bidi: embed;
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
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}
div.stButton > button:hover, div.stButton > button:active {
    background-color: #0f5132 !important;
    color: #ffffff !important;
    border-color: #0f5132 !important;
    transform: translateY(-1px);
}

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #edf2f7 !important;
    border-right: 4px solid #0f5132 !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    margin-bottom: 1.2rem !important;
    color: #2d3748 !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.7 !important;
    animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 20px !important;
    padding: 8px 16px !important;
}
[data-testid="stChatInput"] textarea {
    color: #1e293b !important;
    font-family: 'Tajawal', sans-serif !important;
}

.official-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    text-align: center;
    padding: 8px;
    font-family: 'Tajawal', sans-serif;
    font-size: 0.8rem;
    color: #6c757d;
    background: rgba(251, 252, 251, 0.9);
    border-top: 1px solid #e2e8f0;
    z-index: 999;
}

footer {visibility: hidden !important;}
.stDeployButton {display: none !important;}
[data-testid="stMainMenu"] {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stHeader"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. الدوال المساعدة
# ==========================================
def clean_arabic_text(text):
    if not text:
        return ""
    tashkeel = re.compile(r'[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED]')
    text = tashkeel.sub('', text)
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ة', 'ه')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def extract_text_from_file(uploaded_file):
    if not uploaded_file:
        return None
    file_type = uploaded_file.type
    text_parts = []
    
    if "wordprocessingml" in file_type or uploaded_file.name.endswith('.docx'):
        if Document is None:
            st.error("مكتبة python-docx غير مثبتة.")
            return None
        doc = Document(uploaded_file)
        text_parts = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        
    elif "pdf" in file_type or uploaded_file.name.endswith('.pdf'):
        if PdfReader is None:
            st.error("مكتبة PyPDF2 غير مثبتة.")
            return None
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    else:
        st.error("نوع الملف غير مدعوم. الرجاء رفع ملف Word (.docx) أو PDF.")
        return None
        
    return clean_arabic_text('\n'.join(text_parts))

def smart_distribute_text(text):
    fields = {"info": "", "schedules": "", "exams": "", "fees": "", "contacts": "", "majors": ""}
    if not text:
        return fields
        
    patterns = {
        "info": ["معلومات عامة", "معلومات اساسية", "عن الجامعة", "نبذة", "تعريف", "المعلومات العامة"],
        "schedules": ["الجداول", "جداول المحاضرات", "الجداول الدراسية", "جدول", "المحاضرات", "المواعيد"],
        "exams": ["الامتحانات", "الاختبارات", "مواعيد الامتحانات", "نظام الامتحانات", "التقويم"],
        "fees": ["الرسوم", "الرسوم الدراسية", "المصاريف", "التكاليف", "الدفع", "السداد", "الاقساط"],
        "contacts": ["جهات الاتصال", "التواصل", "اتصل بنا", "الهاتف", "العنوان", "الموقع", "البريد"],
        "majors": ["التخصصات", "التخصص", "الاقسام", "الشعب", "البرامج", "المسارات"]
    }
    
    current_field = "info"
    sections = {field: [] for field in fields}
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        matched = False
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                if line.startswith(pattern):
                    current_field = field
                    content = line[len(pattern):].strip().lstrip(':').strip()
                    if content:
                        sections[field].append(content)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            sections[current_field].append(line)
            
    return {field: '\n'.join(content) for field, content in sections.items()}

def save_data_to_github(data_json, token, repo):
    """حفظ ملف data.json مباشرة إلى مستودع GitHub"""
    if not token or not repo:
        return False
    
    url = f"https://api.github.com/repos/{repo}/contents/data.json"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # محاولة الحصول على الملف الحالي
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get("sha")
    
    # تحضير المحتوى
    content = json.dumps(data_json, ensure_ascii=False, indent=4)
    data = {
        "message": "تحديث بيانات الجامعة",
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

# ==========================================
# 4. تهيئة الحالات
# ==========================================
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "db" not in st.session_state:
    st.session_state.db = load_data() if load_data else {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "auto_question" not in st.session_state:
    st.session_state.auto_question = None

# ==========================================
# 5. عرض الواجهة
# ==========================================
st.markdown('<div class="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="uni-title">جامعة القرآن الكريم<br>والعلوم الإسلامية</div>', unsafe_allow_html=True)
st.markdown('<div class="branch-title">✦ فرع غيل باوزير - حضرموت ✦</div>', unsafe_allow_html=True)

# --- وضع الطالب ---
if not st.session_state.admin_mode:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("الجداول", icon=":material/calendar_month:"):
            st.session_state.auto_question = "أريد الاستفسار عن جداول المحاضرات"
            st.rerun()
    with col2:
        if st.button("الامتحانات", icon=":material/edit_document:"):
            st.session_state.auto_question = "ما هي مواعيد وترتيبات الامتحانات؟"
            st.rerun()
    with col3:
        if st.button("التواصل", icon=":material/call:"):
            st.session_state.auto_question = "كيف يمكنني التواصل مع إدارة الفرع؟"
            st.rerun()
    with col4:
        if st.button("التخصصات", icon=":material/school:"):
            st.session_state.auto_question = "ما هي التخصصات الأكاديمية المتاحة ورسومها؟"
            st.rerun()

    st.markdown('<div class="quran-verse">﴿وَقُل رَّبِّ زِدْنِي عِلْمًا﴾</div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        welcome_msg = "مرحباً بك في المساعد الذكي لجامعة القرآن الكريم - فرع غيل باوزير. تفضل بطرح استفسارك أو اختر من الخدمات المتاحة أعلاه."
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    for msg in st.session_state.messages:
        avatar = ":material/school:" if msg["role"] == "assistant" else ":material/person:"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- وضع الإدارة ---
else:
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h2 style="color: #0f5132; font-family: 'Tajawal', sans-serif; font-weight: 800; font-size: 2rem;">🔐 لوحة الإدارة</h2>
        <p style="color: #6c757d; font-family: 'Tajawal', sans-serif;">جامعة القرآن الكريم والعلوم الإسلامية - فرع غيل باوزير</p>
    </div>
    """, unsafe_allow_html=True)

    admin_password = st.text_input("🔑 كلمة مرور المشرف", type="password", key="admin_pwd")
    
    if admin_password == ADMIN_PASSWORD:
        st.success("✅ تم التحقق بنجاح")
        tab1, tab2, tab3 = st.tabs(["📝 تحرير البيانات", "📊 الإحصائيات", "🧠 الذاكرة"])
        
        with tab1:
            uploaded_file = st.file_uploader("📂 رفع ملف Word أو PDF لتحديث البيانات", type=["docx", "pdf"])
            
            col1, col2 = st.columns(2)
            with col1:
                if uploaded_file and st.button("🚀 معالجة الملف", use_container_width=True):
                    extracted_text = extract_text_from_file(uploaded_file)
                    if extracted_text:
                        st.session_state.db = smart_distribute_text(extracted_text)
                        save_data(st.session_state.db)
                        st.success("تم استخراج البيانات وحفظها محلياً بنجاح!")
                        st.rerun()
            
            with col2:
                if st.button("☁️ حفظ البيانات إلى GitHub", use_container_width=True):
                    if GITHUB_TOKEN and GITHUB_REPO:
                        if save_data_to_github(st.session_state.db, GITHUB_TOKEN, GITHUB_REPO):
                            st.success("✅ تم تحديث بيانات الجامعة بنجاح في المستودع!")
                        else:
                            st.error("❌ فشل في تحديث المستودع. تأكد من إعدادات GitHub.")
                    else:
                        st.error("❌ معلومات GitHub غير مكتملة في الإعدادات (Secrets).")

            st.markdown("---")
            
            with st.form("data_form"):
                e_info = st.text_area("📋 معلومات عامة", st.session_state.db.get("info", ""), height=100)
                e_sched = st.text_area("📚 الجداول", st.session_state.db.get("schedules", ""), height=100)
                e_exams = st.text_area("📝 الامتحانات", st.session_state.db.get("exams", ""), height=100)
                e_fees = st.text_area("💰 الرسوم", st.session_state.db.get("fees", ""), height=100)
                e_contacts = st.text_area("📞 جهات الاتصال", st.session_state.db.get("contacts", ""), height=100)
                e_majors = st.text_area("🎓 التخصصات", st.session_state.db.get("majors", ""), height=150)
                
                if st.form_submit_button("💾 حفظ التعديلات محلياً", use_container_width=True):
                    st.session_state.db = {
                        "info": e_info, "schedules": e_sched, "exams": e_exams,
                        "fees": e_fees, "contacts": e_contacts, "majors": e_majors
                    }
                    save_data(st.session_state.db)
                    st.success("تم تحديث قاعدة البيانات محلياً بنجاح!")
        
        with tab2:
            if get_stats:
                stats = get_stats()
                col1, col2, col3 = st.columns(3)
                col1.metric("📊 إجمالي الأسئلة", stats.get("total", 0))
                col2.metric("📅 أسئلة اليوم", stats.get("today", 0))
                col3.metric("🧠 أسئلة الذاكرة", stats.get("memory_size", 0))
                
                st.markdown("---")
                st.subheader("🔍 أكثر الأسئلة شيوعاً")
                top_q = stats.get("top_questions", [])
                for i, q in enumerate(top_q[:5], 1):
                    st.markdown(f"**{i}.** {q['question']}  `({q['count']} مرة)`")
                if not top_q:
                    st.info("لا توجد أسئلة مسجلة بعد")
            else:
                st.info("الإحصائيات ستظهر بعد أول سؤال من الطلاب.")
        
        with tab3:
            st.subheader("🧠 إدارة ذاكرة المساعد الذكي")
            
            if os.path.exists("training_data.json"):
                try:
                    with open("training_data.json", "r", encoding="utf-8") as f:
                        memory = json.load(f)
                    st.metric("🧠 حجم الذاكرة الحالي", f"{len(memory)} سؤال")
                except:
                    st.warning("تعذر قراءة ملف الذاكرة.")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🚀 توليد الأسئلة الأساسية", use_container_width=True):
                    if generate_training_data:
                        with st.spinner("🧠 جاري بناء الذاكرة..."):
                            generate_training_data(num_questions=50000)
                            st.success("تم بناء الذاكرة بنجاح!")
                            st.rerun()
                    else:
                        st.info("ميزة التوليد غير متاحة حالياً.")
            
            with col_btn2:
                if st.button("🗑️ مسح الذاكرة", use_container_width=True):
                    if os.path.exists("training_data.json"):
                        os.remove("training_data.json")
                        st.success("تم مسح الذاكرة بنجاح.")
                        st.rerun()
                    else:
                        st.info("الذاكرة فارغة بالفعل.")

    elif admin_password != "":
        st.error("❌ كلمة المرور غير صحيحة")
    
    st.markdown("---")
    if st.button("🔙 خروج من لوحة الإدارة والعودة للمساعد الذكي", use_container_width=True):
        st.session_state.admin_mode = False
        st.rerun()

# ==========================================
# 6. حقل الدردشة الدائم
# ==========================================
user_input = st.chat_input("تفضل بطرح استفسارك هنا...")

if st.session_state.auto_question:
    user_input = st.session_state.auto_question
    st.session_state.auto_question = None

if user_input:
    if user_input.strip() == ADMIN_SECRET_CODE:
        st.session_state.admin_mode = True
        st.rerun()

    elif not st.session_state.admin_mode:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(user_input)
            
        with st.chat_message("assistant", avatar=":material/school:"):
            with st.spinner("جارٍ معالجة استفسارك..."):
                if ask_ai and smart_classify:
                    category = smart_classify(user_input)
                    ai_response = ask_ai(user_input, category)
                else:
                    ai_response = "⚠️ نظام المساعدة غير متصل حالياً."
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

    else:
        st.warning("أنت في لوحة الإدارة. استخدم الخيارات أعلاه أو اضغط خروج.")

st.markdown('<div class="official-footer">المطور: سالم التريمي</div>', unsafe_allow_html=True)
