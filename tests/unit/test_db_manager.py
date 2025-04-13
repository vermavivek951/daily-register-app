import pytest
from datetime import datetime
from src.database.db_manager import DatabaseManager

def test_init_db(test_db):
    """Test database initialization."""
    assert test_db is not None
    # Verify tables exist
    cursor = test_db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    assert 'transactions' in table_names
    assert 'items' in table_names
    assert 'old_items' in table_names

def test_add_transaction(test_db, sample_transaction):
    """Test adding a transaction."""
    transaction_id = test_db.add_transaction(sample_transaction)
    assert transaction_id is not None
    
    # Verify transaction was added
    cursor = test_db.conn.cursor()
    cursor.execute("SELECT id, date, timestamp, comments, total_amount, net_amount_paid, cash_amount, card_amount, upi_amount FROM transactions WHERE id=?", (transaction_id,))
    transaction = cursor.fetchone()
    assert transaction is not None
    assert transaction[3] == sample_transaction['comments']

def test_get_transactions_by_date(test_db, sample_transaction):
    """Test retrieving transactions by date."""
    # Add a transaction
    test_db.add_transaction(sample_transaction)
    
    # Get transactions for today
    today = datetime.now().date()
    transactions = test_db.get_transactions_by_date(today)
    assert len(transactions) > 0
    
    # Verify transaction details
    transaction = transactions[0]
    assert transaction['comments'] == sample_transaction['comments']
    assert len(transaction['new_items']) == len(sample_transaction['new_items'])
    assert len(transaction['old_items']) == len(sample_transaction['old_items'])

def test_delete_transaction(test_db, sample_transaction):
    """Test deleting a transaction."""
    # Add a transaction
    transaction_id = test_db.add_transaction(sample_transaction)
    
    # Delete the transaction
    test_db.delete_transaction(transaction_id)
    
    # Verify transaction was deleted
    cursor = test_db.conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
    transaction = cursor.fetchone()
    assert transaction is None

def test_update_transaction(test_db, sample_transaction):
    """Test updating a transaction."""
    # Add a transaction
    transaction_id = test_db.add_transaction(sample_transaction)
    
    # Modify the transaction
    updated_transaction = sample_transaction.copy()
    updated_transaction['comments'] = 'Updated test transaction'
    
    # Update the transaction
    test_db.update_transaction(transaction_id, updated_transaction)
    
    # Verify transaction was updated
    cursor = test_db.conn.cursor()
    cursor.execute("SELECT id, date, timestamp, comments, total_amount, net_amount_paid, cash_amount, card_amount, upi_amount FROM transactions WHERE id=?", (transaction_id,))
    transaction = cursor.fetchone()
    assert transaction is not None
    assert transaction[3] == 'Updated test transaction'

def test_get_transaction_summary(test_db, sample_transaction):
    """Test getting transaction summary."""
    # Add a transaction
    test_db.add_transaction(sample_transaction)
    
    # Get summary for today
    today = datetime.now().date()
    summary = test_db.get_transaction_summary(today)
    
    assert summary is not None
    assert 'total_amount' in summary
    assert 'total_weight' in summary
    assert summary['total_amount'] == sample_transaction['new_items'][0]['amount'] + sample_transaction['old_items'][0]['amount']
    assert summary['total_weight'] == sample_transaction['new_items'][0]['weight'] + sample_transaction['old_items'][0]['weight'] 