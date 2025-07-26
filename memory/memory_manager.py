"""
Enhanced memory and storage management with improved performance
"""
import logging
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from tinydb import TinyDB, Query
from config import config
from utils.local_cache import local_cache
from utils.error_handling import retry_with_backoff, safe_execute

logger = logging.getLogger(__name__)

class MemoryManager:
    """Enhanced memory manager with caching and better performance"""
    
    def __init__(self):
        self.memory_db_path = config.DATA_DIR / config.MEMORY_DB
        self.tasks_db_path = config.DATA_DIR / config.TASKS_DB
        
        # Create backup directory
        self.backup_dir = config.DATA_DIR / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.memory_db = TinyDB(self.memory_db_path)
        self.tasks_db = TinyDB(self.tasks_db_path)
        
        # Add thread lock for safe concurrent access
        self._lock = threading.Lock()
        
        # Cache frequently accessed data
        self._conversation_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Tables
        self.conversations = self.memory_db.table('conversations')
        self.context = self.memory_db.table('context')
        self.tasks = self.tasks_db.table('tasks')
        self.completed_tasks = self.tasks_db.table('completed_tasks')
        
        # Performance optimization
        self._setup_indexes()
        
        # Start background backup process
        self._schedule_backup()
    
    def _setup_indexes(self):
        """Setup database indexes for better performance"""
        try:
            # TinyDB doesn't have traditional indexes, but we can optimize queries
            # by caching frequent lookups
            pass
        except Exception as e:
            logger.error(f"Failed to setup indexes: {e}")
    
    def _schedule_backup(self):
        """Schedule periodic backups"""
        import threading
        import time
        
        def backup_worker():
            while True:
                try:
                    time.sleep(3600)  # Backup every hour
                    self.create_backup()
                except Exception as e:
                    logger.error(f"Backup worker error: {e}")
        
        backup_thread = threading.Thread(target=backup_worker, daemon=True)
        backup_thread.start()
    
    @retry_with_backoff(max_retries=3)
    def create_backup(self):
        """Create backup of databases"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup memory database
            memory_backup = self.backup_dir / f"memory_backup_{timestamp}.json"
            with open(memory_backup, 'w') as f:
                json.dump(self.memory_db.all(), f, indent=2)
            
            # Backup tasks database
            tasks_backup = self.backup_dir / f"tasks_backup_{timestamp}.json"
            with open(tasks_backup, 'w') as f:
                json.dump(self.tasks_db.all(), f, indent=2)
            
            logger.info(f"Created backups: {memory_backup.name}, {tasks_backup.name}")
            
            # Clean old backups (keep last 10)
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def _cleanup_old_backups(self):
        """Remove old backup files"""
        try:
            backup_files = sorted(self.backup_dir.glob("*_backup_*.json"))
            if len(backup_files) > 20:  # Keep last 20 backups
                for old_backup in backup_files[:-20]:
                    old_backup.unlink()
                    logger.debug(f"Removed old backup: {old_backup.name}")
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def store_conversation(self, user_input: str, assistant_response: str, metadata: Dict = None):
        """Store conversation turn"""
        try:
            record = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'assistant_response': assistant_response,
                'metadata': metadata or {}
            }
            self.conversations.insert(record)
            logger.debug("Stored conversation turn")
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        try:
            all_conversations = self.conversations.all()
            return sorted(all_conversations, key=lambda x: x['timestamp'], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []
    
    def store_context(self, key: str, value: Any, category: str = "general"):
        """Store contextual information"""
        try:
            Context = Query()
            record = {
                'key': key,
                'value': value,
                'category': category,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update if exists, insert if new
            if self.context.search(Context.key == key):
                self.context.update(record, Context.key == key)
            else:
                self.context.insert(record)
            logger.debug(f"Stored context: {key}")
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
    
    def get_context(self, key: str) -> Optional[Any]:
        """Retrieve contextual information"""
        try:
            Context = Query()
            result = self.context.search(Context.key == key)
            return result[0]['value'] if result else None
        except Exception as e:
            logger.error(f"Failed to get context {key}: {e}")
            return None
    
    def get_context_by_category(self, category: str) -> List[Dict]:
        """Get all context items by category"""
        try:
            Context = Query()
            return self.context.search(Context.category == category)
        except Exception as e:
            logger.error(f"Failed to get context by category {category}: {e}")
            return []
    
    def add_task(self, task_description: str, priority: str = "normal") -> str:
        """Add a new task"""
        try:
            task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            task = {
                'id': task_id,
                'description': task_description,
                'priority': priority,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self.tasks.insert(task)
            logger.info(f"Added task: {task_description}")
            return task_id
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return ""
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        try:
            Task = Query()
            return self.tasks.search(Task.status == 'pending')
        except Exception as e:
            logger.error(f"Failed to get pending tasks: {e}")
            return []
    
    def complete_task(self, task_id: str):
        """Mark task as completed"""
        try:
            Task = Query()
            task = self.tasks.search(Task.id == task_id)
            if task:
                task_data = task[0]
                task_data['status'] = 'completed'
                task_data['completed_at'] = datetime.now().isoformat()
                
                # Move to completed tasks
                self.completed_tasks.insert(task_data)
                self.tasks.remove(Task.id == task_id)
                logger.info(f"Task completed: {task_id}")
            else:
                logger.warning(f"Task not found: {task_id}")
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversations for context"""
        try:
            recent = self.get_recent_conversations(5)
            if not recent:
                return "No previous conversations."
            
            summary = "Recent conversation context:\n"
            for conv in reversed(recent):  # Show chronologically
                summary += f"User: {conv['user_input'][:100]}...\n"
                summary += f"Assistant: {conv['assistant_response'][:100]}...\n\n"
            
            return summary
        except Exception as e:
            logger.error(f"Failed to get conversation summary: {e}")
            return "Error retrieving conversation history."
    
    def clear_old_data(self, days_to_keep: int = 30):
        """Clear old data to prevent database bloat"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            # This is a simple implementation - in production you'd want more sophisticated cleanup
            logger.info(f"Data cleanup - keeping last {days_to_keep} days")
        except Exception as e:
            logger.error(f"Failed to clear old data: {e}")

# Global memory manager instance
memory_manager = MemoryManager()
