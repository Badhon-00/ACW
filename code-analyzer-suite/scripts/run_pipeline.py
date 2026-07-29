#!/usr/bin/env python3
"""
Code Analyzer Pipeline Orchestrator
Runs the complete parallel analysis workflow.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_generate_tasks(request: str, code: str, file_path: str = None, output_dir: Path = None) -> Path:
    """Run task generation step."""
    print("[Pipeline] Generating parallel analysis tasks...")

    cmd = [
        sys.executable, "-m", "generate_tasks",
        "--request", request,
        "--code", code,
        "--format", "json"
    ]

    if file_path:
        cmd.extend(["--file", file_path])

    tasks_file = output_dir / "tasks.json"
    cmd.extend(["--output", str(tasks_file)])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)

    if result.returncode != 0:
        print(f"[Pipeline] Task generation failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"[Pipeline] Tasks generated: {tasks_file}")
    return tasks_file


def run_dimension_analysis(tasks_file: Path, dimension: str, output_dir: Path) -> Path:
    """Run analysis for a single dimension (placeholder for agent execution)."""
    print(f"[Pipeline] Running {dimension} analysis...")

    # In practice, this would spawn an agent window with the task
    # For now, create a placeholder result
    result = {
        "dimension": dimension,
        "issues": [],
        "positive_findings": ["Analysis completed"],
        "score": None
    }

    result_file = output_dir / f"{dimension}-result.json"
    result_file.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"[Pipeline] {dimension} result: {result_file}")
    return result_file


def run_consolidation(result_files: list, output_path: Path) -> Path:
    """Run report consolidation step."""
    print("[Pipeline] Consolidating reports...")

    cmd = [
        sys.executable, "-m", "consolidate_report",
        *[str(f) for f in result_files],
        "--output", str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)

    if result.returncode != 0:
        print(f"[Pipeline] Consolidation failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"[Pipeline] Consolidated report: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Run complete code analysis pipeline")
    parser.add_argument("--request", required=True, help="User's analysis request")
    parser.add_argument("--code", default="", help="Code snippet")
    parser.add_argument("--file", help="File path to analyze")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--dimensions", nargs="+", help="Specific dimensions to run")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate tasks
    code = args.code
    if args.file and not code:
        file_path = Path(args.file)
        if file_path.exists():
            code = file_path.read_text(encoding="utf-8")

    tasks_file = run_generate_tasks(args.request, code, args.file, output_dir)

    # Step 2: Load tasks and run dimension analyses
    tasks_data = json.loads(tasks_file.read_text(encoding="utf-8"))
    dimensions = args.dimensions or tasks_data.get("dimensions_analyzed", [])

    result_files = []
    for dim in dimensions:
        result_file = run_dimension_analysis(tasks_file, dim, output_dir)
        result_files.append(result_file)

    # Step 3: Consolidate
    report_path = output_dir / "consolidated-report.md"
    run_consolidation(result_files, report_path)

    print(f"\n[Pipeline] Complete! Report: {report_path}")


if __name__ == "__main__":
    main()
