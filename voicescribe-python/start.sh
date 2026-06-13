#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [[ ! -f venv/bin/activate ]]; then
    echo " [ERROR] Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate
exec python app.py
