"""
EXIF and metadata extraction from media files.
"""

import os
from datetime import datetime
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import mimetypes

class MetadataExtractor:
    """Extracts date information from media files."""
    
    @staticmethod
    def get_date_from_file(filepath, fallback_to_filesystem=True):
        """
        Try to get date from metadata, fall back to file system dates.
        Returns datetime object or None.
        """
        # First try EXIF/metadata
        date_from_meta = MetadataExtractor._get_date_from_metadata(filepath)
        if date_from_meta:
            return date_from_meta
            
        # Fall back to file system dates
        if fallback_to_filesystem:
            return MetadataExtractor._get_date_from_filesystem(filepath)
            
        return None
    
    @staticmethod
    def _get_date_from_metadata(filepath):
        """Extract date from image EXIF or video metadata."""
        try:
            mime_type, _ = mimetypes.guess_type(filepath)
            
            if mime_type and mime_type.startswith('image/'):
                return MetadataExtractor._get_exif_date(filepath)
            elif mime_type and mime_type.startswith('video/'):
                # For videos, we could use a library like hachoir or ffmpeg
                # For simplicity, we'll use file system dates for now
                # This can be extended with proper video metadata extraction
                return None
                
        except Exception as e:
            print(f"Error reading metadata from {filepath}: {e}")
            
        return None
    
    @staticmethod
    def _get_exif_date(filepath):
        """Extract date from EXIF data of images."""
        try:
            with Image.open(filepath) as img:
                exif_data = img._getexif()
                
                if exif_data:
                    # Try different EXIF date tags
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
    
    @staticmethod
    def _get_date_from_filesystem(filepath):
        """Get date from file creation or modification time."""
        try:
            # Try creation time first
            creation_time = os.path.getctime(filepath)
            mod_time = os.path.getmtime(filepath)
            
            # Use the earlier of the two
            return datetime.fromtimestamp(min(creation_time, mod_time))
            
        except Exception:
            return None