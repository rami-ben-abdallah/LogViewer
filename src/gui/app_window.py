import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import glob
from datetime import datetime
from collections import Counter
import os

from core.log_filter import LogFilter
from core.log_parser import LogParser
from gui.styles import *
from gui.context_menu import ContextMenuManager
from gui.icon_loader import IconLoader

class AppWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")
        self.root.after(100, self.set_icon)

        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-zoomed', True)

        self.parser = LogParser()
        self.filter = LogFilter()     
        
        # Data storage
        self.original_entries = []
        self.filtered_entries = []
        self.file_paths = []
        self.color_scheme = COLORS
        self.text_colors = TEXT_COLORS
        self.log_text = None  
        
        # Setup
        self.create_widgets()
        self.context_menu = ContextMenuManager(self)   
        self.create_menu_bar()
        self.setup_styles()
        self.configure_text_tags()

        self.update_statistics()

    def set_icon(self):
        icon_loader = IconLoader()
        self._icon = icon_loader.set_application_icon(self.root)    

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Files", command=self.open_files)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_command(label="Close Files", command=self.close_files)
        file_menu.add_separator()
        file_menu.add_command(label="Export TXT", command=self.export_txt)
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Highlight menu
        highlight_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Highlight", menu=highlight_menu)
        
        # Add color options
        if hasattr(self, 'context_menu'):
            for name, color in self.context_menu.highlight_colors:
                highlight_menu.add_command(
                    label=f"Highlight with {name}",
                    command=lambda c=color: self.context_menu.highlight_selected(c),
                )
        
        highlight_menu.add_separator()
        highlight_menu.add_command(
            label="Custom Color...",
            command=self.context_menu.highlight_with_custom_color
        )
        highlight_menu.add_separator()
        highlight_menu.add_command(
            label="Clear Current Highlight",
            command=self.context_menu.clear_highlight
        )
        highlight_menu.add_command(
            label="Clear All Highlights",
            command=self.context_menu.clear_all_highlights,
            accelerator="Ctrl+Shift+H"
        )
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy_selected, accelerator="Ctrl+C")
        edit_menu.add_command(label="Select All", command=self.context_menu.select_all, accelerator="Ctrl+A")
        #edit_menu.add_command(label="Find...", command=self.open_search_dialog, accelerator="Ctrl+F")        
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Stats.TLabel', font=('Arial', 10))
        style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='orange', font=('Arial', 10, 'bold'))
    
    def configure_text_tags(self):
        for level, color in self.text_colors.items():
            self.log_text.tag_config(f'tag_{level}', foreground=color)
    
    def create_widgets(self):       
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame, relief=tk.RAISED, borderwidth=1)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=(1, 3))
        
        ttk.Label(toolbar_frame, text="FILTERS").pack(side=tk.LEFT, padx=(5, 2))
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Level Filter in Toolbar
        ttk.Label(toolbar_frame, text="Levels:").pack(side=tk.LEFT, padx=(5, 2))
        
        self.level_vars = {}
        for level in ['error', 'warning', 'info', 'debug', 'trace']:
            var = tk.BooleanVar(value=True)
            self.level_vars[level] = var
            cb = ttk.Checkbutton(
                toolbar_frame, 
                text=level.title(), 
                variable=var, 
                command=self.apply_filters,
                width=10
            )
            cb.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Timestamp Filter in Toolbar
        ttk.Label(toolbar_frame, text="Timestamp:   From ").pack(side=tk.LEFT, padx=(0, 2))
        self.time_from_var = tk.StringVar()
        self.time_from_entry = ttk.Entry(toolbar_frame, textvariable=self.time_from_var, width=18)
        self.time_from_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar_frame, text="  To ").pack(side=tk.LEFT, padx=(0, 2))
        self.time_to_var = tk.StringVar()
        self.time_to_entry = ttk.Entry(toolbar_frame, textvariable=self.time_to_var, width=18)
        self.time_to_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar_frame, text="Apply", width=6, command=lambda: self.apply_filters()).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Text Search in Toolbar
        ttk.Label(toolbar_frame, text="Text:").pack(side=tk.LEFT, padx=(0, 2))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_var.trace('w', lambda *args: self.apply_filters())
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Clear All Filters button
        ttk.Button(toolbar_frame, text="Clear All", command=self.clear_all_filters, width=8).pack(side=tk.RIGHT, padx=2)
        
        # MAIN DISPLAY AREA
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))
        
        # Text widget with scrollbars - using pack with expand
        text_frame = ttk.Frame(display_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar at the bottom
        x_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vertical scrollbar on the right
        y_scrollbar = ttk.Scrollbar(text_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Main text widget in the center
        self.log_text = tk.Text(
            text_frame, 
            wrap=tk.NONE,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            font=('Courier', 10), 
            bg='white',
            relief=tk.FLAT
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.log_text.yview)
        x_scrollbar.config(command=self.log_text.xview)
        
        # STATUS BAR
        status_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=1, pady=(3, 1))
        
        self.status_left = tk.StringVar(value="Ready")
        self.status_right = tk.StringVar(value="No logs loaded")
        
        status_left_label = ttk.Label(
            status_frame, 
            textvariable=self.status_left, 
            relief=tk.FLAT, 
            anchor=tk.W,
            padding=(5, 2)
        )
        status_left_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        status_right_label = ttk.Label(
            status_frame, 
            textvariable=self.status_right, 
            relief=tk.FLAT, 
            anchor=tk.E,
            padding=(5, 2)
        )
        status_right_label.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    
    def open_files(self):
        files = filedialog.askopenfilenames(
            title="Select log files",
            filetypes=[
                ("Log files", "*.log; *.trc; *.txt"),                
                ("All files", "*.*")
            ]
        )
        if files:
            self.close_files()
            for file in files:
                if file not in self.file_paths:
                    self.file_paths.append(file)
            self.load_logs()
    
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select folder with log files")
        if folder:
            self.close_files()
            log_files = glob.glob(os.path.join(folder, "*.trc")) + \
                        glob.glob(os.path.join(folder, "*.log")) + \
                        glob.glob(os.path.join(folder, "*.txt"))
            for file in log_files:
                if file not in self.file_paths:
                    self.file_paths.append(file)
            self.load_logs()
    
    def close_files(self):
        self.file_paths.clear()
        self.filtered_entries.clear()
        self.original_entries.clear()
        self.clear_log_display()
        self.update_statistics()
        self.status_left.set("Cleared all files")
    
    def load_logs(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select log files first")
            return
        
        self.original_entries = self.parser.parse_files(self.file_paths)
        self.apply_filters()
        self.status_left.set(f"Loaded {len(self.original_entries)} log entries from {len(self.file_paths)} file(s)")
    
    def apply_filters(self):
        if not self.original_entries:
            return
        
        # Get filter criteria from UI
        selected_levels = [
            level for level, var in self.level_vars.items() 
            if var.get()
        ]
        
        # Get time filters
        time_from = None
        time_to = None
        
        if self.time_from_var.get().strip():
            try:
                time_from = datetime.strptime(self.time_from_var.get().strip(), TIME_FORMAT_INPUT)
            except ValueError:
                messagebox.showerror("Invalid Time", "Time 'From' must be in format: YYYY-MM-DD HH:MM:SS")
                return
        
        if self.time_to_var.get().strip():
            try:
                time_to = datetime.strptime(self.time_to_var.get().strip(), TIME_FORMAT_INPUT)
            except ValueError:
                messagebox.showerror("Invalid Time", "Time 'To' must be in format: YYYY-MM-DD HH:MM:SS")
                return
            
        # Get search text            
        search_text = self.search_var.get().lower().strip()
        
        # Use filter service
        self.filtered_entries = self.filter.apply(
            self.original_entries,
            levels=selected_levels,
            time_from=time_from,
            time_to=time_to,
            search_text=search_text
        )
        
        # Update display
        self.display_logs()
        self.update_statistics()

    def clear_all_filters(self):
        # Clear level checkboxes
        for level in self.level_vars:
            self.level_vars[level].set(True)

        # Clear time entries
        self.time_from_var.set('')
        self.time_to_var.set('')

        # Clear search
        self.search_var.set('')

        # Re-apply filters
        self.apply_filters()    
    
    def display_logs(self):
        self.clear_log_display()
        
        if not self.filtered_entries:
            self.log_text.insert(tk.END, "No log entries match the current filters.")
            return
        
        for entry in self.filtered_entries:
            time_str = entry.timestamp.strftime(TIME_FORMAT_DISPLAY)[:-3]
            line = f"[{time_str}] {entry.message} {entry.file_name}:{entry.line_number}\n"
            self.log_text.insert(tk.END, line, f'tag_{entry.level}')
        
        # Scroll to top
        self.log_text.see(1.0)
    
    def clear_log_display(self):
        self.log_text.delete(1.0, tk.END)
    
    def update_statistics(self):
        if not self.original_entries:
            self.status_right.set(f"No logs loaded")
            return
        
        filtered = len(self.filtered_entries)
        
        # Count by level
        level_counts = Counter()
        for entry in self.filtered_entries:
            level_counts[entry.level] += 1
        
        stats_text = f"Showing: {filtered} | "
        for level in ['error', 'warning', 'info', 'debug', 'trace']:
            if level_counts[level]:
                stats_text += f"{level.title()}: {level_counts[level]} | "
        
        self.status_right.set(stats_text.rstrip(' | '))
    
    def export_txt(self):
        if not self.filtered_entries:
            messagebox.showwarning("No Data", "No log entries to export")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        
        if file_path:
            try:
                from core.exporter import export_to_txt
                if export_to_txt(self.filtered_entries, file_path):
                    messagebox.showinfo("Export Complete", f"Successfully exported {len(self.filtered_entries)} entries to:\n{file_path}")
                    self.status_left.set(f"Exported to {os.path.basename(file_path)}")
            
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting file: {str(e)}")
    
    def export_json(self):
        if not self.filtered_entries:
            messagebox.showwarning("No Data", "No log entries to export")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        
        if file_path:
            try:
                from core.exporter import export_to_json
                if export_to_json(self.filtered_entries, file_path):
                    messagebox.showinfo("Export Complete", f"Successfully exported {len(self.filtered_entries)} entries to JSON")
                    self.status_left.set(f"Exported JSON to {os.path.basename(file_path)}")
            
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting JSON: {str(e)}")
    
    def copy_selected(self, event=None):
        try:
            # Check if there's a selection in the text widget
            if self.log_text.tag_ranges("sel"):
                selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                
                # Clear clipboard and append text
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                
                # Show status message
                char_count = len(selected_text)
                line_count = selected_text.count('\n') + 1
                self.status_left.set(f"Copied {char_count} chars ({line_count} lines)")
                
            else:
                # If nothing selected, show message
                self.status_left.set("No text selected to copy")
                
        except tk.TclError:
            # No selection exists
            self.status_left.set("No text selected to copy")
        
        # Return "break" to prevent default behavior when called from shortcut
        return "break"