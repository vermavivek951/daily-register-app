from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit
)
from PyQt6.QtCore import QDate, Qt

class TransactionDisplay:
    """Helper class for displaying transactions in the UI."""
    
    @staticmethod
    def display_transactions(table_widget, transactions):
        """Display transactions in the history table."""
        # Clear existing rows
        table_widget.setRowCount(0)
        
        # Add transactions to table
        for transaction in transactions:
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            
            # Format date and time
            date_str = transaction.timestamp.strftime("%Y-%m-%d")
            time_str = transaction.timestamp.strftime("%H:%M:%S")
            
            # Add transaction details
            table_widget.setItem(row_position, 0, QTableWidgetItem(date_str))
            table_widget.setItem(row_position, 1, QTableWidgetItem(time_str))
            
            # Format items
            items_text = TransactionDisplay.format_items_text(transaction)
            table_widget.setItem(row_position, 2, QTableWidgetItem(items_text))
            
            # Format weight
            weight_text = TransactionDisplay.format_weight_text(transaction)
            table_widget.setItem(row_position, 3, QTableWidgetItem(weight_text))
            
            # Format amount
            amount_text = f"₹{transaction.total_amount:.2f}"
            table_widget.setItem(row_position, 4, QTableWidgetItem(amount_text))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            view_button = QPushButton("View")
            view_button.clicked.connect(lambda checked, t=transaction: TransactionDisplay.view_transaction(t))
            actions_layout.addWidget(view_button)
            
            table_widget.setCellWidget(row_position, 5, actions_widget)
        
        # Adjust column widths
        table_widget.resizeColumnsToContents()
    
    @staticmethod
    def format_items_text(transaction):
        """Format the items text for display in the table."""
        items = []
        
        # Add new items
        for item in transaction.new_items:
            item_type = "Gold" if "G" in item.code else "Silver"
            items.append(f"{item_type} ({item.code})")
        
        # Add old items
        for item in transaction.old_items:
            items.append(f"Old {item.type}")
        
        return ", ".join(items)
    
    @staticmethod
    def format_weight_text(transaction):
        """Format the weight text for display in the table."""
        gold_weight = 0.0
        silver_weight = 0.0
        
        # Calculate weights
        for item in transaction.new_items:
            if "G" in item.code:
                gold_weight += item.weight
            else:
                silver_weight += item.weight
        
        for item in transaction.old_items:
            if item.type == "Gold":
                gold_weight += item.weight
            else:
                silver_weight += item.weight
        
        # Format text
        weight_text = []
        if gold_weight > 0:
            weight_text.append(f"G: {gold_weight:.2f}")
        if silver_weight > 0:
            weight_text.append(f"S: {silver_weight:.2f}")
        
        return ", ".join(weight_text)
    
    @staticmethod
    def view_transaction(transaction):
        """View detailed information about a transaction."""
        # Create a detailed message
        message = f"Transaction Details\n\n"
        message += f"Date: {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # New items
        if transaction.new_items:
            message += "New Items:\n"
            for item in transaction.new_items:
                item_type = "Gold" if "G" in item.code else "Silver"
                message += f"- {item_type} ({item.code}): {item.weight:.2f} gm, ₹{item.amount:.2f}"
                if item.is_billable:
                    message += " (Billable)"
                message += "\n"
            message += "\n"
        
        # Old items
        if transaction.old_items:
            message += "Old Items:\n"
            for item in transaction.old_items:
                message += f"- {item.type}: {item.weight:.2f} gm, ₹{item.amount:.2f}\n"
            message += "\n"
        
        # Payment details
        message += "Payment Details:\n"
        message += f"- Cash: ₹{transaction.payment_details.get('cash', 0):.2f}\n"
        message += f"- Card: ₹{transaction.payment_details.get('card', 0):.2f}\n"
        message += f"- UPI: ₹{transaction.payment_details.get('upi', 0):.2f}\n"
        message += f"- Total: ₹{transaction.total_amount:.2f}\n"
        
        # Show message
        QMessageBox.information(None, "Transaction Details", message)
    
    @staticmethod
    def setup_transaction_table(table_widget):
        """Setup the transaction table with proper columns."""
        table_widget.setColumnCount(6)
        table_widget.setHorizontalHeaderLabels([
            "Date", "Time", "Items", "Weight (gm)", "Amount (₹)", "Actions"
        ])
        
        # Set styling
        table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #F8EDD9;
                gridline-color: #317039;
                border: 1px solid #317039;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #317039;
                color: #317039;
                background-color: transparent;
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
                border-bottom: 2px solid #F8EDD9;
                font-weight: bold;
            }
            QPushButton {
                background-color: #317039;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3d8847;
            }
            QPushButton:pressed {
                background-color: #245b2b;
            }
        """)
        
        # Set column widths
        table_widget.setColumnWidth(0, 100)  # Date
        table_widget.setColumnWidth(1, 80)   # Time
        table_widget.setColumnWidth(2, 300)  # Items
        table_widget.setColumnWidth(3, 120)  # Weight
        table_widget.setColumnWidth(4, 120)  # Amount
        table_widget.setColumnWidth(5, 100)  # Actions 