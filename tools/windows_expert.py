"""
Universal Windows Expert Agent - Powered by Gemma3n AI
Handles ANY Windows scenario through intelligent AI-guided command execution
"""
import subprocess
import os
import logging
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class WindowsCommandExpert:
    """Universal Windows Expert Agent - AI-Guided Dynamic Command Execution
    
    Capabilities:
    - Handles ANY Windows scenario (technical & non-technical users)
    - AI-guided command suggestions one by one
    - Intelligent error correction and auto-recovery
    - Adaptive workflow generation
    - Complete task completion guarantee
    """
    
    def __init__(self):
        self.command_database = self._build_command_database()
        self.scenario_workflows = self._build_scenario_workflows()
        self.ai_suggestions = self._build_ai_suggestions()
        self.execution_stats = {
            'commands_executed': 0,
            'scenarios_handled': 0,
            'workflows_completed': 0,
            'success_rate': 0.0
        }
        
        # Universal AI-guided execution context
        self.current_goal = None
        self.execution_context = {
            'goal': '',
            'original_request': '',
            'progress': [],
            'failed_commands': [],
            'successful_commands': [],
            'current_step': 0,
            'max_retries': 5,  # Increased for persistence
            'user_level': 'auto_detect',  # auto_detect, beginner, intermediate, advanced
            'adaptive_mode': True,  # Enable intelligent adaptation
            'error_learning': [],  # Learn from errors to improve
            'alternative_strategies': [],  # Multiple approach strategies
            'completion_confidence': 0.0  # Track completion confidence
        }
        
        # Universal command knowledge base for any scenario
        self.universal_commands = self._build_universal_command_database()
        
        # AI-guided approach mappings
        self.approach_strategies = {
            'direct': 'Execute specific commands directly',
            'exploratory': 'Discover information first, then act',
            'step_by_step': 'Break into small, safe steps',
            'alternative_path': 'Use different tools to achieve same goal',
            'gui_assisted': 'Combine CLI with GUI tools',
            'safe_mode': 'Use safest possible approach'
        }
    
    def analyze_request(self, user_request: str) -> Dict[str, Any]:
        """Universal AI-guided analysis for ANY Windows scenario"""
        logger.info(f"🤖 Universal Windows Expert analyzing: {user_request}")
        
        # Initialize execution context for this request
        self.execution_context['goal'] = user_request
        self.execution_context['original_request'] = user_request
        self.execution_context['current_step'] = 0
        self.execution_context['progress'] = []
        self.execution_context['failed_commands'] = []
        self.execution_context['successful_commands'] = []
        self.execution_context['completion_confidence'] = 0.0
        
        # Detect user technical level from request
        user_level = self._detect_user_level(user_request)
        self.execution_context['user_level'] = user_level
        
        # Generate AI-guided analysis for ANY scenario
        ai_analysis = self._get_universal_ai_analysis(user_request)
        
        # Create adaptive execution plan with multiple strategies
        execution_plan = self._create_adaptive_execution_plan(user_request, ai_analysis, user_level)
        
        # Generate first set of AI-suggested commands
        next_commands = self._generate_first_commands(user_request, ai_analysis)
        
        return {
            'scenario': ai_analysis,
            'workflow': execution_plan['workflow'],
            'next_commands': next_commands,  # AI suggests commands one by one
            'strategies': execution_plan['alternative_strategies'],
            'execution_plan': execution_plan,
            'risk_assessment': self._assess_dynamic_risk(user_request),
            'expected_outcome': ai_analysis.get('expected_outcome', 'Complete the requested task'),
            'user_level': user_level,
            'is_universal': True,  # This can handle ANY scenario
            'ai_guided': True,
            'adaptive': True,
            'error_recovery': True,
            'completion_guarantee': True
        }
    
    def _detect_user_level(self, user_request: str) -> str:
        """Detect user technical level from their request"""
        request_lower = user_request.lower()
        
        # Advanced user indicators
        advanced_indicators = [
            'powershell', 'cmd', 'registry', 'regedit', 'gpo', 'group policy',
            'dism', 'sfc', 'chkdsk', 'netstat', 'ipconfig', 'nslookup',
            'service', 'process', 'task scheduler', 'event viewer', 'wmic'
        ]
        
        # Beginner user indicators
        beginner_indicators = [
            'how to', 'help me', 'i don\'t know', 'simple way', 'easy way',
            'step by step', 'guide me', 'show me', 'what should i do'
        ]
        
        if any(indicator in request_lower for indicator in advanced_indicators):
            return 'advanced'
        elif any(indicator in request_lower for indicator in beginner_indicators):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _get_universal_ai_analysis(self, user_request: str) -> Dict[str, Any]:
        """Get comprehensive AI analysis for ANY Windows scenario"""
        
        # Parse the request to understand the goal
        request_lower = user_request.lower()
        
        # Categorize the type of request
        request_category = self._categorize_request(user_request)
        
        # Determine the best approach strategy
        approach_strategy = self._determine_best_approach(user_request, request_category)
        
        # Assess technical complexity
        complexity = self._assess_request_complexity(user_request)
        
        analysis = {
            'goal': user_request,
            'category': request_category,
            'approach_strategy': approach_strategy,
            'complexity': complexity,
            'requires_admin': self._requires_admin_analysis(user_request),
            'estimated_steps': 'adaptive',  # Will adapt based on execution
            'primary_tools': self._identify_primary_tools(user_request),
            'expected_outcome': f"Successfully complete: {user_request}",
            'safety_level': self._assess_safety_level(user_request),
            'user_benefits': self._identify_user_benefits(user_request),
            'success_indicators': self._define_success_indicators(user_request),
            'fallback_strategies': self._generate_fallback_strategies(user_request),
            'adaptive_features': {
                'can_pivot': True,
                'learn_from_errors': True,
                'multiple_approaches': True,
                'real_time_guidance': True,
                'auto_correction': True
            }
        }
        
        return analysis
    
    def _categorize_request(self, user_request: str) -> str:
        """Categorize any Windows request into actionable categories"""
        request_lower = user_request.lower()
        
        # Comprehensive categorization patterns
        categories = {
            'file_operations': ['file', 'folder', 'directory', 'copy', 'move', 'delete', 'create', 'save', 'open'],
            'system_info': ['info', 'information', 'specs', 'details', 'status', 'version', 'hardware'],
            'performance': ['slow', 'fast', 'optimize', 'speed', 'performance', 'boost', 'improve'],
            'network': ['network', 'internet', 'wifi', 'connection', 'ip', 'dns', 'ping'],
            'troubleshooting': ['problem', 'issue', 'error', 'fix', 'repair', 'not working', 'broken'],
            'applications': ['app', 'application', 'program', 'software', 'install', 'uninstall', 'run'],
            'security': ['security', 'antivirus', 'firewall', 'protection', 'malware', 'virus'],
            'maintenance': ['clean', 'cleanup', 'maintenance', 'scan', 'check', 'update'],
            'customization': ['customize', 'setting', 'configure', 'change', 'modify', 'personalize'],
            'automation': ['automate', 'schedule', 'task', 'script', 'batch', 'automatic']
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in request_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return the highest scoring category, or 'general' if none found
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'general_task'
    
    def _determine_best_approach(self, user_request: str, category: str) -> str:
        """Determine the best approach strategy for the request"""
        request_lower = user_request.lower()
        
        # Approach decision logic
        if any(word in request_lower for word in ['urgent', 'quickly', 'fast', 'asap']):
            return 'direct'
        elif any(word in request_lower for word in ['don\'t know', 'not sure', 'help me', 'how to']):
            return 'exploratory'
        elif any(word in request_lower for word in ['safe', 'careful', 'backup', 'important']):
            return 'safe_mode'
        elif category in ['troubleshooting', 'performance']:
            return 'step_by_step'
        elif category in ['file_operations', 'applications']:
            return 'gui_assisted'
        else:
            return 'adaptive'  # Let the system choose the best approach
    
    def _assess_request_complexity(self, user_request: str) -> str:
        """Assess the complexity of any request"""
        request_lower = user_request.lower()
        
        # Complexity indicators
        high_complexity_indicators = [
            'registry', 'boot', 'system file', 'driver', 'partition', 'recovery',
            'network configuration', 'group policy', 'active directory'
        ]
        
        medium_complexity_indicators = [
            'install', 'configure', 'settings', 'multiple', 'batch', 'script',
            'permissions', 'user account', 'firewall'
        ]
        
        simple_indicators = [
            'open', 'close', 'view', 'check', 'list', 'show', 'display', 'copy'
        ]
        
        if any(indicator in request_lower for indicator in high_complexity_indicators):
            return 'complex'
        elif any(indicator in request_lower for indicator in medium_complexity_indicators):
            return 'medium'
        elif any(indicator in request_lower for indicator in simple_indicators):
            return 'simple'
        else:
            return 'auto_determine'  # Will be determined during execution
    
    def _create_adaptive_execution_plan(self, user_request: str, ai_analysis: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """Create adaptive execution plan with multiple strategies"""
        
        primary_strategy = ai_analysis['approach_strategy']
        category = ai_analysis['category']
        
        # Create base workflow
        base_workflow = self._create_base_workflow(user_request, category, user_level)
        
        # Generate alternative strategies
        alternative_strategies = self._generate_alternative_strategies(user_request, ai_analysis)
        
        # Create execution phases that adapt based on results
        execution_phases = self._create_adaptive_phases(user_request, ai_analysis, user_level)
        
        execution_plan = {
            'workflow': base_workflow,
            'primary_strategy': primary_strategy,
            'alternative_strategies': alternative_strategies,
            'execution_phases': execution_phases,
            'adaptive_features': {
                'can_change_strategy': True,
                'learns_from_failures': True,
                'suggests_alternatives': True,
                'provides_guidance': True,
                'auto_corrects': True
            },
            'success_criteria': self._define_success_criteria(user_request),
            'fallback_options': self._create_fallback_options(user_request, ai_analysis)
        }
        
        return execution_plan
    
    def _create_base_workflow(self, user_request: str, category: str, user_level: str) -> Dict[str, Any]:
        """Create base workflow template for any scenario"""
        workflows = {
            'system_analysis': {
                'phases': ['information_gathering', 'analysis', 'recommendations'],
                'estimated_time': '5-10 minutes',
                'risk_level': 'low',
                'requires_admin': False
            },
            'performance': {
                'phases': ['system_assessment', 'cleanup_operations', 'optimization'],
                'estimated_time': '15-30 minutes', 
                'risk_level': 'medium',
                'requires_admin': True
            },
            'network': {
                'phases': ['network_assessment', 'connectivity_test', 'configuration_check'],
                'estimated_time': '10-20 minutes',
                'risk_level': 'low',
                'requires_admin': False
            },
            'troubleshooting': {
                'phases': ['problem_identification', 'diagnostic_tests', 'resolution_steps'],
                'estimated_time': '20-45 minutes',
                'risk_level': 'medium',
                'requires_admin': True
            },
            'maintenance': {
                'phases': ['system_backup', 'cleanup_operations', 'updates_check'],
                'estimated_time': '30-60 minutes',
                'risk_level': 'medium',
                'requires_admin': True
            }
        }
        
        # Get base workflow or create generic one
        base = workflows.get(category, {
            'phases': ['information_gathering', 'execution', 'verification'],
            'estimated_time': '10-20 minutes',
            'risk_level': 'low',
            'requires_admin': False
        })
        
        # Add user level adaptations
        base['user_level'] = user_level
        base['request_context'] = user_request
        
        return base
    
    def _generate_alternative_strategies(self, user_request: str, ai_analysis: Dict[str, Any]) -> List[str]:
        """Generate alternative strategies for achieving the goal"""
        return [
            'direct_execution',
            'step_by_step_guided',
            'exploratory_approach',
            'safety_first_method',
            'gui_assisted'
        ]
    
    def _create_adaptive_phases(self, user_request: str, ai_analysis: Dict[str, Any], user_level: str) -> List[Dict[str, Any]]:
        """Create adaptive execution phases"""
        return [
            {
                'name': 'Analysis Phase',
                'description': 'Understand the request and system state',
                'adaptive': True
            },
            {
                'name': 'Execution Phase', 
                'description': 'Execute commands with AI guidance',
                'adaptive': True
            },
            {
                'name': 'Verification Phase',
                'description': 'Verify results and suggest next steps',
                'adaptive': True
            }
        ]
    
    def _define_success_criteria(self, user_request: str) -> List[str]:
        """Define success criteria for the request"""
        return [
            'Command executed without errors',
            'User goal accomplished',
            'System remains stable',
            'Appropriate feedback provided'
        ]
    
    def _create_fallback_options(self, user_request: str, ai_analysis: Dict[str, Any]) -> List[str]:
        """Create fallback options if primary approach fails"""
        return [
            'Try alternative commands',
            'Use different tool approach',
            'Provide manual instructions',
            'Suggest related solutions'
        ]
        
        return execution_plan
    
    def _generate_first_commands(self, user_request: str, ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-suggested first commands for any scenario"""
        
        category = ai_analysis['category']
        approach = ai_analysis['approach_strategy']
        request_lower = user_request.lower()
        
        commands = []
        
        # Universal approach - start with understanding the current state
        if approach == 'exploratory' or 'don\'t know' in request_lower:
            # For users who need guidance, start with safe information gathering
            commands.append({
                'command': 'systeminfo | findstr /i "OS Name"',
                'purpose': 'Check your Windows version',
                'explanation': 'First, let\'s see what version of Windows you\'re running',
                'risk_level': 'safe',
                'next_step_depends_on': 'output'
            })
        
        # Category-specific first commands
        elif category == 'performance':
            commands.append({
                'command': 'tasklist /svc | sort /r /+5',
                'purpose': 'Check which programs are using the most resources',
                'explanation': 'Let\'s see what\'s currently running on your system',
                'risk_level': 'safe',
                'fallback_commands': ['tasklist', 'wmic process get name,workingsetsize']
            })
            
        elif category == 'network':
            commands.append({
                'command': 'ipconfig /all',
                'purpose': 'Check your network configuration',
                'explanation': 'Let\'s examine your current network settings',
                'risk_level': 'safe',
                'fallback_commands': ['ipconfig', 'netsh int show profiles']
            })
            
        elif category == 'file_operations':
            # For file operations, be more careful and ask for specifics
            commands.append({
                'command': 'echo Please specify the file path or directory you want to work with',
                'purpose': 'Get clarification on file operation',
                'explanation': 'I need to know which files or folders you want to work with',
                'risk_level': 'safe',
                'requires_user_input': True
            })
            
        elif category == 'troubleshooting':
            commands.append({
                'command': 'sfc /verifyonly',
                'purpose': 'Check for system file problems without fixing them',
                'explanation': 'Let\'s first check if there are any system file issues',
                'risk_level': 'safe',
                'fallback_commands': ['systeminfo', 'wmic logicaldisk get size,freespace,caption']
            })
            
        else:
            # Generic safe starting point for any unknown scenario
            commands.append({
                'command': 'wmic computersystem get model,totalphysicalmemory',
                'purpose': 'Get basic system information',
                'explanation': 'Let\'s start by understanding your system configuration',
                'risk_level': 'safe',
                'fallback_commands': ['systeminfo | findstr /i "system manufacturer model"']
            })
        
        # Always add a guidance command
        commands.append({
            'command': 'echo Based on the results above, I will suggest the next best step',
            'purpose': 'Provide next step guidance',
            'explanation': 'I\'ll analyze the output and guide you to the next step',
            'risk_level': 'safe',
            'is_guidance': True
        })
        
        return commands[:2]  # Return first 2 commands to start with
    
    def _create_dynamic_execution_plan(self, user_request: str, ai_analysis: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """Create dynamic execution plan that adapts as we execute"""
        
        # Generate first set of commands based on AI analysis
        first_commands = self._generate_first_commands(user_request, user_level)
        
        return {
            'type': 'dynamic_ai_guided',
            'user_level': user_level,
            'workflow': {
                'approach': 'step_by_step_ai_guided',
                'adaptable': True,
                'self_correcting': True,
                'explanation_level': self._get_explanation_level(user_level)
            },
            'next_commands': first_commands,
            'execution_strategy': 'one_by_one_with_ai_correction',
            'retry_strategy': 'ai_guided_alternatives'
        }
    
    def _generate_first_commands(self, user_request: str, user_level: str) -> List[Dict[str, Any]]:
        """Generate the first set of AI-guided commands"""
        request_lower = user_request.lower()
        commands = []
        
        # Analyze what the user wants to accomplish
        if any(word in request_lower for word in ['check', 'show', 'see', 'find', 'list', 'view']):
            # Information gathering request
            if 'process' in request_lower and ('resource' in request_lower or 'cpu' in request_lower or 'memory' in request_lower):
                commands.extend([
                    {
                        'command': 'tasklist /fo csv | findstr /v "Image Name" | sort /r /+5',
                        'purpose': 'List all processes sorted by memory usage',
                        'explanation': 'This command shows all running processes sorted by memory consumption',
                        'fallback_commands': ['tasklist', 'wmic process get name,processid,pagefileusage'],
                        'expected_output': 'List of processes with memory usage'
                    },
                    {
                        'command': 'wmic process get name,processid,percentprocessortime,workingsetsize /format:table',
                        'purpose': 'Get detailed resource usage information',
                        'explanation': 'This provides detailed CPU and memory information for each process',
                        'fallback_commands': ['tasklist /v', 'get-process | sort cpu -desc'],
                        'expected_output': 'Detailed process resource information'
                    }
                ])
            elif 'disk' in request_lower or 'storage' in request_lower or 'space' in request_lower:
                commands.extend([
                    {
                        'command': 'wmic logicaldisk get size,freespace,caption',
                        'purpose': 'Check disk space on all drives',
                        'explanation': 'This shows available space on all your drives',
                        'fallback_commands': ['dir c:\\ /-c', 'fsutil volume diskfree c:'],
                        'expected_output': 'Disk space information for all drives'
                    }
                ])
            elif 'network' in request_lower or 'wifi' in request_lower or 'connection' in request_lower:
                commands.extend([
                    {
                        'command': 'netsh wlan show profiles',
                        'purpose': 'Show all WiFi networks you\'ve connected to',
                        'explanation': 'This lists all saved WiFi network profiles',
                        'fallback_commands': ['ipconfig /all', 'netsh interface show interface'],
                        'expected_output': 'List of WiFi network profiles'
                    },
                    {
                        'command': 'netsh wlan show profiles name="*" key=clear',
                        'purpose': 'Show WiFi network details including passwords',
                        'explanation': 'This shows detailed information about your WiFi networks',
                        'fallback_commands': ['netsh wlan show interfaces', 'ipconfig'],
                        'expected_output': 'Detailed WiFi network information'
                    }
                ])
        
        elif any(word in request_lower for word in ['open', 'start', 'launch', 'run']):
            # Application launching request
            app_name = self._extract_app_name(user_request)
            if app_name:
                commands.append({
                    'command': f'start {app_name}',
                    'purpose': f'Open {app_name}',
                    'explanation': f'This will launch the {app_name} application',
                    'fallback_commands': [f'{app_name}', f'explorer shell:appsFolder\\{app_name}'],
                    'expected_output': f'{app_name} application window opens'
                })
        
        elif any(word in request_lower for word in ['clean', 'optimize', 'speed', 'performance']):
            # System optimization request
            commands.extend([
                {
                    'command': 'cleanmgr /sagerun:1',
                    'purpose': 'Clean temporary files and system cache',
                    'explanation': 'This removes temporary files to free up space and improve performance',
                    'fallback_commands': ['del /q /f /s %TEMP%\\*', 'sfc /scannow'],
                    'expected_output': 'Disk cleanup completion'
                }
            ])
        
        # If no specific commands generated, create generic diagnostic commands
        if not commands:
            commands.extend([
                {
                    'command': 'systeminfo | findstr /i "OS Name OS Version Total Physical Memory"',
                    'purpose': 'Get basic system information to understand your setup',
                    'explanation': 'This helps me understand your system configuration',
                    'fallback_commands': ['systeminfo', 'wmic computersystem get TotalPhysicalMemory'],
                    'expected_output': 'Basic system information'
                },
                {
                    'command': f'echo Analyzing request: {user_request}',
                    'purpose': 'Confirm we understand your request',
                    'explanation': 'Let me confirm what you\'re trying to accomplish',
                    'fallback_commands': ['echo Request understood'],
                    'expected_output': 'Confirmation message'
                }
            ])
        
        return commands
    
    def execute_dynamic_command(self, command_info: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Execute a command with AI-guided error correction and adaptation"""
        command = command_info.get('command', '')
        purpose = command_info.get('purpose', 'Execute command')
        explanation = command_info.get('explanation', '')
        fallback_commands = command_info.get('fallback_commands', [])
        
        logger.info(f"🤖 AI-guided execution: {command}")
        
        # Update execution context
        self.execution_context['current_step'] += 1
        
        # Try the main command first
        result = self._execute_single_command_with_ai_correction(command, context, explanation)
        
        # If main command failed, intelligently try alternatives
        if result['status'] != 'success' and fallback_commands:
            logger.info(f"Main command failed. Trying {len(fallback_commands)} intelligent alternatives...")
            
            for i, fallback_cmd in enumerate(fallback_commands):
                logger.info(f"Trying alternative {i+1}: {fallback_cmd}")
                fallback_result = self._execute_single_command_with_ai_correction(
                    fallback_cmd, context, f"Alternative approach: {explanation}"
                )
                
                if fallback_result['status'] == 'success':
                    result = fallback_result
                    result['used_fallback'] = True
                    result['fallback_command'] = fallback_cmd
                    result['adaptation_success'] = True
                    break
        
        # If still failed, try AI-guided alternative approach
        if result['status'] != 'success':
            result = self._try_ai_guided_alternative(command_info, result)
        
        # Update execution tracking
        if result['status'] == 'success':
            self.execution_context['successful_commands'].append(command_info)
            self.execution_context['completion_confidence'] += 0.2
        else:
            self.execution_context['failed_commands'].append(command_info)
            # Learn from the error for future improvements
            self.execution_context['error_learning'].append({
                'command': command,
                'error': result.get('error', ''),
                'context': context
            })
        
        # Generate AI-guided next steps
        result['next_suggestions'] = self._generate_next_ai_commands(result, command_info)
        result['execution_guidance'] = self._get_intelligent_guidance(result, command_info)
        result['progress_update'] = self._get_progress_update()
        
        return result
    
    def _execute_single_command_with_ai_correction(self, command: str, context: str, explanation: str) -> Dict[str, Any]:
        """Execute a single command with intelligent error handling and learning"""
        try:
            logger.info(f"Executing: {command}")
            
            # Handle special command types
            if command.startswith('echo '):
                # Guidance or information commands
                message = command[5:]  # Remove 'echo '
                return {
                    'command': command,
                    'status': 'success',
                    'message': message,
                    'output': message,
                    'explanation': explanation,
                    'type': 'guidance'
                }
            
            elif any(gui_cmd in command.lower() for gui_cmd in ['msconfig', 'regedit', 'gpedit', 'services.msc']):
                # GUI applications - launch without waiting for output
                result = subprocess.run(command, shell=True, capture_output=False, timeout=5)
                return {
                    'command': command,
                    'status': 'success',
                    'message': f'Launched: {command}',
                    'output': f'GUI application {command} started',
                    'explanation': explanation,
                    'type': 'gui_launch'
                }
            
            else:
                # Regular CLI commands with intelligent timeout handling
                timeout = self._calculate_intelligent_timeout(command)
                
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.execution_stats['commands_executed'] += 1
                
                if result.returncode == 0:
                    return {
                        'command': command,
                        'status': 'success',
                        'message': 'Command executed successfully',
                        'output': result.stdout.strip(),
                        'explanation': explanation,
                        'execution_time': timeout
                    }
                else:
                    # Intelligent error analysis and correction suggestions
                    error_analysis = self._analyze_command_error_intelligently(
                        command, result.stderr, result.returncode, result.stdout
                    )
                    
                    return {
                        'command': command,
                        'status': 'error',
                        'message': f'Command failed (exit code {result.returncode})',
                        'output': result.stdout.strip(),
                        'error': result.stderr.strip(),
                        'error_analysis': error_analysis,
                        'explanation': explanation,
                        'intelligent_suggestions': error_analysis.get('ai_suggestions', [])
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'status': 'timeout',
                'message': f'Command took longer than expected ({timeout}s)',
                'output': '',
                'suggestion': 'This operation may require more time or a different approach',
                'explanation': explanation,
                'next_approach': 'try_simpler_version'
            }
        except Exception as e:
            return {
                'command': command,
                'status': 'error',
                'message': f'Execution failed: {str(e)}',
                'output': '',
                'suggestion': 'This command may require administrator privileges or may not be available',
                'explanation': explanation,
                'recovery_options': self._get_recovery_options(command, str(e))
            }
    
    def _try_ai_guided_alternative(self, command_info: Dict[str, Any], failed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Try an AI-guided alternative approach when commands fail"""
        
        original_command = command_info.get('command', '')
        purpose = command_info.get('purpose', '')
        
        # Generate intelligent alternatives based on the purpose
        alternative_approaches = self._generate_intelligent_alternatives(original_command, purpose, failed_result)
        
        for approach in alternative_approaches:
            logger.info(f"Trying AI-guided alternative: {approach['command']}")
            
            result = self._execute_single_command_with_ai_correction(
                approach['command'], 
                "AI-guided alternative", 
                approach['explanation']
            )
            
            if result['status'] == 'success':
                result['ai_alternative_used'] = True
                result['original_command'] = original_command
                result['alternative_explanation'] = approach['explanation']
                return result
        
        # If all alternatives failed, return enhanced failure info
        failed_result['all_alternatives_tried'] = True
        failed_result['alternative_count'] = len(alternative_approaches)
        failed_result['ai_recommendation'] = self._get_ai_failure_recommendation(command_info, failed_result)
        
        return failed_result
    
    def _execute_single_command_with_correction(self, command: str, context: str, explanation: str) -> Dict[str, Any]:
        """Execute a single command with intelligent error handling"""
        try:
            logger.info(f"Executing: {command}")
            
            # Handle different command types
            if command.startswith('echo '):
                # Echo commands for information
                message = command[5:]  # Remove 'echo '
                return {
                    'command': command,
                    'status': 'success',
                    'message': message,
                    'output': message,
                    'explanation': explanation
                }
            
            elif any(cmd in command.lower() for cmd in ['cleanmgr', 'msconfig', 'regedit']):
                # GUI commands that don't return output
                result = subprocess.run(command, shell=True, capture_output=False, timeout=5)
                return {
                    'command': command,
                    'status': 'success',
                    'message': f'Launched: {command}',
                    'output': f'GUI application {command} started',
                    'explanation': explanation
                }
            
            else:
                # Regular CLI commands
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.execution_stats['commands_executed'] += 1
                
                if result.returncode == 0:
                    return {
                        'command': command,
                        'status': 'success',
                        'message': 'Command executed successfully',
                        'output': result.stdout.strip(),
                        'explanation': explanation
                    }
                else:
                    # Command failed - try to provide intelligent error correction
                    error_correction = self._analyze_command_error(command, result.stderr, result.returncode)
                    
                    return {
                        'command': command,
                        'status': 'error',
                        'message': f'Command failed (exit code {result.returncode})',
                        'output': result.stdout.strip(),
                        'error': result.stderr.strip(),
                        'error_correction': error_correction,
                        'explanation': explanation
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'status': 'timeout',
                'message': 'Command timed out (taking too long)',
                'output': '',
                'suggestion': 'Try a simpler version of this command',
                'explanation': explanation
            }
        except Exception as e:
            return {
                'command': command,
                'status': 'error',
                'message': f'Execution failed: {str(e)}',
                'output': '',
                'suggestion': 'This command may require administrator privileges or may not be available',
                'explanation': explanation
            }
    
    def _calculate_intelligent_timeout(self, command: str) -> int:
        """Calculate intelligent timeout based on command type"""
        cmd_lower = command.lower()
        
        # Long-running commands
        if any(long_cmd in cmd_lower for long_cmd in ['sfc /scannow', 'chkdsk', 'cleanmgr', 'dism']):
            return 300  # 5 minutes for system maintenance
        elif any(medium_cmd in cmd_lower for medium_cmd in ['systeminfo', 'wmic', 'netstat']):
            return 60   # 1 minute for information gathering
        elif any(quick_cmd in cmd_lower for quick_cmd in ['tasklist', 'ipconfig', 'ping']):
            return 30   # 30 seconds for quick commands
        else:
            return 45   # Default timeout
    
    def _analyze_command_error_intelligently(self, command: str, error_output: str, exit_code: int, stdout: str) -> Dict[str, Any]:
        """Provide intelligent analysis of command errors with AI-guided solutions"""
        
        error_lower = error_output.lower()
        command_lower = command.lower()
        
        analysis = {
            'error_type': 'unknown',
            'user_friendly_explanation': 'The command encountered an issue',
            'technical_details': error_output,
            'ai_suggestions': [],
            'recovery_steps': [],
            'prevention_tips': []
        }
        
        # Intelligent error categorization
        if 'access denied' in error_lower or 'permission denied' in error_lower:
            analysis.update({
                'error_type': 'permission_error',
                'user_friendly_explanation': 'You don\'t have permission to run this command',
                'ai_suggestions': [
                    'Try running as Administrator (Right-click Command Prompt → Run as Administrator)',
                    'Check if you have the necessary user permissions for this action'
                ],
                'recovery_steps': [
                    'Open Command Prompt as Administrator',
                    'Run the command again',
                    'If still failing, check user account permissions'
                ]
            })
        
        elif 'not recognized' in error_lower or 'not found' in error_lower:
            analysis.update({
                'error_type': 'command_not_found',
                'user_friendly_explanation': 'This command is not available on your system',
                'ai_suggestions': self._get_command_alternatives(command),
                'recovery_steps': [
                    'Try one of the suggested alternative commands',
                    'Check if the feature is installed on your Windows version',
                    'Consider using a GUI tool instead'
                ]
            })
        
        elif 'network' in error_lower or 'connection' in error_lower:
            analysis.update({
                'error_type': 'network_error',
                'user_friendly_explanation': 'There\'s a network connectivity issue',
                'ai_suggestions': [
                    'Check your internet connection',
                    'Try again in a few moments',
                    'Use offline alternatives if available'
                ],
                'recovery_steps': [
                    'Test internet connection with: ping google.com',
                    'Check network adapter status',
                    'Restart network connection if needed'
                ]
            })
        
        elif exit_code == 1 and 'invalid' in error_lower:
            analysis.update({
                'error_type': 'invalid_parameter',
                'user_friendly_explanation': 'The command has incorrect parameters',
                'ai_suggestions': [
                    'Check the command syntax',
                    'Try a simpler version of the command',
                    'Use command help: {command} /?'
                ],
                'recovery_steps': [
                    f'Try: {command} /?',
                    'Review the command parameters',
                    'Use a corrected version of the command'
                ]
            })
        
        return analysis
    
    def _generate_intelligent_alternatives(self, failed_command: str, purpose: str, failed_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-guided alternative approaches when commands fail"""
        
        alternatives = []
        cmd_lower = failed_command.lower()
        
        # Command-specific intelligent alternatives
        if 'tasklist' in cmd_lower:
            alternatives.extend([
                {
                    'command': 'wmic process get name,processid,workingsetsize',
                    'explanation': 'Using WMIC to get process information with memory usage'
                },
                {
                    'command': 'powershell "Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10"',
                    'explanation': 'Using PowerShell to show top 10 processes by memory usage'
                }
            ])
        
        elif 'systeminfo' in cmd_lower:
            alternatives.extend([
                {
                    'command': 'wmic computersystem get model,totalphysicalmemory',
                    'explanation': 'Getting basic system information using WMIC'
                },
                {
                    'command': 'msinfo32',
                    'explanation': 'Opening System Information GUI tool'
                }
            ])
        
        elif 'netsh' in cmd_lower or 'wifi' in purpose.lower():
            alternatives.extend([
                {
                    'command': 'ipconfig /all',
                    'explanation': 'Getting network configuration information'
                },
                {
                    'command': 'powershell "Get-NetAdapter | Where-Object Status -eq \'Up\'"',
                    'explanation': 'Using PowerShell to check active network adapters'
                }
            ])
        
        elif 'ping' in cmd_lower:
            alternatives.extend([
                {
                    'command': 'nslookup google.com',
                    'explanation': 'Testing DNS resolution instead of ping'
                },
                {
                    'command': 'telnet google.com 80',
                    'explanation': 'Testing connectivity on specific port'
                }
            ])
        
        # Generic alternatives based on purpose
        if 'information' in purpose.lower() or 'check' in purpose.lower():
            alternatives.append({
                'command': 'echo Let me try a different approach to get this information',
                'explanation': 'Switching to an alternative information gathering method'
            })
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _get_command_alternatives(self, failed_command: str) -> List[str]:
        """Get alternative commands when one is not found"""
        cmd_lower = failed_command.lower()
        
        alternatives = []
        
        if 'netsh' in cmd_lower:
            alternatives.extend(['ipconfig /all', 'powershell Get-NetAdapter'])
        elif 'wmic' in cmd_lower:
            alternatives.extend(['systeminfo', 'tasklist'])
        elif 'powershell' in cmd_lower:
            alternatives.extend(['cmd equivalent commands', 'wmic alternatives'])
        elif any(admin_cmd in cmd_lower for admin_cmd in ['sfc', 'dism', 'chkdsk']):
            alternatives.extend(['Run Command Prompt as Administrator first'])
        
        return alternatives
    
    def _generate_next_ai_commands(self, execution_result: Dict[str, Any], completed_command: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent next commands based on execution results and overall goal"""
        
        next_commands = []
        goal = self.execution_context['goal'].lower()
        output = execution_result.get('output', '').lower()
        command = completed_command.get('command', '').lower()
        
        # Analyze output to intelligently determine next steps
        if execution_result['status'] == 'success':
            
            # If we just got system info, suggest relevant next actions
            if 'systeminfo' in command or 'wmic' in command:
                if 'performance' in goal or 'slow' in goal:
                    next_commands.append({
                        'command': 'tasklist /svc | findstr /i "svchost"',
                        'purpose': 'Check for resource-heavy services',
                        'explanation': 'Now let\'s see which services might be using resources',
                        'confidence': 0.9
                    })
                elif 'memory' in goal or 'ram' in goal:
                    next_commands.append({
                        'command': 'wmic OS get TotalVisibleMemorySize,FreePhysicalMemory',
                        'purpose': 'Check memory usage details',
                        'explanation': 'Let\'s get detailed memory information',
                        'confidence': 0.9
                    })
            
            # If we listed processes, suggest analysis
            elif 'tasklist' in command:
                if any(keyword in goal for keyword in ['performance', 'slow', 'resource']):
                    next_commands.append({
                        'command': 'wmic process get name,processid,workingsetsize | sort /r /+3',
                        'purpose': 'Find processes using most memory',
                        'explanation': 'Let\'s identify which processes are using the most resources',
                        'confidence': 0.8
                    })
            
            # If we checked network, suggest connectivity tests
            elif 'ipconfig' in command or 'network' in goal:
                next_commands.append({
                    'command': 'ping 8.8.8.8 -n 4',
                    'purpose': 'Test internet connectivity',
                    'explanation': 'Let\'s verify your internet connection is working',
                    'confidence': 0.8
                })
        
        else:
            # Command failed - suggest recovery or alternative approach
            error_type = execution_result.get('error_analysis', {}).get('error_type', 'unknown')
            
            if error_type == 'permission_error':
                next_commands.append({
                    'command': 'echo Please run Command Prompt as Administrator and try again',
                    'purpose': 'Provide guidance for permission issues',
                    'explanation': 'You need administrator privileges for this command',
                    'confidence': 1.0,
                    'is_guidance': True
                })
            
            elif error_type == 'command_not_found':
                # Try a simpler alternative
                alternatives = self._get_command_alternatives(completed_command.get('command', ''))
                if alternatives:
                    next_commands.append({
                        'command': alternatives[0],
                        'purpose': 'Try alternative approach',
                        'explanation': 'Using a different command to achieve the same goal',
                        'confidence': 0.7
                    })
        
        # Always add a progress check
        if len(self.execution_context['successful_commands']) > 0:
            completion_progress = min(100, int(self.execution_context['completion_confidence'] * 100))
            next_commands.append({
                'command': f'echo Progress: {completion_progress}% - Continue with next step?',
                'purpose': 'Progress update',
                'explanation': f'We\'re making progress towards: {self.execution_context["goal"]}',
                'confidence': 1.0,
                'is_guidance': True
            })
        
        return next_commands[:2]  # Return max 2 next suggestions
        """Analyze command errors and provide intelligent corrections"""
        
        error_lower = error_output.lower()
        command_lower = command.lower()
        
        corrections = {
            'suggestion': 'Try the command with administrator privileges',
            'alternative_commands': [],
            'explanation': 'Command failed due to unknown error'
        }
        
        # Common error patterns and corrections
        if 'access denied' in error_lower or 'permission denied' in error_lower:
            corrections.update({
                'suggestion': 'Run as Administrator - Right-click Command Prompt and select "Run as Administrator"',
                'explanation': 'This command requires administrator privileges',
                'alternative_commands': [f'runas /user:Administrator "{command}"']
            })
        
        elif 'not recognized' in error_lower or 'is not a valid' in error_lower:
            corrections.update({
                'suggestion': 'Command not found - it may not be installed or available on your system',
                'explanation': 'This command is not available on your Windows version',
                'alternative_commands': self._find_alternative_commands(command)
            })
        
        elif 'network' in error_lower and 'not available' in error_lower:
            corrections.update({
                'suggestion': 'Check your network connection and try again',
                'explanation': 'Network-related command failed - check connectivity',
                'alternative_commands': ['ping google.com', 'ipconfig']
            })
        
        elif 'file not found' in error_lower or 'path not found' in error_lower:
            corrections.update({
                'suggestion': 'The specified file or path does not exist',
                'explanation': 'Command failed because target file/path was not found',
                'alternative_commands': ['dir', 'echo %cd%']
            })
        
        return corrections
    
    def _build_universal_command_database(self) -> Dict[str, Any]:
        """Build comprehensive universal command database for ANY Windows scenario"""
        return {
            'system_analysis': {
                'basic_info': ['systeminfo', 'msinfo32', 'wmic computersystem get model,totalphysicalmemory'],
                'performance': ['tasklist /svc', 'wmic process get name,workingsetsize', 'perfmon'],
                'hardware': ['wmic cpu get name', 'wmic logicaldisk get size,freespace', 'dxdiag'],
                'memory': ['wmic OS get TotalVisibleMemorySize,FreePhysicalMemory', 'tasklist /m']
            },
            'network_operations': {
                'configuration': ['ipconfig /all', 'netsh int show profiles', 'netsh wlan show profiles'],
                'connectivity': ['ping google.com', 'nslookup google.com', 'tracert google.com'],
                'diagnostics': ['netstat -an', 'netsh wlan show profiles', 'arp -a'],
                'wifi': ['netsh wlan show profiles', 'netsh wlan connect', 'netsh wlan disconnect']
            },
            'file_management': {
                'navigation': ['dir', 'cd', 'tree'],
                'operations': ['copy', 'move', 'del', 'mkdir', 'rmdir'],
                'permissions': ['icacls', 'takeown', 'attrib'],
                'search': ['findstr', 'where', 'forfiles']
            },
            'troubleshooting': {
                'system_repair': ['sfc /scannow', 'dism /online /cleanup-image /restorehealth'],
                'diagnostics': ['chkdsk', 'msconfig', 'eventvwr'],
                'recovery': ['rstrui', 'systempropertiesprotection', 'bcdedit']
            },
            'maintenance': {
                'cleanup': ['cleanmgr', 'temp file cleanup', 'disk cleanup'],
                'updates': ['wuauclt /detectnow', 'powershell Get-WindowsUpdate'],
                'services': ['services.msc', 'sc query', 'net start']
            },
            'security': {
                'antivirus': ['mssecexe.exe', 'defender scans'],
                'firewall': ['netsh firewall show state', 'wf.msc'],
                'permissions': ['whoami /all', 'net user', 'lusrmgr.msc']
            },
            'applications': {
                'management': ['appwiz.cpl', 'winget list', 'wmic product get name'],
                'execution': ['start', 'taskkill', 'runas'],
                'monitoring': ['tasklist', 'resmon', 'procmon']
            }
        }
    
    def _identify_user_benefits(self, user_request: str) -> List[str]:
        """Identify what benefits the user will get from completing this request"""
        request_lower = user_request.lower()
        benefits = []
        
        if any(word in request_lower for word in ['slow', 'performance', 'optimize']):
            benefits.extend([
                'Faster system performance',
                'Improved application response times',
                'Better overall computer experience'
            ])
        elif any(word in request_lower for word in ['network', 'wifi', 'internet']):
            benefits.extend([
                'Better internet connectivity',
                'Resolved network issues',
                'Improved online experience'
            ])
        elif any(word in request_lower for word in ['clean', 'maintenance', 'fix']):
            benefits.extend([
                'More available disk space',
                'Improved system stability',
                'Reduced system errors'
            ])
        elif any(word in request_lower for word in ['information', 'check', 'status']):
            benefits.extend([
                'Better understanding of your system',
                'Informed decision making',
                'Proactive problem prevention'
            ])
        else:
            benefits.append('Successful completion of your requested task')
        
        return benefits
    
    def _define_success_indicators(self, user_request: str) -> List[str]:
        """Define clear success indicators for the request"""
        request_lower = user_request.lower()
        indicators = []
        
        if 'performance' in request_lower or 'slow' in request_lower:
            indicators.extend([
                'System responds faster to commands',
                'Applications launch more quickly',
                'Task Manager shows lower CPU/memory usage'
            ])
        elif 'network' in request_lower or 'wifi' in request_lower:
            indicators.extend([
                'Successful ping to external servers',
                'Stable internet connection',
                'Network adapter shows as connected'
            ])
        elif 'clean' in request_lower or 'maintenance' in request_lower:
            indicators.extend([
                'More free disk space available',
                'No system file errors found',
                'System runs without errors'
            ])
        else:
            indicators.append('Task completed successfully with expected results')
        
        return indicators
    
    def _generate_fallback_strategies(self, user_request: str) -> List[Dict[str, str]]:
        """Generate multiple fallback strategies for completing the task"""
        strategies = [
            {
                'name': 'GUI-Based Approach',
                'description': 'Use Windows graphical tools instead of command line',
                'when_to_use': 'When command line approaches fail'
            },
            {
                'name': 'PowerShell Alternative',
                'description': 'Use PowerShell commands as alternatives to CMD',
                'when_to_use': 'When traditional CMD commands are not available'
            },
            {
                'name': 'Safe Mode Approach',
                'description': 'Break down into smaller, safer steps',
                'when_to_use': 'When the direct approach has risks'
            },
            {
                'name': 'Manual Guidance',
                'description': 'Provide step-by-step manual instructions',
                'when_to_use': 'When automated approaches are not possible'
            }
        ]
        return strategies
    
    def _get_intelligent_guidance(self, execution_result: Dict[str, Any], command_info: Dict[str, Any]) -> Dict[str, str]:
        """Provide intelligent, user-friendly guidance based on execution results"""
        
        guidance = {
            'status_summary': '',
            'what_happened': '',
            'next_steps': '',
            'user_action_needed': False,
            'progress_indicator': ''
        }
        
        if execution_result['status'] == 'success':
            guidance['status_summary'] = '✅ Command completed successfully'
            guidance['what_happened'] = f"Successfully executed: {command_info.get('purpose', 'command')}"
            guidance['next_steps'] = 'Ready for the next step in your task'
            guidance['progress_indicator'] = f'Progress: {self._get_progress_percentage()}%'
            
        elif execution_result['status'] == 'error':
            error_analysis = execution_result.get('error_analysis', {})
            guidance['status_summary'] = '⚠️ Command encountered an issue'
            guidance['what_happened'] = error_analysis.get('user_friendly_explanation', 'Command failed')
            guidance['next_steps'] = error_analysis.get('ai_suggestions', ['Trying alternative approach...'])[0]
            guidance['user_action_needed'] = 'administrator' in guidance['next_steps'].lower()
            
        elif execution_result['status'] == 'timeout':
            guidance['status_summary'] = '⏱️ Command is taking longer than expected'
            guidance['what_happened'] = 'The operation may require more time or a different approach'
            guidance['next_steps'] = 'Let me try a faster alternative method'
            
        return guidance
    
    def _get_progress_update(self) -> Dict[str, Any]:
        """Get current progress update for the overall task"""
        successful = len(self.execution_context['successful_commands'])
        failed = len(self.execution_context['failed_commands'])
        total = successful + failed
        
        progress = {
            'current_step': self.execution_context['current_step'],
            'successful_commands': successful,
            'failed_commands': failed,
            'completion_confidence': self.execution_context['completion_confidence'],
            'overall_status': 'in_progress',
            'progress_description': ''
        }
        
        if self.execution_context['completion_confidence'] >= 0.8:
            progress['overall_status'] = 'near_completion'
            progress['progress_description'] = 'Almost finished with your request'
        elif self.execution_context['completion_confidence'] >= 0.5:
            progress['overall_status'] = 'good_progress'
            progress['progress_description'] = 'Making good progress on your task'
        elif failed > successful:
            progress['overall_status'] = 'needs_adjustment'
            progress['progress_description'] = 'Adjusting approach to better complete your task'
        else:
            progress['progress_description'] = f'Working on: {self.execution_context["goal"]}'
        
        return progress
    
    def _get_progress_percentage(self) -> int:
        """Calculate progress percentage"""
        return min(100, int(self.execution_context['completion_confidence'] * 100))
        """Find alternative commands when one fails"""
        alternatives = []
        
        cmd_lower = failed_command.lower()
        
        # Command alternatives mapping
        if 'tasklist' in cmd_lower:
            alternatives = ['wmic process list', 'get-process', 'taskmgr']
        elif 'systeminfo' in cmd_lower:
            alternatives = ['wmic computersystem list', 'msinfo32']
        elif 'netsh' in cmd_lower:
            alternatives = ['ipconfig /all', 'netstat -an']
        elif 'wmic' in cmd_lower:
            alternatives = ['tasklist', 'systeminfo']
        
        return alternatives
    
    def _generate_next_commands(self, execution_result: Dict[str, Any], completed_command: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-guided next commands based on execution results"""
        
        next_commands = []
        
        # Analyze the output to determine next steps
        output = execution_result.get('output', '').lower()
        command = completed_command.get('command', '').lower()
        
        # If we just got system info, suggest specific analysis
        if 'systeminfo' in command and execution_result['status'] == 'success':
            next_commands.append({
                'command': 'wmic cpu get name,maxclockspeed,numberofcores',
                'purpose': 'Get detailed CPU information',
                'explanation': 'Now let\'s check your processor details'
            })
        
        # If we listed processes, suggest analyzing high resource usage
        elif 'tasklist' in command and execution_result['status'] == 'success':
            next_commands.append({
                'command': 'wmic process get name,processid,workingsetsize | sort /r /+3',
                'purpose': 'Find processes using most memory',
                'explanation': 'Let\'s identify which processes are using the most resources'
            })
        
        # If we checked disk space, suggest cleanup if space is low
        elif 'diskfree' in command or 'logicaldisk' in command:
            next_commands.append({
                'command': 'cleanmgr /sagerun:1',
                'purpose': 'Clean up disk space',
                'explanation': 'Run disk cleanup to free up space'
            })
        
        # Default continuation based on goal
        if not next_commands and self.execution_context['goal']:
            goal_lower = self.execution_context['goal'].lower()
            
            if 'performance' in goal_lower or 'slow' in goal_lower:
                next_commands.append({
                    'command': 'msconfig',
                    'purpose': 'Open system configuration to manage startup programs',
                    'explanation': 'Let\'s check what programs start with Windows'
                })
            
            elif 'network' in goal_lower or 'wifi' in goal_lower:
                next_commands.append({
                    'command': 'ping google.com',
                    'purpose': 'Test internet connectivity',
                    'explanation': 'Let\'s verify your internet connection is working'
                })
        
        return next_commands[:2]  # Return max 2 next suggestions
    
    def _get_execution_guidance(self, execution_result: Dict[str, Any], command_info: Dict[str, Any]) -> Dict[str, Any]:
        """Provide user-friendly guidance based on execution results"""
        
        guidance = {
            'status_message': '',
            'what_happened': '',
            'next_steps': '',
            'user_action_needed': False
        }
        
        if execution_result['status'] == 'success':
            guidance['status_message'] = f"✅ Success: {command_info.get('purpose', 'Command completed')}"
            guidance['what_happened'] = command_info.get('explanation', 'Command executed successfully')
            
            if execution_result.get('next_suggestions'):
                guidance['next_steps'] = "I've prepared the next steps to continue helping you."
            else:
                guidance['next_steps'] = "Task completed! Let me know if you need anything else."
                
        else:
            guidance['status_message'] = f"❌ Issue: {execution_result.get('message', 'Command failed')}"
            guidance['what_happened'] = execution_result.get('error_correction', {}).get('explanation', 'Command encountered an error')
            guidance['next_steps'] = execution_result.get('error_correction', {}).get('suggestion', 'Trying alternative approach...')
            guidance['user_action_needed'] = 'administrator' in guidance['next_steps'].lower()
        
        return guidance
    
    def _analyze_scenario(self, user_request: str) -> Dict[str, Any]:
        """Analyze user request to understand the complete scenario"""
        request_lower = user_request.lower()
        
        # Comprehensive scenario patterns
        scenario_patterns = {
            'performance_optimization': [
                r'(?:slow|sluggish|performance|speed|optimize|boost|faster)',
                r'(?:system.*slow|computer.*slow|pc.*slow)',
                r'(?:clean.*system|cleanup|optimize|speed.*up)',
                r'(?:improve.*performance|boost.*performance)'
            ],
            'troubleshooting': [
                r'(?:problem|issue|error|not.*work|fix|repair|troubleshoot)',
                r'(?:blue.*screen|bsod|crash|freeze|hang)',
                r'(?:corrupt|damage|missing|broken)',
                r'(?:won\'t.*start|can\'t.*open|failing)'
            ],
            'system_maintenance': [
                r'(?:maintenance|check.*system|system.*health|diagnose)',
                r'(?:disk.*check|file.*system|integrity|scan)',
                r'(?:update|patch|security|vulnerability)',
                r'(?:backup|restore|recovery)'
            ],
            'network_management': [
                r'(?:network|internet|connection|wifi|ethernet)',
                r'(?:can\'t.*connect|no.*internet|slow.*internet)',
                r'(?:ip.*config|dns|dhcp|firewall)',
                r'(?:share|access|remote)'
            ],
            'security_management': [
                r'(?:security|virus|malware|antivirus|threat)',
                r'(?:password|encryption|firewall|defender)',
                r'(?:permission|access.*control|user.*account)',
                r'(?:policy|gpo|registry.*security)'
            ],
            'system_information': [
                r'(?:info|information|spec|specification|detail)',
                r'(?:hardware|cpu|memory|ram|disk|gpu)',
                r'(?:version|build|edition|license)',
                r'(?:driver|device|component)'
            ]
        }
        
        # Detect primary and secondary scenarios
        detected_scenarios = []
        for scenario, patterns in scenario_patterns.items():
            for pattern in patterns:
                if re.search(pattern, request_lower):
                    detected_scenarios.append(scenario)
                    break
        
        # Determine primary scenario
        primary_scenario = detected_scenarios[0] if detected_scenarios else 'general_command'
        
        # Extract specific entities and context
        entities = self._extract_entities(user_request)
        context = self._determine_context(user_request, primary_scenario)
        
        return {
            'primary_scenario': primary_scenario,
            'secondary_scenarios': detected_scenarios[1:] if len(detected_scenarios) > 1 else [],
            'entities': entities,
            'context': context,
            'complexity': self._assess_complexity(detected_scenarios, entities),
            'user_intent': self._determine_user_intent(user_request, primary_scenario)
        }
    
    def _extract_entities(self, user_request: str) -> Dict[str, List[str]]:
        """Extract specific entities from user request"""
        entities = {
            'drive_letters': re.findall(r'\b[A-Z]:\\\b', user_request.upper()),
            'file_types': re.findall(r'\.(exe|dll|sys|bat|cmd|ps1|msi|zip|rar)\b', user_request.lower()),
            'processes': re.findall(r'\b(?:chrome|firefox|explorer|notepad|winword|excel|outlook)\.exe\b', user_request.lower()),
            'services': re.findall(r'\b(?:windows update|defender|firewall|dns|dhcp|iis)\b', user_request.lower()),
            'numbers': re.findall(r'\b\d+\b', user_request)
        }
        return {k: v for k, v in entities.items() if v}  # Remove empty lists
    
    def _determine_context(self, user_request: str, primary_scenario: str) -> Dict[str, Any]:
        """Determine context and urgency of the request"""
        urgency_keywords = ['urgent', 'emergency', 'critical', 'immediately', 'asap', 'now']
        scope_keywords = {
            'system_wide': ['system', 'computer', 'pc', 'machine', 'all'],
            'specific_app': ['application', 'program', 'software', 'app'],
            'network_wide': ['network', 'all computers', 'domain', 'workgroup'],
            'user_specific': ['user', 'account', 'profile', 'my']
        }
        
        urgency = 'high' if any(word in user_request.lower() for word in urgency_keywords) else 'normal'
        
        scope = 'general'
        for scope_type, keywords in scope_keywords.items():
            if any(word in user_request.lower() for word in keywords):
                scope = scope_type
                break
        
        return {
            'urgency': urgency,
            'scope': scope,
            'requires_reboot': any(word in user_request.lower() for word in ['reboot', 'restart', 'boot']),
            'backup_recommended': primary_scenario in ['troubleshooting', 'security_management']
        }
    
    def _assess_complexity(self, scenarios: List[str], entities: Dict[str, List[str]]) -> str:
        """Assess complexity of the task"""
        complexity_score = len(scenarios)
        complexity_score += sum(len(v) for v in entities.values())
        
        if complexity_score <= 2:
            return 'simple'
        elif complexity_score <= 5:
            return 'moderate'
        else:
            return 'complex'
    
    def _determine_user_intent(self, user_request: str, primary_scenario: str) -> Dict[str, Any]:
        """Determine user's intent and expected outcome"""
        intent_patterns = {
            'fix_issue': ['fix', 'repair', 'solve', 'resolve', 'troubleshoot'],
            'optimize': ['optimize', 'improve', 'speed up', 'boost', 'enhance'],
            'gather_info': ['check', 'show', 'display', 'list', 'get', 'find'],
            'configure': ['configure', 'setup', 'set', 'enable', 'disable'],
            'maintain': ['clean', 'update', 'maintain', 'scan', 'verify']
        }
        
        detected_intent = 'general'
        for intent, keywords in intent_patterns.items():
            if any(keyword in user_request.lower() for keyword in keywords):
                detected_intent = intent
                break
        
        return {
            'primary_intent': detected_intent,
            'expects_immediate_result': 'now' in user_request.lower() or 'immediately' in user_request.lower(),
            'wants_detailed_info': any(word in user_request.lower() for word in ['detailed', 'comprehensive', 'complete', 'full']),
            'automated_execution': 'automatically' in user_request.lower() or 'auto' in user_request.lower()
        }
    
    def _generate_workflow(self, scenario_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete workflow for the scenario"""
        primary_scenario = scenario_analysis['primary_scenario']
        
        # Get workflow template
        workflow_template = self.scenario_workflows.get(primary_scenario, {})
        
        # Customize workflow based on context and entities
        workflow = self._customize_workflow(workflow_template, scenario_analysis)
        
        return workflow
    
    def _customize_workflow(self, workflow_template: Dict[str, Any], scenario_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Customize workflow based on scenario analysis"""
        if not workflow_template:
            return self._create_generic_workflow(scenario_analysis)
        
        customized_workflow = workflow_template.copy()
        
        # Adjust workflow based on urgency
        if scenario_analysis['context']['urgency'] == 'high':
            customized_workflow['execution_mode'] = 'priority'
            customized_workflow['parallel_execution'] = True
        
        # Adjust based on user intent
        if scenario_analysis['user_intent']['wants_detailed_info']:
            for phase in customized_workflow.get('phases', []):
                phase['verbose_output'] = True
        
        # Add backup recommendations if needed
        if scenario_analysis['context']['backup_recommended']:
            backup_phase = {
                'name': 'Backup Preparation',
                'commands': ['wbadmin get versions', 'systempropertiesprotection'],
                'description': 'Verify backup status and create restore point'
            }
            customized_workflow['phases'].insert(0, backup_phase)
        
        return customized_workflow
    
    def _create_generic_workflow(self, scenario_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a generic workflow for unrecognized scenarios"""
        return {
            'phases': [
                {
                    'name': 'Information Gathering',
                    'commands': ['systeminfo', 'tasklist', 'netstat -an'],
                    'description': 'Gather system information for analysis'
                }
            ],
            'expected_time': '5-10 minutes',
            'risk_level': 'low',
            'requires_admin': False
        }
    
    def _build_scenario_workflows(self) -> Dict[str, Any]:
        """Build comprehensive scenario workflows"""
        return {
            'performance_optimization': {
                'phases': [
                    {
                        'name': 'System Analysis',
                        'commands': ['systeminfo', 'tasklist /svc', 'wmic cpu get name'],
                        'description': 'Analyze current system state and resource usage'
                    },
                    {
                        'name': 'Cleanup Operations',
                        'commands': ['cleanmgr /sagerun:1', 'sfc /scannow'],
                        'description': 'Clean temporary files and repair system files'
                    }
                ],
                'expected_time': '15-30 minutes',
                'risk_level': 'low',
                'requires_admin': True
            },
            'system_information': {
                'phases': [
                    {
                        'name': 'System Information Gathering',
                        'commands': ['systeminfo', 'msinfo32', 'dxdiag /t C:\\temp\\dxdiag.txt'],
                        'description': 'Gather comprehensive system information'
                    }
                ],
                'expected_time': '5-10 minutes',
                'risk_level': 'low',
                'requires_admin': False
            },
            'network_management': {
                'phases': [
                    {
                        'name': 'Network Assessment',
                        'commands': ['ipconfig /all', 'netstat -an', 'ping 8.8.8.8'],
                        'description': 'Assess current network configuration and connectivity'
                    }
                ],
                'expected_time': '5-15 minutes',
                'risk_level': 'low',
                'requires_admin': False
            }
        }
    
    def _build_ai_suggestions(self) -> Dict[str, List[str]]:
        """Build intelligent suggestions for different scenarios"""
        return {
            'performance_optimization': [
                "Monitor system performance for 24 hours to ensure improvements",
                "Consider disabling unnecessary startup programs",
                "Schedule regular maintenance tasks for optimal performance"
            ],
            'system_information': [
                "Save system information for future reference",
                "Compare specs with software requirements",
                "Consider hardware upgrades if needed"
            ],
            'network_management': [
                "Test connectivity after configuration changes",
                "Monitor network performance over time",
                "Consider updating network drivers if issues persist"
            ]
        }
    
    def _generate_smart_suggestions(self, scenario_analysis: Dict[str, Any], workflow: Dict[str, Any]) -> List[str]:
        """Generate intelligent suggestions based on scenario and workflow"""
        suggestions = []
        
        # Base suggestions from scenario
        base_suggestions = self.ai_suggestions.get(scenario_analysis['primary_scenario'], [])
        suggestions.extend(base_suggestions[:2])
        
        # Context-aware suggestions
        if scenario_analysis['context']['urgency'] == 'high':
            suggestions.append("Consider running critical commands first for immediate relief")
        
        if scenario_analysis['complexity'] == 'complex':
            suggestions.append("Break down the task into smaller steps for better control")
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _create_execution_plan(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed execution plan from workflow"""
        execution_plan = {
            'total_phases': len(workflow.get('phases', [])),
            'estimated_time': workflow.get('expected_time', 'Unknown'),
            'requires_admin': workflow.get('requires_admin', False),
            'risk_level': workflow.get('risk_level', 'unknown'),
            'phases': []
        }
        
        for i, phase in enumerate(workflow.get('phases', []), 1):
            phase_plan = {
                'phase_number': i,
                'name': phase['name'],
                'description': phase['description'],
                'commands': phase['commands'],
                'estimated_duration': self._estimate_phase_duration(phase),
                'prerequisites': self._determine_prerequisites(phase)
            }
            execution_plan['phases'].append(phase_plan)
        
        return execution_plan
    
    def _estimate_phase_duration(self, phase: Dict[str, Any]) -> str:
        """Estimate duration for a phase"""
        command_count = len(phase.get('commands', []))
        if command_count <= 2:
            return '1-3 minutes'
        elif command_count <= 5:
            return '3-8 minutes'
        else:
            return '8-15 minutes'
    
    def _determine_prerequisites(self, phase: Dict[str, Any]) -> List[str]:
        """Determine prerequisites for a phase"""
        prerequisites = []
        commands = phase.get('commands', [])
        
        for command in commands:
            if any(admin_cmd in command.lower() for admin_cmd in ['sfc', 'dism', 'chkdsk']):
                prerequisites.append('Administrator privileges required')
                break
        
        return prerequisites
    
    def _assess_risk(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level of the workflow"""
        risk_factors = {
            'data_loss_risk': False,
            'system_stability_risk': False,
            'requires_backup': False,
            'reversible': True
        }
        
        high_risk_commands = ['format', 'del', 'rmdir', 'reg delete']
        medium_risk_commands = ['chkdsk /f', 'sfc /scannow', 'dism']
        
        all_commands = []
        for phase in workflow.get('phases', []):
            all_commands.extend(phase.get('commands', []))
        
        commands_text = ' '.join(all_commands).lower()
        
        for cmd in high_risk_commands:
            if cmd in commands_text:
                risk_factors['data_loss_risk'] = True
                risk_factors['requires_backup'] = True
                risk_factors['reversible'] = False
                break
        
        for cmd in medium_risk_commands:
            if cmd in commands_text:
                risk_factors['system_stability_risk'] = True
                break
        
        return risk_factors
    
    def _predict_outcome(self, scenario_analysis: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Predict expected outcomes"""
        return {
            'success_probability': self._calculate_success_probability(scenario_analysis, workflow),
            'expected_improvements': self._predict_improvements(scenario_analysis),
            'potential_side_effects': ['Minimal side effects expected'],
            'follow_up_actions': self._suggest_follow_up(scenario_analysis)
        }
    
    def _calculate_success_probability(self, scenario_analysis: Dict[str, Any], workflow: Dict[str, Any]) -> str:
        """Calculate probability of successful outcome"""
        base_probability = 0.8
        
        if scenario_analysis['complexity'] == 'simple':
            base_probability += 0.1
        elif scenario_analysis['complexity'] == 'complex':
            base_probability -= 0.2
        
        percentage = max(0, min(100, base_probability * 100))
        
        if percentage >= 90:
            return 'Very High (90%+)'
        elif percentage >= 75:
            return 'High (75-90%)'
        else:
            return 'Moderate (60-75%)'
    
    def _predict_improvements(self, scenario_analysis: Dict[str, Any]) -> List[str]:
        """Predict expected improvements"""
        improvements_map = {
            'performance_optimization': [
                'Faster system startup and shutdown',
                'Improved application response times',
                'Better memory utilization'
            ],
            'system_information': [
                'Complete system overview',
                'Hardware specifications available',
                'System status assessment'
            ],
            'network_management': [
                'Improved network connectivity',
                'Better network performance',
                'Enhanced network security'
            ]
        }
        
        return improvements_map.get(scenario_analysis['primary_scenario'], ['General system improvements'])
    
    def _suggest_follow_up(self, scenario_analysis: Dict[str, Any]) -> List[str]:
        """Suggest follow-up actions"""
        follow_up_map = {
            'performance_optimization': [
                'Monitor system performance for 24-48 hours',
                'Schedule regular maintenance tasks'
            ],
            'system_information': [
                'Save system information for future reference',
                'Compare with software requirements'
            ],
            'network_management': [
                'Test network connectivity thoroughly',
                'Monitor network performance'
            ]
        }
        
        return follow_up_map.get(scenario_analysis['primary_scenario'], ['Monitor system behavior'])
    
    def execute_workflow_phase(self, phase: Dict[str, Any], confirmation_callback=None) -> Dict[str, Any]:
        """Execute a single phase of the workflow with intelligent monitoring"""
        phase_name = phase.get('name', 'Unknown Phase')
        commands = phase.get('commands', [])
        
        logger.info(f"Executing workflow phase: {phase_name}")
        
        results = []
        phase_success = True
        
        for i, command in enumerate(commands, 1):
            try:
                result = self._execute_single_command(command, f"{phase_name} - Step {i}")
                results.append(result)
                
                if result['status'] != 'success':
                    phase_success = False
                
            except Exception as e:
                logger.error(f"Error executing command {command}: {e}")
                results.append({
                    'command': command,
                    'status': 'error',
                    'message': str(e)
                })
                phase_success = False
        
        return {
            'phase_name': phase_name,
            'success': phase_success,
            'results': results,
            'summary': self._generate_phase_summary(results)
        }
    
    def _execute_single_command(self, command: str, context: str) -> Dict[str, Any]:
        """Execute a single command with proper error handling and output capture"""
        try:
            logger.info(f"Executing: {command} (Context: {context})")
            
            if command.endswith('.msc') or command.endswith('.cpl'):
                # GUI commands
                result = subprocess.run(command, shell=True, capture_output=False, timeout=5)
                return {
                    'command': command,
                    'status': 'success',
                    'message': f'Launched GUI application: {command}',
                    'output': f'GUI application {command} started'
                }
            else:
                # CLI commands
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.execution_stats['commands_executed'] += 1
                
                if result.returncode == 0:
                    return {
                        'command': command,
                        'status': 'success',
                        'message': 'Command executed successfully',
                        'output': result.stdout
                    }
                else:
                    return {
                        'command': command,
                        'status': 'error',
                        'message': f'Command failed with exit code {result.returncode}',
                        'output': result.stdout,
                        'error': result.stderr
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'status': 'timeout',
                'message': 'Command timed out',
                'output': ''
            }
        except Exception as e:
            return {
                'command': command,
                'status': 'error',
                'message': f'Execution failed: {str(e)}',
                'output': ''
            }
    
    def _generate_phase_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of phase execution"""
        total_commands = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] in ['error', 'timeout'])
        
        return {
            'total_commands': total_commands,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_commands * 100) if total_commands > 0 else 0
        }
    
    def format_analysis_output(self, analysis: Dict[str, Any]) -> str:
        """Format the intelligent analysis for user display"""
        scenario = analysis['scenario']
        workflow = analysis['workflow']
        suggestions = analysis['suggestions']
        execution_plan = analysis['execution_plan']
        
        output = f"🤖 **Windows Expert Analysis**\n\n"
        
        # Scenario Summary
        output += f"**📋 Scenario Detected:** {scenario['primary_scenario'].replace('_', ' ').title()}\n"
        output += f"**🎯 User Intent:** {scenario['user_intent']['primary_intent'].replace('_', ' ').title()}\n"
        output += f"**⚡ Complexity:** {scenario['complexity'].title()}\n\n"
        
        # Execution Plan
        output += f"**🔧 Execution Plan:**\n"
        output += f"• **Total Phases:** {execution_plan['total_phases']}\n"
        output += f"• **Estimated Time:** {execution_plan['estimated_time']}\n"
        output += f"• **Admin Required:** {'Yes' if execution_plan['requires_admin'] else 'No'}\n"
        output += f"• **Risk Level:** {execution_plan['risk_level'].title()}\n\n"
        
        # Workflow Phases
        if execution_plan['phases']:
            output += f"**📝 Workflow Phases:**\n"
            for i, phase in enumerate(execution_plan['phases'], 1):
                output += f"{i}. **{phase['name']}** ({phase['estimated_duration']})\n"
                output += f"   _{phase['description']}_\n\n"
        
        # Smart Suggestions
        if suggestions:
            output += f"**💡 Smart Suggestions:**\n"
            for suggestion in suggestions[:3]:
                output += f"• {suggestion}\n"
        
        return output
    
    def _build_command_database(self) -> Dict[str, Any]:
        """Build comprehensive Windows command knowledge base"""
        return {
            'system_info': {
                'commands': {
                    'systeminfo': {'description': 'Display system configuration', 'category': 'info'},
                    'msinfo32': {'description': 'System Information utility', 'category': 'info'},
                    'dxdiag': {'description': 'DirectX diagnostics', 'category': 'info'}
                }
            },
            'network': {
                'commands': {
                    'ipconfig': {'description': 'IP configuration', 'category': 'network'},
                    'ping': {'description': 'Test network connectivity', 'category': 'network'},
                    'netstat': {'description': 'Network statistics', 'category': 'network'}
                }
            }
        }
    
    def _extract_app_name(self, user_request: str) -> str:
        """Extract application name from user request"""
        request_lower = user_request.lower()
        
        # Common application mappings
        app_patterns = {
            'notepad': 'notepad',
            'calculator': 'calc',
            'task manager': 'taskmgr',
            'command prompt': 'cmd',
            'powershell': 'powershell',
            'file explorer': 'explorer',
            'control panel': 'control',
            'registry editor': 'regedit',
            'system configuration': 'msconfig',
            'disk cleanup': 'cleanmgr'
        }
        
        for app_name, executable in app_patterns.items():
            if app_name in request_lower:
                return executable
        
        # Try to extract app name after "open" or "start"
        import re
        match = re.search(r'(?:open|start|launch|run)\s+([a-zA-Z0-9\s]+)', request_lower)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _requires_admin_analysis(self, user_request: str) -> bool:
        """Analyze if request requires administrator privileges"""
        admin_keywords = [
            'registry', 'regedit', 'system file', 'sfc', 'dism', 'services',
            'policy', 'gpo', 'administrator', 'admin', 'permissions',
            'install', 'uninstall', 'driver', 'system restore'
        ]
        
        return any(keyword in user_request.lower() for keyword in admin_keywords)
    
    def _identify_primary_tools(self, user_request: str) -> List[str]:
        """Identify primary Windows tools needed for the request"""
        request_lower = user_request.lower()
        tools = []
        
        tool_patterns = {
            'Command Prompt': ['cmd', 'command', 'prompt', 'dos'],
            'PowerShell': ['powershell', 'ps1', 'script'],
            'Task Manager': ['process', 'task manager', 'taskmgr', 'resource'],
            'Registry Editor': ['registry', 'regedit', 'reg'],
            'Control Panel': ['control panel', 'settings', 'configuration'],
            'File Explorer': ['file', 'folder', 'explorer', 'directory'],
            'System Configuration': ['msconfig', 'startup', 'boot'],
            'Disk Management': ['disk', 'partition', 'drive', 'storage']
        }
        
        for tool_name, keywords in tool_patterns.items():
            if any(keyword in request_lower for keyword in keywords):
                tools.append(tool_name)
        
        return tools if tools else ['Command Prompt']  # Default to Command Prompt
    
    def _assess_safety_level(self, user_request: str) -> str:
        """Assess safety level of the request"""
        request_lower = user_request.lower()
        
        high_risk_keywords = [
            'delete', 'format', 'registry', 'system file', 'boot',
            'partition', 'driver', 'uninstall', 'remove'
        ]
        
        medium_risk_keywords = [
            'modify', 'change', 'edit', 'configure', 'install', 'update'
        ]
        
        if any(keyword in request_lower for keyword in high_risk_keywords):
            return 'high_risk'
        elif any(keyword in request_lower for keyword in medium_risk_keywords):
            return 'medium_risk'
        else:
            return 'safe'
    
    def _get_explanation_level(self, user_level: str) -> str:
        """Get appropriate explanation level for user"""
        explanation_levels = {
            'beginner': 'detailed_with_context',
            'intermediate': 'moderate_explanation',
            'advanced': 'minimal_explanation'
        }
        
        return explanation_levels.get(user_level, 'moderate_explanation')
    
    def _assess_dynamic_risk(self, user_request: str) -> Dict[str, Any]:
        """Assess risk for dynamic execution"""
        safety_level = self._assess_safety_level(user_request)
        requires_admin = self._requires_admin_analysis(user_request)
        
        risk_assessment = {
            'safety_level': safety_level,
            'requires_admin': requires_admin,
            'reversible': self._is_operation_reversible(user_request),
            'backup_recommended': safety_level in ['high_risk', 'medium_risk'],
            'confirmation_required': safety_level == 'high_risk'
        }
        
        return risk_assessment
    
    def _is_operation_reversible(self, user_request: str) -> bool:
        """Check if operation can be easily reversed"""
        irreversible_keywords = [
            'delete', 'format', 'remove', 'uninstall', 'destroy', 'wipe'
        ]
        
        return not any(keyword in user_request.lower() for keyword in irreversible_keywords)
    
    def get_dynamic_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate user-friendly summary of AI-guided analysis"""
        scenario = analysis.get('scenario', {})
        user_level = analysis.get('user_level', 'intermediate')
        suggestions = analysis.get('suggestions', [])
        
        output = f"🤖 **AI-Guided Windows Assistant**\n\n"
        
        # Goal Understanding
        output += f"**🎯 Goal:** {scenario.get('goal', 'Task completion')}\n"
        output += f"**👤 User Level:** {user_level.title()}\n"
        output += f"**🛡️ Safety Level:** {scenario.get('safety_level', 'safe').replace('_', ' ').title()}\n\n"
        
        # Approach
        output += f"**🔄 Approach:** AI-guided step-by-step execution\n"
        output += f"**⚡ Strategy:** One command at a time with intelligent error correction\n"
        output += f"**🎓 Explanation Level:** {self._get_explanation_level(user_level).replace('_', ' ').title()}\n\n"
        
        # First Commands
        if suggestions:
            output += f"**🚀 First Steps:**\n"
            for i, suggestion in enumerate(suggestions, 1):
                if isinstance(suggestion, dict):
                    purpose = suggestion.get('purpose', str(suggestion))
                    output += f"{i}. {purpose}\n"
                else:
                    output += f"{i}. {suggestion}\n"
            
            output += f"\n💡 **Each command will be executed one by one with explanations and error correction**\n"
        
        # Risk Assessment
        risk = analysis.get('risk_assessment', {})
        if risk.get('requires_admin'):
            output += f"\n⚠️ **Note:** Some commands may require administrator privileges\n"
        
        if risk.get('backup_recommended'):
            output += f"💾 **Recommendation:** Consider creating a system backup first\n"
        
        return output

# Global instance
windows_expert = WindowsCommandExpert()
