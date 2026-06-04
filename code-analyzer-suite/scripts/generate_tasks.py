#!/usr/bin/env python3
"""
Parallel Analysis Task Generator
Generates dimension-specific analysis tasks from code input.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


DIMENSIONS = {
    "security": {
        "name": "Security Analysis",
        "keywords": ["security", "vulnerability", "auth", "injection", "XSS", "CSRF", "crypto", "encrypt", "sanitize", "validate"],
        "focus_areas": ["Authentication", "Authorization", "Input validation", "Data exposure", "Injection risks", "Cryptographic practices"],
        "checklist": [
            "Check for SQL injection vulnerabilities (string concatenation, f-strings in queries)",
            "Verify input validation and sanitization",
            "Check authentication and authorization mechanisms",
            "Look for hardcoded secrets, API keys, or passwords",
            "Verify secure data handling (encryption, hashing)",
            "Check for XSS, CSRF, and other web vulnerabilities",
            "Verify proper error handling that doesn't leak sensitive info",
            "Check file upload/download security",
            "Verify session management and token handling",
            "Check for insecure dependencies or deprecated functions"
        ]
    },
    "performance": {
        "name": "Performance Analysis",
        "keywords": ["performance", "bottleneck", "slow", "memory leak", "optimize", "N+1", "cache", "async", "query", "complexity"],
        "focus_areas": ["Algorithm complexity", "Memory usage", "Database queries", "Caching strategies", "Async patterns", "Resource management"],
        "checklist": [
            "Analyze time and space complexity of algorithms",
            "Check for N+1 query problems",
            "Identify memory leaks or excessive allocation",
            "Verify caching implementation and cache invalidation",
            "Check for blocking operations in async contexts",
            "Analyze database query efficiency and missing indexes",
            "Check for unnecessary computations or redundant calls",
            "Verify proper resource cleanup (files, connections, locks)",
            "Identify potential deadlock or race conditions",
            "Check for inefficient data structures or patterns"
        ]
    },
    "quality": {
        "name": "Code Quality Analysis",
        "keywords": ["quality", "style", "complexity", "documentation", "test", "coverage", "lint", "format", "clean", "maintainable"],
        "focus_areas": ["Style consistency", "Readability", "Complexity metrics", "Documentation", "Test coverage", "Maintainability"],
        "checklist": [
            "Check naming conventions and consistency",
            "Evaluate code readability and clarity",
            "Measure cyclomatic and cognitive complexity",
            "Verify function and class documentation",
            "Check for proper type hints or annotations",
            "Evaluate test coverage and test quality",
            "Check for code duplication (DRY principle)",
            "Verify error handling completeness",
            "Check for magic numbers and string literals",
            "Evaluate code organization and modularity"
        ]
    },
    "architecture": {
        "name": "Architecture Review",
        "keywords": ["architecture", "design pattern", "coupling", "cohesion", "scalable", "modular", "dependency", "layer", "structure"],
        "focus_areas": ["Design patterns", "Modularity", "Dependencies", "Scalability", "Maintainability", "Separation of concerns"],
        "checklist": [
            "Evaluate use of appropriate design patterns",
            "Check coupling between modules/components",
            "Assess cohesion within classes and functions",
            "Verify separation of concerns",
            "Check for circular dependencies",
            "Evaluate API design and contracts",
            "Assess scalability and extensibility",
            "Check for proper abstraction layers",
            "Evaluate database schema design if applicable",
            "Verify configuration and environment management"
        ]
    },
    "logic": {
        "name": "Logic Verification",
        "keywords": ["logic", "correctness", "edge case", "error handling", "bug", "business", "validation", "state", "flow"],
        "focus_areas": ["Business logic correctness", "Boundary conditions", "Error handling", "State management", "Data flow"],
        "checklist": [
            "Verify business logic correctness",
            "Check boundary conditions and edge cases",
            "Validate input ranges and constraints",
            "Verify error handling paths",
            "Check state management consistency",
            "Validate transaction boundaries",
            "Check for race conditions in state changes",
            "Verify null/undefined/empty handling",
            "Check for off-by-one errors",
            "Validate conditional logic completeness"
        ]
    }
}


def detect_language(code_or_path: str) -> str:
    """Detect programming language from file extension or code syntax."""
    extension_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "JavaScript (React)",
        ".tsx": "TypeScript (React)",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".c": "C",
        ".cpp": "C++",
        ".h": "C/C++ Header",
        ".cs": "C#",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".r": "R",
        ".sql": "SQL",
        ".sh": "Shell",
        ".ps1": "PowerShell",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".json": "JSON",
        ".xml": "XML",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sass": "Sass",
        ".vue": "Vue",
        ".svelte": "Svelte"
    }

    # Check if it's a file path
    path = Path(code_or_path)
    if path.suffix in extension_map:
        return extension_map[path.suffix]

    # Detect from code syntax
    if re.search(r'def\s+\w+\s*\(', code_or_path):
        return "Python"
    elif re.search(r'function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=', code_or_path):
        if re.search(r':\s*(string|number|boolean|any|void)', code_or_path):
            return "TypeScript"
        return "JavaScript"
    elif re.search(r'public\s+static|private\s+|class\s+\w+.*\{', code_or_path):
        return "Java"
    elif re.search(r'func\s+\w+\s*\(|package\s+main', code_or_path):
        return "Go"
    elif re.search(r'fn\s+\w+|let\s+mut|impl\s+\w+', code_or_path):
        return "Rust"
    elif re.search(r'select\s+.*from|insert\s+into|update\s+.*set', code_or_path, re.IGNORECASE):
        return "SQL"

    return "Unknown"


def identify_dimensions(user_request: str, code: str = "") -> List[str]:
    """Identify relevant analysis dimensions from user request."""
    request_lower = user_request.lower()
    selected = []

    for dim_key, dim_info in DIMENSIONS.items():
        if any(keyword.lower() in request_lower for keyword in dim_info["keywords"]):
            selected.append(dim_key)

    # If no specific dimensions found, include all
    if not selected:
        selected = list(DIMENSIONS.keys())

    return selected


def generate_task(dimension: str, code: str, language: str, file_path: Optional[str] = None) -> Dict:
    """Generate a complete analysis task for a dimension."""
    dim_info = DIMENSIONS[dimension]

    context = f"File: {file_path}\n" if file_path else ""
    context += f"Language: {language}\n\n"
    context += f"```\n{code}\n```"

    task = {
        "dimension": dim_info["name"],
        "focus_areas": dim_info["focus_areas"],
        "code_context": context,
        "checklist": dim_info["checklist"],
        "output_template": {
            "issues_found": [
                {
                    "id": "1",
                    "title": "Issue title",
                    "location": "Line X or Function Y",
                    "severity": "Critical/High/Medium/Low",
                    "description": "Detailed description of the issue",
                    "recommendation": "Specific fix recommendation"
                }
            ],
            "positive_findings": [
                "What's done well in this dimension"
            ],
            "dimension_score": "Optional: 1-10 rating",
            "summary": "Brief summary of findings"
        }
    }

    return task


def generate_all_tasks(user_request: str, code: str, file_path: Optional[str] = None) -> Dict:
    """Generate parallel tasks for all relevant dimensions."""
    language = detect_language(file_path or code)
    dimensions = identify_dimensions(user_request, code)

    result = {
        "language": language,
        "dimensions_analyzed": dimensions,
        "tasks": {}
    }

    for dim in dimensions:
        result["tasks"][dim] = generate_task(dim, code, language, file_path)

    return result


def format_task_markdown(task_data: Dict) -> str:
    """Format task data as markdown for agent consumption."""
    lines = []

    for dim_key, task in task_data["tasks"].items():
        lines.append(f"## Parallel Task: {task['dimension']}")
        lines.append("")
        lines.append(f"**Focus Areas:** {', '.join(task['focus_areas'])}")
        lines.append("")
        lines.append("### Code Context")
        lines.append(task["code_context"])
        lines.append("")
        lines.append("### Analysis Checklist")
        for item in task["checklist"]:
            lines.append(f"- [ ] {item}")
        lines.append("")
        lines.append("### Output Template")
        lines.append("```json")
        lines.append(json.dumps(task["output_template"], indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate parallel code analysis tasks")
    parser.add_argument("--request", required=True, help="User's analysis request")
    parser.add_argument("--code", default="", help="Code snippet or file path")
    parser.add_argument("--file", help="File path to analyze")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format")

    args = parser.parse_args()

    code = args.code
    if args.file and not code:
        file_path = Path(args.file)
        if file_path.exists():
            code = file_path.read_text(encoding="utf-8")
        else:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

    if not code:
        print("Error: No code provided. Use --code or --file.", file=sys.stderr)
        sys.exit(1)

    tasks = generate_all_tasks(args.request, code, args.file)

    if args.format == "json":
        output = json.dumps(tasks, indent=2, ensure_ascii=False)
    else:
        output = format_task_markdown(tasks)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Tasks written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
