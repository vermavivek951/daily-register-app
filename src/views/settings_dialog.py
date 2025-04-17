from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLabel, QLineEdit, QComboBox,
    QTabWidget, QWidget, QHeaderView
)
from PyQt6.QtCore import Qt
from services.item_service import ItemService

class ItemCodeDialog(QDialog):
    """Dialog for adding or editing an item code."""
    
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Item Code" if not self.item_data else "Edit Item Code")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Code input
        code_layout = QHBoxLayout()
        code_label = QLabel("Code:")
        self.code_input = QLineEdit()
        if self.item_data:
            self.code_input.setText(self.item_data['code'])
            self.code_input.setEnabled(False)  # Code cannot be edited
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_input)
        layout.addLayout(code_layout)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        if self.item_data:
            self.name_input.setText(self.item_data['name'])
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Gold", "Silver", "Other"])
        if self.item_data:
            type_map = {'G': "Gold", 'S': "Silver", 'O': "Other"}
            self.type_combo.setCurrentText(type_map.get(self.item_data['type'], "Other"))
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_item_data(self):
        """Get the item data from the form."""
        code = self.code_input.text().strip().upper()
        name = self.name_input.text().strip()
        type_map = {"Gold": 'G', "Silver": 'S', "Other": 'O'}
        type_ = type_map[self.type_combo.currentText()]
        
        return {
            'code': code,
            'name': name,
            'type': type_
        }

class ItemCodesSettingsTab(QWidget):
    """Tab for managing item codes in settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_service = ItemService()
        self.setup_ui()
        self.load_items()
        
    def setup_ui(self):
        """Set up the tab UI."""
        layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Item Code")
        edit_button = QPushButton("Edit Item Code")
        delete_button = QPushButton("Delete Item Code")
        
        add_button.clicked.connect(self.add_item)
        edit_button.clicked.connect(self.edit_item)
        delete_button.clicked.connect(self.delete_item)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)
        
        # Items table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Code", "Name", "Type", "Last Used"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Add styling to make text visible
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #F8EDD9;
                border: 1px solid #317039;
                border-radius: 4px;
            }
            QTableWidget::item {
                color: #317039;
                padding: 8px;
                border-bottom: 1px solid #317039;
            }
            QTableWidget::item:selected {
                background-color: #F1BE49;
                color: #317039;
            }
            QHeaderView::section {
                background-color: #317039;
                color: white;
                padding: 8px;
                border: none;
                border-right: 1px solid #F8EDD9;
                border-bottom: 1px solid #F8EDD9;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_items(self):
        """Load items into the table."""
        items = self.item_service.ITEM_CODES
        self.table.setRowCount(len(items))
        
        for row, (code, details) in enumerate(items.items()):
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(details['name']))
            type_map = {'G': "Gold", 'S': "Silver", 'O': "Other"}
            self.table.setItem(row, 2, QTableWidgetItem(type_map.get(details['type'], "Other")))
            self.table.setItem(row, 3, QTableWidgetItem(details.get('last_used', '')))
            
    def add_item(self):
        """Add a new item code."""
        dialog = ItemCodeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_data = dialog.get_item_data()
            if self.item_service.add_item(item_data['code'], item_data['name'], item_data['type']):
                self.load_items()
                QMessageBox.information(self, "Success", "Item code added successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to add item code.")
                
    def edit_item(self):
        """Edit the selected item code."""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an item code to edit.")
            return
            
        row = selected_rows[0].row()
        code = self.table.item(row, 0).text()
        item_data = self.item_service.get_item_details(code)
        
        if item_data:
            dialog = ItemCodeDialog(self, {'code': code, **item_data})
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_item_data()
                if self.item_service.add_item(new_data['code'], new_data['name'], new_data['type']):
                    self.load_items()
                    QMessageBox.information(self, "Success", "Item code updated successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update item code.")
                    
    def delete_item(self):
        """Delete the selected item code."""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an item code to delete.")
            return
            
        row = selected_rows[0].row()
        code = self.table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the item code '{code}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.item_service.delete_item(code):
                self.load_items()
                QMessageBox.information(self, "Success", "Item code deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete item code.")

class SettingsDialog(QDialog):
    """Main settings dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(ItemCodesSettingsTab(), "Item Codes")
        # Add more tabs here as needed
        
        layout.addWidget(tab_widget)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout) 