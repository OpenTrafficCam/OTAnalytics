echo Install OTAnalytics development environment.
call install.cmd
call venv\Scripts\activate
pip install -r requirements-tools.txt --no-cache-dir%
pip install -e .
pre-commit install --install-hooks
deactivate
