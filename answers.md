# IT Controls, Cybersecurity & AI Integration — Assessment

---

## Section 1: Foundational Knowledge

---

### 1. What is the purpose of system hardening in an enterprise environment, and why is it important?

System hardening is the process of reducing a system's attack surface by eliminating unnecessary software, services, user accounts, and configurations that an attacker could exploit. Think of it as locking every door and window in a building that nobody uses — the fewer entry points, the harder it is to break in.

In an enterprise environment, hardening is critical for several reasons. First, default installations of operating systems and applications ship with features turned *on* for convenience, not security. Services like Telnet, unused network daemons, or sample web applications often have known vulnerabilities. Removing or disabling them eliminates entire classes of risk before they can be exploited. Second, enterprises operate under regulatory and compliance frameworks (PCI-DSS, HIPAA, SOC 2, MAS-TRM in Singapore) that explicitly require systems to be configured to a security baseline. Non-compliance can result in financial penalties and reputational damage. Third, hardened systems are significantly easier to defend, monitor, and audit — they produce less noise in security logs, making anomalous behaviour easier to spot.

Practical hardening activities include: disabling unnecessary services and ports, enforcing strong password and account lockout policies, applying the principle of least privilege, enabling audit logging, removing default credentials, patching the operating system and applications, and configuring host-based firewalls. The goal is not to make a system invulnerable, but to make it *resilient* — forcing an attacker to work harder and increasing the likelihood that defensive tools detect the intrusion before damage is done.

---

### 2. Describe briefly the purpose of CIS Benchmarks and OpenSCAP.

**CIS Benchmarks** are consensus-based, best-practice security configuration guides published by the Center for Internet Security. They exist for hundreds of technologies — operating systems (RHEL, Windows Server, Ubuntu), cloud platforms (AWS, Azure), databases, web servers, and more. Each benchmark contains specific, actionable recommendations (e.g., "Ensure SSH root login is disabled") organised into scored and unscored items. Scored items are measurable and auditable; unscored items are advisory. Benchmarks are developed by communities of security professionals and are widely accepted as an industry-standard baseline, often referenced by auditors and regulators.

**OpenSCAP** is an open-source toolchain that *automates* the assessment of systems against security policies like CIS Benchmarks. It implements the Security Content Automation Protocol (SCAP) — a collection of standards including XCCDF (policy definition), OVAL (system testing), and CPE (platform identification). In practice, OpenSCAP takes a security profile (expressed as SCAP content, often provided by vendors like Red Hat via `scap-security-guide`), scans a target system, and produces a compliance report showing which checks passed, which failed, and suggested remediation steps.

The relationship between the two is straightforward: CIS Benchmarks define *what* should be checked, and OpenSCAP provides a *machine-readable, automatable way* to check it. Together, they enable enterprises to move from manual, error-prone audits to continuous, repeatable compliance validation.

---

### 3. How would you use a programming language like Python to automate a repetitive IT task?

Python is exceptionally well-suited for IT automation because of its readable syntax, extensive standard library, and rich ecosystem of third-party packages. A typical automation workflow follows four steps: **discover** what needs to be done, **implement** the logic, **schedule** execution, and **report** results.

**Example — Automating user account audits across Linux servers:**

1. **Discovery**: The task is to check all servers for dormant accounts (no login in 90+ days) and produce a report.
2. **Implementation**: Write a Python script that SSHs into each server (using `paramiko` or `fabric`), reads `/var/log/lastlog` or parses the output of `lastlog`, compares the last login timestamp against a 90-day threshold, and collects the results.
3. **Scheduling**: Deploy the script via `cron` (Linux) or a workflow orchestrator like Ansible Tower/AWX, Jenkins, or Apache Airflow to run weekly.
4. **Reporting**: Format findings into a CSV or HTML report using `pandas` and `jinja2`, then email it to the security team via `smtplib` or push it to a Slack channel via a webhook.

Python's `subprocess` module lets you run shell commands, `os` and `pathlib` handle file operations, `re` handles text parsing, and libraries like `paramiko` (SSH), `requests` (HTTP), and `pywinrm` (Windows Remote Management) extend reach across the network. For configuration management at scale, Python underpins tools like Ansible, SaltStack, and Fabric — so learning Python directly translates to proficiency with enterprise automation platforms.

