import sqlite3
from datetime import datetime
import json
import shutil
from pathlib import Path
import os
from typing import List, Dict, Any

class DatabaseService:
    def __init__(self):
        """Initialize the database service."""
        try:
            # Get AppData/Roaming path
            app_data = os.getenv('APPDATA')
            if not app_data:
                raise ValueError("Could not get APPDATA directory")
            
            # Create application directory in AppData
            self.app_dir = Path(app_data) / 'DailyRegister'
            self.app_dir.mkdir(exist_ok=True)
            
            # Set database path
            self.db_file = self.app_dir / 'transactions.db'
            print(f"[DatabaseService] Using database at: {self.db_file}")
            
            # Initialize database
            self.init_db()
            
        except Exception as e:
            print(f"[DatabaseService] Error initializing database service: {e}")
            raise

    def init_db(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Create transactions table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        new_items TEXT,
                        old_items TEXT,
                        comments TEXT,
                        cash_amount REAL DEFAULT 0,
                        card_amount REAL DEFAULT 0,
                        upi_amount REAL DEFAULT 0
                    )
                ''')
                
                conn.commit()
                print("[DatabaseService] Database initialized successfully")
                
        except Exception as e:
            print(f"[DatabaseService] Error initializing database: {e}")
            raise

    def save_transaction(self, transaction):
        """Save a transaction to the database."""
        try:
            print(f"[DatabaseService] Saving transaction: {transaction}")
            
            # Convert datetime to string if it's a datetime object
            if isinstance(transaction['timestamp'], datetime):
                transaction['timestamp'] = transaction['timestamp'].isoformat()
            
            # Convert lists to JSON strings
            new_items = json.dumps(transaction.get('new_items', []))
            old_items = json.dumps(transaction.get('old_items', []))
            
            # Insert transaction
            query = """
                INSERT INTO transactions (
                    timestamp, new_items, old_items, comments,
                    cash_amount, card_amount, upi_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    transaction['timestamp'],
                    new_items,
                    old_items,
                    transaction.get('comments', ''),
                    float(transaction.get('cash_amount', 0)),
                    float(transaction.get('card_amount', 0)),
                    float(transaction.get('upi_amount', 0))
                ))
                conn.commit()
            
            print("[DatabaseService] Transaction saved successfully")
            return True
            
        except Exception as e:
            print(f"[DatabaseService] Error saving transaction: {e}")
            return False

    def delete_transaction(self, transaction):
        """Delete a transaction from the database."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Get timestamp
                timestamp = transaction['timestamp']
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.isoformat()
                
                # Delete transaction
                cursor.execute('''
                    DELETE FROM transactions
                    WHERE timestamp = ?
                ''', (timestamp,))
                
                conn.commit()
                print(f"[DatabaseService] Transaction deleted successfully")
                return True
                
        except Exception as e:
            print(f"[DatabaseService] Error deleting transaction: {e}")
            return False

    def get_transactions_by_date(self, date):
        """Get all transactions for a specific date."""
        try:
            # Convert date to string in YYYY-MM-DD format
            date_str = date.strftime('%Y-%m-%d')
            print(f"[DatabaseService] Getting transactions for date: {date_str}")
            
            # Query transactions for the date
            query = """
                SELECT * FROM transactions 
                WHERE date(timestamp) = ?
                ORDER BY timestamp DESC
            """
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (date_str,))
                rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            transactions = []
            for row in rows:
                transaction = {
                    'id': row[0],
                    'timestamp': datetime.fromisoformat(row[1]),
                    'new_items': json.loads(row[2]) if row[2] else [],
                    'old_items': json.loads(row[3]) if row[3] else [],
                    'comments': row[4],
                    'cash_amount': float(row[5]),
                    'card_amount': float(row[6]),
                    'upi_amount': float(row[7])
                }
                transactions.append(transaction)
            
            print(f"[DatabaseService] Retrieved {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            print(f"[DatabaseService] Error getting transactions: {e}")
            return []

    def get_transactions(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get transactions for a date range."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Format dates for query
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
                
                # Get transactions
                cursor.execute('''
                    SELECT date, time, new_items, old_items, comments,
                           cash_amount, card_amount, upi_amount
                    FROM transactions
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC, time DESC
                ''', (start_str, end_str))
                
                transactions = []
                for row in cursor.fetchall():
                    try:
                        timestamp = datetime.strptime(f"{row[0]} {row[1]}", '%Y-%m-%d %H:%M:%S')
                        transactions.append({
                            'timestamp': timestamp,
                            'new_items': json.loads(row[2]),
                            'old_items': json.loads(row[3]),
                            'comments': row[4],
                            'cash_amount': row[5],
                            'card_amount': row[6],
                            'upi_amount': row[7]
                        })
                    except Exception as e:
                        print(f"[DatabaseService] Error parsing transaction: {e}")
                        continue
                        
                print(f"[DatabaseService] Retrieved {len(transactions)} transactions")
                return transactions
                
        except Exception as e:
            print(f"[DatabaseService] Error getting transactions: {e}")
            return []
            
    def backup(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            shutil.copy2(self.db_file, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
            
    def restore(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            shutil.copy2(backup_path, self.db_file)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False 