#!/bin/bash
set -e

echo "=== CIS Compliance Triage Pipeline ==="
echo ""

# Wait for target's SSH to be ready
echo "[1/4] Waiting for target server SSH..."
for i in $(seq 1 30); do
  if sshpass -p demo1234 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 root@target echo "SSH ready" 2>/dev/null; then
    break
  fi
  echo "  Waiting... ($i/30)"
  sleep 2
done

# Run Ansible playbook — SSHs into target, installs oscap, runs scan, fetches results
echo ""
echo "[2/4] Running Ansible scan against target server..."
cd /app/ansible
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.ini scan.yml
cd /app

# Run triage on collected results
echo ""
echo "[3/4] Running AI triage on scan results..."
RESULTS_FILE=$(find /app/results -name "results.xml" | head -1)

if [ -z "$RESULTS_FILE" ]; then
  echo "ERROR: No results.xml found. Scan may have failed."
  exit 1
fi

if [ -n "$OPENAI_API_KEY" ]; then
  python triage.py --results "$RESULTS_FILE" --output /app/results/triage_results.json
else
  python triage.py --results "$RESULTS_FILE" --output /app/results/triage_results.json --mock
fi

# Start web UI
echo ""
echo "[4/4] Starting web UI on port 5001..."
echo "  Open http://localhost:5001"
TRIAGE_FILE=/app/results/triage_results.json python app.py
