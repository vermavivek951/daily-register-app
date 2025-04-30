import os
import sys
import subprocess
import re
import uuid
import argparse
from pathlib import Path
from src.utils.version import APP_ID  # Import the fixed App ID
from build_notify import notify_user

# ---------------------------
# Constants and Paths
# ---------------------------

APP_NAME = "DailyRegister"
BASE_DIR = Path(__file__).parent.resolve()
SRC_DIR = BASE_DIR / "src"
MAIN_SCRIPT = SRC_DIR / "main.py"
VERSION_FILE = SRC_DIR / "utils" / "version.py"
ICON_PATH = BASE_DIR / "icon.ico"
MANIFEST_PATH = BASE_DIR / "app.manifest"
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
INSTALLER_TEMPLATE = BASE_DIR / "installer_script.iss.template"
INSTALLER_SCRIPT = BASE_DIR / "installer_script.iss"
HOOKS_DIR = BASE_DIR / "hooks"

PYTHON_EXE = sys.executable # Use the current python interpreter
INNO_COMPILER = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe") # Adjust path if needed

# ---------------------------
# Helper Functions
# ---------------------------

def get_version():
    """Extract version from version.py"""
    if not VERSION_FILE.exists():
        raise FileNotFoundError(f"Version file not found: {VERSION_FILE}")
    version_content = VERSION_FILE.read_text()
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", version_content)
    if not match:
        raise ValueError("Version not found in version.py")
    return match.group(1)

def generate_app_id():
    """Create a consistent UUID for the installer"""
    namespace = uuid.UUID("8955b190-be46-44f1-9bcb-de6f98ead67d")  # You can change this seed
    return str(uuid.uuid5(namespace, "DailyRegisterInstaller"))

def generate_installer_script(version):
    """Generate installer script from template"""
    if not INSTALLER_TEMPLATE.exists():
        raise FileNotFoundError(f"Inno Setup template not found: {INSTALLER_TEMPLATE}")
    
    template = INSTALLER_TEMPLATE.read_text()
    content = template.replace("{{VERSION}}", version).replace("{{APP_ID}}", APP_ID)
    
    INSTALLER_SCRIPT.write_text(content)
    print("Installer script generated.")


def run_pyinstaller():
    """Build executable using PyInstaller"""
    if not MAIN_SCRIPT.exists():
        raise FileNotFoundError(f"Main script not found: {MAIN_SCRIPT}")
    
    print("Running PyInstaller...")
    command = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_PATH}",
        f"--manifest={MANIFEST_PATH}",
        f"--add-data={SRC_DIR / 'views'};views",
        f"--add-data={SRC_DIR / 'controllers'};controllers",
        f"--add-data={SRC_DIR / 'models'};models",
        f"--add-data={SRC_DIR / 'utils'};utils",
        f"--add-data={BASE_DIR/ 'assets'};assets",
        f"--additional-hooks-dir={HOOKS_DIR}",
        "--hidden-import=PyQt6",
        "--hidden-import=matplotlib.backends.backend_qt5agg",
        "--hidden-import=matplotlib.pyplot",
        "--hidden-import=matplotlib.backends.backend_pdf",
        "--collect-all=PyQt6",
        "--collect-all=matplotlib",
        str(MAIN_SCRIPT)
    ]

    if not ICON_PATH.exists():
        raise FileNotFoundError(f"Icon not found: {ICON_PATH}")
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest file not found: {MANIFEST_PATH}")
    
    
    subprocess.run(command, check=True)
    print("PyInstaller build complete.")

def run_inno_setup():
    """Compile installer using Inno Setup Compiler"""
    if not INSTALLER_SCRIPT.exists():
        raise FileNotFoundError(f"Inno Setup script not found: {INSTALLER_SCRIPT}")
    print("Compiling installer with Inno Setup...")
    subprocess.run([str(INNO_COMPILER), str(INSTALLER_SCRIPT)], check=True)
    print("Installer compiled successfully.")

# ---------------------------
# Entry Point
# ---------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="App version", default=None)
    args = parser.parse_args()

    try:
        version = args.version or get_version()
        print(f"Building version: {version}")
        generate_installer_script(version)
        run_pyinstaller()
        run_inno_setup()
        notify_user("Build Completed Successfully!")
    except Exception as e:
        notify_user("Build Failed!")
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
