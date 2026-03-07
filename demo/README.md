# CIS Compliance Triage — Demo

A minimal working demo of the "Dependabot for CIS Benchmarks" pipeline.
Two containers, one command — replicates the real architecture:

```
app (control node) ──SSH (Ansible)──► target (misconfigured RHEL server)
```

1. **Scan** — Ansible SSHs into target, runs OpenSCAP CIS scan, fetches results
2. **Triage** — AI (or mock heuristics) prioritises findings by severity
3. **Review** — Web UI shows MR-style cards with approve/dismiss
4. **Eval** — Ground truth check scores the AI's accuracy

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

Zone 1 (server access):  Ansible + oscap on the target container
Zone 2 (AI, no access):  triage.py only reads the XML output
```

## Quickstart

### Prerequisites
- Podman + podman-compose (or Docker + docker-compose)
- Optional: OpenAI API key for real AI triage

### One command

```bash
cd demo
podman-compose up --build
```

That's it. The pipeline runs automatically:
1. Builds the target container (Rocky 9 + 13 intentional CIS misconfigs + SSH)
2. Builds the app container (Python + Ansible + Flask)
3. App waits for target SSH → runs Ansible scan → triages → starts web UI

Open **http://localhost:5001** to see MR-style findings.

### With real AI triage

```bash
# Copy the example and add your key
cp .env.example .env
echo "OPENAI_API_KEY=sk-..." > .env

podman-compose up --build
```

Without a key, it falls back to mock mode (keyword heuristics).

### Evaluate the AI

After the pipeline runs, exec into the app container:

```bash
podman-compose exec app python eval.py --triage /app/results/triage_results.json
```

Scores: detection rate, severity accuracy, grounding (hallucination check).

## What's in the target container?

13 intentional misconfigurations across:
- **SSH** (CIS 5.2.x) — root login, empty passwords, weak MaxAuthTries
- **File permissions** (CIS 6.1.x) — world-readable shadow, world-writable dir
- **Packages** (CIS 2.2.x) — telnet, mariadb-server installed
- **User accounts** (CIS 5.4.x) — empty password user, no password aging
- **Kernel** (CIS 3.2.x) — IP forwarding, ICMP redirects, SYN cookies disabled

See [Containerfile](Containerfile) comments for each one mapped to its CIS control ID.

## Files

| File | Purpose |
|---|---|
| `compose.yaml` | Orchestrates both containers via SSH |
| `Containerfile` | Rocky 9 target — 13 intentional CIS misconfigs + SSH |
| `Containerfile.app` | App container — Python + Ansible + Flask |
| `start.sh` | Pipeline entrypoint: wait for SSH → scan → triage → serve |
| `ansible/inventory.ini` | Target server list (add one line per server) |
| `ansible/scan.yml` | Playbook: install oscap, scan, fetch results |
| `triage.py` | Parse oscap XML → AI triage → structured JSON |
| `app.py` | Flask web UI — MR-style finding cards |
| `templates/index.html` | Card UI with severity badges + remediation |
| `eval.py` | Score AI accuracy against ground truth |
| `.env.example` | Environment variable template |

## Notes for the assessment

- **CIS RHEL Benchmark only covers OS-level settings.** MariaDB is installed to
  trigger "unnecessary service" findings, but its *own* security config (root
  password etc) is checked by a separate CIS MySQL Benchmark.
- **The AI never touches production.** It only reads scan output (Zone 2). All
  server access is through Ansible/SSH with least privilege (Zone 1).
- **No auto-remediation.** The tool proposes MRs, humans approve. Same workflow
  as code review.
