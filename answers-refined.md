# IT Controls, Cybersecurity & AI Integration — Assessment

---

## Section 1: Foundational Knowledge

---

### 1. What is the purpose of system hardening in an enterprise environment, and why is it important?

System hardening is the process of reducing a system's attack surface by eliminating unnecessary software, services, user accounts, and configurations that an attacker could exploit. Think of it as locking every door and window in a building that nobody uses — the fewer entry points, the harder it is to break in.

In an enterprise environment, hardening is critical for several reasons. First, default installations of operating systems and applications ship with features turned *on* for convenience, not security. Services like Telnet, unused network daemons, or sample web applications often have known vulnerabilities. Removing or disabling them eliminates entire classes of risk before they can be exploited. Second, enterprises operate under regulatory and compliance frameworks (PCI-DSS, HIPAA, SOC 2, MAS-TRM in Singapore) that explicitly require systems to be configured to a security baseline. Non-compliance can result in financial penalties and reputational damage. Third, hardened systems are significantly easier to defend, monitor, and audit — they produce less noise in security logs, making anomalous behaviour easier to spot.

Practical hardening activities include: disabling unnecessary services and ports, enforcing strong password and account lockout policies, applying the principle of least privilege, enabling audit logging, removing default credentials, patching the operating system and applications, and configuring host-based firewalls. In a cloud-native context, this also extends to infrastructure-level controls — for example, in a university project where I migrated a system to Azure Kubernetes Service (ESMOS — Cloud Migration), hardening meant configuring Network Security Group rules to restrict traffic to only required ports, enforcing RBAC for cluster access, and enabling HTTPS via automated certificate management. The goal is not to make a system invulnerable, but to make it *resilient* — forcing an attacker to work harder and increasing the likelihood that defensive tools detect the intrusion before damage is done.

---

### 2. Describe briefly the purpose of CIS Benchmarks and OpenSCAP.

**CIS Benchmarks** are best-practice security configuration guides published by the Center for Internet Security. They cover hundreds of technologies — operating systems (RHEL, Windows Server, Ubuntu), cloud platforms (AWS, Azure), databases, and more. Each benchmark contains specific, actionable recommendations (e.g., "Ensure SSH root login is disabled") organised into scored and unscored items. Scored items are measurable and auditable; unscored items are advisory. Benchmarks are developed by communities of security professionals and are widely accepted as an industry-standard baseline, often referenced by auditors and regulators.

**OpenSCAP** is an open-source toolchain that *automates* the assessment of systems against security policies like CIS Benchmarks. It takes a security profile (often provided by vendors like Red Hat via the `scap-security-guide` package), scans a target system, and produces a compliance report showing which checks passed, which failed, and suggested remediation steps. Under the hood, it uses a set of standards collectively called SCAP (Security Content Automation Protocol) that define how policies, tests, and platform identifiers are expressed in machine-readable formats.

The relationship between the two is straightforward: CIS Benchmarks define *what* should be checked, and OpenSCAP provides an *automatable way* to check it. Together, they enable enterprises to move from manual, error-prone audits to continuous, repeatable compliance validation. This concept of "automated compliance against a defined baseline" is something I've applied in other contexts — for instance, in my ESMOS cloud migration project, we established a security baseline (HTTPS, RBAC, network rules) and verified it through our DevSecOps pipeline, which follows the same philosophy even though the tooling was different.

---

### 3. How would you use a programming language like Python to automate a repetitive IT task?

Python is exceptionally well-suited for IT automation because of its readable syntax, extensive standard library, and rich ecosystem of third-party packages. A typical automation workflow follows four steps: **discover** what needs to be done, **implement** the logic, **schedule** execution, and **report** results.

I've applied this pattern across several projects:

**Example 1 — Automating data pipeline quality checks at scale (Aircraft Delay Propagation — Big Data on AWS):**

In a big data project processing over 120 million flight records, I used Python (PySpark) to automate the entire ETL pipeline on AWS. The workflow mapped directly to the four-step pattern: *discovery* involved using AWS Glue to automatically catalogue and infer schemas from raw CSV files in S3; *implementation* was PySpark jobs on EMR that cleaned, joined, and transformed flight, aircraft, and weather data; *scheduling* was handled through EMR cluster orchestration; and *reporting* used Athena SQL queries to validate outputs and surface insights. Without Python automation, manually processing 120M+ records would have been infeasible.

