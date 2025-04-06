from datetime import datetime
from typing import Dict, List, Optional, Any

from models.transaction import Transaction, NewItem, OldItem
from services.transaction_service import TransactionService
from services.database_service import DatabaseService
from services.item_service import ItemService

class TransactionController:
    """Controller for handling transaction operations."""
    
    def __init__(self, db_service=None):
        """Initialize the controller with a database service."""
        self.service = TransactionService()
        self.db_service = db_service or DatabaseService()
        self.current_transaction = Transaction()
        self.item_service = ItemService()
    
    def validate_item_code(self, code: str) -> bool:
        """Validate item code format."""
        if not code:
            return False
        # Code should start with G or S for Gold/Silver
        return code.startswith(('G', 'S'))
    
    def validate_item_type(self, type_: str) -> bool:
        """Validate item type."""
        if not type_:
            return False
        return type_.upper() in ['G', 'S']
    
    def validate_amount(self, amount: float) -> bool:
        """Validate amount value."""
        return amount > 0
    
    def validate_weight(self, weight: float) -> bool:
        """Validate weight value."""
        return weight > 0
    
    def add_new_item(self, code: str, weight: float, amount: float, is_billable: bool = False) -> bool:
        """Add a new item to the current transaction."""
        try:
            if not self.validate_item_code(code):
                raise ValueError("Invalid item code. Must start with G or S")
                
            if not self.validate_weight(weight):
                raise ValueError("Weight must be greater than 0")
                
            if not self.validate_amount(amount):
                raise ValueError("Amount must be greater than 0")
                
            # Update item last used timestamp
            self.item_service.update_last_used(code)
            
            self.current_transaction.add_new_item({
                'code': code,
                'weight': weight,
                'amount': amount,
                'is_billable': is_billable
            })
            return True
        except Exception as e:
            print(f"Error adding new item: {e}")
            return False
    
    def add_old_item(self, item_type: str, weight: float, amount: float) -> bool:
        """Add an old item to the current transaction."""
        try:
            if not self.validate_item_type(item_type):
                raise ValueError("Invalid item type. Must be Gold or Silver")
                
            if not self.validate_weight(weight):
                raise ValueError("Weight must be greater than 0")
                
            if not self.validate_amount(amount):
                raise ValueError("Amount must be greater than 0")
                
            self.current_transaction.add_old_item({
                'type': item_type,
                'weight': weight,
                'amount': amount
            })
            return True
        except Exception as e:
            print(f"Error adding old item: {e}")
            return False
    
    def remove_new_item(self, index: int) -> bool:
        """Remove a new item from the current transaction."""
        try:
            self.current_transaction.remove_new_item(index)
            return True
        except Exception as e:
            print(f"Error removing new item: {e}")
            return False
    
    def remove_old_item(self, index: int) -> bool:
        """Remove an old item from the current transaction."""
        try:
            self.current_transaction.remove_old_item(index)
            return True
        except Exception as e:
            print(f"Error removing old item: {e}")
            return False
    
    def validate_payment_details(self, payment_details: Dict[str, float]) -> bool:
        """Validate payment details."""
        try:
            # Ensure all payment values are non-negative
            if not all(isinstance(amount, (int, float)) and amount >= 0 for amount in payment_details.values()):
                return False
                
            total_payment = sum(payment_details.values())
            if total_payment <= 0:
                return False
                
            total_amount = self.current_transaction.get_total_amount()
            if total_payment > total_amount:
                return False
                
            return True
        except Exception as e:
            print(f"Error validating payment details: {e}")
            return False
    
    def save_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Save a transaction to the database."""
        try:
            # Pass the transaction dictionary directly to the database service
            return self.db_service.save_transaction(transaction)
        except Exception as e:
            print(f"[TransactionController] Error saving transaction: {e}")
            return False
    
    def delete_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Delete a transaction from the database."""
        try:
            return self.db_service.delete_transaction(transaction)
        except Exception as e:
            print(f"[TransactionController] Error deleting transaction: {e}")
            return False
    
    def get_daily_summary(self, date) -> Dict[str, Any]:
        """Get summary for a specific date."""
        try:
            transactions = self.get_transactions_by_date(date)
            
            # Initialize totals
            summary = {
                'new_weight': 0,
                'new_amount': 0,
                'old_weight': 0,
                'old_amount': 0,
                'cash_total': 0,
                'card_total': 0,
                'upi_total': 0
            }
            
            # Calculate totals
            for transaction in transactions:
                # New items
                for item in transaction.get('new_items', []):
                    summary['new_weight'] += float(item.get('weight', 0))
                    summary['new_amount'] += float(item.get('amount', 0))
                
                # Old items
                for item in transaction.get('old_items', []):
                    summary['old_weight'] += float(item.get('weight', 0))
                    summary['old_amount'] += float(item.get('amount', 0))
                
                # Payment totals
                summary['cash_total'] += float(transaction.get('cash_amount', 0))
                summary['card_total'] += float(transaction.get('card_amount', 0))
                summary['upi_total'] += float(transaction.get('upi_amount', 0))
            
            return summary
            
        except Exception as e:
            print(f"[TransactionController] Error getting daily summary: {e}")
            return {
                'new_weight': 0,
                'new_amount': 0,
                'old_weight': 0,
                'old_amount': 0,
                'cash_total': 0,
                'card_total': 0,
                'upi_total': 0
            }
    
    def get_transactions(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get transactions for a date range."""
        try:
            return self.db_service.get_transactions(start_date, end_date)
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def get_current_transaction_summary(self) -> Dict:
        """Get summary of the current transaction."""
        return self.current_transaction.get_summary()
    
    def get_total_amount(self) -> float:
        """Get total amount of the current transaction."""
        return self.current_transaction.get_total_amount()
    
    def export_to_excel(self, start_date: datetime, end_date: datetime, filename: str) -> bool:
        """Export transactions to Excel."""
        try:
            transactions = self.get_transactions(start_date, end_date)
            if not transactions:
                raise ValueError("No transactions found for the specified date range")
                
            # TODO: Implement Excel export using pandas or openpyxl
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Backup the database."""
        try:
            return self.db_service.backup(backup_path)
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore the database from backup."""
        try:
            return self.db_service.restore(backup_path)
        except Exception as e:
            print(f"Error restoring database: {e}")
            return False
    
    def get_item_suggestions(self, code_prefix: str) -> List[Dict]:
        """Get item suggestions based on code prefix."""
        try:
            # Get suggestions from item service
            suggestions = self.item_service.get_suggestions(code_prefix)
            
            # Format suggestions for display
            formatted_suggestions = []
            for suggestion in suggestions:
                formatted_suggestions.append({
                    'code': suggestion['code'],
                    'name': suggestion['name'],
                    'type': suggestion['type'],
                    'last_used': suggestion.get('last_used', '')
                })
                
            return formatted_suggestions
        except Exception as e:
            print(f"Error getting item suggestions: {e}")
            return []
    
    def get_transactions_for_date(self, date: datetime) -> List[Dict]:
        """Get transactions for a specific date."""
        try:
            # Create start and end datetime for the given date
            start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
            return self.db_service.get_transactions(start_date, end_date)
        except Exception as e:
            print(f"Error getting transactions for date: {e}")
            return []

    def get_transactions_by_date(self, date) -> List[Dict[str, Any]]:
        """Get all transactions for a specific date."""
        try:
            return self.db_service.get_transactions_by_date(date)
        except Exception as e:
            print(f"[TransactionController] Error getting transactions: {e}")
            return [] 