"""
Test & Validation Script for Lottery Intelligence System
Run this before deployment to verify all components are working
"""

import sys
import importlib
from pathlib import Path


class SystemValidator:
    """Validates that the Lottery Intelligence System is properly configured"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        
    def check(self, name, condition, error_msg=""):
        """Generic check utility"""
        if condition:
            print(f"  ✓ {name}")
            self.checks_passed += 1
        else:
            print(f"  ✗ {name}")
            if error_msg:
                print(f"     Error: {error_msg}")
            self.checks_failed += 1
            
    def warning(self, name, msg=""):
        """Log a warning without failing validation"""
        print(f"  ⚠ {name}")
        if msg:
            print(f"     {msg}")
        self.warnings += 1


def check_python_version(validator):
    """Verify Python version compatibility"""
    print("\n[1/7] Checking Python Version...")
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    validator.check(
        f"Python {current_version[0]}.{current_version[1]}",
        current_version >= required_version,
        f"Python 3.8+ required (you have {current_version[0]}.{current_version[1]})"
    )


def check_dependencies(validator):
    """Check if all required packages are installed"""
    print("\n[2/7] Checking Dependencies...")
    
    required_packages = {
        'undetected_chromedriver': 'undetected-chromedriver',
        'requests': 'requests',
        'PyPDF2': 'PyPDF2',
        'pandas': 'pandas',
        'gspread': 'gspread',
        'oauth2client': 'oauth2client',
    }
    
    for import_name, package_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            validator.check(f"{package_name} installed", True)
        except ImportError:
            validator.check(
                f"{package_name} installed",
                False,
                f"Run: pip install {package_name}"
            )


def check_credentials(validator):
    """Verify credentials.json exists and is valid"""
    print("\n[3/7] Checking Credentials...")
    
    creds_path = Path("credentials.json")
    validator.check(
        "credentials.json exists",
        creds_path.exists(),
        "Create credentials.json from Google Cloud Console"
    )
    
    if creds_path.exists():
        try:
            import json
            with open("credentials.json") as f:
                creds = json.load(f)
                
            required_fields = [
                'type',
                'project_id',
                'private_key_id',
                'private_key',
                'client_email',
                'client_id'
            ]
            
            all_present = all(field in creds for field in required_fields)
            validator.check(
                "credentials.json is valid",
                all_present,
                "Missing required fields in credentials.json"
            )
            
            validator.check(
                "Service account type is correct",
                creds.get('type') == 'service_account',
                "credentials.json must be for a service account"
            )
            
        except Exception as e:
            validator.check("credentials.json is valid", False, str(e))


def check_files(validator):
    """Verify all required project files exist"""
    print("\n[4/7] Checking Project Files...")
    
    required_files = {
        'main.py': 'Main automation script',
        'requirements.txt': 'Dependencies list',
        'README.md': 'Documentation',
        'QUICKSTART.md': 'Quick start guide',
        'config.py': 'Configuration template',
        'test_system.py': 'This test script',
    }
    
    for filename, description in required_files.items():
        path = Path(filename)
        validator.check(f"{filename}", path.exists(), f"{description}")


def check_chrome(validator):
    """Verify Chrome/Chromium is installed"""
    print("\n[5/7] Checking Chrome/Chromium Installation...")
    
    import platform
    system = platform.system()
    
    # Try to import undetected chromedriver to test Chrome availability
    try:
        import undetected_chromedriver as uc
        
        # This will fail if Chrome is not installed
        try:
            # Try to find Chrome (don't actually launch it)
            chrome_path = uc.find_chrome_executable()
            validator.check(f"Chrome found at: {chrome_path}", True)
        except:
            if system == "Windows":
                validator.warning(
                    "Chrome not found in standard locations",
                    "Install from https://www.google.com/chrome/"
                )
            else:
                validator.warning(
                    "Chrome/Chromium not found",
                    f"Install the latest Chrome or Chromium for {system}"
                )
                
    except ImportError:
        validator.check(
            "undetected-chromedriver available",
            False,
            "Run: pip install undetected-chromedriver"
        )


def check_network(validator):
    """Test network connectivity"""
    print("\n[6/7] Checking Network Connectivity...")
    
    import socket
    
    # Test DNS resolution
    try:
        socket.gethostbyname('lotterysambad.com')
        validator.check("DNS resolution works", True)
    except socket.gaierror:
        validator.check(
            "DNS resolution works",
            False,
            "Cannot resolve lotterysambad.com. Check internet connection."
        )
    
    # Test Google Sheets API connectivity
    try:
        socket.gethostbyname('sheets.googleapis.com')
        validator.check("Can reach Google Sheets API", True)
    except socket.gaierror:
        validator.check(
            "Can reach Google Sheets API",
            False,
            "Cannot reach Google Sheets. Check firewall/VPN."
        )


def check_configuration(validator):
    """Check configuration file"""
    print("\n[7/7] Checking Configuration...")
    
    config_path = Path("config.py")
    validator.check(
        "config.py exists (optional)",
        config_path.exists(),
        "You can use config.py to customize settings"
    )
    
    if config_path.exists():
        try:
            import config
            
            # Check key configuration items
            checks = [
                ('HOMEPAGE_URL', hasattr(config, 'HOMEPAGE_URL')),
                ('SHEET_NAME', hasattr(config, 'SHEET_NAME')),
                ('WINNING_NUMBER_PATTERN', hasattr(config, 'WINNING_NUMBER_PATTERN')),
            ]
            
            for attr_name, exists in checks:
                validator.check(f"config.{attr_name} defined", exists)
                
        except Exception as e:
            validator.warning("config.py validation", f"Could not import: {str(e)}")


def print_summary(validator):
    """Print validation summary"""
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    total = validator.checks_passed + validator.checks_failed
    
    if validator.checks_failed == 0:
        print(f"\n✓ ALL CHECKS PASSED ({validator.checks_passed}/{total})")
        if validator.warnings > 0:
            print(f"⚠ {validator.warnings} warning(s) - review above\n")
        else:
            print("\nYou're ready to run: python main.py\n")
        return True
    else:
        print(f"\n✗ VALIDATION FAILED ({validator.checks_passed}/{total})")
        print(f"\nFailed checks: {validator.checks_failed}")
        print(f"Warnings: {validator.warnings}")
        print("\nPlease fix the issues above before running main.py\n")
        return False


def main():
    """Run all validation checks"""
    print("\n" + "#"*60)
    print("# LOTTERY INTELLIGENCE SYSTEM - VALIDATION TEST")
    print("#"*60)
    
    validator = SystemValidator()
    
    # Run all checks
    check_python_version(validator)
    check_dependencies(validator)
    check_credentials(validator)
    check_files(validator)
    check_chrome(validator)
    check_network(validator)
    check_configuration(validator)
    
    # Print summary and return status
    success = print_summary(validator)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
