import streamlit as st
import json
import os
import re
import datetime
import threading
import time
import requests

# --- استيراد خدمات الذكاء الاصطناعي ---
try:
    from services import (
        ask_ai, smart_classify, get_stats, load_data, save_data
    )
except ImportError:
    ask_ai = smart_classify = get_stats = load_data = save_data = None

# ==========================================
# 0. الحل النهائي: منع النوم + الحفظ التلقائي (في الخلفية)
# ==========================================
APP_URL = "https://ldqdgjrfdhzsmbgj3p22gn.streamlit.app/"

def background_worker():
    while True:
        # 1. منع السيرفر من النوم (إرسال نبضة كل 5 دقائق)
        try:
            requests.get(APP_URL)
            print("👋 [Keep-Alive] تم إرسال نبضة لإبقاء السيرفر حياً.")
        except:
            pass
        
        # 2. حفظ البيانات تلقائياً كل ساعة
        try:
            data = load_data()
            save_data(data)
            print("✅ [Auto-Save] تم حفظ البيانات تلقائياً في الخلفية.")
        except Exception as e:
            print(f"⚠️ [Auto-Save] فشل الحفظ التلقائي: {e}")
            
        # الانتظار لمدة ساعة قبل تكرار العملية
        time.sleep(3600)

# تشغيل الخلفية (Daemon Thread) بمجرد بدء التطبيق
thread = threading.Thread(target=background_worker, daemon=True)
thread.start()

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
    text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    line-height: 1.6;
    letter-spacing: 1px;
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
    text-shadow: 1px 1px 3px rgba(0,0,0,0.03);
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

hr {
    border: 0 !important;
    height: 1px !important;
    background: linear-gradient(to right, transparent, #bfa15f, transparent) !important;
    margin: 25px 0 !important;
    opacity: 0.4;
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
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}
div.stButton > button:hover, div.stButton > button:active {
    background-color: #0f5132 !important;
    color: #ffffff !important;
    border-color: #0f5132 !important;
    box-shadow: 0 4px 12px rgba(15,81,50,0.15) !important;
    transform: translateY(-1px);
}

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #edf2f7 !important;
    border-right: 4px solid #0f5132 !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    margin-bottom: 1.2rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
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
    box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    padding: 8px 16px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #0f5132 !important;
    box-shadow: 0 10px 25px rgba(15,81,50,0.08) !important;
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

@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        padding-bottom: 15px !important;
    }
    [data-testid="column"] {
        min-width: 140px !important;
        flex: 0 0 auto !important;
    }
    .basmala {
        font-size: 2.4rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. تهيئة الحالات
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
# 4. عرض الواجهة
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
    </div>
    """, unsafe_allow_html=True)

    admin_password = st.text_input("🔑 كلمة مرور المشرف", type="password", key="admin_pwd")
    
    if admin_password == ADMIN_PASSWORD:
        st.success("✅ تم التحقق بنجاح")
        
        tab1, tab2 = st.tabs(["📝 تحرير البيانات", "📊 الإحصائيات"])
        
        with tab1:
            st.markdown("### 📝 تحرير البيانات مباشرة")
            st.info("يمكنك تعديل جميع بيانات الجامعة من خلال الحقول أدناه. استخدم القالب الموحد للتخصصات.")
            
            with st.form("data_form"):
                e_info = st.text_area("معلومات عامة", st.session_state.db.get("info", ""), height=100)
                e_sched = st.text_area("الجداول الدراسية", st.session_state.db.get("schedules", ""), height=100)
                e_exams = st.text_area("الامتحانات", st.session_state.db.get("exams", ""), height=100)
                e_fees = st.text_area("الرسوم الدراسية", st.session_state.db.get("fees", ""), height=100)
                e_contacts = st.text_area("جهات الاتصال", st.session_state.db.get("contacts", ""), height=100)
                e_majors = st.text_area("التخصصات (بالقالب الموحد)", st.session_state.db.get("majors", ""), height=200)
                
                if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
                    st.session_state.db = {
                        "info": e_info, "schedules": e_sched, "exams": e_exams,
                        "fees": e_fees, "contacts": e_contacts, "majors": e_majors
                    }
                    save_data(st.session_state.db)
                    st.success("تم تحديث قاعدة البيانات بنجاح!")
            
            st.markdown("---")
            st.markdown("### 📋 القالب الموحد (انسخه واملأه)")
            st.code("""
[INFO]
معلومات عامة:
(اكتب هنا معلومات عن الجامعة، الرؤية، الرسالة، الأهداف)

[SCHEDULES]
الجداول الدراسية:
(اكتب هنا مواعيد المحاضرات، أيام الدراسة، نظام الحضور)

[EXAMS]
الامتحانات:
(اكتب هنا مواعيد الامتحانات، نظام التقييم، المعدلات)

[FEES]
الرسوم الدراسية:
(اكتب هنا رسوم التخصصات، طرق الدفع، التقسيط، المنح)

[CONTACTS]
جهات الاتصال:
(اكتب هنا أرقام الهواتف، العنوان، الإيميل، ساعات العمل)

[MAJORS]
التخصصات:
تخصص: [اسم التخصص]
الوصف: [وصف التخصص]
الرسوم: [المبلغ]
المدة: [عدد السنوات]
فرص العمل: [فرص العمل]
---
تخصص: [اسم التخصص الثاني]
الوصف: ...
---
""", language="text")
        
        with tab2:
            if get_stats:
                stats = get_stats()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 إجمالي الأسئلة", stats.get("total", 0))
                with col2:
                    st.metric("📅 أسئلة اليوم", stats.get("today", 0))
                with col3:
                    st.metric("📂 عدد الفئات", len(stats.get("categories", {})))
                with col4:
                    top_q = stats.get("top_questions", [])
                    top_count = top_q[0]["count"] if top_q else 0
                    st.metric("🔥 أعلى تكرار", top_count)
                
                st.markdown("---")
                
                st.subheader("🔍 أكثر الأسئلة شيوعاً")
                top_q = stats.get("top_questions", [])
                if top_q:
                    q_labels = [q["question"][:40] + "..." if len(q["question"]) > 40 else q["question"] for q in top_q[:8]]
                    q_counts = [q["count"] for q in top_q[:8]]
                    
                    chart_data = {"السؤال": q_labels, "عدد المرات": q_counts}
                    st.bar_chart(chart_data, x="السؤال", y="عدد المرات", use_container_width=True)
                    
                    with st.expander("📋 عرض القائمة التفصيلية"):
                        for i, q in enumerate(top_q[:15], 1):
                            st.markdown(f"**{i}.** {q['question']}  `({q['count']} مرة)`")
                else:
                    st.info("لا توجد أسئلة مسجلة بعد")
                
                st.markdown("---")
                
                st.subheader("📂 توزيع الفئات")
                cats = stats.get("categories", {})
                if cats:
                    cat_df = {"الفئة": list(cats.keys()), "عدد الأسئلة": list(cats.values())}
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.dataframe(cat_df, use_container_width=True, hide_index=True)
                    with col2:
                        st.bar_chart(cat_df, x="الفئة", y="عدد الأسئلة", use_container_width=True)
                else:
                    st.info("لا توجد بيانات فئات")
            else:
                st.info("الإحصائيات ستظهر بعد أول سؤال من الطلاب.")

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
