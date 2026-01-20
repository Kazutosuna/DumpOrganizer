"""
Enhanced EXIF and metadata extraction from media files.
Now includes video metadata support via hachoir and exiftool fallback.
"""

import os
import subprocess
from datetime import datetime
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import mimetypes
import sys

class MetadataExtractor:
    """Extracts date information from media files with multiple fallback methods."""
    
    def __init__(self):
        self.hachoir_available = self._check_hachoir_available()
        self.exiftool_available = self._check_exiftool_available()
        
    def _check_hachoir_available(self):
        """Check if hachoir library is available."""
        try:
            import hachoir
            return True
        except ImportError:
            return False
            
    def _check_exiftool_available(self):
        """Check if exiftool command-line tool is available."""
        try:
            # Try to run exiftool -ver
            result = subprocess.run(['exiftool', '-ver'], 
                                  capture_output=True, 
                                  text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def get_date_from_file(self, filepath, fallback_to_filesystem=True):
        """
        Try to get date from metadata using multiple methods.
        Returns datetime object or None.
        """
        methods = [
            self._get_exif_date,           # Image EXIF
            self._get_video_metadata_hachoir,  # Video via hachoir
            self._get_metadata_exiftool,   # Universal via exiftool
        ]
        
        for method in methods:
            try:
                date_result = method(filepath)
                if date_result:
                    return date_result
            except Exception:
                continue
        
        # Fall back to file system dates
        if fallback_to_filesystem:
            return self._get_date_from_filesystem(filepath)
            
        return None
    
    def _get_exif_date(self, filepath):
        """Extract date from EXIF data of images."""
        try:
            with Image.open(filepath) as img:
                exif_data = img._getexif()
                
                if exif_data:
                    # Try different EXIF date tags in order of preference
                    date_tags = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']
                    
                    for tag_name in date_tags:
                        for tag_id, tag_value in TAGS.items():
                            if tag_value == tag_name and tag_id in exif_data:
                                date_str = exif_data[tag_id]
                                if date_str:
                                    # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                                    try:
                                        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                                    except ValueError:
                                        continue
        except Exception:
            pass
            
        return None
    
        def _get_video_metadata_hachoir(self, filepath):
        """Extract date from video files using hachoir."""
        if not self.hachoir_available:
            return None
            
        try:
            # Import inside the method to avoid issues if hachoir is partially installed
            try:
                from hachoir.parser import createParser
                from hachoir.metadata import extractMetadata
            except ImportError as e:
                # Hachoir might be installed but missing some components
                print(f"Hachoir import error: {e}")
                self.hachoir_available = False
                return None
                
            parser = createParser(filepath)
            if not parser:
                return None
                
            with parser:
                metadata = extractMetadata(parser)
                if metadata:
                    # Try different metadata keys for creation date
                    date_keys = ['creation_date', 'date', 'creation_time']
                    
                    for key in date_keys:
                        if metadata.has(key):
                            date_value = metadata.get(key)
                            if date_value:
                                # Convert to datetime if it's a datetime object
                                if hasattr(date_value, 'datetime'):
                                    return date_value.datetime
                                # Try to parse string
                                elif isinstance(date_value, str):
                                    # Try common date formats
                                    date_formats = [
                                        '%Y-%m-%d %H:%M:%S',
                                        '%Y/%m/%d %H:%M:%S',
                                        '%Y:%m:%d %H:%M:%S',
                                        '%Y-%m-%d',
                                        '%Y/%m/%d'
                                    ]
                                    
                                    for fmt in date_formats:
                                        try:
                                            return datetime.strptime(str(date_value)[:19], fmt)
                                        except ValueError:
                                            continue
        except Exception as e:
            # Log the error but don't crash
            print(f"Hachoir error processing {filepath}: {e}")
            # Disable hachoir for future calls if it's causing issues
            self.hachoir_available = False
            
        return None
    
    def _get_metadata_exiftool(self, filepath):
        """Extract date using exiftool (command-line)."""
        if not self.exiftool_available:
            return None
            
        try:
            # Run exiftool to get creation date
            cmd = ['exiftool', '-d', '%Y:%m:%d %H:%M:%S', '-DateTimeOriginal', '-CreateDate', '-MediaCreateDate', '-TrackCreateDate', '-FileModifyDate', '-T', filepath]
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line and line != '-':
                        try:
                            return datetime.strptime(line.strip(), '%Y:%m:%d %H:%M:%S')
                        except ValueError:
                            continue
        except Exception:
            pass
            
        return None
    
    def _get_date_from_filesystem(self, filepath):
        """Get date from file creation or modification time."""
        try:
            # Try to get birth time (creation date) if available
            try:
                birth_time = os.path.getctime(filepath)
            except AttributeError:
                # On some systems, getctime returns last metadata change
                birth_time = os.path.getmtime(filepath)
            
            # Use the earliest available time
            return datetime.fromtimestamp(birth_time)
            
        except Exception:
            return None
    
    def get_metadata_summary(self, filepath):
        """Get a summary of all available metadata for debugging."""
        summary = {}
        
        # Get all possible dates
        summary['exif_date'] = self._get_exif_date(filepath)
        summary['hachoir_date'] = self._get_video_metadata_hachoir(filepath)
        summary['exiftool_date'] = self._get_metadata_exiftool(filepath)
        summary['filesystem_date'] = self._get_date_from_filesystem(filepath)
        
        # Get file info
        try:
            summary['file_size'] = os.path.getsize(filepath)
            summary['file_extension'] = os.path.splitext(filepath)[1].lower()
        except:
            pass
            
        return summary