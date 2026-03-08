#!/usr/bin/env python3
"""Minimal Flask app showing AI-triaged CIS findings as MR-style cards."""

import json
import os
import subprocess
from flask import Flask, render_template, redirect, url_for, send_file, abort

app = Flask(__name__)

TRIAGE_FILE = os.environ.get("TRIAGE_FILE", "triage_results.json")
RESULTS_DIR = "/app/results"


@app.route("/")
def index():
    try:
        with open(TRIAGE_FILE) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"total_failures": 0, "findings": [], "summary": {}}

    return render_template("index.html", data=data)


@app.route("/rescan")
def rescan():
    """Trigger a new scan+triage cycle. In production this would be a scheduled job."""
    # Run Ansible scan
    subprocess.run(
        ["ansible-playbook", "-i", "ansible/inventory.ini", "ansible/scan.yml"],
        cwd="/app",
        env={**os.environ, "ANSIBLE_HOST_KEY_CHECKING": "False"},
        check=True,
    )

    # Find results and triage
    results_xml = None
    for root, _dirs, files in os.walk(RESULTS_DIR):
        if "results.xml" in files:
            results_xml = os.path.join(root, "results.xml")
            break

    if results_xml:
        cmd = ["python", "triage.py", "--results", results_xml, "--output", TRIAGE_FILE]
        if not os.environ.get("OPENAI_API_KEY"):
            cmd.append("--mock")
        subprocess.run(cmd, cwd="/app", check=True)

    return redirect(url_for("index"))


@app.route("/report")
def report():
    """Serve the original OpenSCAP HTML report."""
    for root, _dirs, files in os.walk(RESULTS_DIR):
        if "report.html" in files:
            return send_file(os.path.join(root, "report.html"))
    abort(404)
    abort(404)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
