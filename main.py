"""
Main GUI application for Media Organizer.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from pathlib import Path

from .file_scanner import FileScanner
from .metadata_extractor import MetadataExtractor
from .file_organizer import FileOrganizer
from . progress_handler import ProgressHandler


class MediaOrganizerGUI:
    """Main GUI application."""
    
    def __init__(self, root):
        """Initialize GUI."""
        self.root = root
        self.root. title("Media File Organizer")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Apply modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.sort_mode = tk.StringVar(value='year_month_day')
        self.selected_extensions = {}
        self.scanned_files = []
        self.is_processing = False
        self.progress_handler = ProgressHandler()
        
        self._build_ui()
        self._center_window()
    
    def _build_ui(self):
        """Build the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self. root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # ===== SOURCE FOLDER SECTION =====
        source_frame = ttk.LabelFrame(main_frame, text="1. Select Source Folder", padding="10")
        source_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        source_frame.columnconfigure(1, weight=1)
        
        ttk.Button(
            source_frame, text="Browse Source Folder",
            command=self._select_source_folder
        ).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(source_frame, textvariable=self.source_folder, 
                 foreground="blue").grid(row=0, column=1, sticky=tk.W)
        
        # ===== FILE TYPE SELECTION =====
        filetypes_frame = ttk.LabelFrame(main_frame, text="2. Select File Types", padding="10")
        filetypes_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filetypes_frame.columnconfigure(0, weight=1)
        
        # Scrollable frame for checkboxes
        canvas = tk.Canvas(filetypes_frame)
        scrollbar = ttk. Scrollbar(filetypes_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas. create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.filetypes_container = scrollable_frame
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        filetypes_frame.rowconfigure(0, weight=1)
        filetypes_frame.columnconfigure(0, weight=1)
        
        ttk.Label(self.filetypes_container, 
                 text="Select source folder to see available file types.. .",
                 foreground="gray").pack()
        
        # ===== SORTING OPTIONS =====
        sort_frame = ttk.LabelFrame(main_frame, text="3. Select Sorting Method", padding="10")
        sort_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        sort_options = [
            ("Year only (e.g., 2021/)", "year"),
            ("Year / Month (e.g., 2021/12/)", "year_month"),
            ("Year / Month / Day (e.g., 2021/12/25/)", "year_month_day")
        ]
        
        for text, value in sort_options: 
            ttk.Radiobutton(
                sort_frame, text=text, variable=self.sort_mode, value=value
            ).pack(anchor=tk.W)
        
        # ===== DESTINATION FOLDER SECTION =====
        dest_frame = ttk.LabelFrame(main_frame, text="4. Select Destination Folder", padding="10")
        dest_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dest_frame.columnconfigure(1, weight=1)
        
        ttk.Button(
            dest_frame, text="Browse Destination Folder",
            command=self._select_dest_folder
        ).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(dest_frame, textvariable=self.dest_folder,
                 foreground="green").grid(row=0, column=1, sticky=tk.W)
        
        # ===== DRY RUN & ACTION BUTTONS =====
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.dry_run_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            action_frame, text="Dry Run (preview without copying)",
            variable=self.dry_run_var
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(
            action_frame, text="Start Organization",
            command=self._start_organization
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            action_frame, text="Clear All",
            command=self._clear_all
        ).pack(side=tk.RIGHT)
        
        # ===== PROGRESS SECTION =====
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, mode='determinate', length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk. W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(
            progress_frame, text="Ready to start"
        )
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # ===== LOG SECTION =====
        log_frame = ttk.LabelFrame(main_frame, text="Log & Errors", padding="10")
        log_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        scrollbar_log = ttk. Scrollbar(log_frame)
        self.log_text = tk.Text(
            log_frame, height=8, width=80,
            yscrollcommand=scrollbar_log.set
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_log.grid(row=0, column=1, sticky=(tk. N, tk.S))
        scrollbar_log.config(command=self.log_text.yview)
        
        main_frame.rowconfigure(6, weight=1)
    
    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _select_source_folder(self):
        """Select source folder and scan for file types."""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self. source_folder. set(folder)
            self._scan_folder_async()
    
    def _scan_folder_async(self):
        """Scan folder in background thread."""
        def scan():
            self._log("Scanning folder for file types...")
            extensions = MetadataExtractor.get_all_media_extensions(
                self.source_folder.get()
            )
            
            self.root.after(0, lambda: self._display_file_types(extensions))
        
        thread = threading.Thread(target=scan, daemon=True)
        thread.start()
    
    def _display_file_types(self, extensions:  dict):
        """Display detected file types as checkboxes."""
        # Clear previous checkboxes
        for widget in self.filetypes_container. winfo_children():
            widget.destroy()
        
        self. selected_extensions = {}
        
        if not extensions:
            ttk.Label(self.filetypes_container,
                     text="No media files found",
                     foreground="red").pack()
            return
        
        # Sort by count (descending)
        sorted_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
        
        for ext, count in sorted_ext: 
            var = tk.BooleanVar(value=True)
            self.selected_extensions[ext] = var
            
            frame = ttk.Frame(self. filetypes_container)
            frame.pack(fill=tk. X, pady=2)
            
            ttk.Checkbutton(
                frame, text=f"{ext}",
                variable=var
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                frame, text=f"({count} files)",
                foreground="gray"
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        self._log(f"Found {len(extensions)} file types")
    
    def _select_dest_folder(self):
        """Select destination folder."""
        folder = filedialog. askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder.set(folder)
            self._log(f"Destination folder set:  {folder}")
    
    def _start_organization(self):
        """Start file organization process."""
        # Validation
        if not self.source_folder.get():
            messagebox.showerror("Error", "Please select a source folder")
            return
        
        if not self.dest_folder.get():
            messagebox.showerror("Error", "Please select a destination folder")
            return
        
        if not any(var.get() for var in self.selected_extensions.values()):
            messagebox.showerror("Error", "Please select at least one file type")
            return
        
        # Get selected extensions
        selected = {
            ext for ext, var in self.selected_extensions.items() if var.get()
        }
        
        # Start organization in background
        self.is_processing = True
        thread = threading.Thread(
            target=self._organize_files_worker,
            args=(selected,),
            daemon=True
        )
        thread.start()
    
    def _organize_files_worker(self, selected_extensions:  set):
        """Worker thread for file organization."""
        try:
            # Update UI
            self.root.after(0, lambda: self._set_ui_processing(True))
            
            # Scan files
            self._log("Scanning files...")
            scanner = FileScanner(
                progress_callback=lambda msg: self. root.after(0, lambda: self._log(msg))
            )
            files = scanner.scan_folder(
                self.source_folder.get(),
                selected_extensions
            )
            
            self. root.after(0, lambda: self._log(f"Found {len(files)} files to process"))
            
            if not files:
                self.root. after(0, lambda: messagebox.showinfo("Info", "No files found to process"))
                self.root.after(0, lambda: self._set_ui_processing(False))
                return
            
            # Organize files
            self._log("Starting file organization...")
            organizer = FileOrganizer(
                progress_callback=lambda data: self.root.after(0, lambda: self._update_progress(data)),
                error_callback=lambda msg: self.root.after(0, lambda: self._log(f"⚠ {msg}"))
            )
            
            results = organizer.organize_files(
                files,
                self. dest_folder.get(),
                self.sort_mode.get(),
                dry_run=self.dry_run_var.get()
            )
            
            # Display results
            self. root.after(0, lambda: self._display_results(results))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self._log(f"Error:  {str(e)}")
        
        finally:
            self.root.after(0, lambda: self._set_ui_processing(False))
    
    def _update_progress(self, data:  dict):
        """Update progress bar and label."""
        percentage = data['percentage']
        self.progress_bar['value'] = percentage
        
        label_text = (
            f"Processing: {data['processed']}/{data['total']} | "
            f"{percentage:.1f}% | "
            f"Speed: {data['speed']} | "
            f"ETA: {data['eta'] or 'calculating.. .'} | "
            f"File:  {data['destination']}"
        )
        
        self.progress_label.config(text=label_text)
        self.root.update_idletasks()
    
    def _display_results(self, results:  dict):
        """Display organization results."""
        self._log("\n" + "="*60)
        self._log("ORGANIZATION COMPLETE")
        self._log("="*60)
        self._log(f"Total files: {results['total']}")
        self._log(f"Processed: {results['processed']}")
        self._log(f"Skipped: {results['skipped']}")
        
        if results['summary']:
            self._log("\nFiles by year:")
            for year in sorted(results['summary'].keys()):
                count = results['summary'][year]
                self._log(f"  {year}: {count} files")
        
        if results['errors']:
            self._log(f"\nErrors ({len(results['errors'])}):")
            for error in results['errors'][:10]:  # Show first 10 errors
                self._log(f"  - {error}")
            if len(results['errors']) > 10:
                self._log(f"  ... and {len(results['errors']) - 10} more")
        
        # Show summary dialog
        mode_str = {
            'year': 'Year',
            'year_month': 'Year/Month',
            'year_month_day': 'Year/Month/Day'
        }
        
        message = (
            f"Organization {'simulation' if self.dry_run_var.get() else 'completed'}!\n\n"
            f"Total files:  {results['total']}\n"
            f"Processed: {results['processed']}\n"
            f"Skipped: {results['skipped']}\n"
            f"Sort mode: {mode_str[self.sort_mode.get()]}"
        )
        
        messagebox.showinfo("Complete", message)
    
    def _set_ui_processing(self, processing: bool):
        """Enable/disable UI during processing."""
        self.is_processing = processing
    
    def _log(self, message: str):
        """Add message to log."""
        self. log_text.insert(tk. END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _clear_all(self):
        """Clear all selections."""
        if messagebox.askyesno("Confirm", "Clear all selections?"):
            self.source_folder.set("")
            self.dest_folder. set("")
            self.selected_extensions.clear()
            self.log_text.delete("1.0", tk.END)
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Ready to start")
            for widget in self.filetypes_container.winfo_children():
                widget.destroy()
            ttk.Label(self.filetypes_container,
                     text="Select source folder to see available file types...",
                     foreground="gray").pack()


def main():
    """Entry point."""
    root = tk.Tk()
    app = MediaOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()