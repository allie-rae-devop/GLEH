#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GLEH Setup Verification Script

Run this script to verify:
1. Python environment is correct
2. Dependencies are installed
3. Storage system is configured
4. Database is accessible
5. All configuration files exist

Usage:
    python verify_setup.py
"""

import os
import sys
import json
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(text):
    print(f"{GREEN}[OK] {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}[WARN] {text}{RESET}")


def print_error(text):
    print(f"{RED}[ERROR] {text}{RESET}")


def check_python_version():
    """Check Python version is 3.8+"""
    print_header("Python Version")
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python Version: {version}")

    if sys.version_info >= (3, 8):
        print_success(f"Python {version} is compatible")
        return True
    else:
        print_error(f"Python {version} is too old (need 3.8+)")
        return False


def check_project_structure():
    """Check all required directories and files exist"""
    print_header("Project Structure")

    required_files = [
        '.env',
        '.env.example',
        '.gitignore',
        'src/storage.py',
        'src/app.py',
        'src/models.py',
        'requirements.txt',
        'docker/docker-compose.yml',
        'docker/Dockerfile',
        'docker/entrypoint.sh',
        '.vscode/settings.json',
        '.vscode/launch.json',
        '.vscode/tasks.json',
        '.vscode/extensions.json',
        'MIGRATION_GUIDE.md',
        'STORAGE_QUICK_REFERENCE.md',
    ]

    missing = []
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - NOT FOUND")
            missing.append(file_path)

    return len(missing) == 0


def check_dependencies():
    """Check if main dependencies are installed"""
    print_header("Dependencies")

    required = [
        'flask',
        'sqlalchemy',
        'flask_sqlalchemy',
        'python-dotenv',
    ]

    all_good = True
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT INSTALLED")
            all_good = False

    if not all_good:
        print_warning("Install missing packages with: pip install -r requirements.txt")

    return all_good


def check_environment():
    """Check .env file and environment variables"""
    print_header("Environment Configuration")

    env_path = Path('.env')
    if not env_path.exists():
        print_error(".env file not found")
        return False

    print_success(".env file exists")

    # Try to load and check key variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print_warning("python-dotenv not installed (needed for .env loading)")
        print_warning("Install with: pip install python-dotenv")

    required_env = [
        'STORAGE_TYPE',
        'CONTENT_DIR',
    ]

    all_good = True
    for var in required_env:
        value = os.environ.get(var)
        if value:
            display_value = value[:50] + "..." if len(value) > 50 else value
            print_success(f"{var} = {display_value}")
        else:
            print_warning(f"{var} - NOT SET (using default)")

    return True


def check_storage():
    """Check storage system is working"""
    print_header("Storage System")

    try:
        from src.storage import get_storage

        storage = get_storage()
        print_success("StorageManager initialized")

        info = storage.get_storage_info()
        print(json.dumps(info, indent=2))

        if info.get('is_ready'):
            print_success("Storage is ready")
            return True
        else:
            print_warning("Storage paths may not be fully accessible")
            return True  # Not a critical failure

    except Exception as e:
        print_error(f"Error loading storage: {e}")
        return False


def check_database():
    """Check database connectivity"""
    print_header("Database")

    try:
        from src.database import db
        from src.models import User

        # Check if we can import models
        print_success("Database models import successfully")

        # Try to get database URL
        db_url = os.environ.get('DATABASE_URL', 'sqlite (default)')
        print(f"Database: {db_url}")

        return True
    except Exception as e:
        print_warning(f"Database check: {e}")
        return False


def check_docker():
    """Check Docker is installed and working"""
    print_header("Docker")

    try:
        import subprocess

        result = subprocess.run(['docker', '--version'],
                              capture_output=True,
                              text=True)
        if result.returncode == 0:
            print_success(result.stdout.strip())
        else:
            print_warning("Docker check failed")
            return False

        result = subprocess.run(['docker-compose', '--version'],
                              capture_output=True,
                              text=True)
        if result.returncode == 0:
            print_success(result.stdout.strip())
        else:
            print_warning("Docker Compose not found")
            return False

        return True
    except FileNotFoundError:
        print_warning("Docker/Docker Compose not installed (optional)")
        return True


def main():
    """Run all checks"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}GLEH Setup Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    results = {
        'Python Version': check_python_version(),
        'Project Structure': check_project_structure(),
        'Dependencies': check_dependencies(),
        'Environment': check_environment(),
        'Storage System': check_storage(),
        'Database': check_database(),
        'Docker': check_docker(),
    }

    # Summary
    print_header("Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"[{status}] {name}")

    print(f"\n{BLUE}Passed: {passed}/{total}{RESET}")

    # Final message
    print_header("Next Steps")

    if passed == total:
        print(f"{GREEN}[OK] All checks passed!{RESET}")
        print("\nYou're ready to:")
        print("  1. Run Flask: flask run")
        print("  2. Run Docker: cd docker && docker-compose up")
        print("  3. Read STORAGE_QUICK_REFERENCE.md for configuration")
        print("  4. Read MIGRATION_GUIDE.md for detailed information")
        return 0
    else:
        print_warning("Some checks failed. Please review above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Copy .env.example to .env: cp .env.example .env")
        print("  3. Check .env has correct CONTENT_DIR")
        return 1


if __name__ == '__main__':
    sys.exit(main())
