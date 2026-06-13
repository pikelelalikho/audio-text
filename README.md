# VoiceScribe

VoiceScribe is a local audio-to-text web application. It records or accepts an
audio file, transcribes speech with a Whisper model running on the same machine,
and returns plain text, paragraphs, timestamps, SRT subtitles, or VTT subtitles.

No API key is required. Audio remains local during transcription. An internet
connection is only needed to install dependencies and download a Whisper model
the first time it is used.

## Features

- Record from a browser microphone or upload an audio file
- Automatically detect the spoken language or select one manually
- Transcribe speech or translate it into English
- Export plain text, paragraphs, timestamps, SRT, or VTT
- Automatically use a supported NVIDIA GPU when available
- Run privately on `127.0.0.1` by default

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Application language and runtime |
| Gradio | Builds the browser interface and local HTTP server |
| faster-whisper | Runs Whisper speech recognition efficiently |
| CTranslate2 | Inference engine used by faster-whisper; detects and uses CUDA when available |
| Whisper models | Convert spoken audio into text or translated English |
| `venv` and pip | Isolate and install Python dependencies |
| `unittest` | Tests timestamp formatting and transcript file generation |
| Bash and batch scripts | Provide setup and startup commands for Linux, macOS, and Windows |

PyTorch is intentionally not required. `faster-whisper` uses CTranslate2
directly, which keeps the installation smaller and provides efficient CPU and
GPU inference.

## How It Is Built

The application is a small single-process Gradio service:

1. The browser sends recorded or uploaded audio to the local Gradio server.
2. `app.py` validates the selected audio source and transcription settings.
3. CTranslate2 detects whether a supported CUDA device is available.
4. `faster-whisper` loads the selected Whisper model.
5. The model transcribes or translates the audio.
6. VoiceScribe formats the generated segments into the selected output format.
7. Gradio displays the result and can generate a downloadable transcript file.

Only one transcription job runs at a time. VoiceScribe keeps one model in
memory and replaces it when a different model size is selected. This prevents
multiple large models from exhausting system memory.

## Project Structure

```text
audio-voice/
├── README.md                       # Project overview and architecture
├── GIT_COMMANDS.md                 # Git and GitHub command guide
├── .gitignore                      # Files Git must not track
└── voicescribe-python/
    ├── app.py                      # Transcription logic and Gradio UI
    ├── requirements.txt            # Runtime dependencies
    ├── test_app.py                 # Automated tests
    ├── setup.sh / setup.bat        # Create the environment and install packages
    ├── start.sh / start.bat        # Start the application
    └── README.md                   # Detailed operating instructions
```

## Quick Start

### Linux or macOS

```bash
cd voicescribe-python
./setup.sh
./start.sh
```

### Windows

Open `voicescribe-python`, then run:

```bat
setup.bat
start.bat
```

Open `http://127.0.0.1:7860` if the browser does not open automatically.

## Testing

```bash
cd voicescribe-python
venv/bin/python -m unittest -v test_app.py
venv/bin/python -m pip check
```

On Windows, replace `venv/bin/python` with `venv\Scripts\python`.

## Runtime Configuration

| Variable | Default | Purpose |
|---|---|---|
| `VOICESCRIBE_HOST` | `127.0.0.1` | Address on which the server listens |
| `VOICESCRIBE_PORT` | `7860` | HTTP server port |
| `VOICESCRIBE_INBROWSER` | `true` | Open the browser when the app starts |
| `VOICESCRIBE_SHARE` | `false` | Create a public Gradio share link |
| `VOICESCRIBE_SHOW_ERROR` | `false` | Show detailed server errors in the UI |
| `VOICESCRIBE_LOG_LEVEL` | `INFO` | Application logging level |

Example headless launch:

```bash
cd voicescribe-python
VOICESCRIBE_INBROWSER=false VOICESCRIBE_PORT=8080 ./start.sh
```

Do not expose the app directly to the public internet without authentication,
HTTPS, request limits, and a managed reverse proxy.

## Privacy

Gradio analytics are disabled and the interface does not load external fonts.
Audio transcription runs locally. Enabling `VOICESCRIBE_SHARE=true` creates a
public Gradio link and changes that privacy boundary.

See [voicescribe-python/README.md](voicescribe-python/README.md) for model
sizes, setup details, and troubleshooting.
