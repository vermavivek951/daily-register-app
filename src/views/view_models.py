from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal
from models.transaction import Transaction, NewItem, OldItem
from controllers.transaction_controller import TransactionController
from utils.validation import (
    is_valid_float, is_valid_item_code, is_valid_item_type,
    parse_amount, parse_weight, validate_payment_amounts
)
from PyQt6.QtCore import QObject, pyqtSignal
from database.db_manager import DatabaseManager

class TransactionViewModel(QObject):
    """View model for handling transaction-related UI logic"""
    def __init__(self, db_manager=None):
        """Initialize the view model with a transaction controller."""
        super().__init__()
        self.db_manager = db_manager or DatabaseManager()
        self.current_transaction = {
            'new_items': [],
            'old_items': [],
            'comments': ''
        }

    def add_new_item(self, item):
        """Add a new item to the current transaction."""
        try:
            # Validate required fields
            if not all(key in item for key in ['code', 'name', 'weight', 'amount']):
                raise ValueError("Missing required fields in new item")
                
            # Ensure weight and amount are float
            weight = float(item['weight'])
            amount = float(item['amount'])
            
            if weight <= 0 or amount <= 0:
                raise ValueError("Weight and amount must be greater than 0")
                
            # Set item type based on code if not provided
            if 'type' not in item:
                item['type'] = 'G' if item['code'].upper().startswith('G') else 'S'
                
            # Create new item dictionary
            new_item = {
                'code': item['code'].upper(),
                'name': item['name'],
                'type': item['type'].upper(),  # Ensure type is uppercase
                'weight': weight,
                'amount': amount,
                'is_billable': bool(item.get('is_billable', False))
            }
            
            print(f"[ViewModel] Adding new item: {new_item}")
            
            # Add to current transaction
            if 'new_items' not in self.current_transaction:
                self.current_transaction['new_items'] = []
            self.current_transaction['new_items'].append(new_item)
            
            return True
            
        except Exception as e:
            print(f"[ViewModel] Error adding new item: {e}")
            return False

    def add_old_item(self, item):
        """Add an old item to the current transaction."""
        try:
            self.current_transaction['old_items'].append(item)
            return True
        except Exception as e:
            print(f"Error adding old item: {e}")
            return False

    def save_transaction(self, transaction_data):
        """Save a transaction to the database."""
        try:
            # Ensure we have a valid db_manager
            if not self.db_manager:
                print("[ViewModel] Error: No database manager available")
                return False
                
            # Format the transaction data
            formatted_data = {
                'timestamp': datetime.now(),
                'comments': transaction_data.get('comments', ''),
                'new_items': self.current_transaction.get('new_items', []),
                'old_items': self.current_transaction.get('old_items', []),
                'payment_details': {
                    'cash': float(transaction_data.get('cash_amount', 0)),
                    'card': float(transaction_data.get('card_amount', 0)),
                    'upi': float(transaction_data.get('upi_amount', 0))
                }
            }
            
            print(f"[ViewModel] Saving transaction: {formatted_data}")
            
            # Save using the database manager
            transaction_id = self.db_manager.add_transaction(formatted_data)
            
            if transaction_id:
                print(f"[ViewModel] Transaction saved successfully with ID: {transaction_id}")
                # Clear the current transaction after successful save
                self.clear_transaction()
                return True
            else:
                print("[ViewModel] Failed to save transaction")
            return False
            
        except Exception as e:
            print(f"[ViewModel] Error saving transaction: {e}")
            return False

    def delete_transaction(self, transaction_id):
        """Delete a transaction from the database."""
        return self.db_manager.delete_transaction(transaction_id)

    def get_transactions(self, start_date, end_date):
        """Get transactions for a date range."""
        return self.db_manager.get_transactions(start_date, end_date)

    def get_transactions_by_date(self, date):
        """Get transactions for a specific date."""
        return self.db_manager.get_transactions_by_date(date)

    def get_transactions_range(self, start_date, end_date):
        """Get transactions for a date range."""
        return self.db_manager.get_transactions_range(start_date, end_date)

    def format_transaction_for_display(self, transaction):
        """Format a transaction for display in the UI."""
        try:
            # Format date and time
            date = transaction.get('date', '')
            time = transaction.get('time', '')
            
            # Format comments
            comments = transaction.get('comments', '')
            
            # Format payment amounts
            cash_amount = transaction.get('cash_amount', 0)
            card_amount = transaction.get('card_amount', 0)
            upi_amount = transaction.get('upi_amount', 0)
            
            # Format items
            new_items = transaction.get('new_items', [])
            old_items = transaction.get('old_items', [])
            
            return {
                'id': transaction.get('id'),
                'date': date,
                'time': time,
                'comments': comments,
                'cash_amount': cash_amount,
                'card_amount': card_amount,
                'upi_amount': upi_amount,
                'new_items': new_items,
                'old_items': old_items,
                'total_amount': transaction.get('total_amount', 0),
                'net_amount_paid': transaction.get('net_amount_paid', 0)
            }
        except Exception as e:
            print(f"Error formatting transaction: {e}")
            return None

    def get_daily_summary(self, date):
        """Get summary for a specific date."""
        try:
            transactions = self.get_transactions(date, date)
            
            # Initialize totals
            summary = {
                'new_gold_weight': 0,
                'new_silver_weight': 0,
                'new_amount': 0,
                'old_gold_weight': 0,
                'old_silver_weight': 0,
                'old_amount': 0,
                'cash_total': 0,
                'card_total': 0,
                'upi_total': 0
            }
            
            # Calculate totals
            for transaction in transactions:
                # New items
                for item in transaction.get('new_items', []):
                    weight = float(item.get('weight', 0))
                    if item.get('type', '').upper() in ['G', 'GOLD']:
                        summary['new_gold_weight'] += weight
                    elif item.get('type', '').upper() in ['S', 'SILVER']:
                        summary['new_silver_weight'] += weight
                    summary['new_amount'] += float(item.get('amount', 0))
                
                # Old items
                for item in transaction.get('old_items', []):
                    weight = float(item.get('weight', 0))
                    if item.get('type', '').upper() in ['G', 'GOLD']:
                        summary['old_gold_weight'] += weight
                    elif item.get('type', '').upper() in ['S', 'SILVER']:
                        summary['old_silver_weight'] += weight
                    summary['old_amount'] += float(item.get('amount', 0))
                
                # Payment totals
                summary['cash_total'] += float(transaction.get('cash_amount', 0))
                summary['card_total'] += float(transaction.get('card_amount', 0))
                summary['upi_total'] += float(transaction.get('upi_amount', 0))
            
            print(f"[ViewModel] Daily summary calculated: {summary}")
            return summary
            
        except Exception as e:
            print(f"[ViewModel] Error getting daily summary: {e}")
            return {
                'new_gold_weight': 0,
                'new_silver_weight': 0,
                'new_amount': 0,
                'old_gold_weight': 0,
                'old_silver_weight': 0,
                'old_amount': 0,
                'cash_total': 0,
                'card_total': 0,
                'upi_total': 0
            }

    def clear_transaction(self):
        """Clear the current transaction."""
        self.current_transaction = {
            'new_items': [],
            'old_items': [],
            'comments': ''
        }
        
    def get_total_amount(self) -> float:
        """Get total amount of current transaction."""
        new_total = sum(item['amount'] for item in self.current_transaction['new_items'])
        old_total = sum(item['amount'] for item in self.current_transaction['old_items'])
        return new_total + old_total
        
    def get_current_transaction_summary(self):
        """Get summary of current transaction."""
        try:
            new_items = self.current_transaction.get('new_items', [])
            old_items = self.current_transaction.get('old_items', [])
            
            # Calculate new items totals
            new_gold_weight = sum(float(item['weight']) for item in new_items 
                                if item.get('type', '').upper() == 'G')
            new_silver_weight = sum(float(item['weight']) for item in new_items 
                                  if item.get('type', '').upper() == 'S')
            new_amount = sum(float(item['amount']) for item in new_items)
            
            # Calculate old items totals
            old_gold_weight = sum(float(item['weight']) for item in old_items 
                                if item.get('type', '').upper() == 'G')
            old_silver_weight = sum(float(item['weight']) for item in old_items 
                                  if item.get('type', '').upper() == 'S')
            old_amount = sum(float(item['amount']) for item in old_items)
            
            print(f"[ViewModel] Current transaction summary:")
            print(f"New items: {new_items}")
            print(f"Old items: {old_items}")
            print(f"New gold weight: {new_gold_weight}")
            print(f"New silver weight: {new_silver_weight}")
            print(f"Old gold weight: {old_gold_weight}")
            print(f"Old silver weight: {old_silver_weight}")
            
            return {
                'new_items_count': len(new_items),
                'new_gold_weight': new_gold_weight,
                'new_silver_weight': new_silver_weight,
                'new_amount': new_amount,
                'old_items_count': len(old_items),
                'old_gold_weight': old_gold_weight,
                'old_silver_weight': old_silver_weight,
                'old_amount': old_amount,
                'total_amount': new_amount + old_amount
            }
        except Exception as e:
            print(f"[ViewModel] Error getting transaction summary: {e}")
            return {
                'new_items_count': 0,
                'new_gold_weight': 0,
                'new_silver_weight': 0,
                'new_amount': 0,
                'old_items_count': 0,
                'old_gold_weight': 0,
                'old_silver_weight': 0,
                'old_amount': 0,
                'total_amount': 0
            }
        
    def get_billable_items(self, date):
        """
        Get billable and non-billable items for a specific date, grouped by item code.
        Returns a dictionary with 'billable' and 'non_billable' keys, each containing
        grouped items with their totals.
        """
        try:
            # Initialize result dictionaries
            billable_items = {}
            non_billable_items = {}
            
            # Get transactions for the date
            transactions = self.get_transactions(date, date)
            
            # Process each transaction
            for transaction in transactions:
                # Process new items
                for item in transaction.get('new_items', []):
                    # Get item details
                    item_code = item.get('code', '')
                    weight = float(item.get('weight', 0))
                    amount = float(item.get('amount', 0))
                    is_billable = item.get('is_billable', False)
                    
                    # Choose target dictionary based on billable status
                    target_dict = billable_items if is_billable else non_billable_items
                    
                    # Add or update item in the appropriate dictionary
                    if item_code not in target_dict:
                        target_dict[item_code] = {
                            'total_weight': 0,
                            'total_amount': 0,
                            'transactions': []
                        }
                    
                    # Update totals
                    target_dict[item_code]['total_weight'] += weight
                    target_dict[item_code]['total_amount'] += amount
                    
                    # Add transaction details
                    target_dict[item_code]['transactions'].append({
                        'date': transaction.get('date', ''),
                        'time': transaction.get('time', ''),
                        'weight': weight,
                        'amount': amount,
                        'comments': transaction.get('comments', '')
                    })
            
            return {
                'billable': billable_items,
                'non_billable': non_billable_items
            }
            
        except Exception as e:
            print(f"Error getting billable items: {e}")
            return {
                'billable': {},
                'non_billable': {}
            }

    def get_date_range_summary(self, from_date, to_date):
        """Get summary of transactions between from_date and to_date inclusive."""
        try:
            transactions = self.get_transactions_range(from_date, to_date)
            
            summary = {
                'new_gold_weight': 0,
                'new_silver_weight': 0,
                'new_amount': 0,
                'old_gold_weight': 0,
                'old_silver_weight': 0,
                'old_amount': 0,
                'cash_total': 0,
                'card_total': 0,
                'upi_total': 0
            }
            
            for transaction in transactions:
                # Process new items
                for item in transaction.get('new_items', []):
                    if 'Gold' in item.get('name', ''):
                        summary['new_gold_weight'] += item.get('weight', 0)
                    elif 'Silver' in item.get('name', ''):
                        summary['new_silver_weight'] += item.get('weight', 0)
                    summary['new_amount'] += item.get('amount', 0)
                
                # Process old items
                for item in transaction.get('old_items', []):
                    item_type = item.get('type', '').upper()
                    if item_type in ['G', 'GOLD']:
                        summary['old_gold_weight'] += item.get('weight', 0)
                    elif item_type in ['S', 'SILVER']:
                        summary['old_silver_weight'] += item.get('weight', 0)
                    summary['old_amount'] += item.get('amount', 0)
                
                # Process payments
                summary['cash_total'] += transaction.get('cash_amount', 0)
                summary['card_total'] += transaction.get('card_amount', 0)
                summary['upi_total'] += transaction.get('upi_amount', 0)
            
            return summary
        except Exception as e:
            print(f"Error getting summary for date range: {e}")
            return {}

    def get_billable_items_range(self, from_date, to_date):
        """Get billable and non-billable items summary for a date range."""
        try:
            transactions = self.get_transactions_range(from_date, to_date)
            
            billable_items = {}
            non_billable_items = {}
            
            for transaction in transactions:
                for item in transaction.get('new_items', []):
                    item_code = item.get('code', '')
                    item_name = item.get('name', '')
                    item_weight = item.get('weight', 0)
                    item_amount = item.get('amount', 0)
                    is_billable = item.get('is_billable', False)
                    
                    target_dict = billable_items if is_billable else non_billable_items
                    
                    if item_code not in target_dict:
                        target_dict[item_code] = {
                            'name': item_name,
                            'total_weight': 0,
                            'total_amount': 0,
                            'items': []
                        }
                    
                    target_dict[item_code]['total_weight'] += item_weight
                    target_dict[item_code]['total_amount'] += item_amount
                    target_dict[item_code]['items'].append({
                        'weight': item_weight,
                        'amount': item_amount
                    })
            
            return {
                'billable': billable_items,
                'non_billable': non_billable_items
            }
        except Exception as e:
            print(f"Error getting billable items for date range: {e}")
            return {} 