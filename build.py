import os
import sys
import subprocess
import re
import traceback
import argparse
from pathlib import Path
from src.utils.version import APP_ID  # Import AppId directly from version.py

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.resolve() # Get absolute path of script's dir
SRC_DIR = PROJECT_ROOT / "src"
UTILS_DIR = SRC_DIR / "utils"
VERSION_FILE = UTILS_DIR / "version.py"
MAIN_SCRIPT = SRC_DIR / "main.py"
ICON_FILE = PROJECT_ROOT / "icon.ico"
MANIFEST_FILE = PROJECT_ROOT / "app.manifest"
APP_NAME = "DailyRegister"
INSTALLER_SCRIPT_TEMPLATE = PROJECT_ROOT / "installer_script.iss.template" # Template file
INSTALLER_SCRIPT_OUTPUT = PROJECT_ROOT / "installer_script.iss" # Generated file
INNO_COMPILER = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe") # Adjust path if needed
PYTHON_EXE = sys.executable # Use the current python interpreter
OUTPUT_DIR = PROJECT_ROOT / "Output" # Define output directory

# --- Functions ---
def get_version():
    """Reads the version from src/utils/version.py"""
    try:
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", content)
            if match:
                version = match.group(1)
                print(f"--> Found version: {version}")
                return version
            else:
                raise ValueError(f"Could not find __version__ = \"...\" line in {VERSION_FILE}")
    except FileNotFoundError:
            raise FileNotFoundError(f"Version file not found: {VERSION_FILE}")
    except Exception as e:
            raise RuntimeError(f"Error reading version file: {e}")

def ensure_output_dir():
    """Ensures the Output directory exists"""
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        print(f"--> Ensured Output directory exists at: {OUTPUT_DIR}")
    except Exception as e:
        raise RuntimeError(f"Error creating Output directory: {e}")

def generate_installer_script(version):
    """Generates installer_script.iss from a template"""
    print(f"--> Generating installer script for version {version} (AppId: {APP_ID})...")
    try:
        with open(INSTALLER_SCRIPT_TEMPLATE, 'r', encoding='utf-8') as f_template:
            template_content = f_template.read()

        # Define patterns for replacement
        define_pattern = re.compile(r'^(#define\s+MyAppVersion\s+)"\{#MyAppVersion\}"', re.MULTILINE)
        filename_pattern = re.compile(r"^(OutputBaseFilename=.*?_v)\{#MyAppVersion\}", re.MULTILINE)
        version_pattern = re.compile(r"^(AppVersion=)\{#MyAppVersion\}", re.MULTILINE)
        appid_pattern = re.compile(r"^(AppId=)\{#MyAppId\}", re.MULTILINE)

        # Replace version in #define line
        updated_content = define_pattern.sub(f'#define MyAppVersion "{version}"', template_content)
        if updated_content == template_content:
            raise ValueError(f"Could not find '#define MyAppVersion \"{{#MyAppVersion}}\"' line in template: {INSTALLER_SCRIPT_TEMPLATE}")

        # Replace version marker in OutputBaseFilename line
        updated_content = filename_pattern.sub(f'OutputBaseFilename=DailyRegister_Setup_v{version}', updated_content)
        if updated_content == template_content:
            print(f"Warning: Could not find 'OutputBaseFilename=..._v{{#MyAppVersion}}' pattern in template: {INSTALLER_SCRIPT_TEMPLATE}. Check template.", file=sys.stderr)

        # Replace version marker in AppVersion line
        updated_content = version_pattern.sub(f'AppVersion={version}', updated_content)
        if updated_content == template_content:
            print(f"Warning: Could not find 'AppVersion={{#MyAppVersion}}' pattern in template: {INSTALLER_SCRIPT_TEMPLATE}. Check template.", file=sys.stderr)

        # Replace AppId marker
        updated_content = appid_pattern.sub(f'AppId={APP_ID}', updated_content)
        if updated_content == template_content:
            print(f"Warning: Could not find 'AppId={{#MyAppId}}' pattern in template: {INSTALLER_SCRIPT_TEMPLATE}. Check template.", file=sys.stderr)

        with open(INSTALLER_SCRIPT_OUTPUT, 'w', encoding='utf-8') as f_output:
            f_output.write(updated_content)
        print(f"   + Generated installer script: {INSTALLER_SCRIPT_OUTPUT}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Installer script template not found: {INSTALLER_SCRIPT_TEMPLATE}")
    except Exception as e:
        raise RuntimeError(f"Error generating installer script: {e}")

