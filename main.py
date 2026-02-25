from __future__ import annotations

import json
import os
import webbrowser
from datetime import datetime, timezone
from threading import Timer
from urllib.error import HTTPError
from urllib.request import Request as URLRequest
from urllib.request import urlopen

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_compress import Compress

from problems.registry import discover_problems

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_REALTIME_MODEL = "gpt-4o-realtime-preview-2024-12-17"

VOICE_TOOLS = [
    {
        "type": "function",
        "name": "seek_to_step",
        "description": "Jump the visualizer to a specific step by index. Call this BEFORE explaining what happens at that step so the student can see it.",
        "parameters": {
            "type": "object",
            "properties": {
                "step_index": {
                    "type": "integer",
                    "description": "Zero-based index of the step to jump to (0 to total_steps-1)",
                }
            },
            "required": ["step_index"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "highlight_code_lines",
        "description": "Highlight a contiguous range of lines in the source code panel. Use to draw the student's attention to specific code.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_line": {
                    "type": "integer",
                    "description": "1-based line number to start highlighting",
                },
                "end_line": {
                    "type": "integer",
                    "description": "1-based line number to end highlighting (inclusive)",
                },
            },
            "required": ["start_line", "end_line"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "play_steps",
        "description": "Animate the visualizer playing from one step to another, then auto-pause. Good for showing a sequence of operations.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_step": {
                    "type": "integer",
                    "description": "Zero-based index to start playing from",
                },
                "to_step": {
                    "type": "integer",
                    "description": "Zero-based index to stop at (inclusive, will pause here)",
                },
            },
            "required": ["from_step", "to_step"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "pause_player",
        "description": "Pause the visualizer animation if it is currently playing.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_current_state",
        "description": "Get the current state of the visualizer: which step is displayed, how many total steps, whether it is playing, and the current step description.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "clear_highlight",
        "description": "Remove the extra code highlight range, restoring only the default single-line highlight for the current step.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
]
app.config["COMPRESS_REGISTER"] = False
app.config["COMPRESS_ALGORITHM"] = ["br", "gzip"]
app.config["COMPRESS_LEVEL"] = 6
app.config["COMPRESS_MIN_SIZE"] = 500
compress = Compress(app)

_problems = discover_problems()


def _coerce_bool(value: object, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    if isinstance(value, (int, float)):
        return value != 0
    return default


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/screenshots/<path:filename>")
def serve_screenshot(filename):
    return send_from_directory("screenshots", filename)


@app.route("/api/problems")
def list_problems():
    result = []
    for name, cls in _problems.items():
        result.append(
            {
                "name": name,
                "topic": cls.topic(),
                "subtopic": cls.subtopic(),
                "description": cls.description(),
                "long_description": cls.long_description(),
                "renderer_type": cls.renderer_type(),
                "default_params": cls.default_params(),
            }
        )
    return jsonify(result)


@app.route("/api/run", methods=["POST"])
@compress.compressed()
def run_problem():
    data = request.get_json(silent=True) or {}
    problem_name = data.get("problem")
    params = data.get("params", {})
    compact = _coerce_bool(data.get("compact"), default=True)

    if not isinstance(params, dict):
        return jsonify({"error": "'params' must be an object"}), 400

    cls = _problems.get(problem_name)
    if cls is None:
        return jsonify({"error": f"Unknown problem: {problem_name}"}), 404

    # Convert param values to appropriate types
    clean_params = {}
    for k, v in params.items():
        try:
            clean_params[k] = int(v)
        except (ValueError, TypeError):
            clean_params[k] = v

    steps = cls.generate_steps(**clean_params)

    return jsonify(
        {
            "source_code": cls.source_code(),
            "renderer_type": cls.renderer_type(),
            "steps": [s.to_dict(compact=compact) for s in steps],
        }
    )


def _build_voice_prompt(cls, steps):
    """Build the system prompt for the voice tutor agent."""
    step_lines = []
    for i, s in enumerate(steps):
        desc = s.description or "(no description)"
        step_lines.append(f"  Step {i}: line {s.line_number} — {desc}")
    step_listing = "\n".join(step_lines)

    long_desc = cls.long_description()
    long_desc_block = f"\nFULL PROBLEM STATEMENT:\n{long_desc}\n" if long_desc else ""

    return f"""You are an expert algorithm tutor guiding a student through a live visualization of "{cls.name()}".

PROBLEM: {cls.description()}
{long_desc_block}
SOURCE CODE (line numbers are 1-based):
```
{cls.source_code()}
```

VISUALIZATION STEPS ({len(steps)} total, zero-indexed):
{step_listing}

INSTRUCTIONS:
- You are speaking aloud via audio. Use short, clear, conversational sentences. Do NOT use markdown, bullet points, or formatting — this is speech.
- ALWAYS call seek_to_step BEFORE explaining what happens at a step, so the student sees the visualization update while you talk.
- When referencing specific lines of code, call highlight_code_lines first to draw attention, then explain.
- Call clear_highlight when you move on to a different topic.
- When the student starts a session, give a brief 2-3 sentence overview of the problem, then begin walking through the visualization step by step.
- You do NOT need to explain every single step. Group related steps (e.g. "steps 5 through 12 process the neighbors") and use play_steps to animate ranges.
- If the student asks a question, call get_current_state to know where they are, then answer in context.
- If you receive a message saying the user navigated to a different step, acknowledge it briefly and explain that step.
- Mention time/space complexity when you reach the end of the walkthrough.
- Share practical interview tips if relevant (e.g. "interviewers often ask about edge cases like...").
- Keep your pace moderate. Pause briefly between major phases of the algorithm.
"""


@app.route("/api/voice-session", methods=["POST"])
def voice_session():
    if not OPENAI_API_KEY:
        return jsonify({"error": "OPENAI_API_KEY not configured on server"}), 500

    data = request.get_json(silent=True) or {}
    problem_name = data.get("problem_id")

    cls = _problems.get(problem_name)
    if cls is None:
        return jsonify({"error": f"Unknown problem: {problem_name}"}), 404

    params = cls.default_params()
    steps = cls.generate_steps(**params)
    system_prompt = _build_voice_prompt(cls, steps)

    body = json.dumps(
        {
            "model": OPENAI_REALTIME_MODEL,
            "voice": "ash",
            "modalities": ["text", "audio"],
            "instructions": system_prompt,
            "tools": VOICE_TOOLS,
            "input_audio_transcription": {"model": "gpt-4o-mini-transcribe"},
        }
    ).encode()

    req = URLRequest(
        "https://api.openai.com/v1/realtime/sessions",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req) as resp:
            session_data = json.loads(resp.read())
    except HTTPError as e:
        error_body = e.read().decode()
        return (
            jsonify({"error": f"OpenAI API error: {e.code}", "detail": error_body}),
            502,
        )

    client_secret = session_data.get("client_secret", {})
    return jsonify(
        {
            "token": client_secret.get("value"),
            "expires_at": client_secret.get("expires_at"),
            "step_count": len(steps),
        }
    )


@app.route("/api/log-session", methods=["POST"])
def log_session():
    data = request.get_json(silent=True) or {}
    data["server_timestamp"] = datetime.now(timezone.utc).isoformat()
    with open("session_log.jsonl", "a") as f:
        f.write(json.dumps(data) + "\n")
    return jsonify({"ok": True})


PORT = 5050


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    Timer(1.0, open_browser).start()
    app.run(debug=False, port=PORT, host="0.0.0.0")
