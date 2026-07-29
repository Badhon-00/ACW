#!/usr/bin/env python3
"""
Evaluation Runner for Code Analyzer Suite
Validates the skill against defined evaluation criteria.
"""

import json
import sys
from pathlib import Path


def load_eval_spec(skill_dir: Path) -> dict:
    """Load evaluation specification."""
    eval_file = skill_dir / "evals" / "code-analyzer.eval.md"
    if not eval_file.exists():
        return None

    # Parse eval spec from markdown
    content = eval_file.read_text(encoding="utf-8")
    spec = {"checks": [], "golden_cases": []}

    # Simple markdown parsing for eval spec
    current_section = None
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## Binary Checks"):
            current_section = "checks"
        elif line.startswith("## Golden Cases"):
            current_section = "cases"
        elif line.startswith("- [") and current_section == "checks":
            check = {"description": line[4:].strip(), "type": "llm-judge"}
            spec["checks"].append(check)
        elif line.startswith("### Case") and current_section == "cases":
            spec["golden_cases"].append({"name": line[4:].strip(), "details": ""})
        elif current_section == "cases" and spec["golden_cases"]:
            spec["golden_cases"][-1]["details"] += line + "\n"

    return spec


def validate_structure(skill_dir: Path) -> bool:
    """Validate skill structure (binary check)."""
    required = ["SKILL.md", "AGENTS.md", "scripts", "assets", "references"]
    for item in required:
        path = skill_dir / item
        if not path.exists():
            return False
    return True


def validate_frontmatter(skill_dir: Path) -> bool:
    """Validate SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False

    content = skill_md.read_text(encoding="utf-8")
    return content.startswith("---") and "name: code-analyzer-skill" in content


def validate_scripts_executable(skill_dir: Path) -> bool:
    """Validate scripts can be compiled."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return False

    for script in scripts_dir.glob("*.py"):
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError:
            return False
    return True


def run_check(name: str, check_func, skill_dir: Path) -> tuple:
    """Run a single check and return result."""
    try:
        passed = check_func(skill_dir)
        return name, passed, None
    except Exception as e:
        return name, False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Run code-analyzer-suite evaluations")
    parser.add_argument("--validate", action="store_true", help="Run validation checks")
    parser.add_argument("--skill-dir", default=None, help="Skill directory path")

    args = parser.parse_args()

    if args.skill_dir:
        skill_dir = Path(args.skill_dir)
    else:
        skill_dir = Path(__file__).parent.parent

    print(f"[Eval] Running evaluations for: {skill_dir}\n")

    # Binary checks
    checks = [
        ("Structure", validate_structure),
        ("Frontmatter", validate_frontmatter),
        ("Scripts Compilable", validate_scripts_executable),
    ]

    all_passed = True
    results = []

    for name, check_func in checks:
        check_name, passed, error = run_check(name, check_func, skill_dir)
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {check_name}")
        if error:
            print(f"    Error: {error}")
        results.append((check_name, passed))
        if not passed:
            all_passed = False

    # Load and display eval spec
    spec = load_eval_spec(skill_dir)
    if spec:
        print(f"\n[Eval] Loaded {len(spec.get('checks', []))} checks from spec")
        print(f"[Eval] Loaded {len(spec.get('golden_cases', []))} golden cases")

    print("\n[Eval] Summary:")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")

    if all_passed:
        print("\n[Eval] VALID - All checks passed")
        return 0
    else:
        print("\n[Eval] INVALID - Some checks failed")
        return 1


if __name__ == "__main__":
    import argparse
    sys.exit(main())
