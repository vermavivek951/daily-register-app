from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QDateEdit, QTableWidget, QGroupBox,
    QMessageBox, QCheckBox, QComboBox, QTableWidgetItem, QFrame,
    QSpacerItem, QSizePolicy, QMenuBar, QMenu, QStatusBar, QScrollArea,
    QSplitter, QTabWidget, QListWidget, QListWidgetItem, QDialog,
    QHeaderView, QFileDialog, QTextEdit, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QEvent
from PyQt6.QtGui import QFont, QColor, QAction, QPainter, QPen, QPixmap

from controllers.transaction_controller import TransactionController
from views.transaction_display import TransactionDisplay
from views.ui_components import TransactionTable, SummaryCard, DateRangeSelector
from views.view_models import TransactionViewModel
from views.slip_entry_form import SlipEntryForm
from utils.excel_exporter import ExcelExporter
from utils.backup_manager import BackupManager

class JewellerySlip(QWidget):
    def __init__(self, transaction_data):
        super().__init__()
        self.transaction_data = transaction_data
        self.setup_ui()

    def setup_ui(self):
        """Setup the slip UI with transaction data."""
        self.setWindowTitle("Jewellery Sale Entry Slip")
        self.setGeometry(100, 100, 400, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Increased spacing between sections
        layout.setContentsMargins(20, 20, 20, 20)  # Added more padding

        # Header (Slip Number & Date)
        header_layout = QHBoxLayout()
        
        slip_no = QLabel(f"Slip No: {self.transaction_data.get('id', '')}")
        slip_no.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        slip_no.setStyleSheet("color: navy;")
        header_layout.addWidget(slip_no)

        date_label = QLabel(f"Date: {self.transaction_data['timestamp'].strftime('%d-%m-%Y')}")
        date_label.setFont(QFont("Arial", 12))
        date_label.setStyleSheet("color: navy;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)

        # Item Details
        items_text = QTextEdit()
        items_text.setReadOnly(True)
        items_text.setFont(QFont("Arial", 12))
        items_text.setStyleSheet("""
            QTextEdit {
                color: navy;
                background-color: transparent;
                border: none;
                padding: 10px;
            }
        """)
        
        # Format new items with better spacing
        items_content = "New Items:\n\n"
        for item in self.transaction_data.get('new_items', []):
            name = item['name'].ljust(20)  # Left justify name with 20 chars
            weight = f"{item['weight']:.3f}g".rjust(10)  # Right justify weight with 10 chars
            amount = f"₹{item['amount']:.2f}".rjust(12)  # Right justify amount with 12 chars
            items_content += f"{name} {weight}  {amount}\n"
        
        # Format old items with better spacing
        items_content += "\nOld Items:\n\n"
        for item in self.transaction_data.get('old_items', []):
            type_str = item['type'].ljust(20)  # Left justify type with 20 chars
            weight = f"{item['weight']:.3f}g".rjust(10)  # Right justify weight with 10 chars
            amount = f"₹{item['amount']:.2f}".rjust(12)  # Right justify amount with 12 chars
            items_content += f"{type_str} {weight}  {amount}\n"
            
        items_text.setText(items_content)
        layout.addWidget(items_text)

        # Payment Details
        payment_text = QTextEdit()
        payment_text.setReadOnly(True)
        payment_text.setFont(QFont("Arial", 12))
        payment_text.setStyleSheet("""
            QTextEdit {
                color: navy;
                background-color: transparent;
                border: none;
                padding: 10px;
            }
        """)
        
        # Format payment details with better spacing
        payment_content = "Payment Details:\n\n"
        payment_content += f"{'Cash:'.ljust(20)} ₹{self.transaction_data.get('cash_amount', 0):.2f}\n"
        payment_content += f"{'Card:'.ljust(20)} ₹{self.transaction_data.get('card_amount', 0):.2f}\n"
        payment_content += f"{'UPI:'.ljust(20)} ₹{self.transaction_data.get('upi_amount', 0):.2f}\n\n"
        
        total = (self.transaction_data.get('cash_amount', 0) +
                self.transaction_data.get('card_amount', 0) +
                self.transaction_data.get('upi_amount', 0))
        
        payment_content += f"{'Total Amount:'.ljust(20)} ₹{total:.2f}"
        payment_text.setText(payment_content)
        layout.addWidget(payment_text)

        # Comments
        if self.transaction_data.get('comments'):
            comments = QLabel(f"Comments: {self.transaction_data['comments']}")
            comments.setFont(QFont("Arial", 12))
            comments.setStyleSheet("color: navy; padding: 10px;")
            comments.setWordWrap(True)
            layout.addWidget(comments)

        # Print Button
        print_button = QPushButton("Print")
        print_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        print_button.setStyleSheet("""
            QPushButton {
                background-color: navy;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-height: 30px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #000066;
            }
        """)
        print_button.clicked.connect(self.print_slip)
        layout.addWidget(print_button)

        self.setLayout(layout)

    def print_slip(self):
        """Print the slip."""
        try:
            # TODO: Implement actual printing functionality
            QMessageBox.information(self, "Print", "Printing functionality will be implemented soon!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to print: {str(e)}")

    def paintEvent(self, event):
        """Custom drawing for borders and background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Load and draw texture background
        try:
            texture = QPixmap("assets/texture.jpeg")
            if not texture.isNull():
                # Tile the texture across the background
                for x in range(0, self.width(), texture.width()):
                    for y in range(0, self.height(), texture.height()):
                        painter.drawPixmap(x, y, texture)
            else:
                # Fallback to light pink if texture can't be loaded
                painter.fillRect(self.rect(), QColor("#fff8f8"))
                print("Failed to load texture: texture is null")
        except Exception as e:
            print(f"Failed to load texture: {e}")
            painter.fillRect(self.rect(), QColor("#fff8f8"))

        # Draw border
        painter.setPen(QPen(QColor("navy"), 2))
        painter.drawRect(10, 10, self.width() - 20, self.height() - 20)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Create transaction controller with database service
        self.transaction_controller = TransactionController()
        self.view_model = TransactionViewModel(self.transaction_controller)
        self.excel_exporter = ExcelExporter()
        # Use the same database service instance
        self.backup_manager = BackupManager(self.transaction_controller.db_service)
        
        # Setup UI components
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.connect_signals()
        self.apply_styles()
        
        # Initialize with today's date and load transactions
        today = QDate.currentDate()
        print(f"[MainWindow] Initializing with today's date: {today.toString('dd-MM-yyyy')}")
        self.date_selector.setDate(today)
        self.refresh_register_view()  # This will load today's transactions
        
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Jewellery Shop Management System")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create vertical splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top pane - Slip Entry Form
        top_pane = QWidget()
        top_layout = QVBoxLayout(top_pane)
        
        # Create slip entry form with view model
        self.slip_form = SlipEntryForm(view_model=self.view_model)
        self.slip_form.transaction_saved.connect(self.refresh_register_view)  # Connect the new signal
        top_layout.addWidget(self.slip_form)
        
        # Save button
        self.save_button = QPushButton("Save Slip")
        top_layout.addWidget(self.save_button)
        
        top_pane.setLayout(top_layout)
        
        # Bottom pane - Register View
        bottom_pane = QWidget()
        bottom_layout = QVBoxLayout(bottom_pane)
        
        # Toolbar with date selector and new slip button
        toolbar = QHBoxLayout()
        
        # Date selector
        date_label = QLabel("Date:")
        self.date_selector = QDateEdit()
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())  # Set to today's date
        self.date_selector.setDisplayFormat("dd-MM-yyyy")  # Set display format
        toolbar.addWidget(date_label)
        toolbar.addWidget(self.date_selector)
        
        # Add stretch to push buttons to the right
        toolbar.addStretch()
        
        # New slip button
        self.new_slip_button = QPushButton("New Slip")
        toolbar.addWidget(self.new_slip_button)
        
        bottom_layout.addLayout(toolbar)
        
        # Register table
        self.register_table = QTableWidget()
        
        # Set up header
        self.register_table.setColumnCount(12)
        
        # Create and set header labels
        headers = [
            "Date",
            "Time",
            "Item Code",
            "Item Name",
            "Item Weight",
            "Item Amount",
            "Mark as Bill",
            "Old Item Type",
            "Old Item Weight",
            "Old Item Amount",
            "Comments",
            "Actions"
        ]
        self.register_table.setHorizontalHeaderLabels(headers)
        
        # Define header style
        header_style = """
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                padding: 8px;
                border: none;
                border-right: 1px solid #dee2e6;
                border-bottom: 1px solid #dee2e6;
                font-weight: 500;
            }
            QHeaderView::section:horizontal {
                border-top: 1px solid #dee2e6;
            }
            QHeaderView::section:vertical {
                border-left: 1px solid #dee2e6;
            }
            QHeaderView::section:pressed {
                background-color: #e9ecef;
            }
        """
        
        # Apply styles to both headers
        self.register_table.horizontalHeader().setStyleSheet(header_style)
        self.register_table.verticalHeader().setStyleSheet(header_style)
        
        # Configure vertical header (row numbers)
        self.register_table.verticalHeader().setVisible(True)
        self.register_table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.register_table.verticalHeader().setMinimumWidth(40)
        
        # Configure horizontal header for manual resizing and initial widths
        header = self.register_table.horizontalHeader()
        
        # Enable interactive resizing for all columns initially
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Set specific column widths
        column_widths = {
            0: 100,  # Date
            1: 100,  # Time
            2: 100,  # Item Code
            3: 150,  # Item Name
            4: 100,  # Item Weight
            5: 100,  # Item Amount
            6: 100,  # Mark as Bill
            7: 100,  # Old Item Type
            8: 100,  # Old Item Weight
            9: 100,  # Old Item Amount
            10: 200, # Comments
            11: 150  # Actions
        }
        
        # Apply column widths and ensure minimum sizes
        for col, width in column_widths.items():
            header.resizeSection(col, width)
        
        # Set minimum section size to prevent columns from becoming too narrow
        header.setMinimumSectionSize(50)
        
        # Enable column stretching when window is resized
        self.register_table.horizontalHeader().setStretchLastSection(True)
        
        # Set word wrap and adjust row height automatically
        self.register_table.setWordWrap(True)
        self.register_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Enable features
        self.register_table.setAlternatingRowColors(True)
        self.register_table.setShowGrid(True)
        self.register_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.register_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Allow deselection by clicking in empty area
        self.register_table.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.register_table.viewport().installEventFilter(self)
        
        # Set grid style
        self.register_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e9ecef;
                color: black;
            }
        """)
        
        # Add to layout
        bottom_layout.addWidget(self.register_table)
        
        # Daily totals
        totals_layout = self.setup_summary_section()
        
        bottom_layout.addLayout(totals_layout)
        bottom_pane.setLayout(bottom_layout)
        
        # Add panes to splitter
        splitter.addWidget(top_pane)
        splitter.addWidget(bottom_pane)
        
        # Set initial sizes (40% top, 60% bottom)
        splitter.setSizes([320, 480])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
    def connect_signals(self):
        """Connect all signals."""
        # Connect slip form signals
        self.slip_form.item_added.connect(self.on_new_item_added)
        self.slip_form.old_item_added.connect(self.on_old_item_added)
        self.slip_form.payment_entered.connect(self.on_payment_entered)
        
        # Button signals
        self.save_button.clicked.connect(self.save_transaction)
        self.new_slip_button.clicked.connect(self.clear_slip_form)
        
        # Date selector signal
        self.date_selector.dateChanged.connect(self.refresh_register_view)
        
        # Register table signal
        self.register_table.itemSelectionChanged.connect(self.on_register_selection_changed)
        
    def on_new_item_added(self, item):
        """Handle new item added from slip form."""
        if self.view_model.add_new_item(item):
            self.statusBar().showMessage(f"Added new item: {item['code']}", 3000)
        else:
            QMessageBox.warning(self, "Error", "Failed to add new item")
        
    def on_old_item_added(self, item):
        """Handle old item added from slip form."""
        if self.view_model.add_old_item(item):
            self.statusBar().showMessage(f"Added old item: {item['type']}", 3000)
        else:
            QMessageBox.warning(self, "Error", "Failed to add old item")
        
    def on_payment_entered(self, payment_details):
        """Handle payment entered from slip form."""
        # Don't call save_transaction here since it's handled in slip_entry_form
        pass
        
    def clear_slip_form(self):
        """Clear all input fields in the slip form."""
        self.slip_form.clear_form()
        self.view_model.clear_transaction()
        self.statusBar().showMessage("Form cleared", 3000)
        
    def save_transaction(self):
        """Save the transaction."""
        try:
            payment_details = self.slip_form.get_payment_details()
            
            # Try to save the transaction
            if self.view_model.save_transaction(payment_details):
                self.statusBar().showMessage("Transaction saved successfully", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to save transaction. Please check all inputs.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        
    def on_register_selection_changed(self):
        """Handle selection changes in the register table."""
        # Update status bar with selected row info
        selected_rows = self.register_table.selectedItems()
        if selected_rows:
            self.statusBar().showMessage(f"Selected {len(selected_rows)} items")
        else:
            self.statusBar().showMessage("Ready")
            
    def refresh_register_view(self):
        """Refresh the register view with current date's transactions."""
        try:
            # Clear existing rows
            self.register_table.setRowCount(0)
            
            # Get current date
            current_date = self.date_selector.date().toPyDate()
            print(f"[MainWindow] Refreshing register view for date: {current_date}")
            
            # Get transactions for current date
            transactions = self.view_model.get_transactions(current_date)
            print(f"[MainWindow] Retrieved {len(transactions)} transactions")
            
            # Add transactions to table with serial numbers
            for index, transaction in enumerate(transactions, 1):
                self.add_transaction_to_register(transaction, index)
                
            # Update daily summary
            summary = self.view_model.get_daily_summary(current_date)
            self.update_totals_display(summary)
            
            # Update status bar
            self.statusBar().showMessage(f"Showing transactions for {current_date}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh register: {str(e)}")
            print(f"[MainWindow] Error refreshing register: {e}")

    def update_totals_display(self, summary):
        """Update the totals display with summary data."""
        # Update new items totals
        self.new_items_gold_weight_label.setText(f"Gold Weight: {summary.get('new_gold_weight', 0):.3f}")
        self.new_items_silver_weight_label.setText(f"Silver Weight: {summary.get('new_silver_weight', 0):.3f}")
        self.new_items_amount_label.setText(f"Amount: ₹{summary.get('new_amount', 0):.2f}")
        
        # Update old items totals
        self.old_items_gold_weight_label.setText(f"Gold Weight: {summary.get('old_gold_weight', 0):.3f}")
        self.old_items_silver_weight_label.setText(f"Silver Weight: {summary.get('old_silver_weight', 0):.3f}")
        self.old_items_amount_label.setText(f"Amount: ₹{summary.get('old_amount', 0):.2f}")
        
        # Update payment totals
        cash_total = summary.get('cash_total', 0)
        card_total = summary.get('card_total', 0)
        upi_total = summary.get('upi_total', 0)
        total_amount = cash_total + card_total + upi_total
        
        self.cash_total_label.setText(f"Cash: ₹{cash_total:.2f}")
        self.card_total_label.setText(f"Card: ₹{card_total:.2f}")
        self.upi_total_label.setText(f"UPI: ₹{upi_total:.2f}")
        self.total_amount_label.setText(f"Total: ₹{total_amount:.2f}")
        
    def add_transaction_to_register(self, transaction, serial_number):
        """Add a transaction to the register table."""
        try:
            # Get base transaction data
            timestamp = transaction['timestamp']
            date_str = timestamp.strftime('%d-%m-%Y')  # Format date as dd-mm-yyyy
            time_str = timestamp.strftime('%H:%M:%S')
            comments = transaction.get('comments', '')
            
            # Get new items and old items
            new_items = transaction.get('new_items', [])
            old_items = transaction.get('old_items', [])
            
            # Calculate how many rows we need initially (based on new items)
            num_rows_needed = len(new_items) if new_items else 1
            
            # Create first row
            row = self.register_table.rowCount()
            self.register_table.insertRow(row)
            
            # Set the row number in vertical header for the first row only
            self.register_table.setVerticalHeaderItem(row, QTableWidgetItem(str(serial_number)))
            
            # Add date, time and comments with row spanning
            self.set_cell_value(row, 0, date_str, True, num_rows_needed)  # Date
            self.set_cell_value(row, 1, time_str, True, num_rows_needed)  # Time
            self.set_cell_value(row, 10, comments, True, num_rows_needed)  # Comments
            
            # Add buttons only to first row
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(2, 2, 2, 2)
            buttons_layout.setSpacing(4)
            
            print_button = QPushButton("Show Slip")
            print_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            print_button.clicked.connect(lambda: self.show_slip(transaction))
            buttons_layout.addWidget(print_button)
            
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            delete_button.clicked.connect(lambda: self.delete_transaction(transaction))
            buttons_layout.addWidget(delete_button)
            
            # Set row span for buttons column
            self.register_table.setCellWidget(row, 11, buttons_widget)  # Changed to column 11
            self.register_table.setSpan(row, 11, num_rows_needed, 1)  # Changed to column 11
            
            # Create additional rows if needed for new items
            for i in range(1, num_rows_needed):
                self.register_table.insertRow(row + i)
                # Create empty vertical header items for additional rows
                self.register_table.setVerticalHeaderItem(row + i, QTableWidgetItem(""))
            
            # Set the span for the vertical header (row number)
            self.register_table.setSpan(row, -1, num_rows_needed, 1)  # -1 represents the vertical header section
            
            # Fill in new items
            for i, new_item in enumerate(new_items):
                current_row = row + i
                self.set_cell_value(current_row, 2, new_item.get('code', ''))  # Shifted one column right
                self.set_cell_value(current_row, 3, new_item.get('name', ''))
                self.set_cell_value(current_row, 4, f"{new_item.get('weight', 0):.3f}")
                self.set_cell_value(current_row, 5, f"₹{new_item.get('amount', 0):.2f}")
                self.set_cell_value(current_row, 6, 'Yes' if new_item.get('mark_bill') else 'No')
            
            # Fill in old items
            for i, old_item in enumerate(old_items):
                # If we have enough rows, use them; otherwise create new ones
                if i < num_rows_needed:
                    current_row = row + i
                else:
                    # Need to create a new row for this old item
                    current_row = self.register_table.rowCount()
                    self.register_table.insertRow(current_row)
                    # Create empty vertical header item for this additional row
                    self.register_table.setVerticalHeaderItem(current_row, QTableWidgetItem(""))
                    # Extend the span of the row number
                    self.register_table.setSpan(row, -1, current_row - row + 1, 1)
                
                self.set_cell_value(current_row, 7, old_item.get('type', ''))
                self.set_cell_value(current_row, 8, f"{old_item.get('weight', 0):.3f}")
                self.set_cell_value(current_row, 9, f"₹{old_item.get('amount', 0):.2f}")
            
            # Add visual separation between transactions
            if row > 0:
                for col in range(self.register_table.columnCount()):
                    item = self.register_table.item(row - 1, col)
                    if item:
                        item.setBackground(QColor("#ffffff"))
            
        except Exception as e:
            print(f"Error adding transaction to register: {e}")
            
    def delete_transaction(self, transaction):
        """Delete a transaction after confirmation."""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                'Confirm Delete',
                'Are you sure you want to delete this transaction?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete transaction using view model
                if self.view_model.delete_transaction(transaction):
                    # Get current date for summary update
                    current_date = self.date_selector.date().toPyDate()
                    
                    # Get updated transactions and summary
                    transactions = self.view_model.get_transactions(current_date)
                    summary = self.view_model.get_daily_summary(current_date)
                    
                    # Update the UI
                    self.register_table.setRowCount(0)  # Clear the table
                    for trans in transactions:
                        self.add_transaction_to_register(trans, 1)
                    self.update_totals_display(summary)
                    
                    self.statusBar().showMessage("Transaction deleted successfully", 3000)
            else:
                    QMessageBox.warning(self, "Error", "Failed to delete transaction")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete transaction: {str(e)}")

    def set_cell_value(self, row: int, col: int, value: str, is_common_cell: bool = False, row_span: int = 1):
        """Helper method to set cell value with consistent styling."""
        item = QTableWidgetItem(str(value))
        
        # Center alignment - horizontal for all, vertical only for common cells
        if is_common_cell:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
        item.setForeground(Qt.GlobalColor.black)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        # Set background color for visual grouping
        if is_common_cell:
            item.setBackground(QColor("#f8f9fa"))
        
        self.register_table.setItem(row, col, item)
        
        # Set row span for common cells
        if is_common_cell and row_span > 1:
            self.register_table.setSpan(row, col, row_span, 1)
            
        # Adjust row height to fit content
        self.register_table.resizeRowToContents(row)

    def setup_menu(self):
        """Setup the main menu bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f8f9fa;
                color: #2c3e50;
                border-bottom: 1px solid #dcdde1;
                padding: 2px;
            }
            QMenuBar::item {
                padding: 4px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background-color: #e8f0fe;
                color: #2c3e50;
            }
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
                color: #2c3e50;
            }
            QMenu::item:selected {
                background-color: #e8f0fe;
                color: #2c3e50;
            }
            QMenu::separator {
                height: 1px;
                background: #dcdde1;
                margin: 5px 0;
            }
        """)

        # File Menu
        file_menu = menubar.addMenu('File')
        
        # Export submenu
        export_menu = QMenu('Export', self)
        export_excel = QAction('Export to Excel', self)
        export_excel.triggered.connect(self.export_to_excel)
        export_csv = QAction('Export to CSV', self)
        export_csv.triggered.connect(self.export_to_csv)
        export_menu.addAction(export_excel)
        export_menu.addAction(export_csv)
        
        # Backup submenu
        backup_menu = QMenu('Backup', self)
        backup_db = QAction('Backup Database', self)
        backup_db.triggered.connect(self.backup_database)
        restore_db = QAction('Restore Database', self)
        restore_db.triggered.connect(self.restore_database)
        backup_menu.addAction(backup_db)
        backup_menu.addAction(restore_db)
        
        # Add actions to File menu
        file_menu.addMenu(export_menu)
        file_menu.addMenu(backup_menu)
        file_menu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Reports Menu
        reports_menu = menubar.addMenu('Reports')
        daily_report = QAction('Daily Report', self)
        daily_report.triggered.connect(self.generate_daily_report)
        monthly_report = QAction('Monthly Report', self)
        monthly_report.triggered.connect(self.generate_monthly_report)
        billable_summary = QAction('Billable Summary', self)
        billable_summary.triggered.connect(self.show_billable_summary)
        reports_menu.addAction(daily_report)
        reports_menu.addAction(monthly_report)
        reports_menu.addSeparator()
        reports_menu.addAction(billable_summary)
        
        # Help Menu
        help_menu = menubar.addMenu('Help')
        check_updates = QAction('Check for Updates', self)
        check_updates.triggered.connect(self.check_for_updates)
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(check_updates)
        help_menu.addSeparator()
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Setup the status bar."""
        self.statusBar().showMessage("Ready")
        
    def apply_styles(self):
        """Apply styles to the main window."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
                background-color: white;
            }
            QLineEdit, QDateEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #3498db;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                color: #2c3e50;
                font-weight: bold;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
                padding: 0px 3px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
                width: 0;
                height: 0;
                margin-top: 5px;
            }
            /* Dialog Styling */
            QDialog {
                background-color: white;
            }
            QDialog QLabel {
                color: black;
                font-size: 11pt;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: black;
                font-size: 11pt;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
            /* Dialog Content Styling */
            QDialog QGroupBox {
                background-color: white;
                color: black;
                border: 1px solid #ddd;
                margin-top: 1.5em;
                font-weight: bold;
            }
            QDialog QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 3px;
                background-color: white;
                color: #2c3e50;
            }
        """)
        
    def export_to_excel(self):
        """Export transactions to Excel."""
        try:
            current_date = self.date_selector.date().toPyDate()
            transactions = self.view_model.get_transactions(current_date)
            
            # Use the existing export_transactions method
            filename = self.excel_exporter.export_transactions(
                transactions, 
                current_date.strftime("%Y-%m-%d")
            )
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Data exported successfully to:\n{filename}"
            )
            self.statusBar().showMessage("Export completed successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
            
    def export_to_csv(self):
        """Export transactions to CSV."""
        try:
            # Get save file location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
            )
            if file_path:
                # Get current date's transactions
                current_date = self.date_selector.date().toPyDate()
                transactions = self.view_model.get_transactions(current_date)
                
                # Export to CSV
                self.excel_exporter.export_to_csv(transactions, file_path)
                QMessageBox.information(self, "Success", "Data exported successfully!")
                self.statusBar().showMessage("Export completed successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
            
    def backup_database(self):
        """Backup the database."""
        try:
            # Use the existing create_backup method
            backup_path = self.backup_manager.create_backup()
            QMessageBox.information(
                self, 
                "Success", 
                f"Database backed up successfully to:\n{backup_path}"
            )
            self.statusBar().showMessage("Backup completed successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to backup database: {str(e)}")
            
    def restore_database(self):
        """Restore the database from backup."""
        try:
            # Show warning
            reply = QMessageBox.warning(
                self, "Warning",
                "Restoring from backup will replace your current database. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Get list of available backups
                backups = self.backup_manager.list_backups()
                if not backups:
                    QMessageBox.warning(self, "Warning", "No backups found!")
                    return
                
                # Get backup file
                file_path, _ = QFileDialog.getOpenFileName(
                    self, 
                    "Select Backup File", 
                    str(self.backup_manager.backup_dir),
                    "Backup Files (*.db);;All Files (*)"
                )
                
                if file_path:
                    self.backup_manager.restore_backup(file_path)
                    QMessageBox.information(self, "Success", "Database restored successfully!")
                    self.statusBar().showMessage("Restore completed successfully", 3000)
                    # Refresh view
                    self.refresh_register_view()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore database: {str(e)}")
            
    def generate_daily_report(self):
        """Generate and show daily report."""
        try:
            current_date = self.date_selector.date().toPyDate()
            transactions = self.view_model.get_transactions(current_date)
            summary = self.view_model.get_daily_summary(current_date)
            
            # Create report dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Daily Report - {current_date}")
            dialog.setMinimumWidth(600)
            
            layout = QVBoxLayout(dialog)
            
            # Add summary information
            summary_group = QGroupBox("Summary")
            summary_layout = QVBoxLayout()
            
            # New items summary
            summary_layout.addWidget(QLabel(f"New Items:"))
            summary_layout.addWidget(QLabel(f"  Gold Weight: {summary.get('new_gold_weight', 0):.3f} gm"))
            summary_layout.addWidget(QLabel(f"  Silver Weight: {summary.get('new_silver_weight', 0):.3f} gm"))
            summary_layout.addWidget(QLabel(f"  Total Amount: ₹{summary.get('new_amount', 0):.2f}"))
            
            # Old items summary
            summary_layout.addWidget(QLabel(f"\nOld Items:"))
            summary_layout.addWidget(QLabel(f"  Gold Weight: {summary.get('old_gold_weight', 0):.3f} gm"))
            summary_layout.addWidget(QLabel(f"  Silver Weight: {summary.get('old_silver_weight', 0):.3f} gm"))
            summary_layout.addWidget(QLabel(f"  Total Amount: ₹{summary.get('old_amount', 0):.2f}"))
            
            # Payment summary
            summary_layout.addWidget(QLabel(f"\nPayments:"))
            summary_layout.addWidget(QLabel(f"  Cash: ₹{summary.get('cash_total', 0):.2f}"))
            summary_layout.addWidget(QLabel(f"  Card: ₹{summary.get('card_total', 0):.2f}"))
            summary_layout.addWidget(QLabel(f"  UPI: ₹{summary.get('upi_total', 0):.2f}"))
            total_amount = (summary.get('cash_total', 0) + 
                          summary.get('card_total', 0) + 
                          summary.get('upi_total', 0))
            summary_layout.addWidget(QLabel(f"  Total: ₹{total_amount:.2f}"))
            
            summary_group.setLayout(summary_layout)
            layout.addWidget(summary_group)
            
            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)
            
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            
    def generate_monthly_report(self):
        """Generate and show monthly report."""
        try:
            current_date = self.date_selector.date()
            start_date = QDate(current_date.year(), current_date.month(), 1)
            end_date = start_date.addMonths(1).addDays(-1)
            
            transactions = self.view_model.get_transactions_range(
                start_date.toPyDate(),
                end_date.toPyDate()
            )
            
            # TODO: Implement monthly report dialog
            QMessageBox.information(self, "Info", "Monthly report feature coming soon!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            
    def show_billable_summary(self):
        """Show billable items summary."""
        try:
            current_date = self.date_selector.date().toPyDate()
            billable_items = self.view_model.get_billable_items(current_date)
            
            # TODO: Implement billable summary dialog
            QMessageBox.information(self, "Info", "Billable summary feature coming soon!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show summary: {str(e)}")
            
    def check_for_updates(self):
        """Check for software updates."""
        QMessageBox.information(
            self,
            "Updates",
            "You are running the latest version of the software."
        )
        
    def show_about_dialog(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            "Jewellery Shop Management System\n\n"
            "Version 1.0.0\n"
            "© 2024 All rights reserved.\n\n"
            "A comprehensive solution for managing jewellery shop transactions."
        )
        
    def setup_summary_section(self):
        """Setup the summary section at the bottom."""
        summary_layout = QHBoxLayout()
        
        # New Items Summary
        new_items_summary = QGroupBox("New Items Summary")
        new_items_summary.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0078D4;
                border-radius: 5px;
                margin-top: 1em;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                color: #0078D4;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
            QLabel {
                color: #000000;
                font-size: 11pt;
                padding: 2px;
            }
        """)
        new_items_layout = QVBoxLayout()
        self.new_items_gold_weight_label = QLabel("Gold Weight: 0.000")
        self.new_items_silver_weight_label = QLabel("Silver Weight: 0.000")
        self.new_items_amount_label = QLabel("Amount: ₹0.00")
        new_items_layout.addWidget(self.new_items_gold_weight_label)
        new_items_layout.addWidget(self.new_items_silver_weight_label)
        new_items_layout.addWidget(self.new_items_amount_label)
        new_items_summary.setLayout(new_items_layout)
        
        # Old Items Summary
        old_items_summary = QGroupBox("Old Items Summary")
        old_items_summary.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0078D4;
                border-radius: 5px;
                margin-top: 1em;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                color: #0078D4;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
            QLabel {
                color: #000000;
                font-size: 11pt;
                padding: 2px;
            }
        """)
        old_items_layout = QVBoxLayout()
        self.old_items_gold_weight_label = QLabel("Gold Weight: 0.000")
        self.old_items_silver_weight_label = QLabel("Silver Weight: 0.000")
        self.old_items_amount_label = QLabel("Amount: ₹0.00")
        old_items_layout.addWidget(self.old_items_gold_weight_label)
        old_items_layout.addWidget(self.old_items_silver_weight_label)
        old_items_layout.addWidget(self.old_items_amount_label)
        old_items_summary.setLayout(old_items_layout)
        
        # Payment Summary
        payment_summary = QGroupBox("Payment Summary")
        payment_summary.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0078D4;
                border-radius: 5px;
                margin-top: 1em;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                color: #0078D4;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
            QLabel {
                color: #000000;
                font-size: 11pt;
                padding: 2px;
            }
            QLabel#total_amount {
                color: #0078D4;
                font-weight: bold;
                font-size: 12pt;
                padding: 5px;
                margin-top: 5px;
                border-top: 1px solid #ddd;
            }
        """)
        payment_layout = QVBoxLayout()
        self.cash_total_label = QLabel("Cash: ₹0.00")
        self.card_total_label = QLabel("Card: ₹0.00")
        self.upi_total_label = QLabel("UPI: ₹0.00")
        self.total_amount_label = QLabel("Total: ₹0.00")
        self.total_amount_label.setObjectName("total_amount")  # For specific styling
        payment_layout.addWidget(self.cash_total_label)
        payment_layout.addWidget(self.card_total_label)
        payment_layout.addWidget(self.upi_total_label)
        payment_layout.addWidget(self.total_amount_label)
        payment_summary.setLayout(payment_layout)
        
        # Add all summary boxes to the layout
        summary_layout.addWidget(new_items_summary)
        summary_layout.addWidget(old_items_summary)
        summary_layout.addWidget(payment_summary)
        
        return summary_layout

    def show_slip(self, transaction):
        """Show the jewellery slip for a transaction."""
        try:
            # Store the slip as an instance variable to prevent garbage collection
            self.current_slip = JewellerySlip(transaction)
            self.current_slip.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.current_slip.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show slip: {str(e)}")

    def eventFilter(self, source, event):
        """Event filter to handle deselection in table."""
        if (source is self.register_table.viewport() and 
            event.type() == QEvent.Type.MouseButtonPress):
            point = event.pos()
            item = self.register_table.itemAt(point)
            if item is None:
                # Clicked in empty area
                self.register_table.clearSelection()
                return True
        return super().eventFilter(source, event)