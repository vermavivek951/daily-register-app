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

    # Create the application-specific directory
    app_data_dir = os.path.join(base_path, app_name)
    try:
        os.makedirs(app_data_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating AppData directory ({app_data_dir}): {e}. Using current directory as fallback.")
        # Fallback to current directory if AppData creation fails
        return os.path.abspath("transactions.db")

    return os.path.join(app_data_dir, 'transactions.db')

class DatabaseManager:
    # The constructor now ignores the db_path argument and uses AppData
    def __init__(self, db_path: Optional[str] = None):
        # Get the standard database path
        self.db_path = _get_appdata_db_path()
        print(f"[DatabaseManager] Using database file at: {self.db_path}")
        # Initialize the DB (creates tables if they don't exist)
        self.initialize_db()

    def initialize_db(self):
        """Initialize the database with required tables"""
        # Connect using the path determined in __init__
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            net_amount_paid REAL NOT NULL,
            cash_amount REAL NOT NULL,
            card_amount REAL NOT NULL,
            upi_amount REAL NOT NULL,
            comments TEXT
        )
        ''')

        # Create items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            item_type TEXT NOT NULL,
            is_billable INTEGER NOT NULL,
            weight REAL NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        )
        ''')

        # Create old items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS old_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            weight REAL NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_transaction(self, transaction_data: Dict[str, Any], items_data: List[Dict[str, Any]], old_items_data: List[Dict[str, Any]] = None) -> int:
        """Add a new transaction with its items and old items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert transaction
            cursor.execute('''
            INSERT INTO transactions (date, total_amount, net_amount_paid, cash_amount, card_amount, upi_amount, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_data['date'],
                transaction_data['total_amount'],
                transaction_data['net_amount_paid'],
                transaction_data['cash_amount'],
                transaction_data['card_amount'],
                transaction_data['upi_amount'],
                transaction_data['comments']
            ))
            
            transaction_id = cursor.lastrowid
            
            # Insert items
            for item in items_data:
                # Convert boolean is_billable to integer (1 for True, 0 for False)
                is_billable_int = 1 if item.get('is_billable', True) else 0
                
                cursor.execute('''
                INSERT INTO items (transaction_id, item_name, item_type, is_billable, weight, amount)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_id,
                    item['item_name'],
                    item['item_type'],
                    is_billable_int,  # Store as integer
                    item['weight'],
                    item['amount']
                ))

            # Insert old items
            if old_items_data:
                for item in old_items_data:
                    cursor.execute('''
                    INSERT INTO old_items (transaction_id, item_type, weight, amount)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        transaction_id,
                        item['item_type'],
                        item['weight'],
                        item['amount']
                    ))
            
            conn.commit()
            return transaction_id
            
        except Exception as e:
            conn.rollback()
            print(f"Error adding item: {str(e)}")  # Add error logging
            traceback.print_exc()  # Print full traceback
            raise e
        finally:
            conn.close()

    def get_transactions_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Get all transactions for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get transactions
            cursor.execute('''
            SELECT * FROM transactions WHERE date = ?
            ''', (date,))
            
            transactions = []
            for row in cursor.fetchall():
                transaction = {
                    'id': row[0],
                    'date': row[1],
                    'total_amount': row[2],
                    'net_amount_paid': row[3],
                    'cash_amount': row[4],
                    'card_amount': row[5],
                    'upi_amount': row[6],
                    'comments': row[7]
                }
                
                # Get items for this transaction
                cursor.execute('SELECT * FROM items WHERE transaction_id = ?', (transaction['id'],))
                items = []
                for item_row in cursor.fetchall():
                    items.append({
                        'id': item_row[0],
                        'transaction_id': item_row[1],
                        'item_name': item_row[2],
                        'item_type': item_row[3],
                        'is_billable': bool(item_row[4]),  # Convert integer to boolean
                        'weight': item_row[5],
                        'amount': item_row[6]
                    })
                transaction['items'] = items

                # Get old items for this transaction
                cursor.execute('SELECT * FROM old_items WHERE transaction_id = ?', (transaction['id'],))
                old_items = []
                for item_row in cursor.fetchall():
                    old_items.append({
                        'id': item_row[0],
                        'transaction_id': item_row[1],
                        'item_type': item_row[2],
                        'weight': item_row[3],
                        'amount': item_row[4]
                    })
                transaction['old_items'] = old_items
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions: {str(e)}")  # Add error logging
            traceback.print_exc()  # Print full traceback
            raise e
        finally:
            conn.close()

    def update_transaction(self, transaction_id: int, transaction_data: Dict[str, Any], items_data: List[Dict[str, Any]], old_items_data: List[Dict[str, Any]] = None):
        """Update an existing transaction and its items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update transaction
            cursor.execute('''
            UPDATE transactions 
            SET date=?, total_amount=?, net_amount_paid=?, cash_amount=?, card_amount=?, upi_amount=?, comments=?
            WHERE id=?
            ''', (
                transaction_data['date'],
                transaction_data['total_amount'],
                transaction_data['net_amount_paid'],
                transaction_data['cash_amount'],
                transaction_data['card_amount'],
                transaction_data['upi_amount'],
                transaction_data['comments'],
                transaction_id
            ))
            
            # Delete existing items
            cursor.execute('DELETE FROM items WHERE transaction_id = ?', (transaction_id,))
            
            # Insert updated items
            for item in items_data:
                # Convert boolean is_billable to integer (1 for True, 0 for False)
                is_billable_int = 1 if item.get('is_billable', True) else 0
                
                cursor.execute('''
                INSERT INTO items (transaction_id, item_name, item_type, is_billable, weight, amount)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_id,
                    item['item_name'],
                    item['item_type'],
                    is_billable_int,  # Store as integer
                    item['weight'],
                    item['amount']
                ))

            # Handle old items if provided
            if old_items_data is not None:
                # Delete existing old items
                cursor.execute('DELETE FROM old_items WHERE transaction_id = ?', (transaction_id,))
                
                # Insert updated old items
                for item in old_items_data:
                    cursor.execute('''
                    INSERT INTO old_items (transaction_id, item_type, weight, amount)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        transaction_id,
                        item['item_type'],
                        item['weight'],
                        item['amount']
                    ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating transaction: {str(e)}")  # Add error logging
            traceback.print_exc()  # Print full traceback
            raise e
        finally:
            conn.close()

    def delete_transaction(self, transaction_id: int):
        """Delete a transaction and its related items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete items first (foreign key constraint)
            cursor.execute('DELETE FROM items WHERE transaction_id = ?', (transaction_id,))
            cursor.execute('DELETE FROM old_items WHERE transaction_id = ?', (transaction_id,))
            
            # Delete transaction
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

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

    def update_transaction(self, transaction_id, transaction_data, items_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Start a transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Update transaction
            cursor.execute('''
                UPDATE transactions 
                SET total_amount = ?, net_amount_paid = ?, cash_amount = ?, card_amount = ?, upi_amount = ?, comments = ?
                WHERE id = ?
                ''', (
                    transaction_data['total_amount'],
                    transaction_data['net_amount_paid'],
                    transaction_data['cash_amount'],
                    transaction_data['card_amount'],
                    transaction_data['upi_amount'],
                    transaction_data['comments'],
                    transaction_id
                ))
            
            # Get existing item IDs
            cursor.execute("SELECT id FROM items WHERE transaction_id = ?", (transaction_id,))
            existing_item_ids = {row[0] for row in cursor.fetchall()}
            
            # Update or insert items
            for item in items_data:
                item_id = item.get('id')
                if item_id in existing_item_ids:
                    # Update existing item
                    cursor.execute('''
                    UPDATE items 
                    SET item_name = ?, item_type = ?, is_billable = ?, weight = ?, amount = ?,
                        old_item_returned = ?, old_item_weight = ?, old_item_amount = ?
                    WHERE id = ? AND transaction_id = ?
                    ''', (
                        item['item_name'],
                        item['item_type'],
                        item['is_billable'],
                        item['weight'],
                        item['amount'],
                        item['old_item_returned'],
                        item['old_item_weight'],
                        item['old_item_amount'],
                        item_id,
                        transaction_id
                    ))
                    existing_item_ids.remove(item_id)
                else:
                    # Insert new item
                    cursor.execute('''
                    INSERT INTO items (transaction_id, item_name, item_type, is_billable, weight, amount,
                                     old_item_returned, old_item_weight, old_item_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        transaction_id,
                        item['item_name'],
                        item['item_type'],
                        item['is_billable'],
                        item['weight'],
                        item['amount'],
                        item['old_item_returned'],
                        item['old_item_weight'],
                        item['old_item_amount']
                    ))
            
            # Delete items that were removed
            for old_id in existing_item_ids:
                cursor.execute("DELETE FROM items WHERE id = ? AND transaction_id = ?", (old_id, transaction_id))
            
            # Commit the transaction
            cursor.execute("COMMIT")
            
        except Exception as e:
            # Rollback in case of error
            cursor.execute("ROLLBACK")
            print(f"Error updating transaction: {str(e)}")
            print("Traceback:", traceback.format_exc())
            raise
        finally:
            conn.close()

    def get_transactions_by_date_range(self, from_date, to_date):
        """Get all transactions between two dates (inclusive)"""
        conn = None
        try:
            # Convert dates to strings in YYYY-MM-DD format
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = to_date.strftime("%Y-%m-%d")
            
            # Create database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get transactions within date range
            cursor.execute("""
                SELECT id, date, cash_amount, card_amount, upi_amount, 
                       net_amount_paid, total_amount, comments
                FROM transactions 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
            """, (from_date_str, to_date_str))
            
            transactions = []
            for row in cursor.fetchall():
                transaction = {
                    'id': row[0],
                    'date': row[1],
                    'cash_amount': row[2],
                    'card_amount': row[3],
                    'upi_amount': row[4],
                    'net_amount_paid': row[5],
                    'total_amount': row[6],
                    'comments': row[7]
                }
                
                # Get items for this transaction
                cursor.execute("""
                    SELECT item_name, item_type, weight, amount, is_billable
                    FROM items
                    WHERE transaction_id = ?
                """, (transaction['id'],))
                
                transaction['items'] = []
                for item_row in cursor.fetchall():
                    transaction['items'].append({
                        'item_name': item_row[0],
                        'item_type': item_row[1],
                        'weight': item_row[2],
                        'amount': item_row[3],
                        'is_billable': bool(item_row[4])
                    })
                
                # Get old items for this transaction
                cursor.execute("""
                    SELECT item_type, weight, amount
                    FROM old_items
                    WHERE transaction_id = ?
                """, (transaction['id'],))
                
                transaction['old_items'] = []
                for old_item_row in cursor.fetchall():
                    transaction['old_items'].append({
                        'item_type': old_item_row[0],
                        'weight': old_item_row[1],
                        'amount': old_item_row[2]
                    })
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transactions by date range: {str(e)}")
            raise
        finally:
            if conn:
                conn.close() 