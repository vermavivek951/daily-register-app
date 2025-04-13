import sqlite3
from datetime import datetime
import traceback
from typing import List, Dict, Any, Optional
import os
import sys # Import sys

# Helper function to determine the database path in AppData
def _get_appdata_db_path():
    """Gets the path to the database file in the user's AppData directory."""
    app_name = "DailyRegister"
    if sys.platform == 'win32':
        # Use APPDATA environment variable on Windows
        base_path = os.getenv('APPDATA')
    # Add elif conditions here for macOS ('darwin') or Linux if needed in the future
    # elif sys.platform == 'darwin':
    #     base_path = os.path.expanduser('~/Library/Application Support')
    # else: # Linux/other
    #     base_path = os.path.expanduser('~/.local/share')
    else:
        # Fallback to home directory if platform not recognized or APPDATA not set
        base_path = os.path.expanduser('~')
        if not base_path: # Handle cases where home dir might not be resolvable
             base_path = "." # Fallback to current directory

    if not base_path:
        # Final fallback if APPDATA wasn't set and home dir didn't work
        print("Warning: Could not determine AppData or home directory. Using current directory for database.")
        base_path = "."

    # Create the app directory if it doesn't exist
    app_dir = os.path.join(base_path, app_name)
    os.makedirs(app_dir, exist_ok=True)
    
    # Return the full path to the database file
    return os.path.join(app_dir, "transactions.db")

