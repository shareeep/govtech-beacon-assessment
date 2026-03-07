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

**Overall approach**: Keep it simple. The tool works like **Dependabot, but for CIS Benchmarks on RHEL servers** — it scans, identifies non-compliance, and generates change requests (MRs/PRs) with remediation for engineers to review and approve before anything is applied.

---

#### 1. How would your tool check server settings? Any security considerations?

I would use **OpenSCAP** (`oscap`) as the scanning engine. It handles querying system configuration files, checking running state, and evaluating kernel parameters against a defined security profile — no need to write custom parsers.

```bash
oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis \
  --results results.xml \
  --report report.html \
  /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml
```

This produces an HTML report with pass/fail for each CIS control, plus remediation snippets (Ansible/shell) for each failure.

The output needs to be verified:

- Results should be **spot-checked by a senior engineer/sysadmin** familiar with the environment, especially for the first few runs.
- A flagged "failure" may be an intentional deviation — e.g., a legacy app requiring an older TLS version. Context matters.
- The compliance report should be reviewed with the infrastructure team before acting on findings.

**Security considerations for the tool itself:**

- **Least privilege**: Read access to configs only. Where root is required, use `sudo` with a tightly scoped policy.
- **Transport security**: If connecting remotely (SSH), key-based auth only — never store passwords in scripts.
- **Output handling**: Reports contain sensitive configuration details. Store encrypted, restrict access to authorised personnel.
- **No auto-remediation**: The tool *reports* non-compliance, it doesn't fix it. Remediation goes through change management — like a PR that needs approval before merge.

[Source: OpenSCAP project docs, CIS Benchmark documentation, tested locally with Rocky Linux 9 container]

---

#### 2. How would your tool verify compliance with CIS Benchmarks?

Use **OpenSCAP with SCAP Security Guide**. Red Hat ships `scap-security-guide` with pre-built CIS profiles (Level 1, Level 2) that translate the CIS PDF recommendations into machine-readable SCAP rules. The profiles are automatically available after install — no separate download.

**How it works:**

1. Install `openscap-scanner` + `scap-security-guide` on the target.
2. Select the appropriate CIS profile — the package bundles profiles matched to the OS version (e.g., `ssg-rhel9-ds.xml` for RHEL 9). Choose L1 (essential baseline, most production servers) or L2 (stricter, for high-security/regulated environments).
3. `oscap` evaluates each CIS control against actual system state — checking config files, service states, file permissions, kernel parameters, etc.
4. Outputs: machine-readable XML (for automation) + human-readable HTML report with pass/fail per CIS control ID + remediation snippets (Ansible/shell).

This is battle-tested, community-maintained, and produces auditor-ready reports. The alternative — writing custom checks mapped to each CIS control — is possible but means manually maintaining the mapping every time CIS releases a new version. SCAP Security Guide handles that for you.

[Source: Red Hat SCAP Security Guide docs, OpenSCAP project docs, CIS Benchmarks FAQ, tested locally with Rocky Linux 9 container]

---

#### 3. How would you automate this?

Three layers: **scan**, **orchestrate**, **report**.

**Scan**: `oscap` runs against each server and outputs results (XML) + report (HTML) with remediation snippets.

**Orchestrate**: Use **Ansible** to run the scan across all RHEL hosts — it's agentless (SSH), aligns with the Red Hat ecosystem, scales easily. A playbook deploys the scanner to all hosts in inventory, executes in parallel, and collects results centrally. Schedule recurring scans via **cron** or **Ansible Tower/AWX**.

**Report + Monitor**: Store results in a database (Elasticsearch/PostgreSQL) for trending. Visualise in **Grafana/Kibana** — per-server compliance percentages, most-failed controls, trends over time. Set up **alerts** (Slack, PagerDuty) when compliance drops — e.g., "prod-db-01 at 78% CIS compliance, down from 95%." This gives the team a live view of fleet security posture.

**Remediate (the Dependabot analogy)**: This is where AI adds practical value. The `oscap` report already provides Ansible/shell remediation snippets for each failure — but these are generated for a generic RHEL install. In practice, they won't always work first try: custom paths, conflicting services, environment-specific dependencies. So:

