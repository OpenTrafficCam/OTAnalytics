echo Install OTAnalytics development environment.
call install.cmd
call .venv\Scripts\activate
uv pip install -e --python .venv
uv sync --dev
pre-commit install --install-hooks
deactivate
