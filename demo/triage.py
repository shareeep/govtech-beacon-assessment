#!/usr/bin/env python3
"""Parse OpenSCAP results XML, triage findings with AI, output structured JSON."""

import xml.etree.ElementTree as ET
import json
import argparse
import os
import sys
import time
import requests

# XCCDF 1.2 namespace
NS = {"xccdf": "http://checklists.nist.gov/xccdf/1.2"}


def parse_results(xml_path):
    """Extract failed rules from oscap results XML."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Build rule metadata map: rule_id -> {title, description, fixes, severity}
    rule_meta = {}
    for rule in root.iter(f"{{{NS['xccdf']}}}Rule"):
        rule_id = rule.get("id", "")
        severity = rule.get("severity", "unknown")  # OpenSCAP's own severity
        title_el = rule.find(f"{{{NS['xccdf']}}}title")
        desc_el = rule.find(f"{{{NS['xccdf']}}}description")
        fixes = []
        for fix in rule.findall(f"{{{NS['xccdf']}}}fix"):
            fixes.append({
                "system": fix.get("system", ""),
                "content": (fix.text or "").strip()
            })
        rule_meta[rule_id] = {
            "title": title_el.text if title_el is not None else "",
            "description": (desc_el.text or "")[:200] if desc_el is not None else "",
            "fixes": fixes,
            "oscap_severity": severity
        }

    # Extract failures from TestResult
    failures = []
    for rule_result in root.iter(f"{{{NS['xccdf']}}}rule-result"):
        result_el = rule_result.find(f"{{{NS['xccdf']}}}result")
        if result_el is not None and result_el.text == "fail":
            rule_id = rule_result.get("idref", "")
            short_name = rule_id.split("content_rule_")[-1] if "content_rule_" in rule_id else rule_id
            meta = rule_meta.get(rule_id, {})
            failures.append({
                "rule_id": rule_id,
                "short_name": short_name,
                "title": meta.get("title", short_name),
                "description": meta.get("description", ""),
                "fixes": meta.get("fixes", []),
                "oscap_severity": meta.get("oscap_severity", "unknown")
            })

    return failures


def triage_with_ai(failures, api_key, base_url="https://api.openai.com/v1", model="gpt-4o"):
    """Send findings to LLM for triage and prioritisation."""
    # Build concise summary of failures for the prompt
    finding_lines = []
    for f in failures:
        line = f"- {f['short_name']}: {f['title']} [oscap severity: {f['oscap_severity']}]"
        if f["fixes"]:
            line += f" (has {len(f['fixes'])} remediation snippet(s))"
        finding_lines.append(line)

    prompt = f"""You are a senior security engineer triaging CIS Benchmark compliance
findings for a RHEL 9 / Rocky Linux 9 server. Below are {len(failures)} failed controls.

Return a JSON object with two keys:

1. "findings" — an array where each element has:
   - "short_name": the rule short name (must match exactly)
   - "severity": "critical" | "high" | "medium" | "low" (your assessment, may differ from oscap)
   - "explanation": 1-2 sentence plain-English explanation of the risk
   - "remediation": specific command or config change to fix it
   - "verification_cmd": a shell command to verify the fix was applied correctly (e.g. grep, stat, sysctl)
   - "rollback": command or steps to undo the fix if it causes issues
   - "complexity": "trivial" | "easy" | "moderate" | "complex" — how hard is the fix
   - "change_window": "live" | "restart_required" | "maintenance_window" — can this be applied without downtime?
   - "change_window_note": brief explanation (e.g. "requires sshd restart, active sessions will drop")
   - "automation_readiness": "fully_automatable" | "needs_review" | "manual_only"
   - "automation_note": brief explanation (e.g. "safe to apply via Ansible" or "requires human decision")
   - "risk_if_ignored": 1 sentence — worst-case outcome of not fixing this
   - "dependencies": 1 sentence — what could break if this is applied (or "None expected")
   - "related_findings": list of other short_names from this scan that should be fixed together (same config file, same service, etc.) — empty list if standalone
   - "likely_intentional": boolean — true if this could be an intentional deviation