---

### 4. Share your understanding of web scraping / API functions, and how AI tools can use them.

**Web scraping** is the programmatic extraction of data from web pages by parsing their HTML structure. Tools like Python's `BeautifulSoup` and `Scrapy` navigate the DOM, locate elements by tag, class, or XPath, and extract text or attributes. Scraping is useful when data is publicly displayed on websites but not available through a structured interface.

**APIs (Application Programming Interfaces)** are the preferred, structured alternative. RESTful APIs expose data as JSON or XML over HTTP endpoints. You send a request (`GET /api/v1/servers?status=active`), and receive a predictable, well-documented response. APIs are more reliable, faster, and less brittle than scraping because they are designed to be consumed programmatically.

**How AI tools leverage these capabilities:**

- **Data ingestion**: AI agents can call APIs to pull real-time data (threat intelligence feeds, vulnerability databases like NVD, cloud inventory APIs) and reason about it in context. For instance, an AI assistant could query the Shodan API, retrieve exposed services for an organisation's IP range, and summarise the findings.
- **Tool use / function calling**: Modern LLMs support "tool use" — the model outputs a structured function call (e.g., `search_vulnerabilities(cve_id="CVE-2024-1234")`), an orchestration layer executes it against an API, and the result is fed back to the model for interpretation. This is how AI agents interact with the real world without hallucinating data.
- **Web scraping as fallback**: When no API exists, AI-powered agents can use web scraping (often via headless browsers like Playwright) to gather information, but this is less reliable and raises ethical and legal considerations around terms of service and rate limiting.
- **Retrieval-Augmented Generation (RAG)**: Combining API/scraping output with LLM reasoning enables grounded, up-to-date responses. Instead of relying solely on training data, the AI retrieves current facts and synthesises an answer.

The key distinction is that APIs provide **structured, sanctioned access** while scraping is **unstructured and fragile**. AI tools should prefer APIs wherever available, falling back to scraping only when necessary and with appropriate safeguards.

---

### 5. What are the main considerations to test / validate an AI tool's response for accuracy (hallucinations, etc.)?

Hallucination — where an AI generates plausible-sounding but factually incorrect output — is one of the most significant risks when deploying AI in security-sensitive contexts. Validation requires a multi-layered approach:

**1. Ground truth comparison**: The most reliable method. Compare the AI's output against a known-correct source. For compliance checks, this means running the same check both programmatically (e.g., a shell command that reads `/etc/ssh/sshd_config`) and via the AI, then comparing results. Any divergence is a hallucination or reasoning error.

**2. Source attribution and traceability**: Require the AI to cite where it found each claim. If it references a CIS Benchmark control, verify that control actually exists and says what the AI claims. Tools with Retrieval-Augmented Generation (RAG) can be configured to return source passages alongside answers, making verification easier.

**3. Structured output validation**: Instead of free-text responses, constrain the AI to return structured formats (JSON with defined schemas). This makes it possible to programmatically validate outputs — for example, checking that a listed CVE ID matches the format `CVE-YYYY-NNNNN` and exists in the NVD.

**4. Consistency checks (self-verification)**: Run the same query multiple times or rephrase it. If the AI gives contradictory answers across runs, at least one is wrong. Ensemble approaches — asking multiple models and comparing — can also surface disagreements.

**5. Human-in-the-loop review**: For high-stakes decisions (remediation actions, compliance sign-off), always have a qualified human review the AI's output before action is taken. AI should *assist* decision-making, not replace it, especially when the cost of error is high.

**6. Confidence calibration**: Some AI systems can express uncertainty. If a model says "I'm not sure about this configuration," that signal should be taken seriously. Fine-tuned or well-prompted models can be trained to say "I don't know" rather than guess.

**7. Adversarial testing**: Deliberately feed the AI edge cases, ambiguous inputs, or intentionally misleading prompts to see if it produces incorrect output. This is analogous to penetration testing but for the AI itself.

In summary: never trust AI output blindly in security contexts. Validate programmatically where possible, require citations, use structured outputs, and keep humans in the loop for consequential decisions.

---

## Section 2: Case Studies

---

### Case Study 1 — Automating System Security Checks

