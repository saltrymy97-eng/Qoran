import os
import sys
import subprocess
import time
import json

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("جاري تثبيت المتطلبات...")
try:
    install("groq")
    install("flask")
    install("requests")
    install("qrcode")
    install("Pillow")
except:
    pass

from groq import Groq
from flask import Flask, request, jsonify
import threading
import webbrowser

# ======== مفتاح Groq ========
GROQ_API_KEY = "gsk_مفتاحك_هنا"  # ضع مفتاحك الحقيقي

# ======== شخصية البوت ========
SYSTEM_PROMPT = """أنت المساعد الذكي لفرع جامعة القرآن الكريم والعلوم الإسلامية - غيل باوزير، حضرموت، اليمن.

معلومات الفرع:
- المستويات الدراسية: الأول، الثاني، الثالث، الرابع
- التخصصات: القرآن الكريم وعلومه، الشريعة الإسلامية
- الدوام: من السبت إلى الأربعاء (8:00 صباحًا - 2:00 ظهرًا)
- إجازة: الخميس والجمعة
- الرسوم الدراسية للفصل: 50,000 ريال يمني
- طرق السداد: حوالة بنكية أو تسليم مباشر لإدارة الفرع

جداول المحاضرات (جميعها الساعة 8:00 صباحًا):
المستوى الأول: السبت قرآن، الأحد عقيدة، الإثنين فقه، الثلاثاء نحو، الأربعاء حديث
المستوى الثاني: السبت تفسير، الأحد أصول فقه، الإثنين بلاغة، الثلاثاء سيرة، الأربعاء تلاوة
المستوى الثالث: السبت علوم قرآن، الأحد فقه مقارن، الإثنين نحو متقدم، الثلاثاء مصطلح حديث، الأربعاء دعوة
المستوى الرابع: السبت تفسير موضوعي، الأحد قواعد فقهية، الإثنين أدب عربي، الثلاثاء تخريج حديث، الأربعاء فقه معاصر

مواعيد الامتحانات النهائية:
- الأحد 1/7: فقه العبادات - 9:00 صباحًا
- الإثنين 2/7: علوم القرآن - 9:00 صباحًا
- الثلاثاء 3/7: النحو والصرف - 9:00 صباحًا
- الأربعاء 4/7: العقيدة - 9:00 صباحًا
- الخميس 5/7: الحديث - 9:00 صباحًا

للتواصل: شؤون الطلاب 05xxxxxxxx، إدارة الفرع 05xxxxxxxx
العنوان: غيل باوزير - حضرموت

تعليماتك: أجب بالعربية. كن مختصرًا ومفيدًا. استخدم الإيموجي باعتدال. لا تفتح مواضيع خارج نطاق الجامعة."""

# ======== عميل Groq ========
groq_client = Groq(api_key=GROQ_API_KEY)

def ask_llama(question):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"خطأ Groq: {e}")
        return "⚠️ عذرًا، حدث خطأ. يرجى المحاولة لاحقًا أو الاتصال بإدارة الفرع."

# ======== خادم ========
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>بوت جامعة القرآن - فرع غيل باوزير يعمل ✅</h1>
    <p>للتجربة: أرسل POST إلى /chat مع {"message": "سؤالك"}</p>
    """

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    reply = ask_llama(msg)
    return jsonify({'reply': reply})

def run_server():
    app.run(port=5000, debug=False)

# ======== تشغيل ========
if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    print("=" * 50)
    print("✅ البوت شغال!")
    print("=" * 50)
    print("\n📱 لربطه بالواتساب:")
    print("   1. افتح الرابط: http://localhost:5000")
    print("   2. افتح whatsapp_connect.html في المتصفح")
    print("\nاضغط Ctrl+C للإيقاف")
    print("=" * 50)
    webbrowser.open("http://localhost:5000")
    while True:
        time.sleep(1)
