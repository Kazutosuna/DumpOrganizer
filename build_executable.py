"""
Build standalone executable using PyInstaller
Run:  python build_executable.py
"""

import PyInstaller.__main__
import sys
import os

def build():
    """Build executable."""
    PyInstaller.__main__.run([
        'app.py',
        '--onefile',  # Single executable
        '--windowed',  # No console window
        '--name=MediaOrganizer',
        '--icon=NONE',  # Add icon if available
        '--add-data=src: src',  # Include src package
        '--hidden-import=tkinter',
        '--hidden-import=PIL',
        '--clean',
    ])
    
    print("\n✓ Executable built successfully!")
    print(f"  Location: {os.path.join('dist', 'MediaOrganizer.exe')}")

if __name__ == "__main__":
    build()