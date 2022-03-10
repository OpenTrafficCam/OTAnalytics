cd %~dp0
cd ..
call venv\Scripts\activate
cd OTAnalytics
python __main__.py
timeout /T 10