import os
import json
import copy
from datetime import datetime

# Constants
TRANSACTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'transactions.json')

class MainWindowViewModel:
    def __init__(self):
        """Initialize the view model."""
        self.transactions = []
        self.load_transactions()
        
    def add_transaction(self, transaction):
        """Add a new transaction."""
        try:
            # Add timestamp to transaction
            transaction['timestamp'] = datetime.now()
            
            # Save transaction to file
            self.transactions.append(transaction)
            self.save_transactions()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
            
    def delete_transaction(self, transaction_to_delete):
        """Delete a transaction."""
        try:
            # Find and remove the transaction
            self.transactions = [t for t in self.transactions 
                               if t.get('timestamp') != transaction_to_delete.get('timestamp')]
            
            # Save updated transactions
            self.save_transactions()
            return True
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
            
    def load_transactions(self):
        """Load transactions from file."""
        try:
            if os.path.exists(TRANSACTIONS_FILE):
                with open(TRANSACTIONS_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert timestamp strings back to datetime objects
                    for transaction in data:
                        if 'timestamp' in transaction:
                            transaction['timestamp'] = datetime.fromisoformat(transaction['timestamp'])
                    self.transactions = data
        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.transactions = []
            
    def save_transactions(self):
        """Save transactions to file."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(TRANSACTIONS_FILE), exist_ok=True)
            
            # Convert datetime objects to ISO format strings for JSON serialization
            data = copy.deepcopy(self.transactions)
            for transaction in data:
                if 'timestamp' in transaction:
                    transaction['timestamp'] = transaction['timestamp'].isoformat()
                    
            with open(TRANSACTIONS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving transactions: {e}")
            
    def get_transactions(self):
        """Get all transactions."""
        return self.transactions 