**Context**: Building a tool to automate CIS Benchmark hardening checks for RHEL servers, evaluating AI vs. programmatic approaches.

*Information sources: CIS Benchmark documentation, Red Hat SCAP Security Guide documentation, OpenSCAP project documentation, NIST SCAP standards, and practical experience with configuration compliance tooling.*

---

#### 1. How would your tool check server settings? Any security considerations?

The tool would check server settings by executing targeted queries against system configuration files, running state, and kernel parameters. Concretely, this means:

**Configuration file inspection**: Parsing files like `/etc/ssh/sshd_config`, `/etc/login.defs`, `/etc/pam.d/*`, `/etc/sysctl.conf`, and `/etc/fstab` to verify expected values. For example, to check that SSH root login is disabled, the tool reads the `PermitRootLogin` directive and verifies it is set to `no`.

**Command output parsing**: Some checks require querying live system state — e.g., `systemctl is-enabled firewalld` to verify the firewall is active, `rpm -q` to check installed packages, or `auditctl -l` to verify audit rules are loaded.

**File permission and ownership checks**: Using `stat` to verify permissions on sensitive files like `/etc/shadow` (expected: `0000` or `0640`) and `/etc/passwd` (expected: `0644`).

**Security considerations for the tool itself are paramount:**

- **Least privilege**: The tool needs read access to system configurations but should *not* run as root unless absolutely necessary. Where root is required (e.g., reading `/etc/shadow` permissions), use `sudo` with a tightly scoped sudoers policy that limits which commands the tool account can execute.
- **Transport security**: If the tool connects remotely (SSH), enforce key-based authentication only — never store passwords in scripts or configuration files. SSH keys should be passphrase-protected and rotated regularly.
- **Output handling**: Compliance reports may contain sensitive information about system configurations. Store and transmit them encrypted. Restrict access to reports to authorised personnel only.
- **Integrity of the tool itself**: The scanning scripts should be version-controlled, code-reviewed, and stored in a tamper-evident repository. If an attacker modifies the scanning tool, they can make a compromised system appear compliant.
- **No remediation without approval**: The tool should *report* non-compliance but not automatically fix it. Auto-remediation can cause outages (e.g., disabling a service that a production application depends on). Remediation should go through change management.

---

#### 2. How would your tool verify compliance with CIS Benchmarks?

The tool would map each CIS Benchmark recommendation to a discrete, automatable check and evaluate pass/fail against the benchmark's expected value. There are two viable approaches:

**Approach A — Leverage OpenSCAP with SCAP Security Guide (recommended for production)**

Red Hat ships the `scap-security-guide` package, which contains pre-built SCAP profiles that directly map to CIS Benchmark Level 1 and Level 2 for RHEL. The tool would:

1. Install `openscap-scanner` and `scap-security-guide` on the target server.
2. Run: `oscap xccdf eval --profile cis --results results.xml --report report.html /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml`
3. Parse the XCCDF results XML to extract pass/fail status for each control.
4. Map each result to the corresponding CIS Benchmark control ID for reporting.

This approach is battle-tested, maintained by Red Hat, and produces auditor-ready reports.

**Approach B — Custom checks mapped to CIS controls**

For more flexibility or when OpenSCAP is not available, the tool can implement checks directly. This requires maintaining a mapping file (e.g., YAML or JSON) that links each CIS control to a specific check:

```yaml
- cis_id: "5.2.5"
  title: "Ensure SSH root login is disabled"
  check_type: "config_file"
  file: "/etc/ssh/sshd_config"
  key: "PermitRootLogin"
  expected: "no"
  
- cis_id: "1.4.1"
  title: "Ensure permissions on bootloader config are configured"
  check_type: "file_permissions"
  file: "/boot/grub2/grub.cfg"
  expected_mode: "0600"
  expected_owner: "root"
```

The tool reads this mapping, runs each check, and produces a structured compliance report. The trade-off is that this mapping must be updated manually whenever a new CIS Benchmark version is released, whereas the SCAP Security Guide is maintained by the community.

---

#### 3. How would you automate this?

Automation involves three layers: **execution**, **orchestration**, and **reporting**.

