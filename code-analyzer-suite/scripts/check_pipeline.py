#!/usr/bin/env python3
"""
Pipeline Validation Script
Validates the code-analyzer-suite structure and dependencies.
"""

import json
import sys
from pathlib import Path


def validate_skill_structure(skill_dir: Path) -> bool:
    """Validate the skill directory structure."""
    required_files = [
        "SKILL.md",
        "AGENTS.md",
        "README.md",
        "install.sh"
    ]

    required_dirs = [
        "scripts",
        "references",
        "assets"
    ]

    all_valid = True

    print("[Validate] Checking required files...")
    for file in required_files:
        file_path = skill_dir / file
        if file_path.exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [MISSING] {file}")
            all_valid = False

    print("[Validate] Checking required directories...")
    for dir_name in required_dirs:
        dir_path = skill_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"  [OK] {dir_name}/")
        else:
            print(f"  [MISSING] {dir_name}/")
            all_valid = False

    return all_valid


def validate_skill_md(skill_dir: Path) -> bool:
    """Validate SKILL.md format."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False

    content = skill_md.read_text(encoding="utf-8")
    valid = True

    print("[Validate] Checking SKILL.md format...")

    # Check frontmatter
    if content.startswith("---"):
        print("  [OK] Frontmatter present")
    else:
        print("  [FAIL] Missing frontmatter")
        valid = False

    # Check name field
    if "name: code-analyzer-skill" in content:
        print("  [OK] Name field correct")
    else:
        print("  [FAIL] Name field missing or incorrect")
        valid = False

    # Check trigger section
    if "# /code-analyzer" in content:
        print("  [OK] Trigger header present")
    else:
        print("  [FAIL] Missing trigger header")
        valid = False

    # Check line count
    lines = content.split("\n")
    if len(lines) <= 500:
        print(f"  [OK] Line count: {len(lines)} (<= 500)")
    else:
        print(f"  [WARN] Line count: {len(lines)} (> 500)")

    return valid


def validate_scripts(skill_dir: Path) -> bool:
    """Validate Python scripts."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return False

    valid = True
    print("[Validate] Checking scripts...")

    required_scripts = [
        "generate_tasks.py",
        "consolidate_report.py",
        "run_pipeline.py",
        "check_pipeline.py"
    ]

    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"  [OK] {script}")
            # Try to compile
            try:
                compile(script_path.read_text(encoding="utf-8"), script, "exec")
                print(f"    [OK] Syntax valid")
            except SyntaxError as e:
                print(f"    [FAIL] Syntax error: {e}")
                valid = False
        else:
            print(f"  [MISSING] {script}")
            valid = False

    return valid


def validate_assets(skill_dir: Path) -> bool:
    """Validate analysis templates."""
    assets_dir = skill_dir / "assets"
    if not assets_dir.exists():
        return False

    valid = True
    print("[Validate] Checking assets...")

    required_templates = [
        "security-template.md",
        "performance-template.md",
        "quality-template.md",
        "architecture-template.md",
        "logic-template.md",
        "consolidated-template.md"
    ]

    for template in required_templates:
        template_path = assets_dir / template
        if template_path.exists():
            print(f"  [OK] {template}")
        else:
            print(f"  [MISSING] {template}")
            valid = False

    return valid


def validate_references(skill_dir: Path) -> bool:
    """Validate reference documentation."""
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        return False

    valid = True
    print("[Validate] Checking references...")

    required_refs = [
        "analysis-dimensions.md",
        "severity-guidelines.md",
        "output-templates.md",
        "parallel-execution.md"
    ]

    for ref in required_refs:
        ref_path = refs_dir / ref
        if ref_path.exists():
            print(f"  [OK] {ref}")
        else:
            print(f"  [MISSING] {ref}")
            valid = False

    return valid


def main():
    skill_dir = Path(__file__).parent.parent

    print(f"[Validate] Validating: {skill_dir}\n")

    results = []
    results.append(("Structure", validate_skill_structure(skill_dir)))
    results.append(("SKILL.md", validate_skill_md(skill_dir)))
    results.append(("Scripts", validate_scripts(skill_dir)))
    results.append(("Assets", validate_assets(skill_dir)))
    results.append(("References", validate_references(skill_dir)))

    print("\n[Validate] Summary:")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[Validate] All checks passed!")
        return 0
    else:
        print("\n[Validate] Some checks failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
