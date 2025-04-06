import sys
import os

# Get the absolute path of the executable (or script when running directly)
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (compiled with PyInstaller)
    application_path = sys._MEIPASS
else:
    # If the application is run from a Python interpreter
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the src directory to Python path
src_path = os.path.join(application_path, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-top: 1ex;
            padding: 10px;
            background-color: white;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QLineEdit, QComboBox, QDateEdit {
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
        }
        QTableWidget {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            gridline-color: #eee;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 6px;
            border: none;
            border-right: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            color: #2c3e50;
            font-weight: bold;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 