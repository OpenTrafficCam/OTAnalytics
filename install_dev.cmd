echo Install OTAnalytics development environment.
call install.cmd
call .venv\Scripts\activate
uv sync --dev --python .venv
uv run playwright install
pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push
deactivate
