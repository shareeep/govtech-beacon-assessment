#!/usr/bin/env python3
"""Evaluate AI triage output against known ground truth.

We intentionally broke specific things in the Containerfile — so we KNOW
which rules should fail and roughly what severity they should be.
This lets us score the AI's triage accuracy.
"""

import json
import argparse
import sys

# Ground truth: rules we intentionally broke and their expected severity
GROUND_TRUTH = {
    # SSH misconfigs
    "sshd_disable_root_login":       {"expected_severity": "critical", "category": "ssh"},
    "sshd_disable_empty_passwords":  {"expected_severity": "critical", "category": "ssh"},
    "sshd_set_max_auth_tries":       {"expected_severity": "high",     "category": "ssh"},
    # File permissions
    "file_permissions_etc_shadow":    {"expected_severity": "critical", "category": "permissions"},
    "file_permissions_etc_gshadow":   {"expected_severity": "critical", "category": "permissions"},
    # Unnecessary services
    "package_telnet_removed":         {"expected_severity": "high",     "category": "packages"},
    # User/password
    "no_empty_passwords":             {"expected_severity": "critical", "category": "users"},
    # Network/kernel
    "sysctl_net_ipv4_ip_forward":     {"expected_severity": "high",     "category": "network"},
    "sysctl_net_ipv4_conf_all_accept_redirects": {"expected_severity": "medium", "category": "network"},
    "sysctl_net_ipv4_tcp_syncookies": {"expected_severity": "high",     "category": "network"},
}

SEVERITY_RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0}


def evaluate(triage_path):
    with open(triage_path) as f:
        data = json.load(f)

    findings = {f["short_name"]: f for f in data["findings"]}

    results = []
    matched = 0
    severity_correct = 0
    severity_close = 0  # within 1 rank

    for rule_name, truth in GROUND_TRUTH.items():
        # Check if the AI found this rule at all (partial match on name)
        found = None
        for fname, fdata in findings.items():
            if rule_name in fname or fname in rule_name:
                found = fdata
                break

        if found:
            matched += 1
            expected_rank = SEVERITY_RANK[truth["expected_severity"]]
            actual_rank = SEVERITY_RANK.get(found["severity"], 0)
            exact = found["severity"] == truth["expected_severity"]
            close = abs(expected_rank - actual_rank) <= 1

            if exact:
                severity_correct += 1
            if close:
                severity_close += 1

            results.append({
                "rule": rule_name,
                "found": True,
                "expected_severity": truth["expected_severity"],
                "actual_severity": found["severity"],
                "severity_match": exact,
                "has_remediation": bool(found.get("remediation")),
            })
        else:
            results.append({
                "rule": rule_name,
                "found": False,
                "expected_severity": truth["expected_severity"],
                "actual_severity": None,
                "severity_match": False,
                "has_remediation": False,
            })

    total = len(GROUND_TRUTH)
    print("=" * 60)
    print("EVAL: AI Triage vs Ground Truth")
    print("=" * 60)
    print(f"Known broken rules:       {total}")
    print(f"Detected by AI:           {matched}/{total} ({matched/total*100:.0f}%)")
    print(f"Severity exact match:     {severity_correct}/{matched} ({severity_correct/matched*100:.0f}%)" if matched else "")
    print(f"Severity within 1 rank:   {severity_close}/{matched} ({severity_close/matched*100:.0f}%)" if matched else "")
    print()

    for r in results:
        icon = "✓" if r["found"] else "✗"
        sev = f"{r['expected_severity']} → {r['actual_severity']}" if r["found"] else f"{r['expected_severity']} → MISSED"
        match_icon = "✓" if r["severity_match"] else "~" if r["found"] else "✗"
        print(f"  {icon} {r['rule']:<45} [{match_icon}] {sev}")

    # Grounding check: did AI hallucinate findings not in the scan?
    grounding = data.get("grounding", {})
    hallucinated = grounding.get("hallucinated_rules", [])
    if hallucinated:
        print(f"\n⚠️  GROUNDING FAILURES: {len(hallucinated)} rule(s) in AI output were NOT in scan results:")
        for h in hallucinated:
            print(f"   - {h}")
        print("   The AI invented findings. This is a reliability problem.")
    else:
        print("\n✓ Grounding: All AI findings map to actual scan results (no hallucinations).")

    print()
    if matched == total and severity_correct == matched and not hallucinated:
        print("RESULT: Perfect — all rules found, correct severity, no hallucinations.")
    elif matched == total and not hallucinated:
        print("RESULT: All rules detected, no hallucinations, some severity mismatches.")
    elif hallucinated:
        print(f"RESULT: AI hallucinated {len(hallucinated)} rule(s). Grounding needs improvement.")
    else:
        print(f"RESULT: {total - matched} rules missed by triage.")

    return matched == total and not hallucinated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate AI triage accuracy")
    parser.add_argument("--triage", default="triage_results.json", help="Path to triage output JSON")
    args = parser.parse_args()
    success = evaluate(args.triage)
    sys.exit(0 if success else 1)
