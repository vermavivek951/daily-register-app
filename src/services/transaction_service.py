from datetime import datetime
from typing import Dict, List, Optional

from models.transaction import Transaction, NewItem, OldItem
from database.db_manager import DatabaseManager

class TransactionService:
    """Service for handling transaction operations."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.current_transaction = {
            'new_items': [],
            'old_items': [],
            'payment_details': {}
        }
    
    def add_new_item(self, code: str, weight: float, amount: float, is_billable: bool = False) -> bool:
        """Add a new item to the current transaction."""
        try:
            item = {
                'code': code,
                'weight': weight,
                'amount': amount,
                'is_billable': is_billable,
                'timestamp': datetime.now()
            }
            self.current_transaction['new_items'].append(item)
            return True
        except Exception as e:
            # Log error
            return False
    
    def add_old_item(self, item_type: str, weight: float, amount: float) -> bool:
        """Add an old item to the current transaction."""
        try:
            item = {
                'type': item_type,
                'weight': weight,
                'amount': amount,
                'timestamp': datetime.now()
            }
            self.current_transaction['old_items'].append(item)
            return True
        except Exception as e:
            # Log error
            return False
    
    def remove_old_item(self, item: Dict) -> bool:
        """Remove an old item from the current transaction."""
        try:
            self.current_transaction['old_items'].remove(item)
            return True
        except ValueError:
            return False
    
    def save_transaction(self, payment_details: Dict[str, float]) -> bool:
        """Save the current transaction to the database."""
        try:
            self.current_transaction['payment_details'] = payment_details
            self.current_transaction['timestamp'] = datetime.now()
            
            # Save to database
            success = self.db.save_transaction(self.current_transaction)
            
            if success:
                # Clear current transaction
                self.current_transaction = {
                    'new_items': [],
                    'old_items': [],
                    'payment_details': {}
                }
            
            return success
        except Exception as e:
            # Log error
            return False
    
    def get_daily_summary(self, date: datetime) -> Dict[str, Dict[str, float]]:
        """Get the summary for a specific date."""
        try:
            return self.db.get_daily_summary(date)
        except Exception as e:
            # Log error
            return {
                'new_items': {'gold': 0.0, 'silver': 0.0},
                'old_items': {'gold': 0.0, 'silver': 0.0},
                'billable_items': {'gold': 0.0, 'silver': 0.0, 'amount': 0.0},
                'payments': {'cash': 0.0, 'card': 0.0, 'upi': 0.0}
            }
    
    def get_transactions(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions for a date range."""
        try:
            transactions_data = self.db.get_transactions(start_date, end_date)
            return [Transaction.from_dict(data) for data in transactions_data]
        except Exception as e:
            # Log error
            return []
    
    def get_current_transaction(self) -> Dict:
        """Get the current transaction being worked on."""
        return self.current_transaction
    
    def backup_data(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            return self.db.backup_database(backup_path)
        except Exception as e:
            # Log error
            return False
    
    def restore_data(self, backup_path: str) -> bool:
        """Restore data from a backup."""
        try:
            return self.db.restore_database(backup_path)
        except Exception as e:
            # Log error
            return False 