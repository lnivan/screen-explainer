import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Capture AI Setup")
        self.setFixedSize(400, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("Welcome to Screen Capture AI Assistant!\n\nPlease enter your Gemini API Key to continue:")
        layout.addWidget(label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("AIzaSy...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.api_key_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.save_btn = QPushButton("Save & Continue")
        self.save_btn.clicked.connect(self.save_api_key)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)

    def save_api_key(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "API Key cannot be empty.")
            return

        try:
            with open(".env", "w") as f:
                f.write(f'GEMINI_API_KEY="{api_key}"\n')
            QMessageBox.information(self, "Success", "API Key saved successfully! The app will now start in the background.\n\nPress Ctrl+Shift+A to capture your screen.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save API Key: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SetupWindow()
    window.show()
    sys.exit(app.exec())
