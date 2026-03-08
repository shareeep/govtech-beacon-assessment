# IT Controls, Cybersecurity & AI Integration — Assessment

---

## Section 1: Foundational Knowledge

---

### 1. What is the purpose of system hardening in an enterprise environment, and why is it important?

System hardening reduces a system's attack surface by eliminating unnecessary software, services, accounts, and configurations an attacker could exploit. [Intel]

It matters for three key reasons:

1. **Default installations prioritise convenience over security.** Default OS and application configurations are optimised for ease of development, not security, which leaves unnecessary services and insecure defaults enabled. Examples: MySQL allowing root access with a blank password by default, kube-prometheus-stack deploying Grafana with widely known default credentials such as `admin/admin`. [MySQL Docs, Grafana Docs]
2. **Regulatory compliance demands it.** Major frameworks mandate system hardening as a non-negotiable baseline control. An example is SG Gov IM8 (ICT&SS Management) mandating system hardening as the strict security baseline for all public sector IT systems. Non-compliance in these environments can lead to audit failures, regulatory fines, and blocked deployments. [Worked on a ticket at work to add 1hr session timeout IM8 - AS-11: Session Management]
3. **Hardened systems are easier to defend.** A smaller attack surface means fewer open ports, tighter permissions, stripped-down configurations. This reduces vulnerabilities, simplifies monitoring and auditing.

In practice, this means: disabling unnecessary services/ports, enforcing principle of least privilege, enabling audit logging, removing default credentials, patching, and configuring host-based firewalls.

---

### 2. Describe briefly the purpose of CIS Benchmarks and OpenSCAP.

**CIS Benchmarks** define what security settings should exist. **OpenSCAP** is a tool that automatically verifies those settings using SCAP content (e.g. via the `oscap` CLI).

**Workflow:**
CIS Benchmarks (security recommendations) → translated into SCAP rules (XCCDF + OVAL, XML format) → packaged in content such as SCAP Security Guide → scanned using OpenSCAP (`oscap`) against the target system → compliance report generated.

**CIS Benchmarks** are secure configuration recommendations from the Center for Internet Security that harden specific technologies (OS, cloud, databases, network devices, etc.) against cyber attacks. They are globally recognised and community-developed. Level 1 covers essential controls and Level 2 are stricter controls for high-risk/regulated environments. They typically also help with regulatory compliance. [CIS Benchmarks FAQ]

**OpenSCAP** is an open-source toolset that implements the Security Content Automation Protocol (SCAP) developed by NIST (National Institute of Standards and Technology). It allows systems to be automatically evaluated against machine-readable security policies using tools such as the `oscap` command-line interface. [oscap cli - OpenSCAP Manual]

---

### 3. How would you use a programming language like Python to automate a repetitive IT task?

I would use Python to automate repetitive IT tasks by writing scripts that perform routine checks or actions.

For example, for network monitoring, I could create a Python script that periodically checks whether a server or website is online and sends an alert if it's down. This script could be scheduled with `cron` to run automatically at set intervals. Python's libraries like `requests` for HTTP checks and `smtplib` for notifications make this straightforward, and the same approach can be applied to file management, API interactions, or other repetitive IT tasks.

```bash
*/5 * * * * /usr/bin/python3 /path/to/script.py  # every 5 minutes cron job
```

```python
import requests

url = "https://example.com"
try:
    if requests.get(url).status_code != 200:
        print(f"{url} is down!")
except requests.RequestException:
    print(f"{url} is down!")
```

[Source: For administrative IT tasks, I have used tools like Uptime Monitoring by Better Stack. At my former internship, I developed a robust Python script that would parse Google Docs word documents into a JSON object with proper formatting, for use in our learning platform, which was a huge time saver for the developers and writers.]

---

### 4. Share your understanding of web scraping / API functions, and how AI tools can use them.

