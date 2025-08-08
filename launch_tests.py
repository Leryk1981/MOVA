#!/usr/bin/env python3
import sys
import os
import pytest

def ensure_paths():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    web_root = os.path.join(repo_root, 'web_interface')
    # Normalize to absolute strings
    paths = [repo_root, web_root]
    for p in paths:
        if p not in sys.path:
            sys.path.insert(0, p)
    # Verify that import of web_interface is possible
    try:
        import web_interface  # noqa: F401
    except Exception as e:
        # Try one more time by forcing the web_interface path
        if web_root not in sys.path:
            sys.path.insert(0, web_root)
        try:
            import web_interface  # noqa: F401
        except Exception as e2:
            print(f"ERROR: cannot import web_interface after path adjustments: {e2}", file=sys.stderr)
            raise
    return repo_root

def main():
    ensure_paths()
    # Execute targeted tests
    rc = pytest.main(['-q',
                      'web_interface/backend/tests/test_dashboard_api.py',
                      'web_interface/backend/tests/test_e2e_integration.py'])
    raise SystemExit(rc)

if __name__ == "__main__":
    main()