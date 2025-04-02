from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class OldItem:
    id: Optional[int] = None
    transaction_id: Optional[int] = None
    item_type: str = "Gold"
    weight: float = 0.0
    amount: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OldItem':
        return cls(
            id=data.get('id'),
            transaction_id=data.get('transaction_id'),
            item_type=data.get('item_type', "Gold"),
            weight=float(data.get('weight', 0)),
            amount=float(data.get('amount', 0))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'item_type': self.item_type,
            'weight': self.weight,
            'amount': self.amount
        }

@dataclass
class Item:
    id: Optional[int] = None
    transaction_id: Optional[int] = None
    item_name: str = ""
    item_type: str = "Gold"
    is_billable: bool = True
    weight: float = 0.0
    amount: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        return cls(
            id=data.get('id'),
            transaction_id=data.get('transaction_id'),
            item_name=data.get('item_name', ""),
            item_type=data.get('item_type', "Gold"),
            is_billable=bool(data.get('is_billable', True)),
            weight=float(data.get('weight', 0)),
            amount=float(data.get('amount', 0))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'item_name': self.item_name,
            'item_type': self.item_type,
            'is_billable': self.is_billable,
            'weight': self.weight,
            'amount': self.amount
        }

@dataclass
class Transaction:
    id: Optional[int] = None
    date: str = ""
    total_amount: float = 0.0
    net_amount_paid: float = 0.0
    cash_amount: float = 0.0
    card_amount: float = 0.0
    upi_amount: float = 0.0
    comments: str = ""
    items: List[Item] = None
    old_items: List[OldItem] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.old_items is None:
            self.old_items = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        items = [Item.from_dict(item) for item in data.get('items', [])]
        old_items = [OldItem.from_dict(item) for item in data.get('old_items', [])]
        
        return cls(
            id=data.get('id'),
            date=data.get('date', ""),
            total_amount=float(data.get('total_amount', 0)),
            net_amount_paid=float(data.get('net_amount_paid', 0)),
            cash_amount=float(data.get('cash_amount', 0)),
            card_amount=float(data.get('card_amount', 0)),
            upi_amount=float(data.get('upi_amount', 0)),
            comments=data.get('comments', ""),
            items=items,
            old_items=old_items
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'date': self.date,
            'total_amount': self.total_amount,
            'net_amount_paid': self.net_amount_paid,
            'cash_amount': self.cash_amount,
            'card_amount': self.card_amount,
            'upi_amount': self.upi_amount,
            'comments': self.comments
        }

    def get_items_dict(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]

    def get_old_items_dict(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.old_items]

    def add_item(self, item: Item) -> None:
        self.items.append(item)
        self.update_total_amount()

    def remove_item(self, item: Item) -> None:
        if item in self.items:
            self.items.remove(item)
            self.update_total_amount()

    def update_item(self, item: Item) -> None:
        for i, existing_item in enumerate(self.items):
            if existing_item.id == item.id:
                self.items[i] = item
                self.update_total_amount()
                break

    def update_total_amount(self) -> None:
        self.total_amount = sum(item.amount for item in self.items)

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def get_item_by_name(self, item_name: str) -> Optional[Item]:
        for item in self.items:
            if item.item_name == item_name:
                return item
        return None

    def get_items_by_type(self, item_type: str) -> List[Item]:
        return [item for item in self.items if item.item_type == item_type]

    def get_items_by_billable(self, is_billable: bool) -> List[Item]:
        return [item for item in self.items if item.is_billable == is_billable]

    def get_items_by_criteria(self, **criteria) -> List[Item]:
        """
        Get items that match all the specified criteria.
        Example: get_items_by_criteria(item_type='Gold', is_billable=True)
        """
        return [
            item for item in self.items
            if all(getattr(item, key) == value for key, value in criteria.items())
        ] 