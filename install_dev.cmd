echo Install OTAnalytics development environment.
call install.cmd
call .venv\Scripts\activate
uv sync --dev --python .venv
pre-commit install --install-hooks
deactivate
