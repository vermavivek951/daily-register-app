"""Validation utilities for the application."""
from decimal import Decimal
from typing import Optional, Union

def is_valid_float(value: Union[str, float]) -> bool:
    """Check if a value can be converted to a valid float."""
    try:
        float_val = float(value)
        return float_val >= 0
    except (ValueError, TypeError):
        return False

def is_valid_item_code(code: str) -> bool:
    """Check if an item code is valid (exists in predefined list)."""
    if not code:
        return False
    from services.item_service import ItemService
    item_service = ItemService()
    return code.upper() in item_service.ITEM_CODES

def is_valid_item_type(type_str: str) -> bool:
    """Check if an item type is valid (G, S, or O)."""
    if not type_str:
        return False
    return type_str.upper() in ('G', 'S', 'O')

def parse_amount(amount_str: Union[str, float, int]) -> Optional[float]:
    """Parse and validate an amount value."""
    try:
        amount = float(amount_str)
        return amount if amount >= 0 else None
    except (ValueError, TypeError):
        return None

def parse_weight(weight_str: Union[str, float, int]) -> Optional[float]:
    """Parse and validate a weight value."""
    try:
        weight = float(weight_str)
        return weight if weight >= 0 else None
    except (ValueError, TypeError):
        return None

def validate_payment_amounts(**payments) -> bool:
    """Validate payment amounts."""
    try:
        # Convert all amounts to Decimal for precise comparison
        amounts = [Decimal(str(amount)) for amount in payments.values()]
        return all(amount >= 0 for amount in amounts)
    except (ValueError, TypeError, decimal.InvalidOperation):
        return False 