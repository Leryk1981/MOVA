#!/usr/bin/env python3
"""
Test Runner Script
Скрипт для запуску тестів
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests(test_type="all", coverage=False, parallel=False):
    """Run tests with specified options"""
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test type filters
    if test_type == "dashboard":
        cmd.extend(["-k", "dashboard"])
    elif test_type == "plugin":
        cmd.extend(["-k", "plugin"])
    elif test_type == "websocket":
        cmd.extend(["-k", "websocket"])
    elif test_type == "e2e":
        cmd.extend(["-k", "e2e"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type != "all":
        print(f"Unknown test type: {test_type}")
        return False
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add parallel execution if requested
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Add verbose output
    cmd.append("-v")
    
    print(f"Running tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run MOVA API integration tests")
    parser.add_argument(
        "--type", 
        choices=["all", "dashboard", "plugin", "websocket", "e2e", "integration"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="Run tests in parallel"
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting MOVA API Integration Tests")
    print(f"📋 Test type: {args.type}")
    print(f"📊 Coverage: {args.coverage}")
    print(f"⚡ Parallel: {args.parallel}")
    print("=" * 50)
    
    success = run_tests(args.type, args.coverage, args.parallel)
    
    if success:
        print("🎉 Test execution completed successfully!")
        sys.exit(0)
    else:
        print("💥 Test execution failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 