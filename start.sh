#!/usr/bin/env bash
set -e

echo "==============================================================="
echo "Starting OpenLMS (Python Flask)"
echo "==============================================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+"
    exit 1
fi

python3 run.py
