import os
import shutil
import json
import csv
from datetime import datetime
from pathlib import Path
import sqlite3
import pandas as pd
from services.database_service import DatabaseService

class BackupManager:
    """Manages database backups."""
    
    def __init__(self, db_service: DatabaseService = None):
        """Initialize backup manager with optional database service."""
        self.db_service = db_service or DatabaseService()
        
        # Get AppData/Roaming path
        app_data = os.getenv('APPDATA')
        if not app_data:
            raise ValueError("Could not get APPDATA directory")
        
        # Create backups directory in AppData/DailyRegister/backups
        self.backup_dir = Path(app_data) / 'DailyRegister' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"[BackupManager] Using backup directory: {self.backup_dir}")

    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self):
        """Create a backup of the current database."""
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"db_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename

            # Copy the current database file to backup location
            shutil.copy2(self.db_service.db_file, backup_path)
            
            print(f"[BackupManager] Created backup at: {backup_path}")
            return str(backup_path)

        except Exception as e:
            print(f"[BackupManager] Error creating backup: {e}")
            raise

    def restore_backup(self, backup_path):
        """Restore database from a backup file."""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError("Backup file not found")

            # Create a backup of current database before restoring
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pre_restore_backup = self.backup_dir / f"pre_restore_backup_{timestamp}.db"
            shutil.copy2(self.db_service.db_file, pre_restore_backup)

            # Restore the backup
            shutil.copy2(backup_path, self.db_service.db_file)
            
            # Reload the database
            self.db_service.init_db()
            
            print(f"[BackupManager] Restored backup from: {backup_path}")
            return True

        except Exception as e:
            print(f"[BackupManager] Error restoring backup: {e}")
            raise

    def export_to_csv(self, start_date=None, end_date=None):
        """Export database contents to CSV files"""
        conn = sqlite3.connect(self.db_service.db_file)
        
        # Export transactions
        query = "SELECT * FROM transactions"
        if start_date and end_date:
            query += f" WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        
        df = pd.read_sql_query(query, conn)
        csv_path = os.path.join(self.backup_dir, f'transactions_{datetime.now().strftime("%Y%m%d")}.csv')
        df.to_csv(csv_path, index=False)
        
        conn.close()
        return csv_path

    def list_backups(self):
        """List all available backup files."""
        try:
            backups = []
            for file in self.backup_dir.glob('db_backup_*.db'):
                backups.append({
                    'path': str(file),
                    'timestamp': datetime.strptime(
                        file.stem.replace('db_backup_', ''),
                        '%Y%m%d_%H%M%S'
                    )
                })
            return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

        except Exception as e:
            print(f"[BackupManager] Error listing backups: {e}")
            raise

    def auto_backup(self):
        """Create automatic backup if needed"""
        # Check if we need to create a backup (e.g., daily)
        latest_backups = self.list_backups()
        if not latest_backups or (datetime.now() - latest_backups[0]['timestamp']).days >= 1:
            return self.create_backup()
        return None 