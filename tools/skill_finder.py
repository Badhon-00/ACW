#!/usr/bin/env python3
"""
skill_finder.py — Dynamic CLI Skill Finder & Registry Query Tool
Parses Awesome Claude Skills markdown files and provides instant CLI search & MCP tool formatters.
"""
import os
import sys
import re
import argparse
from pathlib import Path

def parse_readme(readme_path: Path) -> list[dict]:
    items = []
    if not readme_path.exists():
        return items
    text = readme_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = re.search(r'\[([^\]]+)\]\(([^\)]+)\)\s*-\s*(.+)', line)
        if m:
            items.append({
                "title": m.group(1).strip(),
                "url": m.group(2).strip(),
                "description": m.group(3).strip()
            })
    return items

def main():
    parser = argparse.ArgumentParser(description="Dynamic Awesome Claude Skills CLI Finder")
    parser.add_argument("query", nargs="*", help="Search terms")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    q = " ".join(args.query).lower() if args.query else ""
    readme = Path("README.md")
    items = parse_readme(readme)

    matches = [it for it in items if q in it["title"].lower() or q in it["description"].lower()] if q else items[:10]

    if args.json:
        import json
        print(json.dumps(matches, indent=2))
    else:
        print(f"Found {len(matches)} Claude skills:")
        for m in matches:
            print(f"  * {m['title']}: {m['description']}")

if __name__ == "__main__":
    main()
