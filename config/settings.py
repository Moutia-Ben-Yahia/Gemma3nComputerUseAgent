"""
Configuration settings for the Gemma3n Assistant
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import validator, Field

class Config(BaseSettings):
    """Application configuration with validation"""
    
    # Ollama settings
    OLLAMA_HOST: str = Field(default="http://localhost:11434", description="Ollama server URL")
    OLLAMA_MODEL: str = Field(default="qwen2.5-coder:latest", description="AI model to use")
    OLLAMA_TIMEOUT: int = Field(default=30, ge=5, le=300, description="Request timeout in seconds")
    
    # Voice settings
    VOICE_ENABLED: bool = True
    VOICE_RATE: int = 200
    VOICE_VOLUME: float = 0.9
    
    # Agent settings
    AGENT_NAME: str = "Gemma Assistant"
    MAX_ITERATIONS: int = 5
    THINKING_TIMEOUT: int = 30
    
    # Storage settings
    DATA_DIR: Path = Path(__file__).parent.parent / "data"
    MEMORY_DB: str = "memory.json"
    TASKS_DB: str = "tasks.json"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path(__file__).parent.parent / "logs"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global config instance
config = Config()

# Ensure directories exist
config.DATA_DIR.mkdir(exist_ok=True)
config.LOG_DIR.mkdir(exist_ok=True)
