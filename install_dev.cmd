echo Install OTAnalytics development environment.
call install.cmd
call .venv\Scripts\activate
uv pip install -e .[dev] --python .venv
pre-commit install --install-hooks
deactivate
