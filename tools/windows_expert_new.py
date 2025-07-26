"""
Comprehensive Windows 10/11 Expert Agent
Intelligent scenario analysis and complete task execution
"""
import subprocess
import os
import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class WindowsCommandExpert:
    """Intelligent Windows Expert Agent for complete scenario handling"""
    
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
    
    def analyze_request(self, user_request: str) -> Dict[str, Any]:
        """Intelligent analysis of user request with complete workflow planning"""
        logger.info(f"Analyzing Windows scenario: {user_request}")
        
        # Enhanced scenario detection
        scenario_analysis = self._analyze_scenario(user_request)
        
        # Generate complete workflow
        workflow = self._generate_workflow(scenario_analysis)
        
        # Provide intelligent suggestions
        suggestions = self._generate_smart_suggestions(scenario_analysis, workflow)
        
        return {
            'scenario': scenario_analysis,
            'workflow': workflow,
            'suggestions': suggestions,
            'execution_plan': self._create_execution_plan(workflow),
            'risk_assessment': self._assess_risk(workflow),
            'expected_outcome': self._predict_outcome(scenario_analysis, workflow)
        }
    
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

# Global instance
windows_expert = WindowsCommandExpert()
