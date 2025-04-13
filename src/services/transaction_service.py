from datetime import datetime
from typing import Dict, List, Optional

from models.transaction import Transaction, NewItem, OldItem
from database.db_manager import DatabaseManager
from services.item_service import ItemService

class TransactionService:
    """Service for handling transaction operations."""
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        """Initialize the transaction service.
        
        Args:
            db: Optional database manager instance. If not provided, a new one will be created.
        """
        self.db = db if db is not None else DatabaseManager()
        self.item_service = ItemService(db)
        self.current_transaction = {
            'new_items': [],
            'old_items': [],
            'payment_details': {},
            'comments': ''
        }
    
    def add_new_item(self, code: str, weight: float, amount: float, is_billable: bool = False) -> bool:
        """Add a new item to the current transaction."""
        try:
            # Validate item code
            if not code or len(code) < 2:
                return False
                
            # Get item details from service
            item_details = self.item_service.get_item_details(code)
            if not item_details:
                return False
                
            item = {
                'code': code,
                'name': item_details['name'],
                'type': item_details['type'],
                'weight': weight,
                'amount': amount,
                'is_billable': is_billable,
                'timestamp': datetime.now()
            }
            self.current_transaction['new_items'].append(item)
            return True
        except Exception as e:
            print(f"Error adding new item: {e}")
            return False
    
    def add_old_item(self, item_type: str, weight: float, amount: float) -> bool:
        """Add an old item to the current transaction."""
        try:
            if item_type not in ['G', 'S']:
                return False
                
            item = {
                'type': item_type,
                'weight': weight,
                'amount': amount,
                'timestamp': datetime.now()
            }
            self.current_transaction['old_items'].append(item)
            return True
        except Exception as e:
            print(f"Error adding old item: {e}")
            return False
    
    def remove_old_item(self, item: Dict) -> bool:
        """Remove an old item from the current transaction."""
        try:
            self.current_transaction['old_items'].remove(item)
            return True
        except ValueError:
            return False
    
    def set_comments(self, comments: str):
        """Set comments for the current transaction."""
        self.current_transaction['comments'] = comments
    
    def save_transaction(self, payment_details: Dict[str, float], comments: str = None) -> bool:
        """Save the current transaction to the database."""
        try:
            if not self.current_transaction['new_items'] and not self.current_transaction['old_items']:
                return False
                
            # Validate payment details
            for amount in payment_details.values():
                if amount < 0:
                    return False
                    
            self.current_transaction['payment_details'] = payment_details
            self.current_transaction['timestamp'] = datetime.now()
            
            # Set comments if provided
            if comments is not None:
                self.current_transaction['comments'] = comments
            
            # Save to database
            transaction_id = self.db.add_transaction(self.current_transaction)
            
            if transaction_id:
                # Clear current transaction
                self.clear_current_transaction()
                return True
            return False
            
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return False
            
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by ID.
        
        Args:
            transaction_id: The ID of the transaction to delete.
            
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            return self.db.delete_transaction(transaction_id)
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    def clear_current_transaction(self):
        """Clear the current transaction."""
        self.current_transaction = {
            'new_items': [],
            'old_items': [],
            'payment_details': {},
            'comments': ''
        }
    
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
    
    def get_transactions(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get transactions for a date range."""
        try:
            return self.db.get_transactions_by_date_range(start_date, end_date)
        except Exception as e:
            print(f"Error getting transactions: {e}")
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