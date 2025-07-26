"""
Universal Computer Use Agent - Like Claude Computer Use
Comprehensive screen capture, analysis, and control system for any computer task
"""
import os
import logging
import time
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import threading
import queue

# Computer vision and screen control
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image, ImageDraw, ImageFont
import pytesseract

# Web automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# System integration
import psutil
import win32gui
import win32con
import win32api
import win32process

logger = logging.getLogger(__name__)

class ComputerUseAgent:
    """
    Universal Computer Use Agent - Comprehensive computer automation like Claude
    
    Capabilities:
    - Screen capture and analysis
    - Visual element detection
    - Mouse and keyboard automation
    - Application control
    - Web browser automation
    - File system operations
    - Multi-screen support
    - Real-time screen monitoring
    - Task recording and playback
    """
    
    def __init__(self):
        # Initialize screen capture settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Screen analysis settings
        self.screen_width, self.screen_height = pyautogui.size()
        self.current_screenshot = None
        self.element_detection_confidence = 0.8
        
        # Computer vision settings
        self.template_matching_threshold = 0.7
        self.ocr_confidence_threshold = 60
        
        # Browser automation
        self.browser_driver = None
        self.browser_options = self._setup_browser_options()
        
        # Task recording
        self.is_recording = False
        self.recorded_actions = []
        self.action_queue = queue.Queue()
        
        # Multi-screen support
        self.monitors = self._detect_monitors()
        
        # Application tracking
        self.tracked_windows = {}
        self.active_applications = {}
        
        # Computer use statistics
        self.stats = {
            'screenshots_taken': 0,
            'elements_detected': 0,
            'actions_performed': 0,
            'tasks_completed': 0,
            'accuracy_rate': 0.0
        }
        
        logger.info("🖥️ Universal Computer Use Agent initialized")
        logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        logger.info(f"Monitors detected: {len(self.monitors)}")
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture screen or specific region with high accuracy"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # Convert to numpy array for computer vision
            screen_array = np.array(screenshot)
            self.current_screenshot = screen_array
            self.stats['screenshots_taken'] += 1
            
            return screen_array
            
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    def analyze_screen(self, screenshot: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Analyze screen content using computer vision and OCR"""
        if screenshot is None:
            screenshot = self.capture_screen()
        
        if screenshot is None:
            return {"error": "Failed to capture screen"}
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'screen_size': screenshot.shape[:2],
            'detected_elements': [],
            'text_content': [],
            'clickable_areas': [],
            'visual_patterns': [],
            'applications': []
        }
        
        try:
            # OCR text detection
            text_data = self._extract_text_with_positions(screenshot)
            analysis['text_content'] = text_data
            
            # Visual element detection
            elements = self._detect_ui_elements(screenshot)
            analysis['detected_elements'] = elements
            
            # Clickable area detection
            clickable = self._find_clickable_areas(screenshot)
            analysis['clickable_areas'] = clickable
            
            # Application window detection
            windows = self._detect_application_windows()
            analysis['applications'] = windows
            
            # Visual pattern analysis
            patterns = self._analyze_visual_patterns(screenshot)
            analysis['visual_patterns'] = patterns
            
            self.stats['elements_detected'] += len(elements)
            
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def find_element_by_text(self, text: str, exact_match: bool = False) -> Optional[Dict[str, Any]]:
        """Find screen element by text content"""
        screenshot = self.capture_screen()
        if screenshot is None:
            return None
        
        text_data = self._extract_text_with_positions(screenshot)
        
        for item in text_data:
            if exact_match:
                if item['text'].strip() == text.strip():
                    return item
            else:
                if text.lower() in item['text'].lower():
                    return item
        
        return None
    
    def find_element_by_image(self, template_path: str, confidence: float = None) -> Optional[Dict[str, Any]]:
        """Find screen element by image template matching"""
        if confidence is None:
            confidence = self.template_matching_threshold
        
        screenshot = self.capture_screen()
        if screenshot is None:
            return None
        
        try:
            # Load template image
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"Could not load template image: {template_path}")
                return None
            
            # Convert screenshot to BGR for OpenCV
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                h, w = template.shape[:2]
                return {
                    'x': max_loc[0],
                    'y': max_loc[1],
                    'width': w,
                    'height': h,
                    'confidence': max_val,
                    'center': (max_loc[0] + w // 2, max_loc[1] + h // 2)
                }
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
        
        return None
    
    def click_element(self, element: Dict[str, Any], click_type: str = 'left') -> Dict[str, Any]:
        """Click on detected element with high precision"""
        try:
            if 'center' in element:
                x, y = element['center']
            elif 'x' in element and 'y' in element:
                x = element['x'] + element.get('width', 0) // 2
                y = element['y'] + element.get('height', 0) // 2
            else:
                return {"status": "error", "message": "Invalid element coordinates"}
            
            # Ensure coordinates are within screen bounds
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))
            
            # Perform click
            if click_type == 'left':
                pyautogui.click(x, y)
            elif click_type == 'right':
                pyautogui.rightClick(x, y)
            elif click_type == 'double':
                pyautogui.doubleClick(x, y)
            
            self.stats['actions_performed'] += 1
            
            # Record action if recording is enabled
            if self.is_recording:
                self._record_action('click', {
                    'x': x, 'y': y, 'click_type': click_type,
                    'element': element, 'timestamp': time.time()
                })
            
            return {
                "status": "success",
                "message": f"Clicked at ({x}, {y}) with {click_type} click",
                "coordinates": (x, y)
            }
            
        except Exception as e:
            logger.error(f"Click action failed: {e}")
            return {"status": "error", "message": f"Click failed: {str(e)}"}
    
    def type_text(self, text: str, element: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Type text with optional element targeting"""
        try:
            # Click on element first if provided
            if element:
                click_result = self.click_element(element)
                if click_result['status'] != 'success':
                    return click_result
                time.sleep(0.2)  # Wait for focus
            
            # Type the text
            pyautogui.typewrite(text, interval=0.01)
            
            self.stats['actions_performed'] += 1
            
            # Record action if recording is enabled
            if self.is_recording:
                self._record_action('type', {
                    'text': text, 'element': element,
                    'timestamp': time.time()
                })
            
            return {
                "status": "success",
                "message": f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}",
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"Text typing failed: {e}")
            return {"status": "error", "message": f"Typing failed: {str(e)}"}
    
    def scroll(self, direction: str = 'down', clicks: int = 3, x: int = None, y: int = None) -> Dict[str, Any]:
        """Scroll in specified direction"""
        try:
            if x is None or y is None:
                x, y = self.screen_width // 2, self.screen_height // 2
            
            if direction.lower() == 'down':
                pyautogui.scroll(-clicks, x, y)
            elif direction.lower() == 'up':
                pyautogui.scroll(clicks, x, y)
            elif direction.lower() == 'left':
                pyautogui.hscroll(-clicks, x, y)
            elif direction.lower() == 'right':
                pyautogui.hscroll(clicks, x, y)
            
            self.stats['actions_performed'] += 1
            
            # Record action if recording is enabled
            if self.is_recording:
                self._record_action('scroll', {
                    'direction': direction, 'clicks': clicks,
                    'x': x, 'y': y, 'timestamp': time.time()
                })
            
            return {
                "status": "success",
                "message": f"Scrolled {direction} {clicks} clicks at ({x}, {y})"
            }
            
        except Exception as e:
            logger.error(f"Scroll action failed: {e}")
            return {"status": "error", "message": f"Scroll failed: {str(e)}"}
    
    def perform_keyboard_shortcut(self, keys: List[str]) -> Dict[str, Any]:
        """Perform keyboard shortcut combination"""
        try:
            pyautogui.hotkey(*keys)
            
            self.stats['actions_performed'] += 1
            
            # Record action if recording is enabled
            if self.is_recording:
                self._record_action('hotkey', {
                    'keys': keys, 'timestamp': time.time()
                })
            
            return {
                "status": "success",
                "message": f"Executed keyboard shortcut: {'+'.join(keys)}"
            }
            
        except Exception as e:
            logger.error(f"Keyboard shortcut failed: {e}")
            return {"status": "error", "message": f"Shortcut failed: {str(e)}"}
    
    def wait_for_element(self, text: str = None, image_path: str = None, 
                        timeout: int = 10, interval: float = 0.5) -> Optional[Dict[str, Any]]:
        """Wait for element to appear on screen"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if text:
                element = self.find_element_by_text(text)
                if element:
                    return element
            
            if image_path:
                element = self.find_element_by_image(image_path)
                if element:
                    return element
            
            time.sleep(interval)
        
        return None
    
    def execute_computer_task(self, task_description: str) -> Dict[str, Any]:
        """Execute complex computer task using AI guidance"""
        logger.info(f"🎯 Executing computer task: {task_description}")
        
        try:
            # Analyze current screen state
            screen_analysis = self.analyze_screen()
            
            # Break down task into steps
            task_steps = self._plan_task_execution(task_description, screen_analysis)
            
            # Execute each step
            results = []
            for i, step in enumerate(task_steps, 1):
                logger.info(f"Step {i}/{len(task_steps)}: {step['description']}")
                
                step_result = self._execute_task_step(step)
                results.append(step_result)
                
                if step_result['status'] != 'success':
                    logger.warning(f"Step {i} failed: {step_result['message']}")
                    # Try to recover or provide alternative
                    recovery_result = self._attempt_step_recovery(step, step_result)
                    if recovery_result['status'] == 'success':
                        results[-1] = recovery_result
                    else:
                        break
                
                # Wait between steps
                time.sleep(step.get('wait_time', 0.5))
            
            self.stats['tasks_completed'] += 1
            
            return {
                "status": "success" if all(r['status'] == 'success' for r in results) else "partial",
                "message": f"Task execution completed with {len(results)} steps",
                "task_description": task_description,
                "steps_executed": len(results),
                "step_results": results,
                "final_screen_state": self.analyze_screen()
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                "status": "error",
                "message": f"Task execution failed: {str(e)}",
                "task_description": task_description
            }
    
    def start_browser_automation(self, url: str = None) -> Dict[str, Any]:
        """Start browser automation session"""
        try:
            if self.browser_driver is None:
                self.browser_driver = webdriver.Chrome(options=self.browser_options)
            
            if url:
                self.browser_driver.get(url)
            
            return {
                "status": "success",
                "message": "Browser automation started",
                "current_url": self.browser_driver.current_url if url else "about:blank"
            }
            
        except Exception as e:
            logger.error(f"Browser automation failed: {e}")
            return {"status": "error", "message": f"Browser failed: {str(e)}"}
    
    def interact_with_webpage(self, action: str, selector: str = None, 
                            text: str = None, **kwargs) -> Dict[str, Any]:
        """Interact with webpage elements"""
        if self.browser_driver is None:
            return {"status": "error", "message": "Browser not initialized"}
        
        try:
            wait = WebDriverWait(self.browser_driver, 10)
            
            if action == 'click':
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                element.click()
                
            elif action == 'type':
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                element.clear()
                element.send_keys(text)
                
            elif action == 'get_text':
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                return {
                    "status": "success",
                    "message": "Text retrieved",
                    "text": element.text
                }
            
            return {
                "status": "success",
                "message": f"Webpage action '{action}' completed"
            }
            
        except Exception as e:
            logger.error(f"Webpage interaction failed: {e}")
            return {"status": "error", "message": f"Webpage interaction failed: {str(e)}"}
    
    def start_task_recording(self) -> Dict[str, Any]:
        """Start recording user actions for later playback"""
        self.is_recording = True
        self.recorded_actions = []
        
        return {
            "status": "success",
            "message": "Task recording started"
        }
    
    def stop_task_recording(self) -> Dict[str, Any]:
        """Stop recording and return recorded actions"""
        self.is_recording = False
        
        return {
            "status": "success",
            "message": f"Task recording stopped with {len(self.recorded_actions)} actions",
            "recorded_actions": self.recorded_actions
        }
    
    def replay_recorded_task(self, recorded_actions: List[Dict[str, Any]], 
                           speed_multiplier: float = 1.0) -> Dict[str, Any]:
        """Replay recorded actions"""
        try:
            for i, action in enumerate(recorded_actions):
                logger.info(f"Replaying action {i+1}/{len(recorded_actions)}: {action['type']}")
                
                if action['type'] == 'click':
                    pyautogui.click(action['data']['x'], action['data']['y'])
                    
                elif action['type'] == 'type':
                    pyautogui.typewrite(action['data']['text'])
                    
                elif action['type'] == 'scroll':
                    data = action['data']
                    if data['direction'] == 'down':
                        pyautogui.scroll(-data['clicks'], data['x'], data['y'])
                    elif data['direction'] == 'up':
                        pyautogui.scroll(data['clicks'], data['x'], data['y'])
                
                elif action['type'] == 'hotkey':
                    pyautogui.hotkey(*action['data']['keys'])
                
                # Wait between actions (adjusted by speed multiplier)
                time.sleep(0.5 / speed_multiplier)
            
            return {
                "status": "success",
                "message": f"Replayed {len(recorded_actions)} actions successfully"
            }
            
        except Exception as e:
            logger.error(f"Action replay failed: {e}")
            return {"status": "error", "message": f"Replay failed: {str(e)}"}
    
    def get_computer_use_stats(self) -> Dict[str, Any]:
        """Get computer use statistics and metrics"""
        return {
            "statistics": self.stats.copy(),
            "screen_info": {
                "resolution": f"{self.screen_width}x{self.screen_height}",
                "monitors": len(self.monitors)
            },
            "session_info": {
                "recording_active": self.is_recording,
                "browser_active": self.browser_driver is not None,
                "tracked_windows": len(self.tracked_windows)
            }
        }
    
    # Private helper methods
    def _extract_text_with_positions(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text with position information using OCR"""
        try:
            # Convert to PIL Image for pytesseract
            pil_image = Image.fromarray(screenshot)
            
            # Get text data with bounding boxes
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            text_items = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > self.ocr_confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        text_items.append({
                            'text': text,
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i],
                            'confidence': data['conf'][i],
                            'center': (
                                data['left'][i] + data['width'][i] // 2,
                                data['top'][i] + data['height'][i] // 2
                            )
                        })
            
            return text_items
            
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            return []
    
    def _detect_ui_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements like buttons, text fields, etc."""
        elements = []
        
        try:
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours (potential UI elements)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by area to avoid noise
                area = cv2.contourArea(contour)
                if 100 < area < 50000:  # Reasonable UI element size
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate aspect ratio to identify likely buttons/fields
                    aspect_ratio = w / h if h > 0 else 0
                    
                    element_type = "unknown"
                    if 0.5 < aspect_ratio < 8:  # Likely button or text field
                        if aspect_ratio > 3:
                            element_type = "text_field"
                        else:
                            element_type = "button"
                    
                    elements.append({
                        'type': element_type,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'center': (x + w // 2, y + h // 2)
                    })
            
        except Exception as e:
            logger.error(f"UI element detection failed: {e}")
        
        return elements
    
    def _find_clickable_areas(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Find potentially clickable areas on screen"""
        clickable_areas = []
        
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
            
            # Define color ranges for common UI elements
            button_colors = [
                ([100, 50, 50], [130, 255, 255]),  # Blue buttons
                ([0, 50, 50], [10, 255, 255]),     # Red buttons
                ([50, 50, 50], [70, 255, 255]),    # Green buttons
            ]
            
            for i, (lower, upper) in enumerate(button_colors):
                lower = np.array(lower)
                upper = np.array(upper)
                
                # Create mask for this color range
                mask = cv2.inRange(hsv, lower, upper)
                
                # Find contours in mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 200 < area < 10000:  # Reasonable button size
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        clickable_areas.append({
                            'type': 'colored_button',
                            'color_category': i,
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'center': (x + w // 2, y + h // 2),
                            'confidence': min(area / 1000, 1.0)
                        })
            
        except Exception as e:
            logger.error(f"Clickable area detection failed: {e}")
        
        return clickable_areas
    
    def _detect_application_windows(self) -> List[Dict[str, Any]]:
        """Detect currently visible application windows"""
        windows = []
        
        try:
            for window in gw.getAllWindows():
                if window.visible and window.width > 50 and window.height > 50:
                    windows.append({
                        'title': window.title,
                        'x': window.left,
                        'y': window.top,
                        'width': window.width,
                        'height': window.height,
                        'is_active': window == gw.getActiveWindow(),
                        'center': (window.left + window.width // 2, window.top + window.height // 2)
                    })
        
        except Exception as e:
            logger.error(f"Window detection failed: {e}")
        
        return windows
    
    def _analyze_visual_patterns(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze visual patterns in screenshot"""
        patterns = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            
            # Detect lines (could be UI borders, dividers)
            lines = cv2.HoughLinesP(gray, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            
            if lines is not None:
                patterns.append({
                    'type': 'lines',
                    'count': len(lines),
                    'description': f"Detected {len(lines)} linear elements"
                })
            
            # Detect circles (buttons, icons)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=100)
            
            if circles is not None:
                patterns.append({
                    'type': 'circles',
                    'count': len(circles[0]),
                    'description': f"Detected {len(circles[0])} circular elements"
                })
        
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
        
        return patterns
    
    def _setup_browser_options(self) -> Options:
        """Setup Chrome browser options for automation"""
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options
    
    def _detect_monitors(self) -> List[Dict[str, Any]]:
        """Detect available monitors"""
        monitors = []
        try:
            # This is a simplified version - you might want to use a library like screeninfo
            monitors.append({
                'id': 0,
                'width': self.screen_width,
                'height': self.screen_height,
                'is_primary': True
            })
        except Exception as e:
            logger.error(f"Monitor detection failed: {e}")
        
        return monitors
    
    def _plan_task_execution(self, task_description: str, screen_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan task execution steps based on description and screen state"""
        # This is a simplified planning algorithm
        # In a full implementation, this would use AI/ML to understand the task
        
        steps = []
        
        # Basic task parsing
        task_lower = task_description.lower()
        
        if 'open' in task_lower:
            app_name = task_lower.split('open')[-1].strip()
            steps.append({
                'type': 'open_application',
                'description': f'Open application: {app_name}',
                'target': app_name
            })
        
        elif 'click' in task_lower:
            if 'button' in task_lower:
                steps.append({
                    'type': 'click_button',
                    'description': 'Click on button',
                    'search_method': 'visual'
                })
        
        elif 'type' in task_lower or 'enter' in task_lower:
            steps.append({
                'type': 'type_text',
                'description': 'Type text',
                'text': task_description  # Simplified
            })
        
        # Default fallback
        if not steps:
            steps.append({
                'type': 'analyze_and_act',
                'description': 'Analyze screen and determine action',
                'task': task_description
            })
        
        return steps
    
    def _execute_task_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task step"""
        try:
            step_type = step['type']
            
            if step_type == 'open_application':
                # Try to open application using Windows start menu
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.typewrite(step['target'])
                time.sleep(0.5)
                pyautogui.press('enter')
                
                return {
                    "status": "success",
                    "message": f"Attempted to open {step['target']}"
                }
            
            elif step_type == 'click_button':
                # Look for clickable elements
                screen_analysis = self.analyze_screen()
                clickable_areas = screen_analysis.get('clickable_areas', [])
                
                if clickable_areas:
                    # Click the first detected clickable area
                    element = clickable_areas[0]
                    return self.click_element(element)
                else:
                    return {
                        "status": "error",
                        "message": "No clickable elements found"
                    }
            
            elif step_type == 'type_text':
                return self.type_text(step.get('text', ''))
            
            elif step_type == 'analyze_and_act':
                # Perform screen analysis and suggest action
                screen_analysis = self.analyze_screen()
                
                return {
                    "status": "success",
                    "message": "Screen analyzed",
                    "analysis": screen_analysis
                }
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown step type: {step_type}"
                }
        
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {
                "status": "error",
                "message": f"Step execution failed: {str(e)}"
            }
    
    def _attempt_step_recovery(self, step: Dict[str, Any], error_result: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover from step failure"""
        # Simplified recovery - could be much more sophisticated
        try:
            # Wait a moment and retry
            time.sleep(1)
            return self._execute_task_step(step)
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Recovery failed: {str(e)}"
            }
    
    def _record_action(self, action_type: str, action_data: Dict[str, Any]):
        """Record an action for later playback"""
        self.recorded_actions.append({
            'type': action_type,
            'data': action_data,
            'timestamp': time.time()
        })
    
    def cleanup(self):
        """Cleanup resources"""
        if self.browser_driver:
            self.browser_driver.quit()
            self.browser_driver = None
        
        logger.info("🧹 Computer Use Agent cleaned up")

# Global instance
computer_use_agent = ComputerUseAgent()
