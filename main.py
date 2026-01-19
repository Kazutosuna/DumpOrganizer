"""
Main entry point for Media Sorter application.
"""

import tkinter as tk
from gui import MediaSorterGUI
import sys

def main():
    """Main function to run the application."""
    # Check if Pillow is available
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow library is required but not installed.")
        print("Please install it using: pip install pillow")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create and run the application
    root = tk.Tk()
    app = MediaSorterGUI(root)
    
    # Handle window close
    def on_closing():
        if hasattr(app, 'file_processor') and app.file_processor:
            app.file_processor.stop_processing()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()