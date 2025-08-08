import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from mova_sdk.core.engine import Engine

def parse_args():
    parser = argparse.ArgumentParser(prog="mova-cli", description="MOVA SDK Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    
    run_parser = subparsers.add_parser("run", help="Execute task with payload")
    run_parser.add_argument("payload", help="Input data (JSON string or file path)")
    run_parser.add_argument("--cache-key", help="Optional cache key for results")

    subparsers.add_parser("status", help="Check engine status")
    subparsers.add_parser("version", help="Show SDK version")
    
    return parser.parse_args()

def load_payload(payload_str: str):
    try:
        if Path(payload_str).exists():
            with open(payload_str) as f:
                return json.load(f)
        return json.loads(payload_str)
    except json.JSONDecodeError:
        print("\033[91mError: Invalid JSON format\033[0m", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\033[91mError loading payload: {e}\033[0m", file=sys.stderr)
        sys.exit(1)

def main() -> int:
    try:
        args = parse_args()
        engine = Engine()
        
        if args.command == "run":
            payload = load_payload(args.payload)
            if args.cache_key:
                payload = {"cache_key": args.cache_key, "value": payload}
            result = engine.run(payload)
            print("\033[92m" + json.dumps(result, indent=2) + "\033[0m")
        
        elif args.command == "status":
            print(f"\033[94mEngine status: {engine.status()}\033[0m")
        
        elif args.command == "version":
            from importlib.metadata import version
            print(f"\033[94mMOVA SDK version: {version('mova-sdk')}\033[0m")
        
        return 0
    except Exception as e:
        print(f"\033[91mCLI error: {e}\033[0m", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())