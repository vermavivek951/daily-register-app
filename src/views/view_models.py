from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal
from models.transaction import Transaction, NewItem, OldItem
from controllers.transaction_controller import TransactionController
from utils.validation import (
    is_valid_float, is_valid_item_code, is_valid_item_type,
    parse_amount, parse_weight, validate_payment_amounts
)

class TransactionViewModel:
    """View model for handling transaction-related UI logic"""
    def __init__(self, transaction_controller):
        """Initialize the view model with a transaction controller."""
        self.transaction_controller = transaction_controller
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
                'mark_bill': bool(item.get('mark_bill', False))
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

    def save_transaction(self, payment_details):
        """Save the current transaction with payment details."""
        try:
            # Add payment details to current transaction
            self.current_transaction.update({
                'timestamp': datetime.now(),  # Use current date and time
                'comments': payment_details.get('comments', ''),
                'cash_amount': float(payment_details.get('cash_amount', 0)),
                'card_amount': float(payment_details.get('card_amount', 0)),
                'upi_amount': float(payment_details.get('upi_amount', 0))
            })
            
            print(f"[ViewModel] Saving transaction: {self.current_transaction}")
            
            # Save using controller
            if self.transaction_controller.save_transaction(self.current_transaction):
                # Clear current transaction after successful save
                self.clear_transaction()
                return True
            return False
            
        except Exception as e:
            print(f"[ViewModel] Error saving transaction: {e}")
            return False

    def delete_transaction(self, transaction):
        """Delete a transaction."""
        try:
            return self.transaction_controller.delete_transaction(transaction)
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False

    def get_transactions(self, date):
        """Get transactions for a specific date."""
        try:
            print(f"[ViewModel] Getting transactions for date: {date}")
            transactions = self.transaction_controller.get_transactions_by_date(date)
            print(f"[ViewModel] Retrieved {len(transactions)} transactions")
            return transactions
        except Exception as e:
            print(f"[ViewModel] Error getting transactions: {e}")
            return []

    def get_daily_summary(self, date):
        """Get summary for a specific date."""
        try:
            transactions = self.get_transactions(date)
            
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
        
    def format_transaction_for_display(self, transaction: dict) -> List[str]:
        """Format a transaction for display in the register table."""
        try:
            # Get timestamp
            timestamp = transaction['timestamp']
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.now()  # Fallback to current time if invalid
            time_str = timestamp.strftime('%H:%M:%S')
            
            # Get first new item (if any)
            new_items = transaction.get('new_items', [])
            if new_items:
                new_item = new_items[0]
                code = new_item.get('code', '')
                weight = f"{new_item.get('weight', 0):.3f}"
                amount = f"{new_item.get('amount', 0):.2f}"
                mark_bill = 'B' if new_item.get('mark_bill') else ''
            else:
                code = weight = amount = mark_bill = ''
                
            # Get first old item (if any)
            old_items = transaction.get('old_items', [])
            if old_items:
                old_item = old_items[0]
                old_type = old_item.get('type', '')
                old_weight = f"{old_item.get('weight', 0):.3f}"
                old_amount = f"{old_item.get('amount', 0):.2f}"
            else:
                old_type = old_weight = old_amount = ''
                
            return [
                time_str,      # Time
                code,          # Code
                weight,        # Weight
                amount,        # Amount
                mark_bill,     # Mark Bill
                old_type,      # Old Type
                old_weight,    # Old Weight
                old_amount     # Old Amount
            ]
            
        except Exception as e:
            print(f"Error formatting transaction: {e}")
            return [''] * 8 