**Example 2 — Automating CI/CD test execution (Agile Software Project Management):**

As Scrum Master on a microservices project, I set up a two-layer automated testing pipeline using Python. Locally, pre-push Git hooks ran `pytest` only on changed Flask services — so developers got fast feedback without running the entire test suite. On push, GitHub Actions triggered parallel test execution across 14 microservices, plus linting and Gitleaks secret scanning. This automation enforced 70% code coverage across 11 services and caught regressions before they reached the main branch.

Python's `subprocess` module lets you run shell commands, `os` and `pathlib` handle file operations, `re` handles text parsing, and libraries like `paramiko` (SSH), `requests` (HTTP), and `pywinrm` (Windows Remote Management) extend reach across the network. For configuration management at scale, Python underpins tools like Ansible, SaltStack, and Fabric — so learning Python directly translates to proficiency with enterprise automation platforms.

---

### 4. Share your understanding of web scraping / API functions, and how AI tools can use them.

**Web scraping** is the programmatic extraction of data from web pages by parsing their HTML structure. Tools like Python's `BeautifulSoup` and `Scrapy` navigate the page, locate elements by tag or class, and extract text or attributes. Scraping is useful when data is publicly displayed on websites but not available through a structured interface.

**APIs (Application Programming Interfaces)** are the preferred, structured alternative. RESTful APIs expose data as JSON or XML over HTTP endpoints. You send a request (e.g., `GET /api/v1/servers?status=active`), and receive a predictable, well-documented response. APIs are more reliable, faster, and less brittle than scraping because they are designed to be consumed programmatically. I've worked extensively with APIs across several projects — for instance, integrating **Stripe Connect's API** for split payments in a food delivery platform (CampusG), consuming the **Google Maps and OneMap APIs** for location-based features in a social app (PetConnect), and querying the **WHOIS API** to extract domain registration data as features for a phishing URL detection model.

**How AI tools leverage these capabilities:**

- **Data ingestion**: AI agents can call APIs to pull real-time data (threat intelligence feeds, vulnerability databases, cloud inventory APIs) and reason about it in context. For instance, an AI assistant could query a vulnerability database API, retrieve known exploits for a specific software version, and summarise the findings.
- **Tool use / function calling**: Modern LLMs support "tool use" — the model outputs a structured function call (e.g., `search_vulnerabilities(cve_id="CVE-2024-1234")`), an orchestration layer executes it against an API, and the result is fed back to the model for interpretation. This is how AI agents interact with the real world without hallucinating data. In my current internship at HTX, I work on a system that uses **Model Context Protocol (MCP)** — agent-facing automation contracts that let an AI agent create, validate, and upload procurement reports through structured API calls. This is tool use in a production government context.
- **Web scraping as fallback**: When no API exists, AI-powered agents can use web scraping (often via headless browsers like Playwright) to gather information, but this is less reliable and raises ethical/legal considerations around terms of service and rate limiting.
- **Retrieval-Augmented Generation (RAG)**: Combining API/scraping output with LLM reasoning enables grounded, up-to-date responses. Instead of relying solely on training data, the AI retrieves current facts and synthesises an answer. I've implemented this pattern in a PII anonymisation project, where a retrieval pipeline feeds context to an LLM for domain-specific text anonymisation.

The key distinction is that APIs provide **structured, sanctioned access** while scraping is **unstructured and fragile**. AI tools should prefer APIs wherever available, falling back to scraping only when necessary and with appropriate safeguards.

---

### 5. What are the main considerations to test / validate an AI tool's response for accuracy (hallucinations, etc.)?

Hallucination — where an AI generates plausible-sounding but factually incorrect output — is one of the most significant risks when deploying AI in security-sensitive contexts. This is an area I've worked on directly: at my current internship at HTX, I help build anti-hallucination controls into an AI-powered government procurement system, and in an academic project on AI safety, I've evaluated LLM bias and reliability in resume screening. Validation requires a multi-layered approach:

