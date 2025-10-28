#!/bin/bash
set -e
echo "Install OTAnalytics development environment."

WORKING_DIR=$(pwd)

bash "$WORKING_DIR"/install.sh

uv lock --upgrade
uv sync --dev
uv run pre-commit install --install-hooks
