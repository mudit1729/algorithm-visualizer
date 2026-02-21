from __future__ import annotations

import webbrowser
from threading import Timer

from flask import Flask, jsonify, render_template, request

from problems.registry import discover_problems

app = Flask(__name__)

_problems = discover_problems()


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
def run_problem():
    data = request.get_json()
    problem_name = data.get("problem")
    params = data.get("params", {})

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
            "steps": [s.to_dict() for s in steps],
        }
    )


PORT = 5050


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    Timer(1.0, open_browser).start()
    app.run(debug=False, port=PORT)
