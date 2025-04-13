from typing import Dict, List, Optional
import sqlite3
from pathlib import Path
from datetime import datetime
from database.db_manager import DatabaseManager

class ItemService:
    def __init__(self, db: Optional[DatabaseManager] = None):
        """Initialize the item service.
        
        Args:
            db: Optional database manager instance. If not provided, a new one will be created.
        """
        self.db = db if db is not None else DatabaseManager()
        self.db_path = Path('database/items.db')
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Predefined item codes
        self.ITEM_CODES = {
            # Gold Items
            'GCH': {'name': 'Gold Chain', 'type': 'G'},
            'GBG': {'name': 'Gold Bangle', 'type': 'G'},
            'GRIN': {'name': 'Gold Ring', 'type': 'G'},
            'GER': {'name': 'Gold Earring', 'type': 'G'},
            'GBT': {'name': 'Gold Bracelet', 'type': 'G'},
            'GNK': {'name': 'Gold Necklace', 'type': 'G'},
            'GPD': {'name': 'Gold Pendant', 'type': 'G'},
            'GAN': {'name': 'Gold Anklet', 'type': 'G'},
            'GMG': {'name': 'Gold Mangalsutra', 'type': 'G'},
            'GNT': {'name': 'Gold Nath', 'type': 'G'},
            'GTK': {'name': 'Gold Tikka', 'type': 'G'},
            'GTC': {'name': 'Gold Toe Chain', 'type': 'G'},
            'GLOC': {'name': 'Gold Locket', 'type': 'G'},
            'GBALI': {'name': 'Gold Bali', 'type': 'G'},
            'NP': {'name': 'Gold Nose Pin', 'type': 'G'},
            
            # Silver Items
            'SCH': {'name': 'Silver Chain', 'type': 'S'},
            'SBG': {'name': 'Silver Bangle', 'type': 'S'},
            'SRG': {'name': 'Silver Ring', 'type': 'S'},
            'SER': {'name': 'Silver Earring', 'type': 'S'},
            'SBR': {'name': 'Silver Bracelet', 'type': 'S'},
            'SNK': {'name': 'Silver Necklace', 'type': 'S'},
            'SPD': {'name': 'Silver Pendant', 'type': 'S'},
            'SAN': {'name': 'Silver Anklet', 'type': 'S'},
            'SPA': {'name': 'Silver Payal', 'type': 'S'},
            'STK': {'name': 'Silver Tikka', 'type': 'S'},
            'STC': {'name': 'Silver Toe Chain', 'type': 'S'}
        }
        
        self.init_db()
        
        # Cache for quick lookups
        self._items_cache: Dict[str, dict] = {}
        self._load_cache()
        
    def init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,  -- 'G' or 'S'
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert predefined items if they don't exist
            for code, info in self.ITEM_CODES.items():
                cursor.execute('''
                    INSERT OR IGNORE INTO items (code, name, type)
                    VALUES (?, ?, ?)
                ''', (code, info['name'], info['type']))
            
            conn.commit()
            
    def _load_cache(self):
        """Load items into cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT code, name, type, last_used FROM items')
            for code, name, type_, last_used in cursor.fetchall():
                self._items_cache[code] = {
                    'name': name,
                    'type': type_,
                    'last_used': last_used
                }
                
    def get_item_details(self, code: str) -> Optional[dict]:
        """Get item details from cache."""
        if not code or code not in self._items_cache:
            return None
            
        item = self._items_cache[code].copy()
        if item['type'] not in ['G', 'S']:  # Gold or Silver
            return None
            
        return item
        
    def add_item(self, code: str, name: str, type_: str) -> bool:
        """Add a new item or update existing one."""
        try:
            if not code or not name or not type_:
                return False
                
            if type_ not in ['G', 'S']:  # Gold or Silver
                # Remove from cache if exists with invalid type
                if code in self._items_cache:
                    del self._items_cache[code]
                return False
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO items (code, name, type, last_used)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (code, name, type_))
                conn.commit()
                
            # Update cache
            self._items_cache[code] = {
                'code': code,
                'name': name,
                'type': type_,
                'last_used': datetime.now().isoformat()
            }
            return True
        except Exception as e:
            print(f"Error adding item: {e}")
            return False
            
    def get_suggestions(self, prefix: str) -> List[Dict]:
        """Get item suggestions based on code prefix."""
        suggestions = []
        prefix = prefix.lower()
        
        # First try exact matches
        for code, details in self._items_cache.items():
            if code.lower() == prefix:
                suggestions.append({
                    'code': code,
                    'name': details['name'],
                    'type': details['type'],
                    'last_used': details.get('last_used', '')
                })
                
        # Then try prefix matches
        for code, details in self._items_cache.items():
            if code.lower().startswith(prefix) and code.lower() != prefix:
                suggestions.append({
                    'code': code,
                    'name': details['name'],
                    'type': details['type'],
                    'last_used': details.get('last_used', '')
                })
                
        # Sort by last used (most recent first), with empty strings for None values
        return sorted(suggestions, key=lambda x: x.get('last_used', '') or '', reverse=True)
        
    def update_last_used(self, code: str) -> bool:
        """Update last used timestamp for an item."""
        try:
            if not code or code not in self._items_cache:
                return False
                
            current_time = datetime.now().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE items
                    SET last_used = ?
                    WHERE code = ?
                ''', (current_time, code))
                conn.commit()
                
            # Update cache
            self._items_cache[code]['last_used'] = current_time
            return True
        except Exception as e:
            print(f"Error updating last used: {e}")
            return False
            
    def get_recent_items(self, limit: int = 10) -> List[Dict]:
        """Get recently used items."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT code, name, type, last_used
                    FROM items
                    ORDER BY last_used DESC
                    LIMIT ?
                ''', (limit,))
                return [
                    {
                        'code': code,
                        'name': name,
                        'type': type_,
                        'last_used': last_used
                    }
                    for code, name, type_, last_used in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error getting recent items: {e}")
            return [] 