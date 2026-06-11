@echo off
title بوت جامعة القرآن - فرع غيل باوزير
cd /d "%~dp0"
echo جاري تثبيت المتطلبات...
pip install -r requirements.txt
echo.
echo جاري تشغيل البوت...
python bot.py
pause