**Execution layer (the scanner)**:
A Python script (or set of scripts) that performs the actual checks. The script accepts a configuration file defining which CIS profile to evaluate, connects to one or more target servers (locally or via SSH), runs the checks, and outputs structured results (JSON or XML).

**Orchestration layer (scheduling and multi-server coordination)**:
Wrap the scanner in an automation framework:

- **Ansible** is the natural choice for RHEL environments. Write an Ansible playbook that deploys the scanner, runs it on all target hosts in the inventory, and collects results back to a central location. Ansible is agentless (uses SSH), aligns with the Red Hat ecosystem, and scales easily.
- For recurring scans, schedule the playbook via **Ansible Tower/AWX**, **Jenkins**, or **cron** to run daily or weekly.
- Store results in a central database (PostgreSQL, Elasticsearch) for historical trending.

**Reporting layer (dashboards and alerts)**:
- Parse scan results and generate summary reports (per-server pass rates, most-commonly-failed controls, trend over time).
- Visualise in a dashboard (Grafana, Kibana, or a custom web UI).
- Send alerts (email, Slack, PagerDuty) when a server drops below a compliance threshold — e.g., "Server prod-db-01 is at 78% CIS compliance, down from 95% yesterday."

**CI/CD integration**: For newly provisioned servers, integrate the compliance scan into the deployment pipeline. A server that fails the baseline CIS check does not get promoted to production. This is the "shift-left" approach to compliance — catch misconfigurations before they reach production.

---

#### 4. Pros and cons of using LLMs vs. programmatic approaches, and key considerations?

| Dimension | Programmatic Approach | LLM-Based Approach |
|---|---|---|
| **Accuracy** | Deterministic. Same input always produces same output. No hallucination risk. | Probabilistic. May hallucinate control IDs, misinterpret config syntax, or give inconsistent results across runs. |
| **Speed** | Very fast at scale. Can scan hundreds of servers in minutes via parallel execution. | Slower per-check due to inference latency. API rate limits can bottleneck large-scale scans. |
| **Maintainability** | Requires manual updates when benchmarks change, but changes are explicit and version-controlled. | Can adapt to new benchmarks with updated prompts, but "adapting" means relying on the model's training data, which may be outdated. |
| **Flexibility** | Rigid — only checks what it's programmed to check. Adding a new check requires code changes. | Highly flexible — can interpret natural-language descriptions of new controls and reason about novel configurations. |
| **Auditability** | Fully auditable. Every check has a clear, inspectable logic path. Auditors can trace exactly how a pass/fail was determined. | Opaque. An LLM's reasoning is not inspectable or reproducible, making audit sign-off difficult. |
| **Cost** | Low marginal cost. Open-source tools, runs on existing infrastructure. | Higher marginal cost. API calls incur per-token charges; self-hosted models require GPU infrastructure. |
| **Edge cases** | Fails silently on unexpected configs (e.g., an unusual `Include` directive in `sshd_config` that changes behaviour). | Can reason about context and catch subtle issues a regex-based check would miss, but may also introduce false positives/negatives. |

**Key considerations for choosing:**

- For **compliance reporting and audit evidence**, use the programmatic approach. Auditors need deterministic, reproducible results with clear audit trails. An LLM-generated compliance report would not pass scrutiny from a serious auditor.
- For **interpreting results, generating remediation guidance, and triaging findings**, LLMs add significant value. After the programmatic scan identifies failures, an LLM can explain *why* the control matters, draft a remediation playbook, or help prioritise which failures to address first based on the organisation's risk profile.
- The **hybrid approach** is optimal: use programmatic tools (OpenSCAP, custom scripts) for the actual compliance checks, and layer an LLM on top for interpretation, reporting in natural language, and interactive Q&A. This gets the best of both worlds — deterministic accuracy for the checks, and intelligent assistance for the human-facing layer.
- **Never let an LLM be the sole source of truth** for a compliance determination. Always validate LLM output against programmatic ground truth.

---

### Case Study 2 — Scaling and Product Delivery

**Context**: Presenting the hardening-check tool to non-technical stakeholders, focusing on accuracy and flexibility.

---

#### 1. Presenting to non-technical stakeholders

Non-technical stakeholders care about **risk, cost, and business impact** — not configuration file syntax. The presentation should translate technical compliance into business language.

