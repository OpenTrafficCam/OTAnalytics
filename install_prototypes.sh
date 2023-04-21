#!/bin/bash
set -e
echo "Install OTAnalytics prototype dependencies."

WORKING_DIR=$(pwd)
VENV="$WORKING_DIR"/venv
PIP="$VENV"/bin/pip

bash "$WORKING_DIR"/install_dev.sh

$PIP install -r requirements-prototypes.txt --no-cache-dir
