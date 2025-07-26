"""
Simplified Multi-tasking GUI for Gemma3n Assistant
Clean PyQt5 interface with essential features
"""
import sys
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QSplitter,
    QStatusBar, QMessageBox, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor

# Project imports
from agents.task_executor import task_executor
from voice.voice_manager import voice_manager
from async_tasks import task_queue
from config import config

logger = logging.getLogger(__name__)

class WorkerThread(QThread):
    """Worker thread for AI processing"""
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, user_input: str):
        super().__init__()
        self.user_input = user_input
    
    def run(self):
        try:
            result = task_executor.execute_task(self.user_input)
            self.result_ready.emit(result)
        except Exception as e:
            logger.error(f"Worker thread error: {e}")
            self.error_occurred.emit(str(e))

class VoiceThread(QThread):
    """Thread for voice recognition"""
    speech_recognized = pyqtSignal(str)
    listening_status = pyqtSignal(bool)
    
    def run(self):
        try:
            self.listening_status.emit(True)
            text = voice_manager.listen(timeout=10.0)
            if text:
                self.speech_recognized.emit(text)
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
        finally:
            self.listening_status.emit(False)

class GemmaMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('GemmaAssistant', 'MainWindow')
        self.worker_thread = None
        self.voice_thread = None
        self.is_processing = False
        self.is_listening = False
        
        self.setup_ui()
        self.setup_voice_callbacks()
        self.setup_system_tray()
        self.load_settings()
        
        # Status timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Gemma3n AI Assistant")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🤖 Gemma3n AI Assistant")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Consolas", 10))
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setFont(QFont("Arial", 10))
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #555;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        # Buttons
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        self.voice_button = QPushButton("🎤 Listen")
        self.voice_button.clicked.connect(self.toggle_voice)
        self.voice_button.setEnabled(voice_manager.is_available())
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        input_layout.addWidget(self.voice_button)
        
        layout.addWidget(input_frame)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Welcome message
        self.add_message("system", "🚀 Welcome to Gemma3n AI Assistant!")
        self.add_message("system", "💡 You can type messages or use voice input")
        if not voice_manager.is_available():
            self.add_message("system", "⚠️ Voice features disabled (missing libraries)")
    
    def setup_voice_callbacks(self):
        """Setup voice system callbacks"""
        voice_manager.add_callback('on_speech_start', lambda: self.status_bar.showMessage("🔊 Speaking..."))
        voice_manager.add_callback('on_speech_end', lambda: self.status_bar.showMessage("Ready"))
        voice_manager.add_callback('on_listen_start', lambda: self.status_bar.showMessage("🎤 Listening..."))
        voice_manager.add_callback('on_listen_end', lambda: self.status_bar.showMessage("Ready"))
        voice_manager.add_callback('on_error', self.on_voice_error)
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
            
            tray_menu = QMenu()
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            
            tray_menu.addAction(show_action)
            tray_menu.addAction(quit_action)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
    
    def add_message(self, sender: str, message: str):
        """Add a message to the chat area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "user":
            formatted = f"<div style='color: #4fc3f7; margin: 5px 0;'><b>[{timestamp}] You:</b> {message}</div>"
        elif sender == "assistant":
            formatted = f"<div style='color: #81c784; margin: 5px 0;'><b>[{timestamp}] Assistant:</b> {message}</div>"
        else:
            formatted = f"<div style='color: #ffb74d; margin: 5px 0;'><b>[{timestamp}] System:</b> {message}</div>"
        
        self.chat_area.append(formatted)
        
        # Auto-scroll to bottom
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)
    
    def send_message(self):
        """Send user message"""
        if self.is_processing:
            return
        
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        
        self.input_field.clear()
        self.add_message("user", user_input)
        
        # Start processing
        self.is_processing = True
        self.send_button.setEnabled(False)
        self.status_bar.showMessage("🤔 Thinking...")
        
        # Start worker thread
        self.worker_thread = WorkerThread(user_input)
        self.worker_thread.result_ready.connect(self.on_result_ready)
        self.worker_thread.error_occurred.connect(self.on_error_occurred)
        self.worker_thread.start()
    
    def toggle_voice(self):
        """Toggle voice recognition"""
        if not voice_manager.is_available():
            QMessageBox.warning(self, "Voice Unavailable", 
                              "Voice recognition is not available. Please install required libraries.")
            return
        
        if self.is_listening:
            return
        
        self.is_listening = True
        self.voice_button.setText("🎤 Listening...")
        self.voice_button.setEnabled(False)
        
        # Start voice thread
        self.voice_thread = VoiceThread()
        self.voice_thread.speech_recognized.connect(self.on_speech_recognized)
        self.voice_thread.listening_status.connect(self.on_listening_status_changed)
        self.voice_thread.start()
    
    def on_result_ready(self, result: dict):
        """Handle AI result"""
        self.is_processing = False
        self.send_button.setEnabled(True)
        
        message = result.get('message', 'No response')
        self.add_message("assistant", message)
        
        # Speak response if voice is available
        if voice_manager.is_available() and message:
            voice_manager.speak(message)
        
        self.status_bar.showMessage("Ready")
    
    def on_error_occurred(self, error: str):
        """Handle processing error"""
        self.is_processing = False
        self.send_button.setEnabled(True)
        self.add_message("system", f"❌ Error: {error}")
        self.status_bar.showMessage("Error occurred")
    
    def on_speech_recognized(self, text: str):
        """Handle recognized speech"""
        self.input_field.setText(text)
        self.send_message()
    
    def on_listening_status_changed(self, is_listening: bool):
        """Handle listening status change"""
        self.is_listening = is_listening
        if not is_listening:
            self.voice_button.setText("🎤 Listen")
            self.voice_button.setEnabled(True)
    
    def on_voice_error(self, error: str):
        """Handle voice error"""
        self.add_message("system", f"🎤 Voice error: {error}")
    
    def update_status(self):
        """Update status bar with system info"""
        if not self.is_processing and not self.is_listening:
            stats = voice_manager.get_stats()
            if stats['enabled']:
                success_rate = stats.get('success_rate', 0)
                self.status_bar.showMessage(f"Ready | Voice: {success_rate:.1f}% success rate")
            else:
                self.status_bar.showMessage("Ready")
    
    def load_settings(self):
        """Load window settings"""
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
    
    def save_settings(self):
        """Save window settings"""
        self.settings.setValue('geometry', self.saveGeometry())
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        
        # Cleanup
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.terminate()
        
        voice_manager.shutdown()
        task_queue.shutdown()
        
        event.accept()

def main():
    """Main function to run the standard GUI"""
    return create_and_run_gui()

def create_and_run_gui():
    """Create and run the GUI application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Gemma3n Assistant")
    app.setQuitOnLastWindowClosed(True)
    
    # Apply dark theme
    app.setStyle('Fusion')
    palette = app.palette()
    palette.setColor(palette.Window, QColor(53, 53, 53))
    palette.setColor(palette.WindowText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = GemmaMainWindow()
    window.show()
    
    try:
        return app.exec_()
    except KeyboardInterrupt:
        return 0

if __name__ == "__main__":
    exit_code = create_and_run_gui()
    sys.exit(exit_code)
