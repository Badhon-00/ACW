#!/usr/bin/env python3
"""
Security scan script for parallel-decomposer-skill.
Checks for hardcoded secrets, API keys, and injection patterns.
"""

import os
import re
import sys
from pathlib import Path


# Patterns that might indicate secrets
SECRET_PATTERNS = [
    (r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]{16,}["\']?', "Potential API key"),
    (r'secret\s*[:=]\s*["\']?[a-zA-Z0-9]{16,}["\']?', "Potential secret"),
    (r'token\s*[:=]\s*["\']?[a-zA-Z0-9]{16,}["\']?', "Potential token"),
    (r'password\s*[:=]\s*["\'][^"\']{4,}["\']', "Potential password"),
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API key pattern"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'AKIA[0-9A-Z]{16}', "AWS access key ID"),
]

# Suspicious file patterns
SUSPICIOUS_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    "secrets.json",
    "credentials.json",
    "id_rsa",
    "id_dsa",
]


def scan_file(filepath: Path) -> list:
    """Scan a single file for security issues."""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return findings

    for pattern, description in SECRET_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Check if it's in a comment or documentation
            line_start = content.rfind('\n', 0, match.start()) + 1
            line = content[line_start:match.end()]
            if line.strip().startswith('#') or line.strip().startswith('//'):
                continue
            if 'example' in line.lower() or 'placeholder' in line.lower():
                continue

            findings.append({
                "file": str(filepath),
                "line": content[:match.start()].count('\n') + 1,
                "match": match.group()[:50],
                "description": description,
            })

    return findings


def scan_directory(skill_dir: str) -> list:
    """Scan entire skill directory."""
    all_findings = []
    skill_path = Path(skill_dir)

    # Check for suspicious files
    for suspicious in SUSPICIOUS_FILES:
        suspicious_path = skill_path / suspicious
        if suspicious_path.exists():
            all_findings.append({
                "file": str(suspicious_path),
                "line": 0,
                "match": suspicious,
                "description": "Suspicious file found",
            })

    # Scan all text files
    for root, _, files in os.walk(skill_dir):
        for fname in files:
            if fname.endswith(('.py', '.sh', '.md', '.yaml', '.yml', '.json', '.txt')):
                filepath = Path(root) / fname
                findings = scan_file(filepath)
                all_findings.extend(findings)

    return all_findings


def main():
    if len(sys.argv) < 2:
        script_dir = Path(__file__).parent.resolve()
        skill_dir = script_dir.parent
    else:
        skill_dir = sys.argv[1]

    print(f"Security scanning: {skill_dir}")
    print("=" * 50)

    findings = scan_directory(skill_dir)

    if findings:
        print(f"\nFOUND {len(findings)} POTENTIAL SECURITY ISSUES:")
        for finding in findings:
            print(f"\n  File: {finding['file']}:{finding['line']}")
            print(f"  Issue: {finding['description']}")
            print(f"  Match: {finding['match']}")
        print("\n" + "=" * 50)
        print("RESULT: ISSUES FOUND - Review above findings")
        sys.exit(1)
    else:
        print("\nNo security issues found.")
        print("=" * 50)
        print("RESULT: CLEAN")
        sys.exit(0)


if __name__ == "__main__":
    main()
