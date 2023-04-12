#!/bin/bash
echo "Start OTAnalytics."

WORKING_DIR=$(pwd)

source "$WORKING_DIR"/venv/bin/activate
python3.10 -m OTAnalytics
deactivate
