#!/bin/bash
set -e

# ── CIS Compliance Triage Pipeline ────────────────────────────
#
# This script orchestrates the full scan → triage → serve flow.
# It replicates what would happen in production:
#
#   1. Ansible SSHs into the target server (Zone 1 — server access)
#   2. Installs oscap + scap-security-guide if not present
#   3. Runs CIS benchmark scan, fetches results.xml back
#   4. AI triage parses XML and prioritises findings (Zone 2 — no server access)
#   5. Flask serves MR-style cards for human review
#
# In production, steps 1-4 would be a daily cron job or Ansible Tower
# scheduled job. The Flask UI exposes /rescan for on-demand re-runs
# during the demo.
#
# Key architectural point: the AI (step 4) never touches the server.
# It only reads the XML output. This is a security boundary by design.
# ───────────────────────────────────────────────────────────────

RESULTS_DIR="/app/results"
TRIAGE_OUT="$RESULTS_DIR/triage_results.json"

echo "=== CIS Compliance Triage Pipeline ==="
echo ""

# ── Step 1: Wait for target SSH ───────────────────────────────
# The target container runs an SSH daemon (simulating a real server).
# In production, this wait wouldn't exist — servers are already running.
# Here we just need to wait for the container to boot.
echo "[1/3] Waiting for target server SSH..."
for i in $(seq 1 30); do
  if sshpass -p demo1234 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@target echo "SSH ready" 2>/dev/null; then
    break
  fi
  echo "  Waiting... ($i/30)"
  sleep 2
done

# ── Step 2: Ansible scan (Zone 1 — has server access) ─────────
# This is the "bolt‐on" part: Ansible is agentless. Nothing gets
# installed permanently on the target. The playbook:
#   - SSHs in using credentials from inventory.ini
#   - Installs openscap‐scanner + scap‐security‐guide (idempotent)
#   - Runs: oscap xccdf eval --profile cis --results results.xml
#   - Fetches results.xml + report.html back to this container
# To add a new server, add one line to inventory.ini. That's it.
echo ""
echo "[2/3] Running Ansible scan against target server..."
cd /app/ansible
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.ini scan.yml
cd /app

RESULTS_FILE=$(find "$RESULTS_DIR" -name "results.xml" | head -1)
if [ -z "$RESULTS_FILE" ]; then
  echo "ERROR: No results.xml found. Scan may have failed."
  exit 1
fi

# ── Step 3: AI triage (Zone 2 — no server access) ─────────────
# triage.py parses the oscap XML and either:
#   --mock: uses keyword heuristics (no API key needed)
#   default: sends findings to an OpenAI-compatible API
#
# Either way, output is structured JSON with severity, explanation,
# remediation command, and a grounding check (catches hallucinations).
echo ""
echo "[3/3] Running AI triage on scan results..."
TRIAGE_CMD="python triage.py --results $RESULTS_FILE --output $TRIAGE_OUT"
if [ -z "$OPENAI_API_KEY" ]; then
  TRIAGE_CMD="$TRIAGE_CMD --mock"
fi
$TRIAGE_CMD

echo ""
echo "  Scan complete at $(date '+%Y-%m-%d %H:%M:%S')"

# ── Start web UI ──────────────────────────────────────────────
# Flask serves the triaged findings as MR-style cards.
# /rescan triggers a fresh scan+triage cycle on demand.
# In production this would be a dashboard (Grafana, etc.) pulling
# from the same structured JSON.
echo ""
echo "Starting web UI on port 5001..."
echo "  Open http://localhost:5001"
echo "  Hit  http://localhost:5001/rescan to trigger a new scan"
TRIAGE_FILE="$TRIAGE_OUT" python app.py
