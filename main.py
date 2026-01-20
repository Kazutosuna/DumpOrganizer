"""
Enhanced main entry point for Media Sorter application.
"""

import tkinter as tk
from gui import MediaSorterGUI
import sys

def check_dependencies():
    """Check for required and optional dependencies."""
    required = ['PIL']
    optional = ['hachoir']
    
    print("Checking dependencies...")
    
    # Check required dependencies
    for dep in required:
        try:
            if dep == 'PIL':
                from PIL import Image
            print(f"✓ {dep} is installed")
        except ImportError:
            print(f"✗ {dep} is NOT installed")
            print(f"Please install using: pip install pillow")
            return False
    
    # Check optional dependencies
    for dep in optional:
        try:
            if dep == 'hachoir':
                import hachoir
            print(f"✓ {dep} is installed (optional)")
        except ImportError:
            print(f"⚠ {dep} is not installed (optional)")
            print(f"  For video metadata support: pip install hachoir")
    
    # Check exiftool
    try:
        import subprocess
        result = subprocess.run(['exiftool', '-ver'], 
                              capture_output=True, 
                              text=True,
                              creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        if result.returncode == 0:
            print("✓ ExifTool is installed (optional)")
        else:
            print("⚠ ExifTool is not installed (optional)")
            print("  Download from: https://exiftool.org/")
    except:
        print("⚠ ExifTool is not installed (optional)")
        print("  Download from: https://exiftool.org/")
    
    return True

def main():
    """Main function to run the application."""
    print("=" * 50)
    print("Media Sorter Pro - Enhanced Version")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Starting application...")
    
    # Create and run the application
    root = tk.Tk()
    app = MediaSorterGUI(root)
    
    # Handle window close
    def on_closing():
        if hasattr(app, 'file_processor') and app.file_processor:
            app.file_processor.stop_processing()
        if hasattr(app, 'batch_processor') and app.batch_processor:
            app.batch_processor.stop_processing()
        root.destroy()
        print("\nApplication closed")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()