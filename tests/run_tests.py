#!/usr/bin/env python3
"""
Test runner for MOVA SDK
Запускач тестів для MOVA SDK
"""

import sys
import os
import argparse
import unittest
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False


def run_pytest_tests(test_path=None, verbose=False, coverage=False):
    """
    Run tests using pytest
    Запустити тести за допомогою pytest
    
    Args:
        test_path: Path to tests / Шлях до тестів
        verbose: Verbose output / Детальний вивід
        coverage: Enable coverage report / Увімкнути звіт про покриття
        
    Returns:
        Exit code / Код виходу
    """
    if not PYTEST_AVAILABLE:
        print("pytest is not available. Please install it with: pip install pytest")
        return 1
    
    # Build pytest arguments
    args = []
    
    if test_path:
        args.append(test_path)
    else:
        args.append("tests")
    
    if verbose:
        args.append("-v")
    
    if coverage and COVERAGE_AVAILABLE:
        args.append("--cov=mova")
        args.append("--cov-report=html")
        args.append("--cov-report=term-missing")
    elif coverage and not COVERAGE_AVAILABLE:
        print("coverage is not available. Please install it with: pip install coverage")
    
    # Run pytest
    exit_code = pytest.main(args)
    
    return exit_code


def run_unittest_tests(test_path=None, verbose=False):
    """
    Run tests using unittest
    Запустити тести за допомогою unittest
    
    Args:
        test_path: Path to tests / Шлях до тестів
        verbose: Verbose output / Детальний вивід
        
    Returns:
        Exit code / Код виходу
    """
    # Build test loader
    loader = unittest.TestLoader()
    
    # Discover tests
    if test_path:
        if os.path.isfile(test_path):
            # Load specific test file
            suite = loader.loadTestsFromName(test_path.replace('/', '.').replace('.py', ''))
        else:
            # Load tests from directory
            suite = loader.discover(test_path, pattern='test_*.py')
    else:
        # Load all tests
        suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module, test_class=None, test_method=None, verbose=False):
    """
    Run specific test
    Запустити конкретний тест
    
    Args:
        test_module: Test module name / Назва тестового модуля
        test_class: Test class name / Назва тестового класу
        test_method: Test method name / Назва тестового методу
        verbose: Verbose output / Детальний вивід
        
    Returns:
        Exit code / Код виходу
    """
    if PYTEST_AVAILABLE:
        # Build test path
        test_path = f"tests/{test_module.replace('.', '/')}"
        
        if test_class:
            test_path += f"::{test_class}"
            
            if test_method:
                test_path += f"::{test_method}"
        
        # Run pytest
        args = [test_path]
        
        if verbose:
            args.append("-v")
        
        exit_code = pytest.main(args)
        return exit_code
    else:
        # Use unittest
        test_name = f"tests.{test_module}"
        
        if test_class:
            test_name += f".{test_class}"
            
            if test_method:
                test_name += f".{test_method}"
        
        # Run unittest
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_name)
        
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1


def list_tests():
    """
    List all available tests
    Показати всі доступні тести
    """
    print("Available tests:")
    print("===============")
    
    # List test modules
    test_dir = Path("tests")
    
    if test_dir.exists():
        for module_dir in test_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("__"):
                print(f"\n{module_dir.name}:")
                
                # List test files
                for test_file in module_dir.glob("test_*.py"):
                    test_name = test_file.stem
                    print(f"  - {module_dir.name}.{test_name}")
                    
                    # List test classes
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Find test classes
                        import re
                        class_pattern = r'class\s+(Test\w+)\('
                        classes = re.findall(class_pattern, content)
                        
                        for cls in classes:
                            print(f"    - {module_dir.name}.{test_name}.{cls}")
                            
                            # Find test methods
                            method_pattern = r'def\s+(test_\w+)\('
                            methods = re.findall(method_pattern, content)
                            
                            for method in methods:
                                print(f"      - {module_dir.name}.{test_name}.{cls}.{method}")


def main():
    """
    Main function
    Головна функція
    """
    parser = argparse.ArgumentParser(description="Run tests for MOVA SDK")
    parser.add_argument("--path", "-p", help="Path to tests (default: tests)")
    parser.add_argument("--module", "-m", help="Test module name")
    parser.add_argument("--class", "-c", help="Test class name")
    parser.add_argument("--method", help="Test method name")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Enable coverage report")
    parser.add_argument("--unittest", action="store_true", help="Use unittest instead of pytest")
    parser.add_argument("--list", action="store_true", help="List all available tests")
    
    args = parser.parse_args()
    
    # List tests if requested
    if args.list:
        list_tests()
        return 0
    
    # Run specific test if module is specified
    if args.module:
        test_class = getattr(args, 'class', None)
        return run_specific_test(args.module, test_class, args.method, args.verbose)
    
    # Run all tests
    if args.unittest or not PYTEST_AVAILABLE:
        return run_unittest_tests(args.path, args.verbose)
    else:
        return run_pytest_tests(args.path, args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())