**Web scraping** extracts data directly from webpage HTML. I use tools like JinaAI to scrape, followed by BeautifulSoup to clean the output and remove HTML tags. Scraping is unstructured and fragile since website layouts change.

**APIs** provide data through structured, dedicated endpoints. These may require authentication, but some are public access and provide sufficient data. Typically with a scraping script, we may want to add pauses between requests to avoid hitting rate limits. They output clean, reliable data (like JSON) and are far more stable than direct webpage scraping.

**How AI tools use them:**

AI agents/chatbots with added functionality can use tools to access external data. Through frameworks like the **Model Context Protocol (MCP)** which acts as an API gateway for agents, an AI can use a tool like Playwright MCP to access a browser, navigate the DOM, and scrape a page. In simpler cases, the AI could execute a basic HTTP fetch or `curl` to retrieve the webpage. In this case, it could directly scrape data to shape its response, or trigger API calls to get a desired response.

[Source: I use AI at work and my team leverages AI-assisted coding heavily. I also have developed an MCP server that wraps around an existing service.]

---

### 5. What are the main considerations to test / validate an AI tool's response for accuracy (hallucinations, etc.)?

The main approach is to use **evals** (evaluations of the AI system/tool). We define a set of metrics to grade the AI's output against. This is like stress testing, and as we know AI is non-deterministic, so we need to ensure that the output remains consistent in usage.

Generally, we deploy **LLM-as-judge**, but there are other more traditional methods to do recall checks. LLM grading the output of the AI tool, with the presence of our ground truth, is what typically helps validate against hallucinations. Common approaches include:

- **Correctness & Recall**: Compare outputs to ground truth sources or benchmark labels to ensure factual accuracy and completeness.
- **Faithfulness & Relevance**: Ensure answers are supported by provided context and directly address the query.
- **Structured Output Validation**: Enforce schemas (JSON, required fields) to enable automated checks for malformed or incomplete responses.
- **Consistency**: Repeat queries across runs or models; divergences highlight unreliable outputs.
- **Adversarial Robustness**: Stress-test with edge cases or policy-violating prompts to reveal vulnerabilities.
- **Human-in-the-loop**: High-stakes scenarios require human review before action.

[Source: I help develop the FE and BE of an AI-powered procurement report service, and I have seen the AI engineers use these metrics. In my research of developing AI systems, these are common metrics and ways to improve the reliability and usefulness of AI outputs.]

---

## Section 2: Case Studies

---

### Case Study 1 — Automating System Security Checks

**Context**: Building a tool to automate CIS Benchmark hardening checks for RHEL servers, evaluating AI vs. programmatic approaches.

**Overall approach**: The tool works like **Dependabot, but for CIS Benchmarks on RHEL servers** — it scans, identifies non-compliance, and generates change requests (MRs/PRs) with remediation for engineers to review and approve before anything is applied.

**Architecture:**

```
┌─ Zone 1: Server Access ──────────────────────────────────────┐
│                                                               │
│  Ansible (SSH, key-based) ──► Target Servers                 │
│                                  └─ installs oscap if needed  │
│                                  └─ runs CIS L1 scan          │
│                                  └─ outputs: XML + HTML       │
│                                                               │
│  Results fetched back to control node via Ansible             │
│  (AI never touches servers — only reads scan output)          │
└─────────────────────────────┬─────────────────────────────────┘
                              │ structured XML
                              ▼
┌─ Zone 2: AI Triage (no server access) ───────────────────────┐
│                                                               │
│  Parses XML → sends failed controls to LLM → returns:        │
│  • Re-prioritised severity (may upgrade from oscap rating)    │
│  • Plain-English explanation + remediation command            │
│  • Verification command (confirm fix without full rescan)     │
│  • Rollback instruction (undo if fix causes issues)           │
│  • Fix complexity, change window, automation readiness        │
│  • Related findings ("fix these together — same config")      │
│  • Attack chains (compound risk across multiple findings)     │
│  • Intentional deviation flag                                 │
│                                                               │
│  Grounded by architecture, not just prompting:                │
│  1. Input bounded — AI only receives parsed XML from oscap    │
│  2. Output validated — every rule AI mentions must exist       │
│     in the scan results (hallucination caught automatically)  │
│  3. Action gated — human reviews MR before any change         │
└─────────────────────────────┬─────────────────────────────────┘
                              ▼
┌─ Output ─────────────────────────────────────────────────────┐
│  MR-style cards (per finding: severity, remediation, details) │
│  Attack chain view (compound threats across findings)          │
│  Dashboard (compliance %, trends, per-server drill-down)      │
│  Alerts (Slack/PagerDuty on compliance drift)                 │
│  DB for historical data + cross-server querying               │
└───────────────────────────────────────────────────────────────┘
```