**1. Ground truth comparison**: The most reliable method. Compare the AI's output against a known-correct source. For compliance checks, this means running the same check both programmatically (e.g., a shell command that reads a config file) and via the AI, then comparing results. Any divergence is a hallucination or reasoning error. In my hate speech classification project, I validated fine-tuned model outputs against the HateXplain benchmark dataset — the same principle of measuring predictions against established ground truth.

**2. Source attribution and traceability**: Require the AI to cite where it found each claim. If it references a CIS Benchmark control, verify that control actually exists and says what the AI claims. RAG-based tools can be configured to return source passages alongside answers, making verification easier. At HTX, our system uses **hybrid semantic + keyword retrieval with reranking** to ensure that generated reports are grounded in actual source documents rather than fabricated content.

**3. Structured output validation**: Instead of free-text responses, constrain the AI to return structured formats (JSON with defined schemas). This makes it possible to programmatically validate outputs — for example, checking that a listed CVE ID follows the expected format and exists in a vulnerability database. At HTX, we use **strict output contracts** for deterministic extraction — the LLM must produce outputs that conform to a defined schema, which can be validated automatically before reaching the user.

**4. Consistency checks (self-verification)**: Run the same query multiple times or rephrase it. If the AI gives contradictory answers across runs, at least one is wrong. Ensemble approaches — asking multiple models and comparing — can also surface disagreements. In my AI safety research on resume screening, I test the same resumes across five different models (GPT, Claude, DeepSeek, Mistral, LLaMA) to identify where models diverge, revealing systematic biases and inconsistencies.

**5. Human-in-the-loop review**: For high-stakes decisions (remediation actions, compliance sign-off), always have a qualified human review the AI's output before action is taken. AI should *assist* decision-making, not replace it, especially when the cost of error is high. At HTX, the frontend includes **report guards and guardrails** that require human review and approval before AI-generated procurement reports are finalised.

**6. Confidence calibration**: Some AI systems can express uncertainty. If a model says "I'm not sure about this configuration," that signal should be taken seriously. Well-prompted models can be guided to say "I don't know" rather than guess.

**7. Adversarial testing**: Deliberately feed the AI edge cases, ambiguous inputs, or intentionally misleading prompts to see if it produces incorrect output. This is analogous to penetration testing but for the AI itself. In my PII anonymisation project, I used an adversarial multi-agent workflow where one agent attempts to re-identify anonymised text and feeds failures back to the anonymisation agent — pushing the system to 97% anonymisation accuracy through iterative challenge and improvement.

In summary: never trust AI output blindly in security contexts. Validate programmatically where possible, require citations, use structured outputs, and keep humans in the loop for consequential decisions.

---

## Section 2: Case Studies

---

### Case Study 1 — Automating System Security Checks

**Context**: Building a tool to automate CIS Benchmark hardening checks for RHEL servers, evaluating AI vs. programmatic approaches.

*Information sources: CIS Benchmark documentation, Red Hat SCAP Security Guide documentation, OpenSCAP project documentation, NIST SCAP standards, and practical experience with configuration compliance tooling and DevSecOps pipelines.*

---

#### 1. How would your tool check server settings? Any security considerations?

The tool would check server settings by executing targeted queries against system configuration files, running state, and kernel parameters. Concretely, this means:

**Configuration file inspection**: Parsing files like `/etc/ssh/sshd_config`, `/etc/login.defs`, `/etc/pam.d/*`, `/etc/sysctl.conf`, and `/etc/fstab` to verify expected values. For example, to check that SSH root login is disabled, the tool reads the `PermitRootLogin` directive and verifies it is set to `no`.

**Command output parsing**: Some checks require querying live system state — e.g., `systemctl is-enabled firewalld` to verify the firewall is active, `rpm -q` to check installed packages, or `auditctl -l` to verify audit rules are loaded. This is conceptually similar to what I did in my ESMOS cloud migration project, where our monitoring stack (Prometheus + Grafana) continuously queried pod health and resource utilisation to verify the system was operating within expected parameters.

**File permission and ownership checks**: Using `stat` to verify permissions on sensitive files like `/etc/shadow` (expected: `0000` or `0640`) and `/etc/passwd` (expected: `0644`).

**Security considerations for the tool itself are paramount:**

