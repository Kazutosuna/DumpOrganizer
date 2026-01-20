"""
Enhanced build script for Media Sorter Pro.
"""

import PyInstaller.__main__
import os
import shutil
import sys

def build_executable():
    """Build the enhanced application into a standalone executable."""
    
    print("Building Media Sorter Pro...")
    print("This may take a few minutes...")
    
    # Ensure required packages are installed
    try:
        import PyInstaller
        import pillow
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install: pip install pyinstaller pillow")
        return
    
    # Create build directory
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=MediaSorterPro',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',  # Optional: add an icon file
        '--add-data=config.py;.',
        '--add-data=file_processor.py;.',
        '--add-data=gui.py;.',
        '--add-data=metadata_extractor.py;.',
        '--add-data=batch_processor.py;.',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=hachoir',
        '--hidden-import=hachoir.parser',
        '--hidden-import=hachoir.metadata',
        '--clean',
        '--distpath=dist'
    ]
    
    try:
        PyInstaller.__main__.run(args)
        
        print("\n" + "=" * 50)
        print("Build successful!")
        print("=" * 50)
        print(f"\nExecutable created at: dist/MediaSorterPro.exe")
        print("\nFile size: ", end="")
        
        exe_path = os.path.join('dist', 'MediaSorterPro.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"{size_mb:.1f} MB")
        
        print("\nFeatures included:")
        print("  ✓ Batch processing")
        print("  ✓ 10+ languages support")
        print("  ✓ Enhanced metadata (Hachoir)")
        print("  ✓ ExifTool integration")
        print("  ✓ Structure preview")
        print("  ✓ Dark/light themes")
        
        print("\nNote: ExifTool is not included in the executable.")
        print("      Users must install it separately for full metadata support.")
        print("\nFirst run may take a moment to start.")
        
    except Exception as e:
        print(f"\nBuild failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Try running as administrator")
        print("3. Check if antivirus is blocking PyInstaller")

if __name__ == "__main__":
    build_executable()