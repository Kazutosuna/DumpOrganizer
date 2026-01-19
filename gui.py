"""
GUI implementation using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from collections import defaultdict
import threading
import time

class MediaSorterGUI:
    """Main GUI for Media Sorter application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Media Sorter")
        self.root.geometry("900x700")
        
        # Variables
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.sort_level = tk.IntVar(value=2)  # Default: Year/Month/Day
        self.use_month_names = tk.BooleanVar(value=False)
        self.month_language = tk.StringVar(value='english')
        self.dry_run = tk.BooleanVar(value=False)
        
        # File tracking
        self.selected_extensions = set()
        self.all_files = []
        self.file_processor = None
        
        # Create GUI
        self._setup_style()
        self._create_widgets()
        self._apply_theme('light')
        
    def _setup_style(self):
        """Setup ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
    def _apply_theme(self, theme):
        """Apply light or dark theme."""
        if theme == 'dark':
            bg = '#2b2b2b'
            fg = '#ffffff'
            entry_bg = '#3c3c3c'
            button_bg = '#404040'
        else:
            bg = '#f0f0f0'
            fg = '#000000'
            entry_bg = '#ffffff'
            button_bg = '#e0e0e0'
            
        self.root.configure(bg=bg)
        
        # Widget colors would be applied here
        # In a full implementation, we'd configure all widgets
        
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Row counter
        row = 0
        
        # Source Folder
        ttk.Label(main_frame, text="Source Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_folder, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self._browse_source).grid(
            row=row, column=2, sticky=tk.W, pady=5)
        row += 1
        
        # Destination Folder
        ttk.Label(main_frame, text="Destination Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dest_folder, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        ttk.Button(main_frame, text="Browse...", command=self._browse_dest).grid(
            row=row, column=2, sticky=tk.W, pady=5)
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # File Type Selection Frame
        filetype_frame = ttk.LabelFrame(main_frame, text="File Types", padding="10")
        filetype_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        filetype_frame.columnconfigure(0, weight=1)
        
        self.filetype_container = ttk.Frame(filetype_frame)
        self.filetype_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(filetype_frame, text="Select All", 
                  command=lambda: self._toggle_all_filetypes(True)).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Button(filetype_frame, text="Deselect All", 
                  command=lambda: self._toggle_all_filetypes(False)).grid(row=1, column=0, sticky=tk.E, pady=5)
        
        row += 1
        
        # Sorting Options Frame
        sort_frame = ttk.LabelFrame(main_frame, text="Sorting Options", padding="10")
        sort_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Sort level
        ttk.Radiobutton(sort_frame, text="By Year only", 
                       variable=self.sort_level, value=0).grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(sort_frame, text="By Year/Month", 
                       variable=self.sort_level, value=1).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Radiobutton(sort_frame, text="By Year/Month/Day", 
                       variable=self.sort_level, value=2).grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Month names option
        ttk.Checkbutton(sort_frame, text="Use month names", 
                       variable=self.use_month_names, 
                       command=self._toggle_month_language).grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.month_language_combo = ttk.Combobox(sort_frame, 
                                                textvariable=self.month_language,
                                                values=['english', 'spanish'],
                                                state='disabled', width=15)
        self.month_language_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Dry run option
        ttk.Checkbutton(sort_frame, text="Dry Run (simulate only)", 
                       variable=self.dry_run).grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        
        row += 1
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.current_file_label = ttk.Label(progress_frame, text="")
        self.current_file_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.stats_label = ttk.Label(progress_frame, text="")
        self.stats_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        row += 1
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.scan_button = ttk.Button(button_frame, text="Scan Folder", 
                                     command=self._scan_folder)
        self.scan_button.grid(row=0, column=0, padx=5)
        
        self.start_button = ttk.Button(button_frame, text="Start Sorting", 
                                      command=self._start_sorting, state='disabled')
        self.start_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self._stop_processing, state='disabled')
        self.stop_button.grid(row=0, column=2, padx=5)
        
        row += 1
        
        # Log/Error Display
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights for resizing
        main_frame.rowconfigure(row, weight=1)
        
    def _browse_source(self):
        """Browse for source folder."""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder.set(folder)
            self._scan_folder()
            
    def _browse_dest(self):
        """Browse for destination folder."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder.set(folder)
            
    def _scan_folder(self):
        """Scan folder for file types."""
        source = self.source_folder.get()
        if not source or not os.path.exists(source):
            messagebox.showwarning("Warning", "Please select a valid source folder")
            return
            
        from file_processor import FileProcessor
        
        self.scan_button.config(state='disabled')
        self._log_message("Scanning folder...")
        
        # Scan in background thread
        def scan_thread():
            processor = FileProcessor()
            import config
            
            # Get all supported extensions
            all_extensions = set(config.SUPPORTED_EXTENSIONS['images'] + 
                               config.SUPPORTED_EXTENSIONS['videos'])
            
            self.all_files, extension_counts = processor.scan_files(source, all_extensions)
            
            # Update UI in main thread
            self.root.after(0, self._update_filetype_list, extension_counts)
            self.root.after(0, self.scan_button.config, {'state': 'normal'})
            
            self._log_message(f"Found {len(self.all_files)} files")
            
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def _update_filetype_list(self, extension_counts):
        """Update file type checkboxes based on scan results."""
        # Clear existing widgets
        for widget in self.filetype_container.winfo_children():
            widget.destroy()
            
        if not extension_counts:
            ttk.Label(self.filetype_container, text="No supported files found").pack()
            self.start_button.config(state='disabled')
            return
            
        # Create checkboxes for each file type
        self.filetype_vars = {}
        row = 0
        col = 0
        
        for ext, count in sorted(extension_counts.items()):
            var = tk.BooleanVar(value=True)
            self.filetype_vars[ext] = var
            
            cb = ttk.Checkbutton(self.filetype_container, 
                                text=f"{ext} ({count} files)",
                                variable=var,
                                command=self._update_selected_extensions)
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        self._update_selected_extensions()
        
    def _update_selected_extensions(self):
        """Update set of selected extensions."""
        self.selected_extensions = {
            ext for ext, var in self.filetype_vars.items() if var.get()
        }
        
        # Enable/disable start button based on selections
        if self.selected_extensions and self.dest_folder.get():
            self.start_button.config(state='normal')
        else:
            self.start_button.config(state='disabled')
            
    def _toggle_all_filetypes(self, select):
        """Select or deselect all file types."""
        for var in self.filetype_vars.values():
            var.set(select)
        self._update_selected_extensions()
        
    def _toggle_month_language(self):
        """Enable/disable month language combobox."""
        if self.use_month_names.get():
            self.month_language_combo.config(state='normal')
        else:
            self.month_language_combo.config(state='disabled')
            
    def _start_sorting(self):
        """Start the sorting process."""
        if not self.selected_extensions:
            messagebox.showwarning("Warning", "Please select at least one file type")
            return
            
        if not self.dest_folder.get():
            messagebox.showwarning("Warning", "Please select a destination folder")
            return
            
        # Filter files by selected extensions
        files_to_process = [
            f for f in self.all_files 
            if os.path.splitext(f)[1].lower() in self.selected_extensions
        ]
        
        if not files_to_process:
            messagebox.showwarning("Warning", "No files match the selected types")
            return
            
        # Disable controls during processing
        self.scan_button.config(state='disabled')
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting...")
        
        # Start processing in background thread
        def process_thread():
            from file_processor import FileProcessor
            
            self.file_processor = FileProcessor(
                progress_callback=self._update_progress,
                error_callback=self._log_error
            )
            
            stats, errors = self.file_processor.organize_files(
                source_files=files_to_process,
                dest_folder=self.dest_folder.get(),
                sort_level=self.sort_level.get(),
                use_month_names=self.use_month_names.get(),
                month_language=self.month_language.get(),
                dry_run=self.dry_run.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self._processing_complete, stats, errors)
            
        threading.Thread(target=process_thread, daemon=True).start()
        
    def _update_progress(self, current, current_file):
        """Update progress display."""
        def update():
            total = self.file_processor.total_files
            processed = current + 1
            
            # Update progress bar
            progress_percent = (processed / total) * 100
            self.progress_bar['value'] = progress_percent
            
            # Update labels
            self.progress_label.config(
                text=f"Processed: {processed}/{total} ({progress_percent:.1f}%)"
            )
            
            # Show current file (truncate if too long)
            display_file = os.path.basename(current_file)
            if len(display_file) > 50:
                display_file = "..." + display_file[-47:]
            self.current_file_label.config(text=f"Current: {display_file}")
            
            # Calculate and display ETA
            if hasattr(self.file_processor, 'start_time') and processed > 0:
                elapsed = time.time() - self.file_processor.start_time
                files_per_second = processed / elapsed
                remaining = total - processed
                eta = remaining / files_per_second if files_per_second > 0 else 0
                
                if eta < 60:
                    eta_str = f"{eta:.0f}s"
                elif eta < 3600:
                    eta_str = f"{eta/60:.1f}m"
                else:
                    eta_str = f"{eta/3600:.1f}h"
                    
                self.stats_label.config(
                    text=f"Speed: {files_per_second:.1f} files/sec | ETA: {eta_str}"
                )
                
        self.root.after(0, update)
        
    def _processing_complete(self, stats, errors):
        """Handle completion of processing."""
        # Re-enable controls
        self.scan_button.config(state='normal')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        # Show completion message
        total_files = sum(year_stats['count'] for year_stats in stats.values())
        total_size = sum(year_stats['size'] for year_stats in stats.values())
        
        size_mb = total_size / (1024 * 1024)
        
        mode = "Dry Run - Simulated" if self.dry_run.get() else "Completed"
        
        message = f"{mode}!\n\n"
        message += f"Total files processed: {total_files}\n"
        message += f"Total size: {size_mb:.1f} MB\n\n"
        message += "By year:\n"
        
        for year in sorted(stats.keys()):
            count = stats[year]['count']
            size = stats[year]['size'] / (1024 * 1024)
            message += f"  {year}: {count} files ({size:.1f} MB)\n"
            
        if errors:
            message += f"\nErrors: {len(errors)} (see log for details)"
            
        messagebox.showinfo("Processing Complete", message)
        
        # Log errors
        for error in errors:
            self._log_error(error)
            
        self._log_message(f"Processing complete. {total_files} files processed.")
        
    def _stop_processing(self):
        """Stop the current processing."""
        if self.file_processor:
            self.file_processor.stop_processing()
            self._log_message("Processing stopped by user")
            
        self.stop_button.config(state='disabled')
        
    def _log_message(self, message):
        """Add message to log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def _log_error(self, error):
        """Add error message to log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] ERROR: {error}\n", 'error')
        self.log_text.see(tk.END)
        
        # Configure error tag (if not already)
        if not self.log_text.tag_names() or 'error' not in self.log_text.tag_names():
            self.log_text.tag_config('error', foreground='red')