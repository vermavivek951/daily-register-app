from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of views
hiddenimports = collect_submodules('views')

# Collect all data files from views
datas = collect_data_files('views')

# Print debug information
print(f"Hidden imports for views: {hiddenimports}")
print(f"Data files for views: {datas}")