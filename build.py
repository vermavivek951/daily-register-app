import os
import sys
import subprocess
import re
import traceback
from pathlib import Path
from src.utils.version import APP_ID  # Import AppId directly from version.py

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.resolve() # Get absolute path of script's dir
SRC_DIR = PROJECT_ROOT / "src"
UTILS_DIR = SRC_DIR / "utils"
VERSION_FILE = UTILS_DIR / "version.py"
MAIN_SCRIPT = SRC_DIR / "main.py"
ICON_FILE = PROJECT_ROOT / "icon.ico"
APP_NAME = "DailyRegister"
INSTALLER_SCRIPT_TEMPLATE = PROJECT_ROOT / "installer_script.iss.template" # Template file
INSTALLER_SCRIPT_OUTPUT = PROJECT_ROOT / "installer_script.iss" # Generated file
INNO_COMPILER = Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe") # Adjust path if needed
PYTHON_EXE = sys.executable # Use the current python interpreter

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

def generate_installer_script(version):
    """Generates installer_script.iss from a template"""
    print(f"--> Generating installer script for version {version} (AppId: {APP_ID})...")
    try:
        with open(INSTALLER_SCRIPT_TEMPLATE, 'r', encoding='utf-8') as f_template:
            template_content = f_template.read()

        # Define patterns for replacement
        define_pattern = re.compile(r'^(#define\s+MyAppVersion\s+)[\'].*?[\']', re.MULTILINE)
        filename_pattern = re.compile(r"^(OutputBaseFilename=.*?_v)\{#MyAppVersion}", re.MULTILINE)
        version_pattern = re.compile(r"^(AppVersion=)\{#MyAppVersion}", re.MULTILINE)
        appid_pattern = re.compile(r"^(AppId=)\{#MyAppId}", re.MULTILINE) # Pattern for AppId


        # Replace version in #define line
        updated_content, n_subs_define = define_pattern.subn(f'\1"{version}"', template_content)
        if n_subs_define == 0:
            raise ValueError(f"Could not find '#define MyAppVersion \"...\"' line in template: {INSTALLER_SCRIPT_TEMPLATE}")

        # Replace version marker in OutputBaseFilename line
        updated_content, n_subs_filename = filename_pattern.subn(rf"\g<1>{version}", updated_content)
        if n_subs_filename == 0:
            print(f"Warning: Could not find 'OutputBaseFilename=..._v{{#MyAppVersion}}' pattern in template: {INSTALLER_SCRIPT_TEMPLATE}. Check template.", file=sys.stderr)
            # As a fallback, maybe try replacing the hardcoded version if the template wasn't updated
            filename_pattern_direct = re.compile(r"^(OutputBaseFilename=.*?_v)\d+\.\d+\.\d+", re.MULTILINE)
            updated_content, n_subs_filename_direct = filename_pattern_direct.subn(rf"\g<1>{version}", updated_content)
            if n_subs_filename_direct == 0:
                 raise ValueError(f"Could not find/replace version in 'OutputBaseFilename=...' line in template: {INSTALLER_SCRIPT_TEMPLATE}")

        # Replace version marker in AppVersion line
        updated_content, n_subs_appversion = version_pattern.subn(rf"\g<1>{version}", updated_content)
        if n_subs_appversion == 0:
            print(f"Warning: Could not find 'AppVersion={{#MyAppVersion}}' pattern in template: {INSTALLER_SCRIPT_TEMPLATE}. Check template.", file=sys.stderr)
             # As a fallback, maybe try replacing the hardcoded version if the template wasn't updated
            version_pattern_direct = re.compile(r"^(AppVersion=)\d+\.\d+\.\d+", re.MULTILINE)
            updated_content, n_subs_appversion_direct = version_pattern_direct.subn(rf"\g<1>{version}", updated_content)
            if n_subs_appversion_direct == 0:
                raise ValueError(f"Could not find/replace version in 'AppVersion=...' line in template: {INSTALLER_SCRIPT_TEMPLATE}")

        # Replace AppId marker
        updated_content, n_subs_appid = appid_pattern.subn(f"\\1{APP_ID}", updated_content)
        if n_subs_appid == 0:
            print(f"Warning: Could not find 'AppId={{#MyAppId}}' pattern in template: {INSTALLER_SCRIPT_TEMPLATE}. Check template.", file=sys.stderr)
            # Fallback if template marker wasn't used
            appid_pattern_direct = re.compile(r"^(AppId=){.*?}", re.MULTILINE)
            updated_content, n_subs_appid_direct = appid_pattern_direct.subn(rf"\g<1>{APP_ID}", updated_content)
            if n_subs_appid_direct == 0:
                raise ValueError(f"Could not find/replace AppId in template: {INSTALLER_SCRIPT_TEMPLATE}")


        # --- DEBUG: Print first few lines of generated content ---
        print("--> DEBUG: Content to be written (first 10 lines):") # Increased lines for debug
        generated_lines = updated_content.splitlines()
        for i, line in enumerate(generated_lines[:10]):
            print(f"    Line {i+1}: {repr(line)}") # Use repr to show hidden chars
        print("--------------------------------------------------")
        # --- End DEBUG ---

        with open(INSTALLER_SCRIPT_OUTPUT, 'w', encoding='utf-8') as f_output:
            f_output.write(updated_content)
        print(f"   + Generated installer script: {INSTALLER_SCRIPT_OUTPUT}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Installer script template not found: {INSTALLER_SCRIPT_TEMPLATE}")
    except Exception as e:
        raise RuntimeError(f"Error generating installer script: {e}")

