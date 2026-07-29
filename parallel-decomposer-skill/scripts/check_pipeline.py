#!/usr/bin/env python3
"""
Pipeline validation script for parallel-decomposer-skill.
Checks that all required files exist and are valid.
"""

import os
import sys
from pathlib import Path


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists and report."""
    exists = os.path.isfile(path)
    status = "PASS" if exists else "FAIL"
    print(f"  [{status}] {description}: {path}")
    return exists


def check_directory_exists(path: str, description: str) -> bool:
    """Check if a directory exists and report."""
    exists = os.path.isdir(path)
    status = "PASS" if exists else "FAIL"
    print(f"  [{status}] {description}: {path}")
    return exists


def validate_skill(skill_dir: str) -> bool:
    """Validate the skill structure."""
    skill_path = Path(skill_dir)
    if not skill_path.exists():
        print(f"ERROR: Skill directory not found: {skill_dir}")
        return False

    print(f"\nValidating skill: {skill_dir}")
    print("=" * 50)

    all_pass = True

    # Required files
    print("\nRequired Files:")
    all_pass &= check_file_exists(
        str(skill_path / "SKILL.md"), "SKILL.md"
    )
    all_pass &= check_file_exists(
        str(skill_path / "AGENTS.md"), "AGENTS.md"
    )
    all_pass &= check_file_exists(
        str(skill_path / "README.md"), "README.md"
    )
    all_pass &= check_file_exists(
        str(skill_path / "install.sh"), "install.sh"
    )

    # Required directories
    print("\nRequired Directories:")
    all_pass &= check_directory_exists(
        str(skill_path / "scripts"), "scripts/"
    )
    all_pass &= check_directory_exists(
        str(skill_path / "references"), "references/"
    )
    all_pass &= check_directory_exists(
        str(skill_path / "assets"), "assets/"
    )

    # Optional but recommended
    print("\nOptional Directories:")
    check_directory_exists(str(skill_path / "evals"), "evals/")

    # Validate SKILL.md frontmatter
    print("\nSKILL.md Validation:")
    skill_md_path = skill_path / "SKILL.md"
    if skill_md_path.exists():
        content = skill_md_path.read_text(encoding="utf-8")
        if content.startswith("---"):
            print("  [PASS] Frontmatter present")
        else:
            print("  [FAIL] Frontmatter missing")
            all_pass = False

        if "name: parallel-decomposer-skill" in content:
            print("  [PASS] Name field present")
        else:
            print("  [FAIL] Name field missing or incorrect")
            all_pass = False

        if "description:" in content:
            print("  [PASS] Description field present")
        else:
            print("  [FAIL] Description field missing")
            all_pass = False
    else:
        print("  [FAIL] SKILL.md not found")
        all_pass = False

    print("\n" + "=" * 50)
    if all_pass:
        print("RESULT: ALL CHECKS PASSED")
    else:
        print("RESULT: SOME CHECKS FAILED")

    return all_pass


def main():
    if len(sys.argv) < 2:
        # Default to checking the skill in the parent directory
        script_dir = Path(__file__).parent.resolve()
        skill_dir = script_dir.parent
    else:
        skill_dir = sys.argv[1]

    success = validate_skill(str(skill_dir))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
