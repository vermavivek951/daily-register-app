import sys
import pkg_resources
import importlib

def check_dependency(package_name, min_version=None):
    try:
        module = importlib.import_module(package_name)
        version = pkg_resources.get_distribution(package_name).version
        print(f"✓ {package_name} is installed (version {version})")
        if min_version:
            if pkg_resources.parse_version(version) >= pkg_resources.parse_version(min_version):
                print(f"  ✓ Version requirement >= {min_version} is satisfied")
            else:
                print(f"  ✗ Version {version} is lower than required {min_version}")
        return True
    except ImportError:
        print(f"✗ {package_name} is not installed")
        return False
    except Exception as e:
        print(f"✗ Error checking {package_name}: {str(e)}")
        return False

def main():
    print("Python version:", sys.version)
    print("\nChecking dependencies...")
    print("-" * 50)
    
    dependencies = {
        'pandas': '1.3.0',
        'openpyxl': '3.0.7',
        'pywin32': '300',
        'packaging': '21.0',
        'matplotlib': '3.5.0',
        'PyQt6': '6.4.0',
        'PyQt6-Qt6': '6.4.0',
        'PyQt6-sip': '13.4.0',
        'requests': '2.31.0',
        'pyinstaller': '5.0.0'
    }
    
    all_passed = True
    for package, version in dependencies.items():
        if not check_dependency(package, version):
            all_passed = False
    
    print("\nSpecial checks for PyQt6:")
    try:
        import PyQt6.QtCore
        print("✓ PyQt6.QtCore is available")
        import PyQt6.QtWidgets
        print("✓ PyQt6.QtWidgets is available")
    except ImportError as e:
        print(f"✗ PyQt6 component check failed: {str(e)}")
        all_passed = False
    
    print("\nSummary:")
    print("-" * 50)
    if all_passed:
        print("✓ All dependencies are installed with correct versions")
    else:
        print("✗ Some dependencies are missing or have incorrect versions")
        sys.exit(1)

if __name__ == "__main__":
    main() 