from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QFrame, QScrollArea, QFileDialog, QMenuBar,
                             QMenu, QStatusBar, QSplitter, QGroupBox,
                             QCheckBox, QHeaderView, QDialog, QFormLayout,
                             QDateEdit, QAbstractItemView, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize, QTimer, QDate, QMarginsF
from PyQt6.QtGui import QFont, QIcon, QColor, QKeySequence, QShortcut, QPageSize, QAction
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.database.db_manager import DatabaseManager
from ..models.transaction import Transaction, Item, OldItem
from ..utils.excel_exporter import ExcelExporter
from ..utils.backup_manager import BackupManager
from ..utils.analytics import Analytics
from ..utils.translations import Translations
import traceback
import logging
from src.utils.version import __version__ as APP_VERSION , LATEST_VERSION_URL , DOWNLOAD_PAGE_URL # Import version
import requests
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

# --- Version Information ---
# APP_VERSION = "1.0.0" # Removed - now imported
# LATEST_VERSION_URL = "YOUR_URL_TO_LATEST_VERSION.TXT_HERE" # Removed - now imported
# DOWNLOAD_PAGE_URL = "YOUR_URL_TO_DOWNLOAD_PAGE_HERE"       # Removed - now imported
# --------------------------

class DailyRegisterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize language
        self.current_language = 'en'
        self.translations = Translations()
        
        self.setWindowTitle("Jewellery Shop Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("QMainWindow { background-color: #f8f9fa; }") # Light background

        # Initialize data structures
        self.current_directory = os.getcwd()
        self.current_file = None
        self.entries: List[Dict] = []
        self.total_amount = 0.0
        
        # Set up logging
        self.setup_logging()
        
        # Initialize database and managers
        self.db = DatabaseManager()
        self.backup_manager = BackupManager(self.db.db_path)
        self.analytics = Analytics(self.db.db_path)
        
        # Item code mappings
        self.ITEM_CODES = {
            # Gold Items
            'GCH': {'name': 'Gold Chain', 'type': 'Gold'},
            'GBG': {'name': 'Gold Bangle', 'type': 'Gold'},
            'GRIN': {'name': 'Gold Ring', 'type': 'Gold'},
            'GER': {'name': 'Gold Earring', 'type': 'Gold'},
            'GBT': {'name': 'Gold Bracelet', 'type': 'Gold'},
            'GNK': {'name': 'Gold Necklace', 'type': 'Gold'},
            'GPD': {'name': 'Gold Pendant', 'type': 'Gold'},
            'GAN': {'name': 'Gold Anklet', 'type': 'Gold'},
            'GMG': {'name': 'Gold Mangalsutra', 'type': 'Gold'},
            'GNT': {'name': 'Gold Nath', 'type': 'Gold'},
            'GTK': {'name': 'Gold Tikka', 'type': 'Gold'},
            'GTC': {'name': 'Gold Toe Chain', 'type': 'Gold'},
            'GLOC': {'name': 'Gold Locket', 'type': 'Gold'},
            'GBALI': {'name': 'Gold Bali', 'type': 'Gold'},
            'NP': {'name': 'Gold Nose Pin', 'type': 'Gold'},
            
            # Silver Items
            'SCH': {'name': 'Silver Chain', 'type': 'Silver'},
            'SBG': {'name': 'Silver Bangle', 'type': 'Silver'},
            'SRG': {'name': 'Silver Ring', 'type': 'Silver'},
            'SER': {'name': 'Silver Earring', 'type': 'Silver'},
            'SBR': {'name': 'Silver Bracelet', 'type': 'Silver'},
            'SNK': {'name': 'Silver Necklace', 'type': 'Silver'},
            'SPD': {'name': 'Silver Pendant', 'type': 'Silver'},
            'SAN': {'name': 'Silver Anklet', 'type': 'Silver'},
            'SPA': {'name': 'Silver Payal', 'type': 'Silver'},
            'STK': {'name': 'Silver Tikka', 'type': 'Silver'},
            'STC': {'name': 'Silver Toe Chain', 'type': 'Silver'}
        }
        
        # Setup UI components
        self.setup_ui()
        self.create_menu_bar()
        self.setup_auto_backup()
        
        # Load initial data
        self.load_today_data()
        
        # Set up auto-save
        self.setup_auto_save()
        
        # Connect payment field signals
        self.cash_amount.textChanged.connect(self.calculate_net_paid)
        self.card_amount.textChanged.connect(self.calculate_net_paid)
        self.upi_amount.textChanged.connect(self.calculate_net_paid)
        
        # Initialize keyboard shortcuts
        self.setup_shortcuts()
        
        # Set up keyboard navigation for suggestion popup
        self.item_code_input.keyPressEvent = self.handle_item_code_key_press
        
    def setup_logging(self):
        """Set up logging to both file and console"""
        import logging
        import sys
        import os
        
        # Get user's AppData directory for logs
        appdata_dir = os.path.join(os.getenv('APPDATA', ''), 'DailyRegister')
        logs_dir = os.path.join(appdata_dir, 'logs')
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        # Set up logging format
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Create file handler
        file_handler = logging.FileHandler(os.path.join(logs_dir, 'app.log'))
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Set up root logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("Application started")
        
    def setup_ui(self):
        """Set up the main user interface with split layout"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-bottom: 2px solid #2980b9;
            }
        """)
        header.setFixedHeight(60)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Jewellery Shop Management System")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        main_layout.addWidget(header)
        
        # Create split pane
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create left and right panes
        left_pane = self.create_left_pane()
        right_pane = self.create_right_pane()
        
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        
        # Set splitter proportions (40:60)
        splitter.setStretchFactor(0, 40)
        splitter.setStretchFactor(1, 60)
        
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QMenuBar {
                background-color: #ffffff;
                color: #1a1a1a;
                border-bottom: 1px solid #e4e6eb;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                color: #1a1a1a;
            }
            QMenuBar::item:selected {
                background-color: #e7f3ff;
                color: #1a1a1a;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                color: #1a1a1a;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #e7f3ff;
                color: #1a1a1a;
            }
            QMessageBox, QDialog {
                background-color: #f0f2f5;
            }
            QMessageBox QLabel, QDialog QLabel {
                color: #1a1a1a;
                font-size: 14px;
                padding: 10px;
            }
            QMessageBox QPushButton, QDialog QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover, QDialog QPushButton:hover {
                background-color: #166fe5;
            }
            QMessageBox QPushButton:pressed, QDialog QPushButton:pressed {
                background-color: #1459b3;
            }
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                color: #1a1a1a;
                font-weight: bold;
                padding: 0 5px;
            }
            QLabel {
                color: #1a1a1a;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
                background-color: #ffffff;
                color: #1a1a1a;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #1877f2;
                background-color: #ffffff;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
                background-color: #ffffff;
                color: #1a1a1a;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 1px solid #1877f2;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1a1a1a;
                selection-background-color: #e7f3ff;
                selection-color: #1a1a1a;
                border: 1px solid #e4e6eb;
            }
            QCheckBox {
                color: #1a1a1a;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #e4e6eb;
                background-color: #ffffff;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #1877f2;
                background-color: #1877f2;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
            QPushButton:pressed {
                background-color: #1459b3;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 8px;
                gridline-color: #e4e6eb;
            }
            QTableWidget::item {
                padding: 8px;
                color: #1a1a1a;
                background-color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #e7f3ff;
                color: #1a1a1a;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e4e6eb;
                font-weight: bold;
                color: #1a1a1a;
            }
            QStatusBar {
                background-color: #ffffff;
                color: #1a1a1a;
                border-top: 1px solid #e4e6eb;
            }
        """)
        
    def create_left_pane(self):
        """Create the left pane with entry forms"""
        left_pane = QWidget()
        layout = QVBoxLayout(left_pane)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Common card style
        card_style = """
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e4e6eb;
            }
            QLabel {
                color: #1a1a1a;
                font-size: 11px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 11px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #1877f2;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
            QCheckBox {
                font-size: 11px;
                color: #1a1a1a;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #42b72a;
                border-color: #42b72a;
                border-radius: 4px;
            }
        """

        # Quick Entry Section
        quick_entry_card = QFrame()
        quick_entry_card.setStyleSheet(card_style)
        quick_entry_layout = QVBoxLayout(quick_entry_card)
        quick_entry_layout.setContentsMargins(12, 12, 12, 12)
        quick_entry_layout.setSpacing(6)

        # Quick Entry Header
        header_label = QLabel("Quick Entry")
        header_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #2c3e50;")
        quick_entry_layout.addWidget(header_label)

        # Forms Container
        forms_container = QWidget()
        forms_layout = QHBoxLayout(forms_container)
        forms_layout.setContentsMargins(0, 0, 0, 0)
        forms_layout.setSpacing(12)

        # New Item Form Card
        new_item_card = QFrame()
        new_item_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e4e6eb;
            }
            QLabel {
                color: #1a1a1a;
                font-size: 11px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 11px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #1877f2;
                background-color: #ffffff;
            }
            QCheckBox {
                font-size: 11px;
                color: #1a1a1a;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #42b72a;
                border-color: #42b72a;
                border-radius: 4px;
            }
        """)
        new_item_layout = QVBoxLayout(new_item_card)
        new_item_layout.setContentsMargins(10, 10, 10, 10)
        new_item_layout.setSpacing(6)

        new_item_header = QLabel("New Item")
        new_item_header.setStyleSheet("font-weight: bold; font-size: 11px; color: #2c3e50;")
        new_item_layout.addWidget(new_item_header)

        new_item_form = QFormLayout()
        new_item_form.setSpacing(6)
        new_item_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        new_item_form.setContentsMargins(0, 0, 0, 0)

        # Replace QComboBox with QLineEdit for item code entry
        self.item_code_input = QLineEdit()
        self.item_code_input.setPlaceholderText("Enter item code (e.g., GCH)")
        self.item_code_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 11px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #1877f2;
                background-color: #ffffff;
            }
        """)
        
        # Create a popup widget for suggestions
        self.suggestion_popup = QWidget(self)
        self.suggestion_popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.suggestion_popup.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
            }
        """)
        self.suggestion_layout = QVBoxLayout(self.suggestion_popup)
        self.suggestion_layout.setContentsMargins(0, 0, 0, 0)
        self.suggestion_layout.setSpacing(0)
        
        # Create a list widget for suggestions
        self.suggestion_list = QListWidget()
        self.suggestion_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: none;
                font-size: 11px;
                color: #1a1a1a;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e4e6eb;
                color: #1a1a1a;
            }
            QListWidget::item:selected {
                background-color: #e7f3ff;
                color: #1a1a1a;
            }
        """)
        self.suggestion_layout.addWidget(self.suggestion_list)
        
        # Connect signals
        self.item_code_input.textChanged.connect(self.update_suggestions)
        self.item_code_input.returnPressed.connect(self.select_suggestion)
        self.suggestion_list.itemClicked.connect(self.select_suggestion)
        
        # Add items to form
        new_item_form.addRow("Code:", self.item_code_input)
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Weight (gm)")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount (₹)")
        self.billable_checkbox = QCheckBox("Billable")

        new_item_form.addRow("Weight:", self.weight_input)
        new_item_form.addRow("Amount:", self.amount_input)
        new_item_form.addRow("", self.billable_checkbox)

        new_item_layout.addLayout(new_item_form)
        forms_layout.addWidget(new_item_card)

        # Old Item Form Card
        old_item_card = QFrame()
        old_item_card.setStyleSheet(new_item_card.styleSheet())
        old_item_layout = QVBoxLayout(old_item_card)
        old_item_layout.setContentsMargins(10, 10, 10, 10)
        old_item_layout.setSpacing(6)

        old_item_header = QLabel("Old Item")
        old_item_header.setStyleSheet("font-weight: bold; font-size: 11px; color: #2c3e50;")
        old_item_layout.addWidget(old_item_header)

        old_item_form = QFormLayout()
        old_item_form.setSpacing(6)
        old_item_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        old_item_form.setContentsMargins(0, 0, 0, 0)

        self.old_item_type_combo = QComboBox()
        self.old_item_type_combo.addItems(["Gold", "Silver"])
        self.old_weight_input = QLineEdit()
        self.old_weight_input.setPlaceholderText("Weight (gm)")
        self.old_amount_input = QLineEdit()
        self.old_amount_input.setPlaceholderText("Amount (₹)")

        old_item_form.addRow("Type:", self.old_item_type_combo)
        old_item_form.addRow("Weight:", self.old_weight_input)
        old_item_form.addRow("Amount:", self.old_amount_input)

        old_item_layout.addLayout(old_item_form)
        forms_layout.addWidget(old_item_card)

        quick_entry_layout.addWidget(forms_container)

        # Add Item Buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)

        add_new_item_btn = QPushButton("Add New Item")
        add_old_item_btn = QPushButton("Add Old Item")
        
        for btn in [add_new_item_btn, add_old_item_btn]:
            btn.setStyleSheet("""
            QPushButton {
                    background-color: #1877f2;
                color: white;
                border: none;
                    padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                    font-size: 11px;
            }
            QPushButton:hover {
                    background-color: #166fe5;
            }
        """)
            buttons_layout.addWidget(btn)

        add_new_item_btn.clicked.connect(self.add_new_item)
        add_old_item_btn.clicked.connect(self.add_old_item)

        quick_entry_layout.addWidget(buttons_container)
        layout.addWidget(quick_entry_card)

        # Items List Section
        items_list_card = QFrame()
        items_list_card.setStyleSheet(card_style)
        items_list_layout = QVBoxLayout(items_list_card)
        items_list_layout.setContentsMargins(12, 12, 12, 12)
        items_list_layout.setSpacing(6)

        # Items List Header with Tabs
        list_header_container = QWidget()
        list_header_layout = QHBoxLayout(list_header_container)
        list_header_layout.setContentsMargins(0, 0, 0, 0)
        list_header_layout.setSpacing(0)

        new_items_tab = QPushButton("New Items")
        old_items_tab = QPushButton("Old Items")
        
        for tab in [new_items_tab, old_items_tab]:
            tab.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #1a1a1a;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 11px;
                    border-radius: 6px 6px 0 0;
                    border-bottom: 2px solid transparent;
                }
                QPushButton:hover {
                    background-color: #e7f3ff;
                }
                QPushButton[active="true"] {
                    background-color: #1877f2;
                    color: white;
                    border-bottom: 2px solid #1459b3;
                }
            """)
            list_header_layout.addWidget(tab)

        items_list_layout.addWidget(list_header_container)

        # Tables Stack
        tables_stack = QWidget()
        tables_stack_layout = QVBoxLayout(tables_stack)
        tables_stack_layout.setContentsMargins(0, 0, 0, 0)
        tables_stack_layout.setSpacing(0)

        # New Items Table
        self.new_items_table = QTableWidget()
        self.new_items_table.setColumnCount(5)
        self.new_items_table.setHorizontalHeaderLabels(["Item", "Weight", "Amount", "Billable", "Actions"])
        self.new_items_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;      /* Match card border */
                border-radius: 8px;         /* Match card radius */
                font-size: 11px;
                gridline-color: transparent; /* Hide grid lines */
                alternate-background-color: #f8f9fa; /* Subtle alternating row color */
                selection-background-color: #e7f3ff; /* Selection color */
                selection-color: #1a1a1a;
            }
            QTableWidget::item {
                padding: 10px 8px; /* Increased vertical padding */
                border-bottom: 1px solid #f1f2f6; /* Softer row separator */
                color: #1a1a1a;
            }
            /* Remove bottom border for last row */
            QTableWidget::item:last-row {
                border-bottom: none;
            }
            QTableWidget::item:selected {
                background-color: #e7f3ff;
                color: #1a1a1a;
            }
            QHeaderView {
                background-color: #ffffff;
            }
            QHeaderView::section:horizontal {
                background-color: #f8f9fa; /* Light header */
                padding: 10px 8px; /* Adjust padding */
                border: none;
                border-bottom: 1px solid #e4e6eb; /* Header separator */
                font-weight: bold;
                font-size: 11px;
                color: #1a1a1a;
            }
            QHeaderView::section:vertical {
                background-color: #f8f9fa !important; /* Keep this explicit style working */
                color: #1a1a1a !important;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #e4e6eb;
            }
            /* Style delete button within the table */
            QTableWidget QPushButton {
                background-color: #f8f9fa; /* Lighter background */
                color: #e74c3c; /* Red text */
                border: 1px solid #e4e6eb;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QTableWidget QPushButton:hover {
                background-color: #e74c3c;
                color: white;
                border-color: #e74c3c;
            }
        """)
        self.new_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.new_items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.new_items_table.setAlternatingRowColors(True)  # Re-enable alternating rows
        self.new_items_table.setCornerButtonEnabled(False) # Keep corner hidden
        self.new_items_table.setShowGrid(False) # Explicitly hide grid lines
        self.new_items_table.verticalHeader().setVisible(False) # Hide vertical numbers header for cleaner look

        # Explicitly style the vertical header (This approach works - BUT WE HIDE IT NOW)
        # vertical_header = self.new_items_table.verticalHeader()
        # vertical_header.setStyleSheet("""
        #     QHeaderView::section {
        #         background-color: #f8f9fa !important; /* Light background */
        #         color: #1a1a1a !important; /* Dark text */
        #         padding: 8px;
        #         border: none;
        #         border-right: 1px solid #e4e6eb;
        #     }
        # """)

        # Old Items Table
        self.old_items_table = QTableWidget()
        self.old_items_table.setColumnCount(4)
        self.old_items_table.setHorizontalHeaderLabels(["Item", "Weight", "Amount", "Actions"])
        self.old_items_table.setStyleSheet(self.new_items_table.styleSheet())
        self.old_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.old_items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.old_items_table.setVisible(False)  # Hide old items table initially

        tables_stack_layout.addWidget(self.new_items_table)
        tables_stack_layout.addWidget(self.old_items_table)

        items_list_layout.addWidget(tables_stack)
        layout.addWidget(items_list_card)

        # Summary and Payment Container
        summary_payment_container = QWidget()
        summary_payment_layout = QHBoxLayout(summary_payment_container)
        summary_payment_layout.setContentsMargins(0, 0, 0, 0)
        summary_payment_layout.setSpacing(12)

        # Transaction Summary Section
        summary_card = QFrame()
        summary_card.setStyleSheet(card_style)
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(12, 12, 12, 8)
        summary_layout.setSpacing(6)

        # Summary Header
        summary_header = QLabel("Transaction Summary")
        summary_header.setStyleSheet("font-weight: bold; font-size: 11px; color: #2c3e50;")
        summary_layout.addWidget(summary_header)

        # Summary Details
        summary_details = QFormLayout()
        summary_details.setSpacing(6)
        summary_details.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        summary_details.setContentsMargins(0, 0, 0, 0)

        self.new_items_total_label = QLabel("₹0.00")
        self.old_items_total_label = QLabel("₹0.00")
        self.total_to_pay_label = QLabel("₹0.00")
        self.total_to_pay_label.setStyleSheet("font-weight: bold; color: #2c3e50;")

        summary_details.addRow("New Items:", self.new_items_total_label)
        summary_details.addRow("Old Items:", self.old_items_total_label)
        summary_details.addRow("Total:", self.total_to_pay_label)

        summary_layout.addLayout(summary_details)
        summary_payment_layout.addWidget(summary_card)

        # Payment Section
        payment_card = QFrame()
        payment_card.setStyleSheet(card_style)
        payment_layout = QVBoxLayout(payment_card)
        payment_layout.setContentsMargins(12, 12, 12, 8)
        payment_layout.setSpacing(6)

        # Payment Header
        payment_header = QLabel("Payment Details")
        payment_header.setStyleSheet("font-weight: bold; font-size: 11px; color: #2c3e50;")
        payment_layout.addWidget(payment_header)

        # Payment Form
        payment_form = QFormLayout()
        payment_form.setSpacing(6)
        payment_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        payment_form.setContentsMargins(0, 0, 0, 0)

        self.cash_amount = QLineEdit()
        self.cash_amount.setPlaceholderText("Cash (₹)")
        self.card_amount = QLineEdit()
        self.card_amount.setPlaceholderText("Card (₹)")
        self.upi_amount = QLineEdit()
        self.upi_amount.setPlaceholderText("UPI (₹)")

        payment_form.addRow("Cash:", self.cash_amount)
        payment_form.addRow("Card:", self.card_amount)
        payment_form.addRow("UPI:", self.upi_amount)

        payment_layout.addLayout(payment_form)

        # Net Paid Label
        self.net_paid_label = QLabel("Net Paid: ₹0.00")
        self.net_paid_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.net_paid_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        payment_layout.addWidget(self.net_paid_label)

        summary_payment_layout.addWidget(payment_card)
        layout.addWidget(summary_payment_container)

        # Save Transaction Button
        save_btn = QPushButton("Save Transaction")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #42b72a;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #36a420;
            }
        """)
        save_btn.clicked.connect(self.save_transaction)
        layout.addWidget(save_btn)

        # Connect tab buttons
        def switch_items_list_tab(active_tab):
            new_items_tab.setProperty("active", active_tab == new_items_tab)
            old_items_tab.setProperty("active", active_tab == old_items_tab)
            self.new_items_table.setVisible(active_tab == new_items_tab)
            self.old_items_table.setVisible(active_tab == old_items_tab)
            # Force style update
            new_items_tab.style().unpolish(new_items_tab)
            old_items_tab.style().unpolish(old_items_tab)
            new_items_tab.style().polish(new_items_tab)
            old_items_tab.style().polish(old_items_tab)

        new_items_tab.clicked.connect(lambda: switch_items_list_tab(new_items_tab))
        old_items_tab.clicked.connect(lambda: switch_items_list_tab(old_items_tab))

        # Set initial states
        new_items_tab.setProperty("active", True)
        new_items_tab.style().unpolish(new_items_tab)
        new_items_tab.style().polish(new_items_tab)

        return left_pane
        
    def create_right_pane(self) -> QWidget:
        """Create the right pane containing the transaction list and summary"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # Summary Section
        summary_group = QGroupBox("Daily Summary")
        summary_group.setMaximumHeight(180)
        summary_group.setStyleSheet("""
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 8px;
                margin-top: 5px;
                padding: 2px;
            }
            QGroupBox::title {
                color: #1a1a1a;
                font-size: 13px;
                font-weight: bold;
                padding: 0 5px;
            }
        """)
        
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(8)
        summary_layout.setContentsMargins(8, 15, 8, 8)
        
        # Left side: Three cards for items
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)
        
        # New Items Card
        new_items_card = QFrame()
        new_items_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
            }
            QLabel {
                color: #1a1a1a;
            }
            QLabel[class="header"] {
                font-size: 12px;
                font-weight: bold;
                color: #1a1a1a;
                border-bottom: 1px solid #e4e6eb;
                padding-bottom: 5px;
                margin-bottom: 5px;
            }
            QLabel[class="content"] {
                font-size: 12px;
                color: #1a1a1a;
            }
        """)
        new_items_layout = QVBoxLayout(new_items_card)
        new_items_layout.setSpacing(3)
        new_items_layout.setContentsMargins(12, 10, 12, 10)
        
        new_items_header = QLabel("New Items")
        new_items_header.setProperty("class", "header")
        new_items_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        new_items_layout.addWidget(new_items_header)
        
        self.gold_weight_label = QLabel("Gold: 0.00 gm")
        self.silver_weight_label = QLabel("Silver: 0.00 gm")
        self.gold_weight_label.setProperty("class", "content")
        self.silver_weight_label.setProperty("class", "content")
        new_items_layout.addWidget(self.gold_weight_label)
        new_items_layout.addWidget(self.silver_weight_label)
        
        # Old Items Card
        old_items_card = QFrame()
        old_items_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
            }
            QLabel {
                color: #1a1a1a;
            }
            QLabel[class="header"] {
                font-size: 12px;
                font-weight: bold;
                color: #1a1a1a;
                border-bottom: 1px solid #e4e6eb;
                padding-bottom: 5px;
                margin-bottom: 5px;
            }
            QLabel[class="content"] {
                font-size: 12px;
                color: #1a1a1a;
            }
        """)
        old_items_layout = QVBoxLayout(old_items_card)
        old_items_layout.setSpacing(3)
        old_items_layout.setContentsMargins(12, 10, 12, 10)
        
        old_items_header = QLabel("Old Items")
        old_items_header.setProperty("class", "header")
        old_items_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        old_items_layout.addWidget(old_items_header)
        
        self.old_gold_label = QLabel("Gold: 0.00 gm")
        self.old_silver_label = QLabel("Silver: 0.00 gm")
        self.old_gold_label.setProperty("class", "content")
        self.old_silver_label.setProperty("class", "content")
        old_items_layout.addWidget(self.old_gold_label)
        old_items_layout.addWidget(self.old_silver_label)
        
        # Billable Items Card
        billable_card = QFrame()
        billable_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
            }
            QLabel {
                color: #1a1a1a;
            }
            QLabel[class="header"] {
                font-size: 12px;
                font-weight: bold;
                color: #1a1a1a;
                border-bottom: 1px solid #e4e6eb;
                padding-bottom: 5px;
                margin-bottom: 5px;
            }
            QLabel[class="content"] {
                font-size: 12px;
                color: #1a1a1a;
            }
            QLabel[class="amount"] {
                font-size: 12px;
                font-weight: bold;
                color: #1a1a1a;
            }
        """)
        billable_layout = QVBoxLayout(billable_card)
        billable_layout.setSpacing(3)
        billable_layout.setContentsMargins(12, 10, 12, 10)
        
        billable_header = QLabel("Billable Items")
        billable_header.setProperty("class", "header")
        billable_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        billable_layout.addWidget(billable_header)
        
        self.billable_gold_label = QLabel("Gold: 0.00 gm")
        self.billable_silver_label = QLabel("Silver: 0.00 gm")
        self.billable_amount_label = QLabel("Amount: ₹0.00")
        self.billable_gold_label.setProperty("class", "content")
        self.billable_silver_label.setProperty("class", "content")
        self.billable_amount_label.setProperty("class", "amount")
        billable_layout.addWidget(self.billable_gold_label)
        billable_layout.addWidget(self.billable_silver_label)
        billable_layout.addWidget(self.billable_amount_label)
        
        # Add cards to layout
        cards_layout.addWidget(new_items_card, stretch=1)
        cards_layout.addWidget(old_items_card, stretch=1)
        cards_layout.addWidget(billable_card, stretch=1)
        
        # Payment Details Card
        payment_card = QFrame()
        payment_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
            }
            QLabel {
                color: #1a1a1a;
            }
            QLabel[class="header"] {
                font-size: 12px;
                font-weight: bold;
                color: #1a1a1a;
                border-bottom: 1px solid #e4e6eb;
                padding-bottom: 5px;
                margin-bottom: 5px;
            }
            QLabel[class="content"] {
                font-size: 12px;
                color: #1a1a1a;
            }
            QLabel[class="total"] {
                font-size: 15px;
                font-weight: bold;
                color: #1a1a1a;
                padding-top: 5px;
                border-top: 1px solid #e4e6eb;
            }
        """)
        payment_layout = QVBoxLayout(payment_card)
        payment_layout.setSpacing(3)
        payment_layout.setContentsMargins(12, 10, 12, 10)
        
        payment_header = QLabel("Payment Details")
        payment_header.setProperty("class", "header")
        payment_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.cash_total_label = QLabel("Cash: ₹0.00")
        self.card_total_label = QLabel("Card: ₹0.00")
        self.upi_total_label = QLabel("UPI: ₹0.00")
        self.cash_total_label.setProperty("class", "content")
        self.card_total_label.setProperty("class", "content")
        self.upi_total_label.setProperty("class", "content")
        
        self.total_amount_label = QLabel("₹0.00")
        self.total_amount_label.setProperty("class", "total")
        self.total_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        payment_layout.addWidget(payment_header)
        payment_layout.addWidget(self.cash_total_label)
        payment_layout.addWidget(self.card_total_label)
        payment_layout.addWidget(self.upi_total_label)
        payment_layout.addWidget(self.total_amount_label)
        
        # Add all layouts to summary layout
        summary_layout.addLayout(cards_layout, stretch=4)
        summary_layout.addWidget(payment_card, stretch=1)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Transaction List Section
        transaction_header = QWidget()
        transaction_header_layout = QHBoxLayout(transaction_header)
        transaction_header_layout.setContentsMargins(0, 5, 0, 5)
        
        # Transaction Label
        transaction_label = QLabel("Transaction History")
        transaction_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        transaction_header_layout.addWidget(transaction_label)
        
        # Add spacer
        transaction_header_layout.addStretch()
        
        # Date Selection Widget
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(5)
        
        # From Date
        from_label = QLabel("From:")
        from_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 12px;
            }
        """)
        date_layout.addWidget(from_label)
        
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate.currentDate())
        self.from_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.from_date_edit.setStyleSheet("""
            QDateEdit {
                background-color: #ffffff;
                border: 1px solid #e4e6eb;
                border-radius: 6px;
                padding: 8px;
                min-width: 120px;
                font-size: 12px;
                color: #1a1a1a;
            }
            QDateEdit:focus {
                border: 1px solid #1877f2;
                background-color: #ffffff;
            }
            QDateEdit::drop-down {
                border: none;
                width: 25px;
                background-color: #ffffff;
                border-left: 1px solid #e4e6eb;
            }
            QDateEdit::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM1877f2IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iMyIgeT0iNCIgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiByeD0iMiIgcnk9IjIiLz48bGluZSB4MT0iMTYiIHkxPSIyIiB4Mj0iMTYiIHkyPSI2Ii8+PHN0eWxlPi50ZXh0LWFsaWduLXJwb3Mge2ZvbnQtc2l6ZToxMnB4O308L3N0eWxlPjwvc3ZnPg==);
                width: 16px;
                height: 16px;
            }
            QDateEdit::drop-down:hover {
                background-color: #e7f3ff;
            }
        """)
        date_layout.addWidget(self.from_date_edit)
        
        # To Date
        to_label = QLabel("To:")
        to_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 12px;
            }
        """)
        date_layout.addWidget(to_label)
        
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.to_date_edit.setStyleSheet(self.from_date_edit.styleSheet())
        date_layout.addWidget(self.to_date_edit)
        
        # Load Data Button
        load_button = QPushButton("Load")
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
        """)
        load_button.clicked.connect(self.load_date_range)
        date_layout.addWidget(load_button)
        
        transaction_header_layout.addWidget(date_widget)
        layout.addWidget(transaction_header)
        
        # Transaction Table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(8)
        self.transaction_table.setHorizontalHeaderLabels([
            "Date", "Time", "Items", "New Weight", "Old Weight", "Amount", "Type", "Actions"
        ])
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transaction_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #dcdde1;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                selection-background-color: #f5f6fa;
                selection-color: #2c3e50;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f2f6;
            }
            QTableWidget::item:selected {
                background-color: #f5f6fa;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dcdde1;
                font-weight: bold;
            }
            QTableWidget::item[type="Gold"] {
                color: #c0392b;
                font-weight: bold;
            }
            QTableWidget::item[type="Silver"] {
                color: #7f8c8d;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.transaction_table)
        
        # Buttons Container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 5, 0, 0)
        
        # Billable Summary Button
        billable_summary_button = QPushButton("Show Billable Summary")
        billable_summary_button.setStyleSheet("""
            QPushButton {
                background-color: #42b72a;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #36a420;
            }
        """)
        billable_summary_button.clicked.connect(self.show_billable_summary)
        
        # Add Print button
        print_btn = QPushButton("Print List")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
        """)
        print_btn.clicked.connect(self.print_transaction_list)
        
        # Add Export button
        export_btn = QPushButton("Export to Excel")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
        """)
        export_btn.clicked.connect(self.export_to_excel)
        
        buttons_layout.addWidget(billable_summary_button)
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(export_btn)
        layout.addWidget(buttons_container)
        
        return right_widget
            
    def update_transaction_table(self, transactions: List[Dict]):
        """Update the transaction table with the given transactions"""
        try:
            self.logger.info("Updating transaction table")
            self.transaction_table.setRowCount(0)
            
            # Configure table settings
            self.transaction_table.setShowGrid(True)
            self.transaction_table.setAlternatingRowColors(True)
            self.transaction_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.transaction_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            
            # Set column count and headers
            self.transaction_table.setColumnCount(8)
            self.transaction_table.setHorizontalHeaderLabels([
                "Date", "Time", "Items", "New Weight", "Old Weight", "Amount", "Type", "Actions"
            ])
            
            # Apply enhanced table styling
            self.transaction_table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e4e6eb;
                    border-radius: 8px;
                    gridline-color: #e4e6eb;
                }
                QTableWidget::item {
                    padding: 12px 8px;
                    border-bottom: 1px solid #f1f2f6;
                }
                QTableWidget::item:selected {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    padding: 12px 8px;
                    border: none;
                    border-bottom: 2px solid #e4e6eb;
                    font-weight: bold;
                    font-size: 13px;
                }
                QTableWidget::item[type="Gold"] {
                    color: #d35400;
                    font-weight: bold;
                }
                QTableWidget::item[type="Silver"] {
                    color: #7f8c8d;
                    font-weight: bold;
                }
            """)
            
            for transaction in transactions:
                self.logger.debug(f"Adding transaction to table: {transaction}")
                row = self.transaction_table.rowCount()
                self.transaction_table.insertRow(row)
                
                # Format date from string
                date_str = transaction['date']
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Date column with custom formatting
                date_item = QTableWidgetItem(date_obj.strftime("%d %b %Y"))
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.transaction_table.setItem(row, 0, date_item)
                
                # Time column with custom formatting
                time_item = QTableWidgetItem(date_obj.strftime("%I:%M %p"))
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.transaction_table.setItem(row, 1, time_item)
                
                # Process items with better formatting
                items_text = []
                for item in transaction['items']:
                    items_text.append(f"{item['item_name']}\n₹{item['amount']:.2f}")
                
                # Calculate new items weight
                new_weight = sum(item['weight'] for item in transaction['items'])
                
                # Process old items with better formatting
                old_items_text = []
                old_weight = 0
                if 'old_items' in transaction and transaction['old_items']:
                    old_items_text.append("─" * 20)  # Separator line
                    for item in transaction['old_items']:
                        old_items_text.append(f"Old {item['item_type']}\n₹{item['amount']:.2f}")
                        old_weight += item['weight']
                
                # Items column with improved layout
                items_text.extend(old_items_text)
                items_item = QTableWidgetItem("\n".join(items_text))
                items_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.transaction_table.setItem(row, 2, items_item)
                
                # Weight columns with consistent formatting
                new_weight_item = QTableWidgetItem(f"{new_weight:.2f} gm")
                new_weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.transaction_table.setItem(row, 3, new_weight_item)
                
                old_weight_item = QTableWidgetItem(f"{old_weight:.2f} gm" if old_weight > 0 else "—")
                old_weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.transaction_table.setItem(row, 4, old_weight_item)
                
                # Amount column with currency formatting
                amount_item = QTableWidgetItem(f"₹{transaction['total_amount']:.2f}")
                amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.transaction_table.setItem(row, 5, amount_item)
                
                # Type column with color coding
                if transaction['items']:
                    type_item = QTableWidgetItem(transaction['items'][0]['item_type'])
                    type_item.setData(Qt.ItemDataRole.UserRole, "type")
                    type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.transaction_table.setItem(row, 6, type_item)
                else:
                    type_item = QTableWidgetItem("—")
                    type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.transaction_table.setItem(row, 6, type_item)
                
                # Action buttons with improved styling and layout
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(8, 4, 8, 4)
                actions_layout.setSpacing(8)
                
                edit_button = QPushButton("Edit")
                edit_button.setFixedSize(70, 28)
                edit_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f1c40f;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #f39c12;
                    }
                    QPushButton:pressed {
                        background-color: #e67e22;
                    }
                """)
                edit_button.clicked.connect(lambda checked, t=transaction: self.edit_transaction(t))
                
                delete_button = QPushButton("Delete")
                delete_button.setFixedSize(70, 28)
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                    QPushButton:pressed {
                        background-color: #a93226;
                    }
                """)
                delete_button.clicked.connect(lambda checked, t=transaction: self.delete_transaction(t))
                
                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.addStretch()
                
                self.transaction_table.setCellWidget(row, 7, actions_widget)
                
                # Set row height to accommodate content
                self.transaction_table.setRowHeight(row, max(60, self.transaction_table.rowHeight(row)))
            
            # Adjust column widths
            self.transaction_table.setColumnWidth(0, 100)  # Date
            self.transaction_table.setColumnWidth(1, 90)   # Time
            self.transaction_table.setColumnWidth(2, 250)  # Items
            self.transaction_table.setColumnWidth(3, 100)  # New Weight
            self.transaction_table.setColumnWidth(4, 100)  # Old Weight
            self.transaction_table.setColumnWidth(5, 100)  # Amount
            self.transaction_table.setColumnWidth(6, 80)   # Type
            self.transaction_table.setColumnWidth(7, 180)  # Actions
            
            # Force style update
            self.transaction_table.style().unpolish(self.transaction_table)
            self.transaction_table.style().polish(self.transaction_table)
            
            self.logger.info("Transaction table updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating transaction table: {str(e)}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Error updating transaction table: {str(e)}")
        
    def add_new_item(self):
        """Add a new item to the new items list"""
        try:
            # Get item details
            item_text = self.item_code_input.text()
            if not item_text:
                QMessageBox.warning(self, "Error", "Please enter an item code")
                return
                
            # Split the text to get code and name
            parts = item_text.split(" - ")
            if len(parts) != 2:
                QMessageBox.warning(self, "Error", "Invalid item format")
                return
                
            code, name = parts
            if code not in self.ITEM_CODES:
                QMessageBox.warning(self, "Error", "Invalid item code")
                return
                
            weight = float(self.weight_input.text())
            amount = float(self.amount_input.text())
            is_billable = self.billable_checkbox.isChecked()
            
            # Add to table
            row = self.new_items_table.rowCount()
            self.new_items_table.insertRow(row)
            
            self.new_items_table.setItem(row, 0, QTableWidgetItem(item_text))
            self.new_items_table.setItem(row, 1, QTableWidgetItem(f"{weight:.2f} gm"))
            self.new_items_table.setItem(row, 2, QTableWidgetItem(f"₹{amount:.2f}"))
            self.new_items_table.setItem(row, 3, QTableWidgetItem("Yes" if is_billable else "No"))
            
            # Add delete button
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_button.clicked.connect(lambda: self.delete_new_item(row))
            
            self.new_items_table.setCellWidget(row, 4, delete_button)
            
            # Clear inputs
            self.item_code_input.clear()
            self.weight_input.clear()
            self.amount_input.clear()
            
            # Update totals
            self.update_totals()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", "Please enter valid weight and amount")
            
    def add_old_item(self):
        """Add an old item to the old items list"""
        try:
            # Get item details
            item_type = self.old_item_type_combo.currentText()
            weight = float(self.old_weight_input.text())
            amount = float(self.old_amount_input.text())
            
            # Add to table
            row = self.old_items_table.rowCount()
            self.old_items_table.insertRow(row)
            
            self.old_items_table.setItem(row, 0, QTableWidgetItem(item_type))
            self.old_items_table.setItem(row, 1, QTableWidgetItem(f"{weight:.2f} gm"))
            self.old_items_table.setItem(row, 2, QTableWidgetItem(f"₹{amount:.2f}"))
            
            # Add delete button
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_button.clicked.connect(lambda: self.delete_old_item(row))
            
            self.old_items_table.setCellWidget(row, 3, delete_button)
            
            # Clear inputs
            self.old_weight_input.clear()
            self.old_amount_input.clear()
            
            # Update totals
            self.update_totals()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", "Please enter valid weight and amount")
            
    def delete_new_item(self, row):
        """Delete a new item from the list"""
        self.new_items_table.removeRow(row)
        self.update_totals()
        
    def delete_old_item(self, row):
        """Delete an old item from the list"""
        self.old_items_table.removeRow(row)
        self.update_totals()
        
    def update_totals(self):
        """Update all total amounts"""
        # Calculate new items total
        new_total = 0.0
        for row in range(self.new_items_table.rowCount()):
            amount_text = self.new_items_table.item(row, 2).text()
            amount = float(amount_text.replace('₹', ''))
            new_total += amount
            
        # Calculate old items total
        old_total = 0.0
        for row in range(self.old_items_table.rowCount()):
            amount_text = self.old_items_table.item(row, 2).text()
            amount = float(amount_text.replace('₹', ''))
            old_total += amount
            
        # Update labels
        self.new_items_total_label.setText(f"New Items Total: ₹{new_total:.2f}")
        self.old_items_total_label.setText(f"Old Items Total: ₹{old_total:.2f}")
        self.total_to_pay_label.setText(f"Total to Pay: ₹{new_total - old_total:.2f}")
        
    def save_transaction(self):
        """Save all items as a transaction"""
        try:
            # Create transaction data dictionary
            transaction_data = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'cash_amount': float(self.cash_amount.text() or 0),
                'card_amount': float(self.card_amount.text() or 0),
                'upi_amount': float(self.upi_amount.text() or 0),
                'net_amount_paid': float(self.net_paid_label.text().replace("Net Paid: ₹", "") or 0),
                'comments': "",  # Add comments field if needed
                'total_amount': 0  # Will be calculated from items
            }

            # Process new items
            items_data = []
            total_amount = 0
            for row in range(self.new_items_table.rowCount()):
                item_text = self.new_items_table.item(row, 0).text()
                code = item_text.split(" - ")[0]
                name = item_text.split(" - ")[1]
                weight = float(self.new_items_table.item(row, 1).text().replace(' gm', ''))
                amount = float(self.new_items_table.item(row, 2).text().replace('₹', ''))
                is_billable = self.new_items_table.item(row, 3).text() == "Yes"
                
                item_info = self.ITEM_CODES[code]
                items_data.append({
                    'item_name': name,
                    'item_type': item_info['type'],
                    'is_billable': is_billable,
                    'weight': weight,
                    'amount': amount
                })
                total_amount += amount
            
            # Process old items
            old_items_data = []
            for row in range(self.old_items_table.rowCount()):
                item_type = self.old_items_table.item(row, 0).text()
                weight = float(self.old_items_table.item(row, 1).text().replace(' gm', ''))
                amount = float(self.old_items_table.item(row, 2).text().replace('₹', ''))
                
                old_items_data.append({
                    'item_type': item_type,
                    'weight': weight,
                    'amount': amount
                })
                total_amount -= amount  # Subtract old items amount from total
            
            # Update total amount in transaction data
            transaction_data['total_amount'] = total_amount
            
            # Save transaction to database
            self.db.add_transaction(transaction_data, items_data, old_items_data)
            
            # Clear all
            self.new_items_table.setRowCount(0)
            self.old_items_table.setRowCount(0)
            self.clear_form()
            self.update_totals()
            
            # Update main table
            self.load_today_data()
            
            QMessageBox.information(self, "Success", "Transaction saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving transaction: {str(e)}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Error saving transaction: {str(e)}")

    def clear_form(self):
        """Clear all input fields"""
        # Clear new item inputs
        self.weight_input.clear()
        self.amount_input.clear()
        self.billable_checkbox.setChecked(True)
        
        # Clear old item inputs
        self.old_weight_input.clear()
        self.old_amount_input.clear()
        
        # Clear payment inputs
        self.cash_amount.clear()
        self.card_amount.clear()
        self.upi_amount.clear()
        self.net_paid_label.setText("Net Paid: ₹0.00")
        
        # Clear tables
        self.new_items_table.setRowCount(0)
        self.old_items_table.setRowCount(0)
        
        # Update totals
        self.update_totals()
        
        # Update status
        self.status_bar.showMessage("Form cleared", 3000)
        
    def edit_transaction(self, transaction: Dict):
        """Edit an existing transaction"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Transaction")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        
        # Create main layout
        main_layout = QVBoxLayout(dialog)
        
        # Transaction details section
        details_group = QGroupBox("Transaction Details")
        details_layout = QFormLayout()
        
        # Payment fields
        cash_input = QLineEdit(str(transaction['cash_amount']))
        card_input = QLineEdit(str(transaction['card_amount']))
        upi_input = QLineEdit(str(transaction['upi_amount']))
        
        details_layout.addRow("Cash Amount:", cash_input)
        details_layout.addRow("Card Amount:", card_input)
        details_layout.addRow("UPI Amount:", upi_input)
        details_group.setLayout(details_layout)
        main_layout.addWidget(details_group)
        
        # Items section
        items_group = QGroupBox("Items")
        items_layout = QVBoxLayout()
        
        # Create table for items
        items_table = QTableWidget()
        items_table.setColumnCount(5)
        items_table.setHorizontalHeaderLabels(["Item", "Type", "Weight (gm)", "Amount", "Billable"])
        
        # Add items to table
        items_table.setRowCount(len(transaction['items']))
        for row, item in enumerate(transaction['items']):
            items_table.setItem(row, 0, QTableWidgetItem(item['item_name']))
            items_table.setItem(row, 1, QTableWidgetItem(item['item_type']))
            items_table.setItem(row, 2, QTableWidgetItem(str(item['weight'])))
            items_table.setItem(row, 3, QTableWidgetItem(str(item['amount'])))
            items_table.setItem(row, 4, QTableWidgetItem("Yes" if item['is_billable'] else "No"))
        
        items_layout.addWidget(items_table)
        items_group.setLayout(items_layout)
        main_layout.addWidget(items_group)
        
        # Old Items section
        if 'old_items' in transaction and transaction['old_items']:
            old_items_group = QGroupBox("Old Items")
            old_items_layout = QVBoxLayout()
            
            # Create table for old items
            old_items_table = QTableWidget()
            old_items_table.setColumnCount(3)
            old_items_table.setHorizontalHeaderLabels(["Type", "Weight (gm)", "Amount"])
            
            # Add old items to table
            old_items_table.setRowCount(len(transaction['old_items']))
            for row, item in enumerate(transaction['old_items']):
                old_items_table.setItem(row, 0, QTableWidgetItem(item['item_type']))
                old_items_table.setItem(row, 1, QTableWidgetItem(str(item['weight'])))
                old_items_table.setItem(row, 2, QTableWidgetItem(str(item['amount'])))
            
            old_items_layout.addWidget(old_items_table)
            old_items_group.setLayout(old_items_layout)
            main_layout.addWidget(old_items_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
        # Style the dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #dcdde1;
                border-radius: 3px;
                background-color: white;
            }
            QTableWidget {
                border: 1px solid #dcdde1;
                background-color: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Connect buttons
        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Update transaction data
                transaction['cash_amount'] = float(cash_input.text())
                transaction['card_amount'] = float(card_input.text())
                transaction['upi_amount'] = float(upi_input.text())
                transaction['net_amount_paid'] = (transaction['cash_amount'] + 
                                                transaction['card_amount'] + 
                                                transaction['upi_amount'])
                
                # Update items
                updated_items = []
                for row in range(items_table.rowCount()):
                    item = {
                        'item_name': items_table.item(row, 0).text(),
                        'item_type': items_table.item(row, 1).text(),
                        'weight': float(items_table.item(row, 2).text()),
                        'amount': float(items_table.item(row, 3).text()),
                        'is_billable': items_table.item(row, 4).text() == "Yes"
                    }
                    updated_items.append(item)
                
                # Update old items if they exist
                updated_old_items = []
                if 'old_items' in transaction and transaction['old_items']:
                    for row in range(old_items_table.rowCount()):
                        old_item = {
                            'item_type': old_items_table.item(row, 0).text(),
                            'weight': float(old_items_table.item(row, 1).text()),
                            'amount': float(old_items_table.item(row, 2).text())
                        }
                        updated_old_items.append(old_item)
                
                # Calculate total amount
                total_amount = sum(item['amount'] for item in updated_items)
                total_amount -= sum(item['amount'] for item in updated_old_items)
                transaction['total_amount'] = total_amount
                
                # Save to database
                self.db.update_transaction(transaction['id'], transaction, updated_items, updated_old_items)
                
                # Update UI
                self.load_today_data()
                
                QMessageBox.information(self, "Success", "Transaction updated successfully")
                
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error updating transaction: {str(e)}")
                
    def delete_transaction(self, transaction: Dict):
        """Delete a transaction"""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this transaction?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete from database
                self.db.delete_transaction(transaction['id'])
                
                # Reload data
                self.load_today_data()
                
                # Show success message
                QMessageBox.information(self, "Success", "Transaction deleted successfully")
                self.status_bar.showMessage("Transaction deleted successfully", 3000)
                
        except Exception as e:
            self.logger.error(f"Error deleting transaction: {str(e)}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Error deleting transaction: {str(e)}")

    def load_data(self):
        """Load transactions for a specific date"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Data")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #dcdde1;
                border-radius: 3px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """)
        dialog_layout = QFormLayout()
        
        date_input = QLineEdit()
        date_input.setPlaceholderText("YYYY-MM-DD")
        dialog_layout.addRow("Date:", date_input)
        
        buttons_layout = QHBoxLayout()
        load_button = QPushButton("Load")
        cancel_button = QPushButton("Cancel")
        
        buttons_layout.addWidget(load_button)
        buttons_layout.addWidget(cancel_button)
        dialog_layout.addRow(buttons_layout)
        
        dialog.setLayout(dialog_layout)
        
        # Connect signals
        load_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                date = datetime.strptime(date_input.text(), "%Y-%m-%d").date()
                transactions = self.db.get_transactions_by_date(date)
                self.update_transaction_table(transactions)
                self.update_summary(transactions)
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Invalid date format: {str(e)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error loading data: {str(e)}")
                
    def export_to_excel(self):
        """Export transactions to Excel"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export to Excel",
                "",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                exporter = ExcelExporter(self.db.db_path)
                exporter.export_transactions(file_path)
                QMessageBox.information(self, "Success", "Data exported successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error exporting data: {str(e)}")
            
    def export_to_csv(self):
        """Export transactions to CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export to CSV",
                "",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                exporter = ExcelExporter(self.db.db_path)
                exporter.export_transactions_csv(file_path)
                QMessageBox.information(self, "Success", "Data exported successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error exporting data: {str(e)}")
            
    def backup_database(self):
        """Create a manual database backup"""
        try:
            self.backup_manager.create_backup()
            QMessageBox.information(self, "Success", "Database backup created successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error creating backup: {str(e)}")
            
    def restore_database(self):
        """Restore database from backup"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Backup File",
                "",
                "Backup Files (*.db)"
            )
            
            if file_path:
                self.backup_manager.restore_backup(file_path)
                self.load_today_data()
                QMessageBox.information(self, "Success", "Database restored successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error restoring backup: {str(e)}")
            
    def generate_daily_report(self):
        """Generate daily report"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Daily Report",
                "",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                self.analytics.generate_daily_report(file_path)
                QMessageBox.information(self, "Success", "Daily report generated successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generating report: {str(e)}")
            
    def generate_monthly_report(self):
        """Generate monthly report"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Monthly Report",
                "",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                self.analytics.generate_monthly_report(file_path)
                QMessageBox.information(self, "Success", "Monthly report generated successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generating report: {str(e)}")

    def calculate_net_paid(self):
        """Calculate and update the net paid amount"""
        try:
            cash = float(self.cash_amount.text() or 0)
            card = float(self.card_amount.text() or 0)
            upi = float(self.upi_amount.text() or 0)
            net_paid = cash + card + upi
            self.net_paid_label.setText(f"Net Paid: ₹{net_paid:.2f}")
        except ValueError:
            self.net_paid_label.setText("Net Paid: ₹0.00")

    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Save transaction shortcut (Ctrl+S)
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_transaction)
        
        # Clear form shortcut (Ctrl+R)
        clear_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        clear_shortcut.activated.connect(self.clear_form)
        
        # Load data shortcut (Ctrl+L)
        load_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        load_shortcut.activated.connect(self.load_data)
        
        # Export to Excel shortcut (Ctrl+E)
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_to_excel)

    def setup_auto_save(self):
        """Set up auto-save functionality"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(5 * 60 * 1000)  # Auto-save every 5 minutes

    def setup_auto_backup(self):
        """Set up automatic database backup"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(self.db.db_path), 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Create a backup every day at midnight
            self.backup_timer = QTimer()
            self.backup_timer.timeout.connect(self.check_and_backup)
            self.backup_timer.start(60 * 1000)  # Check every minute
            
            self.logger.info("Auto-backup system initialized")
        except Exception as e:
            self.logger.error(f"Error setting up auto-backup: {str(e)}")
    
    def check_and_backup(self):
        """Check if it's time for a daily backup"""
        try:
            current_time = datetime.now()
            if current_time.hour == 0 and current_time.minute == 0:
                self.backup_manager.create_backup()
                self.logger.info("Daily auto-backup completed")
        except Exception as e:
            self.logger.error(f"Error during auto-backup: {str(e)}")

    def auto_save(self):
        """Perform auto-save"""
        try:
            self.backup_manager.create_backup()
            self.status_bar.showMessage("Auto-saved successfully", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Auto-save failed: {str(e)}", 5000)

    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Perform final backup before closing
            self.backup_manager.create_backup()
            self.logger.info("Final backup created before closing")
            event.accept()
        except Exception as e:
            self.logger.error(f"Error during final backup: {str(e)}")
            reply = QMessageBox.question(
                self,
                "Backup Failed",
                "Failed to create final backup. Close anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()

    def show_billable_summary(self):
        """Show billable summary dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Billable Summary")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                gridline-color: #dcdde1;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f1f2f6;
                background-color: white;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dcdde1;
                font-weight: bold;
                color: #2c3e50;
            }
            QHeaderView::section:first {
                border-top-left-radius: 5px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Get current date from the first row of transaction table, or use today's date if empty
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.transaction_table.rowCount() > 0:
            current_date = self.transaction_table.item(0, 0).text()
        
        # Add date label
        date_label = QLabel(f"Summary for date: {current_date}")
        date_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(date_label)
        
        # Create tables for billable and non-billable items
        billable_table = QTableWidget()
        billable_table.setColumnCount(6)  # Added one column for count
        billable_table.setHorizontalHeaderLabels(["Code", "Name", "Type", "Count", "Weight", "Amount"])
        billable_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        non_billable_table = QTableWidget()
        non_billable_table.setColumnCount(6)  # Added one column for count
        non_billable_table.setHorizontalHeaderLabels(["Code", "Name", "Type", "Count", "Weight", "Amount"])
        non_billable_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Get transactions for the selected date
        transactions = self.db.get_transactions_by_date(current_date)
        
        # Process transactions
        billable_items = {}
        non_billable_items = {}
        
        for transaction in transactions:
            for item in transaction['items']:
                key = (item['item_name'], item['item_type'])
                if item['is_billable']:
                    if key not in billable_items:
                        billable_items[key] = {'count': 0, 'weight': 0, 'amount': 0}
                    billable_items[key]['count'] += 1
                    billable_items[key]['weight'] += item['weight']
                    billable_items[key]['amount'] += item['amount']
                else:
                    if key not in non_billable_items:
                        non_billable_items[key] = {'count': 0, 'weight': 0, 'amount': 0}
                    non_billable_items[key]['count'] += 1
                    non_billable_items[key]['weight'] += item['weight']
                    non_billable_items[key]['amount'] += item['amount']
        
        # Fill billable table
        billable_table.setRowCount(len(billable_items))
        total_billable_count = 0
        total_billable_weight = 0
        total_billable_amount = 0
        for row, ((name, type_), data) in enumerate(billable_items.items()):
            code = next((code for code, info in self.ITEM_CODES.items() 
                        if info['name'] == name and info['type'] == type_), '')
            billable_table.setItem(row, 0, QTableWidgetItem(code))
            billable_table.setItem(row, 1, QTableWidgetItem(name))
            billable_table.setItem(row, 2, QTableWidgetItem(type_))
            billable_table.setItem(row, 3, QTableWidgetItem(str(data['count'])))  # Add count
            billable_table.setItem(row, 4, QTableWidgetItem(f"{data['weight']:.2f} gm"))
            billable_table.setItem(row, 5, QTableWidgetItem(f"₹{data['amount']:.2f}"))
            total_billable_count += data['count']
            total_billable_weight += data['weight']
            total_billable_amount += data['amount']
        
        # Fill non-billable table
        non_billable_table.setRowCount(len(non_billable_items))
        total_non_billable_count = 0
        total_non_billable_weight = 0
        total_non_billable_amount = 0
        for row, ((name, type_), data) in enumerate(non_billable_items.items()):
            code = next((code for code, info in self.ITEM_CODES.items() 
                        if info['name'] == name and info['type'] == type_), '')
            non_billable_table.setItem(row, 0, QTableWidgetItem(code))
            non_billable_table.setItem(row, 1, QTableWidgetItem(name))
            non_billable_table.setItem(row, 2, QTableWidgetItem(type_))
            non_billable_table.setItem(row, 3, QTableWidgetItem(str(data['count'])))  # Add count
            non_billable_table.setItem(row, 4, QTableWidgetItem(f"{data['weight']:.2f} gm"))
            non_billable_table.setItem(row, 5, QTableWidgetItem(f"₹{data['amount']:.2f}"))
            total_non_billable_count += data['count']
            total_non_billable_weight += data['weight']
            total_non_billable_amount += data['amount']
        
        # Add labels and tables to layout
        billable_label = QLabel("Billable Items")
        billable_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        layout.addWidget(billable_label)
        layout.addWidget(billable_table)
        
        # Add billable totals with count
        billable_totals = QLabel(f"Total: {total_billable_count} items, {total_billable_weight:.2f} gm, ₹{total_billable_amount:.2f}")
        billable_totals.setStyleSheet("font-weight: bold; color: #2980b9; margin-top: 5px;")
        layout.addWidget(billable_totals)
        
        non_billable_label = QLabel("Non-Billable Items")
        non_billable_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 20px;")
        layout.addWidget(non_billable_label)
        layout.addWidget(non_billable_table)
        
        # Add non-billable totals with count
        non_billable_totals = QLabel(f"Total: {total_non_billable_count} items, {total_non_billable_weight:.2f} gm, ₹{total_non_billable_amount:.2f}")
        non_billable_totals.setStyleSheet("font-weight: bold; color: #2980b9; margin-top: 5px;")
        layout.addWidget(non_billable_totals)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.setLayout(layout)
        dialog.exec()

    def print_transaction_list(self):
        """Print the transaction list with summary"""
        try:
            from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
            from PyQt6.QtGui import QTextDocument, QPageSize
            from PyQt6.QtCore import QMarginsF
            from PyQt6.QtWidgets import QMessageBox
            
            # Create the document to print
            doc = QTextDocument()
            
            # Get date range for the header
            from_date = self.from_date_edit.text()
            to_date = self.to_date_edit.text()
            date_range = from_date if from_date == to_date else f"{from_date} to {to_date}"
            
            # Create HTML content with CSS styling
            html = """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h2 { color: #2c3e50; text-align: center; margin-bottom: 20px; }
                    h3 { color: #2c3e50; margin-top: 20px; }
                    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                    th { background-color: #f8f9fa; padding: 8px; text-align: left; border: 1px solid #dcdde1; }
                    td { padding: 8px; border: 1px solid #dcdde1; }
                    .summary-table { width: auto; margin-top: 20px; }
                    .summary-table td { border: none; padding: 4px 15px 4px 0; }
                    .summary-header { font-weight: bold; color: #2c3e50; }
                    .total-row { font-weight: bold; background-color: #f8f9fa; }
                </style>
            </head>
            <body>
            """
            
            # Add header with date range
            html += f"<h2>Transaction List - {date_range}</h2>"
            
            # Add transactions table
            html += "<table>"
            html += "<tr><th>Date</th><th>Time</th><th>Items</th><th>New Weight</th><th>Old Weight</th><th>Amount</th><th>Type</th></tr>"
            
            # Add transaction rows
            for row in range(self.transaction_table.rowCount()):
                html += "<tr>"
                # Only include the first 7 columns (excluding the Actions column)
                for col in range(7):
                    item = self.transaction_table.item(row, col)
                    if item:
                        # Replace newlines with <br> for HTML
                        text = item.text().replace('\n', '<br>')
                        html += f"<td>{text}</td>"
                    else:
                        html += "<td>-</td>"
                html += "</tr>"
            
            html += "</table>"
            
            # Add summary section
            html += "<h3>Daily Summary</h3>"
            html += "<table class='summary-table'>"
            
            # New Items
            html += "<tr><td colspan='4' class='summary-header'>New Items</td></tr>"
            html += f"<tr><td>Gold: {self.gold_weight_label.text()}</td>"
            html += f"<td>Silver: {self.silver_weight_label.text()}</td></tr>"
            
            # Old Items
            html += "<tr><td colspan='4' class='summary-header'>Old Items</td></tr>"
            html += f"<tr><td>Gold: {self.old_gold_label.text()}</td>"
            html += f"<td>Silver: {self.old_silver_label.text()}</td></tr>"
            
            # Billable Items
            html += "<tr><td colspan='4' class='summary-header'>Billable Items</td></tr>"
            html += f"<tr><td>Gold: {self.billable_gold_label.text()}</td>"
            html += f"<td>Silver: {self.billable_silver_label.text()}</td></tr>"
            html += f"<tr><td colspan='2'>Amount: {self.billable_amount_label.text()}</td></tr>"
            
            # Payment Details
            html += "<tr><td colspan='4' class='summary-header'>Payment Details</td></tr>"
            html += f"<tr><td>{self.cash_total_label.text()}</td></tr>"
            html += f"<tr><td>{self.card_total_label.text()}</td></tr>"
            html += f"<tr><td>{self.upi_total_label.text()}</td></tr>"
            html += f"<tr><td colspan='2' class='summary-header'>{self.total_amount_label.text()}</td></tr>"
            
            html += "</table>"
            html += "</body></html>"
            
            doc.setHtml(html)
            
            # Create printer
            printer = QPrinter()
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            # Set margins (20mm on each side)
            margins = QMarginsF(20, 20, 20, 20)
            printer.setPageMargins(margins)
            
            # Show print preview dialog
            preview = QPrintPreviewDialog(printer)
            preview.paintRequested.connect(lambda p: doc.print(p))  # Changed from print_ to print
            preview.setWindowTitle("Print Preview - Transaction List")
            
            if preview.exec() == QPrintPreviewDialog.DialogCode.Accepted:
                doc.print(printer)  # Changed from print_ to print
                self.status_bar.showMessage("Document printed successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error printing: {str(e)}")
            self.logger.error(f"Error in print_transaction_list: {str(e)}", exc_info=True)

    def tr(self, key: str) -> str:
        """Get translated text for the given key"""
        return Translations.get_text(key, self.current_language)

    def load_selected_date(self):
        """Load transactions for the selected date"""
        try:
            selected_date = self.date_edit.date().toPyDate()
            transactions = self.db.get_transactions_by_date(selected_date)
            self.update_transaction_table(transactions)
            self.update_summary(transactions)
            self.status_bar.showMessage(f"Loaded data for {selected_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading data: {str(e)}")

    def load_date_range(self):
        """Load transactions for the selected date range"""
        try:
            from_date = self.from_date_edit.date().toPyDate()
            to_date = self.to_date_edit.date().toPyDate()
            
            if from_date > to_date:
                QMessageBox.warning(self, "Error", "From date cannot be later than To date")
                return
            
            transactions = self.db.get_transactions_by_date_range(from_date, to_date)
            self.update_transaction_table(transactions)
            self.update_summary(transactions)
            self.status_bar.showMessage(f"Loaded data from {from_date} to {to_date}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading data: {str(e)}")

    def update_suggestions(self, text):
        """Update the suggestion list based on input text"""
        if not text:
            self.suggestion_popup.hide()
            return
            
        # Filter items based on input
        suggestions = []
        for code, info in self.ITEM_CODES.items():
            if text.upper() in code.upper() or text.upper() in info['name'].upper():
                suggestions.append((code, info))
        
        # Update suggestion list
        self.suggestion_list.clear()
        for code, info in suggestions:
            item = QListWidgetItem(f"{code} - {info['name']}")
            item.setData(Qt.ItemDataRole.UserRole, (code, info))
            self.suggestion_list.addItem(item)
        
        # Show/hide popup based on suggestions
        if suggestions:
            # Position popup below the input field
            pos = self.item_code_input.mapToGlobal(self.item_code_input.rect().bottomLeft())
            self.suggestion_popup.move(pos)
            self.suggestion_popup.resize(self.item_code_input.width(), min(200, len(suggestions) * 25))
            self.suggestion_popup.show()
            # Ensure input field maintains focus
            self.item_code_input.setFocus()
            # Prevent the popup from stealing focus
            self.suggestion_popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            self.suggestion_popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        else:
            self.suggestion_popup.hide()
    
    def select_suggestion(self):
        """Handle selection of a suggestion"""
        current_item = self.suggestion_list.currentItem()
        if current_item:
            code, info = current_item.data(Qt.ItemDataRole.UserRole)
            self.item_code_input.setText(f"{code} - {info['name']}")
            self.suggestion_popup.hide()
            self.weight_input.setFocus()  # Move focus to weight input

    def create_menu_bar(self):
        """Create the menu bar with all necessary menus and actions"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        # Load Data Action
        load_action = file_menu.addAction("Load Data")
        load_action.triggered.connect(self.load_data)
        load_action.setShortcut("Ctrl+L")
        
        # Export Menu
        export_menu = file_menu.addMenu("Export")
        export_excel_action = export_menu.addAction("Export to Excel")
        export_excel_action.triggered.connect(self.export_to_excel)
        export_excel_action.setShortcut("Ctrl+E")
        
        export_csv_action = export_menu.addAction("Export to CSV")
        export_csv_action.triggered.connect(self.export_to_csv)
        
        # Backup Menu
        backup_menu = file_menu.addMenu("Backup")
        create_backup_action = backup_menu.addAction("Create Backup")
        create_backup_action.triggered.connect(self.backup_database)
        
        restore_backup_action = backup_menu.addAction("Restore from Backup")
        restore_backup_action.triggered.connect(self.restore_database)
        
        file_menu.addSeparator()
        
        # Exit Action
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Alt+F4")
        
        # Reports Menu
        reports_menu = menubar.addMenu("Reports")
        
        daily_report_action = reports_menu.addAction("Daily Report")
        daily_report_action.triggered.connect(self.generate_daily_report)
        
        monthly_report_action = reports_menu.addAction("Monthly Report")
        monthly_report_action.triggered.connect(self.generate_monthly_report)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)
        
        update_action = help_menu.addAction("Check for Updates...")
        update_action.triggered.connect(self.check_for_updates)
        
    def show_about_dialog(self):
        """Show the about dialog"""
        QMessageBox.about(self, "About",
            f"Jewellery Shop Management System\n\n"
            f"Version {APP_VERSION}\n"
            "A comprehensive solution for managing jewellery shop transactions.\n\n"
            "© 2024 All rights reserved.")

    def load_today_data(self):
        """Load transactions for today's date"""
        try:
            today = datetime.now().date()
            transactions = self.db.get_transactions_by_date(today)
            self.update_transaction_table(transactions)
            self.update_summary(transactions)
            self.status_bar.showMessage(f"Loaded data for {today.strftime('%Y-%m-%d')}")
        except Exception as e:
            self.logger.error(f"Error loading today's data: {str(e)}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Error loading data: {str(e)}")

    def handle_item_code_key_press(self, event):
        """Handle key press events for the item code input"""
        if not self.suggestion_popup.isVisible():
            QLineEdit.keyPressEvent(self.item_code_input, event)
            return
            
        if event.key() == Qt.Key.Key_Up:
            current_row = self.suggestion_list.currentRow()
            if current_row > 0:
                self.suggestion_list.setCurrentRow(current_row - 1)
                self.suggestion_list.scrollToItem(self.suggestion_list.currentItem())
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            current_row = self.suggestion_list.currentRow()
            if current_row < self.suggestion_list.count() - 1:
                self.suggestion_list.setCurrentRow(current_row + 1)
                self.suggestion_list.scrollToItem(self.suggestion_list.currentItem())
            event.accept()
        elif event.key() == Qt.Key.Key_Return:
            self.select_suggestion()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.suggestion_popup.hide()
            event.accept()
        else:
            QLineEdit.keyPressEvent(self.item_code_input, event)

    def update_summary(self, transactions: List[Dict]):
        """Update the summary section with transaction totals"""
        try:
            # Calculate totals
            gold_weight = 0.0
            silver_weight = 0.0
            old_gold = 0.0
            old_silver = 0.0
            total_amount = 0.0
            billable_gold = 0.0
            billable_silver = 0.0
            billable_amount = 0.0
            cash_total = 0.0
            card_total = 0.0
            upi_total = 0.0
            
            for transaction in transactions:
                # Process new items
                for item in transaction['items']:
                    if item['item_type'] == "Gold":
                        gold_weight += item['weight']
                        if item['is_billable']:
                            billable_gold += item['weight']
                            billable_amount += item['amount']
                    elif item['item_type'] == "Silver":
                        silver_weight += item['weight']
                        if item['is_billable']:
                            billable_silver += item['weight']
                            billable_amount += item['amount']
                
                # Process old items if they exist
                if 'old_items' in transaction:
                    for item in transaction['old_items']:
                        if item['item_type'] == "Gold":
                            old_gold += item['weight']
                        elif item['item_type'] == "Silver":
                            old_silver += item['weight']
                
                # Process payment details
                cash_total += transaction.get('cash_amount', 0)
                card_total += transaction.get('card_amount', 0)
                upi_total += transaction.get('upi_amount', 0)
                total_amount += transaction['total_amount']
            
            # Update labels with clear formatting
            self.gold_weight_label.setText(f"Gold: {gold_weight:.2f} gm")
            self.silver_weight_label.setText(f"Silver: {silver_weight:.2f} gm")
            self.old_gold_label.setText(f"Gold: {old_gold:.2f} gm")
            self.old_silver_label.setText(f"Silver: {old_silver:.2f} gm")
            self.billable_gold_label.setText(f"Gold: {billable_gold:.2f} gm")
            self.billable_silver_label.setText(f"Silver: {billable_silver:.2f} gm")
            self.billable_amount_label.setText(f"Amount: ₹{billable_amount:.2f}")
            
            # Update payment details
            self.cash_total_label.setText(f"Cash: ₹{cash_total:.2f}")
            self.card_total_label.setText(f"Card: ₹{card_total:.2f}")
            self.upi_total_label.setText(f"UPI: ₹{upi_total:.2f}")
            self.total_amount_label.setText(f"₹{total_amount:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error updating summary: {str(e)}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Error updating summary: {str(e)}")

    def check_for_updates(self):
        """Check for updates using GitHub API"""
        try:
            # Get latest version from GitHub API
            response = requests.get(LATEST_VERSION_URL)
            if response.status_code == 200:
                latest_data = response.json()
                latest_version = latest_data['tag_name'].lstrip('v')  # Remove 'v' prefix if present
                
                # Compare versions
                if latest_version > APP_VERSION:
                    # Format download URL with current version
                    download_url = DOWNLOAD_PAGE_URL.format(version=APP_VERSION)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Update Available")
                    msg.setText(f"A new version ({latest_version}) is available!")
                    msg.setInformativeText(f"Current version: {APP_VERSION}\n\n"
                                         f"Please visit the releases page to download the update.")
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.setDefaultButton(QMessageBox.StandardButton.Ok)
                    
                    # Add a button to open the download page
                    download_button = msg.addButton("Download Update", QMessageBox.ButtonRole.ActionRole)
                    download_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(download_url)))
                    
                    msg.exec()
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("No Updates")
                    msg.setText("You are running the latest version!")
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.exec()
            else:
                print(f"Failed to check for updates: {response.status_code}")
        except Exception as e:
            print(f"Error checking for updates: {e}")