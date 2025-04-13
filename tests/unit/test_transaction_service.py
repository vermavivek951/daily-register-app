import pytest
from datetime import datetime, timedelta
from src.services.transaction_service import TransactionService

def test_add_new_item(transaction_service, sample_item):
    """Test adding a new item to the current transaction."""
    result = transaction_service.add_new_item(
        sample_item['code'],
        sample_item['weight'],
        sample_item['amount'],
        sample_item['is_billable']
    )
    assert result is True
    
    # Verify item was added to current transaction
    current_transaction = transaction_service.get_current_transaction()
    assert len(current_transaction['new_items']) == 1
    assert current_transaction['new_items'][0]['code'] == sample_item['code']
    assert current_transaction['new_items'][0]['weight'] == sample_item['weight']
    assert current_transaction['new_items'][0]['amount'] == sample_item['amount']

def test_add_old_item(transaction_service):
    """Test adding an old item to the current transaction."""
    result = transaction_service.add_old_item('G', 5.0, 25000.0)
    assert result is True
    
    # Verify item was added to current transaction
    current_transaction = transaction_service.get_current_transaction()
    assert len(current_transaction['old_items']) == 1
    assert current_transaction['old_items'][0]['type'] == 'G'
    assert current_transaction['old_items'][0]['weight'] == 5.0
    assert current_transaction['old_items'][0]['amount'] == 25000.0

def test_save_transaction(transaction_service, sample_transaction):
    """Test saving a transaction."""
    # Add items to current transaction
    for item in sample_transaction['new_items']:
        transaction_service.add_new_item(
            item['code'],
            item['weight'],
            item['amount'],
            item['is_billable']
        )
    
    for item in sample_transaction['old_items']:
        transaction_service.add_old_item(
            item['type'],
            item['weight'],
            item['amount']
        )
    
    # Save transaction
    result = transaction_service.save_transaction(
        sample_transaction['payment_details'],
        sample_transaction['comments']
    )
    assert result is True
    
    # Verify transaction was saved
    today = datetime.now().date()
    transactions = transaction_service.get_transactions(today, today)
    assert len(transactions) == 1
    assert transactions[0]['comments'] == sample_transaction['comments']

def test_get_transactions(transaction_service, sample_transaction):
    """Test retrieving transactions within a date range."""
    # Add and save a transaction
    for item in sample_transaction['new_items']:
        transaction_service.add_new_item(
            item['code'],
            item['weight'],
            item['amount'],
            item['is_billable']
        )
    
    for item in sample_transaction['old_items']:
        transaction_service.add_old_item(
            item['type'],
            item['weight'],
            item['amount']
        )
    
    transaction_service.save_transaction(
        sample_transaction['payment_details'],
        sample_transaction['comments']
    )
    
    # Get transactions for today
    today = datetime.now().date()
    transactions = transaction_service.get_transactions(today, today)
    assert len(transactions) == 1
    assert transactions[0]['comments'] == sample_transaction['comments']

def test_clear_current_transaction(transaction_service, sample_transaction):
    """Test clearing the current transaction."""
    # Add items to current transaction
    for item in sample_transaction['new_items']:
        transaction_service.add_new_item(
            item['code'],
            item['weight'],
            item['amount'],
            item['is_billable']
        )
    
    for item in sample_transaction['old_items']:
        transaction_service.add_old_item(
            item['type'],
            item['weight'],
            item['amount']
        )
    
    # Set comments
    transaction_service.set_comments(sample_transaction['comments'])
    
    # Clear current transaction
    transaction_service.clear_current_transaction()
    
    # Verify current transaction is empty
    current_transaction = transaction_service.get_current_transaction()
    assert len(current_transaction['new_items']) == 0
    assert len(current_transaction['old_items']) == 0
    assert current_transaction['comments'] == '' 