- **Least privilege**: The tool needs read access to system configurations but should *not* run as root unless absolutely necessary. Where root is required, use `sudo` with a tightly scoped policy that limits which commands the tool account can execute.
- **Transport security**: If the tool connects remotely (SSH), enforce key-based authentication only — never store passwords in scripts or configuration files. SSH keys should be passphrase-protected and rotated regularly.
- **Output handling**: Compliance reports may contain sensitive information about system configurations. Store and transmit them encrypted. Restrict access to reports to authorised personnel only.
- **Integrity of the tool itself**: The scanning scripts should be version-controlled, code-reviewed, and stored in a tamper-evident repository. If an attacker modifies the scanning tool, they can make a compromised system appear compliant. In my Agile software project, we integrated **Gitleaks** into our CI pipeline to automatically scan for accidentally committed secrets — applying the same principle of protecting the toolchain itself.
- **No remediation without approval**: The tool should *report* non-compliance but not automatically fix it. Auto-remediation can cause outages (e.g., disabling a service that a production application depends on). Remediation should go through change management.
- **Drift detection**: Beyond one-time checks, the tool should compare current state against a known-good baseline stored in version control and flag any changes. In my ESMOS project, our infrastructure was defined as version-controlled YAML, making it straightforward to detect when the live environment drifted from the intended configuration.

---

#### 2. How would your tool verify compliance with CIS Benchmarks?

The tool would map each CIS Benchmark recommendation to a discrete, automatable check and evaluate pass/fail against the benchmark's expected value. There are two viable approaches:

**Approach A — Leverage OpenSCAP with SCAP Security Guide (recommended for production)**

Red Hat ships the `scap-security-guide` package, which contains pre-built security profiles that directly map to CIS Benchmark Level 1 and Level 2 for RHEL. The tool would:

1. Install `openscap-scanner` and `scap-security-guide` on the target server.
2. Run the OpenSCAP scanner against the CIS profile, which evaluates the system and produces both machine-readable results (XML) and a human-readable report (HTML).
3. Parse the results to extract pass/fail status for each control.
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

Automation involves three layers: **execution**, **orchestration**, and **reporting**. This layered approach mirrors patterns I've used in other projects — for instance, my big data project on AWS had a similar structure: PySpark jobs for execution, AWS Glue + EMR for orchestration, and Athena for reporting/validation.

**Execution layer (the scanner)**:
A Python script (or set of scripts) that performs the actual checks. The script accepts a configuration file defining which CIS profile to evaluate, connects to one or more target servers (locally or via SSH), runs the checks, and outputs structured results (JSON or XML).

**Orchestration layer (scheduling and multi-server coordination)**:
Wrap the scanner in an automation framework:

- **Ansible** is the natural choice for RHEL environments. Write an Ansible playbook that deploys the scanner, runs it on all target hosts in the inventory, and collects results back to a central location. Ansible is agentless (uses SSH), aligns with the Red Hat ecosystem, and scales easily.
- For recurring scans, schedule the playbook via **Ansible Tower/AWX**, **Jenkins**, or **cron** to run daily or weekly.
- Store results in a central database (PostgreSQL, Elasticsearch) for historical trending.

This is similar to how I orchestrated distributed workflows in my CampusG food delivery project, where **Temporal** and **Kafka** coordinated operations across multiple microservices — the same principle of a central orchestrator dispatching work to distributed nodes and collecting results applies here.

**Reporting layer (dashboards and alerts)**:
- Parse scan results and generate summary reports (per-server pass rates, most-commonly-failed controls, trend over time).
- Visualise in a dashboard (Grafana, Kibana, or a custom web UI). I've set up Grafana dashboards in my ESMOS project for infrastructure monitoring — the same approach extends naturally to compliance monitoring.
- Send alerts (email, Slack, PagerDuty) when a server drops below a compliance threshold — e.g., "Server prod-db-01 is at 78% CIS compliance, down from 95% yesterday."

**CI/CD integration**: For newly provisioned servers, integrate the compliance scan into the deployment pipeline. A server that fails the baseline CIS check does not get promoted to production. This "shift-left" approach to compliance is something I applied in my Agile project, where automated tests and security scans (including Gitleaks) ran as part of the CI pipeline — code that failed quality or security checks was blocked from merging.

---

#### 4. Pros and cons of using LLMs vs. programmatic approaches, and key considerations?

