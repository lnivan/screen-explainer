from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextEdit, QFrame, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QThread
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
import markdown # We'll need to add this to requirements if we want to render the MD
# Actually, QTextEdit supports rudimentary markdown/HTML, but for simplicity we'll just use plain text or inject simple HTML

class ResponseWindow(QWidget):
    close_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # Create a modern, frameless, drop-shadow window
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Determine fixed size or allow resize
        self.setFixedSize(450, 600)
        
        self.setup_ui()
        self.drag_pos = None

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Background frame for styling
        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("bgFrame")
        self.bg_frame.setStyleSheet("""
            QFrame#bgFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333333;
            }
        """)
        main_layout.addWidget(self.bg_frame)
        
        # Frame layout
        frame_layout = QVBoxLayout(self.bg_frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        
        # Top Bar (Header + Close Button)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("AI Assistant")
        self.title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        top_bar.addWidget(self.title_label)
        
        top_bar.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #f44336;
                border-radius: 12px;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        top_bar.addWidget(self.close_btn)
        
        frame_layout.addLayout(top_bar)
        
        # Loading Indicator (Initially Hidden)
        self.loading_label = QLabel("Analyzing image...")
        self.loading_label.setStyleSheet("color: #aaaaaa; font-style: italic;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.loading_label)
        self.loading_label.hide()
        
        # Content Area
        self.content_area = QTextEdit()
        self.content_area.setReadOnly(True)
        self.content_area.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                font-size: 14px;
                line-height: 1.5;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        frame_layout.addWidget(self.content_area)

    def set_loading(self, is_loading):
        if is_loading:
            self.content_area.clear()
            self.content_area.hide()
            self.loading_label.show()
        else:
            self.loading_label.hide()
            self.content_area.show()

    def set_response(self, text):
        self.set_loading(False)
        self.content_area.setHtml(text)

    def show_at(self, x, y):
        # Calculate optimal position to not go off screen
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Simple adjust to keep on screen
        if x + self.width() > screen.width():
            x = screen.width() - self.width() - 20
        if y + self.height() > screen.height():
            y = screen.height() - self.height() - 20
            
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    # Allow dragging the window from the background frame
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = ResponseWindow()
    win.set_loading(False)
    win.set_response("# Analysis Result\n\nThis is a **test** response from the AI.")
    win.show_at(100, 100)
    sys.exit(app.exec())
