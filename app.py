import streamlit as st
from services import load_data, save_data, ask_ai

# عنوان الصفحة
st.title("🕌 جامعة القرآن الكريم والعلوم الإسلامية")
st.subheader("فرع غيل باوزير - حضرموت")
st.markdown("---")

# واجهة الطالب
st.markdown("### 💬 اسألني عن أي شيء يخص الجامعة")
user_input = st.text_input("", placeholder="✍️ اكتب سؤالك هنا...")

if user_input:
    data = load_data()
    context = f"{data.get('info','')}\n{data.get('schedules','')}\n{data.get('fees','')}\n{data.get('contacts','')}"
    with st.spinner("⏳"):
        reply = ask_ai(user_input, context)
    st.markdown(f"### 🤖 الرد:\n{reply}")

# لوحة الإدارة
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
        
        if st.button("💾 حفظ", use_container_width=True):
            save_data({"info": info, "schedules": schedules, "fees": fees, "contacts": contacts})
            st.success("✅ تم الحفظ!")
            st.rerun()
    elif password:
        st.error("❌ خطأ")