def run_pyinstaller(version):
    """Runs PyInstaller"""
    # Note: PyInstaller output folder/exe name doesn't typically include version
    command = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_FILE}",
        str(MAIN_SCRIPT),
        "--clean", # Clean cache before build
        "--noconfirm" # Don't ask for confirmation to overwrite dist
    ]
    print(f"--> Running PyInstaller...")
    print(f"    Command: {' '.join(map(str, command))}")
    try:
        # Use shell=True on Windows if python isn't directly found otherwise
        use_shell = sys.platform == "win32"
        result = subprocess.run(command, check=True, cwd=PROJECT_ROOT, capture_output=True, text=True, shell=use_shell, encoding='utf-8', errors='replace')
        print(result.stdout)
        if result.stderr:
             print(f"PyInstaller stderr:\n{result.stderr}", file=sys.stderr)
        print("   + PyInstaller build successful.")
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller stdout:\n{e.stdout}")
        print(f"PyInstaller stderr:\n{e.stderr}", file=sys.stderr)
        raise RuntimeError(f"PyInstaller failed with exit code {e.returncode}")
    except FileNotFoundError:
            raise FileNotFoundError(f"Could not find Python executable: {PYTHON_EXE}. Ensure it's in PATH or provide full path.")


def run_inno_setup():
    """Runs Inno Setup Compiler"""
    if not INNO_COMPILER.exists():
            raise FileNotFoundError(f"Inno Setup Compiler not found at: {INNO_COMPILER}. Please install or update path.")
    command = [str(INNO_COMPILER), str(INSTALLER_SCRIPT_OUTPUT)]
    print(f"--> Running Inno Setup Compiler...")
    print(f"    Command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        # Inno Setup output often includes progress, maybe just print last lines or success
        print("\n".join(result.stdout.splitlines()[-5:])) # Print last few lines
        if result.stderr:
             print(f"Inno Setup stderr:\n{result.stderr}", file=sys.stderr)
        print(f"   + Inno Setup build successful. Installer in: {PROJECT_ROOT / 'Output'}")
    except subprocess.CalledProcessError as e:
        print(f"Inno Setup stdout:\n{e.stdout}")
        print(f"Inno Setup stderr:\n{e.stderr}", file=sys.stderr)
        raise RuntimeError(f"Inno Setup Compiler failed with exit code {e.returncode}")


# --- Main Execution ---
if __name__ == "__main__":
    try:
        print("--- Starting Build Process ---")
        app_version = get_version()
        generate_installer_script(app_version)
        run_pyinstaller(app_version)
        run_inno_setup()
        print("\n--- Build Process Completed Successfully! ---")

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"\n--- Build Failed: {e} ---", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n--- An Unexpected Error Occurred: {e} ---", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
