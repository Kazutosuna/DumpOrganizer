"""
Core file processing and organization logic.
"""

import os
import shutil
from datetime import datetime
from collections import defaultdict
import threading
from queue import Queue
import time

class FileProcessor:
    """Handles file scanning, copying, and organization."""
    
    def __init__(self, progress_callback=None, error_callback=None):
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        self.stop_requested = False
        self.processed_files = 0
        self.total_files = 0
        self.start_time = None
        
    def scan_files(self, source_folder, selected_extensions):
        """Recursively scan for files with selected extensions."""
        all_files = []
        extension_counts = defaultdict(int)
        
        for root, _, files in os.walk(source_folder):
            for file in files:
                if self.stop_requested:
                    return [], {}
                    
                ext = os.path.splitext(file)[1].lower()
                if ext in selected_extensions:
                    filepath = os.path.join(root, file)
                    all_files.append(filepath)
                    extension_counts[ext] += 1
                    
        return all_files, extension_counts
    
    def organize_files(self, source_files, dest_folder, sort_level, 
                      use_month_names=False, month_language='english', dry_run=False):
        """
        Organize files into date-based folder structure.
        
        Args:
            sort_level: 0=Year, 1=Year/Month, 2=Year/Month/Day
            use_month_names: Whether to use month names instead of numbers
            month_language: 'english' or 'spanish'
            dry_run: If True, only simulate without copying
        """
        from metadata_extractor import MetadataExtractor
        import config
        
        self.stop_requested = False
        self.processed_files = 0
        self.total_files = len(source_files)
        self.start_time = time.time()
        
        stats = defaultdict(lambda: {'count': 0, 'size': 0})
        errors = []
        
        for i, source_file in enumerate(source_files):
            if self.stop_requested:
                break
                
            try:
                # Update progress
                if self.progress_callback:
                    self.progress_callback(i, source_file)
                
                # Get date from file
                file_date = MetadataExtractor.get_date_from_file(source_file)
                
                if not file_date:
                    errors.append(f"No date found for {source_file}")
                    continue
                
                # Build destination path
                dest_path = self._build_destination_path(
                    source_file, dest_folder, file_date, 
                    sort_level, use_month_names, month_language
                )
                
                # Update statistics
                year = file_date.year
                stats[year]['count'] += 1
                stats[year]['size'] += os.path.getsize(source_file)
                
                # Copy file (or simulate in dry-run mode)
                if not dry_run:
                    self._copy_file_safely(source_file, dest_path)
                
                self.processed_files += 1
                
            except Exception as e:
                error_msg = f"Error processing {source_file}: {str(e)}"
                errors.append(error_msg)
                if self.error_callback:
                    self.error_callback(error_msg)
        
        return stats, errors
    
    def _build_destination_path(self, source_file, dest_folder, file_date,
                               sort_level, use_month_names, month_language):
        """Build the destination path based on date and sorting level."""
        import config
        
        year_folder = str(file_date.year)
        
        if sort_level >= 1:
            month = file_date.month
            if use_month_names:
                month_names = config.MONTH_NAMES.get(month_language, config.MONTH_NAMES['english'])
                month_folder = month_names[month - 1]
            else:
                month_folder = f"{month:02d}"
        else:
            month_folder = ""
            
        if sort_level >= 2:
            day_folder = f"{file_date.day:02d}"
        else:
            day_folder = ""
        
        # Build path components
        path_parts = [dest_folder, year_folder]
        if month_folder:
            path_parts.append(month_folder)
        if day_folder:
            path_parts.append(day_folder)
        
        # Create destination directory
        dest_dir = os.path.join(*path_parts)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Get filename and handle duplicates
        filename = os.path.basename(source_file)
        dest_path = os.path.join(dest_dir, filename)
        
        return dest_path
    
    def _copy_file_safely(self, source_path, dest_path):
        """Copy file, handling duplicate names."""
        if not os.path.exists(dest_path):
            shutil.copy2(source_path, dest_path)
            return dest_path
        
        # Handle duplicate filenames
        base, ext = os.path.splitext(dest_path)
        counter = 1
        
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        
        new_dest_path = f"{base}_{counter}{ext}"
        shutil.copy2(source_path, new_dest_path)
        return new_dest_path
    
    def stop_processing(self):
        """Request to stop processing."""
        self.stop_requested = True