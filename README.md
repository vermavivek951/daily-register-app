# Daily Register

A comprehensive management system for jewellery shops, designed to be user-friendly and efficient for daily operations.

## Features

- Daily transaction management for jewellery items
- Track gold and silver items with detailed specifications
- Record old item returns and exchanges
- Generate daily summaries and reports
- Export data to Excel format
- Automatic backup system
- User-friendly interface
- Support for multiple payment modes

## Installation

### For End Users

1. Download the latest installer from the releases
2. Run the "Daily Register Installer.exe"
3. Follow the installation wizard
4. Launch the application from the desktop shortcut

### For Developers

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

## Project Structure

```
daily_register/
├── src/
│   ├── database/     # Database management and operations
│   ├── models/       # Data models and business logic
│   ├── ui/          # User interface components
│   ├── utils/       # Utility functions and helpers
│   └── main.py      # Application entry point
├── build/           # Build configuration and scripts
├── dist/           # Distribution files
├── Output/         # Generated reports and exports
├── logs/           # Application logs
└── requirements.txt # Python dependencies
```

## Dependencies

- pandas >= 1.3.0 (Data manipulation and analysis)
- openpyxl >= 3.0.7 (Excel file handling)
- pywin32 >= 300 (Windows-specific functionality)
- packaging >= 21.0 (Version comparison utilities)

## Usage Guide

1. **Daily Transactions**
   - Enter new transaction details
   - Add items with specifications
   - Record payments and payment modes

2. **Reports and Exports**
   - View daily summaries
   - Export data to Excel
   - Generate custom reports

3. **Data Management**
   - Backup and restore functionality
   - Data validation and error checking
   - Automatic daily backups

## Data Storage

- SQLite database for reliable data storage
- Automatic daily backups
- Excel exports for reporting and analysis

## Support and Maintenance

- Check the logs directory for troubleshooting
- Regular backups are stored in the installation directory
- Contact support for technical assistance


## License

This software is proprietary and intended for specific business use. 