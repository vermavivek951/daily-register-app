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
    try:
        subprocess.run(command, check=True)
        print(f"   + PyInstaller build completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ! PyInstaller build failed with exit code {e.returncode}")
        raise

def run_inno_setup():
    """Runs Inno Setup Compiler"""
    print(f"--> Running Inno Setup Compiler...")
    try:
        # Ensure Output directory exists before running Inno Setup
        ensure_output_dir()
        
        # Run Inno Setup Compiler
        subprocess.run([str(INNO_COMPILER), str(INSTALLER_SCRIPT_OUTPUT)], check=True)
        print(f"   + Inno Setup build completed successfully")
        
        # Verify the installer was created
        version = get_version()
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
        run_inno_setup()
        
        print("\n=== Build Process Completed Successfully ===\n")
    except Exception as e:
        print(f"\n=== Build Process Failed ===\nError: {e}")
        if hasattr(e, '__traceback__'):
            traceback.print_tb(e.__traceback__)
        sys.exit(1)

if __name__ == "__main__":
    main()
