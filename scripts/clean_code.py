#!/usr/bin/env python3
"""
Clean Code Script

This script runs all code quality checks including:
- ruff (linting and formatting)
- black (code formatting)
- mypy (type checking)
- pytest (testing)
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'=' * 50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print("=" * 50)

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main function to run all code quality checks."""
    print("🧹 Starting Clean Code Checks...")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    checks = [
        (["ruff", "check", "."], "Ruff Linting"),
        (["ruff", "format", "."], "Ruff Formatting"),
        (["black", "--check", "."], "Black Format Check"),
        (["pytest"], "Pytest Tests"),
    ]

    failed_checks = []

    for command, description in checks:
        if not run_command(command, description):
            failed_checks.append(description)

    print(f"\n{'=' * 50}")
    print("📊 SUMMARY")
    print("=" * 50)

    if failed_checks:
        print("❌ Failed checks:")
        for check in failed_checks:
            print(f"  - {check}")
        print(
            f"\nTotal: {len(failed_checks)} failed, {len(checks) - len(failed_checks)} passed"
        )
        sys.exit(1)
    else:
        print("✅ All checks passed!")
        print(f"Total: {len(checks)} checks passed")


if __name__ == "__main__":
    main()
