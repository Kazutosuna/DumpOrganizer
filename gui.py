"""
Enhanced GUI with batch processing and metadata options.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from collections import defaultdict
import threading
import time

class MediaSorterGUI:
    """Enhanced GUI for Media Sorter application with batch processing."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Media Sorter Pro")
        self.root.geometry("1000x800")
        
        # Variables
        self.source_folders = []  # List for batch processing
        self.dest_folder = tk.StringVar()
        self.sort_level = tk.IntVar(value=2)
        self.use_month_names = tk.BooleanVar(value=False)
        self.month_language = tk.StringVar(value='english')
        self.dry_run = tk.BooleanVar(value=False)
        self.batch_mode = tk.BooleanVar(value=False)
        self.metadata_priority = tk.StringVar(value='exif')
        
        # File tracking
        self.selected_extensions = set()
        self.all_files = []
        self.file_processor = None
        self.batch_processor = None
        
        # Create GUI
        self._setup_style()
        self._create_widgets()
        self._apply_theme('light')
        
    def _setup_style(self):
        """Setup ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
    def _create_widgets(self):
        """Create all GUI widgets with enhanced features."""
        # Main container with notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        main_frame = ttk.Frame(notebook, padding="10")
        notebook.add(main_frame, text="Main")
        
        # Settings tab
        settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(settings_frame, text="Settings")
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Build both tabs
        self._create_main_tab(main_frame)
        self._create_settings_tab(settings_frame)
        
    def _create_main_tab(self, parent):
        """Create the main processing tab."""
        row = 0
        
        # Batch mode toggle
        ttk.Checkbutton(parent, text="Batch Mode (Multiple Source Folders)", 
                       variable=self.batch_mode,
                       command=self._toggle_batch_mode).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1
        
        # Source Folder(s) - Single mode
        self.source_single_frame = ttk.Frame(parent)
        self.source_single_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.source_single_frame, text="Source Folder:").pack(side=tk.LEFT, padx=(0, 5))
        self.source_single_entry = ttk.Entry(self.source_single_frame, width=50)
        self.source_single_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(self.source_single_frame, text="Browse...", 
                  command=self._browse_single_source).pack(side=tk.LEFT)
        
        # Source Folders - Batch mode (initially hidden)
        self.source_batch_frame = ttk.Frame(parent)
        self.source_batch_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.source_batch_frame.grid_remove()
        
        ttk.Label(self.source_batch_frame, text="Source Folders:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.source_listbox = tk.Listbox(self.source_batch_frame, height=4, width=50)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        button_frame = ttk.Frame(self.source_batch_frame)
        button_frame.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Add Folder...", 
                  command=self._add_batch_folder).pack(pady=2)
        ttk.Button(button_frame, text="Remove Selected", 
                  command=self._remove_batch_folder).pack(pady=2)
        ttk.Button(button_frame, text="Clear All", 
                  command=self._clear_batch_folders).pack(pady=2)
        
        row += 1
        
        # Destination Folder
        ttk.Label(parent, text="Destination Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.dest_folder, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        ttk.Button(parent, text="Browse...", command=self._browse_dest).grid(
            row=row, column=2, sticky=tk.W, pady=5)
        row += 1
        
        # Separator
        ttk.Separator(parent, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # File Type Selection Frame
        self._create_filetype_frame(parent, row)
        row += 1
        
        # Sorting Options Frame
        self._create_sorting_frame(parent, row)
        row += 1
        
        # Progress Frame
        self._create_progress_frame(parent, row)
        row += 1
        
        # Control Buttons
        self._create_control_buttons(parent, row)
        row += 1
        
        # Log Display
        self._create_log_frame(parent, row)
        
    def _create_settings_tab(self, parent):
        """Create the settings tab."""
        row = 0
        
        # Metadata Settings
        metadata_frame = ttk.LabelFrame(parent, text="Metadata Settings", padding="10")
        metadata_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(metadata_frame, text="Metadata Priority:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        metadata_combo = ttk.Combobox(metadata_frame, 
                                     textvariable=self.metadata_priority,
                                     values=['exif', 'hachoir', 'exiftool', 'filesystem'],
                                     state='readonly',
                                     width=20)
        metadata_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        metadata_combo.set('exif')
        
        # Check available metadata tools
        self._check_metadata_tools(metadata_frame)
        
        row += 1
        
        # Month Language Settings
        language_frame = ttk.LabelFrame(parent, text="Language Settings", padding="10")
        language_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(language_frame, text="Month Language:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        import config
        languages = [(code, config.LANGUAGE_DISPLAY_NAMES.get(code, code)) 
                    for code in config.MONTH_NAMES.keys()]
        language_values = [code for code, _ in languages]
        
        self.month_language_combo = ttk.Combobox(language_frame, 
                                                textvariable=self.month_language,
                                                values=language_values,
                                                state='readonly',
                                                width=20)
        self.month_language_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        row += 1
        
        # Theme Settings
        theme_frame = ttk.LabelFrame(parent, text="Interface Theme", padding="10")
        theme_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(theme_frame, text="Light Mode", value='light', 
                       command=lambda: self._apply_theme('light')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(theme_frame, text="Dark Mode", value='dark', 
                       command=lambda: self._apply_theme('dark')).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2)
            
    def _check_metadata_tools(self, parent):
        """Check and display available metadata tools."""
        try:
            from metadata_extractor import MetadataExtractor
            extractor = MetadataExtractor()
            
            status_frame = ttk.Frame(parent)
            status_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(status_frame, text="Available Tools:").pack(side=tk.LEFT, padx=(0, 5))
            
            # Hachoir status
            hachoir_color = 'green' if extractor.hachoir_available else 'red'
            hachoir_text = "✓ Hachoir" if extractor.hachoir_available else "✗ Hachoir"
            hachoir_label = tk.Label(status_frame, text=hachoir_text, fg=hachoir_color)
            hachoir_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # ExifTool status
            exiftool_color = 'green' if extractor.exiftool_available else 'red'
            exiftool_text = "✓ ExifTool" if extractor.exiftool_available else "✗ ExifTool"
            exiftool_label = tk.Label(status_frame, text=exiftool_text, fg=exiftool_color)
            exiftool_label.pack(side=tk.LEFT)
            
            # Installation instructions
            if not extractor.hachoir_available or not extractor.exiftool_available:
                install_frame = ttk.Frame(parent)
                install_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
                
                install_btn = ttk.Button(install_frame, text="Install Missing Tools", 
                                        command=self._show_install_instructions)
                install_btn.pack(side=tk.LEFT)
                
        except Exception as e:
            self._log_error(f"Error checking metadata tools: {e}")
            
    def _show_install_instructions(self):
        """Show instructions for installing metadata tools."""
        instructions = """
        Install Missing Metadata Tools:
        
        1. Hachoir (for video metadata):
           pip install hachoir
        
        2. ExifTool (for comprehensive metadata):
           - Download from: https://exiftool.org/
           - Extract to a folder
           - Add to system PATH
        
        Note: Hachoir is optional. ExifTool provides the best results.
        """
        
        messagebox.showinfo("Install Instructions", instructions)
        
    def _toggle_batch_mode(self):
        """Toggle between single and batch mode."""
        if self.batch_mode.get():
            self.source_single_frame.grid_remove()
            self.source_batch_frame.grid()
        else:
            self.source_batch_frame.grid_remove()
            self.source_single_frame.grid()
            
    def _browse_single_source(self):
        """Browse for single source folder."""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_single_entry.delete(0, tk.END)
            self.source_single_entry.insert(0, folder)
            self._scan_folder()
            
    def _add_batch_folder(self):
        """Add a folder to batch processing list."""
        folders = filedialog.askdirectory(
            title="Select Source Folder(s)",
            mustexist=True
        )
        
        if folders:
            if isinstance(folders, tuple):
                for folder in folders:
                    if folder not in self.source_folders:
                        self.source_folders.append(folder)
                        self.source_listbox.insert(tk.END, folder)
            else:
                if folders not in self.source_folders:
                    self.source_folders.append(folders)
                    self.source_listbox.insert(tk.END, folders)
                    
    def _remove_batch_folder(self):
        """Remove selected folder from batch list."""
        selection = self.source_listbox.curselection()
        if selection:
            index = selection[0]
            self.source_listbox.delete(index)
            self.source_folders.pop(index)
            
    def _clear_batch_folders(self):
        """Clear all batch folders."""
        self.source_listbox.delete(0, tk.END)
        self.source_folders.clear()
        
    def _create_filetype_frame(self, parent, row):
        """Create file type selection frame."""
        filetype_frame = ttk.LabelFrame(parent, text="File Types", padding="10")
        filetype_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        filetype_frame.columnconfigure(0, weight=1)
        
        self.filetype_container = ttk.Frame(filetype_frame)
        self.filetype_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(filetype_frame, text="Select All Images", 
                  command=lambda: self._toggle_filetype_category('images', True)).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Button(filetype_frame, text="Select All Videos", 
                  command=lambda: self._toggle_filetype_category('videos', True)).grid(row=1, column=0, sticky=tk.E, pady=2)
                  
        ttk.Button(filetype_frame, text="Deselect All", 
                  command=lambda: self._toggle_all_filetypes(False)).grid(row=2, column=0, sticky=tk.E, pady=2)
                  
    def _toggle_filetype_category(self, category, select):
        """Select/deselect all filetypes in a category."""
        import config
        category_extensions = config.SUPPORTED_EXTENSIONS.get(category, [])
        
        for ext in category_extensions:
            if ext in self.filetype_vars:
                self.filetype_vars[ext].set(select)
                
        self._update_selected_extensions()
        
    def _create_sorting_frame(self, parent, row):
        """Create sorting options frame."""
        sort_frame = ttk.LabelFrame(parent, text="Sorting Options", padding="10")
        sort_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Sort level
        ttk.Label(sort_frame, text="Organization:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(sort_frame, text="Year", 
                       variable=self.sort_level, value=0).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Radiobutton(sort_frame, text="Year/Month", 
                       variable=self.sort_level, value=1).grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Radiobutton(sort_frame, text="Year/Month/Day", 
                       variable=self.sort_level, value=2).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Month names option
        ttk.Checkbutton(sort_frame, text="Use month names", 
                       variable=self.use_month_names).grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        
        import config
        languages = [(code, config.LANGUAGE_DISPLAY_NAMES.get(code, code)) 
                    for code in config.MONTH_NAMES.keys()]
        language_values = [code for code, _ in languages]
        
        self.month_language_combo = ttk.Combobox(sort_frame, 
                                                textvariable=self.month_language,
                                                values=language_values,
                                                state='readonly',
                                                width=15)
        self.month_language_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Dry run option
        ttk.Checkbutton(sort_frame, text="Dry Run (simulate only)", 
                       variable=self.dry_run).grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=5, padx=5)
        
    def _create_progress_frame(self, parent, row):
        """Create progress tracking frame."""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Overall progress
        self.overall_progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.overall_progress_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Folder progress (for batch mode)
        self.folder_progress_frame = ttk.Frame(progress_frame)
        self.folder_progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(self.folder_progress_frame, text="Folder:").pack(side=tk.LEFT)
        self.folder_progress_label = ttk.Label(self.folder_progress_frame, text="")
        self.folder_progress_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Main progress labels
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.current_file_label = ttk.Label(progress_frame, text="")
        self.current_file_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        self.stats_label = ttk.Label(progress_frame, text="")
        self.stats_label.grid(row=4, column=0, sticky=tk.W, pady=2)
        
    def _create_control_buttons(self, parent, row):
        """Create control buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.scan_button = ttk.Button(button_frame, text="Scan Folder(s)", 
                                     command=self._scan_folders)
        self.scan_button.grid(row=0, column=0, padx=5)
        
        self.start_button = ttk.Button(button_frame, text="Start Sorting", 
                                      command=self._start_sorting, state='disabled')
        self.start_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self._stop_processing, state='disabled')
        self.stop_button.grid(row=0, column=2, padx=5)
        
        self.preview_button = ttk.Button(button_frame, text="Preview Structure", 
                                        command=self._preview_structure)
        self.preview_button.grid(row=0, column=3, padx=5)
        
    def _create_log_frame(self, parent, row):
        """Create log display frame."""
        log_frame = ttk.LabelFrame(parent, text="Log", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for styling
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('info', foreground='blue')
        
        # Configure weights for resizing
        parent.rowconfigure(row, weight=1)
        
    def _scan_folders(self):
        """Scan folder(s) for file types."""
        if self.batch_mode.get():
            if not self.source_folders:
                messagebox.showwarning("Warning", "Please add at least one source folder")
                return
            source_paths = self.source_folders
        else:
            source = self.source_single_entry.get()
            if not source or not os.path.exists(source):
                messagebox.showwarning("Warning", "Please select a valid source folder")
                return
            source_paths = [source]
            
        self.scan_button.config(state='disabled')
        self._log_message("Scanning folder(s)...", 'info')
        
        def scan_thread():
            from file_processor import FileProcessor
            import config
            
            all_files = []
            extension_counts = defaultdict(int)
            processor = FileProcessor()
            
            for source in source_paths:
                if not os.path.exists(source):
                    self._log_message(f"Folder not found: {source}", 'error')
                    continue
                    
                self.root.after(0, self._log_message, f"Scanning: {source}", 'info')
                
                # Get all supported extensions
                all_extensions = set(config.SUPPORTED_EXTENSIONS['images'] + 
                                   config.SUPPORTED_EXTENSIONS['videos'])
                
                folder_files, folder_counts = processor.scan_files(source, all_extensions)
                all_files.extend(folder_files)
                
                # Merge extension counts
                for ext, count in folder_counts.items():
                    extension_counts[ext] += count
                    
                self._log_message(f"Found {len(folder_files)} files in {source}", 'info')
            
            # Update UI in main thread
            self.root.after(0, self._update_filetype_list, extension_counts, len(source_paths))
            self.root.after(0, self.scan_button.config, {'state': 'normal'})
            
            self.all_files = all_files
            self._log_message(f"Total files found: {len(all_files)}", 'success')
            
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def _start_sorting(self):
        """Start the sorting process."""
        if not self.selected_extensions:
            messagebox.showwarning("Warning", "Please select at least one file type")
            return
            
        if not self.dest_folder.get():
            messagebox.showwarning("Warning", "Please select a destination folder")
            return
            
        # Get source paths
        if self.batch_mode.get():
            if not self.source_folders:
                messagebox.showwarning("Warning", "Please add at least one source folder")
                return
            source_paths = self.source_folders
        else:
            source = self.source_single_entry.get()
            if not source:
                messagebox.showwarning("Warning", "Please select a source folder")
                return
            source_paths = [source]
            
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
        self.overall_progress_bar['value'] = 0
        self.progress_label.config(text="Starting...")
        
        # Start processing in background thread
        def process_thread():
            from file_processor import FileProcessor
            from batch_processor import BatchProcessor
            
            self.file_processor = FileProcessor(
                progress_callback=self._update_progress,
                error_callback=self._log_error
            )
            
            if self.batch_mode.get() and len(source_paths) > 1:
                # Use batch processor for multiple folders
                self.batch_processor = BatchProcessor(
                    progress_callback=self._update_progress,
                    folder_progress_callback=self._update_folder_progress,
                    error_callback=self._log_error
                )
                
                stats, errors = self.batch_processor.process_folders(
                    source_folders=source_paths,
                    dest_folder=self.dest_folder.get(),
                    file_processor=self.file_processor,
                    sort_level=self.sort_level.get(),
                    use_month_names=self.use_month_names.get(),
                    month_language=self.month_language.get(),
                    dry_run=self.dry_run.get(),
                    selected_extensions=self.selected_extensions
                )
            else:
                # Single folder processing
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
        
    def _update_folder_progress(self, folder_index, total_folders, folder_path):
        """Update folder progress display for batch mode."""
        def update():
            folder_name = os.path.basename(folder_path)
            self.folder_progress_label.config(
                text=f"{folder_name} ({folder_index + 1}/{total_folders})"
            )
            
        self.root.after(0, update)
        
    def _preview_structure(self):
        """Preview the folder structure without copying files."""
        if not self.dest_folder.get():
            messagebox.showwarning("Warning", "Please select a destination folder first")
            return
            
        # Create a preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Structure Preview")
        preview_window.geometry("600x400")
        
        # Sample dates for preview
        sample_dates = [
            (2024, 6, 15),
            (2023, 12, 25),
            (2022, 7, 1),
            (2021, 3, 8)
        ]
        
        import config
        
        # Get current settings
        sort_level = self.sort_level.get()
        use_month_names = self.use_month_names.get()
        month_language = self.month_language.get()
        
        # Build preview structure
        tree_text = f"Destination: {self.dest_folder.get()}\n\n"
        tree_text += "Structure:\n"
        
        for year, month, day in sample_dates:
            path_parts = [self.dest_folder.get(), str(year)]
            
            if sort_level >= 1:
                if use_month_names:
                    month_names = config.MONTH_NAMES.get(month_language, config.MONTH_NAMES['english'])
                    path_parts.append(month_names[month - 1])
                else:
                    path_parts.append(f"{month:02d}")
                    
            if sort_level >= 2:
                path_parts.append(f"{day:02d}")
                
            tree_text += "  " + " → ".join(path_parts[len(path_parts)-sort_level-1:]) + "\n"
        
        # Display preview
        text_widget = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, tree_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(preview_window, text="Close", 
                  command=preview_window.destroy).pack(pady=10)
        
    def _log_message(self, message, tag='info'):
        """Add message to log with styling."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        
    # Keep other methods from original implementation with minor adjustments
    
    def _update_progress(self, current, current_file):
        """Update progress display."""
        def update():
            if hasattr(self, 'file_processor') and self.file_processor:
                total = self.file_processor.total_files
                processed = current + 1
                
                # Update overall progress bar
                progress_percent = (processed / total) * 100 if total > 0 else 0
                self.overall_progress_bar['value'] = progress_percent
                
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
        
    def _stop_processing(self):
        """Stop the current processing."""
        if self.batch_mode.get() and hasattr(self, 'batch_processor'):
            self.batch_processor.stop_processing()
        elif hasattr(self, 'file_processor'):
            self.file_processor.stop_processing()
            
        self._log_message("Processing stopped by user", 'warning')
        self.stop_button.config(state='disabled')
        
        
    def _browse_dest(self):
        """Browse for destination folder."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder.set(folder)
            
    def _scan_folder(self):
        """Scan folder for file types (for single mode)."""
        source = self.source_single_entry.get()
        if not source or not os.path.exists(source):
            messagebox.showwarning("Warning", "Please select a valid source folder")
            return
            
        from file_processor import FileProcessor
        
        self.scan_button.config(state='disabled')
        self._log_message("Scanning folder...", 'info')
        
        def scan_thread():
            import config
            
            # Get all supported extensions
            all_extensions = set(config.SUPPORTED_EXTENSIONS['images'] + 
                               config.SUPPORTED_EXTENSIONS['videos'])
            
            processor = FileProcessor()
            self.all_files, extension_counts = processor.scan_files(source, all_extensions)
            
            # Update UI in main thread
            self.root.after(0, self._update_filetype_list, extension_counts, 1)
            self.root.after(0, self.scan_button.config, {'state': 'normal'})
            
            self._log_message(f"Found {len(self.all_files)} files", 'success')
            
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def _update_filetype_list(self, extension_counts, num_folders=1):
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
                
        # Add category selection buttons
        button_frame = ttk.Frame(self.filetype_container)
        button_frame.grid(row=row+1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame, text="Select All Images", 
                  command=lambda: self._toggle_filetype_category('images', True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Select All Videos", 
                  command=lambda: self._toggle_filetype_category('videos', True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Select All", 
                  command=lambda: self._toggle_all_filetypes(True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Deselect All", 
                  command=lambda: self._toggle_all_filetypes(False)).pack(side=tk.LEFT, padx=2)
                
        self._update_selected_extensions()
        
    def _update_selected_extensions(self):
        """Update set of selected extensions."""
        if hasattr(self, 'filetype_vars'):
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
        if hasattr(self, 'filetype_vars'):
            for var in self.filetype_vars.values():
                var.set(select)
            self._update_selected_extensions()
            
    def _processing_complete(self, stats, errors):
        """Handle completion of processing."""
        # Re-enable controls
        self.scan_button.config(state='normal')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.folder_progress_label.config(text="")
        
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
            
        self._log_message(f"Processing complete. {total_files} files processed.", 'success')
        
    def _log_error(self, error):
        """Add error message to log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] ERROR: {error}\n", 'error')
        self.log_text.see(tk.END)
        
    def _apply_theme(self, theme):
        """Apply light or dark theme."""
        if theme == 'dark':
            bg = '#2b2b2b'
            fg = '#ffffff'
            entry_bg = '#3c3c3c'
            button_bg = '#404040'
            self.log_text.config(bg=entry_bg, fg=fg, insertbackground=fg)
        else:
            bg = '#f0f0f0'
            fg = '#000000'
            entry_bg = '#ffffff'
            button_bg = '#e0e0e0'
            self.log_text.config(bg=entry_bg, fg=fg, insertbackground=fg)
            
        self.root.configure(bg=bg)