1. For each actionable failure, **generate a change request** (MR/PR) containing the remediation snippet from `oscap`.
2. AI triages findings — prioritises by severity, flags context-dependent issues (e.g., "this server runs a legacy app, disabling TLS 1.0 might break it").
3. When the generic fix doesn't apply cleanly, **AI helps the engineer iterate** — adjusting the remediation for the specific environment, explaining what the fix does and why.
4. Engineer reviews and approves before remediation is applied. No auto-fixes.

**CI/CD integration**: Integrate the scan into the deployment pipeline — a server that fails baseline CIS checks doesn't get promoted to production. Shift compliance left.

[Source: Ansible docs, Dependabot workflow analogy, general DevOps/CI pipeline patterns]

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

**Where each fits in the Dependabot-style pipeline:**

- **Programmatic (`oscap`)** does the scanning — this must be deterministic and auditable. Auditors need reproducible results. An LLM-generated compliance report won't pass scrutiny.
- **AI** adds value *after* the scan: triaging findings by risk, explaining *why* a control matters, drafting the remediation MR description, and flagging context-dependent edge cases.
- **The hybrid approach is optimal**: `oscap` is the source of truth, AI makes the output actionable and human-readable. Similar to the pattern at my work — deterministic extraction for the compliance-critical layer, LLM generation for the human-facing layer.
- **Never let an LLM be the sole source of truth** for a compliance determination.

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
Show a concrete comparison: run the tool on a sample server, have a senior engineer manually verify 10–15 controls, present results side-by-side. The tool produces identical results to manual review, but in seconds instead of hours. Use a dashboard (Grafana) showing green/amber/red status per server with a clear compliance percentage (e.g., "94% compliant across 50 servers"). Let stakeholders drill down per server.

If the tool includes an LLM component, be transparent: "The AI helps explain findings in plain English and suggests fixes, but every compliance determination is made by deterministic checks, not AI guesswork. The AI is the interpreter, not the inspector."

**"How flexible is it?"**
Demo: adding a new server in under a minute, switching compliance profiles (CIS Level 1 vs. Level 2), generating filtered reports. Same tool works across RHEL versions and can extend to other OSes.

**Avoid**: technical jargon, individual control deep-dives, live terminal demos with raw CLI output.

[Source: I've presented technical work to non-technical audiences — including an AI-powered visual checkout system for BreadTalk using live demos and Figma prototypes]

---

#### 2. Considerations for scaling in the future

Scaling from proof-of-concept to enterprise-wide centres on four pillars:

**1. Infrastructure orchestration**: Ansible's push model works up to a few hundred hosts. Beyond that, scale with **Ansible Tower/AWX** (smart inventories, role-based scheduling) or **Red Hat Satellite** which natively integrates OpenSCAP. For cloud-native environments, use cloud APIs (AWS SSM, Azure Arc) to scan without direct SSH. Ansible's `forks` enable parallel execution; for very large fleets, a distributed agent model (each server scans locally, reports to central collector) is more efficient.

**2. Continuous compliance and drift detection**: Servers drift from baseline as changes are made. The tool should run on schedule, compare current state against last known state, and alert on *changes* — not just failures. This transforms it from point-in-time auditor to continuous compliance monitor. Also needs a formal **exception/waiver workflow** for legitimate deviations — documenting what, why, who approved, and when it expires.

**3. Data management and ecosystem integration**: At scale, each scan generates substantial data. Need structured storage (database, not flat files), retention policies, and efficient querying (e.g., "all servers that failed control 5.2.5 in the last 30 days"). Compliance data should feed into existing SIEM, GRC platforms, and ticketing systems so findings become trackable work items. Role-based access ensures each team sees their servers while leadership gets aggregate views.

**4. Heterogeneous environments**: Enterprises run diverse OS (RHEL 7/8/9, Ubuntu, Windows Server) across bare metal, VMs, containers, and Kubernetes. Must support multiple CIS profiles and OS-specific differences. Container/Kubernetes hardening (CIS Kubernetes Benchmark) may require separate tooling.

[Source: Ansible docs, Red Hat Satellite docs, general infrastructure scaling patterns]

