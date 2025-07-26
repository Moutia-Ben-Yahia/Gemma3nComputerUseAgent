#!/usr/bin/env python3
"""
Gemma3n Assistant - Offline AI Agent
Main entry point for the agent
"""
import asyncio
import logging
import re
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import colorama
from colorama import Fore, Style

# Initialize colorama for Windows console colors
colorama.init()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from agents.task_executor import task_executor
from memory import memory_manager
from voice import voice_manager
from utils.ollama_client import ollama_client

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    config.LOG_DIR.mkdir(exist_ok=True)
    
    # Setup file logging
    log_file = config.LOG_DIR / f"assistant_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)

class GemmaAssistant:
    """Main assistant class"""
    
    def __init__(self):
        self.running = True
        self.voice_mode = False
        self.last_suggestions = []  # Store last suggestions for execution
        
    def print_banner(self):
        """Print welcome banner"""
        banner = f"""
{Fore.CYAN}
╔═══════════════════════════════════════════════════════════════╗
║              {Fore.YELLOW}DYNAMIC AI AGENT ASSISTANT{Fore.CYAN}                   ║
║                {Fore.GREEN}Smart • Proactive • Context-Aware{Fore.CYAN}              ║
║                                                               ║
║  🧠 Smart Features:                                           ║
║    • Understands context and meaning                         ║
║    • Suggests proactive actions                              ║
║    • Executes multi-step tasks autonomously                  ║
║    • Learns from conversation history                        ║
║                                                               ║
║  💬 Natural Commands:                                         ║
║    "I need to be more productive"                            ║
║    "Help me organize my files"                               ║
║    "Clean up my system"                                      ║
║    "What should I work on next?"                             ║
║                                                               ║
║  🎯 System Commands:                                          ║
║    'status' • 'tasks' • 'help' • 'quit'                     ║
║    'execute suggestion [number]' - Run AI suggestions        ║
╚═══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
        """
        print(banner)
    
    def print_status(self):
        """Print system status"""
        print(f"\n{Fore.YELLOW}=== SYSTEM STATUS ==={Style.RESET_ALL}")
        
        # Ollama status
        ollama_status = "✅ Connected" if ollama_client.is_available() else "❌ Not available"
        print(f"Ollama: {ollama_status}")
        
        # Model info
        if ollama_client.is_available():
            models = ollama_client.list_models()
            model_names = [m.get('name', 'Unknown') for m in models]
            print(f"Available models: {', '.join(model_names)}")
            print(f"Current model: {config.OLLAMA_MODEL}")
        
        # Voice status
        voice_status = "✅ Available" if voice_manager.is_available() else "❌ Not available"
        print(f"Voice system: {voice_status}")
        print(f"Voice mode: {'🎙️ ON' if self.voice_mode else '🔇 OFF'}")
        
        # Memory status
        recent_convs = len(memory_manager.get_recent_conversations())
        pending_tasks = len(memory_manager.get_pending_tasks())
        print(f"Recent conversations: {recent_convs}")
        print(f"Pending tasks: {pending_tasks}")
        
        print(f"{Fore.YELLOW}====================={Style.RESET_ALL}\n")
    
    def show_tasks(self):
        """Show pending tasks"""
        tasks = memory_manager.get_pending_tasks()
        
        if not tasks:
            print(f"{Fore.GREEN}No pending tasks!{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}=== PENDING TASKS ==={Style.RESET_ALL}")
        for i, task in enumerate(tasks, 1):
            priority = task.get('priority', 'normal')
            priority_color = Fore.RED if priority == 'high' else Fore.YELLOW if priority == 'medium' else Fore.GREEN
            print(f"{i}. [{priority_color}{priority.upper()}{Style.RESET_ALL}] {task['description']}")
            print(f"   Created: {task['created_at'][:19]}")
        print(f"{Fore.YELLOW}====================={Style.RESET_ALL}\n")
    
    def show_help(self):
        """Show help information"""
        help_text = f"""
{Fore.CYAN}=== DYNAMIC AI AGENT CAPABILITIES ==={Style.RESET_ALL}

{Fore.GREEN}🧠 Smart Agent Features:{Style.RESET_ALL}
  • Context-aware understanding of your needs
  • Proactive suggestions based on your situation
  • Multi-step task planning and execution
  • Learning from conversation history
  • Intelligent file organization and system cleanup

{Fore.GREEN}💬 Natural Language Examples:{Style.RESET_ALL}
  "I need to be more productive today"
  "Help me organize my workspace"
  "What should I focus on next?"
  "Clean up my computer"
  "I'm working on a project, what do I need?"
  "Suggest some productivity improvements"

{Fore.GREEN}🎯 Direct Commands:{Style.RESET_ALL}
  "Open [app]" / "Close [app]" / "Create file [name]"
  "List files in [folder]" / "Run command [cmd]"
  "Remind me to [task]" / "Read file [name]"

{Fore.GREEN}🤖 System Commands:{Style.RESET_ALL}
  status                    - Show system status
  tasks                     - Show pending tasks
  help                      - Show this help
  voice                     - Toggle voice mode
  execute suggestion [num]  - Run AI suggestions by number
  quit/exit                 - Exit the assistant

{Fore.YELLOW}✨ Pro Tip: The AI analyzes your context and suggests smart actions.
Try asking open-ended questions about productivity, organization, or workflows!{Style.RESET_ALL}
        """
        print(help_text)
    
    def get_user_input(self) -> str:
        """Get input from user (text or voice)"""
        if self.voice_mode and voice_manager.is_available():
            print(f"{Fore.CYAN}🎙️ Listening... (speak now){Style.RESET_ALL}")
            voice_input = voice_manager.listen(timeout=10, phrase_time_limit=10)
            
            if voice_input:
                print(f"{Fore.GREEN}You said: {voice_input}{Style.RESET_ALL}")
                return voice_input
            else:
                print(f"{Fore.YELLOW}No voice input detected. Switching to text mode for this turn.{Style.RESET_ALL}")
        
        # Fallback to text input
        try:
            return input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
        except (KeyboardInterrupt, EOFError):
            return "quit"
    
    def process_response(self, response: dict):
        """Process and display response with enhanced suggestion handling"""
        status = response.get('status', 'unknown')
        message = response.get('message', 'No response')
        response_type = response.get('type', 'standard')
        
        # Check for success in multiple formats for compatibility
        is_success = (status == 'success' or response.get('success', False))
        is_error = (status == 'error' or (response.get('success') is False and status != 'unknown'))
        
        # Color code based on status
        if is_success:
            color = Fore.GREEN
            icon = "✅"
        elif is_error:
            color = Fore.RED
            icon = "❌"
        elif status == 'info':
            color = Fore.YELLOW
            icon = "ℹ️"
        else:
            color = Fore.BLUE
            icon = "🤖"
        
        print(f"{color}{icon} {message}{Style.RESET_ALL}")
        
        # Handle AI understanding feedback
        if 'understanding' in response:
            print(f"{Fore.CYAN}🧠 Understanding: {response['understanding']}{Style.RESET_ALL}")
        
        # Show additional info if available
        if 'content' in response:
            content = response['content']
            if len(content) > 500:
                print(f"{Fore.YELLOW}Content preview (first 500 chars):{Style.RESET_ALL}")
                print(f"{content[:500]}...")
            else:
                print(f"{Fore.YELLOW}Content:{Style.RESET_ALL}")
                print(content)
        
        if 'items' in response:
            items = response['items']
            print(f"{Fore.YELLOW}Found {len(items)} items:{Style.RESET_ALL}")
            for item in items[:10]:  # Show first 10 items
                item_type = "📁" if item.get('type') == 'directory' else "📄"
                print(f"  {item_type} {item['name']}")
            if len(items) > 10:
                print(f"  ... and {len(items) - 10} more items")
        
        # Handle execution results for multi-action responses
        if 'execution_results' in response:
            results = response['execution_results']
            if len(results) > 1:
                print(f"{Fore.BLUE}📋 Execution Details:{Style.RESET_ALL}")
                for i, result in enumerate(results, 1):
                    # Check both 'success' and 'status' fields for compatibility
                    is_success = (result.get('status') == 'success' or 
                                result.get('success', False))
                    status_icon = "✅" if is_success else "❌"
                    print(f"  {i}. {status_icon} {result.get('message', 'Unknown')}")
        
        # Handle smart suggestions
        suggestions = response.get('suggestions', [])
        if suggestions:
            # Store suggestions for potential execution
            self.last_suggestions = suggestions
            
            print(f"\n{Fore.MAGENTA}🤖 Smart Suggestions:{Style.RESET_ALL}")
            for i, suggestion in enumerate(suggestions, 1):
                if isinstance(suggestion, dict):
                    action = suggestion.get('action', str(suggestion))
                    benefit = suggestion.get('benefit', '')
                    priority = suggestion.get('priority', 'medium')
                    priority_icon = "🔥" if priority == 'high' else "⚡" if priority == 'medium' else "💡"
                    print(f"  {i}. {priority_icon} {action}")
                    if benefit:
                        print(f"     💡 {benefit}")
                else:
                    print(f"  {i}. 💡 {suggestion}")
            
            # Offer to execute suggestions
            if response_type in ['conversational_with_suggestions', 'multi_action_execution']:
                print(f"\n{Fore.CYAN}💬 Say 'execute suggestion [number]' or 'do suggestion [number]' to run any suggestion!{Style.RESET_ALL}")
        else:
            # Clear suggestions if none provided
            self.last_suggestions = []
        
        # Voice output if enabled
        if self.voice_mode and voice_manager.is_available():
            # Clean message for speech (remove emojis and special chars)
            clean_message = message.replace("✅", "").replace("❌", "").replace("ℹ️", "").replace("🤖", "").strip()
            # Also remove suggestion text to keep speech concise
            if "Smart Suggestions:" in clean_message:
                clean_message = clean_message.split("Smart Suggestions:")[0].strip()
            if len(clean_message) < 200:  # Only speak short messages
                voice_manager.speak(clean_message)
    
    async def run_agent_loop(self):
        """Main agent loop"""
        self.print_banner()
        
        # Initial system check
        if not ollama_client.is_available():
            print(f"{Fore.RED}❌ Ollama is not available! Please start Ollama and ensure gemma3n model is installed.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Run: ollama list{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}If gemma3n is not listed, run: ollama pull gemma3n{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}🚀 Assistant ready! Type 'help' for commands or start asking questions.{Style.RESET_ALL}\n")
        
        while self.running:
            try:
                user_input = self.get_user_input()
                
                if not user_input:
                    continue
                
                # Handle system commands
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'voice':
                    self.voice_mode = not self.voice_mode
                    mode_text = "enabled" if self.voice_mode else "disabled"
                    print(f"{Fore.YELLOW}Voice mode {mode_text}{Style.RESET_ALL}")
                    if self.voice_mode and not voice_manager.is_available():
                        print(f"{Fore.RED}Warning: Voice system not available{Style.RESET_ALL}")
                    continue
                elif user_input.lower() == 'status':
                    self.print_status()
                    continue
                elif user_input.lower() == 'tasks':
                    self.show_tasks()
                    continue
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # Handle suggestion execution
                suggestion_match = re.match(r'(?:execute|do|run)\s+suggestion\s+(\d+)', user_input.lower())
                if suggestion_match and self.last_suggestions:
                    suggestion_num = int(suggestion_match.group(1)) - 1
                    if 0 <= suggestion_num < len(self.last_suggestions):
                        suggestion = self.last_suggestions[suggestion_num]
                        suggestion_text = suggestion if isinstance(suggestion, str) else suggestion.get('action', str(suggestion))
                        print(f"{Fore.BLUE}🤖 Executing suggestion: {suggestion_text}{Style.RESET_ALL}")
                        user_input = suggestion_text  # Execute the suggestion as if user typed it
                    else:
                        print(f"{Fore.RED}❌ Invalid suggestion number. Choose 1-{len(self.last_suggestions)}{Style.RESET_ALL}")
                        continue
                
                # Process with AI agent
                print(f"{Fore.BLUE}🤖 Processing...{Style.RESET_ALL}")
                start_time = time.time()
                
                response = task_executor.execute_task(user_input)
                
                end_time = time.time()
                processing_time = round(end_time - start_time, 2)
                
                self.process_response(response)
                
                # Store conversation
                memory_manager.store_conversation(
                    user_input, 
                    response.get('message', 'No response'),
                    {'processing_time': processing_time, 'voice_mode': self.voice_mode}
                )
                
                print(f"{Fore.BLUE}⏱️ Processed in {processing_time}s{Style.RESET_ALL}\n")
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print(f"{Fore.RED}❌ An error occurred: {e}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}The assistant will continue running...{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}👋 Goodbye! Assistant shutting down...{Style.RESET_ALL}")

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n{Fore.YELLOW}Received shutdown signal. Cleaning up...{Style.RESET_ALL}")
    sys.exit(0)

def main():
    """
    Main entry point - AUTO-LAUNCHES GUI
    """
    print("=" * 60)
    print("🤖 GEMMA3N ASSISTANT - AUTO-GUI LAUNCH")
    print("=" * 60)
    print("🚀 Starting advanced multi-tasking GUI interface...")
    print("💡 Enhanced AI agent with concurrent task execution")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    try:
        # Auto-launch GUI interface
        print("\n🎨 Launching multi-tasking GUI interface...")
        try:
            # Try to run the enhanced GUI
            import subprocess
            import sys
            return subprocess.call([sys.executable, "app.py"])
        except Exception as e:
            print(f"❌ GUI launch failed: {e}")
            print("🔄 Falling back to terminal interface...")
            return run_terminal_interface()
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
        return 0

def run_terminal_interface():
    """Run the legacy terminal interface"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Gemma3n Assistant Terminal Interface (Legacy)")
    
    try:
        # Create and run assistant
        assistant = GemmaAssistant()
        
        # Run the main loop
        if sys.platform == "win32":
            # On Windows, use the event loop properly
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(assistant.run_agent_loop())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        return 1
    
    logger.info("Gemma3n Assistant shutdown complete")
    return 0

if __name__ == "__main__":
    main()
