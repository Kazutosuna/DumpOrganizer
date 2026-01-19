"""
Build script to create standalone executable with PyInstaller.
"""

import PyInstaller.__main__
import os
import shutil

def build_executable():
    """Build the application into a standalone executable."""
    
    # Ensure required packages are installed
    try:
        import PyInstaller
        import pillow
        import tkinter
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install requirements: pip install pyinstaller pillow")
        return
    
    # Create build directory
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=MediaSorter',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',  # Optional: add an icon file
        '--add-data=config.py;.',
        '--add-data=file_processor.py;.',
        '--add-data=gui.py;.',
        '--add-data=metadata_extractor.py;.',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--clean',
        '--distpath=dist'
    ]
    
    print("Building executable...")
    PyInstaller.__main__.run(args)
    
    # Copy any additional files needed
    if os.path.exists('config.ini'):
        shutil.copy('config.ini', 'dist/')
    
    print("\nBuild complete!")
    print("Executable created in: dist/MediaSorter.exe")
    print("\nNote: The first run may take a moment to start.")

if __name__ == "__main__":
    build_executable()