from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class NewItem:
    """Represents a new item in a transaction."""
    code: str
    name: str  # New field for item name
    weight: float
    amount: float
    is_billable: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class OldItem:
    """Represents an old item in a transaction."""
    type: str  # "G" or "S" for Gold/Silver
    name: str  # New field for item name
    weight: float
    amount: float
    timestamp: datetime = field(default_factory=datetime.now)

class Transaction:
    def __init__(self):
        self.new_items: List[Dict] = []
        self.old_items: List[Dict] = []
        self.payment_details: Dict = {'cash': 0, 'card': 0, 'upi': 0}
        self.timestamp: Optional[datetime] = None
        self.comments: str = ""  # New field for transaction comments
        
    def add_new_item(self, item: Dict) -> None:
        """Add a new item to the transaction."""
        if not item['code']:
            raise ValueError("Item code is required")
        if not item.get('name'):
            raise ValueError("Item name is required")
        if item['weight'] <= 0:
            raise ValueError("Weight must be greater than 0")
        if item['amount'] <= 0:
            raise ValueError("Amount must be greater than 0")
        self.new_items.append(item)
        
    def add_old_item(self, item: Dict) -> None:
        """Add an old item to the transaction."""
        if not item['type']:
            raise ValueError("Item type is required")
        if item['weight'] <= 0:
            raise ValueError("Weight must be greater than 0")
        if item['amount'] <= 0:
            raise ValueError("Amount must be greater than 0")
        self.old_items.append(item)
        
    def remove_new_item(self, index: int) -> None:
        """Remove a new item from the transaction."""
        if 0 <= index < len(self.new_items):
            self.new_items.pop(index)
            
    def remove_old_item(self, index: int) -> None:
        """Remove an old item from the transaction."""
        if 0 <= index < len(self.old_items):
            self.old_items.pop(index)
            
    def set_payment_details(self, details: Dict) -> None:
        """Set payment details for the transaction."""
        total = self.get_total_amount()
        payment_total = sum(details.values())
        
        # Allow partial payments
        if payment_total <= 0:
            raise ValueError("Payment amount must be greater than 0")
            
        if payment_total > total:
            raise ValueError(f"Payment amount ({payment_total:.2f}) cannot exceed total amount ({total:.2f})")
            
        # Ensure all payment values are non-negative
        if not all(amount >= 0 for amount in details.values()):
            raise ValueError("All payment amounts must be non-negative")
            
        self.payment_details = details
        
    def get_total_amount(self) -> float:
        """Calculate total amount of the transaction."""
        new_items_total = sum(item['amount'] for item in self.new_items)
        old_items_total = sum(item['amount'] for item in self.old_items)
        total = new_items_total - old_items_total
        return max(0, total)  # Return 0 if the total would be negative
        
    def get_summary(self) -> Dict:
        """Get a summary of the transaction."""
        # Calculate new items summary
        new_items_total = sum(item['amount'] for item in self.new_items)
        new_gold = sum(item['weight'] for item in self.new_items if item['type'] == 'G' or item['type'] == 'Gold')
        new_silver = sum(item['weight'] for item in self.new_items if item['type'] == 'S' or item['type'] == 'Silver')
        
        # Calculate old items summary
        old_items_total = sum(item['amount'] for item in self.old_items)
        old_gold = sum(item['weight'] for item in self.old_items if item['type'] == 'Gold')
        old_silver = sum(item['weight'] for item in self.old_items if item['type'] == 'Silver')
        
        # Calculate billable items summary
        billable_items = [item for item in self.new_items if item.get('is_billable', False)]
        billable_gold = sum(item['weight'] for item in billable_items if item['code'].startswith('G'))
        billable_silver = sum(item['weight'] for item in billable_items if item['code'].startswith('S'))
        billable_total = sum(item['amount'] for item in billable_items)
        
        # Calculate total to pay (never negative)
        total_to_pay = max(0, new_items_total - old_items_total)
        
        return {
            # Transaction Summary
            'new_items_count': len(self.new_items),
            'new_items_total': new_items_total,
            'old_items_count': len(self.old_items),
            'old_items_total': old_items_total,
            'total_to_pay': total_to_pay,
            
            # Daily Summary
            'new_items': {
                'gold': new_gold,
                'silver': new_silver
            },
            'old_items': {
                'gold': old_gold,
                'silver': old_silver
            },
            'billable_items': {
                'gold': billable_gold,
                'silver': billable_silver,
                'amount': billable_total
            },
            'payments': self.payment_details.copy()
        }
        
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary for storage."""
        return {
            'new_items': self.new_items,
            'old_items': self.old_items,
            'payment_details': self.payment_details,
            'timestamp': self.timestamp,
            'comments': self.comments  # Include comments in dictionary
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """Create transaction from dictionary."""
        transaction = cls()
        transaction.new_items = data.get('new_items', [])
        transaction.old_items = data.get('old_items', [])
        transaction.payment_details = data.get('payment_details', {})
        transaction.timestamp = data.get('timestamp')
        transaction.comments = data.get('comments', '')  # Load comments from dictionary
        return transaction 