| Dimension | Programmatic Approach | LLM-Based Approach |
|---|---|---|
| **Accuracy** | Deterministic. Same input always produces same output. No hallucination risk. | Probabilistic. May hallucinate control IDs, misinterpret config syntax, or give inconsistent results across runs. |
| **Speed** | Very fast at scale. Can scan hundreds of servers in minutes via parallel execution. | Slower per-check due to inference latency. API rate limits can bottleneck large-scale scans. |
| **Maintainability** | Requires manual updates when benchmarks change, but changes are explicit and version-controlled. | Can adapt to new benchmarks with updated prompts, but "adapting" means relying on the model's training data, which may be outdated. |
| **Flexibility** | Rigid — only checks what it's programmed to check. Adding a new check requires code changes. | Highly flexible — can interpret natural-language descriptions of new controls and reason about novel configurations. |
| **Auditability** | Fully auditable. Every check has a clear, inspectable logic path. | Opaque. An LLM's reasoning is not inspectable or reproducible, making audit sign-off difficult. |
| **Cost** | Low marginal cost. Open-source tools, runs on existing infrastructure. | Higher marginal cost. API calls incur per-token charges; self-hosted models require GPU infrastructure. |
| **Edge cases** | Fails silently on unexpected configurations. | Can reason about context and catch subtle issues a rule-based check would miss, but may also introduce false positives/negatives. |

**Key considerations for choosing:**

- For **compliance reporting and audit evidence**, use the programmatic approach. Auditors need deterministic, reproducible results with clear audit trails. An LLM-generated compliance report would not pass scrutiny from a serious auditor.
- For **interpreting results, generating remediation guidance, and triaging findings**, LLMs add significant value. After the programmatic scan identifies failures, an LLM can explain *why* the control matters, draft a remediation playbook, or help prioritise which failures to address first based on the organisation's risk profile.
- The **hybrid approach** is optimal: use programmatic tools (OpenSCAP, custom scripts) for the actual compliance checks, and layer an LLM on top for interpretation, reporting in natural language, and interactive Q&A. This is the pattern I work with at HTX — our AI-powered procurement system uses **deterministic extraction with strict output contracts** for the compliance-critical layer, and **LLM-powered generation** for the human-facing layer (report drafting, explanations, Q&A). The programmatic layer is the source of truth; the AI layer makes it accessible to humans.
- I've seen the same pattern work in other projects: in my PII anonymisation system, **BERT-based NER** (deterministic, F1 0.87) handles PII detection while **Mistral 7B** handles generative anonymisation. When the LLM alone struggled with long documents, adding a programmatic segmentation step reduced PII leakage by 42% — a clear case where the programmatic approach addressed an LLM weakness.
- **Never let an LLM be the sole source of truth** for a compliance determination. Always validate LLM output against programmatic ground truth.

---

### Case Study 2 — Scaling and Product Delivery

**Context**: Presenting the hardening-check tool to non-technical stakeholders, focusing on accuracy and flexibility.

---

#### 1. Presenting to non-technical stakeholders

Non-technical stakeholders care about **risk, cost, and business impact** — not configuration file syntax. The presentation should translate technical compliance into business language. I've presented technical work to non-technical audiences in several contexts — including an AI-powered visual checkout system for BreadTalk (where we used live demos and Figma prototypes) and an interactive gradient descent workshop for 40+ non-technical mentees (using custom web apps for visualisation). The same principles apply here: show, don't tell; use visuals, not jargon.

**Structure the presentation around three questions:**

**"What does this tool do?"**
Frame it simply: "This tool automatically checks whether our servers are configured securely, based on industry-standard security guidelines (CIS Benchmarks). Think of it as an automated safety inspection for our IT infrastructure — the same way a building inspector checks fire exits and electrical wiring."

**"How accurate is it?"**
Show a concrete comparison. Take a sample server, run the automated tool, and separately have a senior engineer manually verify 10–15 controls. Present the results side-by-side in a simple table. Highlight that the tool produces *identical* results to manual review, but in seconds instead of hours. Use a visual: an interactive dashboard (e.g., Grafana) showing green/amber/red status for each server, with a clear overall compliance percentage (e.g., "94% compliant across 50 servers"). Let stakeholders click on a server to drill down into its specific findings.

