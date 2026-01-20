"""
Configuration and constants for the Media Sorter application.
Now with extended language support.
"""

import os
from datetime import datetime

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.raw', '.cr2', '.nef', '.arw'],
    'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.m4v', '.mpg', '.mpeg', '.3gp', '.webm', '.mts', '.m2ts', '.ogv']
}

# Extended month names in multiple languages
MONTH_NAMES = {
    'english': [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ],
    'spanish': [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ],
    'french': [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ],
    'german': [
        'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
    ],
    'italian': [
        'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
        'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
    ],
    'portuguese': [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ],
    'dutch': [
        'Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni',
        'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'
    ],
    'russian': [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ],
    'japanese': [
        '一月', '二月', '三月', '四月', '五月', '六月',
        '七月', '八月', '九月', '十月', '十一月', '十二月'
    ],
    'chinese_simplified': [
        '一月', '二月', '三月', '四月', '五月', '六月',
        '七月', '八月', '九月', '十月', '十一月', '十二月'
    ]
}

# Language display names (for UI)
LANGUAGE_DISPLAY_NAMES = {
    'english': 'English',
    'spanish': 'Español',
    'french': 'Français',
    'german': 'Deutsch',
    'italian': 'Italiano',
    'portuguese': 'Português',
    'dutch': 'Nederlands',
    'russian': 'Русский',
    'japanese': '日本語',
    'chinese_simplified': '简体中文'
}

# Default settings
DEFAULT_SETTINGS = {
    'sort_level': 2,  # 0=Year, 1=Year/Month, 2=Year/Month/Day
    'use_month_names': False,
    'month_language': 'english',
    'preserve_original': True,
    'dry_run': False,
    'theme': 'light',  # 'light' or 'dark'
    'batch_mode': False,
    'metadata_priority': 'exif'  # 'exif', 'hachoir', 'exiftool', 'filesystem'
}

# File operation constants
MAX_FILENAME_LENGTH = 255
DUPLICATE_SUFFIX_TEMPLATE = "_{}"