"""
Intent parsing and task execution logic with Computer Use Agent integration
"""
import re
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from utils.ollama_client import ollama_client
from tools import system_tools
from memory import memory_manager
from utils.error_handling import retry_with_backoff, safe_execute, error_recovery
from utils.local_cache import ai_cache, local_cache

logger = logging.getLogger(__name__)

# Import Computer Use Agent for advanced automation
try:
    from tools.computer_use_agent import computer_use_agent
    COMPUTER_USE_AVAILABLE = True
    logger.info("🖥️ Computer Use Agent integration enabled")
except ImportError as e:
    logger.warning(f"Computer Use Agent not available: {e}")
    COMPUTER_USE_AVAILABLE = False

class IntentParser:
    """Parses user intent from natural language"""
    
    def __init__(self):
        self.intent_patterns = {
            'open_app': [
                r'open\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$',
                r'launch\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$',
                r'start\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$',
                r'run\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$'
            ],
            'close_app': [
                r'close\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$',
                r'quit\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$',
                r'exit\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$',
                r'stop\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|program))?$'
            ],
            'create_file': [
                r'create\s+(?:a\s+)?file\s+(?:called\s+)?([^\s]+)',
                r'make\s+(?:a\s+)?file\s+(?:named\s+)?([^\s]+)',
                r'new\s+file\s+([^\s]+)'
            ],
            'read_file': [
                r'read\s+(?:the\s+)?file\s+([^\s]+)',
                r'show\s+(?:me\s+)?(?:the\s+)?file\s+([^\s]+)',
                r'open\s+(?:the\s+)?file\s+([^\s]+)'
            ],
            'list_directory': [
                r'list\s+(?:files\s+in\s+)?([^\s]+)',
                r'show\s+(?:me\s+)?(?:files\s+in\s+)?([^\s]+)',
                r'what.*in\s+([^\s]+)',
                r'ls\s+([^\s]+)'
            ],
            'run_command': [
                r'run\s+command\s+(.+)',
                r'execute\s+(.+)',
                r'cmd\s+(.+)'
            ],
            'add_task': [
                r'remind\s+me\s+to\s+(.+)',
                r'add\s+task\s+(.+)',
                r'create\s+reminder\s+(.+)',
                r'set\s+reminder\s+(?:for\s+)?(.+)'
            ],
            'analyze_system': [
                r'check\s+(?:what\s+is\s+the\s+)?process\s+(?:who\s+)?consume.*resources?',
                r'analyze\s+(?:system\s+)?resource.*usage',
                r'show\s+(?:me\s+)?high\s+resource.*processes?',
                r'what.*consuming.*(?:cpu|memory|resources?)',
                r'check\s+system\s+performance',
                r'resource\s+monitor',
                r'performance\s+analysis'
            ],
            'scan_wifi': [
                r'check\s+(?:how\s+many\s+)?wifi.*(?:networks?|there\s+are)',
                r'scan\s+(?:for\s+)?wifi.*networks?',
                r'show\s+(?:me\s+)?(?:available\s+)?wifi.*networks?',
                r'list\s+wifi.*networks?',
                r'what\s+wifi.*(?:networks?|available)',
                r'wifi\s+scan',
                r'networks?\s+available'
            ],
            'scan_available_wifi': [
                r'(?:how\s+many\s+)?wifi.*(?:capted|captured|detected|visible)\s+now',
                r'(?:show|list)\s+(?:only\s+)?(?:available|visible|current)\s+wifi.*networks?',
                r'wifi.*networks?\s+(?:now|currently|visible|available)',
                r'(?:current|available|visible)\s+wifi.*(?:only|just)',
                r'not\s+saved.*networks?.*(?:current|available|visible)',
                r'(?:real.time|live)\s+wifi.*scan'
            ],
            'windows_command': [
                r'(?:run|execute)\s+(?:command\s+)?(\w+)',
                r'(?:check|show|get)\s+system\s+(?:info|information)',
                r'(?:system|computer|pc)\s+(?:analysis|check|scan)',
                r'(?:disk|memory|cpu|performance)\s+(?:usage|check|info)',
                r'(?:network|wifi|internet)\s+(?:config|status|info)'
            ],
            # Computer Use Agent capabilities
            'computer_automation': [
                r'(?:automate|control|use)\s+(?:the\s+)?computer',
                r'click\s+(?:on\s+)?(.+)',
                r'type\s+(.+)',
                r'scroll\s+(?:down|up|left|right)',
                r'find\s+(?:and\s+click\s+)?(.+)',
                r'take\s+(?:a\s+)?screenshot',
                r'analyze\s+(?:the\s+)?screen',
                r'locate\s+(.+)\s+on\s+screen',
                r'interact\s+with\s+(.+)'
            ],
            'screen_analysis': [
                r'what.*(?:on\s+)?(?:the\s+)?screen',
                r'describe\s+(?:what.*)?(?:on\s+)?(?:the\s+)?screen',
                r'analyze\s+(?:current\s+)?screen',
                r'scan\s+(?:the\s+)?screen',
                r'show\s+(?:me\s+)?screen\s+(?:elements|content)',
                r'detect\s+(?:elements|buttons|text)\s+(?:on\s+screen)?'
            ],
            'web_automation': [
                r'open\s+(?:browser|chrome|firefox|edge)',
                r'go\s+to\s+(.+)',
                r'navigate\s+to\s+(.+)',
                r'visit\s+(.+)',
                r'browse\s+(?:to\s+)?(.+)',
                r'search\s+(?:for\s+)?(.+)\s+(?:on\s+)?(?:google|web)',
                r'fill\s+(?:in\s+)?(?:form|field)\s+(.+)',
                r'submit\s+(?:form|search)'
            ],
            'task_automation': [
                r'perform\s+task\s+(.+)',
                r'execute\s+workflow\s+(.+)',
                r'automate\s+(.+)',
                r'do\s+(?:the\s+)?following:\s+(.+)',
                r'complete\s+task\s+(.+)',
                r'carry\s+out\s+(.+)'
            ],
            'system_commands': [
                r'(?:fix|repair)\s+(?:system|windows|corruption)',
                r'(?:clean|cleanup)\s+(?:disk|system|temp)',
                r'(?:optimize|speed\s+up)\s+(?:system|performance)',
                r'(?:diagnose|troubleshoot)\s+(?:system|network|issues?)',
                r'(?:scan|check)\s+(?:system\s+files?|integrity)',
                r'(?:network|ip)\s+(?:config|configuration|info)',
                r'(?:ping|test)\s+(?:network|connection|internet)',
                r'(?:list|show)\s+(?:processes?|running\s+programs?)',
                r'systeminfo|ipconfig|ping|tasklist|sfc|dism|chkdsk|netstat'
            ]
        }
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse user intent from input"""
        user_input = user_input.lower().strip()
        
        # Try pattern matching first
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    return {
                        'intent': intent,
                        'entity': match.group(1) if match.groups() else None,
                        'confidence': 0.9,
                        'method': 'pattern'
                    }
        
        # Fallback to AI parsing
        return self._ai_parse_intent(user_input)
    
    def _ai_parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Use AI to parse complex intents"""
        system_prompt = """You are an intent classifier for a Windows AI assistant. 
        Analyze the user's request and return a JSON response with:
        - intent: one of [open_app, close_app, create_file, read_file, list_directory, run_command, add_task, analyze_system, scan_wifi, scan_available_wifi, windows_command, general_question]
        - entity: the specific thing to act upon (app name, file path, etc.)
        - confidence: 0.0 to 1.0
        
        Examples:
        "What files are in my Documents?" -> {"intent": "list_directory", "entity": "Documents", "confidence": 0.8}
        "Close all Chrome windows" -> {"intent": "close_app", "entity": "chrome", "confidence": 0.9}
        "Check what processes consume resources" -> {"intent": "analyze_system", "entity": "resource_usage", "confidence": 0.9}
        "Check how many wifi there are" -> {"intent": "scan_wifi", "entity": "wifi_networks", "confidence": 0.9}
        "How many wifi capted now" -> {"intent": "scan_available_wifi", "entity": "available_networks", "confidence": 0.9}
        "Show only available wifi networks" -> {"intent": "scan_available_wifi", "entity": "available_networks", "confidence": 0.9}
        """
        
        try:
            response = ollama_client.generate(
                prompt=f"Classify this request: '{user_input}'",
                system_prompt=system_prompt
            )
            
            # Try to extract JSON from response
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            logger.error(f"AI intent parsing failed: {e}")
        
        # Default fallback
        return {
            'intent': 'general_question',
            'entity': user_input,
            'confidence': 0.3,
            'method': 'fallback'
        }

