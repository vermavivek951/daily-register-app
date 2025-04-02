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
        result = subprocess.run(command, check=True, cwd=PROJECT_ROOT, shell=use_shell)
        
        # Verify the output exists
        dist_dir = PROJECT_ROOT / "dist" / "DailyRegister"
        exe_path = dist_dir / "DailyRegister.exe"
        
        if not dist_dir.exists():
            raise RuntimeError(f"PyInstaller output directory not found: {dist_dir}")
        if not exe_path.exists():
            raise RuntimeError(f"PyInstaller executable not found: {exe_path}")
            
        print(f"   + PyInstaller build successful.")
        print(f"   + Executable location: {exe_path}")
        print(f"   + Directory contents of {dist_dir}:")
        for item in dist_dir.iterdir():
            print(f"     - {item.name}")
            
    except subprocess.CalledProcessError as e:
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
        result = subprocess.run(command, check=True, cwd=PROJECT_ROOT)
        print(f"   + Inno Setup build successful. Installer in: {PROJECT_ROOT / 'Output'}")
    except subprocess.CalledProcessError as e:
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
