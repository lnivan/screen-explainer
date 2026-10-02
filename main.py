import sys
import markdown
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QByteArray, QBuffer, QIODevice
from src.capture_overlay import CaptureOverlay
from src.ai_client import AIClient
from src.response_window import ResponseWindow
from src.setup_window import SetupWindow
import keyboard
from PIL import Image
import io
import os
from dotenv import load_dotenv

class AIWorker(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, client, image_pil):
        super().__init__()
        self.client = client
        self.image_pil = image_pil

    def run(self):
        response = self.client.query(self.image_pil)
        self.finished.emit(response)

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Check for API Key
        load_dotenv()
        if not os.getenv("GEMINI_API_KEY"):
            print("API Key not found, launching setup window...")
            self.setup_window = SetupWindow()
            self.setup_window.show()
            # We wait for the setup window to close, then reload env
            self.app.exec() 
            
            # After setup window closes, check again
            load_dotenv()
            if not os.getenv("GEMINI_API_KEY"):
                print("Setup cancelled or no key provided. Exiting.")
                sys.exit(0)
            
            # Reset the quit behavior for the main background app
            self.app.setQuitOnLastWindowClosed(False)

        # Initialize components
        self.overlay = CaptureOverlay()
        self.overlay.capture_completed.connect(self.handle_capture)
        # We don't really need to do anything on cancel right now

        self.ai_client = AIClient()
        self.response_window = ResponseWindow()

        # Register global hotkey
        keyboard.add_hotkey('ctrl+shift+a', self.trigger_capture)
        print("Screen Capture AI Assistant is running.")
        print("Press Ctrl+Shift+A to capture a region of your screen.")

    def trigger_capture(self):
        # Must run UI updates on the main thread
        QTimer.singleShot(0, self.overlay.show_overlay)

    def handle_capture(self, pixmap, rect):
        print(f"Capture completed at {rect}")
        
        # 1. Convert QPixmap to PIL Image
        # Note: saving to a buffer is usually the most robust way to convert between these
        buffer = pyqt_pixmap_to_pil(pixmap)
        if not buffer:
            return
            
        # 2. Show the response window with "loading" state
        self.response_window.set_loading(True)
        # Show near the bottom right of the selection
        self.response_window.show_at(rect.right() + 10, rect.top())

        # 3. Start AI Request in a separate thread so we don't block the UI
        self.worker = AIWorker(self.ai_client, buffer)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.start()

    def handle_ai_response(self, text):
        print("Received AI Response.")
        # Render markdown to HTML before setting it
        html_content = markdown.markdown(text)
        self.response_window.set_response(html_content)

    def run(self):
        sys.exit(self.app.exec())

def pyqt_pixmap_to_pil(pixmap):
    try:
        image = pixmap.toImage()
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        return Image.open(io.BytesIO(byte_array.data()))
    except Exception as e:
        print(f"Error converting image: {e}")
        return None

if __name__ == "__main__":
    app = App()
    app.run()