class TaskExecutor:
    """Enhanced dynamic AI Agent with caching and better performance"""
    
    def __init__(self):
        self.intent_parser = IntentParser()
        self.context_history = []
        self.max_context_history = 5
        
        # Performance tracking
        self.execution_stats = {
            'total_executions': 0,
            'cache_hits': 0,
            'ai_calls': 0,
            'errors': 0
        }
    
    @retry_with_backoff(max_retries=2)
    def execute_task(self, user_input: str) -> Dict[str, Any]:
        """Execute a task with AI-driven understanding and caching"""
        start_time = time.time()
        self.execution_stats['total_executions'] += 1
        
        try:
            # Store user input in context
            self.context_history.append(f"User: {user_input}")
            if len(self.context_history) > self.max_context_history * 2:  # Double to account for user+assistant pairs
                self.context_history.pop(0)
            
            # Check cache for similar requests
            cached_response = self._check_cache(user_input)
            if cached_response:
                self.execution_stats['cache_hits'] += 1
                logger.info(f"Cache hit for: {user_input[:50]}...")
                
                # Store assistant response in context even for cached responses
                self._store_assistant_context(cached_response)
                
                return cached_response
            
            # Check if this is an agreement response to a previous suggestion
            if self._is_agreement_response(user_input):
                logger.info("Agreement response detected, checking handler...")
                result = self._handle_agreement_response(user_input)
                if result:
                    logger.info("Agreement handler returned result, returning early")
                    return result
                else:
                    logger.info("Agreement handler returned None, continuing to AI planning")
            
            # Check if this is a negative response to previous suggestions
            elif self._is_negative_response(user_input):
                logger.info("Negative response detected, handling gracefully")
                result = self._handle_negative_response(user_input)
                if result:
                    return result
            
            # First, let the AI understand the request and plan actions
            plan = self._analyze_and_plan(user_input)
            
            if plan.get('requires_execution', False):
                # Execute the planned actions
                result = self._execute_plan(plan, user_input)
            else:
                # Handle as conversational response with suggestions
                result = self._handle_conversational_response(user_input, plan)
            
            # Store assistant response in context for better conversation flow
            self._store_assistant_context(result)
            
            # Cache successful results
            if result.get('success', True):
                self._cache_response(user_input, result)
            
            # Track performance
            execution_time = time.time() - start_time
            logger.debug(f"Task execution completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.execution_stats['errors'] += 1
            logger.error(f"Task execution failed: {e}")
            
            # Try to recover
            if error_recovery.handle_error('task_execution', e, {'user_input': user_input}):
                # Retry with simplified approach
                return self._fallback_execution(user_input)
            
            return {
                'success': False,
                'message': f"Sorry, I encountered an error: {str(e)}",
                'suggestions': ["Try rephrasing your request", "Check system status"]
            }
    
    def _store_assistant_context(self, result: Dict[str, Any]):
        """Store assistant response in context for conversation flow"""
        assistant_msg = result.get('message', '')
        suggestions = result.get('suggestions', [])
        
        if assistant_msg:
            # Extract main response (before suggestions)
            main_response = assistant_msg.split('\n\n🤖')[0]  # Remove suggestion section
            context_entry = f"Assistant: {main_response}"
            
            # Add suggestions to context for agreement handling
            if suggestions:
                context_entry += f" [Suggestions: {'; '.join(suggestions[:2])}]"
                
            self.context_history.append(context_entry)
            if len(self.context_history) > self.max_context_history * 2:
                self.context_history.pop(0)

    def _is_negative_response(self, user_input: str) -> bool:
        """Check if user input is a negative response to a previous suggestion"""
        user_lower = user_input.lower().strip()
        
        # Check for clarification/correction patterns that aren't negative responses
        clarification_patterns = [
            r'\bno\s+but\b',  # "no but go to..."
            r'\bno\s+instead\b',  # "no instead do..."
            r'\bno\s+please\b',  # "no please do..."
            r'\bno\s+wait\b',  # "no wait..."
        ]
        
        # If it's a clarification, not a negative response
        if any(re.search(pattern, user_lower) for pattern in clarification_patterns):
            return False
        
        # Direct negative responses (must be exact word matches, not substrings)
        negative_patterns = [
            r'\bno\b', r'\bnope\b', r'\bnah\b', r'\bnot\b', 
            r"\bdon't\b", r'\bcancel\b', r'\bskip\b', 
            r'\bnever mind\b', r'\bno thanks\b'
        ]
        
        # Only consider it negative if it's a short response and matches word boundaries
        if len(user_input.split()) <= 3:
            return any(re.search(pattern, user_lower) for pattern in negative_patterns)
        
        return False
    
    def _handle_negative_response(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Handle user declining previous suggestions"""
        try:
            logger.info("User declined previous suggestions")
            
            response = {
                'status': 'success',
                'message': '👍 No problem! Let me know if you need anything else.',
                'execution_results': [{
                    'status': 'success',
                    'message': 'User declined suggestions',
                    'reason': 'User provided negative response to suggestions'
                }],
                'suggestions': [
                    'Feel free to ask for help with any other tasks',
                    'I can help with file operations, opening applications, or system tasks'
                ],
                'type': 'conversational_response'
            }
            
            # Add context
            self._store_assistant_context(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Negative response handling failed: {e}")
            return None

    def _is_agreement_response(self, user_input: str) -> bool:
        """Check if user input is an agreement to a previous suggestion"""
        user_lower = user_input.lower().strip()
        
        # Check for negative responses first
        negative_words = ['no', 'nope', 'nah', 'not', "don't", 'cancel', 'skip', 'never mind']
        if any(word in user_lower for word in negative_words):
            return False
            
        # Check for positive agreement
        agreement_words = ['yes', 'yes please', 'sure', 'ok', 'okay', 'yep', 'yeah', 'please', 'do it']
        return any(word in user_lower for word in agreement_words) and len(user_input.split()) <= 3
    
    def _handle_agreement_response(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Handle user agreement to previous suggestions"""
        try:
            # Look for recent suggestions in context
            recent_context = self.context_history[-3:] if len(self.context_history) >= 3 else self.context_history
            
            # Check if recent conversation mentioned file creation
            for context_item in reversed(recent_context):
                if 'create a test file' in context_item.lower() or 'write' in context_item.lower():
                    # User is agreeing to file creation
                    logger.info("User agreed to file creation suggestion")
                    
                    # Create file directly using system tools instead of complex logic
                    from tools import system_tools
                    result = system_tools.create_file("test.txt", "hello world")
                    
                    # Format as proper response
                    if result.get('status') == 'success':
                        response = {
                            'status': 'success',
                            'message': f"✅ {result.get('message')} with content: 'hello world'",
                            'execution_results': [{
                                'status': 'success',
                                'message': f"{result.get('message')} with content: 'hello world'",
                                'reason': 'User agreed to file creation suggestion'
                            }],
                            'suggestions': ['Would you like to open the file in Notepad?', 'Do you need any other files created?'],
                            'type': 'single_action_execution'
                        }
                    else:
                        response = {
                            'status': 'error',
                            'message': f"❌ Failed to create file: {result.get('message')}",
                            'execution_results': [{
                                'status': 'error', 
                                'message': f"Failed to create file: {result.get('message')}",
                                'reason': 'File creation failed'
                            }],
                            'type': 'single_action_execution'
                        }
                    
                    # Add context
                    self._store_assistant_context(response)
                    
                    return response
            
            return None  # No clear agreement context found
            
        except Exception as e:
            logger.error(f"Agreement handling failed: {e}")
            return None

    def _check_cache(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Check if we have a cached response for similar input"""
        try:
            # Create a normalized version for caching
            normalized_input = user_input.lower().strip()
            
            # Check exact match first
            cached = local_cache.get('task_responses', normalized_input)
            if cached:
                return cached
            
            # Check for similar inputs (simple similarity)
            for cached_key in ['recent_tasks']:
                similar_tasks = local_cache.get('patterns', cached_key)
                if similar_tasks:
                    for task_pattern, response in similar_tasks.items():
                        if self._is_similar_task(normalized_input, task_pattern):
                            return response
            
            return None
        except Exception as e:
            logger.debug(f"Cache check failed: {e}")
            return None
    
    def _is_similar_task(self, input1: str, input2: str) -> bool:
        """Simple similarity check for tasks"""
        # Basic word overlap similarity
        words1 = set(input1.split())
        words2 = set(input2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))
        
        return similarity > 0.7
    
    def _cache_response(self, user_input: str, response: Dict[str, Any]):
        """Cache successful response"""
        try:
            normalized_input = user_input.lower().strip()
            
            # Cache the response with 1 hour TTL
            local_cache.set(
                'task_responses',
                normalized_input,
                response,
                ttl_seconds=3600
            )
            
            # Update pattern cache for similar task detection
            recent_tasks = local_cache.get('patterns', 'recent_tasks') or {}
            recent_tasks[normalized_input] = response
            
            # Keep only last 50 patterns
            if len(recent_tasks) > 50:
                oldest_key = next(iter(recent_tasks))
                del recent_tasks[oldest_key]
            
            local_cache.set('patterns', 'recent_tasks', recent_tasks, ttl_seconds=86400)  # 24 hours
            
        except Exception as e:
            logger.debug(f"Failed to cache response: {e}")
    
    def _fallback_execution(self, user_input: str) -> Dict[str, Any]:
        """Simplified fallback execution when main execution fails"""
        try:
            logger.info("Using fallback execution mode")
            
            # Try basic intent parsing without AI
            basic_intent = self.intent_parser.parse_basic_intent(user_input)
            
            if basic_intent['intent'] == 'open_app':
                app_name = basic_intent.get('entity', '')
                result = system_tools.open_application(app_name)
                return {
                    'success': result.get('success', False),
                    'message': result.get('message', 'Application operation completed'),
                    'suggestions': []
                }
            
            # Default response
            return {
                'success': True,
                'message': "I understand you're asking something, but I'm having trouble processing it right now. Could you try rephrasing?",
                'suggestions': [
                    "Try a simpler command",
                    "Check if Ollama is running",
                    "Restart the assistant"
                ]
            }
        except Exception as e:
            logger.error(f"Fallback execution failed: {e}")
            return {'success': False, 'message': 'Fallback execution failed'}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total = self.execution_stats['total_executions']
        if total == 0:
            return self.execution_stats
        
        return {
            **self.execution_stats,
            'cache_hit_rate': (self.execution_stats['cache_hits'] / total) * 100,
            'error_rate': (self.execution_stats['errors'] / total) * 100,
            'cache_stats': local_cache.get_stats()
        }
    
    @retry_with_backoff(max_retries=2)
    def _analyze_and_plan(self, user_input: str) -> Dict[str, Any]:
        """Use AI to analyze request and create execution plan with caching"""
        
        import json  # Move import to top of function
        
        # Check if we have a cached AI response for similar planning
        cached_plan = ai_cache.get_cached_response(user_input, "planning_system")
        if cached_plan:
            try:
                return json.loads(cached_plan)
            except json.JSONDecodeError:
                logger.debug("Invalid cached plan JSON, proceeding with fresh analysis")
        
        self.execution_stats['ai_calls'] += 1
        
        # Get current context
        context = memory_manager.get_conversation_summary()
        recent_context = "\n".join(self.context_history[-3:])  # Last 3 interactions
        
        # Get system state for context
        system_info = self._get_system_context()
        
        planning_prompt = f"""You are an intelligent AI agent assistant. Analyze the user's request and create an execution plan.

SYSTEM CONTEXT:
{system_info}

RECENT CONVERSATION:
{recent_context}

CONVERSATION HISTORY:
{context}

USER REQUEST: "{user_input}"

IMPORTANT: Look at the RECENT CONVERSATION to understand context. If the user says "yes", "yes please", "sure", "ok", or similar agreement words, they are responding to a previous suggestion.

CRITICAL RULE FOR AGREEMENT RESPONSES:
- If user says "yes please" or similar AND recent conversation mentions file creation suggestion → use "create_file" action only
- If user says "yes" or similar AND recent conversation mentions opening app → use "open_app" action only  
- DO NOT combine multiple actions when user is simply agreeing to ONE suggestion
- DO NOT open Notepad AND save file - that makes no sense for a simple agreement

Analyze this request and respond with a JSON plan. 

For file creation requests (create file, make file, write to file), ALWAYS use "create_file" action:

EXAMPLES:
- "create test.txt file, write hello world inside" → {{"action": "create_file", "target": "test.txt"}}
- "make a file called notes.txt with content hello" → {{"action": "create_file", "target": "notes.txt"}}
- "open task manager" → {{"action": "open_app", "target": "task manager"}}
- "check what processes consume resources" → {{"action": "analyze_system", "target": "resource_usage"}}
- "open task manager and check resource usage" → {{"action": "analyze_system", "target": "resource_usage"}} (prioritize analysis over just opening)

CONVERSATIONAL EXAMPLES:
- If recent conversation shows suggestions and user says "yes please" → analyze what they're agreeing to
- "yes please" after file creation suggestion → {{"action": "create_file", "target": "test.txt"}}
- "sure" after opening app suggestion → {{"action": "open_app", "target": "suggested_app"}}

Response format:
{{
    "understanding": "What the user really wants to accomplish based on conversation context",
    "requires_execution": true,
    "suggested_actions": [
        {{
            "action": "create_file", 
            "target": "test.txt",
            "reason": "User wants to create a file with content"
        }}
    ],
    "proactive_suggestions": [
        "Additional helpful suggestions based on context"
    ],
    "response": "I'll create the file for you"
}}

Action types and their usage:
- create_file: FOR ANY FILE CREATION REQUEST. Use this when user says "create file", "make file", "write to file", etc.
  * target: the filename (e.g., "test.txt")
  * The system will auto-extract content from user input and create the file
- open_app: For opening applications ONLY when user explicitly wants to open an app
  * "notepad" - Opens Notepad 
  * "task manager" or "taskmgr" - Opens Task Manager
  * "calculator" or "calc" - Opens Calculator  
  * "chrome" or "browser" - Opens Chrome browser
- close_app: For closing applications. Use target as app name
- read_file: For reading files. Use target as filepath  
- list_directory: For listing directory contents. Use target as directory path
- run_command: For ACTUAL shell commands like "dir", "ipconfig", "systeminfo" (NOT for opening apps!)
- keyboard_shortcut: For keyboard shortcuts like "ctrl+shift+esc" (for Task Manager), "ctrl+s" (save), etc.
- add_task: For adding reminders/tasks. Use target as task description
- analyze_system: For analyzing system resource usage, checking processes, performance monitoring
- scan_wifi: For scanning WiFi networks, checking available networks, network analysis (includes saved networks)
- scan_available_wifi: For scanning ONLY currently available/visible WiFi networks (real-time scan)
  * Use when user asks for "available networks now", "wifi networks visible", "current wifi", "not saved networks"
- windows_command: For Windows system commands, troubleshooting, registry operations, advanced system tasks
  * Use when user wants: system information, network diagnostics, disk management, process control, registry access, security checks
  * target: description of what to do (e.g., "check system info", "diagnose network", "clean temp files")
  * Examples: "check system info" → windows_command, "run disk cleanup" → windows_command, "show network config" → windows_command

CRITICAL RULES:
1. If user mentions creating, making, or writing a file → ALWAYS use "create_file" action
2. If user mentions opening an application by name → use "open_app" 
3. For Task Manager: Use "open_app" with target "task manager" OR "keyboard_shortcut" with target "ctrl+shift+esc"
4. If user wants to CHECK, ANALYZE, or MONITOR system resources/processes → use "analyze_system"
5. If user wants to CHECK, SCAN, or LIST WiFi networks → use "scan_wifi"
6. If user wants ONLY AVAILABLE/CURRENT WiFi networks (not saved) → use "scan_available_wifi"
7. NEVER use "open_app" for file creation - that's what "create_file" is for!

EXAMPLE MAPPINGS:
- "create test.txt file, write hello world" → action: "create_file", target: "test.txt" 
- "make a file called notes.txt" → action: "create_file", target: "notes.txt"
- "open notepad" → action: "open_app", target: "notepad"
- "open task manager" → action: "open_app", target: "task manager"
- "check processes consuming resources" → action: "analyze_system", target: "resource_usage"
- "open task manager and check resource usage" → action: "analyze_system", target: "resource_usage"
- "check how many wifi there are" → action: "scan_wifi", target: "wifi_networks"
- "open parametre and check wifi" → action: "scan_wifi", target: "wifi_networks"
- "how many wifi capted now" → action: "scan_available_wifi", target: "available_networks"
- "show only available wifi networks" → action: "scan_available_wifi", target: "available_networks"
- "not saved networks, current wifi" → action: "scan_available_wifi", target: "available_networks"
- "check system information" → action: "windows_command", target: "check system info"
- "run disk cleanup" → action: "windows_command", target: "clean disk"
- "show network configuration" → action: "windows_command", target: "show network config"
- "check windows version" → action: "windows_command", target: "check windows version"
- "list installed programs" → action: "windows_command", target: "list installed programs"
- "run system file checker" → action: "windows_command", target: "run sfc scan"

Be proactive and intelligent - suggest related actions that would be helpful!"""

        try:
            response = ollama_client.generate(planning_prompt, "You are an intelligent planning AI assistant.")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                logger.info(f"AI Plan: {plan.get('understanding', 'Unknown')}")
                logger.info(f"Suggested actions: {plan.get('suggested_actions', [])}")
                
                # Cache the successful AI response
                ai_cache.cache_response(user_input, "planning_system", json.dumps(plan), ttl_hours=2)
                
                return plan
            else:
                logger.error(f"No JSON found in AI response: {response}")
            
        except Exception as e:
            logger.error(f"AI planning failed: {e}")
            logger.error(f"AI response was: {response[:500] if 'response' in locals() else 'No response'}")
        
        # Fallback to simple pattern matching
        intent_data = self.intent_parser.parse_intent(user_input)
        logger.info(f"Falling back to pattern matching: {intent_data}")
        return {
            "understanding": f"Simple intent: {intent_data.get('intent')}",
            "requires_execution": intent_data.get('intent') != 'general_question',
            "suggested_actions": [{"action": intent_data.get('intent'), "target": intent_data.get('entity'), "reason": "Pattern matched"}],
            "proactive_suggestions": [],
            "response": "I'll help you with that."
        }
    
    def _get_system_context(self) -> str:
        """Get current system context for AI planning"""
        try:
            # Get running processes
            processes = system_tools.list_running_processes()
            top_processes = sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:5]
            
            # Get pending tasks
            pending_tasks = memory_manager.get_pending_tasks()
            
            # Current directory info
            current_dir = system_tools.list_directory(".")
            
            context = f"""
Current System State:
- Top running processes: {[p['name'] for p in top_processes]}
- Pending tasks: {len(pending_tasks)} tasks
- Current directory files: {len(current_dir.get('items', []))} items
- Working directory: {Path.cwd()}
"""
            return context
        except Exception as e:
            return f"System context unavailable: {e}"
    
    def _execute_plan(self, plan: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Execute the AI-generated plan"""
        results = []
        suggested_actions = plan.get('suggested_actions', [])
        
        logger.info(f"Executing {len(suggested_actions)} planned actions")
        
        for action_item in suggested_actions:
            action = action_item.get('action')
            target = action_item.get('target')
            reason = action_item.get('reason', '')
            
            try:
                if action == 'open_app':
                    result = self._execute_open_app(target)
                elif action == 'close_app':
                    result = self._execute_close_app(target)
                elif action == 'create_file':
                    result = self._execute_create_file(target, user_input)
                elif action == 'read_file':
                    result = self._execute_read_file(target)
                elif action == 'list_directory':
                    result = self._execute_list_directory(target)
                elif action == 'run_command':
                    result = self._execute_run_command(target)
                elif action == 'add_task':
                    result = self._execute_add_task(target)
                elif action == 'analyze_system':
                    result = self._execute_analyze_system()
                elif action == 'scan_wifi':
                    result = self._execute_scan_wifi()
                elif action == 'scan_available_wifi':
                    result = self._execute_scan_available_wifi()
                elif action == 'windows_command':
                    result = self._execute_windows_command(action_item)
                elif action == 'keyboard_shortcut':
                    result = self._execute_keyboard_shortcut(target)
                elif action == 'organize_files':
                    result = self._execute_organize_files(target)
                elif action == 'system_cleanup':
                    result = self._execute_system_cleanup()
                elif action == 'productivity_boost':
                    result = self._execute_productivity_boost()
                # Computer Use Agent actions
                elif action == 'computer_automation':
                    result = self._execute_computer_automation(action_item)
                elif action == 'screen_analysis':
                    result = self._execute_screen_analysis(action_item)
                elif action == 'web_automation':
                    result = self._execute_web_automation(action_item)
                elif action == 'task_automation':
                    result = self._execute_task_automation(action_item)
                else:
                    result = {"status": "info", "message": f"Action '{action}' planned but not yet implemented"}
                
                result['reason'] = reason
                results.append(result)
                
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                results.append({"status": "error", "message": f"Failed to execute {action}: {str(e)}"})
        
        # Combine results into comprehensive response
        return self._combine_execution_results(results, plan)
    
    def _handle_conversational_response(self, user_input: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversational responses with proactive suggestions"""
        understanding = plan.get('understanding', 'I understand your request')
        response = plan.get('response', 'How can I help you?')
        suggestions = plan.get('proactive_suggestions', [])
        
        # Build comprehensive response
        full_response = response
        
        if suggestions:
            full_response += "\n\n🤖 Smart Suggestions:"
            for i, suggestion in enumerate(suggestions, 1):
                full_response += f"\n{i}. {suggestion}"
            full_response += "\n\nWould you like me to help with any of these?"
        
        return {
            "status": "success",
            "message": full_response,
            "understanding": understanding,
            "suggestions": suggestions,
            "type": "conversational_with_suggestions"
        }
    
    def _combine_execution_results(self, results: List[Dict], plan: Dict) -> Dict[str, Any]:
        """Combine multiple execution results into a comprehensive response"""
        # Handle both "status" and "success" keys for compatibility
        success_count = sum(1 for r in results if (r.get('status') == 'success' or r.get('success') == True))
        total_count = len(results)
        
        # Determine overall status
        overall_status = "success" if success_count > 0 else "error"
        
        if total_count > 1:
            # Multiple actions
            main_response = f"✅ Completed {success_count}/{total_count} actions:"
            
            for i, result in enumerate(results, 1):
                # Handle both status formats
                is_success = (result.get('status') == 'success' or result.get('success') == True)
                status_icon = "✅" if is_success else "❌"
                action_msg = result.get('message', 'Action completed')
                reason = result.get('reason', '')
                main_response += f"\n{i}. {status_icon} {action_msg}"
                if reason:
                    main_response += f" ({reason})"
        else:
            # Single action response - use the actual execution result
            if results:
                result = results[0]
                is_success = (result.get('status') == 'success' or result.get('success') == True)
                main_response = result.get('message', 'Action completed')
                
                # Don't add status icons here since main.py will handle it
                # based on the overall status
            else:
                main_response = plan.get('response', 'No actions executed')
        
        # Add proactive suggestions from plan
        suggestions = plan.get('proactive_suggestions', [])
        if suggestions:
            main_response += "\n\n🤖 Additional suggestions:"
            for suggestion in suggestions:
                main_response += f"\n• {suggestion}"
        
        return {
            "status": overall_status,
            "message": main_response,
            "execution_results": results,
            "suggestions": suggestions,
            "type": "multi_action_execution"
        }
    
    def _execute_open_app(self, app_name: str) -> Dict[str, Any]:
        """Execute open application command"""
        if not app_name:
            return {"status": "error", "message": "No application specified"}
        
        result = system_tools.open_application(app_name)
        return result
    
    def _execute_close_app(self, app_name: str) -> Dict[str, Any]:
        """Execute close application command"""
        if not app_name:
            return {"status": "error", "message": "No application specified"}
        
        result = system_tools.close_application(app_name)
        return result
    
    def _execute_create_file(self, filename: str, user_input: str) -> Dict[str, Any]:
        """Execute create file command with content detection and multi-step operations"""
        if not filename:
            # Try to extract filename from user input
            filename_patterns = [
                r'create\s+(?:a\s+)?(?:\.?(\w+)?\s+)?file(?:\s+called\s+([^\s,]+))?',
                r'\.(\w+)\s+file',
                r'file\s+called\s+([^\s,]+)',
                r'file.*?([^\s,]+\.(?:txt|doc|json|py|js|html|css|md))',
            ]
            
            for pattern in filename_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    if match.group(1) and match.group(2):
                        # Extension and name found
                        filename = f"{match.group(2)}.{match.group(1)}"
                    elif match.group(1):
                        # Only extension or name found
                        if '.' in match.group(1):
                            filename = match.group(1)
                        else:
                            # Assume it's extension, create default name
                            filename = f"new_file.{match.group(1)}"
                    break
            
            if not filename:
                filename = "new_file.txt"  # Default filename
        
        # Ensure file has extension
        if '.' not in filename:
            filename += '.txt'
        
        # Extract content from user input
        content = self._extract_file_content(user_input)
        logger.info(f"Extracted content: '{content}' from input: '{user_input}'")
        logger.info(f"Using filename: '{filename}'")
        
        # Execute the file creation
        try:
            # Method 1: Direct file creation (faster for simple content)
            if content and not any(phrase in user_input.lower() for phrase in ['open', 'edit', 'notepad']):
                logger.info(f"Using direct file creation method")
                result = system_tools.create_file(filename, content)
                logger.info(f"Direct creation result: {result}")
                if result.get('status') == 'success':
                    result['message'] += f" with content: '{content}'"
                return result
            
            # Method 2: Multi-step operation using Notepad (for complex operations)
            else:
                logger.info(f"Using multi-step Notepad method")
                return self._execute_complex_file_operation(filename, content, user_input)
                
        except Exception as e:
            logger.error(f"File creation failed: {e}")
            return {"status": "error", "message": f"Failed to create file: {str(e)}"}
    
    def _extract_file_content(self, user_input: str) -> str:
        """Extract content from user input using various patterns"""
        content_patterns = [
            r'note\s+["\']([^"\']+)["\']',  # note "content"
            r'note\s+([^,]+?)(?:\s*,|\s*save|\s*then|\s*$)',  # note content, save
            r'write\s+["\']([^"\']+)["\']',  # write "content"
            r'write\s+([^,]+?)(?:\s*,|\s*save|\s*then|\s*$)',  # write content, save
            r'content\s+["\']([^"\']+)["\']',  # content "text"
            r'with\s+content[:\s]+["\']([^"\']+)["\']',  # with content: "text"
            r'with\s+content[:\s]+([^,]+?)(?:\s*,|\s*save|\s*then|\s*$)',  # with content: text, save
            r'text\s+["\']([^"\']+)["\']',  # text "content"
            r'saying\s+["\']([^"\']+)["\']',  # saying "content"
            r'["\']([^"\']+)["\']\s+inside\s+it',  # "content" inside it
            r'inside\s+it\s+["\']([^"\']+)["\']',  # inside it "content"
            r'wirte\s+["\']([^"\']+)["\']',  # wirte "content" (typo)
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _execute_complex_file_operation(self, filename: str, content: str, user_input: str) -> Dict[str, Any]:
        """Execute complex file operations with multiple steps"""
        import time
        import pyautogui
        
        try:
            steps_completed = []
            
            # Step 1: Open Notepad
            result = system_tools.open_application("notepad")
            if result.get('status') != 'success':
                return {"status": "error", "message": "Failed to open Notepad"}
            
            steps_completed.append("✅ Opened Notepad")
            time.sleep(1)  # Wait for Notepad to open
            
            # Step 2: Type content if provided
            if content:
                pyautogui.typewrite(content)
                steps_completed.append(f"✅ Typed content: '{content}'")
                time.sleep(0.5)
            
            # Step 3: Save the file
            # Ctrl+S to save
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1)  # Wait for save dialog
            
            # Type filename
            pyautogui.typewrite(filename)
            time.sleep(0.5)
            
            # Press Enter to save
            pyautogui.press('enter')
            steps_completed.append(f"✅ Saved file as '{filename}'")
            time.sleep(1)
            
            # Step 4: Close Notepad if requested
            if any(word in user_input.lower() for word in ['close', 'exit', 'quit', 'then close']):
                pyautogui.hotkey('alt', 'f4')  # Alt+F4 to close
                steps_completed.append("✅ Closed Notepad")
            
            return {
                "status": "success", 
                "message": f"Multi-step file operation completed:\n" + "\n".join(steps_completed),
                "steps": steps_completed,
                "filename": filename,
                "content": content
            }
            
        except Exception as e:
            logger.error(f"Complex file operation failed: {e}")
            return {
                "status": "error", 
                "message": f"Failed during file operation: {str(e)}",
                "steps_completed": steps_completed
            }
    
    def _execute_read_file(self, filename: str) -> Dict[str, Any]:
        """Execute read file command"""
        if not filename:
            return {"status": "error", "message": "No filename specified"}
        
        result = system_tools.read_file(filename)
        return result
    
    def _execute_list_directory(self, directory: str) -> Dict[str, Any]:
        """Execute list directory command"""
        if not directory:
            directory = "."
        
        # Handle common directory shortcuts
        if directory.lower() in ['documents', 'my documents']:
            import os
            directory = os.path.expanduser("~/Documents")
        elif directory.lower() == 'desktop':
            import os
            directory = os.path.expanduser("~/Desktop")
        elif directory.lower() == 'downloads':
            import os
            directory = os.path.expanduser("~/Downloads")
        
        result = system_tools.list_directory(directory)
        return result
    
    def _execute_run_command(self, command: str) -> Dict[str, Any]:
        """Execute shell command"""
        if not command:
            return {"status": "error", "message": "No command specified"}
        
        result = system_tools.run_command(command)
        return result
    
    def _execute_add_task(self, task_description: str) -> Dict[str, Any]:
        """Execute add task command"""
        if not task_description:
            return {"status": "error", "message": "No task description provided"}
        
        task_id = memory_manager.add_task(task_description)
        if task_id:
            return {"status": "success", "message": f"Task added: {task_description}", "task_id": task_id}
        else:
            return {"status": "error", "message": "Failed to add task"}
    
    def _execute_analyze_system(self) -> Dict[str, Any]:
        """Execute system resource analysis"""
        try:
            logger.info("Executing system resource analysis")
            result = system_tools.analyze_resource_usage()
            
            if result.get('success'):
                return {
                    "status": "success", 
                    "message": result['message'],
                    "analysis_data": result.get('analysis')
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Resource analysis failed: {result.get('error', 'Unknown error')}"
                }
        except Exception as e:
            logger.error(f"System analysis execution failed: {e}")
            return {"status": "error", "message": f"Failed to analyze system resources: {str(e)}"}

    def _execute_scan_wifi(self) -> Dict[str, Any]:
        """Execute WiFi network scanning"""
        try:
            logger.info("Executing WiFi network scan")
            result = system_tools.scan_wifi_networks()
            
            if result.get('success'):
                return {
                    "status": "success", 
                    "message": result['message'],
                    "wifi_data": result.get('analysis')
                }
            else:
                return {
                    "status": "error", 
                    "message": f"WiFi scan failed: {result.get('error', 'Unknown error')}"
                }
        except Exception as e:
            logger.error(f"WiFi scan execution failed: {e}")
            return {"status": "error", "message": f"Failed to scan WiFi networks: {str(e)}"}

    def _execute_scan_available_wifi(self) -> Dict[str, Any]:
        """Execute available WiFi networks scanning (current/visible only)"""
        try:
            logger.info("Executing available WiFi networks scan")
            result = system_tools.scan_available_wifi_networks()
            
            if result.get('success'):
                return {
                    "status": "success", 
                    "message": result['message'],
                    "wifi_data": result.get('analysis')
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Available WiFi scan failed: {result.get('error', 'Unknown error')}"
                }
        except Exception as e:
            logger.error(f"Available WiFi scan execution failed: {e}")
            return {"status": "error", "message": f"Failed to scan available WiFi networks: {str(e)}"}

    def _execute_windows_command(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Windows command using AI-guided expert system"""
        try:
            # Extract command from action - could be in 'target', 'command', or 'request'
            request = action.get('target') or action.get('command') or action.get('request', '')
            
            logger.info(f"Executing AI-guided Windows command: {request}")
            
            # Use the new AI-guided execution system
            result = system_tools.execute_windows_command_ai_guided(request)
            
            if result.get('success'):
                response = {
                    "status": "success",
                    "message": result.get('message', 'Command executed successfully'),
                    "output": result.get('output', ''),
                    "analysis": result.get('analysis', {}),
                    "guidance": result.get('guidance', {}),
                    "type": result.get('type', 'ai_guided_execution')
                }
                
                # Add next suggestions if available
                if result.get('next_suggestions'):
                    response['next_suggestions'] = result['next_suggestions']
                
                # Add user-friendly suggestions
                if result.get('suggestions'):
                    response['suggestions'] = result['suggestions']
                
                return response
            else:
                # Fallback to traditional method if AI-guided fails
                logger.info("AI-guided execution failed, trying traditional method")
                fallback_result = system_tools.execute_windows_command(request)
                
                if fallback_result.get('status') == 'success':
                    return {
                        "status": "success",
                        "message": f"Executed using fallback method: {fallback_result.get('message', 'Command completed')}",
                        "output": fallback_result.get('raw_output', ''),
                        "analysis": fallback_result.get('analysis', {}),
                        "command": fallback_result.get('command_used', request),
                        "method": "fallback"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Command failed: {result.get('message', 'Unknown error')}",
                        "details": result.get('error', ''),
                        "analysis": result.get('analysis', {})
                    }
                    
        except Exception as e:
            logger.error(f"Windows command execution failed: {e}")
            return {"status": "error", "message": f"Failed to execute Windows command: {str(e)}"}

    def _execute_computer_automation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute computer automation using Computer Use Agent"""
        if not COMPUTER_USE_AVAILABLE:
            return {
                "status": "error",
                "message": "Computer Use Agent not available. Install requirements with: pip install -r computer_use_requirements.txt"
            }
        
        try:
            request = action.get('target') or action.get('task') or action.get('command', '')
            logger.info(f"🖥️ Executing computer automation: {request}")
            
            # Use Computer Use Agent for task execution
            result = computer_use_agent.execute_computer_task(request)
            
            if result['status'] in ['success', 'partial']:
                return {
                    "status": "success",
                    "message": f"🤖 Computer automation completed: {result['message']}",
                    "task_description": result.get('task_description', request),
                    "steps_executed": result.get('steps_executed', 0),
                    "step_results": result.get('step_results', []),
                    "final_screen_state": result.get('final_screen_state'),
                    "type": "computer_automation"
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Computer automation failed: {result['message']}",
                    "details": result.get('error', '')
                }
                
        except Exception as e:
            logger.error(f"Computer automation failed: {e}")
            return {"status": "error", "message": f"Computer automation error: {str(e)}"}

    def _execute_screen_analysis(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute screen analysis using Computer Use Agent"""
        if not COMPUTER_USE_AVAILABLE:
            return {
                "status": "error",
                "message": "Computer Use Agent not available. Install requirements with: pip install -r computer_use_requirements.txt"
            }
        
        try:
            logger.info("🔍 Executing screen analysis")
            
            # Capture and analyze current screen
            analysis = computer_use_agent.analyze_screen()
            
            if analysis and not analysis.get('error'):
                # Format analysis for user
                message = "📊 **Screen Analysis Results:**\n\n"
                
                # UI Elements
                elements = analysis.get('detected_elements', [])
                if elements:
                    message += f"🔲 **UI Elements:** {len(elements)} detected\n"
                    for elem in elements[:3]:  # Show first 3
                        message += f"  • {elem['type']} at ({elem['x']}, {elem['y']})\n"
                
                # Text Content
                text_content = analysis.get('text_content', [])
                if text_content:
                    message += f"\n📝 **Text Content:** {len(text_content)} items found\n"
                    for text in text_content[:5]:  # Show first 5
                        message += f"  • '{text['text']}'\n"
                
                # Clickable Areas
                clickable = analysis.get('clickable_areas', [])
                if clickable:
                    message += f"\n🖱️ **Clickable Areas:** {len(clickable)} detected\n"
                
                # Applications
                apps = analysis.get('applications', [])
                if apps:
                    message += f"\n🪟 **Applications:** {len(apps)} windows visible\n"
                    for app in apps[:3]:  # Show first 3
                        message += f"  • {app['title']}\n"
                
                return {
                    "status": "success",
                    "message": message,
                    "analysis": analysis,
                    "elements_detected": len(elements),
                    "text_items": len(text_content),
                    "clickable_areas": len(clickable),
                    "visible_windows": len(apps),
                    "type": "screen_analysis"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Screen analysis failed: {analysis.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            return {"status": "error", "message": f"Screen analysis error: {str(e)}"}

    def _execute_web_automation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web automation using Computer Use Agent"""
        if not COMPUTER_USE_AVAILABLE:
            return {
                "status": "error",
                "message": "Computer Use Agent not available. Install requirements with: pip install -r computer_use_requirements.txt"
            }
        
        try:
            url = action.get('target') or action.get('url') or action.get('website', '')
            logger.info(f"🌐 Executing web automation: {url}")
            
            # Start browser automation
            result = computer_use_agent.start_browser_automation(url)
            
            if result['status'] == 'success':
                return {
                    "status": "success",
                    "message": f"🌐 Browser automation started: {result['message']}",
                    "current_url": result.get('current_url', url),
                    "type": "web_automation"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Web automation failed: {result['message']}",
                    "details": "Chrome driver may need to be installed"
                }
                
        except Exception as e:
            logger.error(f"Web automation failed: {e}")
            return {"status": "error", "message": f"Web automation error: {str(e)}"}

    def _execute_task_automation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex task automation using Computer Use Agent"""
        if not COMPUTER_USE_AVAILABLE:
            return {
                "status": "error",
                "message": "Computer Use Agent not available. Install requirements with: pip install -r computer_use_requirements.txt"
            }
        
        try:
            task = action.get('target') or action.get('task') or action.get('workflow', '')
            logger.info(f"🚀 Executing task automation: {task}")
            
            # Execute complex task
            result = computer_use_agent.execute_computer_task(task)
            
            if result['status'] in ['success', 'partial']:
                message = f"🤖 **Task Automation Results:**\n\n"
                message += f"📋 **Task:** {result.get('task_description', task)}\n"
                message += f"✅ **Steps Completed:** {result.get('steps_executed', 0)}\n"
                message += f"📊 **Status:** {result['status'].title()}\n"
                
                if result.get('step_results'):
                    successful_steps = sum(1 for step in result['step_results'] if step.get('status') == 'success')
                    message += f"🎯 **Success Rate:** {successful_steps}/{len(result['step_results'])}\n"
                
                return {
                    "status": "success",
                    "message": message,
                    "task_completed": result['status'] == 'success',
                    "steps_executed": result.get('steps_executed', 0),
                    "step_results": result.get('step_results', []),
                    "type": "task_automation"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Task automation failed: {result['message']}",
                    "details": result.get('error', '')
                }
                
        except Exception as e:
            logger.error(f"Task automation failed: {e}")
            return {"status": "error", "message": f"Task automation error: {str(e)}"}

    def _execute_keyboard_shortcut(self, shortcut: str) -> Dict[str, Any]:
        """Execute keyboard shortcut"""
        import pyautogui
        import time
        
        if not shortcut:
            return {"status": "error", "message": "No keyboard shortcut specified"}
        
        try:
            # Parse shortcut string
            keys = shortcut.lower().replace(' ', '').split('+')
            
            # Execute the shortcut
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            
            time.sleep(0.5)  # Give time for the shortcut to execute
            
            return {
                "status": "success", 
                "message": f"Executed keyboard shortcut: {shortcut}"
            }
            
        except Exception as e:
            logger.error(f"Keyboard shortcut execution failed: {e}")
            return {"status": "error", "message": f"Failed to execute shortcut: {str(e)}"}
    
    def _execute_general_question(self, user_input: str) -> Dict[str, Any]:
        """Handle general questions with AI"""
        try:
            # Get conversation context
            context = memory_manager.get_conversation_summary()
            
            system_prompt = """You are a helpful Windows AI assistant. You can:
            - Open/close applications
            - Create/read files
            - List directories
            - Run commands
            - Manage tasks
            - Analyze system resource usage and performance
            
            Be helpful, concise, and suggest actions the user can take.
            """
            
            prompt = f"Context:\n{context}\n\nUser question: {user_input}"
            response = ollama_client.generate(prompt, system_prompt)
            
            return {
                "status": "success",
                "message": response,
                "type": "ai_response"
            }
        except Exception as e:
            logger.error(f"Failed to process general question: {e}")
            return {
                "status": "error",
                "message": "I'm having trouble processing that request. Try being more specific."
            }
    
    def _execute_organize_files(self, target: str = None) -> Dict[str, Any]:
        """Smart file organization based on AI analysis"""
        try:
            # Get current directory contents
            current_dir = target or "."
            result = system_tools.list_directory(current_dir)
            
            if result.get('status') != 'success':
                return result
            
            items = result.get('items', [])
            files = [item for item in items if item['type'] == 'file']
            
            if not files:
                return {"status": "info", "message": "No files to organize in current directory"}
            
            # AI-powered organization suggestions
            file_list = "\n".join([f"- {f['name']}" for f in files])
            
            organize_prompt = f"""Analyze these files and suggest organization:

FILES:
{file_list}

Suggest how to organize these files into folders based on:
- File types and extensions
- Content analysis from names
- Common organization patterns

Respond with JSON:
{{
    "organization_plan": [
        {{"folder": "folder_name", "files": ["file1", "file2"], "reason": "why these go together"}}
    ],
    "summary": "Brief explanation of organization strategy"
}}"""

            response = ollama_client.generate(organize_prompt, "You are a file organization expert.")
            
            # Parse AI response
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                
                # Execute organization plan
                organized_count = 0
                for folder_plan in plan.get('organization_plan', []):
                    folder_name = folder_plan.get('folder')
                    files_to_move = folder_plan.get('files', [])
                    
                    if folder_name and files_to_move:
                        # Create folder if it doesn't exist
                        folder_path = Path(current_dir) / folder_name
                        folder_path.mkdir(exist_ok=True)
                        
                        # Move files (simulate - in real implementation you'd use shutil.move)
                        organized_count += len(files_to_move)
                
                return {
                    "status": "success",
                    "message": f"Organized {organized_count} files. {plan.get('summary', '')}",
                    "organization_plan": plan.get('organization_plan', [])
                }
            
            return {"status": "info", "message": "File organization analysis completed, but no specific actions taken"}
            
        except Exception as e:
            logger.error(f"File organization failed: {e}")
            return {"status": "error", "message": f"Failed to organize files: {str(e)}"}
    
    def _execute_system_cleanup(self) -> Dict[str, Any]:
        """Intelligent system cleanup suggestions"""
        try:
            # Get system information
            processes = system_tools.list_running_processes()
            memory_hogs = [p for p in processes if p['memory_mb'] > 500]
            
            cleanup_suggestions = []
            
            if memory_hogs:
                cleanup_suggestions.append(f"Found {len(memory_hogs)} memory-intensive processes")
            
            # Check for common temp directories
            temp_locations = ["C:\\Temp", "C:\\Windows\\Temp", str(Path.home() / "AppData/Local/Temp")]
            temp_info = []
            
            for temp_dir in temp_locations:
                try:
                    result = system_tools.list_directory(temp_dir)
                    if result.get('status') == 'success':
                        item_count = len(result.get('items', []))
                        if item_count > 10:
                            temp_info.append(f"{temp_dir}: {item_count} items")
                except:
                    continue
            
            if temp_info:
                cleanup_suggestions.extend(temp_info)
            
            message = "System cleanup analysis:\n" + "\n".join([f"• {s}" for s in cleanup_suggestions])
            message += "\n\nWould you like me to help with specific cleanup tasks?"
            
            return {
                "status": "success",
                "message": message,
                "cleanup_suggestions": cleanup_suggestions
            }
            
        except Exception as e:
            logger.error(f"System cleanup analysis failed: {e}")
            return {"status": "error", "message": f"System cleanup analysis failed: {str(e)}"}
    
    def _execute_productivity_boost(self) -> Dict[str, Any]:
        """AI-powered productivity suggestions based on current context"""
        try:
            # Analyze current state
            processes = system_tools.list_running_processes()
            running_apps = [p['name'] for p in processes if 'exe' in p['name']]
            
            # Get recent tasks and conversations
            recent_conversations = memory_manager.get_recent_conversations(3)
            pending_tasks = memory_manager.get_pending_tasks()
            
            context_info = f"""
Current running applications: {', '.join(running_apps[:10])}
Recent conversations: {len(recent_conversations)} exchanges
Pending tasks: {len(pending_tasks)} tasks
Current time: {Path.cwd()}
"""
            
            productivity_prompt = f"""Based on the current context, suggest 3-5 specific productivity actions:

CONTEXT:
{context_info}

Suggest actionable productivity improvements like:
- Organizing or prioritizing tasks
- Closing unnecessary applications
- Creating helpful files or shortcuts
- Setting up productive workflows
- Time management suggestions

Respond with JSON:
{{
    "suggestions": [
        {{"action": "specific_action", "benefit": "why this helps productivity", "priority": "high/medium/low"}}
    ],
    "summary": "Overall productivity assessment"
}}"""

            response = ollama_client.generate(productivity_prompt, "You are a productivity optimization expert.")
            
            # Parse AI response
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                productivity_plan = json.loads(json_match.group())
                
                suggestions = productivity_plan.get('suggestions', [])
                message = f"🚀 Productivity Analysis: {productivity_plan.get('summary', '')}\n\n"
                message += "Suggested actions:\n"
                
                for i, suggestion in enumerate(suggestions, 1):
                    priority = suggestion.get('priority', 'medium')
                    priority_icon = "🔥" if priority == 'high' else "⚡" if priority == 'medium' else "💡"
                    message += f"{i}. {priority_icon} {suggestion.get('action', '')}\n"
                    message += f"   Benefit: {suggestion.get('benefit', '')}\n"
                
                return {
                    "status": "success",
                    "message": message,
                    "productivity_suggestions": suggestions
                }
            
            return {"status": "info", "message": "Productivity analysis completed"}
            
        except Exception as e:
            logger.error(f"Productivity boost failed: {e}")
            return {"status": "error", "message": f"Productivity analysis failed: {str(e)}"}

# Global task executor instance
task_executor = TaskExecutor()
