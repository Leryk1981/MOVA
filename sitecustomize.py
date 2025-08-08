import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_ROOT = os.path.join(ROOT, 'web_interface')

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if WEB_ROOT not in sys.path:
    sys.path.insert(0, WEB_ROOT)