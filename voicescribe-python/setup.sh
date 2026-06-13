#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo ""
echo " ============================================"
echo "  VoiceScribe — Setup"
echo " ============================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo " [ERROR] python3 not found."
    echo " Install via: sudo apt install python3 python3-venv  (Ubuntu/Debian)"
    echo "          or: brew install python  (macOS)"
    exit 1
fi

if ! python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
    echo " [ERROR] Python 3.10 or newer is required."
    exit 1
fi

echo " [1/4] Creating virtual environment..."
python3 -m venv --clear venv

echo " [2/4] Activating virtual environment..."
source venv/bin/activate

echo " [3/4] Installing dependencies (may take a few minutes)..."
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt

echo " [4/4] Done!"
echo ""
echo " ============================================"
echo "  Setup complete. Run  ./start.sh  to launch."
echo " ============================================"
echo ""
