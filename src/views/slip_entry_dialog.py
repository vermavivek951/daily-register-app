from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QGroupBox,
    QMessageBox, QCheckBox, QComboBox, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor
from controllers.transaction_controller import TransactionController

class SlipEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = parent.controller if parent else TransactionController()
        self.new_items = []
        self.old_items = []
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("New Slip Entry")
        self.setMinimumWidth(800)
        
        layout = QVBoxLayout(self)
        
        # New Items Section
        new_items_group = QGroupBox("New Item Entry")
        new_items_layout = QHBoxLayout()
        
        # Code input
        code_layout = QVBoxLayout()
        code_label = QLabel("Code:")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter item code")
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_input)
        new_items_layout.addLayout(code_layout)
        
        # Weight input
        weight_layout = QVBoxLayout()
        weight_label = QLabel("Weight:")
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Enter weight")
        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(self.weight_input)
        new_items_layout.addLayout(weight_layout)
        
        # Amount input
        amount_layout = QVBoxLayout()
        amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        new_items_layout.addLayout(amount_layout)
        
        # Mark Bill input
        mark_bill_layout = QVBoxLayout()
        mark_bill_label = QLabel("Mark Bill:")
        self.mark_bill_input = QLineEdit()
        self.mark_bill_input.setPlaceholderText("B/b or leave empty")
        self.mark_bill_input.setMaxLength(1)
        mark_bill_layout.addWidget(mark_bill_label)
        mark_bill_layout.addWidget(self.mark_bill_input)
        new_items_layout.addLayout(mark_bill_layout)
        
        new_items_group.setLayout(new_items_layout)
        layout.addWidget(new_items_group)
        
        # Old Items Section
        old_items_group = QGroupBox("Old Item Entry")
        old_items_layout = QHBoxLayout()
        
        # Type input (changed from combo to text)
        type_layout = QVBoxLayout()
        type_label = QLabel("Type:")
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("G/S")
        self.type_input.setMaxLength(1)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_input)
        old_items_layout.addLayout(type_layout)
        
        # Old item weight
        old_weight_layout = QVBoxLayout()
        old_weight_label = QLabel("Weight:")
        self.old_weight_input = QLineEdit()
        self.old_weight_input.setPlaceholderText("Enter weight")
        old_weight_layout.addWidget(old_weight_label)
        old_weight_layout.addWidget(self.old_weight_input)
        old_items_layout.addLayout(old_weight_layout)
        
        # Old item amount
        old_amount_layout = QVBoxLayout()
        old_amount_label = QLabel("Amount:")
        self.old_amount_input = QLineEdit()
        self.old_amount_input.setPlaceholderText("Enter amount")
        old_amount_layout.addWidget(old_amount_label)
        old_amount_layout.addWidget(self.old_amount_input)
        old_items_layout.addLayout(old_amount_layout)
        
        old_items_group.setLayout(old_items_layout)
        layout.addWidget(old_items_group)
        
        # Payment Section
        payment_group = QGroupBox("Payment Details")
        payment_layout = QHBoxLayout()
        
        # Cash payment
        cash_layout = QVBoxLayout()
        cash_label = QLabel("Cash:")
        self.cash_input = QLineEdit()
        self.cash_input.setPlaceholderText("Enter cash amount")
        cash_layout.addWidget(cash_label)
        cash_layout.addWidget(self.cash_input)
        payment_layout.addLayout(cash_layout)
        
        # Card payment
        card_layout = QVBoxLayout()
        card_label = QLabel("Card:")
        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Enter card amount")
        card_layout.addWidget(card_label)
        card_layout.addWidget(self.card_input)
        payment_layout.addLayout(card_layout)
        
        # UPI payment
        upi_layout = QVBoxLayout()
        upi_label = QLabel("UPI:")
        self.upi_input = QLineEdit()
        self.upi_input.setPlaceholderText("Enter UPI amount")
        upi_layout.addWidget(upi_label)
        upi_layout.addWidget(self.upi_input)
        payment_layout.addLayout(upi_layout)
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Set initial focus and tab order
        self.setTabOrder(self.code_input, self.weight_input)
        self.setTabOrder(self.weight_input, self.amount_input)
        self.setTabOrder(self.amount_input, self.mark_bill_input)
        self.setTabOrder(self.mark_bill_input, self.type_input)
        self.setTabOrder(self.type_input, self.old_weight_input)
        self.setTabOrder(self.old_weight_input, self.old_amount_input)
        self.setTabOrder(self.old_amount_input, self.cash_input)
        self.setTabOrder(self.cash_input, self.card_input)
        self.setTabOrder(self.card_input, self.upi_input)
        
        self.code_input.setFocus()
        
    def connect_signals(self):
        """Connect all signals."""
        # New item signals
        self.code_input.returnPressed.connect(self.on_code_enter)
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
        
        # Button signals
        self.save_button.clicked.connect(self.save_transaction)
        self.cancel_button.clicked.connect(self.reject)
        
    def on_code_enter(self):
        """Handle code input enter press."""
        print("\n=== Code Enter Pressed ===")
        code = self.code_input.text().strip()
        print(f"Code entered: '{code}'")
        
        if not code:
            print("Empty code detected")
            if self.new_items:
                print(f"Moving to old items (have {len(self.new_items)} new items)")
                self.type_input.setFocus()
            else:
                print("No new items yet, staying on code input")
            return
            
        # Get suggestions for the code
        suggestions = self.controller.get_item_suggestions(code)
        print(f"Found {len(suggestions)} suggestions")
        
        if suggestions:
            # If we have an exact match, use it
            exact_match = next((s for s in suggestions if s['code'].lower() == code.lower()), None)
            if exact_match:
                print(f"Found exact match: {exact_match['code']}")
                self.code_input.setText(exact_match['code'])
                self.weight_input.setFocus()
                return
                
        # If no exact match, show error
        print("No exact match found")
        QMessageBox.warning(self, "Invalid Code", "Please enter a valid item code")
        self.code_input.setFocus()
        
    def on_weight_enter(self):
        """Handle weight input enter press."""
        print("\n=== Weight Enter Pressed ===")
        weight_text = self.weight_input.text().strip()
        if not weight_text:
            print("Empty weight, staying on weight input")
            return
            
        try:
            weight = float(weight_text)
            print(f"Weight entered: {weight}")
            if weight <= 0:
                raise ValueError()
            print("Moving to amount")
            self.amount_input.setFocus()
        except ValueError:
            print("Invalid weight!")
            QMessageBox.warning(self, "Invalid Weight", "Please enter a valid weight")
            self.weight_input.setFocus()
            
    def on_amount_enter(self):
        """Handle amount input enter press."""
        print("\n=== Amount Enter Pressed ===")
        amount_text = self.amount_input.text().strip()
        if not amount_text:
            print("Empty amount, staying on amount input")
            return
            
        try:
            amount = float(amount_text)
            print(f"Amount entered: {amount}")
            if amount <= 0:
                raise ValueError()
            print("Moving to mark bill")
            self.mark_bill_input.setFocus()
        except ValueError:
            print("Invalid amount!")
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount")
            self.amount_input.setFocus()
            
    def on_mark_bill_enter(self):
        """Handle mark bill input enter press."""
        print("\n=== Mark Bill Enter Pressed ===")
        mark_bill = self.mark_bill_input.text().strip().upper()
        print(f"Mark bill entered: '{mark_bill}'")
        
        # Get all field values
        code = self.code_input.text().strip()
        weight_text = self.weight_input.text().strip()
        amount_text = self.amount_input.text().strip()
        
        # If all fields are empty and we have at least one item, move to old items section
        if (not code and not weight_text and not amount_text and not mark_bill) or (not code):
            if self.new_items:
                print("Moving to old items section")
                self.type_input.setFocus()
            else:
                print("No items yet, staying on code input")
                self.code_input.setFocus()
            return
            
        # If mark bill is invalid, show warning
        if mark_bill and mark_bill != 'B':
            print("Invalid mark bill value!")
            QMessageBox.warning(self, "Invalid Input", "Please enter 'B' or leave empty")
            self.mark_bill_input.setFocus()
            return
            
        # If some required fields are empty but not all, move focus to the first empty field
        if not weight_text:
            print("Missing weight, moving focus")
            self.weight_input.setFocus()
            return
        if not amount_text:
            print("Missing amount, moving focus")
            self.amount_input.setFocus()
            return
            
        try:
            # Add item to internal list
            new_item = {
                'code': code,
                'weight': float(weight_text),
                'amount': float(amount_text),
                'is_billable': mark_bill == 'B'
            }
            self.new_items.append(new_item)
            print(f"Added new item: {new_item}")
            print(f"Total new items: {len(self.new_items)}")
            
            # Clear inputs
            self.code_input.clear()
            self.weight_input.clear()
            self.amount_input.clear()
            self.mark_bill_input.clear()
            print("Cleared all inputs")
            
            # Move to code input for next item
            print("Moving to code input for next item")
            self.code_input.setFocus()
            
        except ValueError:
            print("Invalid numeric values!")
            if not self.is_valid_float(weight_text):
                self.weight_input.setFocus()
            else:
                self.amount_input.setFocus()
        
    def on_type_enter(self):
        """Handle type input enter press."""
        print("\n=== Type Enter Pressed ===")
        type_text = self.type_input.text().strip().upper()
        print(f"Type entered: '{type_text}'")
        
        if not type_text:
            print("Empty type, staying on type input")
            return
            
        if type_text not in ['G', 'S']:
            print("Invalid type!")
            QMessageBox.warning(self, "Invalid Type", "Please enter G for Gold or S for Silver")
            self.type_input.setFocus()
            return
            
        # Convert to full type name
        self.type_input.setText(type_text)
        print("Moving to old weight")
        self.old_weight_input.setFocus()
        
    def on_old_weight_enter(self):
        """Handle old item weight enter press."""
        print("\n=== Old Weight Enter Pressed ===")
        weight_text = self.old_weight_input.text().strip()
        if not weight_text:
            print("Empty weight, moving to payments")
            self.cash_input.setFocus()
            return
            
        try:
            weight = float(weight_text)
            print(f"Old weight entered: {weight}")
            if weight <= 0:
                raise ValueError()
            print("Moving to old amount")
            self.old_amount_input.setFocus()
        except ValueError:
            print("Invalid old weight!")
            QMessageBox.warning(self, "Invalid Weight", "Please enter a valid weight")
            self.old_weight_input.setFocus()
            
    def on_old_amount_enter(self):
        """Handle old item amount enter press."""
        print("\n=== Old Amount Enter Pressed ===")
        amount_text = self.old_amount_input.text().strip()
        if not amount_text:
            print("Empty amount, staying on amount input")
            return
            
        try:
            amount = float(amount_text)
            print(f"Old amount entered: {amount}")
            if amount <= 0:
                raise ValueError()
                
            # Add old item to internal list
            type_text = self.type_input.text().strip().upper()
            old_item = {
                'type': 'Gold' if type_text == 'G' else 'Silver',
                'weight': float(self.old_weight_input.text()),
                'amount': amount
            }
            self.old_items.append(old_item)
            print(f"Added old item: {old_item}")
            print(f"Total old items: {len(self.old_items)}")
            
            # Clear inputs
            self.type_input.clear()
            self.old_weight_input.clear()
            self.old_amount_input.clear()
            print("Cleared old item inputs")
            
            # Move to type input for next item
            print("Moving to type input for next item")
            self.type_input.setFocus()
            
        except ValueError:
            print("Invalid old amount!")
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount")
            self.old_amount_input.setFocus()
            
    def on_cash_enter(self):
        """Handle cash input enter press."""
        print("\n=== Cash Enter Pressed ===")
        if self.cash_input.text().strip():
            try:
                amount = float(self.cash_input.text())
                print(f"Cash amount entered: {amount}")
                print("Moving to card")
                self.card_input.setFocus()
            except ValueError:
                print("Invalid cash amount!")
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount")
                self.cash_input.setFocus()
        else:
            print("No cash entered, moving to card")
            self.card_input.setFocus()
            
    def on_card_enter(self):
        """Handle card input enter press."""
        print("\n=== Card Enter Pressed ===")
        if self.card_input.text().strip():
            try:
                amount = float(self.card_input.text())
                print(f"Card amount entered: {amount}")
                print("Moving to UPI")
                self.upi_input.setFocus()
            except ValueError:
                print("Invalid card amount!")
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount")
                self.card_input.setFocus()
        else:
            print("No card amount entered, moving to UPI")
            self.upi_input.setFocus()
            
    def on_upi_enter(self):
        """Handle UPI input enter press."""
        print("\n=== UPI Enter Pressed ===")
        if self.upi_input.text().strip():
            try:
                amount = float(self.upi_input.text())
                print(f"UPI amount entered: {amount}")
                print("Moving to save transaction")
                self.save_transaction()
            except ValueError:
                print("Invalid UPI amount!")
                QMessageBox.warning(self, "Invalid Amount", "Please enter a valid amount")
                self.upi_input.setFocus()
        else:
            print("No UPI amount entered, moving to save transaction")
            self.save_transaction()
            
    def save_transaction(self):
        """Save the transaction."""
        print("\n=== Saving Transaction ===")
        # Get payment details
        try:
            payment_details = {
                'cash': float(self.cash_input.text() or 0),
                'card': float(self.card_input.text() or 0),
                'upi': float(self.upi_input.text() or 0)
            }
            print(f"Payment details: {payment_details}")
            
            print(f"New items ({len(self.new_items)}): {self.new_items}")
            print(f"Old items ({len(self.old_items)}): {self.old_items}")
            
            # Validate that we have at least one item
            if not self.new_items and not self.old_items:
                print("No items added, returning to code input")
                self.code_input.setFocus()
                return
                
            print("Adding new items to controller...")
            # Add all new items
            for item in self.new_items:
                self.controller.add_new_item(
                    item['code'],
                    item['weight'],
                    item['amount'],
                    item['is_billable']
                )
                
            print("Adding old items to controller...")
            # Add all old items
            for item in self.old_items:
                self.controller.add_old_item(
                    item['type'],
                    item['weight'],
                    item['amount']
                )
                
            print("Saving transaction...")
            # Save transaction with payment details
            if self.controller.save_transaction(payment_details):
                print("Transaction saved successfully!")
                self.accept()
            else:
                print("Failed to save transaction!")
                QMessageBox.warning(self, "Error", "Failed to save transaction")
                
        except ValueError:
            print("Invalid payment amounts!")
            QMessageBox.warning(self, "Invalid Amount", "Please enter valid payment amounts")
            self.cash_input.setFocus()

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Don't let Enter/Return propagate up
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return
        super().keyPressEvent(event)

    def is_valid_float(self, text: str) -> bool:
        """Helper method to validate if a string can be converted to float."""
        try:
            float(text)
            return True
        except ValueError:
            return False 