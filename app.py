#!/usr/bin/env python3
"""
Main Application Entry Point - Always launches GUI with Multi-tasking
Enhanced Gemma3n Assistant with concurrent task execution
"""
import sys
import os
import signal
import logging
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup early logging
from config import config

def setup_logging():
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    config.LOG_DIR.mkdir(exist_ok=True)
    
    # Setup file logging
    log_file = config.LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n🛑 Received shutdown signal. Cleaning up...")
    sys.exit(0)

def check_system_requirements():
    """Check system requirements and dependencies"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required. Current: {sys.version}")
        return False
    
    # Check critical dependencies
    missing_deps = []
    
    try:
        import PyQt5
        print("✅ PyQt5 GUI framework")
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        from utils.ollama_client import ollama_client
        if ollama_client.is_available():
            print("✅ Ollama AI backend")
        else:
            print("⚠️ Ollama not available - limited functionality")
    except Exception as e:
        print(f"⚠️ Ollama check failed: {e}")
    
    try:
        import psutil
        import pyautogui
        print("✅ System integration tools")
    except ImportError:
        missing_deps.append("system tools (psutil, pyautogui)")
    
    if missing_deps:
        print(f"❌ Missing: {', '.join(missing_deps)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """
    Main application entry point
    Always launches the GUI interface with multi-tasking capabilities
    """
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print banner
    print("=" * 60)
    print("🤖 GEMMA3N ASSISTANT - MULTI-TASKING AI AGENT")
    print("=" * 60)
    print("🚀 Advanced AI Assistant with Concurrent Task Execution")
    print("🎨 GUI Interface with Multi-threaded Processing")
    print("🧠 Context-Aware • Proactive • Intelligent")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Gemma3n Assistant Multi-tasking GUI")
    
    # Check system requirements
    if not check_system_requirements():
        input("\nPress Enter to exit...")
        return 1
    
    print("\n🎯 System Requirements: ✅ PASSED")
    print("🎨 Launching Multi-tasking GUI Interface...")
    
    try:
        # Import enhanced GUI
        from ui.enhanced_main_window import main as run_enhanced_gui
        
        print("\n" + "=" * 60)
        print("🎮 ENHANCED GUI FEATURES AVAILABLE:")
        print("=" * 60)
        print("💬 Multi-threaded Chat Interface")
        print("🔄 Concurrent Task Execution")
        print("🎤 Real-time Voice Processing")
        print("📋 Background Task Management")
        print("🧠 Live Memory & Context Tracking")
        print("📊 Real-time System Monitoring")
        print("⚙️ Advanced Settings & Configuration")
        print("🔔 System Tray Integration")
        print("🎯 Smart Proactive Suggestions")
        print("=" * 60)
        print("🚀 Ready! The enhanced GUI will open momentarily...")
        print("=" * 60)
        
        # Run the enhanced GUI
        return run_enhanced_gui()
        
    except ImportError as e:
        logger.warning(f"Enhanced GUI not available: {e}")
        print(f"⚠️ Enhanced GUI not available: {e}")
        print("🔄 Falling back to standard GUI...")
        
        try:
            # Fallback to standard GUI
            from ui.main_window import main as run_standard_gui
            
            print("\n" + "=" * 60)
            print("🎮 STANDARD GUI FEATURES:")
            print("=" * 60)
            print("💬 Chat Interface with AI agent")
            print("🎤 Voice input and output")
            print("📋 Task management")
            print("🧠 Conversation memory")
            print("⚙️ Settings and configuration")
            print("📊 System status monitoring")
            print("=" * 60)
            print("🚀 Ready! The standard GUI will open momentarily...")
            print("=" * 60)
            
            return run_standard_gui()
            
        except ImportError as e2:
            logger.error(f"Standard GUI also failed: {e2}")
            print(f"❌ Standard GUI unavailable: {e2}")
            print("📋 Falling back to terminal interface...")
            
            # Final fallback to terminal
            try:
                from main import run_terminal_interface
                return run_terminal_interface()
            except ImportError:
                print("❌ All interfaces failed!")
                return 1
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Application error: {e}")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
