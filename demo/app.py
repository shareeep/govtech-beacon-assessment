#!/usr/bin/env python3
"""Minimal Flask app showing AI-triaged CIS findings as MR-style cards."""

import json
import os
from flask import Flask, render_template

app = Flask(__name__)

TRIAGE_FILE = os.environ.get("TRIAGE_FILE", "triage_results.json")


@app.route("/")
def index():
    try:
        with open(TRIAGE_FILE) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"total_failures": 0, "findings": [], "summary": {}}

    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
