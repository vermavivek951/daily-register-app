"""
Version and release information for the Daily Register application.
This is the single source of truth for all version-related information including:
- Application version
- Application ID (GUID)
- Update check URL
- Download URL
"""

# Version information for the application
__version__ = "1.0.1"

# Application ID (GUID)
APP_ID = "8955b190-be46-44f1-9bcb-de6f98ead67d"

# URLs for updates and downloads
LATEST_VERSION_URL = "https://api.github.com/repos/vermavivek951/daily-register-app/releases/latest"
DOWNLOAD_PAGE_URL = "https://github.com/vermavivek951/daily-register-app/releases/tag/v{version}"