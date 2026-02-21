from __future__ import annotations

import webbrowser
from threading import Timer

from flask import Flask, jsonify, render_template, request
from flask_compress import Compress

from problems.registry import discover_problems

app = Flask(__name__)
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


PORT = 5050


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    Timer(1.0, open_browser).start()
    app.run(debug=False, port=PORT)
