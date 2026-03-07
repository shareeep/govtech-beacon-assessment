#!/usr/bin/env python3
"""Parse OpenSCAP results XML, triage findings with AI, output structured JSON."""

import xml.etree.ElementTree as ET
import json
import argparse
import os
import sys
import requests

# XCCDF 1.2 namespace
NS = {"xccdf": "http://checklists.nist.gov/xccdf/1.2"}


def parse_results(xml_path):
    """Extract failed rules from oscap results XML."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Build rule metadata map: rule_id -> {title, description, fixes}
    rule_meta = {}
    for rule in root.iter(f"{{{NS['xccdf']}}}Rule"):
        rule_id = rule.get("id", "")
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
            "fixes": fixes
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
                "fixes": meta.get("fixes", [])
            })

    return failures


def triage_with_ai(failures, api_key, base_url="https://api.openai.com/v1", model="gpt-4o"):
    """Send findings to LLM for triage and prioritisation."""
    # Build concise summary of failures for the prompt
    finding_lines = []
    for f in failures:
        line = f"- {f['short_name']}: {f['title']}"
        if f["fixes"]:
            line += f" (has {len(f['fixes'])} remediation snippet(s))"
        finding_lines.append(line)

    prompt = f"""You are a senior security engineer triaging CIS Benchmark compliance
findings for a RHEL 9 server. Below are {len(failures)} failed controls.

For each finding, return a JSON object with:
- "short_name": the rule short name
- "severity": "critical" | "high" | "medium" | "low"
- "explanation": 1-2 sentence plain-English explanation of the risk
- "remediation": specific command or config change to fix it
- "likely_intentional": boolean — true if this could be an intentional deviation (explain why)

Return ONLY a JSON array, no markdown fences or commentary.

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

    return json.loads(content)


def mock_triage(failures):
    """Mock triage for testing without an API key. Assigns severity by keyword heuristics."""
    critical_keywords = ["root", "shadow", "password", "empty", "permit"]
    high_keywords = ["ssh", "auth", "permissions", "telnet"]

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

        results.append({
            "short_name": f["short_name"],
            "severity": severity,
            "explanation": f"[MOCK] {f['title']}",
            "remediation": f["fixes"][0]["content"][:200] if f["fixes"] else "See CIS Benchmark documentation",
            "likely_intentional": False
        })

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    results.sort(key=lambda x: severity_order.get(x["severity"], 99))
    return results


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
        triaged = mock_triage(failures)
    else:
        print(f"Triaging with {args.model}...")
        triaged = triage_with_ai(failures, args.api_key, args.base_url, args.model)

    # Grounding check: ensure AI didn't hallucinate rules that weren't in the scan
    parsed_names = {f["short_name"] for f in failures}
    triaged_names = {f["short_name"] for f in triaged}
    hallucinated = triaged_names - parsed_names
    missing = parsed_names - triaged_names

    if hallucinated:
        print(f"\n⚠️  GROUNDING ISSUE: AI returned {len(hallucinated)} rule(s) NOT in scan results:")
        for h in hallucinated:
            print(f"   - {h}")
    if missing:
        print(f"\nℹ️  {len(missing)} parsed failure(s) not in AI output (may have been filtered/merged)")

    output = {
        "total_failures": len(failures),
        "findings": triaged,
        "summary": {
            "critical": sum(1 for f in triaged if f["severity"] == "critical"),
            "high": sum(1 for f in triaged if f["severity"] == "high"),
            "medium": sum(1 for f in triaged if f["severity"] == "medium"),
            "low": sum(1 for f in triaged if f["severity"] == "low"),
        },
        "grounding": {
            "hallucinated_rules": list(hallucinated),
            "missing_from_triage": list(missing),
        }
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results written to {args.output}")
    print(f"Summary: {output['summary']}")


if __name__ == "__main__":
    main()
