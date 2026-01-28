"""
Configuration and constants for the Media Sorter application.
"""

import os
from datetime import datetime

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic'],
    'videos': [
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.m4v', '.mpg', '.mpeg', '.3gp',
        '.webm', '.mts', '.m2ts', '.ogv', '.asf', '.vob', '.dat', '.f4v'
    ]
}
# Month names in different languages
MONTH_NAMES = {
    'english': [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ],
    'spanish': [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
}

# Default settings
DEFAULT_SETTINGS = {
    'sort_level': 2,  # 0=Year, 1=Year/Month, 2=Year/Month/Day
    'use_month_names': False,
    'month_language': 'english',
    'preserve_original': True,
    'dry_run': False,
    'theme': 'light'  # 'light' or 'dark'
}

# File operation constants
MAX_FILENAME_LENGTH = 255
DUPLICATE_SUFFIX_TEMPLATE = "_{}"
