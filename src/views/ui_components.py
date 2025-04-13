from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QGroupBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

class TransactionTable(QTableWidget):
    """Reusable table component for displaying transactions"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Set column headers
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            'Time', 'Code', 'Weight', 'Amount', 'Mark Bill',
            'Old Type', 'Old Weight', 'Old Amount'
        ])
        
        # Style the table
        self.setStyleSheet("""
            QTableWidget {
                color: #317039;
                background-color: #F8EDD9;
                gridline-color: #317039;
                border: 1px solid #317039;
            }
            QTableWidget::item {
                color: #317039;
                padding: 5px;
                border-bottom: 1px solid #317039;
            }
            QTableWidget::item:alternate {
                background-color: #fff8f0;
            }
            QTableWidget::item:selected {
                background-color: #F1BE49;
                color: #317039;
            }
            QHeaderView::section {
                color: white;
                background-color: #317039;
                padding: 5px;
                border: 1px solid #317039;
                font-weight: bold;
            }
        """)
        
        # Enable alternating row colors
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        
        # Set selection behavior and mode
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Set column resize modes
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(self.columnCount() - 1):
            header.setSectionResizeMode(i, header.ResizeMode.ResizeToContents)
        
        # Set row height
        self.verticalHeader().setDefaultSectionSize(30)
        
    def add_row(self, time, code, weight, amount, mark_bill="", old_type="", old_weight="", old_amount="", row_data=None):
        row = self.rowCount()
        self.insertRow(row)
        
        # Add items
        items = [time, code, weight, amount, mark_bill, old_type, old_weight, old_amount]
        for col, value in enumerate(items):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if row_data:
                item.setData(Qt.ItemDataRole.UserRole, row_data)
            self.setItem(row, col, item)

class SummaryCard(QGroupBox):
    """Reusable card component for displaying summary information"""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("""
            QGroupBox {
                background-color: #F8EDD9;
                border: 2px solid #317039;
                border-radius: 8px;
                padding: 10px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                color: #317039;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #F8EDD9;
            }
            QLabel {
                color: #317039;
                font-size: 11pt;
            }
        """)
        
    def add_value(self, label, value):
        value_label = QLabel(f"{label}: {value}")
        value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(value_label)

class DateRangeSelector(QWidget):
    """Reusable component for selecting date range"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate())
        
        # Style the date selectors
        self.setStyleSheet("""
            QWidget {
                background-color: #F8EDD9;
            }
            QLabel {
                color: #317039;
                font-size: 11pt;
                font-weight: bold;
            }
            QDateEdit {
                background-color: #F8EDD9;
                color: #317039;
                border: 1px solid #317039;
                border-radius: 4px;
                padding: 5px;
            }
            QDateEdit:focus {
                border: 2px solid #F1BE49;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #317039;
            }
        """)
        
        layout.addWidget(QLabel("From:"))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel("To:"))
        layout.addWidget(self.end_date)
        
    def get_date_range(self):
        return self.start_date.date().toPyDate(), self.end_date.date().toPyDate() 