**Key design decisions:**

1. **Deterministic scanner, AI interpreter.** `oscap` determines compliance (auditable, reproducible). AI explains, prioritises, and drafts remediations — but never determines pass/fail. Same principle as preferring APIs over scraping (Q4): use structured, reliable data as the source of truth, let AI interpret it.
2. **AI grounded by architecture.** The AI can't access servers. Its input is bounded (XML only). Its output is validated (grounding check). Its actions are gated (human approval). Three layers of control — not just prompt engineering.
3. **Same automation pattern as Q3** — script (`oscap`) + schedule (cron/Ansible) + report (dashboard/MR). Ansible orchestrates, Python glues.

**Demo implementation** (in `demo/` directory) proves the pipeline end-to-end with real SSH-based architecture:

- **Target container**: Rocky Linux 9 with SSH daemon + 13 intentional CIS violations (SSH misconfigs, weak file permissions on shadow/gshadow, unnecessary packages like telnet, users with empty passwords, insecure kernel parameters)
- **App container**: Python 3.11 + Ansible + Flask. Ansible SSHs into target, installs oscap, runs CIS L1 Server scan, fetches XML + HTML results back.
- **AI triage** (real gpt-4o): Parses XML, sends failed controls to LLM. Returns: re-prioritised severity, plain-English explanation, remediation command, verification command (confirm fix without full rescan), rollback instruction, fix complexity, change window guidance, automation readiness, related findings ("fix together"), and attack chain analysis (compound threats).
- **Grounding check**: Every rule the AI returns is validated against parsed scan results — hallucinated rules are caught automatically.
- **Web UI** (Flask on port 5001): MR-style cards sorted by severity. Shows attack chains at the top ("these 4 findings combine into unauthenticated access to password hashes"). Findings tagged ⬆ Upgraded when AI rates higher than OpenSCAP. Expandable detail panel per finding. Original OpenSCAP HTML report accessible via /report.
- **Real results**: 8 failed controls, 5 upgraded by AI from medium to critical/high based on real-world impact. 1 attack chain identified grouping 4 shadow/gshadow file permission findings.
- Mock mode works without API key; real mode with any OpenAI-compatible endpoint.
- Single command to run: `podman compose up --build`

---

#### 1. How would your tool check server settings? Any security considerations?

I would use **OpenSCAP** (`oscap`) as the scanning engine — it's the standard tooling for evaluating SCAP content against system configuration. It handles querying configuration files, checking running state, and evaluating kernel parameters against a defined security profile. No need to write custom parsers.

```bash
oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis_server_l1 \
  --results results.xml \
  --report report.html \
  /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml
```

This produces an HTML report with pass/fail for each CIS control, plus remediation snippets (Ansible/shell) for each failure.

For remote scanning, **OpenSCAP provides `oscap-ssh`** — a built-in utility that SSHs into a target, copies SCAP content, runs the evaluation, and downloads results. I use **Ansible** instead because it scales to fleet management (one inventory line per server), handles idempotent installation, and integrates with orchestration tools like Ansible Tower — but the underlying SSH-based approach is the same one OpenSCAP's own docs endorse.

The output needs to be verified:

