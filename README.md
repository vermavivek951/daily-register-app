# Jewellery Shop Manager

A comprehensive management system for jewellery shops, designed to be user-friendly and easy to maintain.

## Installation Instructions

### For New Users (Your Parents)

1. Double-click the "Jewellery Shop Manager Installer.exe" file
2. Click "Next" through the installation wizard
3. Choose the installation location (default is recommended)
4. Click "Install"
5. Wait for the installation to complete
6. Click "Finish"
7. A shortcut will be created on the desktop
8. Double-click the desktop shortcut to start the application

### For Developers (You)

1. Clone the repository
2. Install Python 3.6 or higher
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python src/main.py
   ```

## Update Instructions

### For Users (Your Parents)

The application will automatically check for updates when started. If an update is available:

1. A popup will appear asking if you want to update
2. Click "Update Now" to install the update
3. Wait for the update to complete
4. The application will restart automatically

### For Developers (You)

To release a new version:

1. Update the version number in `setup.py` and `version.json`
2. Create a new release on GitHub
3. Upload the new version files
4. Update the version information on the update server

## Support

If your parents encounter any issues:

1. They can contact you directly
2. You can provide remote support using TeamViewer or similar software
3. You can access the application logs in the installation directory

## Backup and Data Safety

- The application automatically creates daily backups
- Backups are stored in the installation directory under "backups"
- You can restore from a backup using the "Restore Database" option in the File menu

## Maintenance Tips

1. Regularly check the application logs for any issues
2. Monitor the backup directory to ensure backups are being created
3. Keep track of the version numbers and update history
4. Test updates on a development machine before releasing them

## Version History

- 1.0.0: Initial release
  - Basic transaction management
  - Item tracking
  - Daily summaries
  - Backup functionality

## Features

- Add, edit, and delete jewelry transactions
- Track gold and silver items
- Record old item returns
- Generate daily summaries
- Export data to Excel
- Support for multiple payment modes

## Project Structure

```
src/
├── database/         # Database management
├── models/          # Data models
├── ui/             # User interface components
├── utils/          # Utility functions
└── main.py         # Application entry point
```

## Usage

1. Enter transaction details in the input fields
2. Click "Add Item" to save the transaction
3. Use the date selector to view transactions for different dates
4. Select transactions to edit or delete
5. Export data to Excel using the "Export to Excel" button

## Data Storage

The application uses SQLite for data storage. The database file (`jewelry_shop.db`) is created automatically in the project root directory.

## Excel Export

Exported Excel files are saved in the `exports` directory with the format `jewelry_sales_YYYY-MM-DD.xlsx`. 