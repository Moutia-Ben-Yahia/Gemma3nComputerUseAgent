"""
Robust error handling and recovery system for offline operations
"""
import logging
import traceback
import time
from functools import wraps
from typing import Any, Callable, Optional, Dict, List, Type
from pathlib import Path
import json
from datetime import datetime
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker pattern for failing operations"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                
                raise e

class ErrorRecoveryManager:
    """Enhanced error recovery and fallback strategies"""
    
    def __init__(self):
        self.error_history = []
        self.recovery_strategies = {}
        self.max_error_history = 100
        self.circuit_breakers = {}
        self.error_patterns = defaultdict(int)
        self.lock = threading.Lock()
        
    def register_recovery_strategy(self, error_type: Type[Exception], strategy: Callable):
        """Register a recovery strategy for specific error types"""
        self.recovery_strategies[error_type] = strategy
        logger.info(f"Registered recovery strategy for {error_type.__name__}")
        
    def register_circuit_breaker(self, operation_name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        """Register circuit breaker for an operation"""
        self.circuit_breakers[operation_name] = CircuitBreaker(failure_threshold, recovery_timeout)
        
    def handle_error(self, operation_name: str, error: Exception, context: Dict[str, Any] = None) -> Optional[Any]:
        """Handle error with appropriate recovery strategy"""
        with self.lock:
            error_info = {
                'operation': operation_name,
                'type': type(error).__name__,
                'message': str(error),
                'timestamp': datetime.now().isoformat(),
                'context': context or {},
                'traceback': traceback.format_exc()
            }
            
            self.error_history.append(error_info)
            if len(self.error_history) > self.max_error_history:
                self.error_history.pop(0)
            
            # Track error patterns
            error_key = f"{operation_name}:{type(error).__name__}"
            self.error_patterns[error_key] += 1
            
            logger.error(f"Error in {operation_name}: {error}")
            
            # Try recovery strategy
            for error_type, strategy in self.recovery_strategies.items():
                if isinstance(error, error_type):
                    try:
                        logger.info(f"Attempting recovery for {type(error).__name__}")
                        return strategy(error, context)
                    except Exception as recovery_error:
                        logger.error(f"Recovery strategy failed: {recovery_error}")
                        
            return None
        
    def get_error_patterns(self) -> Dict[str, int]:
        """Analyze error patterns for debugging"""
        patterns = {}
        for error in self.error_history:
            error_type = error['type']
            patterns[error_type] = patterns.get(error_type, 0) + 1
        return patterns

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0, 
                      exceptions: tuple = (Exception,)):
    """Decorator for retrying functions with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                        
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    
            raise last_exception
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_return=None, **kwargs) -> Any:
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Safe execution failed for {func.__name__}: {e}")
        return default_return

class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
                
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
            
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = 'CLOSED'
        
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

# Global error recovery manager
error_recovery = ErrorRecoveryManager()

# Register common recovery strategies
def file_not_found_recovery(error: FileNotFoundError, context: Dict) -> Optional[Any]:
    """Recovery strategy for file not found errors"""
    file_path = context.get('file_path')
    if file_path:
        # Try to create the file
        try:
            Path(file_path).touch()
            logger.info(f"Created missing file: {file_path}")
            return True
        except Exception:
            pass
    return None

def permission_error_recovery(error: PermissionError, context: Dict) -> Optional[Any]:
    """Recovery strategy for permission errors"""
    logger.warning("Permission denied - trying alternative approach")
    return None

error_recovery.register_recovery_strategy(FileNotFoundError, file_not_found_recovery)
error_recovery.register_recovery_strategy(PermissionError, permission_error_recovery)