**Structure the presentation around three questions:**

**"What does this tool do?"**
Frame it simply: "This tool automatically checks whether our servers are configured securely, based on industry-standard security guidelines (CIS Benchmarks). Think of it as an automated safety inspection for our IT infrastructure — the same way a building inspector checks fire exits and electrical wiring."

**"How accurate is it?"**
Show a concrete comparison. Take a sample server, run the automated tool, and separately have a senior engineer manually verify 10–15 controls. Present the results side-by-side in a simple table. Highlight that the tool produces *identical* results to manual review, but in seconds instead of hours. Use a visual: a dashboard screenshot showing green/amber/red status for each server, with a clear overall compliance percentage (e.g., "94% compliant across 50 servers").

If the tool includes an LLM component, be transparent: "The AI assistant helps explain findings in plain English and suggests fixes, but every compliance determination is made by deterministic checks, not by AI guesswork. The AI is the interpreter, not the inspector."

**"How flexible is it?"**
Demonstrate adaptability with a live or recorded demo showing: adding a new server to the scan in under a minute, switching from one compliance profile to another (e.g., CIS Level 1 vs. Level 2), and generating a report filtered by severity. Emphasise that the same tool works across different RHEL versions and can be extended to other operating systems with additional profiles.

**Avoid**: technical jargon (XCCDF, OVAL, SCAP), deep dives into individual controls, or live terminal demos with command-line output. Use visualisations, percentages, and business-impact framing throughout.

---

#### 2. Considerations for scaling in the future

Scaling from a single-server proof-of-concept to enterprise-wide deployment introduces several categories of challenge:

**Infrastructure and connectivity**: Scanning hundreds or thousands of servers requires efficient orchestration. Ansible's push-based model works well up to a few hundred hosts; beyond that, consider Ansible Tower/AWX with smart inventories, or tools like Red Hat Satellite which natively integrate OpenSCAP scanning at scale. For cloud-native environments, leverage cloud APIs (AWS SSM, Azure Arc) to execute scans without direct SSH.

**Performance and parallelism**: Sequential scanning does not scale. The tool must support parallel execution — running scans on multiple servers simultaneously. Ansible handles this with configurable `forks` (e.g., scanning 50 servers in parallel). For very large fleets, consider a distributed architecture where lightweight agents on each server perform the scan locally and report results to a central collector.

**Heterogeneous environments**: Real enterprises run diverse operating systems (RHEL 7, 8, 9; Ubuntu; Windows Server) and workloads (bare metal, VMs, containers, Kubernetes). The tool must support multiple CIS profiles and gracefully handle OS-specific differences. Container and Kubernetes hardening (CIS Kubernetes Benchmark) is a distinct domain that may require separate tooling.

**Drift detection and continuous compliance**: A one-time scan is insufficient. Servers drift from their baseline as changes are made. The scaled tool should run on a schedule (daily or more frequently), compare current state against the last known state, and alert on *changes* — not just failures. This transforms the tool from a point-in-time auditor to a continuous compliance monitor.

**Data management and retention**: At scale, each scan generates substantial data. Plan for structured storage (a database, not flat files), retention policies (how long to keep historical scans), and efficient querying (e.g., "show me all servers that failed control 5.2.5 in the last 30 days").

**Role-based access and multi-tenancy**: Different teams may own different servers. The scaled tool needs role-based access control so that the database team sees their servers' compliance, the networking team sees theirs, and leadership sees an aggregate view.

**Exception management**: Not every CIS control applies universally. Some servers have legitimate reasons for deviating from the benchmark (e.g., a legacy application that requires an older TLS version). The tool needs a formal exception/waiver workflow — a way to document "this server is intentionally non-compliant with control X because of reason Y, approved by person Z, expiring on date D."

**Integration with existing tooling**: The tool should feed into the organisation's existing security ecosystem — SIEM (Splunk, QRadar), GRC platforms (ServiceNow GRC, Archer), and ticketing systems (Jira, ServiceNow ITSM) — so that non-compliance findings automatically become trackable work items with owners and deadlines.

---

*Document prepared with a focus on practical, implementable guidance. Technical depth is calibrated for a reader with a cybersecurity and data science background, while maintaining clarity for cross-functional communication.*