def run_pyinstaller(version):
    """Runs PyInstaller"""
    command = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_FILE}",
        f"--manifest={MANIFEST_FILE}",
        "--add-data", f"{MANIFEST_FILE};.",
        # Add views directory as data
        "--add-data", f"{SRC_DIR / 'views'};views",
        # Add controllers directory as data
        "--add-data", f"{SRC_DIR / 'controllers'};controllers",
        # Add models directory as data
        "--add-data", f"{SRC_DIR / 'models'};models",
        # Add utils directory as data
        "--add-data", f"{SRC_DIR / 'utils'};utils",
        # Add services directory as data
        "--add-data", f"{SRC_DIR / 'services'};services",
        # Add database directory as data
        "--add-data", f"{SRC_DIR / 'database'};database",
        # Add icons directory as data
        "--add-data", f"{SRC_DIR / 'icons'};icons",
        # Add hook file
        "--additional-hooks-dir", str(PROJECT_ROOT),
        # PyQt6 imports
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.sip",
        "--hidden-import=PyQt6.QtPrintSupport",
        "--hidden-import=PyQt6.QtSvg",
        # Add views module explicitly
        "--hidden-import=views",
        "--hidden-import=views.main_window",
        "--hidden-import=views.transaction_display",
        "--hidden-import=views.ui_components",
        "--hidden-import=views.view_models",
        "--hidden-import=views.slip_entry_form",
        "--hidden-import=views.settings_dialog",
        # Add controllers module explicitly
        "--hidden-import=controllers",
        "--hidden-import=controllers.transaction_controller",
        # Add models module explicitly
        "--hidden-import=models",
        "--hidden-import=models.transaction",
        # Add utils module explicitly
        "--hidden-import=utils",
        "--hidden-import=utils.version",
        # Add services module explicitly
        "--hidden-import=services",
        # Add database module explicitly
        "--hidden-import=database",
        # Additional Qt dependencies
        "--hidden-import=PyQt6.QtCore.Qt",
        "--hidden-import=PyQt6.QtCore.QSize",
        "--hidden-import=PyQt6.QtCore.QPoint",
        "--hidden-import=PyQt6.QtCore.QRect",
        "--hidden-import=PyQt6.QtCore.QStringListModel",
        "--hidden-import=PyQt6.QtCore.QTimer",
        "--hidden-import=PyQt6.QtCore.QDate",
        "--hidden-import=PyQt6.QtCore.QDateTime",
        "--hidden-import=PyQt6.QtCore.QTime",
        "--hidden-import=PyQt6.QtCore.QSettings",
        "--hidden-import=PyQt6.QtCore.QDir",
        "--hidden-import=PyQt6.QtCore.QFile",
        "--hidden-import=PyQt6.QtCore.QFileInfo",
        "--hidden-import=PyQt6.QtCore.QIODevice",
        "--hidden-import=PyQt6.QtCore.QTextStream",
        "--hidden-import=PyQt6.QtCore.QTextCodec",
        "--hidden-import=PyQt6.QtCore.QUrl",
        "--hidden-import=PyQt6.QtCore.QVariant",
        "--hidden-import=PyQt6.QtCore.QModelIndex",
        "--hidden-import=PyQt6.QtCore.QAbstractItemModel",
        "--hidden-import=PyQt6.QtCore.QAbstractTableModel",
        "--hidden-import=PyQt6.QtCore.QAbstractListModel",
        "--hidden-import=PyQt6.QtCore.QItemSelectionModel",
        "--hidden-import=PyQt6.QtCore.QItemSelection",
        "--hidden-import=PyQt6.QtCore.QMimeData",
        "--hidden-import=PyQt6.QtCore.QProcess",
        "--hidden-import=PyQt6.QtCore.QThread",
        "--hidden-import=PyQt6.QtCore.QThreadPool",
        "--hidden-import=PyQt6.QtCore.QRunnable",
        "--hidden-import=PyQt6.QtCore.QEventLoop",
        "--hidden-import=PyQt6.QtCore.QTimer",
        "--hidden-import=PyQt6.QtCore.QObject",
        "--hidden-import=PyQt6.QtCore.QEvent",
        "--hidden-import=PyQt6.QtCore.QSizePolicy",
        "--hidden-import=PyQt6.QtCore.QMargins",
        "--hidden-import=PyQt6.QtCore.QSizeF",
        "--hidden-import=PyQt6.QtCore.QPointF",
        "--hidden-import=PyQt6.QtCore.QRectF",
        "--hidden-import=PyQt6.QtCore.QLineF",
        "--hidden-import=PyQt6.QtCore.QEasingCurve",
        "--hidden-import=PyQt6.QtCore.QPropertyAnimation",
        "--hidden-import=PyQt6.QtCore.QSequentialAnimationGroup",
        "--hidden-import=PyQt6.QtCore.QParallelAnimationGroup",
        "--hidden-import=PyQt6.QtCore.QAnimationGroup",
        "--hidden-import=PyQt6.QtCore.QAbstractAnimation",
        "--hidden-import=PyQt6.QtCore.QStateMachine",
        "--hidden-import=PyQt6.QtCore.QState",
        "--hidden-import=PyQt6.QtCore.QFinalState",
        "--hidden-import=PyQt6.QtCore.QHistoryState",
        "--hidden-import=PyQt6.QtCore.QSignalTransition",
        "--hidden-import=PyQt6.QtCore.QPropertyTransition",
        "--hidden-import=PyQt6.QtCore.QEventTransition",
        "--hidden-import=PyQt6.QtCore.QAbstractTransition",
        "--hidden-import=PyQt6.QtCore.QSignalMapper",
        "--hidden-import=PyQt6.QtCore.QMetaObject",
        "--hidden-import=PyQt6.QtCore.QMetaMethod",
        "--hidden-import=PyQt6.QtCore.QMetaProperty",
        "--hidden-import=PyQt6.QtCore.QMetaEnum",
        "--hidden-import=PyQt6.QtCore.QMetaType",
        "--hidden-import=PyQt6.QtCore.QMetaClassInfo",
        "--hidden-import=PyQt6.QtCore.QMetaConnection",
        "--hidden-import=PyQt6.QtCore.QMetaObject",
        "--hidden-import=PyQt6.QtCore.QMetaMethod",
        "--hidden-import=PyQt6.QtCore.QMetaProperty",
        "--hidden-import=PyQt6.QtCore.QMetaEnum",
        "--hidden-import=PyQt6.QtCore.QMetaType",
        "--hidden-import=PyQt6.QtCore.QMetaClassInfo",
        "--hidden-import=PyQt6.QtCore.QMetaConnection",
        # Additional dependencies
        "--hidden-import=pandas",
        "--hidden-import=requests",
        "--hidden-import=sqlite3",
        "--hidden-import=openpyxl",
        "--hidden-import=win32api",
        "--hidden-import=win32con",
        "--hidden-import=win32gui",
        "--hidden-import=win32process",
        "--hidden-import=win32security",
        "--hidden-import=win32timezone",
        # Matplotlib imports
        "--hidden-import=matplotlib",
        "--hidden-import=matplotlib.backends.backend_qt5agg",
        "--hidden-import=matplotlib.backends.backend_agg",
        "--hidden-import=matplotlib.backends.backend_svg",
        "--hidden-import=matplotlib.figure",
        "--hidden-import=matplotlib.pyplot",
        "--hidden-import=matplotlib.backends.backend_qt",
        "--hidden-import=matplotlib.backends.backend_qtagg",
        # Collect all components
        "--collect-all", "matplotlib",
        # Collect all PyQt6 components
        "--collect-all", "PyQt6",
        "--collect-all", "PyQt6-Qt6",
        "--collect-all", "PyQt6-sip",
        # Additional options
        "--clean",
        "--noconfirm",
        str(MAIN_SCRIPT)
    ]
    print(f"--> Running PyInstaller...")
    try:
        subprocess.run(command, check=True)
        print(f"   + PyInstaller build completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ! PyInstaller build failed with exit code {e.returncode}")
        raise

