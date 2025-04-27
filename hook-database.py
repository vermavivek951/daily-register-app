from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of database
hiddenimports = collect_submodules('database')

# Collect all data files from database
datas = collect_data_files('database')

# Print debug information
print(f"Hidden imports for database: {hiddenimports}")
print(f"Data files for database: {datas}") 