If the tool includes an LLM component, be transparent: "The AI assistant helps explain findings in plain English and suggests fixes, but every compliance determination is made by deterministic checks, not by AI guesswork. The AI is the interpreter, not the inspector."

**"How flexible is it?"**
Demonstrate adaptability with a live or recorded demo showing: adding a new server to the scan in under a minute, switching from one compliance profile to another (e.g., CIS Level 1 vs. Level 2), and generating a report filtered by severity. Emphasise that the same tool works across different RHEL versions and can be extended to other operating systems with additional profiles.

**Avoid**: deep technical jargon, deep dives into individual controls, or live terminal demos with raw command-line output. Use visualisations, percentages, and business-impact framing throughout.

---

#### 2. Considerations for scaling in the future

Scaling from a single-server proof-of-concept to enterprise-wide deployment introduces several categories of challenge. I've navigated scaling challenges in several projects — processing 120M+ records on AWS (Aircraft Big Data), supporting 10,000+ concurrent users with zero-error autoscaling on Azure (ESMOS), and building distributed microservices with fault-tolerant orchestration (CampusG). The same principles apply here.

**Infrastructure and connectivity**: Scanning hundreds or thousands of servers requires efficient orchestration. Ansible's push-based model works well up to a few hundred hosts; beyond that, consider Ansible Tower/AWX with smart inventories, or tools like Red Hat Satellite which natively integrate OpenSCAP scanning at scale. For cloud-native environments, leverage cloud APIs (AWS SSM, Azure Arc) to execute scans without direct SSH.

**Performance and parallelism**: Sequential scanning does not scale. The tool must support parallel execution — running scans on multiple servers simultaneously. Ansible handles this with configurable `forks` (e.g., scanning 50 servers in parallel). For very large fleets, consider a distributed architecture where lightweight agents on each server perform the scan locally and report results to a central collector. In my ESMOS project, I configured Horizontal Pod Autoscaling to handle 10,000+ daily users with 0% error rate under load testing — the same philosophy of designing for parallel, elastic workloads applies to compliance scanning.

**Heterogeneous environments**: Real enterprises run diverse operating systems (RHEL 7, 8, 9; Ubuntu; Windows Server) and workloads (bare metal, VMs, containers, Kubernetes). The tool must support multiple CIS profiles and handle OS-specific differences. Container and Kubernetes hardening (CIS Kubernetes Benchmark) is a distinct domain that may require separate tooling.

**Drift detection and continuous compliance**: A one-time scan is insufficient. Servers drift from their baseline as changes are made. The scaled tool should run on a schedule (daily or more frequently), compare current state against the last known state, and alert on *changes* — not just failures. This transforms the tool from a point-in-time auditor to a continuous compliance monitor.

**Data management and retention**: At scale, each scan generates substantial data. Plan for structured storage (a database, not flat files), retention policies (how long to keep historical scans), and efficient querying (e.g., "show me all servers that failed control 5.2.5 in the last 30 days"). In my Aircraft Big Data project, I dealt with this challenge at a much larger scale — designing an S3-based data lake with Parquet storage, Glue cataloguing, and Athena for ad-hoc queries across 120M+ records.

**Role-based access and multi-tenancy**: Different teams may own different servers. The scaled tool needs role-based access control so that the database team sees their servers' compliance, the networking team sees theirs, and leadership sees an aggregate view.

**Exception management**: Not every CIS control applies universally. Some servers have legitimate reasons for deviating from the benchmark (e.g., a legacy application that requires an older TLS version). The tool needs a formal exception/waiver workflow — a way to document "this server is intentionally non-compliant with control X because of reason Y, approved by person Z, expiring on date D."

**Integration with existing tooling**: The tool should feed into the organisation's existing security ecosystem — SIEM, GRC platforms, and ticketing systems — so that non-compliance findings automatically become trackable work items with owners and deadlines. In my CampusG project, I built similar integration patterns: the Saga orchestration layer coordinated across payment (Stripe), notification, and order services, with compensation logic for graceful failure handling. The same principle of integrating a tool into a broader ecosystem with proper error handling applies when plugging compliance data into enterprise security workflows.

---

*Document prepared with a focus on practical, implementable guidance grounded in hands-on project experience across cloud infrastructure, AI/ML systems, and full-stack development.*