- Results should be **spot-checked by a senior engineer/sysadmin** familiar with the environment, especially for the first few runs.
- A flagged "failure" may be an intentional deviation — e.g., a legacy app requiring an older TLS version. Context matters.
- The compliance report should be reviewed with the infrastructure team before acting on findings.

**Security considerations for the tool itself:**

- **Least privilege**: Read access to configs only. Where root is required, use `sudo` with a tightly scoped policy.
- **Transport security**: If connecting remotely (SSH), key-based auth only — never store passwords in scripts.
- **Output handling**: Reports contain sensitive configuration details. Store encrypted, restrict access to authorised personnel.
- **No auto-remediation**: The tool *reports* non-compliance, it doesn't fix it. Remediation goes through change management — like a PR that needs approval before merge.
- **Tool integrity**: The scanning scripts and SCAP profiles should be version-controlled, code-reviewed, and stored in a tamper-evident repository. If an attacker modifies the scanning tool or its profiles, a compromised server can appear compliant.

[Source: OpenSCAP project docs, CIS Benchmark documentation, tested locally with Rocky Linux 9 container]

---

#### 2. How would your tool verify compliance with CIS Benchmarks?

Use **OpenSCAP with SCAP Security Guide**. Red Hat ships `scap-security-guide` with pre-built CIS profiles (Level 1 Server, Level 1 Workstation, Level 2 Server, Level 2 Workstation) that translate the CIS PDF recommendations into machine-readable SCAP rules. The profiles are automatically available after install — no separate download.

**How it works:**

1. Install `openscap-scanner` + `scap-security-guide` on the target.
2. Select the appropriate CIS profile — the package bundles profiles matched to the OS version (e.g., `ssg-rl9-ds.xml` for Rocky Linux 9 / RHEL 9). The demo uses `xccdf_org.ssgproject.content_profile_cis_server_l1` (CIS Level 1 - Server), which covers essential baseline controls suitable for most production servers.
3. `oscap` evaluates each CIS control against actual system state — checking config files, service states, file permissions, kernel parameters, etc.
4. Outputs: machine-readable XML (for automation) + human-readable HTML report with pass/fail per CIS control ID + remediation snippets (Ansible/shell).

A key finding from building the demo: L1 and L2 profiles in the SCAP Security Guide for Rocky Linux 9 evaluate the **same set of 1,523 rules** — the difference is in profile selection and scoring thresholds, not separate rule sets. This means the scanner reports on the same controls regardless of profile; the profile determines which are *required* to pass.

This is battle-tested, community-maintained, and produces auditor-ready reports. The alternative — writing custom checks mapped to each CIS control — is possible but means manually maintaining the mapping every time CIS releases a new version. SCAP Security Guide handles that for you.

[Source: Red Hat SCAP Security Guide docs, OpenSCAP project docs, CIS Benchmarks FAQ, tested locally with Rocky Linux 9 container — verified 1,523 rules evaluated across both L1 and L2 profiles]

---

#### 3. How would you automate this?

Three layers: **scan**, **orchestrate**, **report** (as shown in the architecture above).

**Scan**: `oscap` runs against each server and outputs results (XML) + report (HTML) with remediation snippets.

**Orchestrate**: Use **Ansible** to run the scan across all RHEL hosts — it's agentless (SSH), aligns with the Red Hat ecosystem, scales easily. A playbook installs `openscap-scanner` + `scap-security-guide` on each host (idempotent), runs the scan, and fetches XML + HTML results back to the control node. Schedule recurring scans via **cron** or **Ansible Tower/AWX**. (Note: OpenSCAP also ships `oscap-ssh` for ad-hoc remote scanning — our Ansible approach is the production-grade version of the same SSH-based concept, adding fleet management and Tower/AWX integration.)

**Report + Monitor**: Store results in a database (Elasticsearch/PostgreSQL) for trending. Visualise in **Grafana/Kibana** — per-server compliance percentages, most-failed controls, trends over time. Set up **alerts** (Slack, PagerDuty) when compliance drops — e.g., "prod-db-01 at 78% CIS compliance, down from 95%." This gives the team a live view of fleet security posture.

