import streamlit as st
import json
import os
from datetime import datetime
from services import ask_ai, smart_classify  # تم استبدال الدوال الوهمية بالاستيراد الحقيقي

# ======== إعدادات جامعة القرآن الكريم (تم التحديث) ========
APP_TITLE = "جامعة القرآن الكريم والعلوم الإسلامية"
APP_SUBTITLE = "فرع غيل باوزير - حضرموت"
APP_ICON = "🕌"
THEME = {'primary': '#d4af37', 'text_muted': '#8892b0'}

# ======== إعداد الصفحة ========
st.set_page_config(
    page_title=f"{APP_TITLE} - {APP_SUBTITLE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======== CSS الفاخر جداً (Luxury Design) ========
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=El+Messiri:wght@300;400;600;700&display=swap');
    
    * {{ font-family: 'El Messiri', sans-serif; }}

    /* تخصيص شريط التمرير (Scrollbar) ليناسب الفخامة */
    ::-webkit-scrollbar {{ width: 8px; background: #050b14; }}
    ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #d4af37, #8a6d1c); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #fcf6ba; }}

    /* خلفية التطبيق: تدرج داكن وعميق يعطي إحساساً بالفضاء أو الفخامة الملكية */
    .stApp {{
        background: linear-gradient(135deg, #02060d 0%, #0a1324 40%, #060e1a 100%) !important;
        background-attachment: fixed !important;
    }}

    /* إخفاء الشريط العلوي الافتراضي مع ترك زر القائمة المنسدلة */
    header[data-testid="stHeader"] {{ background-color: transparent !important; }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    /* تأثير النص الذهبي الفاخر (Gold Foil) */
    .gold-foil-text {{
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 20px rgba(212,175,55,0.2);
    }}

    /* العناوين والبسملة */
    .basmala {{
        text-align: center; font-family: 'Amiri', serif; font-size: 2.4em;
        font-weight: 700; margin-bottom: 5px; margin-top: -30px;
    }}
    .main-title {{
        text-align: center; font-size: 3.2em; font-weight: 700; color: #ffffff;
        letter-spacing: 2px; margin-bottom: 5px;
    }}
    .sub-title {{
        text-align: center; font-size: 1.3em; color: #a8b2c1;
        letter-spacing: 5px; margin-bottom: 40px; font-weight: 300;
    }}

    /* فاصل ذهبي متدرج */
    .gold-divider {{
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(212,175,55,0) 0%, rgba(212,175,55,0.8) 50%, rgba(212,175,55,0) 100%);
        margin: 30px 0;
        box-shadow: 0 0 10px rgba(212,175,55,0.4);
    }}

    /* أزرار الخدمات (الكروت الزجاجية) */
    div[data-testid="column"] div.stButton > button {{
        background: linear-gradient(145deg, rgba(20, 30, 50, 0.6), rgba(10, 15, 30, 0.8)) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(212,175,55,0.15) !important;
        border-radius: 25px !important;
        height: 140px !important;
        width: 100% !important;
        color: #e2e8f0 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 2px 10px rgba(255,255,255,0.05);
    }}
    div[data-testid="column"] div.stButton > button:hover {{
        transform: translateY(-10px) scale(1.02) !important;
        border-color: #d4af37 !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.7), 0 0 20px rgba(212,175,55,0.3) !important;
        color: #fcf6ba !important;
    }}
    div[data-testid="column"] div.stButton > button p {{
        font-size: 1.2em !important;
        font-weight: 600;
        margin: 0;
        line-height: 1.6;
    }}

    /* رسائل المحادثة (تصميم زجاجي أنيق) */
    [data-testid="stChatMessage"] {{
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 20px 25px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    /* رسالة المستخدم */
    [data-testid="stChatMessage"]:nth-child(even) {{
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(0,0,0,0)) !important;
        border-right: 3px solid #d4af37 !important;
        border-left: none !important;
    }}
    
    /* رسالة الذكاء الاصطناعي */
    [data-testid="stChatMessage"]:nth-child(odd) {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)) !important;
        border-left: 3px solid #60a5fa !important;
    }}

    /* حقل الكتابة (طافي ومضيء) */
    [data-testid="stChatInput"] {{
        background: transparent !important;
        padding-bottom: 30px !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background: rgba(10, 15, 30, 0.85) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        border-radius: 30px !important;
        color: #ffffff !important;
        padding: 18px 30px !important;
        font-size: 1.15em !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.3s ease !important;
    }}
    [data-testid="stChatInput"] textarea:focus {{
        border-color: #d4af37 !important;
        box-shadow: 0 0 25px rgba(212,175,55,0.3), inset 0 0 10px rgba(212,175,55,0.1) !important;
        outline: none !important;
    }}

    /* تخصيص أيقونات الإرسال في حقل الكتابة */
    [data-testid="stChatInputSubmitButton"] {{
        color: #d4af37 !important;
        background: rgba(212,175,55,0.1) !important;
        border-radius: 50% !important;
        transition: all 0.3s ease !important;
    }}
    [data-testid="stChatInputSubmitButton"]:hover {{
        background: #d4af37 !important;
        color: #000 !important;
        transform: scale(1.1);
    }}

    /* شريط الإدارة الجانبي */
    section[data-testid="stSidebar"] {{
        background: rgba(5, 10, 20, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-left: 1px solid rgba(212,175,55,0.15) !important;
    }}
    .stTextInput > div > div > input, .stTextArea > div > textarea {{
        background: rgba(15, 23, 42, 0.6) !important;
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }}
    .stTextInput > div > div > input:focus, .stTextArea > div > textarea:focus {{
