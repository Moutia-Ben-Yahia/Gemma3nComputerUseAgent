"""
Local caching system for offline AI assistant
Improves performance by caching AI responses, file operations, and user patterns
"""
import json
import hashlib
import time
import logging
import pickle
from typing import Any, Dict, Optional, List, Union
from pathlib import Path
from datetime import datetime, timedelta
from config import config

logger = logging.getLogger(__name__)

class LocalCache:
    """
    Local file-based caching system for offline operations
    """
    
    def __init__(self, cache_dir: Path = None, max_size_mb: int = 100):
        self.cache_dir = cache_dir or (config.DATA_DIR / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        
        self._load_metadata()
        self._cleanup_expired()
    
    def _load_metadata(self):
        """Load cache metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {"entries": {}, "created": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Failed to load cache metadata: {e}")
            self.metadata = {"entries": {}, "created": datetime.now().isoformat()}
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate cache key"""
        combined = f"{namespace}:{key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def set(self, namespace: str, key: str, value: Any, ttl_seconds: int = 3600):
        """
        Store value in cache
        
        Args:
            namespace: Category of cache (e.g., 'ai_responses', 'file_content')
            key: Unique identifier
            value: Data to cache
            ttl_seconds: Time to live in seconds
        """
        try:
            cache_key = self._generate_key(namespace, key)
            cache_file = self._get_cache_file(cache_key)
            
            # Serialize data
            if isinstance(value, (dict, list)):
                data = json.dumps(value)
                serialization = "json"
            else:
                data = pickle.dumps(value)
                serialization = "pickle"
            
            # Write to file
            with open(cache_file, 'wb' if serialization == "pickle" else 'w') as f:
                if serialization == "pickle":
                    f.write(data)
                else:
                    f.write(data)
            
            # Update metadata
            expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
            self.metadata["entries"][cache_key] = {
                "namespace": namespace,
                "key": key,
                "created": datetime.now().isoformat(),
                "expires": expires_at,
                "serialization": serialization,
                "size": cache_file.stat().st_size if cache_file.exists() else 0
            }
            
            self._save_metadata()
            self._enforce_size_limit()
            
            logger.debug(f"Cached {namespace}:{key} with TTL {ttl_seconds}s")
            
        except Exception as e:
            logger.error(f"Failed to cache {namespace}:{key}: {e}")
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            namespace: Category of cache
            key: Unique identifier
            
        Returns:
            Cached value or None if not found/expired
        """
        try:
            cache_key = self._generate_key(namespace, key)
            
            if cache_key not in self.metadata["entries"]:
                return None
            
            entry = self.metadata["entries"][cache_key]
            
            # Check expiration
            expires_at = datetime.fromisoformat(entry["expires"])
            if datetime.now() > expires_at:
                self._remove_entry(cache_key)
                return None
            
            cache_file = self._get_cache_file(cache_key)
            if not cache_file.exists():
                self._remove_entry(cache_key)
                return None
            
            # Load data
            serialization = entry.get("serialization", "json")
            
            with open(cache_file, 'rb' if serialization == "pickle" else 'r') as f:
                if serialization == "pickle":
                    data = pickle.load(f)
                else:
                    data = json.load(f)
            
            logger.debug(f"Cache hit for {namespace}:{key}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve cache {namespace}:{key}: {e}")
            return None
    
    def _remove_entry(self, cache_key: str):
        """Remove cache entry"""
        try:
            cache_file = self._get_cache_file(cache_key)
            if cache_file.exists():
                cache_file.unlink()
            
            if cache_key in self.metadata["entries"]:
                del self.metadata["entries"][cache_key]
                self._save_metadata()
        except Exception as e:
            logger.error(f"Failed to remove cache entry {cache_key}: {e}")
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for cache_key, entry in self.metadata["entries"].items():
            try:
                expires_at = datetime.fromisoformat(entry["expires"])
                if now > expires_at:
                    expired_keys.append(cache_key)
            except Exception:
                expired_keys.append(cache_key)  # Invalid entry
        
        for cache_key in expired_keys:
            self._remove_entry(cache_key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _enforce_size_limit(self):
        """Enforce cache size limit by removing oldest entries"""
        total_size = sum(entry.get("size", 0) for entry in self.metadata["entries"].values())
        
        if total_size <= self.max_size_bytes:
            return
        
        # Sort by creation time (oldest first)
        sorted_entries = sorted(
            self.metadata["entries"].items(),
            key=lambda x: x[1]["created"]
        )
        
        removed_count = 0
        for cache_key, entry in sorted_entries:
            self._remove_entry(cache_key)
            removed_count += 1
            
            # Recalculate total size
            total_size = sum(e.get("size", 0) for e in self.metadata["entries"].values())
            if total_size <= self.max_size_bytes * 0.8:  # Keep some headroom
                break
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} cache entries to enforce size limit")
    
    def clear_namespace(self, namespace: str):
        """Clear all entries in a namespace"""
        keys_to_remove = [
            cache_key for cache_key, entry in self.metadata["entries"].items()
            if entry["namespace"] == namespace
        ]
        
        for cache_key in keys_to_remove:
            self._remove_entry(cache_key)
        
        logger.info(f"Cleared {len(keys_to_remove)} entries from namespace '{namespace}'")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.metadata["entries"])
        total_size = sum(entry.get("size", 0) for entry in self.metadata["entries"].values())
        
        namespaces = {}
        for entry in self.metadata["entries"].values():
            namespace = entry["namespace"]
            if namespace not in namespaces:
                namespaces[namespace] = {"count": 0, "size": 0}
            namespaces[namespace]["count"] += 1
            namespaces[namespace]["size"] += entry.get("size", 0)
        
        return {
            "total_entries": total_entries,
            "total_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "namespaces": namespaces
        }

class AIResponseCache:
    """Specialized cache for AI responses"""
    
    def __init__(self, cache: LocalCache):
        self.cache = cache
        self.namespace = "ai_responses"
    
    def cache_response(self, prompt: str, system_prompt: str, response: str, ttl_hours: int = 24):
        """Cache AI response"""
        # Create a hash of the prompt combination
        prompt_hash = hashlib.md5(f"{system_prompt}|{prompt}".encode()).hexdigest()
        
        self.cache.set(
            self.namespace,
            prompt_hash,
            {
                "prompt": prompt,
                "system_prompt": system_prompt,
                "response": response,
                "timestamp": datetime.now().isoformat()
            },
            ttl_seconds=ttl_hours * 3600
        )
    
    def get_cached_response(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Get cached AI response"""
        prompt_hash = hashlib.md5(f"{system_prompt}|{prompt}".encode()).hexdigest()
        cached_data = self.cache.get(self.namespace, prompt_hash)
        
        if cached_data:
            return cached_data.get("response")
        return None

class FileContentCache:
    """Specialized cache for file content"""
    
    def __init__(self, cache: LocalCache):
        self.cache = cache
        self.namespace = "file_content"
    
    def cache_file_content(self, file_path: str, content: str, ttl_minutes: int = 30):
        """Cache file content with modification time"""
        try:
            file_stat = Path(file_path).stat()
            cache_data = {
                "content": content,
                "mtime": file_stat.st_mtime,
                "cached_at": datetime.now().isoformat()
            }
            
            self.cache.set(
                self.namespace,
                file_path,
                cache_data,
                ttl_seconds=ttl_minutes * 60
            )
        except Exception as e:
            logger.error(f"Failed to cache file content for {file_path}: {e}")
    
    def get_cached_content(self, file_path: str) -> Optional[str]:
        """Get cached file content if file hasn't been modified"""
        try:
            cached_data = self.cache.get(self.namespace, file_path)
            if not cached_data:
                return None
            
            # Check if file has been modified
            file_stat = Path(file_path).stat()
            if file_stat.st_mtime != cached_data["mtime"]:
                return None  # File was modified
            
            return cached_data["content"]
        except Exception as e:
            logger.error(f"Failed to retrieve cached content for {file_path}: {e}")
            return None

# Global cache instances
local_cache = LocalCache()
ai_cache = AIResponseCache(local_cache)
file_cache = FileContentCache(local_cache)
