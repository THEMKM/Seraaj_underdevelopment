#!/usr/bin/env python3
"""
Test Runner Script for Seraaj API
Provides convenient ways to run different test suites
"""
import subprocess
import sys
import argparse
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle the output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def install_dependencies():
    """Install test dependencies"""
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.20.0",
        "pytest-cov>=4.0.0",
        "httpx>=0.24.0",
        "websockets>=11.0.0",
        "psutil>=5.9.0"  # For performance tests
    ]
    
    print("Installing test dependencies...")
    for dep in dependencies:
        command = f"pip install {dep}"
        if not run_command(command, f"Installing {dep}"):
            print(f"⚠️  Warning: Failed to install {dep}")


def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """Run different types of tests"""
    
    base_command = "python -m pytest"
    
    # Add verbosity
    if verbose:
        base_command += " -v"
    else:
        base_command += " -q"
    
    # Add coverage
    if coverage:
        base_command += " --cov=. --cov-report=html --cov-report=term-missing"
    
    # Add parallel execution
    if parallel:
        base_command += " -n auto"
    
    test_commands = {
        "all": {
            "command": f"{base_command} tests/",
            "description": "All tests"
        },
        "unit": {
            "command": f"{base_command} tests/ -m 'not integration and not performance'",
            "description": "Unit tests only"
        },
        "integration": {
            "command": f"{base_command} tests/test_integration.py -m integration",
            "description": "Integration tests"
        },
        "performance": {
            "command": f"{base_command} tests/test_performance.py -m performance",
            "description": "Performance tests"
        },
        "auth": {
            "command": f"{base_command} tests/test_auth.py",
            "description": "Authentication tests"
        },
        "opportunities": {
            "command": f"{base_command} tests/test_opportunities.py",
            "description": "Opportunities API tests"
        },
        "applications": {
            "command": f"{base_command} tests/test_applications.py",
            "description": "Applications API tests"
        },
        "verification": {
            "command": f"{base_command} tests/test_verification.py",
            "description": "Verification system tests"
        },
        "websocket": {
            "command": f"{base_command} tests/test_websocket.py",
            "description": "WebSocket tests"
        },
        "fast": {
            "command": f"{base_command} tests/ -m 'not slow and not performance'",
            "description": "Fast tests only (excluding slow and performance tests)"
        }
    }
    
    if test_type not in test_commands:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available test types: {', '.join(test_commands.keys())}")
        return False
    
    test_info = test_commands[test_type]
    return run_command(test_info["command"], test_info["description"])


def generate_test_report():
    """Generate comprehensive test report"""
    print("\n🧪 Generating comprehensive test report...")
    
    # Run tests with coverage and generate reports
    commands = [
        {
            "command": "python -m pytest tests/ --cov=. --cov-report=html --cov-report=xml --cov-report=term-missing --junitxml=test-results.xml",
            "description": "Running full test suite with coverage"
        },
        {
            "command": "python -m pytest tests/test_performance.py -m performance --tb=short",
            "description": "Running performance tests"
        }
    ]
    
    for cmd_info in commands:
        if not run_command(cmd_info["command"], cmd_info["description"]):
            print(f"⚠️  Warning: {cmd_info['description']} failed")
    
    print("\n📊 Test report generated!")
    print("- HTML coverage report: htmlcov/index.html")
    print("- XML coverage report: coverage.xml")
    print("- JUnit XML report: test-results.xml")


def run_test_quality_checks():
    """Run code quality checks on test files"""
    print("\n🔍 Running test quality checks...")
    
    checks = [
        {
            "command": "python -m flake8 tests/ --max-line-length=120 --ignore=E501,W503",
            "description": "Checking test code style with flake8"
        },
        {
            "command": "python -m pytest --collect-only -q",
            "description": "Validating test collection"
        }
    ]
    
    for check in checks:
        run_command(check["command"], check["description"])


def run_smoke_tests():
    """Run basic smoke tests to verify system is working"""
    print("\n💨 Running smoke tests...")
    
    smoke_tests = [
        "tests/test_auth.py::TestAuthenticationEndpoints::test_user_registration_volunteer_success",
        "tests/test_opportunities.py::TestOpportunityEndpoints::test_get_opportunities_list_public",
        "tests/test_applications.py::TestApplicationEndpoints::test_create_application_success"
    ]
    
    for test in smoke_tests:
        command = f"python -m pytest {test} -v"
        if not run_command(command, f"Smoke test: {test.split('::')[-1]}"):
            print("❌ Smoke test failed - system may have issues")
            return False
    
    print("✅ All smoke tests passed!")
    return True


def setup_test_environment():
    """Set up the test environment"""
    print("🔧 Setting up test environment...")
    
    # Create necessary directories
    os.makedirs("tests/temp", exist_ok=True)
    os.makedirs("tests/fixtures", exist_ok=True)
    os.makedirs("htmlcov", exist_ok=True)
    
    # Install dependencies
    install_dependencies()
    
    print("✅ Test environment setup complete!")


def main():
    parser = argparse.ArgumentParser(description="Seraaj API Test Runner")
    parser.add_argument(
        "command",
        choices=["setup", "test", "report", "quality", "smoke", "install"],
        help="Command to run"
    )
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "performance", "auth", "opportunities", 
                "applications", "verification", "websocket", "fast"],
        default="all",
        help="Type of tests to run (only for 'test' command)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Include coverage reporting"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch for file changes and re-run tests"
    )
    
    args = parser.parse_args()
    
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    if args.command == "setup":
        setup_test_environment()
    
    elif args.command == "install":
        install_dependencies()
    
    elif args.command == "test":
        if args.watch:
            # Install pytest-watch if needed
            run_command("pip install pytest-watch", "Installing pytest-watch")
            # Use pytest-watch for continuous testing
            command = f"ptw tests/ --runner='python -m pytest {args.type if args.type != 'all' else 'tests/'}"
            if args.verbose:
                command += " -v"
            command += "'"
            run_command(command, "Running tests in watch mode")
        else:
            success = run_tests(args.type, args.verbose, args.coverage, args.parallel)
            sys.exit(0 if success else 1)
    
    elif args.command == "report":
        generate_test_report()
    
    elif args.command == "quality":
        run_test_quality_checks()
    
    elif args.command == "smoke":
        success = run_smoke_tests()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()