def run_inno_setup(version):
    """Runs Inno Setup Compiler"""
    print(f"--> Running Inno Setup Compiler...")
    try:
        # Ensure Output directory exists before running Inno Setup
        ensure_output_dir()
        
        # Run Inno Setup Compiler
        subprocess.run([str(INNO_COMPILER), str(INSTALLER_SCRIPT_OUTPUT)], check=True)
        print(f"   + Inno Setup build completed successfully")
        
        # Verify the installer was created
        installer_path = OUTPUT_DIR / f"DailyRegister_Setup_v{version}.exe"
        if installer_path.exists():
            print(f"   + Installer created successfully at: {installer_path}")
        else:
            raise FileNotFoundError(f"Installer not found at expected location: {installer_path}")
    except subprocess.CalledProcessError as e:
        print(f"   ! Inno Setup build failed with exit code {e.returncode}")
        raise
    except Exception as e:
        print(f"   ! Error during Inno Setup build: {e}")
        raise

def main():
    """Main build process"""
    try:
        print("\n=== Starting DailyRegister Build Process ===\n")
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Build DailyRegister installer')
        parser.add_argument('--version', help='Version number to use (e.g., v1.0.2)')
        args = parser.parse_args()
        
        # Get version from command line or version.py
        if args.version:
            version = args.version.lstrip('v')  # Remove 'v' prefix if present
            print(f"--> Using version from command line: {version}")
        else:
            version = get_version()
            print(f"--> Using version from version.py: {version}")
        
        # Generate installer script
        generate_installer_script(version)
        
        # Run PyInstaller
        run_pyinstaller(version)
        
        # Run Inno Setup
        run_inno_setup(version)
        
        print("\n=== Build Process Completed Successfully ===\n")
    except Exception as e:
        print(f"\n=== Build Process Failed ===\nError: {e}")
        if hasattr(e, '__traceback__'):
            traceback.print_tb(e.__traceback__)
        sys.exit(1)

if __name__ == "__main__":
    main()
