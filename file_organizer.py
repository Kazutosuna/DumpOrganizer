"""
Main file organization logic. 
Handles copying files to organized folder structure.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Callable, Optional
from .metadata_extractor import MetadataExtractor


class FileOrganizer:
    """Organizes files into date-based folder structure."""
    
    def __init__(self, progress_callback:  Callable = None, error_callback: Callable = None):
        """
        Initialize organizer with callbacks.
        
        Args:
            progress_callback: Function for progress updates
            error_callback:  Function for error logging
        """
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        self.processed_count = 0
        self.error_count = 0
    
    def organize_files(self, 
                      files: List[Tuple[str, str]],
                      dest_folder: str,
                      sort_mode: str = 'year_month_day',
                      dry_run: bool = False) -> dict:
        """
        Organize files into destination folder structure.
        
        Args:
            files: List of (file_path, extension) tuples
            dest_folder: Destination root folder
            sort_mode: 'year', 'year_month', or 'year_month_day'
            dry_run: If True, don't actually copy files
        
        Returns:
            Dictionary with organization results
        """
        results = {
            'total':  len(files),
            'processed': 0,
            'skipped': 0,
            'errors': [],
            'summary': {}
        }
        
        # Create destination folder if it doesn't exist
        Path(dest_folder).mkdir(parents=True, exist_ok=True)
        
        for idx, (file_path, ext) in enumerate(files):
            try:
                # Extract date from file
                file_date = MetadataExtractor.extract_date(file_path)
                
                if file_date is None:
                    results['errors'].append(
                        f"Could not extract date from {Path(file_path).name}"
                    )
                    results['skipped'] += 1
                    if self.error_callback:
                        self.error_callback(f"Skipped:  {Path(file_path).name} (no date found)")
                    continue
                
                # Build destination path
                dest_path = self._build_destination_path(
                    file_path, file_date, dest_folder, sort_mode
                )
                
                # Ensure destination directory exists
                dest_dir = os.path.dirname(dest_path)
                Path(dest_dir).mkdir(parents=True, exist_ok=True)
                
                # Handle duplicate filenames
                dest_path = self._handle_duplicates(dest_path)
                
                # Copy file
                if not dry_run: 
                    shutil.copy2(file_path, dest_path)
                
                results['processed'] += 1
                
                # Update progress
                if self.progress_callback:
                    self.progress_callback({
                        'processed': results['processed'],
                        'total': results['total'],
                        'current_file': Path(file_path).name,
                        'destination': os.path.relpath(dest_path, dest_folder)
                    })
                
                # Track summary
                year = str(file_date.year)
                if year not in results['summary']:
                    results['summary'][year] = 0
                results['summary'][year] += 1
                
            except Exception as e:
                results['errors'].append(f"Error processing {file_path}: {str(e)}")
                results['skipped'] += 1
                if self.error_callback:
                    self.error_callback(f"Error:  {Path(file_path).name} - {str(e)}")
        
        return results
    
    def _build_destination_path(self, 
                               source_file: str,
                               file_date: datetime,
                               dest_folder: str,
                               sort_mode: str) -> str:
        """Build destination file path based on sort mode."""
        filename = Path(source_file).name
        
        # Create date-based folder structure
        if sort_mode == 'year': 
            rel_path = str(file_date.year)
        elif sort_mode == 'year_month':
            rel_path = os.path.join(
                str(file_date.year),
                f"{file_date.month:02d}"
            )
        else:  # year_month_day
            rel_path = os. path.join(
                str(file_date.year),
                f"{file_date.month:02d}",
                f"{file_date.day:02d}"
            )
        
        return os.path.join(dest_folder, rel_path, filename)
    
    def _handle_duplicates(self, file_path: str) -> str:
        """Add suffix to duplicate filenames."""
        if not os.path.exists(file_path):
            return file_path
        
        # File already exists, add suffix
        path_obj = Path(file_path)
        counter = 1
        
        while True:
            new_name = f"{path_obj.stem}_{counter}{path_obj.suffix}"
            new_path = path_obj. parent / new_name
            
            if not new_path.exists():
                return str(new_path)
            
            counter += 1
    
    def verify_organization(self, dest_folder: str) -> dict:
        """Verify organized files and get statistics."""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'by_year': {}
        }
        
        try:
            for root, dirs, files in os.walk(dest_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Count file
                    stats['total_files'] += 1
                    
                    # Add size
                    try:
                        size = os.path.getsize(file_path)
                        stats['total_size_mb'] += size / (1024 * 1024)
                    except Exception:
                        pass
                    
                    # Track by year (from folder structure)
                    parts = Path(file_path).relative_to(dest_folder).parts
                    if parts: 
                        year = parts[0]
                        if year not in stats['by_year']:
                            stats['by_year'][year] = 0
                        stats['by_year'][year] += 1
        
        except Exception as e: 
            print(f"Error verifying organization: {e}")
        
        return stats