#!/usr/bin/env python3
"""
Spec validation script for parallel-decomposer-skill.
Validates frontmatter, naming, structure, and line count.
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(content: str) -> list:
    """Validate YAML frontmatter."""
    errors = []

    if not content.startswith("---"):
        errors.append("Frontmatter must start with '---'")
        return errors

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        errors.append("Frontmatter not properly closed with '---'")
        return errors

    frontmatter = match.group(1)

    # Required fields
    required_fields = ["name:", "description:", "license:"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Name validation
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not name.endswith("-skill"):
            errors.append(f"Skill name must end with '-skill': {name}")
        if len(name) > 64:
            errors.append(f"Skill name too long (max 64 chars): {name}")
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Skill name must be lowercase alphanumeric with hyphens: {name}")

    return errors


def validate_structure(skill_dir: str) -> list:
    """Validate skill directory structure."""
    errors = []
    skill_path = Path(skill_dir)

    required_files = ["SKILL.md", "AGENTS.md", "README.md", "install.sh"]
    for fname in required_files:
        if not (skill_path / fname).exists():
            errors.append(f"Missing required file: {fname}")

    required_dirs = ["scripts", "references", "assets"]
    for dname in required_dirs:
        if not (skill_path / dname).is_dir():
            errors.append(f"Missing required directory: {dname}/")

    return errors


def validate_skill_md(skill_path: Path) -> list:
    """Validate SKILL.md content."""
    errors = []
    content = skill_path.read_text(encoding="utf-8")

    # Frontmatter
    frontmatter_errors = validate_frontmatter(content)
    errors.extend(frontmatter_errors)

    # Line count (should be < 500)
    lines = content.split('\n')
    if len(lines) > 500:
        errors.append(f"SKILL.md too long ({len(lines)} lines, max 500)")

    # Must have invocation header
    if not re.search(r'^# /[a-z0-9-]+', content, re.MULTILINE):
        errors.append("SKILL.md must have invocation header like '# /skill-name'")

    # Must have trigger section
    if "## Trigger" not in content:
        errors.append("SKILL.md must have '## Trigger' section")

    return errors


def main():
    if len(sys.argv) < 2:
        script_dir = Path(__file__).parent.resolve()
        skill_dir = script_dir.parent
    else:
        skill_dir = sys.argv[1]

    print(f"Validating skill: {skill_dir}")
    print("=" * 50)

    all_errors = []

    # Structure validation
    print("\nStructure Validation:")
    struct_errors = validate_structure(skill_dir)
    all_errors.extend(struct_errors)
    for err in struct_errors:
        print(f"  [FAIL] {err}")
    if not struct_errors:
        print("  [PASS] All structure checks passed")

    # SKILL.md validation
    print("\nSKILL.md Validation:")
    skill_md = Path(skill_dir) / "SKILL.md"
    if skill_md.exists():
        skill_errors = validate_skill_md(skill_md)
        all_errors.extend(skill_errors)
        for err in skill_errors:
            print(f"  [FAIL] {err}")
        if not skill_errors:
            print("  [PASS] All SKILL.md checks passed")
    else:
        print("  [FAIL] SKILL.md not found")
        all_errors.append("SKILL.md not found")

    print("\n" + "=" * 50)
    if all_errors:
        print(f"RESULT: FAILED ({len(all_errors)} errors)")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("RESULT: VALID")
        sys.exit(0)


if __name__ == "__main__":
    main()
