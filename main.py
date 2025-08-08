import os
import sys

# Ensure the backend app package can be discovered when running tests from repo root
ROOT_BACKEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_interface', 'backend')
if ROOT_BACKEND not in sys.path:
    sys.path.insert(0, ROOT_BACKEND)

from web_interface.backend.main import app

__all__ = ["app"]