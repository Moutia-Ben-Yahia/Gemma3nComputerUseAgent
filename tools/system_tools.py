"""
Enhanced system tools for Windows OS interaction with better performance and caching
Advanced Windows 10/11 command execution and scenario handling
"""
import os
import subprocess
import psutil
import pyautogui
import time
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from utils.local_cache import local_cache
from utils.error_handling import retry_with_backoff, safe_execute
from tools.windows_expert import windows_expert

logger = logging.getLogger(__name__)

class SystemTools:
    """Enhanced tools for interacting with Windows OS"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Performance tracking
        self.operation_stats = {
            'app_operations': 0,
            'file_operations': 0,
            'system_queries': 0,
            'cache_hits': 0,
            'errors': 0
        }
    
    def execute_windows_command_ai_guided(self, user_request: str) -> Dict[str, Any]:
        """Execute Windows commands with AI guidance and error correction - Universal Windows Expert"""
        try:
            logger.info(f"🤖 Universal AI-guided Windows execution: {user_request}")
            
            # Get universal AI analysis using the new expert system
            analysis = windows_expert.analyze_request(user_request)
            
            # The new universal system always provides AI guidance
            if not analysis or analysis.get('error'):
                return {
                    'success': False,
                    'message': 'Universal Windows Expert could not analyze this request',
                    'analysis': analysis
                }
            
            # Get AI-guided command suggestions from universal analysis
            ai_commands = analysis.get('ai_guided_commands', [])
            
            if not ai_commands:
                return {
                    'success': False,
                    'message': 'Universal Expert could not generate appropriate commands for this request',
                    'analysis': analysis
                }
            
            # Execute first AI-guided command with universal error correction
            first_command = ai_commands[0]
            execution_result = windows_expert.execute_dynamic_command(first_command, context=user_request)
            
            # Universal AI-guided response formatting
            response = {
                'success': execution_result['status'] == 'success',
                'message': self._format_ai_guided_response(execution_result, analysis),
                'execution_results': [execution_result],
                'analysis': analysis,
                'guidance': execution_result.get('execution_guidance', {}),
                'next_suggestions': execution_result.get('next_suggestions', []),
                'type': 'universal_ai_guided_execution'
            }
            
            # Add intelligent next-step suggestions from universal system
            if execution_result.get('next_suggestions'):
                response['suggestions'] = [
                    cmd.get('purpose', cmd.get('command', '')) 
                    for cmd in execution_result['next_suggestions'][:3]  # Limit to top 3
                ]
            
            # Add universal guidance summary
            if execution_result.get('execution_guidance'):
                guidance = execution_result['execution_guidance']
                response['status_summary'] = guidance.get('status_summary', 'Command executed')
                response['progress'] = guidance.get('progress_indicator', '')
            
            return response
            
        except Exception as e:
            logger.error(f"Universal AI-guided execution failed: {e}")
            return {
                'success': False,
                'message': f'Universal Windows Expert encountered an error: {str(e)}. The system can handle any Windows scenario - please try rephrasing your request.',
                'error': str(e),
                'fallback_suggestion': 'Try describing your goal in different words or break it into smaller steps'
            }
    
    def _format_ai_guided_response(self, execution_result: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Format Universal AI-guided execution response for user"""
        
        guidance = execution_result.get('execution_guidance', {})
        output = execution_result.get('output', '')
        
        # Start with intelligent status from Universal Expert
        message = guidance.get('status_summary', f"✅ Command executed: {execution_result.get('message', 'Completed')}")
        
        # Add what happened explanation (Universal AI understanding)
        if guidance.get('what_happened'):
            message += f"\n\n📝 **What happened:** {guidance['what_happened']}"
        
        # Add command output if meaningful and not too long
        if output and len(output) < 500 and execution_result['status'] == 'success':
            message += f"\n\n**Command Output:**\n```\n{output}\n```"
        elif output and len(output) >= 500:
            message += f"\n\n**Output:** Command completed successfully (detailed output available)"
        elif execution_result.get('type') == 'guidance':
            # For guidance commands, include the message directly
            message += f"\n\n💭 **AI Guidance:** {execution_result.get('message', '')}"
        
        # Add Universal AI next steps guidance
        if guidance.get('next_steps'):
            message += f"\n\n🔄 **Next Steps:** {guidance['next_steps']}"
        
        # Add progress indicator from Universal system
        if guidance.get('progress_indicator'):
            message += f"\n\n📊 **Progress:** {guidance['progress_indicator']}"
        
        # Add user action needed warning
        if guidance.get('user_action_needed'):
            message += f"\n\n⚠️ **Action Required:** Please follow the suggested steps above"
        
        # Add Universal Expert's error correction info if command failed but recovery is in progress
        if execution_result['status'] != 'success' and execution_result.get('adaptation_success'):
            message += f"\n\n🔧 **Auto-Recovery:** Universal Expert automatically tried an alternative approach and succeeded"
        
        # Add intelligent suggestions from Universal Expert
        if execution_result.get('next_suggestions'):
            suggestions = execution_result['next_suggestions'][:2]  # Top 2 suggestions
            message += f"\n\n💡 **AI Recommendations:**"
            for i, suggestion in enumerate(suggestions, 1):
                purpose = suggestion.get('purpose', suggestion.get('command', 'Next step'))
                message += f"\n  {i}. {purpose}"
        
        return message
        """Open a Windows application with enhanced reliability"""
        self.operation_stats['app_operations'] += 1
        
        # Check cache for recent successful app launches
        cached_result = local_cache.get('app_launches', app_name.lower())
        if cached_result and cached_result.get('success'):
            self.operation_stats['cache_hits'] += 1
            logger.info(f"Using cached launch method for {app_name}")
            
            # Try the cached method first
            if self._try_launch_method(app_name, cached_result.get('method')):
                return {'success': True, 'message': f"{app_name} opened successfully (cached method)"}
        
        app_mappings = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'calc': 'calc.exe',
            'paint': 'mspaint.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'explorer': 'explorer.exe',
            'file explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'task manager': 'taskmgr.exe',
            'taskmgr': 'taskmgr.exe',
            'taskmanager': 'taskmgr.exe',
            'control panel': 'control.exe',
            'control': 'control.exe',
            'settings': 'ms-settings:',
            'wordpad': 'wordpad.exe',
            'mspaint': 'mspaint.exe',
            'snipping tool': 'snippingtool.exe',
            'registry editor': 'regedit.exe',
            'regedit': 'regedit.exe'
        }
        
        app_executable = app_mappings.get(app_name.lower(), app_name)
        
        # Try multiple launch methods
        launch_methods = [
            ('keyboard_shortcut', lambda: self._try_keyboard_shortcut(app_name)),
            ('direct_executable', lambda: self._try_direct_executable(app_executable)),
            ('start_command', lambda: self._try_start_command(app_executable)),
            ('search_and_launch', lambda: self._try_search_and_launch(app_name))
        ]
        
        last_error = None
        for method_name, method in launch_methods:
            try:
                if self._try_launch_method(app_name, method_name):
                    # Cache successful method
                    local_cache.set(
                        'app_launches', 
                        app_name.lower(), 
                        {'success': True, 'method': method_name},
                        ttl_seconds=86400  # 24 hours
                    )
                    
                    logger.info(f"Successfully opened {app_name} using {method_name}")
                    return {
                        "success": True, 
                        "message": f"Opened {app_name} using {method_name}",
                        "method": method_name
                    }
            except Exception as e:
                last_error = e
                logger.debug(f"Method {method_name} failed for {app_name}: {e}")
                continue
        
        # All methods failed
        self.operation_stats['errors'] += 1
        error_msg = f"Failed to open {app_name}. Last error: {last_error}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}
    
    def _try_launch_method(self, app_name: str, method_name: str) -> bool:
        """Try specific launch method"""
        if method_name == 'keyboard_shortcut':
            return self._try_keyboard_shortcut(app_name)
        elif method_name == 'direct_executable':
            app_mappings = {
                'notepad': 'notepad.exe', 'calculator': 'calc.exe', 'calc': 'calc.exe',
                'paint': 'mspaint.exe', 'chrome': 'chrome.exe', 'firefox': 'firefox.exe',
                'word': 'winword.exe', 'excel': 'excel.exe', 'task manager': 'taskmgr.exe',
                'taskmgr': 'taskmgr.exe', 'taskmanager': 'taskmgr.exe', 'control panel': 'control.exe',
                'control': 'control.exe', 'settings': 'ms-settings:', 'wordpad': 'wordpad.exe',
                'mspaint': 'mspaint.exe', 'snipping tool': 'snippingtool.exe',
                'registry editor': 'regedit.exe', 'regedit': 'regedit.exe'
            }
            app_executable = app_mappings.get(app_name.lower(), app_name)
            return self._try_direct_executable(app_executable)
        elif method_name == 'start_command':
            return self._try_start_command(app_name)
        elif method_name == 'search_and_launch':
            return self._try_search_and_launch(app_name)
        return False
    
    def _try_keyboard_shortcut(self, app_name: str) -> bool:
        """Try opening app with keyboard shortcuts"""
        shortcuts = {
            'task manager': ('ctrl', 'shift', 'esc'),
            'taskmgr': ('ctrl', 'shift', 'esc'),
            'taskmanager': ('ctrl', 'shift', 'esc'),
        }
        
        if app_name.lower() in shortcuts:
            pyautogui.hotkey(*shortcuts[app_name.lower()])
            time.sleep(1)
            return True
        return False
    
    def _try_direct_executable(self, app_executable: str) -> bool:
        """Try direct executable launch"""
        try:
            if app_executable.startswith('ms-settings:'):
                subprocess.Popen(['start', app_executable], shell=True)
            else:
                subprocess.Popen([app_executable])
            time.sleep(0.5)
            return True
        except Exception:
            return False
    
    def _try_start_command(self, app_name: str) -> bool:
        """Try using Windows start command"""
        try:
            subprocess.Popen(['start', '', app_name], shell=True)
            time.sleep(0.5)
            return True
        except Exception:
            return False
    
    def _try_search_and_launch(self, app_name: str) -> bool:
        """Try using Windows search to launch app"""
        try:
            # Open Windows search
            pyautogui.hotkey('win')
            time.sleep(0.5)
            
            # Type app name
            pyautogui.typewrite(app_name)
            time.sleep(0.5)
            
            # Press Enter to launch
            pyautogui.press('enter')
            time.sleep(0.5)
            
            return True
        except Exception:
            return False
    
    def close_application(self, app_name: str) -> Dict[str, Any]:
        """Close application by name"""
        try:
            closed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed_count += 1
            
            if closed_count > 0:
                logger.info(f"Closed {closed_count} instances of {app_name}")
                return {"status": "success", "message": f"Closed {closed_count} instances of {app_name}"}
            else:
                return {"status": "info", "message": f"No running instances of {app_name} found"}
                
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {e}")
            return {"status": "error", "message": f"Failed to close {app_name}: {str(e)}"}
    
    def list_running_processes(self) -> List[Dict[str, Any]]:
        """List running processes with caching for better performance"""
        return self._safe_list_processes()
    
    def _safe_list_processes(self) -> List[Dict[str, Any]]:
        """Internal method for listing processes with error handling"""
        try:
            self.operation_stats['system_queries'] += 1
            
            # Check cache first (cache for 30 seconds)
            cached_processes = local_cache.get('system_info', 'running_processes')
            if cached_processes:
                self.operation_stats['cache_hits'] += 1
                logger.debug("Using cached process list")
                return cached_processes
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    memory_mb = round(proc.info['memory_info'].rss / 1024 / 1024, 2)
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': memory_mb,
                        'cpu_percent': proc.info.get('cpu_percent', 0)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by memory usage (highest first)
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            # Cache the result
            local_cache.set('system_info', 'running_processes', processes, ttl_seconds=30)
            
            logger.debug(f"Retrieved {len(processes)} running processes")
            return processes
        except Exception as e:
            logger.error(f"Failed to list processes: {e}")
            self.operation_stats['errors'] += 1
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            # Get CPU and memory info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'operation_stats': self.operation_stats
            }
            
            # Cache stats for 10 seconds
            local_cache.set('system_info', 'system_stats', stats, ttl_seconds=10)
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {'error': str(e)}
    
    def analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze processes consuming high resources"""
        try:
            logger.info("Analyzing system resource usage...")
            
            # Get current system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Get all processes with detailed info
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'memory_percent']):
                try:
                    # Get CPU usage for this specific process
                    proc_cpu = proc.cpu_percent(interval=0.1)
                    memory_mb = round(proc.info['memory_info'].rss / 1024 / 1024, 2)
                    memory_percent = round((proc.info['memory_info'].rss / memory.total) * 100, 2)
                    
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory_mb': memory_mb,
                        'memory_percent': memory_percent,
                        'cpu_percent': proc_cpu
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by memory usage first, then CPU
            processes.sort(key=lambda x: (x['memory_mb'], x['cpu_percent']), reverse=True)
            
            # Identify high resource consumers
            high_memory = [p for p in processes if p['memory_mb'] > 100][:10]  # Top 10 by memory
            high_cpu = [p for p in processes if p['cpu_percent'] > 5][:10]     # Top 10 by CPU
            
            analysis = {
                'system_summary': {
                    'total_cpu_usage': cpu_percent,
                    'total_memory_usage': memory.percent,
                    'available_memory_gb': round(memory.available / (1024**3), 2),
                    'total_processes': len(processes)
                },
                'high_memory_processes': high_memory,
                'high_cpu_processes': high_cpu,
                'top_10_overall': processes[:10]
            }
            
            logger.info(f"Resource analysis complete: {len(high_memory)} high memory, {len(high_cpu)} high CPU processes")
            return {
                'success': True,
                'analysis': analysis,
                'message': self._format_resource_analysis(analysis)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze resource usage: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_resource_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format resource analysis into readable text"""
        system = analysis['system_summary']
        high_mem = analysis['high_memory_processes']
        high_cpu = analysis['high_cpu_processes']
        
        result = f"🖥️ **System Resource Analysis**\n\n"
        result += f"**Overall System Usage:**\n"
        result += f"• CPU: {system['total_cpu_usage']:.1f}%\n"
        result += f"• Memory: {system['total_memory_usage']:.1f}% ({system['available_memory_gb']:.1f}GB available)\n"
        result += f"• Total Processes: {system['total_processes']}\n\n"
        
        if high_mem:
            result += f"**🔥 High Memory Consumers (>100MB):**\n"
            for i, proc in enumerate(high_mem[:5], 1):
                result += f"{i}. {proc['name']} - {proc['memory_mb']:.1f}MB ({proc['memory_percent']:.1f}%)\n"
            result += "\n"
        
        if high_cpu:
            result += f"**⚡ High CPU Consumers (>5%):**\n"
            for i, proc in enumerate(high_cpu[:5], 1):
                result += f"{i}. {proc['name']} - {proc['cpu_percent']:.1f}% CPU\n"
            result += "\n"
        
        result += f"**📊 Top Overall Resource Users:**\n"
        for i, proc in enumerate(analysis['top_10_overall'][:5], 1):
            result += f"{i}. {proc['name']} - {proc['memory_mb']:.1f}MB, {proc['cpu_percent']:.1f}% CPU\n"
        
        return result

    def scan_wifi_networks(self) -> Dict[str, Any]:
        """Scan and list available WiFi networks"""
        try:
            logger.info("Scanning for WiFi networks...")
            
            # Use Windows netsh command to scan for WiFi networks
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return {'success': False, 'error': 'WiFi scanning failed - WiFi may be disabled'}
            
            # Parse the output to extract network names
            networks = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'All User Profile' in line or 'Profil Tous les utilisateurs' in line:
                    # Extract network name (after the colon)
                    parts = line.split(':')
                    if len(parts) > 1:
                        network_name = parts[1].strip()
                        networks.append(network_name)
            
            # Get detailed information for each network
            detailed_networks = []
            for network in networks[:10]:  # Limit to first 10 for performance
                try:
                    detail_result = subprocess.run(
                        ["netsh", "wlan", "show", "profile", f'name="{network}"', "key=clear"],
                        capture_output=True,
                        text=True,
                        encoding='utf-8'
                    )
                    
                    if detail_result.returncode == 0:
                        # Parse security type and other details
                        detail_lines = detail_result.stdout.split('\n')
                        security_type = "Unknown"
                        authentication = "Unknown"
                        
                        for detail_line in detail_lines:
                            if 'Security type' in detail_line or 'Type de sécurité' in detail_line:
                                security_type = detail_line.split(':')[1].strip() if ':' in detail_line else "Unknown"
                            elif 'Authentication' in detail_line or 'Authentification' in detail_line:
                                authentication = detail_line.split(':')[1].strip() if ':' in detail_line else "Unknown"
                        
                        detailed_networks.append({
                            'name': network,
                            'security': security_type,
                            'authentication': authentication
                        })
                    else:
                        detailed_networks.append({
                            'name': network,
                            'security': 'Unknown',
                            'authentication': 'Unknown'
                        })
                except Exception as e:
                    logger.warning(f"Failed to get details for network {network}: {e}")
                    detailed_networks.append({
                        'name': network,
                        'security': 'Unknown',
                        'authentication': 'Unknown'
                    })
            
            # Also scan for currently available networks
            scan_result = subprocess.run(
                ["netsh", "wlan", "show", "network"],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            available_networks = []
            if scan_result.returncode == 0:
                scan_lines = scan_result.stdout.split('\n')
                current_network = {}
                
                for line in scan_lines:
                    line = line.strip()
                    if 'SSID' in line and ':' in line:
                        if current_network:
                            available_networks.append(current_network)
                        current_network = {'name': line.split(':')[1].strip()}
                    elif 'Authentication' in line and ':' in line:
                        current_network['authentication'] = line.split(':')[1].strip()
                    elif 'Encryption' in line and ':' in line:
                        current_network['encryption'] = line.split(':')[1].strip()
                    elif 'Signal' in line and ':' in line:
                        current_network['signal'] = line.split(':')[1].strip()
                
                if current_network:
                    available_networks.append(current_network)
            
            total_count = len(detailed_networks) + len([n for n in available_networks if not any(saved['name'] == n['name'] for saved in detailed_networks)])
            
            analysis = {
                'saved_networks': detailed_networks,
                'available_networks': available_networks[:10],  # Limit for readability
                'total_saved': len(detailed_networks),
                'total_available': len(available_networks)
            }
            
            return {
                'success': True,
                'analysis': analysis,
                'message': self._format_wifi_analysis(analysis)
            }
            
        except Exception as e:
            logger.error(f"Failed to scan WiFi networks: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_wifi_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format WiFi analysis into readable text"""
        saved = analysis['saved_networks']
        available = analysis['available_networks']
        
        result = f"📶 **WiFi Networks Analysis**\n\n"
        result += f"**Summary:**\n"
        result += f"• Saved Networks: {analysis['total_saved']}\n"
        result += f"• Available Networks: {analysis['total_available']}\n\n"
        
        if saved:
            result += f"**💾 Saved WiFi Networks:**\n"
            for i, network in enumerate(saved[:8], 1):  # Show top 8
                result += f"{i}. {network['name']} - {network['security']} ({network['authentication']})\n"
            result += "\n"
        
        if available:
            result += f"**📡 Currently Available Networks:**\n"
            for i, network in enumerate(available[:8], 1):  # Show top 8
                name = network.get('name', 'Unknown')
                signal = network.get('signal', 'Unknown')
                auth = network.get('authentication', 'Unknown')
                result += f"{i}. {name} - Signal: {signal}, Security: {auth}\n"
        
        if not saved and not available:
            result += "❌ No WiFi networks found. WiFi may be disabled or no adapter detected.\n"
        
        return result

    def create_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """Create a new file"""
        logger.info(f"create_file called with path='{file_path}', content='{content}'")
        try:
            path = Path(file_path)
            logger.info(f"Resolved path: {path.absolute()}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            logger.info(f"File written successfully: {file_path}")
            
            # Verify file was created
            if path.exists():
                actual_content = path.read_text(encoding='utf-8')
                logger.info(f"File verified - exists: True, content: '{actual_content}'")
            else:
                logger.error(f"File creation failed - file does not exist after write")
            
            return {"status": "success", "message": f"Created file: {file_path}"}
        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            return {"status": "error", "message": f"Failed to create file: {str(e)}"}
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file content"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"status": "error", "message": "File not found"}
            
            content = path.read_text(encoding='utf-8')
            return {"status": "success", "content": content, "size": len(content)}
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {"status": "error", "message": f"Failed to read file: {str(e)}"}
    
    def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(dir_path)
            if not path.exists():
                return {"status": "error", "message": "Directory not found"}
            
            items = []
            for item in path.iterdir():
                items.append({
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else 0
                })
            
            return {"status": "success", "items": items, "count": len(items)}
        except Exception as e:
            logger.error(f"Failed to list directory {dir_path}: {e}")
            return {"status": "error", "message": f"Failed to list directory: {str(e)}"}
    
    def run_command(self, command: str) -> Dict[str, Any]:
        """Run shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "status": "success",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out"}
        except Exception as e:
            logger.error(f"Failed to run command {command}: {e}")
            return {"status": "error", "message": f"Failed to run command: {str(e)}"}
    
    def type_text(self, text: str) -> Dict[str, Any]:
        """Type text at current cursor position"""
        try:
            pyautogui.typewrite(text)
            return {"status": "success", "message": f"Typed: {text[:50]}..."}
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return {"status": "error", "message": f"Failed to type text: {str(e)}"}
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """Press a key"""
        try:
            pyautogui.press(key)
            return {"status": "success", "message": f"Pressed key: {key}"}
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
            return {"status": "error", "message": f"Failed to press key: {str(e)}"}

    def scan_available_wifi_networks(self) -> Dict[str, Any]:
        """Scan for currently available WiFi networks (real-time scan)"""
        try:
            logger.info("Scanning for currently available WiFi networks...")
            
            # First, refresh the WiFi scan to get latest networks
            refresh_result = subprocess.run(
                ["netsh", "wlan", "refresh"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Small delay to let the refresh complete
            import time
            time.sleep(2)
            
            # Now scan for available networks with detailed info
            scan_result = subprocess.run(
                ["netsh", "wlan", "show", "network", "mode=bssid"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=15
            )
            
            available_networks = []
            if scan_result.returncode == 0:
                scan_lines = scan_result.stdout.split('\n')
                current_network = {}
                
                for line in scan_lines:
                    line = line.strip()
                    if 'SSID' in line and ':' in line and 'BSSID' not in line:
                        if current_network and current_network.get('name'):
                            available_networks.append(current_network)
                        ssid = line.split(':', 1)[1].strip()
                        if ssid:  # Only add non-empty SSIDs
                            current_network = {'name': ssid}
                    elif 'Network type' in line and ':' in line:
                        current_network['type'] = line.split(':', 1)[1].strip()
                    elif 'Authentication' in line and ':' in line:
                        current_network['authentication'] = line.split(':', 1)[1].strip()
                    elif 'Encryption' in line and ':' in line:
                        current_network['encryption'] = line.split(':', 1)[1].strip()
                    elif 'Signal' in line and ':' in line:
                        current_network['signal'] = line.split(':', 1)[1].strip()
                    elif 'BSSID' in line and ':' in line:
                        # This indicates multiple access points for same SSID
                        if 'access_points' not in current_network:
                            current_network['access_points'] = 1
                        else:
                            current_network['access_points'] += 1
                
                if current_network and current_network.get('name'):
                    available_networks.append(current_network)
            
            # Remove duplicates and empty names
            unique_networks = []
            seen_names = set()
            for network in available_networks:
                name = network.get('name', '').strip()
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_networks.append(network)
            
            analysis = {
                'available_networks': unique_networks,
                'total_available': len(unique_networks),
                'scan_time': time.strftime('%H:%M:%S')
            }
            
            return {
                'success': True,
                'analysis': analysis,
                'message': self._format_available_wifi_analysis(analysis)
            }
            
        except Exception as e:
            logger.error(f"Available WiFi scan failed: {e}")
            return {'success': False, 'error': str(e)}

    def _format_available_wifi_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format available WiFi networks analysis for display"""
        networks = analysis.get('available_networks', [])
        total = analysis.get('total_available', 0)
        scan_time = analysis.get('scan_time', 'Unknown')
        
        if total == 0:
            return "📶 **Available WiFi Networks**\n\n❌ No WiFi networks detected.\n\n💡 Make sure WiFi is enabled and try again."
        
        result = f"📶 **Currently Available WiFi Networks** (Scanned at {scan_time})\n\n"
        result += f"**🔍 Networks Found:** {total}\n\n"
        
        for i, network in enumerate(networks, 1):
            name = network.get('name', 'Unknown')
            signal = network.get('signal', 'Unknown')
            auth = network.get('authentication', 'Unknown')
            encryption = network.get('encryption', 'Unknown')
            network_type = network.get('type', 'Unknown')
            access_points = network.get('access_points', 1)
            
            result += f"**{i}. {name}**\n"
            result += f"   • Signal Strength: {signal}\n"
            result += f"   • Security: {auth}\n"
            result += f"   • Encryption: {encryption}\n"
            result += f"   • Type: {network_type}\n"
            if access_points > 1:
                result += f"   • Access Points: {access_points}\n"
            result += "\n"
        
        return result

    def execute_windows_command(self, user_request: str) -> Dict[str, Any]:
        """Execute Windows commands using intelligent expert analysis and workflow execution"""
        try:
            logger.info(f"🤖 Intelligent Windows Expert analyzing: {user_request}")
            
            # Get comprehensive analysis from the expert
            analysis = windows_expert.analyze_request(user_request)
            
            # Determine execution mode based on complexity and user intent
            execution_mode = self._determine_execution_mode(analysis)
            
            if execution_mode == 'analysis_only':
                # User wants information/analysis without execution
                return {
                    'status': 'success',
                    'message': windows_expert.format_analysis_output(analysis),
                    'analysis': analysis,
                    'execution_mode': 'analysis_only'
                }
                
            elif execution_mode == 'guided_execution':
                # Execute with user guidance and confirmations
                return self._execute_guided_workflow(analysis, user_request)
                
            elif execution_mode == 'automatic_execution':
                # Safe automatic execution for low-risk workflows
                return self._execute_automatic_workflow(analysis, user_request)
                
            else:
                # Default to analysis with suggestions
                return {
                    'status': 'success',
                    'message': windows_expert.format_analysis_output(analysis) + 
                              "\n\n💡 **Next Steps:** Say 'execute' to run this workflow or 'explain' for more details.",
                    'analysis': analysis,
                    'execution_mode': 'ready_for_execution'
                }
                
        except Exception as e:
            logger.error(f"Windows expert analysis failed: {e}")
            return {
                "status": "error", 
                "message": f"❌ Windows Expert Error: {str(e)}\n\nPlease try rephrasing your request or contact support."
            }
    
    def _determine_execution_mode(self, analysis: Dict[str, Any]) -> str:
        """Determine how to execute based on analysis"""
        scenario = analysis['scenario']
        risk_assessment = analysis['risk_assessment']
        workflow = analysis['workflow']
        
        # Check for information-gathering intents
        if scenario['user_intent']['primary_intent'] == 'gather_info':
            return 'analysis_only'
        
        # Check risk levels
        if risk_assessment['data_loss_risk'] or risk_assessment['system_stability_risk']:
            return 'guided_execution'
        
        # Check if workflow requires admin or has multiple phases
        if workflow.get('requires_admin') or len(workflow.get('phases', [])) > 2:
            return 'guided_execution'
        
        # Simple, low-risk tasks can be automated
        if (scenario['complexity'] == 'simple' and 
            workflow.get('risk_level') == 'low' and 
            not risk_assessment['requires_backup']):
            return 'automatic_execution'
        
        return 'guided_execution'
    
    def _execute_guided_workflow(self, analysis: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """Execute workflow with user guidance and safety checks"""
        workflow = analysis['workflow']
        phases = workflow.get('phases', [])
        
        if not phases:
            return {
                'status': 'error',
                'message': '❌ No executable workflow phases found for this request.'
            }
        
        # For now, execute the first phase as a demonstration
        # In a full implementation, this would be interactive
        first_phase = phases[0]
        
        logger.info(f"Executing guided workflow phase: {first_phase['name']}")
        
        # Execute the phase
        phase_result = windows_expert.execute_workflow_phase(first_phase)
        
        # Format the response
        response = f"🔧 **Windows Expert Execution Report**\n\n"
        response += f"**Scenario:** {analysis['scenario']['primary_scenario'].replace('_', ' ').title()}\n"
        response += f"**Phase Executed:** {phase_result['phase_name']}\n"
        response += f"**Success:** {'✅ Yes' if phase_result['success'] else '❌ No'}\n\n"
        
        # Add phase summary
        summary = phase_result['summary']
        response += f"**📊 Execution Summary:**\n"
        response += f"• Commands Executed: {summary['successful']}/{summary['total_commands']}\n"
        response += f"• Success Rate: {summary['success_rate']:.1f}%\n"
        if summary['failed'] > 0:
            response += f"• Failed Commands: {summary['failed']}\n"
        response += "\n"
        
        # Add detailed results for important commands
        important_results = [r for r in phase_result['results'] if r['status'] == 'success'][:3]
        if important_results:
            response += f"**✅ Key Results:**\n"
            for result in important_results:
                response += f"• **{result['command']}:** {result['message']}\n"
                if result.get('output') and len(result['output']) < 200:
                    response += f"  Output: {result['output'][:150]}...\n"
            response += "\n"
        
        # Add next steps
        remaining_phases = len(phases) - 1
        if remaining_phases > 0:
            response += f"**🔄 Next Steps:**\n"
            response += f"• {remaining_phases} more phases remaining\n"
            response += f"• Next phase: {phases[1]['name'] if len(phases) > 1 else 'N/A'}\n"
        
        # Add suggestions
        if analysis['suggestions']:
            response += f"\n**💡 Expert Suggestions:**\n"
            for suggestion in analysis['suggestions'][:2]:
                response += f"• {suggestion}\n"
        
        return {
            'status': 'success',
            'message': response,
            'analysis': analysis,
            'phase_result': phase_result,
            'execution_mode': 'guided_execution'
        }
    
    def _execute_automatic_workflow(self, analysis: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """Execute simple, low-risk workflows automatically"""
        workflow = analysis['workflow']
        phases = workflow.get('phases', [])
        
        if not phases:
            return {
                'status': 'error',
                'message': '❌ No executable workflow phases found.'
            }
        
        # Execute all phases automatically for simple workflows
        all_results = []
        overall_success = True
        
        for phase in phases[:2]:  # Limit to first 2 phases for safety
            phase_result = windows_expert.execute_workflow_phase(phase)
            all_results.append(phase_result)
            
            if not phase_result['success']:
                overall_success = False
                break  # Stop on first failure
        
        # Format comprehensive response
        response = f"⚡ **Automatic Execution Complete**\n\n"
        response += f"**Scenario:** {analysis['scenario']['primary_scenario'].replace('_', ' ').title()}\n"
        response += f"**Overall Result:** {'✅ Success' if overall_success else '❌ Partial Success'}\n\n"
        
        # Summary of all phases
        total_commands = sum(r['summary']['total_commands'] for r in all_results)
        total_successful = sum(r['summary']['successful'] for r in all_results)
        
        response += f"**📊 Execution Summary:**\n"
        response += f"• Phases Executed: {len(all_results)}\n"
        response += f"• Total Commands: {total_commands}\n"
        response += f"• Success Rate: {(total_successful/total_commands*100):.1f}%\n\n"
        
        # Key outputs from successful commands
        key_outputs = []
        for phase_result in all_results:
            for result in phase_result['results']:
                if result['status'] == 'success' and result.get('output'):
                    key_outputs.append({
                        'command': result['command'],
                        'output': result['output'][:300]  # Limit output length
                    })
        
        if key_outputs:
            response += f"**📋 Key Results:**\n"
            for output in key_outputs[:3]:  # Show top 3
                response += f"• **{output['command']}:**\n"
                response += f"  {output['output'][:150]}...\n\n"
        
        # Add follow-up suggestions
        if analysis['expected_outcome']['follow_up_actions']:
            response += f"**🔄 Recommended Follow-up:**\n"
            for action in analysis['expected_outcome']['follow_up_actions'][:2]:
                response += f"• {action}\n"
        
        return {
            'status': 'success',
            'message': response,
            'analysis': analysis,
            'phase_results': all_results,
            'execution_mode': 'automatic_execution',
            'overall_success': overall_success
        }
    
    def _execute_expert_command(self, command_info: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific Windows command with expert guidance"""
        command = command_info['command']
        risk_level = analysis['risk_level']
        requires_admin = analysis['requires_admin']
        
        # Safety checks
        if risk_level == 'high':
            return {
                "status": "warning",
                "message": f"⚠️ HIGH RISK COMMAND: {command}\n\n"
                          f"Description: {command_info['description']}\n"
                          f"This command can cause system damage. Please confirm if you want to proceed.\n\n"
                          f"Recommended steps:\n" + 
                          "\n".join(f"{i+1}. {step}" for i, step in enumerate(analysis['execution_plan']['step_by_step'])),
                "command_info": command_info,
                "requires_confirmation": True
            }
        
        if requires_admin:
            admin_warning = "⚠️ Administrator privileges required for this command.\n\n"
        else:
            admin_warning = ""
        
        # Execute the command
        try:
            if command.startswith('dism') or command.startswith('sfc') or 'systeminfo' in command:
                return self._execute_system_command(command, command_info, admin_warning)
            elif 'ipconfig' in command or 'ping' in command or 'netstat' in command:
                return self._execute_network_command(command, command_info, admin_warning)
            elif 'tasklist' in command or 'taskkill' in command:
                return self._execute_process_command(command, command_info, admin_warning)
            else:
                return self._execute_general_command(command, command_info, admin_warning)
                
        except Exception as e:
            return {"status": "error", "message": f"Command execution failed: {str(e)}"}
    
    def _execute_system_command(self, command: str, command_info: Dict, admin_warning: str) -> Dict[str, Any]:
        """Execute system-level commands"""
        try:
            if command == 'systeminfo':
                result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    # Parse and format system info
                    output = result.stdout
                    formatted_output = self._format_system_info(output)
                    return {
                        "status": "success",
                        "message": f"{admin_warning}🖥️ **System Information**\n\n{formatted_output}",
                        "raw_output": output
                    }
                else:
                    return {"status": "error", "message": f"Command failed: {result.stderr}"}
            
            elif 'sfc' in command:
                return {
                    "status": "info",
                    "message": f"{admin_warning}🔧 **System File Checker**\n\n"
                              f"Command: {command}\n"
                              f"Description: {command_info['description']}\n\n"
                              f"This will scan for and repair corrupted system files.\n"
                              f"Process may take 30+ minutes.\n\n"
                              f"To execute manually:\n"
                              f"1. Open Command Prompt as Administrator\n"
                              f"2. Run: {command}\n"
                              f"3. Wait for completion\n"
                              f"4. Restart if required",
                    "manual_execution": True
                }
            
            elif 'dism' in command:
                return {
                    "status": "info", 
                    "message": f"{admin_warning}🛠️ **DISM Command**\n\n"
                              f"Command: {command}\n"
                              f"Description: {command_info['description']}\n\n"
                              f"This is a powerful system repair tool.\n\n"
                              f"To execute manually:\n"
                              f"1. Open Command Prompt as Administrator\n"
                              f"2. Run: {command}\n"
                              f"3. Monitor progress\n"
                              f"4. Follow any additional instructions",
                    "manual_execution": True
                }
            
            else:
                return self._execute_general_command(command, command_info, admin_warning)
                
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Command execution timed out"}
        except Exception as e:
            return {"status": "error", "message": f"System command failed: {str(e)}"}
    
    def _execute_network_command(self, command: str, command_info: Dict, admin_warning: str) -> Dict[str, Any]:
        """Execute network-related commands"""
        try:
            if command.startswith('ipconfig'):
                full_command = 'ipconfig /all' if '/all' not in command else command
                result = subprocess.run(full_command.split(), capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    formatted_output = self._format_network_info(result.stdout)
                    return {
                        "status": "success",
                        "message": f"🌐 **Network Configuration**\n\n{formatted_output}",
                        "raw_output": result.stdout
                    }
                else:
                    return {"status": "error", "message": f"Network command failed: {result.stderr}"}
            
            elif command.startswith('ping'):
                # Extract target from command or use default
                target = '8.8.8.8'  # Default to Google DNS
                if len(command.split()) > 1:
                    target = command.split()[1]
                
                result = subprocess.run(['ping', '-n', '4', target], capture_output=True, text=True, timeout=20)
                
                if result.returncode == 0:
                    formatted_output = self._format_ping_results(result.stdout, target)
                    return {
                        "status": "success",
                        "message": f"📡 **Ping Test Results**\n\n{formatted_output}",
                        "raw_output": result.stdout
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"❌ **Ping Failed**\n\nTarget: {target}\nError: {result.stderr}\n\nPossible causes:\n• No internet connection\n• Target server is down\n• Firewall blocking requests"
                    }
            
            elif command.startswith('netstat'):
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    formatted_output = self._format_netstat_results(result.stdout)
                    return {
                        "status": "success",
                        "message": f"🔗 **Network Connections**\n\n{formatted_output}",
                        "raw_output": result.stdout
                    }
            
            else:
                return self._execute_general_command(command, command_info, admin_warning)
                
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Network command timed out"}
        except Exception as e:
            return {"status": "error", "message": f"Network command failed: {str(e)}"}
    
    def _execute_process_command(self, command: str, command_info: Dict, admin_warning: str) -> Dict[str, Any]:
        """Execute process management commands"""
        try:
            if command.startswith('tasklist'):
                result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    formatted_output = self._format_process_list(result.stdout)
                    return {
                        "status": "success",
                        "message": f"⚙️ **Running Processes**\n\n{formatted_output}",
                        "raw_output": result.stdout
                    }
                else:
                    return {"status": "error", "message": f"Process list failed: {result.stderr}"}
            
            elif command.startswith('taskkill'):
                return {
                    "status": "warning",
                    "message": f"{admin_warning}⚠️ **Process Termination**\n\n"
                              f"Command: {command}\n"
                              f"Description: {command_info['description']}\n\n"
                              f"This will forcefully terminate processes.\n"
                              f"Use with caution as it may cause data loss.\n\n"
                              f"To execute manually:\n"
                              f"1. Open Command Prompt as Administrator\n"
                              f"2. Identify process ID or name\n"
                              f"3. Run: taskkill /f /pid [PID] or taskkill /f /im [process.exe]\n"
                              f"4. Verify process termination",
                    "requires_confirmation": True
                }
            
            else:
                return self._execute_general_command(command, command_info, admin_warning)
                
        except Exception as e:
            return {"status": "error", "message": f"Process command failed: {str(e)}"}
    
    def _execute_general_command(self, command: str, command_info: Dict, admin_warning: str) -> Dict[str, Any]:
        """Execute general Windows commands"""
        return {
            "status": "info",
            "message": f"{admin_warning}💻 **Windows Command**\n\n"
                      f"Command: {command}\n"
                      f"Description: {command_info['description']}\n"
                      f"Category: {command_info.get('category', 'general')}\n\n"
                      f"To execute:\n"
                      f"1. Open Command Prompt (as Administrator if required)\n"
                      f"2. Type: {command}\n"
                      f"3. Press Enter\n"
                      f"4. Review output and follow any instructions",
            "manual_execution": True
        }
    
    def _execute_scenario(self, scenario: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific Windows scenario"""
        try:
            scenario_handler = windows_expert.scenario_handlers.get(
                scenario.replace(' ', '_').replace('-', '_').lower()
            )
            
            if scenario_handler:
                scenario_info = scenario_handler()
                return {
                    "status": "success",
                    "message": f"📋 **Scenario: {scenario.title()}**\n\n"
                              f"Description: {scenario_info['description']}\n\n"
                              f"**Recommended Commands:**\n" +
                              "\n".join(f"• {cmd}" for cmd in scenario_info['commands']) + "\n\n"
                              f"**Step-by-Step Process:**\n" +
                              "\n".join(f"{i+1}. {step}" for i, step in enumerate(scenario_info['steps'])),
                    "scenario_info": scenario_info
                }
            else:
                return self._handle_general_request(scenario, analysis)
                
        except Exception as e:
            return {"status": "error", "message": f"Scenario execution failed: {str(e)}"}
    
    def _handle_general_request(self, request: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general Windows requests"""
        intent = analysis.get('intent', 'general')
        
        suggestions = {
            'diagnose': "For system diagnostics, try: systeminfo, msinfo32, or dxdiag",
            'optimize': "For optimization, try: cleanmgr, defrag, or sfc /scannow",
            'network': "For network issues, try: ipconfig /all, ping 8.8.8.8, or netsh winsock reset",
            'cleanup': "For cleanup, try: cleanmgr, disk cleanup, or temp file removal",
            'repair': "For repairs, try: sfc /scannow, dism /online /cleanup-image /restorehealth",
            'info': "For system info, try: systeminfo, ver, or winver"
        }
        
        suggestion = suggestions.get(intent, "Try being more specific about what you want to accomplish")
        
        return {
            "status": "info",
            "message": f"🤖 **Windows Assistant**\n\n"
                      f"Intent detected: {intent.title()}\n\n"
                      f"💡 **Suggestion:**\n{suggestion}\n\n"
                      f"**Available categories:**\n"
                      f"• System Information & Diagnostics\n"
                      f"• Network Configuration & Troubleshooting\n"
                      f"• File Management & Organization\n"
                      f"• Process & Service Management\n"
                      f"• Disk Management & Optimization\n"
                      f"• Security & Permissions\n"
                      f"• Windows Features & Updates\n"
                      f"• System Repair & Recovery\n\n"
                      f"Try asking: 'check system info', 'fix network issues', 'clean disk space', etc.",
            "suggestions": list(suggestions.values())
        }
    
    # Formatting helper methods
    def _format_system_info(self, output: str) -> str:
        """Format system information output"""
        lines = output.split('\n')
        important_info = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in [
                'host name', 'os name', 'os version', 'system type', 
                'total physical memory', 'processor', 'bios version'
            ]):
                important_info.append(line.strip())
        
        return '\n'.join(important_info[:10]) + '\n\n(Truncated for readability)'
    
    def _format_network_info(self, output: str) -> str:
        """Format network configuration output"""
        lines = output.split('\n')
        formatted = []
        current_adapter = ""
        
        for line in lines:
            line = line.strip()
            if 'adapter' in line.lower() and ':' in line:
                current_adapter = line
                formatted.append(f"\n**{current_adapter}**")
            elif any(keyword in line.lower() for keyword in [
                'ipv4 address', 'subnet mask', 'default gateway', 'dhcp enabled'
            ]):
                formatted.append(f"  {line}")
        
        return '\n'.join(formatted[:20]) + '\n\n(Showing key network adapters)'
    
    def _format_ping_results(self, output: str, target: str) -> str:
        """Format ping test results"""
        lines = output.split('\n')
        stats = []
        
        for line in lines:
            if 'reply from' in line.lower() or 'request timed out' in line.lower():
                stats.append(line.strip())
            elif 'packets:' in line.lower() or 'minimum' in line.lower():
                stats.append(line.strip())
        
        return f"Target: {target}\n\n" + '\n'.join(stats)
    
    def _format_netstat_results(self, output: str) -> str:
        """Format netstat results"""
        lines = output.split('\n')
        connections = []
        
        for line in lines[4:15]:  # Skip header, show first 10 connections
            if line.strip() and 'TCP' in line or 'UDP' in line:
                connections.append(line.strip())
        
        return '\n'.join(connections) + '\n\n(Showing first 10 connections)'
    
    def _format_process_list(self, output: str) -> str:
        """Format process list"""
        lines = output.split('\n')
        processes = []
        
        for line in lines[3:13]:  # Skip header, show first 10 processes
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    processes.append(f"{parts[0]:<25} {parts[1]:<10}")
        
        return "Process Name             PID\n" + "-" * 40 + "\n" + '\n'.join(processes)

# Global system tools instance
system_tools = SystemTools()
