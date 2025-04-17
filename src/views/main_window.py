import sys
import os
import traceback
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QDateEdit, QTableWidget, QGroupBox,
    QMessageBox, QCheckBox, QComboBox, QTableWidgetItem, QFrame,
    QSpacerItem, QSizePolicy, QMenuBar, QMenu, QStatusBar, QScrollArea,
    QSplitter, QTabWidget, QListWidget, QListWidgetItem, QDialog,
    QHeaderView, QFileDialog, QTextEdit, QGridLayout, QProgressDialog,
    QApplication
)
from PyQt6.QtCore import Qt, QDate, QEvent, QTimer, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QFont, QColor, QAction, QPainter, QPen, QPixmap, QIcon, QPalette, QFontDatabase

from controllers.transaction_controller import TransactionController
from views.transaction_display import TransactionDisplay
from views.ui_components import TransactionTable, SummaryCard, DateRangeSelector
from views.view_models import TransactionViewModel
from views.slip_entry_form import SlipEntryForm
from utils.excel_exporter import ExcelExporter
from utils.backup_manager import BackupManager
from database.db_manager import DatabaseManager

class JewellerySlip(QWidget):
    def __init__(self, transaction_data):
        super().__init__()
        self.transaction_data = transaction_data
        self.setup_ui()

    def setup_ui(self):
        """Setup the slip UI with transaction data."""
        self.setWindowTitle("Jewellery Sale Entry Slip")
        self.setGeometry(100, 100, 400, 600)
        
        # Set the background color
        self.setStyleSheet("""
            QWidget {
                background-color: #F8EDD9;
            }
            QLabel {
                color: #317039;
                font-family: 'Segoe UI', Arial;
                background: transparent;
            }
            QTextEdit {
                color: #317039;
                font-family: 'Segoe UI', Arial;
                background: transparent;
                border: none;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header (Slip Number & Date)
        header_layout = QHBoxLayout()
        
        slip_no = QLabel(f"Slip No: {self.transaction_data.get('id', '')}")
        slip_no.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        slip_no.setStyleSheet("color: #317039;")
        header_layout.addWidget(slip_no)

        # Get date from transaction data
        date_str = ""
        if 'timestamp' in self.transaction_data:
            try:
                timestamp = self.transaction_data['timestamp']
                if isinstance(timestamp, str):
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    date_str = dt.strftime('%d-%m-%Y')
                else:
                    date_str = timestamp.strftime('%d-%m-%Y')
            except:
                date_str = self.transaction_data.get('date', '')
        else:
            date_str = self.transaction_data.get('date', '')
            
        date_label = QLabel(f"Date: {date_str}")
        date_label.setFont(QFont("Segoe UI", 14))
        date_label.setStyleSheet("color: #317039;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)

        # Item Details
        items_text = QTextEdit()
        items_text.setReadOnly(True)
        items_text.setFont(QFont("Segoe UI", 12))
        
        # Format items content with HTML styling
        items_content = "<div style='color: #317039;'>"
        items_content += "<h3 style='margin-bottom: 10px;'>New Items:</h3>"
        
        for item in self.transaction_data.get('new_items', []):
            name = item.get('name', '').ljust(20)
            weight = f"{float(item.get('weight', 0)):.3f}g".rjust(10)
            amount = f"₹{float(item.get('amount', 0)):.2f}".rjust(12)
            items_content += f"<div style='margin-bottom: 8px; font-size: 12pt;'>{name} {weight}  {amount}</div>"
        
        items_content += "<h3 style='margin: 15px 0 10px 0;'>Old Items:</h3>"
        for item in self.transaction_data.get('old_items', []):
            type_str = item.get('type', '').ljust(20)
            weight = f"{float(item.get('weight', 0)):.3f}g".rjust(10)
            amount = f"₹{float(item.get('amount', 0)):.2f}".rjust(12)
            items_content += f"<div style='margin-bottom: 8px; font-size: 12pt;'>{type_str} {weight}  {amount}</div>"
        
        items_content += "</div>"
        items_text.setHtml(items_content)
        layout.addWidget(items_text)

        # Payment Details
        payment_text = QTextEdit()
        payment_text.setReadOnly(True)
        payment_text.setFont(QFont("Segoe UI", 12))
        
        # Format payment content with HTML styling
        payment_content = "<div style='color: #317039;'>"
        payment_content += "<h3 style='margin-bottom: 10px;'>Payment Details:</h3>"
        
        cash_amount = float(self.transaction_data.get('cash_amount', 0))
        card_amount = float(self.transaction_data.get('card_amount', 0))
        upi_amount = float(self.transaction_data.get('upi_amount', 0))
        
        if cash_amount > 0:
            payment_content += f"<div style='margin-bottom: 8px; font-size: 12pt;'>{'Cash Amount:'.ljust(20)} ₹{cash_amount:.2f}</div>"
        if card_amount > 0:
            payment_content += f"<div style='margin-bottom: 8px; font-size: 12pt;'>{'Card Amount:'.ljust(20)} ₹{card_amount:.2f}</div>"
        if upi_amount > 0:
            payment_content += f"<div style='margin-bottom: 8px; font-size: 12pt;'>{'UPI Amount:'.ljust(20)} ₹{upi_amount:.2f}</div>"
            
        total_amount = cash_amount + card_amount + upi_amount
        payment_content += f"<div style='margin-top: 15px; font-weight: bold; font-size: 14pt;'>{'Total Amount:'.ljust(20)} ₹{total_amount:.2f}</div>"
        
        # Add comments if available
        comments = self.transaction_data.get('comments', '').strip()
        if comments:
            payment_content += f"<h3 style='margin: 15px 0 10px 0;'>Comments:</h3>"
            payment_content += f"<div style='font-size: 12pt;'>{comments}</div>"
        
        payment_content += "</div>"
        payment_text.setHtml(payment_content)
        layout.addWidget(payment_text)

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
        pen = QPen(QColor("#317039"), 2)
        painter.setPen(pen)
        painter.drawRect(10, 10, self.width() - 20, self.height() - 20)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize view model with database manager
        self.view_model = TransactionViewModel(self.db_manager)
        
        # Initialize components
        self.controller = TransactionController(self.db_manager)
        self.excel_exporter = ExcelExporter()
        
        # Selection handling flag
        self.is_handling_selection = False
        
        # Create icons directory if it doesn't exist
        self.ensure_icons_directory()
        
        # Setup UI components
        self.setup_ui()
        self.connect_signals()
        self.apply_styles()
        
        # Load initial data
        self.refresh_register_view()
        
    def ensure_icons_directory(self):
        """Create icons directory if it doesn't exist."""
        import os
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")
        if not os.path.exists(icons_dir):
            try:
                os.makedirs(icons_dir)
            except Exception as e:
                print(f"Error creating icons directory: {e}")
        
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("Jewellery Shop Management System")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)  # Reduce spacing between sections
        main_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # Create top widget for slip form (fixed height)
        top_widget = QWidget()
        top_widget.setFixedHeight(200)  # Reduce fixed height for slip form
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSpacing(2)  # Minimal spacing
        top_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        main_layout.addWidget(top_widget)
        
        # Add horizontal line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: #bdc3c7;
                background-color: #bdc3c7;
                height: 1px;
            }
        """)
        main_layout.addWidget(separator)
        
        # Create bottom widget for register view
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setSpacing(2)  # Minimal spacing
        bottom_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        main_layout.addWidget(bottom_widget)
        
        # Setup slip form in top section
        self.setup_slip_form(top_layout)
        
        # Setup register view in bottom section
        self.setup_register_view(bottom_layout)
        
        # Setup menu and status bar
        self.setup_menu()
        self.setup_status_bar()
        
    def setup_register_view(self, parent_layout):
        """Setup the register view."""
        # Create register view container
        register_container = QWidget()
        register_layout = QVBoxLayout(register_container)
        
        # Toolbar with date selector and show today button
        toolbar = QHBoxLayout()
        
        # Add date range selector
        date_range_group = QGroupBox("Date Range")
        date_range_layout = QHBoxLayout()
        
        # From date
        from_label = QLabel("From:")
        from_label.setFont(QFont("Arial", 10))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate())
        self.from_date.setDisplayFormat("dd-MM-yyyy")
        
        # To date
        to_label = QLabel("To:")
        to_label.setFont(QFont("Arial", 10))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setDisplayFormat("dd-MM-yyyy")
        
        # Apply Range button
        self.apply_range_button = QPushButton("Apply Range")
        self.apply_range_button.setStyleSheet("""
            QPushButton {
                background-color: #317039;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8847;
            }
        """)
        
        # Add "Show Today" button
        self.show_today_button = QPushButton("Show Today")
        try:
            self.show_today_button.setIcon(QIcon("icons/calendar-today.png"))
        except Exception:
            pass
        self.show_today_button.setToolTip("Set date to today and show today's transactions (Ctrl+T)")
        self.show_today_button.setShortcut("Ctrl+T")
        self.show_today_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        # Add widgets to date range layout
        date_range_layout.addWidget(from_label)
        date_range_layout.addWidget(self.from_date)
        date_range_layout.addWidget(to_label)
        date_range_layout.addWidget(self.to_date)
        date_range_layout.addWidget(self.apply_range_button)
        date_range_layout.addWidget(self.show_today_button)
        
        date_range_group.setLayout(date_range_layout)
        date_range_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #317039;
                border-radius: 4px;
                margin-top: 0.5em;
                padding: 5px;
            }
            QGroupBox::title {
                color: #317039;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
        toolbar.addWidget(date_range_group)
        toolbar.addStretch()
        
        # Add toolbar to layout
        register_layout.addLayout(toolbar)
        
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
        
        # Set grid style with eye-friendly colors
        self.register_table.setStyleSheet("""
            QTableWidget {
                gridline-color: transparent;
                background-color: #F8EDD9;
                alternate-background-color: #f3e5c8;
                border: 1px solid #317039;
                border-radius: 4px;
            }
            QTableWidget::item {
                border-right: 1px solid #317039;
                padding: 8px;
                color: #317039;
            }
            QTableWidget::item:column[2],
            QTableWidget::item:column[3],
            QTableWidget::item:column[4],
            QTableWidget::item:column[5],
            QTableWidget::item:column[6],
            QTableWidget::item:column[7],
            QTableWidget::item:column[8],
            QTableWidget::item:column[9] {
                border-bottom: none;
            }
            QTableWidget::item[last_row="true"] {
                border-bottom: 2px solid #317039;
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
            QHeaderView::section:hover {
                background-color: #3d8847;
            }
            QTableCornerButton::section {
                background-color: #317039;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F8EDD9;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #317039;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #F8EDD9;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #317039;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Add to layout
        register_layout.addWidget(self.register_table)
        
        # Daily totals
        totals_layout = self.setup_summary_section()
        register_layout.addLayout(totals_layout)
        
        # Add register container to parent layout
        parent_layout.addWidget(register_container)
        
    def connect_signals(self):
        """Connect all signals and slots."""
        # Connect slip form signals
        if hasattr(self, 'slip_form'):
            self.slip_form.item_added.connect(self.on_new_item_added)
            self.slip_form.old_item_added.connect(self.on_old_item_added)
            self.slip_form.payment_entered.connect(self.on_payment_entered)
        
            # Connect date range signals
            self.from_date.dateChanged.connect(self.on_date_range_changed)
            self.to_date.dateChanged.connect(self.on_date_range_changed)
            self.apply_range_button.clicked.connect(self.refresh_register_view)
            self.show_today_button.clicked.connect(self.show_today)
        
    def on_date_range_changed(self, date):
        """Handle date range change."""
        # Ensure 'to_date' is not earlier than 'from_date'
        if self.to_date.date() < self.from_date.date():
            self.to_date.setDate(self.from_date.date())

    def show_today(self):
        """Set both dates to today and refresh the view."""
        today = QDate.currentDate()
        self.from_date.setDate(today)
        self.to_date.setDate(today)
        self.refresh_register_view()

    def refresh_register_view(self):
        """Refresh the register view with the current date's transactions."""
        try:
            print("Refreshing register view...")  # Debug print
            
            # Clear existing rows
            self.register_table.setRowCount(0)
            
            # Get selected date range and convert QDate to Python date
            from_date = self.from_date.date().toPyDate()
            to_date = self.to_date.date().toPyDate()
            
            # Get transactions for the selected date range
            transactions = self.view_model.get_transactions_range(from_date, to_date)
            print(f"Retrieved {len(transactions)} transactions")  # Debug print
            
            # Dictionary to store row ranges for each transaction
            self.transaction_rows = {}
            
            # Insert rows for each transaction
            for transaction in transactions:
                try:
                    print(f"Processing transaction: {transaction}")  # Debug print
                    
                    # Get the number of rows needed for this transaction
                    new_items = transaction.get('new_items', [])
                    old_items = transaction.get('old_items', [])
                    new_items_count = len(new_items)
                    old_items_count = len(old_items)
                    max_rows = max(1, new_items_count, old_items_count)
                    
                    # Insert rows for this transaction
                    start_row = self.register_table.rowCount()
                    for i in range(max_rows):
                        self.register_table.insertRow(start_row + i)
                    
                    # Store the row range for this transaction
                    self.transaction_rows[transaction['id']] = (start_row, start_row + max_rows - 1)
                    
                    # Get transaction details
                    date_str = str(transaction.get('date', ''))
                    time_str = str(transaction.get('time', ''))
                    comments = str(transaction.get('comments', ''))
                    
                    # Set date, time, and comments in the first row
                    self.register_table.setItem(start_row, 0, QTableWidgetItem(date_str))
                    self.register_table.setItem(start_row, 1, QTableWidgetItem(time_str))
                    self.register_table.setItem(start_row, 10, QTableWidgetItem(comments))
                    
                    # If multiple rows, merge cells for date, time and comments
                    if max_rows > 1:
                        self.register_table.setSpan(start_row, 0, max_rows, 1)  # Date
                        self.register_table.setSpan(start_row, 1, max_rows, 1)  # Time
                        self.register_table.setSpan(start_row, 10, max_rows, 1)  # Comments
                    
                    # Add new items
                    for i, item in enumerate(new_items):
                        row = start_row + i
                        
                        # Item code
                        code = str(item.get('code', ''))
                        self.register_table.setItem(row, 2, QTableWidgetItem(code))
                        
                        # Name
                        name = str(item.get('name', ''))
                        self.register_table.setItem(row, 3, QTableWidgetItem(name))
                        
                        # Weight
                        weight = float(item.get('weight', 0))
                        weight_str = f"{weight:.3f}"
                        self.register_table.setItem(row, 4, QTableWidgetItem(weight_str))
                        
                        # Amount
                        amount = float(item.get('amount', 0))
                        amount_str = f"{amount:.2f}"
                        self.register_table.setItem(row, 5, QTableWidgetItem(amount_str))
                        
                        # Mark as Bill
                        is_billable = "Yes" if item.get('is_billable', False) else "No"
                        self.register_table.setItem(row, 6, QTableWidgetItem(is_billable))
                    
                    # Add old items
                    for i, item in enumerate(old_items):
                        row = start_row + i
                        
                        # Type
                        item_type = str(item.get('type', ''))
                        self.register_table.setItem(row, 7, QTableWidgetItem(item_type))
                        
                        # Weight
                        weight = float(item.get('weight', 0))
                        weight_str = f"{weight:.3f}"
                        self.register_table.setItem(row, 8, QTableWidgetItem(weight_str))
                        
                        # Amount
                        amount = float(item.get('amount', 0))
                        amount_str = f"{amount:.2f}"
                        self.register_table.setItem(row, 9, QTableWidgetItem(amount_str))
                    
                    # Add action buttons in the first row
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(0, 0, 0, 0)
                    
                    view_btn = QPushButton("View")
                    view_btn.clicked.connect(lambda checked, t=transaction: self.view_transaction(t))
                    actions_layout.addWidget(view_btn)
                    
                    delete_btn = QPushButton("Delete")
                    delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                            font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
                    delete_btn.clicked.connect(lambda checked, t=transaction: self.delete_transaction(t))
                    actions_layout.addWidget(delete_btn)
                    
                    self.register_table.setCellWidget(start_row, 11, actions_widget)
                    
                    # If multiple rows, merge cells for actions
                    if max_rows > 1:
                        self.register_table.setSpan(start_row, 11, max_rows, 1)
                        
                except Exception as trans_error:
                    print(f"Error processing transaction: {trans_error}")
                    traceback.print_exc()
            
            # Update daily totals
            self.update_daily_totals()
            
        except Exception as e:
            print(f"Error refreshing register view: {e}")
            traceback.print_exc()
        finally:
            self.is_handling_selection = False

    def handle_selection_changed(self):
        """Handle table selection changes to select all rows of a transaction."""
        # Prevent re-entry if we're already handling selection
        if self.is_handling_selection:
            return
            
        try:
            self.is_handling_selection = True
            
            selected_items = self.register_table.selectedItems()
            if not selected_items:
                self.is_handling_selection = False
                return
                
            # Get the row of the first selected item
            selected_row = selected_items[0].row()
            
            # Find which transaction range this row belongs to
            for base_row, (start_row, end_row) in self.transaction_rows.items():
                if start_row <= selected_row <= end_row:
                    # Select all rows in this transaction range
                    self.register_table.clearSelection()
                    for row in range(start_row, end_row + 1):
                        self.register_table.selectRow(row)
                    break
                    
        except Exception as e:
            print(f"Error handling selection: {e}")
        finally:
            self.is_handling_selection = False

    def eventFilter(self, source, event):
        """Event filter to handle deselection in table."""
        if (source is self.register_table.viewport() and 
            event.type() == QEvent.Type.MouseButtonPress):
            point = event.pos()
            item = self.register_table.itemAt(point)
            
            # Prevent re-entry if we're already handling selection
            if not self.is_handling_selection:
                try:
                    self.is_handling_selection = True
                    
                    if item is None:
                        # Clicked in empty area
                        self.register_table.clearSelection()
                        return True
                    else:
                        # Get the row that was clicked
                        clicked_row = item.row()
                        # Find and select all rows for this transaction
                        for base_row, (start_row, end_row) in self.transaction_rows.items():
                            if start_row <= clicked_row <= end_row:
                                self.register_table.clearSelection()
                                for row in range(start_row, end_row + 1):
                                    self.register_table.selectRow(row)
                                return True
                except Exception as e:
                            print(f"Error in event filter: {e}")
                finally:
                    self.is_handling_selection = False
                    
        return super().eventFilter(source, event)

    def update_daily_totals(self):
        """Update the totals display for the selected date range."""
        try:
            from_date = self.from_date.date().toPyDate()
            to_date = self.to_date.date().toPyDate()
            
            # Get summary for the date range
            summary = self.view_model.get_date_range_summary(from_date, to_date)
            
            # Update New Items Summary
            self.new_items_gold_weight_label.setText(f"Gold Weight: {summary.get('new_gold_weight', 0):.3f}")
            self.new_items_silver_weight_label.setText(f"Silver Weight: {summary.get('new_silver_weight', 0):.3f}")
            self.new_items_amount_label.setText(f"Amount: ₹{summary.get('new_amount', 0):,.2f}")
            
            # Update Old Items Summary
            self.old_items_gold_weight_label.setText(f"Gold Weight: {summary.get('old_gold_weight', 0):.3f}")
            self.old_items_silver_weight_label.setText(f"Silver Weight: {summary.get('old_silver_weight', 0):.3f}")
            self.old_items_amount_label.setText(f"Amount: ₹{summary.get('old_amount', 0):,.2f}")
            
            # Update Payment Summary
            self.cash_total_label.setText(f"Cash: ₹{summary.get('cash_total', 0):,.2f}")
            self.card_total_label.setText(f"Card: ₹{summary.get('card_total', 0):,.2f}")
            self.upi_total_label.setText(f"UPI: ₹{summary.get('upi_total', 0):,.2f}")
            
            # Calculate and update total amount
            total_amount = (summary.get('cash_total', 0) + 
                          summary.get('card_total', 0) + 
                          summary.get('upi_total', 0))
            self.total_amount_label.setText(f"Total: ₹{total_amount:,.2f}")
            
        except Exception as e:
            print(f"Error updating daily totals: {e}")

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
        
        # Settings Menu
        settings_menu = menubar.addMenu('Settings')
        item_codes_action = QAction('Item Codes', self)
        item_codes_action.triggered.connect(self.show_settings_dialog)
        settings_menu.addAction(item_codes_action)
        
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
                background-color: #F8EDD9;
            }
            QLabel {
                color: #317039;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #317039;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d8847;
            }
            QPushButton:pressed {
                background-color: #245b2b;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #317039;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
                background-color: white;
            }
            QLineEdit, QDateEdit {
                padding: 6px;
                border: 1px solid #317039;
                border-radius: 4px;
                background-color: white;
                color: #317039;
                selection-background-color: #F1BE49;
                selection-color: #317039;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #F1BE49;
            }
            QTableWidget {
                border: 1px solid #317039;
                border-radius: 4px;
                background-color: white;
                gridline-color: #F8EDD9;
            }
            QHeaderView::section {
                background-color: #317039;
                padding: 8px;
                border: none;
                border-right: 1px solid #F8EDD9;
                border-bottom: 1px solid #F8EDD9;
                color: white;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #F1BE49;
                color: #317039;
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
                border-top: 5px solid #317039;
                width: 0;
                height: 0;
                margin-top: 5px;
            }
            /* Show Today Button specific style */
            #show_today_button {
                background-color: #F1BE49;
                color: #317039;
            }
            #show_today_button:hover {
                background-color: #f3c968;
            }
            #show_today_button:pressed {
                background-color: #e0af38;
            }
            /* Dialog Styling */
            QDialog {
                background-color: #F8EDD9;
            }
            QDialog QLabel {
                color: #317039;
                font-size: 11pt;
            }
            QMessageBox {
                background-color: #F8EDD9;
            }
            QMessageBox QLabel {
                color: #317039;
                font-size: 11pt;
            }
            QMessageBox QPushButton {
                background-color: #317039;
                color: white;
            }
            QMessageBox QPushButton:hover {
                background-color: #3d8847;
            }
            /* Menu Styling */
            QMenuBar {
                background-color: #317039;
                color: white;
                border-bottom: 1px solid #245b2b;
            }
            QMenuBar::item {
                padding: 4px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background-color: #3d8847;
                color: white;
            }
            QMenu {
                background-color: #F8EDD9;
                border: 1px solid #317039;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
                color: #317039;
            }
            QMenu::item:selected {
                background-color: #F1BE49;
                color: #317039;
            }
            QMenu::separator {
                height: 1px;
                background: #317039;
                margin: 5px 0;
            }
            /* Status Bar */
            QStatusBar {
                background-color: #317039;
                color: white;
            }
            /* Scrollbar Styling */
            QScrollBar:vertical {
                border: none;
                background: #F8EDD9;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #317039;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #F8EDD9;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #317039;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
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
        """Show a dialog with billable and non-billable items summary for the selected date range."""
        try:
            from_date = self.from_date.date().toPyDate()
            to_date = self.to_date.date().toPyDate()
            
            items_data = self.view_model.get_billable_items_range(from_date, to_date)
            
            if not items_data or ('billable' not in items_data and 'non_billable' not in items_data):
                QMessageBox.information(self, "No Data", "No billable items found for the selected date range.")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Billable Summary ({from_date.strftime('%d-%m-%Y')} to {to_date.strftime('%d-%m-%Y')})")
            dialog.setMinimumSize(800, 600)  # Set minimum size for the dialog
            
            tab_widget = QTabWidget()
            billable_table = QTableWidget()
            non_billable_table = QTableWidget()
            
            # Set up the tables
            for table in [billable_table, non_billable_table]:
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels([
                    "Item Code", 
                    "Item Name", 
                    "Total Weight", 
                    "Total Amount",
                    "Actions"
                ])
                
                # Configure header and column widths
                header = table.horizontalHeader()
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)        # Item Code
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)      # Item Name
                header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)        # Total Weight
                header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)        # Total Amount
                header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)        # Actions
                
                # Set specific column widths
                table.setColumnWidth(0, 100)  # Item Code
                table.setColumnWidth(2, 120)  # Total Weight
                table.setColumnWidth(3, 150)  # Total Amount
                table.setColumnWidth(4, 120)  # Actions

                table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
                table.setAlternatingRowColors(True)
                table.setMinimumHeight(400)  # Set minimum height for tables
                
                table.setStyleSheet("""
                    QTableWidget {
                        background-color: #F8EDD9;
                        border: 1px solid #317039;
                        border-radius: 4px;
                        color: black;
                    }
                    QTableWidget::item {
                        color: black;
                        padding: 5px;
                    }
                    QHeaderView::section {
                        background-color: #317039;
                        color: white;
                        padding: 5px;
                        border: none;
                        font-weight: bold;
                    }
                    QTableWidget::item:selected {
                        background-color: #F1BE49;
                        color: black;
                    }
                """)

            def show_weights_dialog(items, code, name):
                weights_dialog = QDialog(dialog)
                weights_dialog.setWindowTitle(f"Individual Weights - {code} ({name})")
                weights_dialog.setMinimumSize(400, 300)
                
                layout = QVBoxLayout(weights_dialog)
                
                # Create table for weights
                weights_table = QTableWidget()
                weights_table.setColumnCount(3)
                weights_table.setHorizontalHeaderLabels(["#", "Weight", "Amount"])
                weights_table.setRowCount(len(items))
                
                # Configure header and column widths for weights dialog
                header = weights_table.horizontalHeader()
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)      # #
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)      # Weight
                header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)    # Amount
                
                # Set specific column widths for weights dialog
                weights_table.setColumnWidth(0, 50)   # #
                weights_table.setColumnWidth(1, 120)  # Weight

                # Make table read-only
                weights_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                
                weights_table.setStyleSheet("""
                    QTableWidget {
                        background-color: #F8EDD9;
                        border: 1px solid #317039;
                        border-radius: 4px;
                        color: black;
                    }
                    QTableWidget::item {
                        color: black;
                        padding: 5px;
                    }
                    QHeaderView::section {
                        background-color: #317039;
                        color: white;
                        padding: 5px;
                        border: none;
                        font-weight: bold;
                    }
                    QTableWidget::item:selected {
                        background-color: #F1BE49;
                        color: black;
                    }
                """)
                
                total_weight = 0
                total_amount = 0
                
                # Add weights to table
                for idx, item in enumerate(items, 1):
                    number_item = QTableWidgetItem(str(idx))
                    weight_item = QTableWidgetItem(f"{item.get('weight', 0):.3f}")
                    amount_item = QTableWidgetItem(f"₹{item.get('amount', 0):,.2f}")
                    
                    number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    
                    weights_table.setItem(idx-1, 0, number_item)
                    weights_table.setItem(idx-1, 1, weight_item)
                    weights_table.setItem(idx-1, 2, amount_item)
                    
                    total_weight += item.get('weight', 0)
                    total_amount += item.get('amount', 0)
                
                # Add total row
                total_row = weights_table.rowCount()
                weights_table.insertRow(total_row)
                
                total_label = QTableWidgetItem("TOTAL")
                total_weight_item = QTableWidgetItem(f"{total_weight:.3f}")
                total_amount_item = QTableWidgetItem(f"₹{total_amount:,.2f}")
                
                for item in [total_label, total_weight_item, total_amount_item]:
                    item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
                    item.setBackground(QColor("#F1BE49"))
                
                total_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                total_weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                total_amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                weights_table.setItem(total_row, 0, total_label)
                weights_table.setItem(total_row, 1, total_weight_item)
                weights_table.setItem(total_row, 2, total_amount_item)
                
                layout.addWidget(weights_table)
                
                close_button = QPushButton("Close")
                close_button.setStyleSheet("""
                    QPushButton {
                        background-color: #317039;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #3d8847;
                    }
                """)
                close_button.clicked.connect(weights_dialog.accept)
                layout.addWidget(close_button)
                
                weights_dialog.exec()
            
            # Populate tables
            for table, items_dict, is_billable in [
                (billable_table, items_data.get('billable', {}), True),
                (non_billable_table, items_data.get('non_billable', {}), False)
            ]:
                table.setRowCount(len(items_dict))
                for row, (code, data) in enumerate(items_dict.items()):
                    items_list = data.get('items', [])
                    
                    code_item = QTableWidgetItem(str(code))
                    name_item = QTableWidgetItem(str(data.get('name', '')))
                    weight_item = QTableWidgetItem(f"{data.get('total_weight', 0):.3f}")
                    amount_item = QTableWidgetItem(f"₹{data.get('total_amount', 0):,.2f}")
                    
                    code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    
                    table.setItem(row, 0, code_item)
                    table.setItem(row, 1, name_item)
                    table.setItem(row, 2, weight_item)
                    table.setItem(row, 3, amount_item)
                    
                    # Add View Details button
                    details_button = QPushButton(f"View Details ({len(items_list)})")
                    details_button.setStyleSheet("""
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
                    """)
                    details_button.clicked.connect(
                        lambda checked, items=items_list, code=code, name=data.get('name', ''): 
                        show_weights_dialog(items, code, name)
                    )
                    
                    button_widget = QWidget()
                    button_layout = QHBoxLayout(button_widget)
                    button_layout.setContentsMargins(0, 0, 0, 0)
                    button_layout.addWidget(details_button)
                    button_layout.addStretch()
                    
                    table.setCellWidget(row, 4, button_widget)
                
                # Add totals row
                current_row = table.rowCount()
                table.insertRow(current_row)
                
                total_weight = sum(data.get('total_weight', 0) for data in items_dict.values())
                total_amount = sum(data.get('total_amount', 0) for data in items_dict.values())
                total_count = sum(len(data.get('items', [])) for data in items_dict.values())
                
                total_label = QTableWidgetItem("TOTAL")
                weight_total = QTableWidgetItem(f"{total_weight:.3f}")
                amount_total = QTableWidgetItem(f"₹{total_amount:,.2f}")
                
                for item in [total_label, weight_total, amount_total]:
                    item.setFont(QFont("Arial", weight=QFont.Weight.Bold))
                    item.setBackground(QColor("#F1BE49"))
                
                total_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                weight_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                amount_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                table.setItem(current_row, 0, total_label)
                table.setSpan(current_row, 0, 1, 2)
                table.setItem(current_row, 2, weight_total)
                table.setItem(current_row, 3, amount_total)
            
            # Add tables to tabs with counters
            billable_count = len(items_data.get('billable', {}))
            non_billable_count = len(items_data.get('non_billable', {}))
            tab_widget.addTab(billable_table, f"Billable Items ({billable_count})")
            tab_widget.addTab(non_billable_table, f"Non-Billable Items ({non_billable_count})")
            
            layout = QVBoxLayout()
            layout.addWidget(tab_widget)
            
            close_button = QPushButton("Close")
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #317039;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3d8847;
                }
                QPushButton:pressed {
                    background-color: #245b2b;
                }
            """)
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"Interface error: {str(e)}\nPlease ensure all required components are properly initialized.")
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Data error: {str(e)}\nPlease check the data format and try again.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show billable summary: {str(e)}")
            
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
        
        # Common GroupBox style
        group_box_style = """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #317039;
                border-radius: 5px;
                margin-top: 1em;
                padding: 15px;
                background-color: #F8EDD9;
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
                padding: 2px;
                background-color: transparent;
            }
            QLabel[amount="true"] {
                font-weight: bold;
                padding: 5px;
                margin-top: 5px;
                border-top: 1px solid #317039;
            }
            QLabel#total_amount {
                color: #CC4B24;
                font-weight: bold;
                font-size: 12pt;
                padding: 8px;
                margin-top: 8px;
                border-top: 2px solid #317039;
                border-radius: 4px;
                background-color: #f3e5c8;
            }
        """
        
        # New Items Summary
        new_items_summary = QGroupBox("New Items Summary")
        new_items_summary.setStyleSheet(group_box_style)
        new_items_layout = QVBoxLayout()
        self.new_items_gold_weight_label = QLabel("Gold Weight: 0.000")
        self.new_items_silver_weight_label = QLabel("Silver Weight: 0.000")
        self.new_items_amount_label = QLabel("Amount: ₹0.00")
        self.new_items_amount_label.setProperty("amount", True)
        new_items_layout.addWidget(self.new_items_gold_weight_label)
        new_items_layout.addWidget(self.new_items_silver_weight_label)
        new_items_layout.addWidget(self.new_items_amount_label)
        new_items_summary.setLayout(new_items_layout)
        
        # Old Items Summary
        old_items_summary = QGroupBox("Old Items Summary")
        old_items_summary.setStyleSheet(group_box_style)
        old_items_layout = QVBoxLayout()
        self.old_items_gold_weight_label = QLabel("Gold Weight: 0.000")
        self.old_items_silver_weight_label = QLabel("Silver Weight: 0.000")
        self.old_items_amount_label = QLabel("Amount: ₹0.00")
        self.old_items_amount_label.setProperty("amount", True)
        old_items_layout.addWidget(self.old_items_gold_weight_label)
        old_items_layout.addWidget(self.old_items_silver_weight_label)
        old_items_layout.addWidget(self.old_items_amount_label)
        old_items_summary.setLayout(old_items_layout)
        
        # Payment Summary
        payment_summary = QGroupBox("Payment Summary")
        payment_summary.setStyleSheet(group_box_style)
        payment_layout = QVBoxLayout()
        self.cash_total_label = QLabel("Cash: ₹0.00")
        self.card_total_label = QLabel("Card: ₹0.00")
        self.upi_total_label = QLabel("UPI: ₹0.00")
        self.total_amount_label = QLabel("Total: ₹0.00")
        self.total_amount_label.setObjectName("total_amount")
        payment_layout.addWidget(self.cash_total_label)
        payment_layout.addWidget(self.card_total_label)
        payment_layout.addWidget(self.upi_total_label)
        payment_layout.addWidget(self.total_amount_label)
        payment_summary.setLayout(payment_layout)
        
        # Add all summary boxes to the layout with spacing
        summary_layout.addWidget(new_items_summary)
        summary_layout.addSpacing(10)  # Add spacing between boxes
        summary_layout.addWidget(old_items_summary)
        summary_layout.addSpacing(10)  # Add spacing between boxes
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

    def setup_slip_form(self, parent_layout):
        """Setup the slip entry form in the top section."""
        # Create slip form container
        slip_container = QWidget()
        slip_layout = QVBoxLayout(slip_container)
        slip_layout.setSpacing(2)  # Minimal spacing
        slip_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        
        # Create slip form with view model
        self.slip_form = SlipEntryForm(view_model=self.view_model)
        slip_layout.addWidget(self.slip_form)
        
        # Add slip container to parent layout
        parent_layout.addWidget(slip_container)
        
    def on_new_item_added(self, item):
        """Handle new item added from slip form."""
        try:
            if self.view_model and hasattr(self.view_model, 'add_new_item'):
                if self.view_model.add_new_item(item):
                    self.statusBar().showMessage(f"Added new item: {item['code']}", 3000)
                else:
                    QMessageBox.warning(self, "Error", "Failed to add new item")
            else:
                QMessageBox.critical(self, "Error", "View model not properly initialized")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add new item: {str(e)}")
            
    def on_old_item_added(self, item):
        """Handle old item added from slip form."""
        try:
            if self.view_model and hasattr(self.view_model, 'add_old_item'):
                if self.view_model.add_old_item(item):
                    self.statusBar().showMessage(f"Added old item: {item['type']}", 3000)
                else:
                    QMessageBox.warning(self, "Error", "Failed to add old item")
            else:
                QMessageBox.critical(self, "Error", "View model not properly initialized")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add old item: {str(e)}")
            
    def on_payment_entered(self, payment_details):
        """Handle payment entered from slip form."""
        try:
            if self.view_model and hasattr(self.view_model, 'save_transaction'):
                # Save the transaction regardless of whether comments are empty
                if self.view_model.save_transaction(payment_details):
                    self.statusBar().showMessage("Transaction saved successfully", 3000)
                    
                    # Force update to today's date
                    today = QDate.currentDate()
                    self.from_date.setDate(today)
                    self.to_date.setDate(today)
                    
                    # Clear the slip form
                    if hasattr(self.slip_form, 'clear_form'):
                        self.slip_form.clear_form()
                    
                    # Explicitly refresh the view and update totals
                    self.refresh_register_view()
                    self.update_daily_totals()
                    
                else:
                    QMessageBox.warning(self, "Error", "Failed to save transaction")
            else:
                QMessageBox.critical(self, "Error", "View model not properly initialized")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save transaction: {str(e)}")

    def delete_transaction(self, transaction):
        """Delete a transaction after confirmation."""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                'Confirm Deletion',
                'Are you sure you want to delete this transaction? This action cannot be undone.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete the transaction
                if self.view_model.delete_transaction(transaction['id']):
                    # Refresh the view
                    self.refresh_register_view()
                    QMessageBox.information(
                        self,
                        'Success',
                        'Transaction deleted successfully.'
                    )
                else:
                    QMessageBox.critical(
                        self,
                        'Error',
                        'Failed to delete transaction. Please try again.'
                    )
                    
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            QMessageBox.critical(
                self,
                'Error',
                f'An error occurred while deleting the transaction: {str(e)}'
            )

    def view_transaction(self, transaction):
        """View detailed information about a transaction."""
        try:
            # Use the existing show_slip method to display the transaction details
            self.show_slip(transaction)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to view transaction: {str(e)}")

    def save_transaction(self, transaction_data):
        """Save a transaction and refresh the view."""
        try:
            # Save the transaction
            success = self.view_model.save_transaction(transaction_data)
            
            if success:
                # Refresh the view to show the new transaction
                self.refresh_register_view()
                QMessageBox.information(self, "Success", "Transaction saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save transaction.")
                
        except Exception as e:
            print(f"Error saving transaction: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while saving the transaction: {str(e)}")

    def show_settings_dialog(self):
        """Show the settings dialog."""
        from views.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh the item service to load any new items
            self.slip_form.item_service._load_cache()
            # Refresh the register view to update any item-related displays
            self.refresh_register_view()