import os
import shutil
import json
import csv
import datetime
from pathlib import Path
import sqlite3
import pandas as pd

class BackupManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
        self.ensure_backup_dir()

    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self, backup_name=None):
        """Create a backup of the database"""
        if backup_name is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'backup_{timestamp}.db'
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    def restore_backup(self, backup_path):
        """Restore database from a backup"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError("Backup file not found")
        
        # Create a backup of current database before restoring
        self.create_backup('pre_restore_backup.db')
        
        # Replace current database with backup
        shutil.copy2(backup_path, self.db_path)

    def export_to_csv(self, start_date=None, end_date=None):
        """Export database contents to CSV files"""
        conn = sqlite3.connect(self.db_path)
        
        # Export transactions
        query = "SELECT * FROM transactions"
        if start_date and end_date:
            query += f" WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        
        df = pd.read_sql_query(query, conn)
        csv_path = os.path.join(self.backup_dir, f'transactions_{datetime.datetime.now().strftime("%Y%m%d")}.csv')
        df.to_csv(csv_path, index=False)
        
        conn.close()
        return csv_path

    def list_backups(self):
        """List all available backups"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.db'):
                path = os.path.join(self.backup_dir, file)
                backups.append({
                    'name': file,
                    'path': path,
                    'date': datetime.datetime.fromtimestamp(os.path.getmtime(path))
                })
        return sorted(backups, key=lambda x: x['date'], reverse=True)

    def auto_backup(self):
        """Create automatic backup if needed"""
        # Check if we need to create a backup (e.g., daily)
        latest_backups = self.list_backups()
        if not latest_backups or (datetime.datetime.now() - latest_backups[0]['date']).days >= 1:
            return self.create_backup()
        return None 