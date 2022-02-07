cd %~dp0
cd ..
call venv\Scripts\activate
cd OTAnalytics
python main.py
timeout /T 10