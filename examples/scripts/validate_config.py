#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate workflow configuration")
    parser.add_argument("--quiet", action="store_true", help="Only print failures")
    args = parser.parse_args()

    workspace_path = Path(__file__).resolve().parents[1]
    src_path = workspace_path / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from config.validators import validate_project_configuration

    issues = validate_project_configuration()
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]

    if not args.quiet:
        print(f"workspace: {workspace_path}")
        if not issues:
            print("configuration: OK")

    for issue in issues:
        print(f"[{issue.severity}] {issue.location}: {issue.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
