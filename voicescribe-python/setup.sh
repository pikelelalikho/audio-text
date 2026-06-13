#!/usr/bin/env bash
set -e

echo ""
echo " ============================================"
echo "  VoiceScribe — Setup"
echo " ============================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo " [ERROR] python3 not found."
    echo " Install via: sudo apt install python3 python3-venv  (Ubuntu/Debian)"
    echo "          or: brew install python  (macOS)"
    exit 1
fi

echo " [1/4] Creating virtual environment..."
python3 -m venv venv

echo " [2/4] Activating virtual environment..."
source venv/bin/activate

echo " [3/4] Installing dependencies (may take a few minutes)..."
pip install --upgrade pip -q
pip install -r requirements.txt

echo " [4/4] Done!"
echo ""
echo " ============================================"
echo "  Setup complete. Run  ./start.sh  to launch."
echo " ============================================"
echo ""
