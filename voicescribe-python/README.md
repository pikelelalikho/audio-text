# VoiceScribe 🎙
### Local Audio-to-Text — No API key, no cloud, fully private

Powered by OpenAI's Whisper model running **entirely on your machine**.

---

## Requirements

- **Python 3.9 or newer** — https://www.python.org/downloads/
  - ⚠️ Windows: tick **"Add Python to PATH"** during install
- ~2 GB free disk space (for the model download on first run)
- Internet connection on first run (to download the model — stored locally after that)

---

## Setup & Launch

### Windows

```
1. Double-click  setup.bat   ← installs everything into a venv
2. Double-click  start.bat   ← launches the app
3. Browser opens at  http://localhost:7860
```

### macOS / Linux

```bash
chmod +x setup.sh start.sh
./setup.sh        # installs everything into a venv
./start.sh        # launches the app
# Browser opens at http://localhost:7860
```

### Manual (any OS)

```bash
python3 -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

---

## First Run

The **first time** you transcribe, Whisper will download the model weights (~150 MB for `base`).  
This happens once and is cached. All subsequent runs are instant.

---

## Model Sizes

| Model    | Size   | Speed   | Accuracy |
|----------|--------|---------|----------|
| tiny     | 75 MB  | Fastest | Good     |
| **base** | 150 MB | Fast    | Better ← default |
| small    | 460 MB | Medium  | Great    |
| medium   | 1.5 GB | Slow    | Excellent|
| large-v3 | 3 GB   | Slowest | Best     |

Start with `base`. Switch to `small` or `medium` for better accuracy on tricky audio.

---

## Features

- 🎙 Record directly from microphone or upload a file
- 📁 Supports mp3, mp4, m4a, wav, ogg, flac, webm
- 🌍 Auto language detection or manual selection (18+ languages)
- 🔄 Translate any language → English
- 📝 Output: plain text, paragraphs, timestamped, SRT, VTT
- ⬇️ Download transcript as a file
- 🔒 100% local — your audio never leaves your computer

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Install Python 3.9+ and tick "Add to PATH" |
| Slow first transcription | Model is downloading — wait once, instant after |
| Mic not working | Allow microphone in browser popup |
| `torch` install fails | Run: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| CUDA errors | Add `device="cpu"` in `app.py` line with `get_model()` |
