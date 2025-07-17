echo Install OTAnalytics development environment.
call install.cmd
call .venv\Scripts\activate
uv pip install -r requirements-dev.txt --python .venv%
uv pip install -e .
pre-commit install --install-hooks
deactivate
