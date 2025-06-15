@echo off
set PYTHONPATH=%~dp0
cd /d %~dp0
streamlit run app.py
pause
