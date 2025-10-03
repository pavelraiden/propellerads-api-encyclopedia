#!/usr/bin/env python3
"""
PropellerAds API Encyclopedia - Deployment Verification Script
Comprehensive verification that everything is ready for production deployment
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path
from typing import List, Tuple, Dict

class DeploymentVerifier:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed_checks = []
        
    def log_pass(self, message: str):
        self.passed_checks.append(f"✅ {message}")
        print(f"✅ {message}")
        
    def log_warning(self, message: str):
        self.warnings.append(f"⚠️ {message}")
        print(f"⚠️ {message}")
        
    def log_error(self, message: str):
        self.issues.append(f"❌ {message}")
        print(f"❌ {message}")

    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        version = sys.version_info
        if version >= (3, 9):
            self.log_pass(f"Python version {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.log_error(f"Python {version.major}.{version.minor} not supported. Requires 3.9+")
            return False

    def check_required_files(self) -> bool:
        """Check all required files exist"""
        required_files = [
            'requirements.txt',
            '.env.template', 
            'setup.py',
            'launch_app.py',
            'launch_app.sh',
            'launch_app.bat',
            'QUICK_START.md',
            'README.md',
            'propellerads/__init__.py',
            'web_interface/app.py'
        ]
        
        all_exist = True
        for file in required_files:
            if Path(file).exists():
                self.log_pass(f"Required file: {file}")
            else:
                self.log_error(f"Missing required file: {file}")
                all_exist = False
                
        return all_exist

    def check_dependencies(self) -> bool:
        """Check all dependencies can be imported"""
        required_modules = [
            'requests',
            'pydantic', 
            'anthropic',
            'flask',
            'flask_socketio',
            'pytest',
            'dotenv'
        ]
        
        all_imported = True
        for module in required_modules:
            try:
                # Special handling for flask_socketio
                if module == 'flask_socketio':
                    import flask_socketio
                else:
                    importlib.import_module(module.replace('_', '-'))
                self.log_pass(f"Dependency: {module}")
            except ImportError:
                self.log_error(f"Missing dependency: {module}")
                all_imported = False
                
        return all_imported

    def check_propellerads_sdk(self) -> bool:
        """Check PropellerAds SDK functionality"""
        try:
            from propellerads import __version__
            from propellerads.client import PropellerAdsClient
            from propellerads.schemas.base import BaseResponse
            
            self.log_pass(f"PropellerAds SDK v{__version__}")
            self.log_pass("PropellerAds client import")
            self.log_pass("PropellerAds schemas import")
            return True
        except Exception as e:
            self.log_error(f"PropellerAds SDK issue: {e}")
            return False

    def check_web_interface(self) -> bool:
        """Check web interface can be imported"""
        try:
            sys.path.append('web_interface')
            import app
            self.log_pass("Web interface import")
            return True
        except Exception as e:
            self.log_error(f"Web interface issue: {e}")
            return False

    def check_launcher_scripts(self) -> bool:
        """Check launcher scripts are executable"""
        scripts = ['launch_app.py', 'launch_app.sh', 'setup.py']
        all_executable = True
        
        for script in scripts:
            if Path(script).exists():
                if os.access(script, os.X_OK):
                    self.log_pass(f"Executable: {script}")
                else:
                    self.log_warning(f"Not executable: {script} (may need chmod +x)")
            else:
                self.log_error(f"Missing launcher: {script}")
                all_executable = False
                
        return all_executable

    def check_environment_template(self) -> bool:
        """Check .env.template is properly configured"""
        template_file = Path('.env.template')
        if not template_file.exists():
            self.log_error(".env.template file missing")
            return False
            
        content = template_file.read_text()
        required_vars = ['MainAPI', 'ANTHROPIC_API_KEY']
        
        all_vars_present = True
        for var in required_vars:
            if var in content:
                self.log_pass(f"Environment variable template: {var}")
            else:
                self.log_error(f"Missing environment variable in template: {var}")
                all_vars_present = False
                
        return all_vars_present

    def run_basic_tests(self) -> bool:
        """Run basic functionality tests"""
        try:
            # Test basic imports
            from propellerads.client import PropellerAdsClient
            from propellerads.mcp_server import PropellerAdsMCPServer
            
            self.log_pass("Basic imports successful")
            
            # Test client instantiation (without API key)
            try:
                client = PropellerAdsClient(api_key="test_key")
                self.log_pass("Client instantiation")
            except Exception as e:
                self.log_warning(f"Client instantiation issue: {e}")
                
            return True
        except Exception as e:
            self.log_error(f"Basic tests failed: {e}")
            return False

    def check_documentation(self) -> bool:
        """Check documentation completeness"""
        doc_files = [
            'README.md',
            'QUICK_START.md', 
            'DEPLOYMENT_GUIDE.md',
            'USER_GUIDE_FOR_NON_DEVELOPERS.md',
            'CONTRIBUTING.md'
        ]
        
        all_docs_exist = True
        for doc in doc_files:
            if Path(doc).exists():
                size = Path(doc).stat().st_size
                if size > 100:  # At least 100 bytes
                    self.log_pass(f"Documentation: {doc} ({size} bytes)")
                else:
                    self.log_warning(f"Documentation too short: {doc}")
            else:
                self.log_error(f"Missing documentation: {doc}")
                all_docs_exist = False
                
        return all_docs_exist

    def check_disabled_tests(self) -> bool:
        """Check for disabled test files"""
        disabled_tests = list(Path('.').glob('**/*.disabled'))
        
        if disabled_tests:
            for test in disabled_tests:
                self.log_warning(f"Disabled test file: {test}")
            return False
        else:
            self.log_pass("No disabled test files")
            return True

    def run_pytest(self) -> bool:
        """Run the full test suite"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/', '--tb=no', '-q'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Parse test results
                output = result.stdout
                if 'passed' in output:
                    self.log_pass(f"Test suite: {output.split()[-4]} tests passed")
                    return True
                else:
                    self.log_warning("Test suite completed but results unclear")
                    return False
            else:
                self.log_error(f"Test suite failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_error("Test suite timed out")
            return False
        except Exception as e:
            self.log_error(f"Test suite error: {e}")
            return False

    def generate_report(self) -> Dict:
        """Generate final deployment report"""
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.issues)
        passed_count = len(self.passed_checks)
        warning_count = len(self.warnings)
        error_count = len(self.issues)
        
        if error_count == 0 and warning_count <= 2:
            status = "READY FOR DEPLOYMENT"
            score = 100
        elif error_count == 0:
            status = "READY WITH MINOR WARNINGS"
            score = 95
        elif error_count <= 2:
            status = "NEEDS FIXES BEFORE DEPLOYMENT"
            score = 80
        else:
            status = "NOT READY FOR DEPLOYMENT"
            score = 60
            
        return {
            'status': status,
            'score': score,
            'total_checks': total_checks,
            'passed': passed_count,
            'warnings': warning_count,
            'errors': error_count,
            'issues': self.issues,
            'warnings_list': self.warnings,
            'passed_list': self.passed_checks
        }

    def run_all_checks(self) -> Dict:
        """Run all deployment verification checks"""
        print("🚀 PropellerAds API Encyclopedia - Deployment Verification")
        print("=" * 60)
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Required Files", self.check_required_files),
            ("Dependencies", self.check_dependencies),
            ("PropellerAds SDK", self.check_propellerads_sdk),
            ("Web Interface", self.check_web_interface),
            ("Launcher Scripts", self.check_launcher_scripts),
            ("Environment Template", self.check_environment_template),
            ("Basic Tests", self.run_basic_tests),
            ("Documentation", self.check_documentation),
            ("Disabled Tests", self.check_disabled_tests),
            ("Test Suite", self.run_pytest)
        ]
        
        for check_name, check_func in checks:
            print(f"\n📋 Checking: {check_name}")
            print("-" * 40)
            try:
                check_func()
            except Exception as e:
                self.log_error(f"{check_name} check failed: {e}")
        
        return self.generate_report()

def main():
    """Main verification function"""
    verifier = DeploymentVerifier()
    report = verifier.run_all_checks()
    
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT VERIFICATION REPORT")
    print("=" * 60)
    print(f"🎯 Status: {report['status']}")
    print(f"📈 Score: {report['score']}/100")
    print(f"✅ Passed: {report['passed']}")
    print(f"⚠️ Warnings: {report['warnings']}")
    print(f"❌ Errors: {report['errors']}")
    
    if report['errors'] > 0:
        print("\n🔧 CRITICAL ISSUES TO FIX:")
        for issue in report['issues']:
            print(f"  {issue}")
    
    if report['warnings'] > 0:
        print("\n⚠️ WARNINGS TO CONSIDER:")
        for warning in report['warnings_list']:
            print(f"  {warning}")
    
    print(f"\n🎉 DEPLOYMENT RECOMMENDATION:")
    if report['score'] >= 95:
        print("✅ DEPLOY NOW - Everything looks great!")
    elif report['score'] >= 85:
        print("⚠️ DEPLOY WITH CAUTION - Minor issues present")
    else:
        print("❌ DO NOT DEPLOY - Critical issues must be fixed first")
    
    return report['score'] >= 85

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
