# CIS Compliance Triage — Demo

**Dependabot for CIS Benchmarks.** Scans a RHEL server against CIS security guidelines, AI triages the findings, and presents them as actionable cards for engineers to review.

One command: `podman compose up --build` → open http://localhost:5001

---

## What it does

![Dashboard header — severity badges, timing, system selector](../images/header.png)

The pipeline:
1. **Scan** — Ansible SSHs into target, installs OpenSCAP, runs CIS Level 1 scan, fetches results
2. **AI Triage** — Parses XML, sends failed controls to gpt-4o. Returns re-prioritised severity, remediation commands, verification steps, rollback instructions, attack chains
3. **Grounding** — 6 programmatic checks validate AI output against scan data (no LLM-as-judge)
4. **Web UI** — MR-style cards sorted by severity, with expandable detail panels

### Attack Chains

![Attack chain — compound threat grouping multiple findings](../images/attack-chain.png)

The AI identifies findings that combine into compound threats — individual "medium" findings that together become critical. Each chain links to the relevant finding cards.

### Finding Cards

![Sample finding card — severity, remediation, details](../images/sample-entry-1.png)

Each card shows: AI-assessed severity (with ⬆ Upgraded tag if higher than OpenSCAP's rating), plain-English explanation, and remediation command.

![Expanded detail panel — verification, rollback, change window](../images/sample-entry-2.png)

Expand "Details" for: fix complexity, change window (live vs restart), automation readiness, verification command, rollback steps, related findings, and OpenSCAP vs AI severity comparison.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      compose network                         │
│                                                              │
│  ┌─────────────┐        SSH          ┌─────────────────┐    │
│  │  app         │ ──────────────────► │  target          │   │
│  │  (Python +   │                     │  (Rocky 9 +      │   │
│  │   Ansible)   │ ◄── results.xml ── │   13 misconfigs)  │   │
│  └──────┬───────┘                     └──────────────────┘   │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ triage.py    │─►│ Flask UI     │  │ eval.py      │       │
│  │ XML → AI     │  │ port 5001    │  │ ground truth │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘

Zone 1 (server access):  Ansible + oscap on the target
Zone 2 (AI, no access):  triage.py only reads the XML output
```

**Key constraint**: The AI never touches servers. It only reads structured XML from the scanner. All server access is through Ansible/SSH (Zone 1).

---

## Quickstart

### Prerequisites
- Podman + podman-compose (or Docker + docker-compose)
- Optional: OpenAI API key for real AI triage

### Run

```bash
cd demo
podman compose up --build
```

Pipeline runs automatically: build containers → wait for SSH → Ansible scan → AI triage → web UI on port 5001.

### With real AI triage

```bash
cp .env.example .env
echo "OPENAI_API_KEY=sk-..." > .env
podman compose up --build
```

Without a key, falls back to mock mode (keyword heuristics).

### Rescan

Hit http://localhost:5001/rescan to re-run the scan+triage pipeline.

### Evaluate

```bash
podman compose exec app python eval.py --triage /app/results/triage_results.json
```

Scores detection rate, severity accuracy, and grounding (hallucination check).

---

## Files

| File | Purpose |
|---|---|
| `compose.yaml` | Orchestrates both containers via SSH |
| `Containerfile` | Rocky 9 target — 13 intentional CIS misconfigs + SSH |
| `Containerfile.app` | App container — Python + Ansible + Flask |
| `start.sh` | Pipeline: wait SSH → scan → triage → serve |
| `ansible/inventory.ini` | Target list (one line per server) |
| `ansible/scan.yml` | Playbook: install oscap, scan, fetch results |
| `triage.py` | Parse XML → AI triage → JSON (with grounding checks) |
| `app.py` | Flask web UI |
| `eval.py` | Score AI accuracy against ground truth |

## Target misconfigurations

13 intentional CIS violations across SSH (root login, empty passwords), file permissions (world-readable shadow), packages (telnet, mariadb-server), user accounts (empty password, no aging), and kernel params (IP forwarding, SYN cookies disabled). See [Containerfile](Containerfile) for each one mapped to its CIS control ID.
