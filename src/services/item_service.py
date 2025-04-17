from typing import Dict, List, Optional
from datetime import datetime
import os
from database.db_manager import DatabaseManager
import sqlite3

class ItemService:
    def __init__(self, db: Optional[DatabaseManager] = None):
        """Initialize the item service.
        
        Args:
            db: Optional database manager instance. If not provided, a new one will be created.
        """
        # Get the database path from environment or use default
        app_data_dir = os.path.join(os.getenv('APPDATA', ''), 'DailyRegister')
        os.makedirs(app_data_dir, exist_ok=True)
        db_path = os.path.join(app_data_dir, 'transactions.db')
        
        # Use the provided db manager or create a new one with the correct path
        self.db = db if db is not None else DatabaseManager(db_path)
        
        # Initialize database and load item codes
        self.init_db()
        
        # Cache for quick lookups
        self._items_cache: Dict[str, dict] = {}
        self._load_cache()
        
    def init_db(self):
        """Initialize the database with required tables."""
        try:
            if not self.db.conn:
                self.db.conn = sqlite3.connect(self.db.db_path)
            cursor = self.db.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS item_codes (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,  -- 'G' or 'S' or 'O'
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default items if the table is empty
            cursor.execute('SELECT COUNT(*) FROM item_codes')
            if cursor.fetchone()[0] == 0:
                default_items = {
                    # Other Items
                    'BARTAN': {'name': 'Bartan', 'type': 'O'},
                    'POOJA': {'name': 'Pooja', 'type': 'O'},
                    'MURTI': {'name': 'Murti', 'type': 'O'},
                    'MIX': {'name': 'Mixed Items', 'type': 'O'}
                }
                
                for code, info in default_items.items():
                    cursor.execute('''
                        INSERT INTO item_codes (code, name, type)
                        VALUES (?, ?, ?)
                    ''', (code, info['name'], info['type']))
                
                self.db.conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
            if self.db.conn:
                self.db.conn.rollback()
            
    def _load_cache(self):
        """Load items into cache."""
        try:
            if not self.db.conn:
                self.db.conn = sqlite3.connect(self.db.db_path)
            cursor = self.db.conn.cursor()
            
            cursor.execute('SELECT code, name, type, last_used FROM item_codes')
            for code, name, type_, last_used in cursor.fetchall():
                self._items_cache[code] = {
                    'name': name,
                    'type': type_,
                    'last_used': last_used
                }
        except Exception as e:
            print(f"Error loading cache: {e}")
                
    @property
    def ITEM_CODES(self) -> Dict[str, dict]:
        """Get all item codes from the database."""
        return self._items_cache
                
    def get_item_details(self, code: str) -> Optional[dict]:
        """Get item details from cache."""
        if not code:
            return None
            
        # Convert code to uppercase for case-insensitive lookup
        code = code.upper()
        
        # Try direct lookup first (faster)
        if code in self._items_cache:
            item = self._items_cache[code].copy()
            if item['type'] not in ['G', 'S', 'O']:  # Gold, Silver, or Other
                return None
            return item
            
        # If not found, try case-insensitive search
        for cached_code, item in self._items_cache.items():
            if cached_code.upper() == code:
                item_copy = item.copy()
                if item_copy['type'] not in ['G', 'S', 'O']:  # Gold, Silver, or Other
                    return None
                return item_copy
                
        return None
        
    def add_item(self, code: str, name: str, type_: str) -> bool:
        """Add a new item or update existing one."""
        try:
            if not code or not name or not type_:
                return False
                
            if type_ not in ['G', 'S', 'O']:  # Gold, Silver, or Other
                # Remove from cache if exists with invalid type
                if code in self._items_cache:
                    del self._items_cache[code]
                return False
                
            if not self.db.conn:
                self.db.conn = sqlite3.connect(self.db.db_path)
            cursor = self.db.conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO item_codes (code, name, type, last_used)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (code, name, type_))
            self.db.conn.commit()
                
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
            if self.db.conn:
                self.db.conn.rollback()
            return False
            
    def delete_item(self, code: str) -> bool:
        """Delete an item from the database."""
        try:
            if not code:
                return False
                
            if not self.db.conn:
                self.db.conn = sqlite3.connect(self.db.db_path)
            cursor = self.db.conn.cursor()
            
            cursor.execute('DELETE FROM item_codes WHERE code = ?', (code,))
            self.db.conn.commit()
                
            # Remove from cache
            if code in self._items_cache:
                del self._items_cache[code]
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            if self.db.conn:
                self.db.conn.rollback()
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
                
            if not self.db.conn:
                self.db.conn = sqlite3.connect(self.db.db_path)
            cursor = self.db.conn.cursor()
            
            current_time = datetime.now().isoformat()
            cursor.execute('''
                UPDATE item_codes
                SET last_used = ?
                WHERE code = ?
            ''', (current_time, code))
            self.db.conn.commit()
                
            # Update cache
            self._items_cache[code]['last_used'] = current_time
            return True
        except Exception as e:
            print(f"Error updating last used: {e}")
            if self.db.conn:
                self.db.conn.rollback()
            return False
            
    def get_recent_items(self, limit: int = 10) -> List[Dict]:
        """Get recently used items."""
        try:
            if not self.db.conn:
                self.db.conn = sqlite3.connect(self.db.db_path)
            cursor = self.db.conn.cursor()
            
            cursor.execute('''
                SELECT code, name, type, last_used
                FROM item_codes
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