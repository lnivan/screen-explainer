import sys
from PyQt6.QtWidgets import QApplication, QWidget, QRubberBand
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QScreen, QPixmap
import io

class CaptureOverlay(QWidget):
    capture_completed = pyqtSignal(object, QRect) # Emits QPixmap and the global QRect
    capture_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        
        self.origin = QPoint()
        self.current_rect = QRect()
        self.is_drawing = False

        # Take a screenshot of the entire desktop to use as the background
        self.desktop_pixmap = None

    def show_overlay(self):
        # We need to capture the screens *before* showing the opaque overlay
        self.desktop_pixmap = QApplication.primaryScreen().grabWindow(0)
        
        # Determine the geometry spanning all screens
        screens = QApplication.screens()
        virtual_geometry = screens[0].geometry()
        for screen in screens[1:]:
            virtual_geometry = virtual_geometry.united(screen.geometry())
        
        self.setGeometry(virtual_geometry)
        self.current_rect = QRect()
        self.show()
        self.raise_()
        self.activateWindow()

    def paintEvent(self, event):
        if not self.desktop_pixmap:
            return

        painter = QPainter(self)
        
        # Draw the desktop screenshot as the base
        # If spanning multiple monitors, we might need a more complex grab
        # For simplicity, assuming primary screen or single screen for now
        # A more robust approach grabs each screen and stitches them or uses virtual desktop.
        painter.drawPixmap(0, 0, self.desktop_pixmap)

        # Draw the dark, semi-transparent overlay over the whole screen
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if not self.current_rect.isNull():
            # Clear the selected area to reveal the desktop underneath
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.current_rect, Qt.GlobalColor.transparent)

            # Draw a border around the selection
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(self.current_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.current_rect = QRect(self.origin, self.origin)
            self.is_drawing = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            # Cancel on right click
            self.hide()
            self.capture_cancelled.emit()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            # QRect.normalized() ensures width/height are positive even if dragged backwards
            self.current_rect = QRect(self.origin, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            self.hide()
            
            # The user might have just clicked without dragging
            if self.current_rect.width() > 10 and self.current_rect.height() > 10:
                # Add a slight delay to ensure the overlay is fully hidden before grabbing the region
                # Alternatively, we already have the `desktop_pixmap`, we can just crop it!
                cropped_pixmap = self.desktop_pixmap.copy(self.current_rect)
                self.capture_completed.emit(cropped_pixmap, self.current_rect)
            else:
                self.capture_cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.capture_cancelled.emit()

if __name__ == '__main__':
    # Simple standalone test for the overlay
    app = QApplication(sys.argv)
    overlay = CaptureOverlay()
    
    def on_capture(pixmap, rect):
        print("Captured!")
        pixmap.save("test.png")
        QApplication.quit()
        
    overlay.capture_completed.connect(on_capture)
    overlay.capture_cancelled.connect(QApplication.quit)
    
    QTimer.singleShot(500, overlay.show_overlay)
    sys.exit(app.exec())
