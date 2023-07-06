echo Install OTAnalytics.
@echo off
FOR /F "tokens=* USEBACKQ" %%F IN (`python --version`) DO SET PYTHON_VERSION=%%F

echo %PYTHON_VERSION%
if "x%PYTHON_VERSION:3.10=%"=="x%PYTHON_VERSION%" (
    echo "Python Version 3.10 is not installed in environment." & cmd /K & exit
)

call venv\Scripts\activate
python -m OTAnalytics
deactivate
