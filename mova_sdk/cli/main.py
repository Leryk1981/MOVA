from typing import Any, Optional
import json
import sys
from pathlib import Path

from mova_sdk.core.engine import Engine


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(prog="mova-cli", description="MOVA SDK CLI MVP integration")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Run command
    run_parser = subparsers.add_parser("run", help="Execute task with payload")
    run_parser.add_argument("payload", nargs='?', default=None, help="Input data (JSON string or path)")

    # Status command
    subparsers.add_parser("status", help="Check engine status")

    # Version command
    subparsers.add_parser("version", help="Show SDK version")

    return parser


def load_payload(payload_str: Optional[str]):
    """Load payload from JSON string or file."""
    if payload_str is None:
        return None
    try:
        if Path(payload_str).exists():
            with open(payload_str, "r") as f:
                return json.load(f)
        return json.loads(payload_str)
    except json.JSONDecodeError:
        print("\033[31mError: Invalid JSON format\033[0m", file=sys.stderr)
        raise SystemExit(1)
    except Exception as e:
        print(f"\033[31mError loading payload: {e}\033[0m", file=sys.stderr)
        raise SystemExit(1)


def get_version():
    """Return the SDK version from metadata if available."""
    try:
        from importlib.metadata import version
        return version("mova-sdk")
    except Exception:
        return "0.0.0"


def main() -> int:
    parser = parse_args()
    args = parser.parse_args()

    engine = Engine()

    if args.command == "run":
        payload = load_payload(args.payload)
        result = engine.run(payload)
        import json as _json
        print("\033[92m" + _json.dumps(result, indent=2) + "\033[0m")
        return 0

    if args.command == "status":
        print("\033[94mEngine status: " + engine.status() + "\033[0m")
        return 0

    if args.command == "version":
        ver = get_version()
        print("\033[94mMOVA SDK version: " + ver + "\033[0m")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())