"""
إعدادات التطبيق المركزية
"""

# عنوان التطبيق
APP_TITLE = "جامعة القرآن الكريم والعلوم الإسلامية"
APP_SUBTITLE = "فرع غيل باوزير - حضرموت"
APP_ICON = "🕌"

# ألوان الثيم
THEME = {
    "primary": "#d4af37",      # ذهبي
    "secondary": "#1a3a2a",    # أخضر داكن
    "bg_dark": "#0a0f1a",
    "glass": "rgba(255,255,255,0.03)",
    "text_light": "#ffffff",
    "text_muted": "#888888"
}

# إعدادات Groq
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 500
TEMPERATURE = 0.5

# مسارات الملفات
DATA_DIR = "data"
INFO_FILE = f"{DATA_DIR}/info.json"
SCHEDULES_FILE = f"{DATA_DIR}/schedules.json"
FEES_FILE = f"{DATA_DIR}/fees.json"
CONTACTS_FILE = f"{DATA_DIR}/contacts.json"
LOGS_FILE = f"{DATA_DIR}/logs.json"

# صلاحيات الإدارة
ADMIN_PASSWORD = "admin123"  # غيّرها فورًا في الإنتاج
EDITOR_PASSWORD = "editor123"
SESSION_TIMEOUT = 3600  # ثانية
