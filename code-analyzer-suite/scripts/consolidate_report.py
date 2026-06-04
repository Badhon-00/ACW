#!/usr/bin/env python3
"""
Consolidated Report Generator
Combines individual dimension analysis results into a unified report.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


def load_dimension_result(file_path: str) -> Dict:
    """Load a dimension analysis result from JSON or markdown."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Result file not found: {file_path}")

    content = path.read_text(encoding="utf-8")

    # Try JSON first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Parse markdown format
    result = {
        "dimension": "Unknown",
        "issues": [],
        "positive_findings": [],
        "score": None
    }

    lines = content.split("\n")
    current_section = None

    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            result["dimension"] = line[2:].strip()
        elif line.startswith("## Issues Found"):
            current_section = "issues"
        elif line.startswith("## Positive Findings"):
            current_section = "positive"
        elif line.startswith("## Dimension Score"):
            current_section = "score"
        elif line.startswith("- **") and current_section == "issues":
            # Parse issue entry
            issue = parse_issue_line(line)
            if issue:
                result["issues"].append(issue)
        elif line.startswith("- ") and current_section == "positive":
            result["positive_findings"].append(line[2:])
        elif current_section == "score" and line:
            try:
                result["score"] = float(line.split("/")[0])
            except ValueError:
                pass

    return result


def parse_issue_line(line: str) -> Dict:
    """Parse an issue line from markdown format."""
    # Format: - **Title** (Severity) - Location: Description
    import re
    match = re.match(r'- \*\*(.+?)\*\*\s*\((.+?)\)\s*-\s*(.+)', line)
    if match:
        return {
            "title": match.group(1),
            "severity": match.group(2),
            "description": match.group(3),
            "location": "Unknown"
        }
    return None


def calculate_overall_risk(results: List[Dict]) -> str:
    """Calculate overall risk level from all dimension results."""
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for result in results:
        for issue in result.get("issues", []):
            severity = issue.get("severity", "Low")
            if severity in severity_counts:
                severity_counts[severity] += 1

    if severity_counts["Critical"] > 0:
        return "Critical"
    elif severity_counts["High"] > 0:
        return "High"
    elif severity_counts["Medium"] > 0:
        return "Medium"
    else:
        return "Low"


def generate_consolidated_report(results: List[Dict]) -> str:
    """Generate a consolidated markdown report from dimension results."""
    lines = []
    lines.append("# Consolidated Code Analysis Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")

    overall_risk = calculate_overall_risk(results)
    total_issues = sum(len(r.get("issues", [])) for r in results)
    critical_issues = sum(
        1 for r in results
        for i in r.get("issues", [])
        if i.get("severity") == "Critical"
    )

    lines.append(f"- **Overall Risk Level:** {overall_risk}")
    lines.append(f"- **Dimensions Analyzed:** {len(results)}")
    lines.append(f"- **Total Issues Found:** {total_issues}")
    lines.append(f"- **Critical Issues Requiring Immediate Action:** {critical_issues}")
    lines.append("")

    # Dimension Summaries
    lines.append("## Dimension Summaries")
    lines.append("")
    lines.append("| Dimension | Issues | Critical | High | Medium | Low | Score |")
    lines.append("|-----------|--------|----------|------|--------|-----|-------|")

    for result in results:
        dim_name = result.get("dimension", "Unknown")
        issues = result.get("issues", [])
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for issue in issues:
            sev = issue.get("severity", "Low")
            if sev in counts:
                counts[sev] += 1
        score = result.get("score", "N/A")
        score_str = f"{score}/10" if score is not None else "N/A"
        lines.append(f"| {dim_name} | {len(issues)} | {counts['Critical']} | {counts['High']} | {counts['Medium']} | {counts['Low']} | {score_str} |")

    lines.append("")

    # Cross-Dimensional Findings
    lines.append("## Cross-Dimensional Findings")
    lines.append("")
    lines.append("_Issues that span multiple dimensions or have systemic impact._")
    lines.append("")

    # Collect all critical and high issues
    significant_issues = []
    for result in results:
        for issue in result.get("issues", []):
            if issue.get("severity") in ["Critical", "High"]:
                significant_issues.append((result["dimension"], issue))

    if significant_issues:
        for dim, issue in significant_issues:
            lines.append(f"- **[{dim}]** {issue['title']} ({issue['severity']})")
    else:
        lines.append("No significant cross-dimensional issues identified.")

    lines.append("")

    # Prioritized Action Items
    lines.append("## Prioritized Action Items")
    lines.append("")

    # Sort all issues by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    all_issues = []
    for result in results:
        for issue in result.get("issues", []):
            all_issues.append((result["dimension"], issue))

    all_issues.sort(key=lambda x: severity_order.get(x[1].get("severity", "Low"), 4))

    for i, (dim, issue) in enumerate(all_issues[:20], 1):  # Top 20
        lines.append(f"{i}. **[{issue.get('severity', 'Low')}] [{dim}]** {issue['title']}")
        if "recommendation" in issue:
            lines.append(f"   - *Recommendation:* {issue['recommendation']}")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    lines.append("### Immediate Actions (Critical/High)")
    lines.append("1. Address all Critical issues before deployment")
    lines.append("2. Schedule High severity fixes as near-term work based on production risk")
    lines.append("")
    lines.append("### Short-term Improvements (Medium)")
    lines.append("1. Plan Medium severity fixes for current sprint")
    lines.append("2. Add missing tests for critical paths")
    lines.append("")
    lines.append("### Long-term Maintenance (Low)")
    lines.append("1. Address style inconsistencies and documentation gaps")
    lines.append("2. Consider refactoring for improved maintainability")
    lines.append("")

    # Dimension Details
    lines.append("## Detailed Dimension Reports")
    lines.append("")

    for result in results:
        dim_name = result.get("dimension", "Unknown")
        lines.append(f"### {dim_name}")
        lines.append("")

        if result.get("issues"):
            lines.append("**Issues:**")
            for issue in result["issues"]:
                lines.append(f"- **{issue['title']}** ({issue.get('severity', 'Low')})")
                lines.append(f"  - Location: {issue.get('location', 'Unknown')}")
                lines.append(f"  - {issue.get('description', '')}")
            lines.append("")

        if result.get("positive_findings"):
            lines.append("**Positive Findings:**")
            for finding in result["positive_findings"]:
                lines.append(f"- {finding}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Consolidate dimension analysis results")
    parser.add_argument("results", nargs="+", help="Dimension result files (JSON or markdown)")
    parser.add_argument("--output", "-o", default="consolidated-report.md", help="Output report path")

    args = parser.parse_args()

    results = []
    for result_file in args.results:
        try:
            result = load_dimension_result(result_file)
            results.append(result)
            print(f"Loaded: {result_file}")
        except Exception as e:
            print(f"Error loading {result_file}: {e}", file=sys.stderr)
            sys.exit(1)

    report = generate_consolidated_report(results)

    output_path = Path(args.output)
    output_path.write_text(report, encoding="utf-8")
    print(f"Consolidated report written to: {args.output}")


if __name__ == "__main__":
    main()
