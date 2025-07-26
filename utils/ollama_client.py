"""
Ollama client for local AI model interaction
"""
import requests
import json
import logging
from typing import Optional, Dict, Any, Generator
from config import config

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama locally"""
    
    def __init__(self, host: str = None, model: str = None):
        self.host = host or config.OLLAMA_HOST
        self.model = model or config.OLLAMA_MODEL
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False
    
    def list_models(self) -> list:
        """List available models"""
        try:
            response = self.session.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        return []
    
    def generate(self, prompt: str, system_prompt: str = None, stream: bool = False) -> str:
        """Generate response from the model"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = self.session.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=config.THINKING_TIMEOUT
            )
            
            if response.status_code == 200:
                if stream:
                    return self._handle_stream_response(response)
                else:
                    return response.json().get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return ""
    
    def _handle_stream_response(self, response) -> Generator[str, None, None]:
        """Handle streaming response"""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
                except json.JSONDecodeError:
                    continue
    
    def chat(self, messages: list, stream: bool = False) -> str:
        """Chat with the model using conversation format"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        try:
            response = self.session.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=config.THINKING_TIMEOUT
            )
            
            if response.status_code == 200:
                if stream:
                    return self._handle_stream_response(response)
                else:
                    return response.json().get('message', {}).get('content', '')
            else:
                logger.error(f"Ollama chat API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to chat: {e}")
            return ""

# Global Ollama client instance
ollama_client = OllamaClient()
