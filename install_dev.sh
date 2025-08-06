#!/bin/bash
set -e
echo "Install OTAnalytics development environment."

WORKING_DIR=$(pwd)
VENV="$WORKING_DIR"/.venv
PRE_COMMIT="$VENV"/bin/pre-commit
UV="$VENV"/bin/uv

bash "$WORKING_DIR"/install.sh

$UV pip install -e .[dev] --python .venv
$PRE_COMMIT install --install-hooks
