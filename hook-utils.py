from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of utils
hiddenimports = collect_submodules('utils')

# Collect all data files from utils
datas = collect_data_files('utils')

# Print debug information
print(f"Hidden imports for utils: {hiddenimports}")
print(f"Data files for utils: {datas}") 