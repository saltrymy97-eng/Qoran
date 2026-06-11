@echo off
title بوت واتساب - جامعة القرآن
cd /d "%~dp0"
pip install groq flask requests qrcode Pillow
python bot.py
pause
