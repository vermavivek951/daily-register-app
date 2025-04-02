import sys
import os
from PyQt6.QtWidgets import QApplication

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.qt_ui import DailyRegisterUI

def main():
    app = QApplication(sys.argv)
    window = DailyRegisterUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 