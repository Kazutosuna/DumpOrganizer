"""
Progress tracking and reporting module.
"""

from typing import Callable, Optional
from datetime import datetime
import time


class ProgressHandler:
    """Manages progress tracking and updates."""
    
    def __init__(self):
        """Initialize progress handler."""
        self. start_time = None
        self. total_items = 0
        self.processed_items = 0
        self.callbacks = []
    
    def add_callback(self, callback:  Callable):
        """Add a progress callback function."""
        self.callbacks.append(callback)
    
    def start(self, total:  int):
        """Start tracking progress."""
        self.start_time = time.time()
        self.total_items = total
        self.processed_items = 0
    
    def update(self, processed: int = 1, message: str = ""):
        """Update progress."""
        self.processed_items += processed
        
        progress_data = {
            'processed': self.processed_items,
            'total': self.total_items,
            'percentage': (self.processed_items / self.total_items * 100) if self.total_items > 0 else 0,
            'elapsed':  self._get_elapsed_time(),
            'eta': self._get_eta(),
            'speed': self._get_speed(),
            'message': message
        }
        
        for callback in self.callbacks:
            try:
                callback(progress_data)
            except Exception as e: 
                print(f"Error in progress callback: {e}")
    
    def _get_elapsed_time(self) -> str:
        """Get elapsed time string."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            return f"{minutes}m {seconds}s"
        return "0m 0s"
    
    def _get_eta(self) -> Optional[str]:
        """Calculate estimated time remaining."""
        if not self.start_time or self.processed_items == 0:
            return None
        
        elapsed = time.time() - self.start_time
        rate = self.processed_items / elapsed
        remaining_items = self.total_items - self.processed_items
        remaining_time = remaining_items / rate if rate > 0 else 0
        
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        return f"{minutes}m {seconds}s"
    
    def _get_speed(self) -> str:
        """Get current processing speed."""
        if not self. start_time or self.processed_items == 0:
            return "0 files/s"
        
        elapsed = time.time() - self.start_time
        speed = self.processed_items / elapsed if elapsed > 0 else 0
        return f"{speed:.1f} files/s"