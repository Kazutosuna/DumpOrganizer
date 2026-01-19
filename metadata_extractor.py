"""
Metadata extraction module for images and videos. 
Supports EXIF data, file dates, and video metadata.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import mimetypes


class MetadataExtractor: 
    """Extracts date information from media files."""
    
    # Image formats that might have EXIF data
    IMAGE_EXTENSIONS = {'. jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
    MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
    
    @staticmethod
    def extract_date(file_path: str) -> Optional[datetime]:
        """
        Extract date from file with multiple fallback methods.
        
        Priority: 
        1. EXIF data (images)
        2. Video metadata (videos)
        3. File modification date
        4. File creation date (Windows)
        
        Args:
            file_path: Full path to the media file
            
        Returns: 
            datetime object or None if extraction fails
        """
        try: 
            # Try EXIF/video metadata first
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in MetadataExtractor.IMAGE_EXTENSIONS:
                exif_date = MetadataExtractor._extract_exif_date(file_path)
                if exif_date:
                    return exif_date
            
            if file_ext in MetadataExtractor.VIDEO_EXTENSIONS:
                video_date = MetadataExtractor._extract_video_date(file_path)
                if video_date:
                    return video_date
            
            # Fallback to file dates
            return MetadataExtractor._extract_file_date(file_path)
            
        except Exception as e:
            print(f"Error extracting date from {file_path}: {e}")
            return None
    
    @staticmethod
    def _extract_exif_date(file_path: str) -> Optional[datetime]:
        """Extract date from image EXIF data."""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            image = Image.open(file_path)
            exif_data = image._getexif()
            
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    
                    # Check for date-related EXIF tags
                    if tag_name in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        try:
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                        except (ValueError, TypeError):
                            continue
            
            return None
            
        except ImportError:
            # PIL not available, continue with fallback
            return None
        except Exception: 
            return None
    
    @staticmethod
    def _extract_video_date(file_path: str) -> Optional[datetime]: 
        """Extract date from video metadata using ffmpeg."""
        try:
            import subprocess
            import json
            
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                 '-show_format', file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Try to extract creation_time from format tags
                if 'format' in data and 'tags' in data['format']:
                    tags = data['format']['tags']
                    creation_time = tags.get('creation_time') or tags.get('date')
                    
                    if creation_time:
                        try:
                            # Try ISO format first
                            return datetime. fromisoformat(creation_time. replace('Z', '+00:00'))
                        except (ValueError, AttributeError):
                            pass
            
            return None
            
        except (ImportError, FileNotFoundError, subprocess.TimeoutExpired):
            # ffmpeg not available or timeout
            return None
        except Exception:
            return None
    
    @staticmethod
    def _extract_file_date(file_path: str) -> Optional[datetime]:
        """Extract date from file timestamps."""
        try:
            stat = os.stat(file_path)
            
            # Prefer modification date
            mtime = stat.st_mtime
            
            # On Windows, try to get creation time
            if hasattr(stat, 'st_birthtime'):
                ctime = stat.st_birthtime
                if ctime < mtime:
                    mtime = ctime
            
            return datetime.fromtimestamp(mtime)
            
        except Exception:
            return None
    
    @staticmethod
    def get_all_media_extensions(folder_path: str) -> dict:
        """
        Recursively scan folder and return all media file extensions with counts.
        
        Args:
            folder_path: Root folder to scan
            
        Returns: 
            Dictionary with extension -> count mapping
        """
        extensions = {}
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    ext = Path(file).suffix.lower()
                    
                    if ext in MetadataExtractor.MEDIA_EXTENSIONS:
                        extensions[ext] = extensions.get(ext, 0) + 1
        
        except Exception as e:
            print(f"Error scanning folder {folder_path}:  {e}")
        
        return extensions
    
    @staticmethod
    def is_supported_media(file_path: str) -> bool:
        """Check if file is a supported media type."""
        ext = Path(file_path).suffix.lower()
        return ext in MetadataExtractor.MEDIA_EXTENSIONS