import pytest
import os
import sqlite3
from datetime import datetime
from src.database.db_manager import DatabaseManager
from src.controllers.transaction_controller import TransactionController
from src.services.item_service import ItemService
from src.services.transaction_service import TransactionService

@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    db_path = "test_transactions.db"
    db = DatabaseManager(db_path)
    yield db
    # Cleanup after tests
    db.close()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            print(f"Warning: Could not remove test database file: {db_path}")

@pytest.fixture
def transaction_controller(test_db):
    """Create a transaction controller with test database."""
    return TransactionController(test_db)

@pytest.fixture
def item_service(test_db):
    """Create an item service with test database."""
    return ItemService(test_db)

@pytest.fixture
def transaction_service(test_db):
    """Create a transaction service with test database."""
    return TransactionService(test_db)

@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing."""
    return {
        'new_items': [
            {
                'code': 'GCH',
                'name': 'Gold Chain',
                'type': 'G',
                'weight': 10.5,
                'amount': 50000.0,
                'is_billable': True
            }
        ],
        'old_items': [
            {
                'type': 'G',
                'weight': 5.0,
                'amount': 25000.0
            }
        ],
        'payment_details': {
            'cash': 20000.0,
            'card': 5000.0,
            'upi': 0.0
        },
        'timestamp': datetime.now(),
        'comments': 'Test transaction'
    }

@pytest.fixture
def sample_item():
    """Create a sample item for testing."""
    return {
        'code': 'GCH',
        'name': 'Gold Chain',
        'type': 'G',
        'weight': 10.5,
        'amount': 50000.0,
        'is_billable': True
    } 