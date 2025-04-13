import pytest
from datetime import datetime
from src.services.transaction_service import TransactionService
from src.services.item_service import ItemService

def test_transaction_with_items(transaction_service, item_service, sample_item):
    """Test creating a transaction with items."""
    # First, add the item to the item service
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Add the item to a transaction
    transaction_service.add_new_item(
        sample_item['code'],
        sample_item['weight'],
        sample_item['amount'],
        sample_item['is_billable']
    )
    
    # Add an old item
    transaction_service.add_old_item('G', 5.0, 25000.0)
    
    # Save the transaction
    payment_details = {
        'cash': 20000.0,
        'card': 5000.0,
        'upi': 0.0
    }
    result = transaction_service.save_transaction(payment_details)
    assert result is True
    
    # Verify the transaction was saved
    today = datetime.now().date()
    transactions = transaction_service.get_transactions(today, today)
    assert len(transactions) == 1
    assert len(transactions[0]['new_items']) == 1
    assert len(transactions[0]['old_items']) == 1
    
    # Verify the item's last used timestamp was updated
    item_details = item_service.get_item_details(sample_item['code'])
    assert item_details['last_used'] is not None

def test_transaction_validation(transaction_service, item_service, sample_item):
    """Test transaction validation with items."""
    # Add the item to the item service
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Try to add an invalid item code
    result = transaction_service.add_new_item(
        'INVALID',
        sample_item['weight'],
        sample_item['amount'],
        sample_item['is_billable']
    )
    assert result is False
    
    # Try to add an invalid old item type
    result = transaction_service.add_old_item('X', 5.0, 25000.0)
    assert result is False
    
    # Add valid items
    transaction_service.add_new_item(
        sample_item['code'],
        sample_item['weight'],
        sample_item['amount'],
        sample_item['is_billable']
    )
    transaction_service.add_old_item('G', 5.0, 25000.0)
    
    # Try to save with invalid payment details
    invalid_payment = {
        'cash': -1000.0,  # Invalid negative amount
        'card': 0.0,
        'upi': 0.0
    }
    result = transaction_service.save_transaction(invalid_payment)
    assert result is False

def test_transaction_retrieval(transaction_service, item_service, sample_item):
    """Test retrieving transactions with item details."""
    # Add the item to the item service
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Create and save a transaction
    transaction_service.add_new_item(
        sample_item['code'],
        sample_item['weight'],
        sample_item['amount'],
        sample_item['is_billable']
    )
    transaction_service.add_old_item('G', 5.0, 25000.0)
    
    payment_details = {
        'cash': 20000.0,
        'card': 5000.0,
        'upi': 0.0
    }
    transaction_service.save_transaction(payment_details)
    
    # Retrieve the transaction
    today = datetime.now().date()
    transactions = transaction_service.get_transactions(today, today)
    assert len(transactions) == 1
    
    # Verify item details in the transaction
    transaction = transactions[0]
    new_item = transaction['new_items'][0]
    assert new_item['code'] == sample_item['code']
    assert new_item['name'] == sample_item['name']
    assert new_item['type'] == sample_item['type']
    
    # Verify old item details
    old_item = transaction['old_items'][0]
    assert old_item['type'] == 'G'
    assert old_item['weight'] == 5.0
    assert old_item['amount'] == 25000.0

def test_transaction_deletion(transaction_service, item_service, sample_item):
    """Test deleting transactions and verifying item history."""
    # Add the item to the item service
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Create and save a transaction
    transaction_service.add_new_item(
        sample_item['code'],
        sample_item['weight'],
        sample_item['amount'],
        sample_item['is_billable']
    )
    
    payment_details = {
        'cash': 20000.0,
        'card': 5000.0,
        'upi': 0.0
    }
    transaction_service.save_transaction(payment_details)
    
    # Get the transaction ID
    today = datetime.now().date()
    transactions = transaction_service.get_transactions(today, today)
    transaction_id = transactions[0]['id']
    
    # Delete the transaction
    result = transaction_service.delete_transaction(transaction_id)
    assert result is True
    
    # Verify the transaction was deleted
    transactions = transaction_service.get_transactions(today, today)
    assert len(transactions) == 0
    
    # Verify the item still exists in the item service
    item_details = item_service.get_item_details(sample_item['code'])
    assert item_details is not None
    assert item_details['code'] == sample_item['code'] 