class DatabaseManager:
    """Manages database operations for the application."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database manager.
        
        Args:
            db_path: Optional path to the database file. If not provided, uses the default path.
        """
        self.db_path = db_path if db_path is not None else _get_appdata_db_path()
        print(f"[DatabaseManager] Using database file at: {self.db_path}")
        self.conn = None
        self._create_tables()

    def _create_tables(self):
        """Create the necessary tables if they don't exist."""
        try:
            if self.conn:
                self.conn.close()
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # Create transactions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    timestamp DATETIME NOT NULL,
                    comments TEXT,
                    total_amount REAL DEFAULT 0,
                    net_amount_paid REAL DEFAULT 0,
                    cash_amount REAL DEFAULT 0,
                    card_amount REAL DEFAULT 0,
                    upi_amount REAL DEFAULT 0
            )
            ''')

            # Create items table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                weight REAL NOT NULL,
                amount REAL NOT NULL,
                    is_billable BOOLEAN DEFAULT 1,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE
            )
            ''')

                # Create old_items table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS old_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                weight REAL NOT NULL,
                amount REAL NOT NULL,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE
            )
            ''')

            self.conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            if self.conn:
                self.conn.close()
                self.conn = None  # Set to None to indicate it's closed

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()

    def add_transaction(self, transaction_data: Dict[str, Any]) -> int:
        """Add a new transaction.
        
        Args:
            transaction_data: Dictionary containing transaction details including new_items, old_items, and payment_details.
            
        Returns:
            int: The ID of the newly created transaction.
        """
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Calculate totals
            total_amount = sum(item['amount'] for item in transaction_data.get('new_items', []))
            total_amount += sum(item['amount'] for item in transaction_data.get('old_items', []))
            net_amount_paid = sum(
                transaction_data.get('payment_details', {}).get(payment_type, 0.0)
                for payment_type in ['cash', 'card', 'upi']
            )
            
            # Insert transaction
            cursor.execute('''
                INSERT INTO transactions (
                    date, timestamp, comments, total_amount, net_amount_paid,
                    cash_amount, card_amount, upi_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().date(),
                transaction_data.get('timestamp', datetime.now()),
                transaction_data.get('comments', ''),
                total_amount,
                net_amount_paid,
                transaction_data.get('payment_details', {}).get('cash', 0.0),
                transaction_data.get('payment_details', {}).get('card', 0.0),
                transaction_data.get('payment_details', {}).get('upi', 0.0)
            ))
            
            transaction_id = cursor.lastrowid
            
            # Insert new items
            for item in transaction_data.get('new_items', []):
                cursor.execute('''
                    INSERT INTO items (transaction_id, code, name, type, weight, amount, is_billable)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_id,
                    item['code'],
                    item['name'],
                    item['type'],
                    item['weight'],
                    item['amount'],
                    item.get('is_billable', False)
                ))

            # Insert old items
            for item in transaction_data.get('old_items', []):
                    cursor.execute('''
                    INSERT INTO old_items (transaction_id, type, weight, amount)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        transaction_id,
                    item['type'],
                        item['weight'],
                        item['amount']
                    ))
            
            self.conn.commit()
            return transaction_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error adding transaction: {e}")
            raise

    def get_transactions_by_date(self, date: datetime.date) -> List[Dict[str, Any]]:
        """Get all transactions for a specific date."""
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Get transactions
            cursor.execute('''
            SELECT * FROM transactions WHERE date = ?
            ''', (date,))
            
            transactions = []
            for row in cursor.fetchall():
                transaction = {
                    'id': row[0],
                    'date': row[1],
                    'timestamp': row[2],
                    'comments': row[3],
                    'total_amount': row[4],
                    'net_amount_paid': row[5],
                    'cash_amount': row[6],
                    'card_amount': row[7],
                    'upi_amount': row[8]
                }
                
                # Get items for this transaction
                cursor.execute('SELECT * FROM items WHERE transaction_id = ?', (transaction['id'],))
                items = []
                for item_row in cursor.fetchall():
                    items.append({
                        'id': item_row[0],
                        'transaction_id': item_row[1],
                        'code': item_row[2],
                        'name': item_row[3],
                        'type': item_row[4],
                        'weight': item_row[5],
                        'amount': item_row[6],
                        'is_billable': bool(item_row[7])
                    })
                transaction['new_items'] = items

                # Get old items for this transaction
                cursor.execute('SELECT * FROM old_items WHERE transaction_id = ?', (transaction['id'],))
                old_items = []
                for item_row in cursor.fetchall():
                    old_items.append({
                        'id': item_row[0],
                        'transaction_id': item_row[1],
                        'type': item_row[2],
                        'weight': item_row[3],
                        'amount': item_row[4]
                    })
                transaction['old_items'] = old_items
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions: {e}")
            raise

    def get_transaction_summary(self, date: datetime.date) -> Dict[str, Dict[str, float]]:
        """Get summary of transactions for a specific date."""
        try:
            transactions = self.get_transactions_by_date(date)
            
            summary = {
                'new_items': {'gold': 0.0, 'silver': 0.0},
                'old_items': {'gold': 0.0, 'silver': 0.0},
                'billable_items': {'gold': 0.0, 'silver': 0.0, 'amount': 0.0},
                'payments': {'cash': 0.0, 'card': 0.0, 'upi': 0.0},
                'total_amount': 0.0,
                'net_amount_paid': 0.0,
                'total_weight': 0.0
            }
            
            for transaction in transactions:
                # Sum up new items
                for item in transaction['new_items']:
                    item_type = 'gold' if item['type'] == 'G' else 'silver'
                    summary['new_items'][item_type] += item['weight']
                    summary['total_weight'] += item['weight']
                    if item['is_billable']:
                        summary['billable_items'][item_type] += item['weight']
                        summary['billable_items']['amount'] += item['amount']
                
                # Sum up old items
                for item in transaction['old_items']:
                    item_type = 'gold' if item['type'] == 'G' else 'silver'
                    summary['old_items'][item_type] += item['weight']
                    summary['total_weight'] += item['weight']
                
                # Sum up payments
                summary['payments']['cash'] += transaction['cash_amount']
                summary['payments']['card'] += transaction['card_amount']
                summary['payments']['upi'] += transaction['upi_amount']
                
                # Sum up totals
                summary['total_amount'] += transaction['total_amount']
                summary['net_amount_paid'] += transaction['net_amount_paid']
            
            return summary
            
        except Exception as e:
            print(f"Error getting transaction summary: {e}")
            raise

    def update_transaction(self, transaction_id: int, transaction_data: Dict[str, Any]) -> bool:
        """Update an existing transaction.
        
        Args:
            transaction_id: The ID of the transaction to update.
            transaction_data: Dictionary containing updated transaction details.
            
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Calculate totals
            total_amount = sum(item['amount'] for item in transaction_data.get('new_items', []))
            total_amount += sum(item['amount'] for item in transaction_data.get('old_items', []))
            net_amount_paid = sum(
                transaction_data.get('payment_details', {}).get(payment_type, 0.0)
                for payment_type in ['cash', 'card', 'upi']
            )
            
            # Update transaction
            cursor.execute('''
            UPDATE transactions 
                SET date = ?, timestamp = ?, comments = ?, total_amount = ?, net_amount_paid = ?,
                    cash_amount = ?, card_amount = ?, upi_amount = ?
                WHERE id = ?
            ''', (
                datetime.now().date(),
                transaction_data.get('timestamp', datetime.now()),
                transaction_data.get('comments', ''),
                total_amount,
                net_amount_paid,
                transaction_data.get('payment_details', {}).get('cash', 0.0),
                transaction_data.get('payment_details', {}).get('card', 0.0),
                transaction_data.get('payment_details', {}).get('upi', 0.0),
                transaction_id
            ))
            
            # Delete existing items
            cursor.execute('DELETE FROM items WHERE transaction_id = ?', (transaction_id,))
            cursor.execute('DELETE FROM old_items WHERE transaction_id = ?', (transaction_id,))
            
            # Insert new items
            for item in transaction_data.get('new_items', []):
                cursor.execute('''
                    INSERT INTO items (transaction_id, code, name, type, weight, amount, is_billable)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_id,
                    item['code'],
                    item['name'],
                    item['type'],
                    item['weight'],
                    item['amount'],
                    item.get('is_billable', False)
                ))
            
            # Insert old items
            for item in transaction_data.get('old_items', []):
                    cursor.execute('''
                    INSERT INTO old_items (transaction_id, type, weight, amount)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        transaction_id,
                    item['type'],
                        item['weight'],
                        item['amount']
                    ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error updating transaction: {e}")
            return False

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction and its related items"""
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Delete items first (foreign key constraint)
            cursor.execute('DELETE FROM items WHERE transaction_id = ?', (transaction_id,))
            cursor.execute('DELETE FROM old_items WHERE transaction_id = ?', (transaction_id,))
            
            # Delete transaction
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error deleting transaction: {e}")
            return False

    def delete_all_transactions_for_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all transaction IDs for the date
        cursor.execute("SELECT id FROM transactions WHERE date = ?", (date,))
        transaction_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete items first
        for t_id in transaction_ids:
            cursor.execute("DELETE FROM items WHERE transaction_id = ?", (t_id,))
        
        # Delete transactions
        cursor.execute("DELETE FROM transactions WHERE date = ?", (date,))
        
        conn.commit()
        conn.close()

    def get_transactions_by_date_range(self, from_date: datetime.date, to_date: datetime.date) -> List[Dict[str, Any]]:
        """Get all transactions between two dates (inclusive)."""
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Get transactions within date range
            cursor.execute("""
                SELECT id, date, timestamp, comments, total_amount, net_amount_paid,
                       cash_amount, card_amount, upi_amount
                FROM transactions 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
            """, (from_date, to_date))
            
            transactions = []
            for row in cursor.fetchall():
                transaction = {
                    'id': row[0],
                    'date': row[1],
                    'timestamp': row[2],
                    'comments': row[3],
                    'total_amount': row[4],
                    'net_amount_paid': row[5],
                    'cash_amount': row[6],
                    'card_amount': row[7],
                    'upi_amount': row[8]
                }
                
                # Get items for this transaction
                cursor.execute("""
                    SELECT code, name, type, weight, amount, is_billable
                    FROM items
                    WHERE transaction_id = ?
                """, (transaction['id'],))
                
                transaction['new_items'] = []
                for item_row in cursor.fetchall():
                    transaction['new_items'].append({
                        'code': item_row[0],
                        'name': item_row[1],
                        'type': item_row[2],
                        'weight': item_row[3],
                        'amount': item_row[4],
                        'is_billable': bool(item_row[5])
                    })
                
                # Get old items for this transaction
                cursor.execute("""
                    SELECT type, weight, amount
                    FROM old_items
                    WHERE transaction_id = ?
                """, (transaction['id'],))
                
                transaction['old_items'] = []
                for old_item_row in cursor.fetchall():
                    transaction['old_items'].append({
                        'type': old_item_row[0],
                        'weight': old_item_row[1],
                        'amount': old_item_row[2]
                    })
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions by date range: {e}")
            raise

    def get_transactions_range(self, start_date, end_date):
        """Get transactions between two dates (inclusive).
        
        Args:
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)
            
        Returns:
            list: List of transactions between the dates
        """
        try:
            # Always create a new connection for this operation
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get transactions within date range
            cursor.execute("""
                SELECT id, date, timestamp, comments, total_amount, net_amount_paid,
                       cash_amount, card_amount, upi_amount
                FROM transactions 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
            """, (start_date, end_date))
            
            transactions = []
            for row in cursor.fetchall():
                # Extract time from timestamp
                timestamp = row[2]
                time_str = timestamp.split()[1] if timestamp and ' ' in timestamp else ''
                
                transaction = {
                    'id': row[0],
                    'date': row[1],
                    'time': time_str,
                    'comments': row[3],
                    'total_amount': row[4],
                    'net_amount_paid': row[5],
                    'cash_amount': row[6],
                    'card_amount': row[7],
                    'upi_amount': row[8],
                    'new_items': [],
                    'old_items': []
                }
                
                # Get new items for this transaction
                cursor.execute("""
                    SELECT code, name, type, weight, amount, is_billable
                    FROM items
                    WHERE transaction_id = ?
                """, (transaction['id'],))
                
                for item_row in cursor.fetchall():
                    transaction['new_items'].append({
                        'code': item_row[0],
                        'name': item_row[1],
                        'type': item_row[2],
                        'weight': item_row[3],
                        'amount': item_row[4],
                        'is_billable': bool(item_row[5])
                    })
                
                # Get old items for this transaction
                cursor.execute("""
                    SELECT type, weight, amount
                    FROM old_items
                    WHERE transaction_id = ?
                """, (transaction['id'],))
                
                for old_item_row in cursor.fetchall():
                    transaction['old_items'].append({
                        'type': old_item_row[0],
                        'weight': old_item_row[1],
                        'amount': old_item_row[2]
                    })
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions by date range: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close() 

    def save_transaction(self, transaction_data):
        """Save a transaction to the database.
        
        Args:
            transaction_data: Dictionary containing transaction details including new_items, old_items, and payment_details.
            
        Returns:
            bool: True if the transaction was saved successfully, False otherwise.
        """
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Calculate totals
            total_amount = sum(item['amount'] for item in transaction_data.get('new_items', []))
            total_amount += sum(item['amount'] for item in transaction_data.get('old_items', []))
            net_amount_paid = sum(
                transaction_data.get('payment_details', {}).get(payment_type, 0.0)
                for payment_type in ['cash', 'card', 'upi']
            )
            
            # Insert transaction
            cursor.execute('''
                INSERT INTO transactions (
                    date, timestamp, comments, total_amount, net_amount_paid,
                    cash_amount, card_amount, upi_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().date(),
                transaction_data.get('timestamp', datetime.now()),
                transaction_data.get('comments', ''),
                total_amount,
                net_amount_paid,
                transaction_data.get('payment_details', {}).get('cash', 0.0),
                transaction_data.get('payment_details', {}).get('card', 0.0),
                transaction_data.get('payment_details', {}).get('upi', 0.0)
            ))
            
            transaction_id = cursor.lastrowid
            
            # Insert new items
            for item in transaction_data.get('new_items', []):
                cursor.execute('''
                    INSERT INTO items (transaction_id, code, name, type, weight, amount, is_billable)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_id,
                    item['code'],
                    item['name'],
                    item['type'],
                    item['weight'],
                    item['amount'],
                    item.get('is_billable', False)
                ))

            # Insert old items
            for item in transaction_data.get('old_items', []):
                    cursor.execute('''
                    INSERT INTO old_items (transaction_id, type, weight, amount)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        transaction_id,
                    item['type'],
                        item['weight'],
                        item['amount']
                    ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error saving transaction: {e}")
            return False