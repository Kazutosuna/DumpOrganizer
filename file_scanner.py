"""
File scanning module for recursive folder traversal.
"""

import os
from pathlib import Path
from typing import List, Tuple, Callable
from . metadata_extractor import MetadataExtractor


class FileScanner: 
    """Scans folders for media files."""
    
    def __init__(self, progress_callback: Callable = None):
        """
        Initialize scanner with optional progress callback.
        
        Args:
            progress_callback: Function to call with progress updates
        """
        self.progress_callback = progress_callback
    
    def scan_folder(self, folder_path: str, 
                   selected_extensions: set = None) -> List[Tuple[str, str]]:
        """
        Recursively scan folder for media files.
        
        Args:
            folder_path: Root folder to scan
            selected_extensions: Set of extensions to include (e.g., {'.jpg', '.mp4'})
                               If None, includes all media files
        
        Returns:
            List of (file_path, extension) tuples
        """
        media_files = []
        total_files_scanned = 0
        
        if selected_extensions is None:
            selected_extensions = MetadataExtractor. MEDIA_EXTENSIONS
        
        # Normalize extensions to lowercase
        selected_extensions = {ext. lower() for ext in selected_extensions}
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    total_files_scanned += 1
                    
                    file_path = os.path.join(root, file)
                    ext = Path(file).suffix.lower()
                    
                    if ext in selected_extensions:
                        media_files. append((file_path, ext))
                        
                        if self.progress_callback:
                            self.progress_callback(
                                f"Scanning...  {total_files_scanned} files found"
                            )
        
        except PermissionError as e:
            print(f"Permission denied scanning {folder_path}: {e}")
        except Exception as e: 
            print(f"Error scanning folder {folder_path}: {e}")
        
        return media_files
    
    def get_file_count(self, folder_path: str) -> int:
        """Get total count of files in folder tree."""
        count = 0
        try:
            for root, dirs, files in os.walk(folder_path):
                count += len(files)
        except Exception: 
            pass
        return count