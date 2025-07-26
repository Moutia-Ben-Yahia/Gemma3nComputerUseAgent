"""
Voice manager for Gemma3n Assistant
"""
import logging

logger = logging.getLogger(__name__)

class VoiceManager:
    """Voice manager with basic functionality"""
    
    def __init__(self):
        self.enabled = False
        logger.info("VoiceManager initialized")
    
    def is_available(self):
        return False
    
    def speak(self, text):
        print(f"🔊 {text}")
        return True
    
    def listen(self):
        return None
    
    def get_stats(self):
        return {
            'enabled': self.enabled,
            'available': False,
            'success_rate': 0,
            'avg_response_time': 0
        }
    
    def reset_stats(self):
        pass

# Global instance
voice_manager = VoiceManager()
