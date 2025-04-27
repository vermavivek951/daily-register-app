from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of models
hiddenimports = collect_submodules('models')

# Collect all data files from models
datas = collect_data_files('models')

# Print debug information
print(f"Hidden imports for models: {hiddenimports}")
print(f"Data files for models: {datas}") 