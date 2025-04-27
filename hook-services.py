from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of services
hiddenimports = collect_submodules('services')

# Collect all data files from services
datas = collect_data_files('services')

# Print debug information
print(f"Hidden imports for services: {hiddenimports}")
print(f"Data files for services: {datas}") 