2. "attack_chains" — an array of compound-risk groups where multiple findings combine to create a greater threat. Each element has:
   - "name": short descriptive name (e.g. "Unauthenticated Root SSH Access")
   - "severity": "critical" | "high" | "medium" | "low"
   - "findings": list of short_names involved
   - "narrative": 2-3 sentences explaining how these findings chain together
   - "combined_impact": what an attacker can achieve with all of these present

Return ONLY a JSON object, no markdown fences or commentary.

Failed controls:
{chr(10).join(finding_lines)}"""

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        },
        timeout=60
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    # Strip markdown fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0]

    parsed = json.loads(content)

    # Handle both formats: new dict format or legacy plain array
    if isinstance(parsed, list):
        return {"findings": parsed, "attack_chains": []}
    return parsed


def mock_triage(failures):
    """Mock triage for testing without an API key. Assigns severity by keyword heuristics."""
    critical_keywords = ["root", "shadow", "password", "empty", "permit"]
    high_keywords = ["ssh", "auth", "permissions", "telnet"]

    # Track SSH-related findings for mock grouping
    ssh_findings = []

    results = []
    for f in failures:
        name_lower = f["short_name"].lower()
        title_lower = f["title"].lower()
        combined = name_lower + " " + title_lower

        if any(k in combined for k in critical_keywords):
            severity = "critical"
        elif any(k in combined for k in high_keywords):
            severity = "high"
        else:
            severity = "medium"

        is_ssh = "ssh" in combined
        if is_ssh:
            ssh_findings.append(f["short_name"])

        results.append({
            "short_name": f["short_name"],
            "severity": severity,
            "oscap_severity": f.get("oscap_severity", "unknown"),
            "explanation": f"[MOCK] {f['title']}",
            "remediation": f["fixes"][0]["content"][:200] if f["fixes"] else "See CIS Benchmark documentation",
            "verification_cmd": "[MOCK] grep -r /etc/ssh/sshd_config" if is_ssh else "[MOCK] Run oscap scan to verify",
            "rollback": "[MOCK] Revert config file from backup",
            "complexity": "easy",
            "change_window": "restart_required" if is_ssh else "live",
            "change_window_note": "[MOCK] Requires sshd restart" if is_ssh else "[MOCK] Safe to apply live",
            "automation_readiness": "fully_automatable",
            "automation_note": "[MOCK] Safe to apply via Ansible",
            "risk_if_ignored": "[MOCK] Potential compliance violation.",
            "dependencies": "[MOCK] None expected.",
            "related_findings": [],  # filled below
            "likely_intentional": False
        })

    # Fill in related_findings for SSH group
    for r in results:
        if r["short_name"] in ssh_findings:
            r["related_findings"] = [n for n in ssh_findings if n != r["short_name"]]

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    results.sort(key=lambda x: severity_order.get(x["severity"], 99))

    # Build mock attack chains
    attack_chains = []
    if len(ssh_findings) >= 2:
        attack_chains.append({
            "name": "Weak SSH Configuration Chain",
            "severity": "critical",
            "findings": ssh_findings,
            "narrative": "[MOCK] Multiple SSH misconfigurations combine to weaken remote access security.",
            "combined_impact": "[MOCK] Attacker could gain unauthenticated root access via SSH."
        })

    return {"findings": results, "attack_chains": attack_chains}


def main():
    parser = argparse.ArgumentParser(description="Triage OpenSCAP findings with AI")
    parser.add_argument("--results", required=True, help="Path to oscap results.xml")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""),
                        help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--base-url", default="https://api.openai.com/v1",
                        help="API base URL (for OpenAI-compatible endpoints)")
    parser.add_argument("--model", default="gpt-4o", help="Model name")
    parser.add_argument("--mock", action="store_true", help="Use mock triage (no API key needed)")
    parser.add_argument("--parse-only", action="store_true", help="Just dump parsed failures (no AI), for validating the parser")
    parser.add_argument("--output", default="triage_results.json", help="Output JSON path")
    args = parser.parse_args()

    print(f"Parsing {args.results}...")
    failures = parse_results(args.results)
    print(f"Found {len(failures)} failed controls.")

    if args.parse_only:
        # Dump raw parsed failures so you can compare against the HTML report
        print(f"\n{'='*60}")
        print(f"PARSED FAILURES ({len(failures)} total)")
        print(f"{'='*60}")
        for i, f in enumerate(failures, 1):
            print(f"\n{i}. {f['short_name']}")
            print(f"   Title: {f['title']}")
            print(f"   Fixes: {len(f['fixes'])} snippet(s)")
        # Also write to JSON for diffing
        with open(args.output, "w") as out:
            json.dump({"total_failures": len(failures), "parsed_failures": failures}, out, indent=2)
        print(f"\nRaw parsed data written to {args.output}")
        return

    if args.mock or not args.api_key:
        if not args.mock:
            print("No API key provided, using mock triage. Use --api-key or set OPENAI_API_KEY.")
        print("Running mock triage...")
        t0 = time.time()
        triage_result = mock_triage(failures)
        triage_duration = time.time() - t0
        triage_mode = "mock"
    else:
        print(f"Triaging with {args.model}...")
        t0 = time.time()
        triage_result = triage_with_ai(failures, args.api_key, args.base_url, args.model)
        triage_duration = time.time() - t0
        triage_mode = args.model

    print(f"AI triage completed in {triage_duration:.1f}s ({triage_mode})")

    triaged = triage_result["findings"]
    attack_chains = triage_result.get("attack_chains", [])

    # ── Grounding checks ──────────────────────────────────────────────
    # These are all *programmatic* — no LLM-as-judge needed.
    # The principle: constrain and verify AI output against source data
    # using deterministic code.
    parsed_names = {f["short_name"]: f for f in failures}
    triaged_names = {f["short_name"] for f in triaged}

    VALID_SEVERITIES = {"critical", "high", "medium", "low"}
    REQUIRED_FIELDS = ["short_name", "severity", "explanation", "remediation"]

    checks = []  # list of {"check", "status": "pass"|"warn"|"fail", "detail"}

    # Check 1: Rule existence — AI can only reference rules from the scan
    hallucinated = triaged_names - set(parsed_names)
    missing = set(parsed_names) - triaged_names
    checks.append({
        "check": "Rule IDs match scan results",
        "status": "fail" if hallucinated else "pass",
        "detail": f"{len(hallucinated)} hallucinated rule(s): {', '.join(hallucinated)}" if hallucinated
                  else f"All {len(triaged)} AI-returned rules exist in scan"
    })
    if missing:
        checks.append({
            "check": "All scan failures covered",
            "status": "warn",
            "detail": f"{len(missing)} failure(s) not in AI output (may have been filtered/merged): {', '.join(missing)}"
        })

    # Check 2: Required fields present on every finding
    fields_missing = []
    for f in triaged:
        for field in REQUIRED_FIELDS:
            if not f.get(field):
                fields_missing.append(f"{f.get('short_name', '?')}.{field}")
    checks.append({
        "check": "Required fields present",
        "status": "fail" if fields_missing else "pass",
        "detail": f"Missing: {', '.join(fields_missing[:5])}" if fields_missing
                  else f"All {len(REQUIRED_FIELDS)} required fields present on every finding"
    })

    # Check 3: Severity values are valid
    invalid_severities = [f["short_name"] for f in triaged if f.get("severity") not in VALID_SEVERITIES]
    checks.append({
        "check": "Severity values valid",
        "status": "fail" if invalid_severities else "pass",
        "detail": f"Invalid severity on: {', '.join(invalid_severities)}" if invalid_severities
                  else f"All severities in {VALID_SEVERITIES}"
    })

    # Check 4: Related findings all reference real scan results
    bad_refs = []
    for f in triaged:
        for ref in f.get("related_findings", []):
            if ref not in parsed_names:
                bad_refs.append(f"{f['short_name']} -> {ref}")
    checks.append({
        "check": "Related findings reference valid rules",
        "status": "fail" if bad_refs else "pass",
        "detail": f"Invalid references: {', '.join(bad_refs)}" if bad_refs
                  else "All related_findings references exist in scan"
    })

    # Check 5: Attack chain findings all reference real scan results
    bad_chain_refs = []
    for chain in attack_chains:
        for ref in chain.get("findings", []):
            if ref not in parsed_names:
                bad_chain_refs.append(f"{chain.get('name', '?')} -> {ref}")
    checks.append({
        "check": "Attack chain findings reference valid rules",
        "status": "fail" if bad_chain_refs else "pass",
        "detail": f"Invalid references: {', '.join(bad_chain_refs)}" if bad_chain_refs
                  else "All attack chain finding references exist in scan"
    })

    # Check 6: Severity upgrade plausibility — flag extreme jumps (low→critical = 3 levels)
    severity_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3, "unknown": 1}
    extreme_upgrades = []
    for f in triaged:
        oscap_sev = parsed_names.get(f["short_name"], {}).get("oscap_severity", "unknown")
        ai_rank = severity_rank.get(f.get("severity"), 1)
        oscap_rank = severity_rank.get(oscap_sev, 1)
        if ai_rank - oscap_rank >= 3:  # jumped 3+ levels
            extreme_upgrades.append(f["short_name"])
    checks.append({
        "check": "No extreme severity jumps (3+ levels)",
        "status": "warn" if extreme_upgrades else "pass",
        "detail": f"Large upgrade on: {', '.join(extreme_upgrades)} — verify justification" if extreme_upgrades
                  else "All severity changes within 2 levels of OpenSCAP rating"
    })

    # Merge oscap_severity from parsed data into AI triage results
    for f in triaged:
        parsed = parsed_names.get(f["short_name"])
        if parsed and "oscap_severity" not in f:
            f["oscap_severity"] = parsed.get("oscap_severity", "unknown")

    passed = sum(1 for c in checks if c["status"] == "pass")
    total_checks = len(checks)
    print(f"\nGrounding: {passed}/{total_checks} checks passed")
    for c in checks:
        icon = "✅" if c["status"] == "pass" else ("⚠️" if c["status"] == "warn" else "❌")
        print(f"  {icon} {c['check']}: {c['detail']}")

    output = {
        "total_failures": len(failures),
        "system": {
            "hostname": os.path.basename(os.path.dirname(args.results)) or "target",
            "profile": "CIS Level 1 — Server",
            "profile_id": "cis_server_l1",
            "os": "Rocky Linux 9",
            "scan_source": "OpenSCAP + SCAP Security Guide",
        },
        "findings": triaged,
        "attack_chains": attack_chains,
        "summary": {
            "critical": sum(1 for f in triaged if f["severity"] == "critical"),
            "high": sum(1 for f in triaged if f["severity"] == "high"),
            "medium": sum(1 for f in triaged if f["severity"] == "medium"),
            "low": sum(1 for f in triaged if f["severity"] == "low"),
        },
        "grounding": {
            "hallucinated_rules": list(hallucinated),
            "missing_from_triage": list(missing),
            "checks": checks,
            "passed": passed,
            "total": total_checks,
        },
        "timing": {
            "triage_seconds": round(triage_duration, 2),
            "model": triage_mode,
            "num_findings": len(failures),
        }
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results written to {args.output}")
    print(f"Summary: {output['summary']}")


if __name__ == "__main__":
    main()
