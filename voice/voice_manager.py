"""
Enhanced voice manager with full optimization and multi-tasking capabilities
"""
print("Loading voice_manager module...")
import logging
import time
import threading
import queue
from typing import Optional, Callable, Dict, Any
from concurrent.futures import ThreadPoolExecutor, Future

# Try to import config, fallback to defaults if not available
try:
    from config import config
    print("Config imported successfully")
except ImportError:
    print("Config import failed, using fallback")
    # Fallback configuration
    class FallbackConfig:
        VOICE_ENABLED = True
        VOICE_RATE = 200
        VOICE_VOLUME = 0.9
    config = FallbackConfig()

logger = logging.getLogger(__name__)
print("Logger created")

# Try to import voice libraries (they're optional)
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("Voice libraries not available. Install with: pip install SpeechRecognition pyttsx3 pyaudio")

class VoiceManager:
    """Enhanced voice manager with multi-tasking and optimization"""
    
    def __init__(self):
        self.enabled = config.VOICE_ENABLED and VOICE_AVAILABLE
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        # Multi-tasking components
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="VoiceWorker")
        self.speech_queue = queue.Queue()
        self.is_speaking = threading.Event()
        self.callbacks = {
            'on_speech_start': [],
            'on_speech_end': [],
            'on_listen_start': [],
            'on_listen_end': [],
            'on_recognition_result': [],
            'on_error': []
        }
        
        # Performance tracking
        self.stats = {
            'recognition_attempts': 0,
            'recognition_successes': 0,
            'speech_outputs': 0,
            'errors': 0,
            'avg_response_time': 0.0
        }
        
        # Initialize if available
        if self.enabled:
            self._initialize_async()
    
    def _initialize_async(self):
        """Initialize voice components asynchronously"""
        def init_worker():
            try:
                if VOICE_AVAILABLE:
                    # Initialize recognition
                    self.recognizer = sr.Recognizer()
                    self.recognizer.energy_threshold = 4000
                    self.recognizer.dynamic_energy_threshold = True
                    self.recognizer.pause_threshold = 0.8
                    
                    # Initialize microphone
                    try:
                        self.microphone = sr.Microphone()
                        with self.microphone as source:
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    except Exception as e:
                        logger.warning(f"Microphone initialization failed: {e}")
                    
                    # Initialize TTS
                    self.tts_engine = pyttsx3.init()
                    if self.tts_engine:
                        voices = self.tts_engine.getProperty('voices')
                        if voices:
                            # Prefer female voice if available
                            for voice in voices:
                                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                                    self.tts_engine.setProperty('voice', voice.id)
                                    break
                        
                        self.tts_engine.setProperty('rate', config.VOICE_RATE)
                        self.tts_engine.setProperty('volume', config.VOICE_VOLUME)
                    
                    logger.info("Voice system initialized successfully")
                
            except Exception as e:
                logger.error(f"Voice initialization error: {e}")
                self.enabled = False
        
        # Initialize in background
        self.executor.submit(init_worker)
    
    def add_callback(self, event: str, callback: Callable):
        """Add callback for voice events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, *args, **kwargs):
        """Trigger callbacks for an event"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")
    
    def speak_async(self, text: str, priority: int = 1) -> Future:
        """Speak text asynchronously with priority"""
        if not self.enabled or not text.strip():
            # Return completed future for non-enabled state
            return self.executor.submit(lambda: False)
        
        return self.executor.submit(self._speak_worker, text, priority)
    
    def _speak_worker(self, text: str, priority: int) -> bool:
        """Worker function for speaking"""
        start_time = time.time()
        
        try:
            self.is_speaking.set()
            self._trigger_callbacks('on_speech_start', text)
            
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
                self.stats['speech_outputs'] += 1
                duration = time.time() - start_time
                self._update_avg_response_time(duration)
                
                self._trigger_callbacks('on_speech_end', text, duration)
                return True
            else:
                # Fallback to print
                print(f"🔊 {text}")
                return True
                
        except Exception as e:
            logger.error(f"Speech error: {e}")
            self.stats['errors'] += 1
            self._trigger_callbacks('on_error', 'speech', e)
            return False
        finally:
            self.is_speaking.clear()
    
    def listen_async(self, timeout: int = 5, phrase_time_limit: int = 10) -> Future:
        """Listen for speech asynchronously"""
        if not self.enabled or not self.microphone:
            # Return completed future for non-enabled state
            return self.executor.submit(lambda: None)
        
        return self.executor.submit(self._listen_worker, timeout, phrase_time_limit)
    
    def _listen_worker(self, timeout: int, phrase_time_limit: int) -> Optional[str]:
        """Worker function for listening"""
        start_time = time.time()
        self.stats['recognition_attempts'] += 1
        
        try:
            self._trigger_callbacks('on_listen_start')
            
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            self.stats['recognition_successes'] += 1
            duration = time.time() - start_time
            self._update_avg_response_time(duration)
            
            self._trigger_callbacks('on_recognition_result', text, duration)
            self._trigger_callbacks('on_listen_end', text, True)
            
            return text
            
        except sr.WaitTimeoutError:
            self._trigger_callbacks('on_listen_end', None, False)
            return None
        except sr.UnknownValueError:
            self._trigger_callbacks('on_listen_end', None, False)
            return None
        except sr.RequestError as e:
            logger.error(f"Recognition error: {e}")
            self.stats['errors'] += 1
            self._trigger_callbacks('on_error', 'recognition', e)
            self._trigger_callbacks('on_listen_end', None, False)
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            self.stats['errors'] += 1
            self._trigger_callbacks('on_error', 'listen', e)
            self._trigger_callbacks('on_listen_end', None, False)
            return None
    
    def _update_avg_response_time(self, duration: float):
        """Update average response time"""
        total_operations = self.stats['recognition_successes'] + self.stats['speech_outputs']
        if total_operations > 0:
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (total_operations - 1) + duration) / total_operations
            )
    
    def speak(self, text: str) -> bool:
        """Synchronous speak method for compatibility"""
        if not self.enabled:
            print(f"🔊 {text}")
            return True
        
        future = self.speak_async(text)
        return future.result(timeout=30)
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Synchronous listen method for compatibility"""
        if not self.enabled:
            return None
        
        future = self.listen_async(timeout, phrase_time_limit)
        return future.result(timeout=timeout + 10)
    
    def is_available(self) -> bool:
        """Check if voice functionality is available"""
        return self.enabled and VOICE_AVAILABLE
    
    def is_busy(self) -> bool:
        """Check if voice system is currently busy"""
        return self.is_speaking.is_set()
    
    def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for all voice operations to complete"""
        try:
            self.executor.shutdown(wait=True, timeout=timeout)
        except Exception as e:
            logger.error(f"Error waiting for voice completion: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive voice system statistics"""
        total_attempts = self.stats['recognition_attempts']
        success_rate = 0
        if total_attempts > 0:
            success_rate = (self.stats['recognition_successes'] / total_attempts) * 100
        
        return {
            **self.stats,
            'success_rate': round(success_rate, 2),
            'enabled': self.enabled,
            'available': VOICE_AVAILABLE,
            'is_busy': self.is_busy(),
            'thread_pool_active': len(self.executor._threads) if hasattr(self.executor, '_threads') else 0
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.stats = {
            'recognition_attempts': 0,
            'recognition_successes': 0,
            'speech_outputs': 0,
            'errors': 0,
            'avg_response_time': 0.0
        }
    
    def shutdown(self):
        """Shutdown voice system gracefully"""
        logger.info("Shutting down voice system...")
        
        # Stop TTS if speaking
        if self.tts_engine and self.is_speaking.is_set():
            try:
                self.tts_engine.stop()
            except:
                pass
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True, timeout=5)
        
        logger.info("Voice system shutdown complete")

# Global voice manager instance
print("Creating voice_manager instance...")
voice_manager = VoiceManager()
print(f"voice_manager created: {type(voice_manager)}")