**Remediate (the Dependabot analogy)**: This is where AI adds practical value that goes beyond what the scanner provides. As outlined in the architecture, the AI never reads raw server configs — it consumes the **structured XML output** from `oscap` only. The scanner already provides Ansible/shell remediation snippets for each failure — but these are generated for a generic RHEL install. In practice, they won't always work first try: custom paths, conflicting services, environment-specific dependencies. So:

1. For each actionable failure, **generate a change request** (MR/PR) containing the remediation snippet from `oscap`.
2. AI triages findings — re-prioritises by severity (in the demo, 5 of 8 findings were upgraded from OpenSCAP's "medium" to "critical" or "high" based on real-world impact). It also identifies **attack chains** — where individual findings combine into compound threats (e.g., "these 4 shadow/gshadow permission issues together expose password hashes").
3. AI adds context a scanner can't provide: **verification commands** (confirm the fix worked without a full rescan), **rollback instructions** (undo if the fix breaks something), **change window guidance** (safe to apply live vs. requires service restart), and **automation readiness** (safe to script vs. needs human review).
4. When the generic fix doesn't apply cleanly, **AI helps the engineer iterate** — adjusting the remediation for the specific environment, explaining what the fix does and why.
5. Engineer reviews and approves before remediation is applied. No auto-fixes.

**CI/CD integration**: Integrate the scan into the deployment pipeline — a server that fails baseline CIS checks doesn't get promoted to production. Shift compliance left.

[Source: Ansible docs, Dependabot workflow analogy, OpenSCAP oscap-ssh docs, demo implementation experience]

---

#### 4. Pros and cons of using LLMs vs. programmatic approaches, and key considerations?

| Dimension | Programmatic (oscap/scripts) | LLM-Based |
|---|---|---|
| **Accuracy** | Deterministic. Same input → same output. No hallucination. | Probabilistic. May hallucinate control IDs or give inconsistent results. |
| **Speed** | Fast at scale. Hundreds of servers in minutes. | Slower — inference latency, API rate limits. |
| **Maintainability** | Manual updates when benchmarks change, but explicit and version-controlled. | Can adapt to new benchmarks via prompts, but relies on training data which may be stale. |
| **Flexibility** | Rigid — only checks what it's programmed to. | Flexible — can interpret new controls and reason about novel configs. |
| **Auditability** | Fully auditable. Clear logic path per check. | Opaque. Not inspectable or reproducible. Hard to get audit sign-off. |
| **Cost** | Low. Open-source, runs on existing infra. | Higher. Per-token API costs or GPU infra for self-hosted. |
| **Edge cases** | Fails silently on unexpected configs (e.g., an `Include` directive in `sshd_config` that changes behaviour). | Can reason about context and catch subtle issues a rule-based check would miss — but may also introduce false positives. |

**Where each fits in the Dependabot-style pipeline:**

- **Programmatic (`oscap`)** does the scanning — this must be deterministic and auditable. Auditors need reproducible results. An LLM-generated compliance report won't pass scrutiny.
- **AI** adds value *after* the scan: triaging findings by risk, explaining *why* a control matters, identifying attack chains across findings, providing verification commands and rollback instructions, drafting the remediation MR description, and flagging context-dependent edge cases. In the demo, this turned 8 undifferentiated "medium" findings into 2 critical, 3 high, 2 medium, 1 low — with the 4 shadow/gshadow findings grouped as an attack chain.
- **The hybrid approach is optimal**: `oscap` is the source of truth, AI makes the output actionable and human-readable. Similar to the pattern at my work — deterministic extraction for the compliance-critical layer, LLM generation for the human-facing layer.
- **Never let an LLM be the sole source of truth** for a compliance determination.
- **AI must be grounded and evaluated** (Q5 principles in action): the architecture constrains AI input (XML only), validates AI output (grounding check — every rule it mentions must exist in the scan), and gates AI actions (human approval). The demo's `eval.py` scores this against known ground truth.

[Source: Experience building AI-powered systems at work with deterministic + LLM hybrid architecture]

---

### Case Study 2 — Scaling and Product Delivery

**Context**: Presenting the hardening-check tool to non-technical stakeholders, focusing on accuracy and flexibility.

---

#### 1. Presenting to non-technical stakeholders

Non-technical stakeholders care about **risk, cost, and business impact** — not config file syntax. Show, don't tell; use visuals, not jargon.

Structure around three questions:

**"What does this tool do?"**
"This tool automatically checks whether our servers are configured securely, based on industry-standard security guidelines (CIS Benchmarks). Think of it as an automated safety inspection for IT infrastructure — like a building inspector checking fire exits and electrical wiring."

**"How accurate is it?"**
Show a concrete comparison: run the tool on a sample server, have a senior engineer manually verify 10–15 controls, present results side-by-side. The tool produces identical results to manual review, but in seconds instead of hours. Use a dashboard showing green/amber/red status per server with a clear compliance percentage (e.g., “94% compliant across 50 servers”). Let stakeholders drill down per server.

The demo's UI shows this in practice: findings sorted by severity as MR-style cards, with findings **tagged ⬆ Upgraded when the AI rates them higher** than the scanner alone — making it immediately visible where human attention is most needed. **Attack chains** surface compound threats (e.g., “4 file permission issues together expose password hashes”) that no single-finding report would highlight.

If the tool includes an LLM component, be transparent: "The AI helps explain findings in plain English and suggests fixes, but every compliance determination is made by deterministic checks, not AI guesswork. The AI is the interpreter, not the inspector."

**"How flexible is it?"**
Demo: adding a new server in under a minute, switching compliance profiles (CIS Level 1 vs. Level 2), generating filtered reports. Same tool works across RHEL versions and can extend to other OSes.

**Avoid**: technical jargon, individual control deep-dives, live terminal demos with raw CLI output.

[Source: I've presented technical work to non-technical audiences — including an AI-powered visual checkout system for BreadTalk using live demos and Figma prototypes]

---

#### 2. Considerations for scaling in the future

The demo proves the pipeline works end-to-end with real SSH-based scanning and AI triage (8 failures detected, 5 re-prioritised by AI, 1 attack chain identified). Scaling to production:

| Area | Problem | Solution | Scale path |
|---|---|---|---|
| **Server access** | Demo uses SSH within containers | Ansible fans out via SSH, one inventory line per server | Ansible → Tower/AWX → Red Hat Satellite (native OpenSCAP) |
| **Scheduling** | Scan on boot + manual /rescan | Cron or Tower scheduler for recurring scans | Drift detection: compare current vs. last state, alert on changes |
| **Data** | Results in container filesystem | PostgreSQL/Elasticsearch with retention policies | Feeds into SIEM/GRC, enables queries like "all servers failing control 5.2.5 in last 30 days" |
| **AI reliability** | Mock triage or single LLM call | Ground-truth test sets, grounding checks, severity scoring | Monitor LLM quality drift over time; eval pipeline runs on every model update |
| **Access control** | Single user | RBAC: DB team sees their servers, networking sees theirs, leadership sees aggregate | Tower/AWX provides this natively |
| **OS diversity** | Rocky 9 only | Multiple CIS profiles + OS-specific SCAP content per target | CIS K8s Benchmark for containers; cloud APIs (SSM, Arc) for cloud-native |

The scaling path is incremental: **cron + Ansible → Tower/AWX → Satellite**, each step adding scheduling, RBAC, and credential management. The AI/eval layer scales independently — same grounding checks, just more data to validate against.

[Source: Ansible docs, Red Hat Satellite docs, general infrastructure scaling patterns, demo implementation experience]

