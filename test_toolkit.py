#!/usr/bin/env python3
"""
test_toolkit.py — Standalone Unit & Integration Test Suite
VirgoYT OSINT Toolkit v4.0
Developer Credit: VIRGOYT707

Usage:
    python3 test_toolkit.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from virgoyt.test_suite import run_all_tests

def main():
    res = run_all_tests()
    if res["failed"] > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
