#!/usr/bin/env python3
"""
Fix Code Script

This script automatically fixes code issues including:
- ruff formatting
- black formatting
- import sorting
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
    """Main function to fix code issues."""
    print("🔧 Starting Code Fixes...")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    fixes = [
        (["ruff", "format", "."], "Ruff Formatting"),
        (["ruff", "check", "--fix", "."], "Ruff Auto-fix"),
        (["black", "."], "Black Formatting"),
        (["ruff", "check", "--select", "I", "--fix", "."], "Import Sorting"),
        (["ruff", "check", "--fix", "."], "Ruff Auto-fix"),
        (["ruff", "format", "."], "Ruff Formatting"),
    ]

    failed_fixes = []

    for command, description in fixes:
        if not run_command(command, description):
            failed_fixes.append(description)

    print(f"\n{'=' * 50}")
    print("📊 SUMMARY")
    print("=" * 50)

    if failed_fixes:
        print("❌ Failed fixes:")
        for fix in failed_fixes:
            print(f"  - {fix}")
        print(
            f"\nTotal: {len(failed_fixes)} failed, {len(fixes) - len(failed_fixes)} successful"
        )
        sys.exit(1)
    else:
        print("✅ All fixes applied successfully!")
        print(f"Total: {len(fixes)} fixes applied")

    print("\n💡 Next steps:")
    print("1. Review the changes")
    print("2. Run tests: pytest")
    print("3. Run clean code check: python scripts/clean_code.py")


if __name__ == "__main__":
    main()
