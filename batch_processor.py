"""
Batch processing module for handling multiple source folders.
"""

import os
from pathlib import Path
from queue import Queue
import threading
import time

class BatchProcessor:
    """Manages batch processing of multiple source folders."""
    
    def __init__(self, progress_callback=None, folder_progress_callback=None, error_callback=None):
        self.progress_callback = progress_callback
        self.folder_progress_callback = folder_progress_callback
        self.error_callback = error_callback
        self.stop_requested = False
        
    def process_folders(self, source_folders, dest_folder, file_processor, 
                       sort_level, use_month_names=False, month_language='english', 
                       dry_run=False, selected_extensions=None):
        """
        Process multiple source folders sequentially.
        
        Args:
            source_folders: List of source folder paths
            dest_folder: Destination folder
            file_processor: Instance of FileProcessor
            sort_level: Sorting level (0-2)
            use_month_names: Whether to use month names
            month_language: Language for month names
            dry_run: If True, simulate only
            selected_extensions: Set of selected file extensions
        """
        self.stop_requested = False
        total_folders = len(source_folders)
        overall_stats = {}
        all_errors = []
        
        for folder_index, source_folder in enumerate(source_folders):
            if self.stop_requested:
                break
                
            # Notify folder progress
            if self.folder_progress_callback:
                self.folder_progress_callback(folder_index, total_folders, source_folder)
            
            try:
                # Scan files in current folder
                files_to_process, _ = file_processor.scan_files(source_folder, selected_extensions)
                
                if not files_to_process:
                    continue
                
                # Process files
                folder_stats, folder_errors = file_processor.organize_files(
                    source_files=files_to_process,
                    dest_folder=dest_folder,
                    sort_level=sort_level,
                    use_month_names=use_month_names,
                    month_language=month_language,
                    dry_run=dry_run
                )
                
                # Merge statistics
                for year, stats in folder_stats.items():
                    if year not in overall_stats:
                        overall_stats[year] = {'count': 0, 'size': 0}
                    overall_stats[year]['count'] += stats['count']
                    overall_stats[year]['size'] += stats['size']
                
                # Collect errors
                all_errors.extend(folder_errors)
                
            except Exception as e:
                error_msg = f"Error processing folder {source_folder}: {str(e)}"
                all_errors.append(error_msg)
                if self.error_callback:
                    self.error_callback(error_msg)
        
        return overall_stats, all_errors
    
    def stop_processing(self):
        """Request to stop batch processing."""
        self.stop_requested = True