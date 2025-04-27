from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of controllers
hiddenimports = collect_submodules('controllers')

# Collect all data files from controllers
datas = collect_data_files('controllers')

# Print debug information
print(f"Hidden imports for controllers: {hiddenimports}")
print(f"Data files for controllers: {datas}") 