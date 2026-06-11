import streamlit as st
import json
import os
from groq import Groq

# ======== إعداد الصفحة ========
st.set_page_config(page_title="جامعة القرآن - غيل باوزير", page_icon="🕌", layout="wide")

# ======== تحميل البيانات ========
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"info": "لم يتم إضافة بيانات بعد."}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======== مفتاح Groq ========
GROQ_API_KEY = "gsk_ضع_مفتاحك_هنا"
groq_client = Groq(api_key=GROQ_API_KEY)

# ======== دالة السؤال ========
def ask_ai(question, context):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"أنت مساعد فرع جامعة القرآن - غيل باوزير. أجب من هذه المعلومات: {context}"},
                {"role": "user", "content": question}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except:
        return "عذرًا، حدث خطأ. حاول لاحقًا."

# ======== واجهة الطالب ========
st.title("🕌 جامعة القرآن الكريم والعلوم الإسلامية")
st.subheader("فرع غيل باوزير - حضرموت")
st.markdown("---")

st.markdown("### 💬 اسأل أي سؤال عن الجامعة")
user_question = st.text_input("✍️ اكتب سؤالك هنا:")

if user_question:
    data = load_data()
    with st.spinner("جاري الرد..."):
        reply = ask_ai(user_question, data.get("info", ""))
    st.markdown("---")
    st.success(reply)

# ======== شريط الإدارة ========
with st.sidebar:
    st.header("🔒 لوحة الإدارة")
    admin_pass = st.text_input("كلمة المرور:", type="password")
    
    if admin_pass == "admin123":
        st.success("✅ مرحبًا بك")
        data = load_data()
        new_info = st.text_area("📝 أدخل بيانات الجامعة:", value=data.get("info", ""), height=300)
        if st.button("💾 حفظ"):
            data["info"] = new_info
            save_data(data)
            st.success("تم الحفظ!")
            st.rerun()
    elif admin_pass:
        st.error("❌ كلمة مرور خاطئة")
