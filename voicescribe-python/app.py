"""
VoiceScribe — Audio to Text
Uses OpenAI Whisper (local model, no API key needed) via the `faster-whisper` library.
"""

import logging
import os
import tempfile
import threading
import time
from pathlib import Path

# Keep runtime activity local unless the operator explicitly enables sharing.
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import ctranslate2
import gradio as gr
from faster_whisper import WhisperModel

logging.basicConfig(
    level=os.getenv("VOICESCRIBE_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("voicescribe")

# Keep one model resident at a time to avoid exhausting memory when users switch sizes.
_model_lock = threading.Lock()
_model_key: tuple[str, str, str] | None = None
_model: WhisperModel | None = None

def get_model(model_size: str, device: str, compute_type: str) -> WhisperModel:
    global _model_key, _model

    key = (model_size, device, compute_type)
    with _model_lock:
        if key != _model_key or _model is None:
            logger.info("Loading model '%s' on %s (%s)", model_size, device, compute_type)
            _model = WhisperModel(model_size, device=device, compute_type=compute_type)
            _model_key = key
            logger.info("Model ready")
        return _model

# ─── Transcription core ─────────────────────────────────────────────────────
def transcribe(
    audio_path: str,
    model_size: str,
    language: str,
    task: str,
    output_format: str,
    word_timestamps: bool,
    progress=gr.Progress(track_tqdm=True),
) -> tuple[str, str]:
    if not audio_path:
        return "", "⚠️ No audio provided."

    device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    progress(0, desc="Loading model…")
    model = get_model(model_size, device, compute_type)

    lang_arg = None if language == "auto" else language
    progress(0.2, desc="Transcribing…")

    t0 = time.time()
    segments, info = model.transcribe(
        audio_path,
        language=lang_arg,
        task=task,
        word_timestamps=word_timestamps,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    # materialise the generator
    seg_list = list(segments)
    elapsed = time.time() - t0

    detected_lang = info.language
    lang_prob     = info.language_probability
    duration      = info.duration

    progress(0.9, desc="Formatting output…")

    if output_format == "plain":
        text = " ".join(s.text.strip() for s in seg_list)
    elif output_format == "paragraphs":
        lines, buf, last_end = [], [], 0.0
        for s in seg_list:
            if s.start - last_end > 2.0 and buf:
                lines.append(" ".join(buf))
                buf = []
            buf.append(s.text.strip())
            last_end = s.end
        if buf:
            lines.append(" ".join(buf))
        text = "\n\n".join(lines)
    elif output_format == "srt":
        parts = []
        for i, s in enumerate(seg_list, 1):
            parts.append(f"{i}\n{_fmt_time(s.start)} --> {_fmt_time(s.end)}\n{s.text.strip()}\n")
        text = "\n".join(parts)
    elif output_format == "vtt":
        parts = ["WEBVTT\n"]
        for s in seg_list:
            parts.append(f"{_fmt_time(s.start, vtt=True)} --> {_fmt_time(s.end, vtt=True)}\n{s.text.strip()}\n")
        text = "\n".join(parts)
    elif output_format == "timestamped":
        lines = []
        for s in seg_list:
            ts = f"[{_fmt_hms(s.start)} → {_fmt_hms(s.end)}]"
            lines.append(f"{ts}  {s.text.strip()}")
        text = "\n".join(lines)
    else:
        text = " ".join(s.text.strip() for s in seg_list)

    words = len(text.split())
    chars = len(text)
    speed = duration / elapsed if elapsed > 0 else 0

    info_md = (
        f"**Detected language:** {detected_lang.upper()}  ({lang_prob*100:.0f}% confidence)\n\n"
        f"**Audio duration:** {_fmt_hms(duration)}\n\n"
        f"**Processing time:** {elapsed:.1f}s  ({speed:.1f}× real-time)\n\n"
        f"**Words:** {words:,}   **Characters:** {chars:,}\n\n"
        f"**Model:** {model_size}   **Device:** {device.upper()}"
    )

    progress(1.0, desc="Done!")
    return text, info_md


def _fmt_time(secs: float, vtt=False) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = secs % 60
    sep = "." if vtt else ","
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", sep) if not vtt else f"{h:02d}:{m:02d}:{s:06.3f}"


def _fmt_hms(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def save_transcript(text: str, fmt: str) -> str | None:
    if not text.strip():
        return None
    ext = {"plain": "txt", "paragraphs": "txt", "srt": "srt",
           "vtt": "vtt", "timestamped": "txt"}.get(fmt, "txt")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}", mode="w", encoding="utf-8")
    tmp.write(text)
    tmp.close()
    return tmp.name


# ─── Gradio UI ──────────────────────────────────────────────────────────────
def build_ui() -> tuple[gr.Blocks, str]:
    ACCENT  = "#00E5C5"
    BG      = "#0B0D13"
    SURFACE = "#13161F"
    BORDER  = "#1E2233"
    TEXT    = "#DDE2F0"
    MUTED   = "#636B82"

    custom_css = f"""
    :root {{
        --accent:  {ACCENT};
        --bg:      {BG};
        --surface: {SURFACE};
        --border:  {BORDER};
        --text:    {TEXT};
        --muted:   {MUTED};
    }}

    * {{ box-sizing: border-box; }}

    body, .gradio-container {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: system-ui, sans-serif !important;
    }}

    /* header */
    #vs-header {{
        text-align: center;
        padding: 40px 0 24px;
    }}

    #vs-header h1 {{
        font-family: system-ui, sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        letter-spacing: -0.04em;
        color: var(--text);
        line-height: 1;
        margin-bottom: 6px;
    }}

    #vs-header h1 span {{
        color: var(--accent);
    }}

    #vs-header p {{
        font-size: 0.95rem;
        color: var(--muted);
        font-weight: 300;
    }}

    /* panels */
    .gr-block, .gr-box, .gr-form,
    .gradio-container .block,
    .gradio-container .panel {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }}

    /* labels */
    label span, .gr-block label {{
        font-family: ui-monospace, monospace !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: var(--muted) !important;
    }}

    /* inputs / dropdowns */
    select, input[type="text"], textarea, .gr-input {{
        background: var(--bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        font-family: system-ui, sans-serif !important;
    }}

    select:focus, input:focus, textarea:focus {{
        border-color: var(--accent) !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(0,229,197,0.15) !important;
    }}

    /* buttons */
    button.primary, .gr-button-primary {{
        background: var(--accent) !important;
        color: #080A10 !important;
        font-family: system-ui, sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        transition: transform 0.15s, box-shadow 0.15s !important;
    }}

    button.primary:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 24px rgba(0,229,197,0.25) !important;
    }}

    button.secondary, .gr-button-secondary {{
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--muted) !important;
        border-radius: 10px !important;
        font-family: system-ui, sans-serif !important;
        transition: border-color 0.15s, color 0.15s !important;
    }}

    button.secondary:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }}

    /* transcript output */
    #transcript-out textarea {{
        font-family: ui-monospace, monospace !important;
        font-size: 0.88rem !important;
        line-height: 1.8 !important;
        background: var(--bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        min-height: 280px !important;
    }}

    /* info card */
    #info-out {{
        background: rgba(0,229,197,0.05) !important;
        border: 1px solid rgba(0,229,197,0.2) !important;
        border-radius: 10px !important;
        padding: 16px !important;
        font-size: 0.85rem !important;
        line-height: 1.7 !important;
    }}

    #info-out strong {{ color: var(--accent) !important; }}

    /* audio component */
    .gr-audio {{ border-radius: 10px !important; }}

    /* checkbox */
    input[type="checkbox"] {{ accent-color: var(--accent) !important; }}

    /* progress */
    .progress-bar {{ background: var(--accent) !important; }}

    /* tab nav */
    .tab-nav button {{
        font-family: ui-monospace, monospace !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }}

    .tab-nav button.selected {{
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }}

    /* scrollbar */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--muted); }}
    """

    with gr.Blocks(title="VoiceScribe") as demo:

        gr.HTML("""
        <div id="vs-header">
          <h1>Voice<span>Scribe</span></h1>
          <p>Local audio transcription — no API key, no cloud, fully private</p>
        </div>
        """)

        with gr.Row():
            # ── LEFT COLUMN ──
            with gr.Column(scale=5):
                with gr.Tabs():
                    with gr.Tab("🎙 Record / Upload"):
                        audio_input = gr.Audio(
                            sources=["microphone", "upload"],
                            type="filepath",
                            label="Audio input",
                        )
                    with gr.Tab("📂 File path"):
                        file_path_input = gr.Textbox(
                            placeholder="/path/to/your/audio.mp3",
                            label="Absolute file path",
                            lines=1,
                        )

                with gr.Row():
                    model_select = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
                        value="base",
                        label="Model size",
                        info="larger = more accurate, slower to load",
                    )
                    task_select = gr.Dropdown(
                        choices=[("Transcribe", "transcribe"), ("Translate → English", "translate")],
                        value="transcribe",
                        label="Task",
                    )

                with gr.Row():
                    lang_select = gr.Dropdown(
                        choices=[
                            ("Auto-detect", "auto"),
                            ("Afrikaans", "af"), ("Arabic", "ar"),
                            ("Chinese", "zh"), ("Dutch", "nl"),
                            ("English", "en"), ("French", "fr"),
                            ("German", "de"), ("Hindi", "hi"),
                            ("Italian", "it"), ("Japanese", "ja"),
                            ("Korean", "ko"), ("Portuguese", "pt"),
                            ("Russian", "ru"), ("Spanish", "es"),
                            ("Swahili", "sw"), ("Turkish", "tr"),
                            ("Ukrainian", "uk"), ("Zulu", "zu"),
                        ],
                        value="auto",
                        label="Language",
                    )
                    fmt_select = gr.Dropdown(
                        choices=[
                            ("Plain text", "plain"),
                            ("Paragraphs", "paragraphs"),
                            ("Timestamped", "timestamped"),
                            ("SRT subtitles", "srt"),
                            ("VTT subtitles", "vtt"),
                        ],
                        value="plain",
                        label="Output format",
                    )

                word_ts = gr.Checkbox(label="Word-level timestamps", value=False)

                with gr.Row():
                    transcribe_btn = gr.Button("▶  Transcribe", variant="primary", scale=4)
                    clear_btn      = gr.Button("Clear", variant="secondary", scale=1)

            # ── RIGHT COLUMN ──
            with gr.Column(scale=7):
                transcript_out = gr.Textbox(
                    label="Transcript",
                    lines=14,
                    elem_id="transcript-out",
                    placeholder="Your transcript will appear here…",
                )
                info_out = gr.Markdown(elem_id="info-out")
                download_btn = gr.Button("⬇  Download transcript", variant="secondary")
                download_file = gr.File(label="Download", visible=False)

        # ─── Event wiring ────────────────────────────────────────────────────
        def get_audio_path(audio, filepath):
            """Return whichever source has content."""
            if audio:
                return audio
            if filepath:
                path = Path(filepath).expanduser()
                if path.is_file():
                    return str(path.resolve())
            return None

        def run(audio, filepath, model, lang, task, fmt, wts, progress=gr.Progress(track_tqdm=True)):
            path = get_audio_path(audio, filepath)
            if not path:
                return "", "⚠️ Please record, upload, or enter a file path."
            try:
                return transcribe(path, model, lang, task, fmt, wts, progress)
            except Exception:
                logger.exception("Transcription failed")
                return "", "⚠️ Transcription failed. Check the server logs for details."

        transcribe_btn.click(
            fn=run,
            inputs=[audio_input, file_path_input, model_select, lang_select,
                    task_select, fmt_select, word_ts],
            outputs=[transcript_out, info_out],
        )

        def do_download(text, fmt):
            path = save_transcript(text, fmt)
            if path:
                return gr.File(value=path, visible=True)
            return gr.File(visible=False)

        download_btn.click(
            fn=do_download,
            inputs=[transcript_out, fmt_select],
            outputs=[download_file],
        )

        clear_btn.click(
            fn=lambda: ("", "", None, ""),
            outputs=[transcript_out, info_out, audio_input, file_path_input],
        )

    return demo, custom_css


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo, custom_css = build_ui()
    demo.queue(default_concurrency_limit=1).launch(
        server_name=os.getenv("VOICESCRIBE_HOST", "127.0.0.1"),
        server_port=int(os.getenv("VOICESCRIBE_PORT", "7860")),
        share=os.getenv("VOICESCRIBE_SHARE", "false").lower() == "true",
        show_error=os.getenv("VOICESCRIBE_SHOW_ERROR", "false").lower() == "true",
        inbrowser=os.getenv("VOICESCRIBE_INBROWSER", "true").lower() == "true",
        css=custom_css,
    )
