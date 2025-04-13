import sqlite3
import os
from datetime import datetime
import json

class DatabaseService:
    def __init__(self, db_path):
        self.db_path = db_path
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Initialize the database if it doesn't exist
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database with required tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create transactions table with the correct schema
            cursor.execute("""
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
            """)
            
            # Create new_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS new_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER,
                    item_code TEXT NOT NULL,
                    item_name TEXT,
                    weight REAL NOT NULL,
                    amount REAL NOT NULL,
                    is_billable BOOLEAN DEFAULT 0,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
                )
            """)
            
            # Create old_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS old_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER,
                    type TEXT NOT NULL,
                    weight REAL NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
                )
            """)
            
            conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def get_transactions_range(self, from_date, to_date):
        """
        Get all transactions between two dates (inclusive).
        Returns a list of transactions with their items.
        """
        try:
            # Convert dates to string format for SQLite comparison
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = to_date.strftime('%Y-%m-%d')
            
            # Get transactions within date range
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, new_items, old_items, comments, cash_amount, card_amount, upi_amount
                FROM transactions
                WHERE date(timestamp) BETWEEN ? AND ?
                ORDER BY timestamp
            """, (from_date_str, to_date_str))
            
            transactions = []
            for row in cursor.fetchall():
                # Parse timestamp to get date and time
                timestamp = row[1]
                try:
                    # First try ISO format
                    dt = datetime.fromisoformat(timestamp)
                except:
                    try:
                        # Then try standard format
                        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    except:
                        # Fallback if timestamp format is different
                        parts = timestamp.split(' ')
                        date_str = parts[0] if parts else timestamp
                        time_str = parts[1] if len(parts) > 1 else '00:00:00'
                        dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                
                date_str = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%H:%M:%S')
                
                # Parse new_items and old_items from JSON
                try:
                    new_items = json.loads(row[2]) if row[2] else []
                except:
                    new_items = []
                
                try:
                    old_items = json.loads(row[3]) if row[3] else []
                except:
                    old_items = []
                
                transaction = {
                    'id': row[0],
                    'date': date_str,
                    'time': time_str,
                    'comments': row[4],
                    'cash_amount': row[5],
                    'card_amount': row[6],
                    'upi_amount': row[7],
                    'new_items': new_items,
                    'old_items': old_items
                }
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions range: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def get_transactions_by_date(self, date):
        """
        Get all transactions for a specific date.
        Returns a list of transactions with their items.
        """
        try:
            # Convert date to string format for SQLite comparison
            date_str = date.strftime('%Y-%m-%d')
            
            # Get transactions for the date
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, new_items, old_items, comments, cash_amount, card_amount, upi_amount
                FROM transactions
                WHERE date(timestamp) = ?
                ORDER BY timestamp
            """, (date_str,))
            
            transactions = []
            for row in cursor.fetchall():
                # Parse timestamp to get date and time
                timestamp = row[1]
                try:
                    # First try ISO format
                    dt = datetime.fromisoformat(timestamp)
                except:
                    try:
                        # Then try standard format
                        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    except:
                        # Fallback if timestamp format is different
                        parts = timestamp.split(' ')
                        date_str = parts[0] if parts else timestamp
                        time_str = parts[1] if len(parts) > 1 else '00:00:00'
                        dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                
                date_str = dt.strftime('%Y-%m-%d')
                time_str = dt.strftime('%H:%M:%S')
                
                # Parse new_items and old_items from JSON
                try:
                    new_items = json.loads(row[2]) if row[2] else []
                    # Ensure is_billable is included for each item
                    for item in new_items:
                        if 'is_billable' not in item:
                            item['is_billable'] = False  # Default to False if not specified
                except:
                    new_items = []
                
                try:
                    old_items = json.loads(row[3]) if row[3] else []
                except:
                    old_items = []
                
                transaction = {
                    'id': row[0],
                    'date': date_str,
                    'time': time_str,
                    'comments': row[4],
                    'cash_amount': row[5],
                    'card_amount': row[6],
                    'upi_amount': row[7],
                    'new_items': new_items,
                    'old_items': old_items
                }
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions by date: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_transaction(self, transaction_id):
        """
        Delete a transaction by its ID.
        
        Args:
            transaction_id: The ID of the transaction to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete the transaction
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            
            # Commit the changes
            conn.commit()
            
            # Check if any row was affected
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close() 