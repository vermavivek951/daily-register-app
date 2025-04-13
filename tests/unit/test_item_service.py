import pytest
from src.services.item_service import ItemService

def test_add_item(item_service, sample_item):
    """Test adding a new item."""
    result = item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    assert result is True
    
    # Verify item was added
    item_details = item_service.get_item_details(sample_item['code'])
    assert item_details is not None
    assert item_details['code'] == sample_item['code']
    assert item_details['name'] == sample_item['name']
    assert item_details['type'] == sample_item['type']

def test_get_item_details(item_service, sample_item):
    """Test retrieving item details."""
    # Add an item first
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Get item details
    item_details = item_service.get_item_details(sample_item['code'])
    assert item_details is not None
    assert item_details['code'] == sample_item['code']
    assert item_details['name'] == sample_item['name']
    assert item_details['type'] == sample_item['type']

def test_get_suggestions(item_service, sample_item):
    """Test getting item suggestions."""
    # Add an item first
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Get suggestions
    suggestions = item_service.get_suggestions(sample_item['code'][:2])
    assert len(suggestions) > 0
    assert any(s['code'] == sample_item['code'] for s in suggestions)

def test_update_last_used(item_service, sample_item):
    """Test updating last used timestamp."""
    # Add an item first
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Update last used
    result = item_service.update_last_used(sample_item['code'])
    assert result is True
    
    # Verify last used was updated
    item_details = item_service.get_item_details(sample_item['code'])
    assert item_details['last_used'] is not None

def test_get_recent_items(item_service, sample_item):
    """Test getting recent items."""
    # Add an item first
    item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        sample_item['type']
    )
    
    # Update last used to make it recent
    item_service.update_last_used(sample_item['code'])
    
    # Get recent items
    recent_items = item_service.get_recent_items(limit=5)
    assert len(recent_items) > 0
    assert any(item['code'] == sample_item['code'] for item in recent_items)

def test_invalid_item_code(item_service):
    """Test handling invalid item code."""
    result = item_service.add_item('', 'Invalid Item', 'G')
    assert result is False
    
    item_details = item_service.get_item_details('')
    assert item_details is None

def test_invalid_item_type(item_service, sample_item):
    """Test handling invalid item type."""
    result = item_service.add_item(
        sample_item['code'],
        sample_item['name'],
        'X'  # Invalid type
    )
    assert result is False
    
    item_details = item_service.get_item_details(sample_item['code'])
    assert item_details is None 