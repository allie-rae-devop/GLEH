#!/usr/bin/env python3
"""
GLEH Startup Manager
Automates session bootstrap: device detection, .env check, git status, progress display
"""

import os
import sys
import subprocess
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print styled header"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}[!] {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}[X] {text}{Colors.END}")

def check_env_file():
    """Check if .env file exists"""
    env_path = Path('.env')

    if not env_path.exists():
        print_header("POTENTIAL NEW DEVICE DETECTED")
        print_error(".env file is missing!")
        print("\nThis usually means:")
        print("  1. You're on a new device")
        print("  2. You need to restore configuration from Samba backup")
        print("  3. The .env file was accidentally deleted\n")

        response = input(f"{Colors.YELLOW}Would you like to run restore_from_samba.ps1 now? (y/n): {Colors.END}").lower()

        if response == 'y':
            print(f"\n{Colors.CYAN}Running restore script...{Colors.END}\n")
            try:
                subprocess.run(['powershell.exe', '-File', 'restore_from_samba.ps1'], check=True)
                print_success("Restore complete! .env and database files restored from Samba.")
                return True
            except subprocess.CalledProcessError as e:
                print_error(f"Restore script failed: {e}")
                print("\nYou can run it manually: .\\restore_from_samba.ps1")
                return False
        else:
            print(f"\n{Colors.YELLOW}Skipping restore. Run manually when ready: .\\restore_from_samba.ps1{Colors.END}")
            return False
    else:
        print_success(".env file present")
        return True

def check_git_status():
    """Check git status"""
    try:
        result = subprocess.run(['git', 'status', '--short'],
                              capture_output=True,
                              text=True,
                              check=True)

        if result.stdout.strip():
            print_warning("Uncommitted changes detected:")
            print(f"\n{result.stdout}")
        else:
            print_success("Git working directory clean")

        # Check branch
        branch_result = subprocess.run(['git', 'branch', '--show-current'],
                                      capture_output=True,
                                      text=True,
                                      check=True)
        branch = branch_result.stdout.strip()
        print_success(f"Current branch: {branch}")

    except subprocess.CalledProcessError as e:
        print_error(f"Git status check failed: {e}")

def read_progress_log():
    """Read and display current phase from PROGRESS_LOG.md"""
    progress_path = Path('PROGRESS_LOG.md')

    if not progress_path.exists():
        print_warning("PROGRESS_LOG.md not found")
        return

    try:
        with open(progress_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for the most recent session header
        lines = content.split('\n')
        current_phase = None
        current_status = None

        for i, line in enumerate(lines):
            if '## Session' in line and '- Phase' in line:
                current_phase = line.strip()
            if '### Status:' in line and i + 1 < len(lines):
                current_status = lines[i].strip()
                break

        print_header("Current Project Status")

        if current_phase:
            print(f"{Colors.BOLD}Phase:{Colors.END} {current_phase}")
        else:
            print(f"{Colors.BOLD}Phase:{Colors.END} Check PROGRESS_LOG.md for details")

        if current_status:
            print(f"{Colors.BOLD}Status:{Colors.END} {current_status}")

        # Find the latest "What we accomplished" or "Next Steps" section
        for i, line in enumerate(lines):
            if '**What we accomplished' in line or '**Next Steps' in line:
                print(f"\n{Colors.CYAN}{line}{Colors.END}")
                # Print next few lines
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        print(lines[j])
                    if lines[j].startswith('##'):
                        break
                break

    except Exception as e:
        print_error(f"Failed to read PROGRESS_LOG.md: {e}")

def main():
    """Main startup routine"""
    print_header("GLEH Startup Manager")
    print(f"{Colors.BOLD}Working Directory:{Colors.END} {os.getcwd()}\n")

    # Step 1: Check .env file
    print(f"{Colors.CYAN}[1/3] Checking configuration...{Colors.END}")
    env_exists = check_env_file()

    if not env_exists:
        print(f"\n{Colors.YELLOW}Setup incomplete. Please restore .env file before continuing.{Colors.END}\n")
        sys.exit(1)

    # Step 2: Check git status
    print(f"\n{Colors.CYAN}[2/3] Checking git status...{Colors.END}")
    check_git_status()

    # Step 3: Display current progress
    print(f"\n{Colors.CYAN}[3/3] Loading project status...{Colors.END}")
    read_progress_log()

    # Final message
    print_header("Startup Complete")
    print_success("Environment validated")
    print_success("Git status checked")
    print_success("Current phase loaded")
    print(f"\n{Colors.GREEN}Ready to work on GLEH!{Colors.END}\n")
    print(f"{Colors.CYAN}Next: Review PROJECT_INDEX.md for file locations{Colors.END}")
    print(f"{Colors.CYAN}Or: Check PROGRESS_LOG.md for detailed history{Colors.END}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Startup cancelled by user{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Startup failed: {e}")
        sys.exit(1)
