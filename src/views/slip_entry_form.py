from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QGroupBox, QMessageBox, QSizePolicy,
    QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from utils.validation import (
    is_valid_float, is_valid_item_code, is_valid_item_type,
    parse_amount, parse_weight, validate_payment_amounts
)

class SlipEntryForm(QWidget):
    """Reusable component for slip entry form."""
    
    # Define signals for form events
    item_added = pyqtSignal(dict)  # Emitted when new item is added
    old_item_added = pyqtSignal(dict)  # Emitted when old item is added
    payment_entered = pyqtSignal(dict)  # Emitted when payment is entered
    transaction_saved = pyqtSignal()  # Emitted when transaction is saved successfully
    
    def __init__(self, view_model=None, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self.new_items = []
        self.old_items = []
        self.has_new_items = False  # Track if at least one new item is added
        self.has_old_items = False  # Track if at least one old item is added
        
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
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the form UI."""
        # Set window background color
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
            }
            QLabel {
                color: #000000;
                font-weight: bold;
                font-size: 11pt;
            }
            QLineEdit, QComboBox {
                background-color: white;
                color: #000000;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 5px;
                font-size: 11pt;
                selection-background-color: #0078D4;
                selection-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0078D4;
                background-color: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
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
                font-size: 12pt;
            }
            QCheckBox {
                font-size: 11pt;
                color: #000000;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #0078D4;
                border: 2px solid #0078D4;
            }
        """)

        main_layout = QVBoxLayout(self)
        form_layout = QHBoxLayout()
        
        # New Items Section
        new_items_group = QGroupBox("New Item Entry")
        new_items_layout = QHBoxLayout()  # Changed back to horizontal
        new_items_layout.setSpacing(15)  # Increased spacing
        
        # Code input
        code_layout = QVBoxLayout()
        code_label = QLabel("Item Code:")
        code_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter item code")
        self.code_input.setFixedWidth(120)
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_input)
        new_items_layout.addLayout(code_layout)
        
        # Name input
        name_layout = QVBoxLayout()
        name_label = QLabel("Item Name:")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name")
        self.name_input.setFixedWidth(200)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        new_items_layout.addLayout(name_layout)
        
        # Weight input
        weight_layout = QVBoxLayout()
        weight_label = QLabel("Weight (g):")
        weight_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Enter weight")
        self.weight_input.setFixedWidth(120)
        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(self.weight_input)
        new_items_layout.addLayout(weight_layout)
        
        # Amount input
        amount_layout = QVBoxLayout()
        amount_label = QLabel("Amount (₹):")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.amount_input.setFixedWidth(120)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        new_items_layout.addLayout(amount_layout)
        
        # Mark Bill input
        mark_bill_layout = QVBoxLayout()
        mark_bill_label = QLabel("Mark Bill:")
        mark_bill_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mark_bill_input = QLineEdit()
        self.mark_bill_input.setPlaceholderText("B/b or leave empty")
        self.mark_bill_input.setMaxLength(1)
        self.mark_bill_input.setFixedWidth(120)
        mark_bill_layout.addWidget(mark_bill_label)
        mark_bill_layout.addWidget(self.mark_bill_input)
        new_items_layout.addLayout(mark_bill_layout)
        
        new_items_group.setLayout(new_items_layout)
        form_layout.addWidget(new_items_group)
        
        # Old Items Section
        old_items_group = QGroupBox("Old Item Entry")
        old_items_layout = QHBoxLayout()  # Changed back to horizontal
        old_items_layout.setSpacing(15)  # Increased spacing
        
        # Type selection
        type_layout = QVBoxLayout()
        type_label = QLabel("Item Type:")
        type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("G/S")
        self.type_input.setMaxLength(1)
        self.type_input.setFixedWidth(120)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_input)
        old_items_layout.addLayout(type_layout)
        
        # Weight input
        old_weight_layout = QVBoxLayout()
        old_weight_label = QLabel("Weight (g):")
        old_weight_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.old_weight_input = QLineEdit()
        self.old_weight_input.setPlaceholderText("Enter weight")
        self.old_weight_input.setFixedWidth(120)
        old_weight_layout.addWidget(old_weight_label)
        old_weight_layout.addWidget(self.old_weight_input)
        old_items_layout.addLayout(old_weight_layout)
        
        # Amount input
        old_amount_layout = QVBoxLayout()
        old_amount_label = QLabel("Amount (₹):")
        old_amount_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.old_amount_input = QLineEdit()
        self.old_amount_input.setPlaceholderText("Enter amount")
        self.old_amount_input.setFixedWidth(120)
        old_amount_layout.addWidget(old_amount_label)
        old_amount_layout.addWidget(self.old_amount_input)
        old_items_layout.addLayout(old_amount_layout)
        
        old_items_group.setLayout(old_items_layout)
        form_layout.addWidget(old_items_group)
        
        # Payment Section
        payment_group = QGroupBox("Payment Details")
        payment_layout = QHBoxLayout()  # Changed back to horizontal
        payment_layout.setSpacing(15)  # Increased spacing
        
        # Payment inputs
        for payment_type in ["Cash", "Card", "UPI"]:
            payment_layout_col = QVBoxLayout()
            label = QLabel(f"{payment_type} Amount (₹):")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            input_field = QLineEdit()
            input_field.setPlaceholderText("0.00")
            input_field.setFixedWidth(120)
            setattr(self, f"{payment_type.lower()}_input", input_field)
            payment_layout_col.addWidget(label)
            payment_layout_col.addWidget(input_field)
            payment_layout.addLayout(payment_layout_col)
        
        # Comments section
        comments_layout = QVBoxLayout()
        comments_label = QLabel("Comments:")
        comments_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.comments_input = QLineEdit()
        self.comments_input.setPlaceholderText("Enter any comments")
        comments_layout.addWidget(comments_label)
        comments_layout.addWidget(self.comments_input)
        payment_layout.addLayout(comments_layout)
        
        payment_group.setLayout(payment_layout)
        form_layout.addWidget(payment_group)
        
        # Add form layout to main layout
        main_layout.addLayout(form_layout)
        
        # Set margins and spacing for better appearance
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        form_layout.setSpacing(15)
        
        # Set size policies for better resizing behavior
        for group in [new_items_group, old_items_group, payment_group]:
            group.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Fixed
            )
        
    def connect_signals(self):
        """Connect all signals."""
        # New item signals
        self.code_input.returnPressed.connect(self.on_code_enter)
        self.name_input.returnPressed.connect(self.on_name_enter)
        self.weight_input.returnPressed.connect(self.on_weight_enter)
        self.amount_input.returnPressed.connect(self.on_amount_enter)
        self.mark_bill_input.returnPressed.connect(self.on_mark_bill_enter)
        
        # Old item signals
        self.type_input.returnPressed.connect(self.on_type_enter)
        self.old_weight_input.returnPressed.connect(self.on_old_weight_enter)
        self.old_amount_input.returnPressed.connect(self.on_old_amount_enter)
        
        # Payment signals
        self.cash_input.returnPressed.connect(self.on_cash_enter)
        self.card_input.returnPressed.connect(self.on_card_enter)
        self.upi_input.returnPressed.connect(self.on_upi_enter)
        self.comments_input.returnPressed.connect(self.on_comments_enter)
        
    def clear_new_item_fields(self):
        """Clear only the new item input fields."""
        self.code_input.clear()
        self.name_input.clear()
        self.weight_input.clear()
        self.amount_input.clear()
        self.mark_bill_input.clear()
        self.code_input.setFocus()
        
    def clear_old_item_fields(self):
        """Clear only the old item input fields."""
        self.type_input.clear()
        self.old_weight_input.clear()
        self.old_amount_input.clear()
        self.type_input.setFocus()
        
    def clear_payment_fields(self):
        """Clear only the payment input fields."""
        self.cash_input.clear()
        self.card_input.clear()
        self.upi_input.clear()
        self.comments_input.clear()
        
    def clear_form(self):
        """Clear all input fields and reset the form."""
        self.clear_new_item_fields()
        self.clear_old_item_fields()
        self.clear_payment_fields()
        
        # Clear internal lists and flags
        self.new_items = []
        self.old_items = []
        self.has_new_items = False
        self.has_old_items = False
        
        # Set focus back to code input
        self.code_input.setFocus()
        
    def get_payment_details(self) -> dict:
        """Get current payment details."""
        return {
            'cash': parse_amount(self.cash_input.text()) or 0,
            'card': parse_amount(self.card_input.text()) or 0,
            'upi': parse_amount(self.upi_input.text()) or 0,
            'comments': self.comments_input.text().strip()
        }
        
    def get_items(self) -> tuple:
        """Get current new and old items."""
        return self.new_items.copy(), self.old_items.copy()
        
    def get_item_name_from_code(self, code: str) -> str:
        """Get item name based on item code."""
        code = code.upper()  # Convert to uppercase for case-insensitive matching
        item_info = self.ITEM_CODES.get(code)
        if item_info:
            return item_info['name']
        return ''  # Return empty string if code not found

    def on_code_enter(self):
        """Handle code input enter press."""
        print("\n=== New Item Entry Started ===")
        code = self.code_input.text().strip().upper()
        print(f"Code entered: {code}")
        
        if not code:
            if not self.has_new_items:
                print("No code entered and no items yet - showing warning")
                QMessageBox.warning(self, "No Items", "Please add at least one item")
                self.code_input.setFocus()
            else:
                print("No code entered - moving to old items")
                self.type_input.setFocus()
            return
            
        if not is_valid_item_code(code):
            print("Invalid code format - showing warning")
            QMessageBox.warning(self, "Invalid Code", "Item code must start with 'G' or 'S'")
            self.code_input.setFocus()
            return
            
        # Check if the code exists in our mappings
        if code not in self.ITEM_CODES:
            print("Unknown item code - showing warning")
            QMessageBox.warning(self, "Unknown Code", "This item code is not recognized")
            self.code_input.setFocus()
            return
            
        print(f"Valid code: {code} - moving to weight")
        self.code_input.setText(code)  # Ensure uppercase display
        
        # Automatically set the item name based on the code
        item_name = self.get_item_name_from_code(code)
        self.name_input.setText(item_name)
        
        self.weight_input.setFocus()
        
    def on_name_enter(self):
        """Handle name input enter press."""
        name = self.name_input.text().strip()
        if name:
            self.weight_input.setFocus()
            
    def on_weight_enter(self):
        """Handle weight input enter press."""
        print("\n=== New Item Weight Entry ===")
        code = self.code_input.text().strip().upper()
        weight_str = self.weight_input.text().strip()
        print(f"Code: {code}, Weight entered: {weight_str}")
        
        if not weight_str:
            print("No weight entered - ignoring")
            return
            
        weight = parse_weight(weight_str)
        if weight is None:
            print("Invalid weight format - showing warning")
            QMessageBox.warning(self, "Invalid Weight", "Please enter a valid positive number")
            self.weight_input.setFocus()
            return
            
        print(f"Valid weight: {weight} - moving to amount")
        self.amount_input.setFocus()
        
    def on_amount_enter(self):
        """Handle amount input enter press."""
        print("\n=== New Item Amount Entry ===")
        code = self.code_input.text().strip().upper()
        name = self.name_input.text().strip()
        weight_str = self.weight_input.text().strip()
        amount_str = self.amount_input.text().strip()
        print(f"Code: {code}, Name: {name}, Weight: {weight_str}, Amount: {amount_str}")
        
        # Validate all fields
        if not code or not is_valid_item_code(code):
            print("Invalid or missing code - returning to code input")
            self.code_input.setFocus()
            return
            
        if not name:
            print("Missing name - returning to name input")
            self.name_input.setFocus()
            return
            
        weight = parse_weight(weight_str)
        if weight is None:
            print("Invalid or missing weight - returning to weight input")
            self.weight_input.setFocus()
            return
            
        amount = parse_amount(amount_str)
        if amount is None:
            print("Invalid or missing amount - returning to amount input")
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number")
            self.amount_input.setFocus()
            return
            
        # Create item dictionary
        item = {
            'code': code,
            'name': name,
            'weight': weight,
            'amount': amount,
            'mark_bill': False  # Default to False, will be updated in on_mark_bill_enter
        }
        
        print(f"Moving to mark bill")
        self.mark_bill_input.setFocus()
        
    def on_mark_bill_enter(self):
        """Handle mark bill input enter press."""
        print("\n=== Mark Bill Entry ===")
        code = self.code_input.text().strip().upper()
        name = self.name_input.text().strip()
        weight_str = self.weight_input.text().strip()
        amount_str = self.amount_input.text().strip()
        mark_bill = self.mark_bill_input.text().strip().upper()
        
        # Validate all fields
        if not code or not is_valid_item_code(code):
            self.code_input.setFocus()
            return
            
        if not name:
            self.name_input.setFocus()
            return
            
        weight = parse_weight(weight_str)
        if weight is None:
            self.weight_input.setFocus()
            return
            
        amount = parse_amount(amount_str)
        if amount is None:
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number")
            self.amount_input.setFocus()
            return
            
        # Create item dictionary
        item = {
            'code': code,
            'name': name,
            'weight': weight,
            'amount': amount,
            'mark_bill': mark_bill == 'B'
        }
        
        print(f"Storing new item: {item}")
        # Only store the item, don't emit signal yet
        self.new_items.append(item)
        self.has_new_items = True
        
        # Clear fields after item is stored
        self.clear_new_item_fields()
        
    def on_type_enter(self):
        """Handle type input enter press."""
        print("\n=== Old Item Entry Started ===")
        type_str = self.type_input.text().strip().upper()
        print(f"Type entered: {type_str}")
        
        if not type_str:
            print("No type entered - moving to payment")
            self.cash_input.setFocus()
            return
            
        if not is_valid_item_type(type_str):
            print("Invalid type format - showing warning")
            QMessageBox.warning(self, "Invalid Type", "Type must be 'G' or 'S'")
            self.type_input.setFocus()
            return
            
        print(f"Valid type: {type_str} - moving to weight")
        self.type_input.setText(type_str)  # Ensure uppercase display
        self.old_weight_input.setFocus()
        
    def on_old_weight_enter(self):
        """Handle old item weight enter press."""
        print("\n=== Old Item Weight Entry ===")
        weight_str = self.old_weight_input.text().strip()
        print(f"Weight entered: {weight_str}")
        
        if not weight_str:
            print("No weight entered - ignoring")
            return
            
        weight = parse_weight(weight_str)
        if weight is None:
            print("Invalid weight format - showing warning")
            QMessageBox.warning(self, "Invalid Weight", "Please enter a valid positive number")
            self.old_weight_input.setFocus()
            return
            
        print(f"Valid weight: {weight} - moving to amount")
        self.old_amount_input.setFocus()
        
    def on_old_amount_enter(self):
        """Handle old item amount input enter press."""
        print("\n=== Old Item Amount Entry ===")
        print("Current values:")
        print(f"Type: {self.type_input.text()}")
        print(f"Weight: {self.old_weight_input.text()}")
        print(f"Amount: {self.old_amount_input.text()}")
        
        # Get all values
        type_ = self.type_input.text().strip().upper()
        weight = self.old_weight_input.text().strip()
        amount = self.old_amount_input.text().strip()
        
        # Validate all fields
        if not type_ or not weight or not amount:
            print("Missing values - showing warning")
            QMessageBox.warning(self, "Missing Values", "Please fill all fields")
            if not type_:
                self.type_input.setFocus()
            elif not weight:
                self.old_weight_input.setFocus()
            else:
                self.old_amount_input.setFocus()
            return
            
        try:
            # Convert to float
            weight_float = float(weight)
            amount_float = float(amount)
            
            # Validate values
            if weight_float <= 0 or amount_float <= 0:
                print("Invalid values - showing warning")
                QMessageBox.warning(self, "Invalid Values", "Weight and amount must be greater than 0")
                if weight_float <= 0:
                    self.old_weight_input.setFocus()
                else:
                    self.old_amount_input.setFocus()
                return
                
            # Create old item
            old_item = {
                'type': type_,
                'weight': weight_float,
                'amount': amount_float
            }
            print(f"Adding old item: {old_item}")
            
            # Add to list only (don't emit signal or add to view model yet)
            self.old_items.append(old_item)
            self.has_old_items = True
            
            # Clear fields
            self.type_input.clear()
            self.old_weight_input.clear()
            self.old_amount_input.clear()
            
            # Move focus back to type input for next old item
            print("Clearing fields and moving back to type input")
            self.type_input.setFocus()
            
        except ValueError:
            print("Invalid number format - showing warning")
            QMessageBox.warning(self, "Invalid Number", "Please enter valid numbers")
            self.old_amount_input.setFocus()

    def on_cash_enter(self):
        """Handle cash payment input enter press."""
        print("\n=== Cash Payment Entry ===")
        amount_str = self.cash_input.text().strip()
        print(f"Cash amount entered: {amount_str}")
        
        if not amount_str:
            print("No cash amount - moving to card")
            self.card_input.setFocus()
            return
            
        amount = parse_amount(amount_str)
        if amount is None:
            print("Invalid cash amount - showing warning")
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number")
            self.cash_input.setFocus()
            return
            
        print(f"Valid cash amount: {amount} - moving to card")
        self.card_input.setFocus()
        
    def on_card_enter(self):
        """Handle card payment input enter press."""
        print("\n=== Card Payment Entry ===")
        amount_str = self.card_input.text().strip()
        print(f"Card amount entered: {amount_str}")
        
        if not amount_str:
            print("No card amount - moving to UPI")
            self.upi_input.setFocus()
            return
            
        amount = parse_amount(amount_str)
        if amount is None:
            print("Invalid card amount - showing warning")
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number")
            self.card_input.setFocus()
            return
            
        print(f"Valid card amount: {amount} - moving to UPI")
        self.upi_input.setFocus()
        
    def on_upi_enter(self):
        """Handle UPI payment input enter press."""
        print("\n=== UPI Payment Entry ===")
        amount_str = self.upi_input.text().strip()
        print(f"UPI amount entered: {amount_str}")
        
        if not amount_str:
            print("No UPI amount - moving to comments")
            self.comments_input.setFocus()
            return
            
        amount = parse_amount(amount_str)
        if amount is None:
            print("Invalid UPI amount - showing warning")
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number")
            self.upi_input.setFocus()
            return
            
        print(f"Valid UPI amount: {amount} - moving to comments")
        self.comments_input.setFocus()
        
    def on_comments_enter(self):
        """Handle comments entry."""
        try:
            comments = self.comments_input.text().strip()
            print("=== Comments Entry ===")
            print(f"Comments entered: {comments}")
            
            # Get payment amounts from inputs
            cash_amount = parse_amount(self.cash_input.text()) or 0
            card_amount = parse_amount(self.card_input.text()) or 0
            upi_amount = parse_amount(self.upi_input.text()) or 0
            
            # Prepare payment details
            payment_details = {
                'cash_amount': cash_amount,
                'card_amount': card_amount,
                'upi_amount': upi_amount,
                'comments': comments
            }
            print(f"Payment details: {payment_details}")
            
            # Add items to view model
            print("Adding new items to view model...")
            for item in self.new_items:
                print(f"Adding new item: {item}")
                self.view_model.add_new_item(item)
                
            print("Adding old items to view model...")
            for item in self.old_items:
                print(f"Adding old item: {item}")
                self.view_model.add_old_item(item)
                
            # Save transaction
            print("Saving transaction...")
            if self.view_model.save_transaction(payment_details):
                self.clear_form()
                # Emit signal for successful save
                self.transaction_saved.emit()
                return True
            else:
                print("Failed to save transaction")
                QMessageBox.warning(self, "Error", "Failed to save transaction")
                return False
                
        except Exception as e:
            print(f"Error handling comments: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            return False

    def add_new_item(self):
        """Add a new item to the transaction."""
        try:
            # Get values from form
            code = self.code_input.text().strip()
            name = self.name_input.text().strip()
            weight = parse_weight(self.weight_input.text())
            amount = parse_amount(self.amount_input.text())
            mark_bill = self.mark_bill_input.text().strip().upper() == 'B'
            
            # Determine item type from code (G for Gold, S for Silver)
            item_type = 'G' if code.upper().startswith('G') else 'S'
            
            # Create new item dictionary
            new_item = {
                'code': code,
                'name': name,
                'type': item_type,  # Add type field
                'weight': weight,
                'amount': amount,
                'mark_bill': mark_bill
            }
            
            print(f"[SlipEntryForm] Adding new item: {new_item}")
            
            # Add to view model
            if self.view_model.add_new_item(new_item):
                # Clear inputs
                self.code_input.clear()
                self.name_input.clear()
                self.weight_input.clear()
                self.amount_input.clear()
                self.mark_bill_input.clear()
                
                # Update summary
                self.update_summary()
                
                # Set focus back to code input
                self.code_input.setFocus()
            else:
                raise Exception("Failed to add new item")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add new item: {str(e)}")
            
    def add_old_item(self):
        """Add an old item to the transaction."""
        try:
            # Get values from form
            item_type = self.type_input.text().strip().upper()
            weight = parse_weight(self.old_weight_input.text())
            amount = parse_amount(self.old_amount_input.text())
            
            # Validate item type
            if not is_valid_item_type(item_type):
                raise ValueError("Invalid item type. Use 'G' for Gold or 'S' for Silver.")
            
            # Create old item dictionary
            old_item = {
                'type': item_type,
                'weight': weight,
                'amount': amount
            }
            
            print(f"[SlipEntryForm] Adding old item: {old_item}")
            
            # Add to view model
            if self.view_model.add_old_item(old_item):
                # Clear inputs
                self.type_input.clear()
                self.old_weight_input.clear()
                self.old_amount_input.clear()
                
                # Update summary
                self.update_summary()
                
                # Set focus back to type input
                self.type_input.setFocus()
            else:
                raise Exception("Failed to add old item")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add old item: {str(e)}")
            
    def update_summary(self):
        """Update the transaction summary display."""
        try:
            summary = self.view_model.get_current_transaction_summary()
            
            # Update new items summary
            new_gold_weight = sum(float(item['weight']) for item in self.view_model.current_transaction['new_items'] 
                                if item.get('type', '').upper() == 'G')
            new_silver_weight = sum(float(item['weight']) for item in self.view_model.current_transaction['new_items'] 
                                  if item.get('type', '').upper() == 'S')
            
            self.new_items_summary.setText(
                f"New Items: {summary['new_items_count']}\n"
                f"Gold Weight: {new_gold_weight:.3f}\n"
                f"Silver Weight: {new_silver_weight:.3f}\n"
                f"Amount: ₹{summary['new_amount']:.2f}"
            )
            
            # Update old items summary
            old_gold_weight = sum(float(item['weight']) for item in self.view_model.current_transaction['old_items'] 
                                if item.get('type', '').upper() == 'G')
            old_silver_weight = sum(float(item['weight']) for item in self.view_model.current_transaction['old_items'] 
                                  if item.get('type', '').upper() == 'S')
            
            self.old_items_summary.setText(
                f"Old Items: {summary['old_items_count']}\n"
                f"Gold Weight: {old_gold_weight:.3f}\n"
                f"Silver Weight: {old_silver_weight:.3f}\n"
                f"Amount: ₹{summary['old_amount']:.2f}"
            )
            
            # Update total amount
            self.total_amount_label.setText(f"Total Amount: ₹{summary['total_amount']:.2f}")
            
        except Exception as e:
            print(f"Error updating summary: {e}") 