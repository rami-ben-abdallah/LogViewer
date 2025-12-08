import tkinter as tk

class ContextMenuManager:   
    def __init__(self, app_window):
        self.app = app_window
        self.log_text = app_window.log_text
        
        # Create menus
        self.context_menu = None

        # Highlighting state
        self.highlight_colors = [
            ('Yellow', 'yellow'),
            ('Green', 'lightgreen'),
            ('Blue', 'lightblue'),
            ('Pink', 'lightpink'),
            ('Orange', 'orange')
        ]
        self.current_highlight_tag = None
        
        # Setup all bindings
        self.setup_all()
    
    def setup_all(self):
        self.setup_context_menu()
        self.setup_keyboard_shortcuts()
        
    def setup_context_menu(self):
        # Create the main context menu
        self.context_menu = tk.Menu(self.log_text, tearoff=0)
        
        # Copy section
        self.context_menu.add_command(
            label="Copy", 
            command=self.app.copy_selected,
            accelerator="Ctrl+C"
        )

        # Highlighting submenu
        highlight_menu = tk.Menu(self.context_menu, tearoff=0)
        for name, color in self.highlight_colors:
            highlight_menu.add_command(
                label=name,
                command=lambda c=color: self.highlight_selected(c)
            )
        highlight_menu.add_separator()
        highlight_menu.add_command(
            label="Clear Highlight",
            command=self.clear_highlight
        )
        highlight_menu.add_command(
            label="Clear All Highlights",
            command=self.clear_all_highlights
        )
        
        self.context_menu.add_cascade(
            label="🎨 Highlight",
            menu=highlight_menu
        )
        
        # Selection section
        self.context_menu.add_command(
            label="Select All", 
            command=self.select_all,
            accelerator="Ctrl+A"
        )
        self.context_menu.add_separator()
        
        # Search section (if search is implemented)
        if hasattr(self.app, 'open_search_dialog'):
            self.context_menu.add_command(
                label="Find...", 
                command=self.app.open_search_dialog,
                accelerator="Ctrl+F"
            )
            self.context_menu.add_separator()
        
        # Bind right-click to show menu
        self.log_text.bind("<Button-3>", self.show_context_menu)
    
    def setup_keyboard_shortcuts(self):
        # Text widget shortcuts
        self.log_text.bind("<Control-c>", self.handle_copy)
        self.log_text.bind("<Control-C>", self.handle_copy)

        # Highlight shortcuts
        self.log_text.bind("<Control-h>", lambda e: self.highlight_selected())
        self.log_text.bind("<Control-H>", lambda e: self.highlight_selected())
        self.log_text.bind("<Control-Shift-h>", lambda e: self.clear_all_highlights())
        self.log_text.bind("<Control-Shift-H>", lambda e: self.clear_all_highlights())

        # Select all
        self.log_text.bind("<Control-a>", lambda e: self.select_all())
        self.log_text.bind("<Control-A>", lambda e: self.select_all())        
        
        # Make text widget focusable on click
        self.log_text.bind("<Button-1>", lambda e: self.log_text.focus_set())
        
        # Global application shortcuts
        self.app.root.bind("<Control-o>", lambda e: self.app.add_files())
        self.app.root.bind("<Control-O>", lambda e: self.app.add_files())
        self.app.root.bind("<Control-l>", lambda e: self.app.load_logs())
        self.app.root.bind("<Control-L>", lambda e: self.app.load_logs())
        
        # If you have a filter focus shortcut
        self.app.root.bind("<Control-f>", self.focus_search_filter)
        self.app.root.bind("<Control-F>", self.focus_search_filter)
    
    # ===== CONTEXT MENU HANDLERS =====
    
    def show_context_menu(self, event):
        """Display context menu at cursor position"""
        try:
            # Only show if there's text selected
            if self.log_text.tag_ranges("sel"):
                self.context_menu.tk_popup(event.x_root, event.y_root)
            else:
                # Show simplified menu when no selection
                self.show_no_selection_menu(event)
        finally:
            if self.context_menu:
                self.context_menu.grab_release()
    
    def show_no_selection_menu(self, event):
        """Show context menu when no text is selected"""
        no_selection_menu = tk.Menu(self.log_text, tearoff=0)
        no_selection_menu.add_command(
            label="Select All", 
            command=self.select_all
        )
        no_selection_menu.tk_popup(event.x_root, event.y_root)
        no_selection_menu.grab_release()
    
    # ===== ACTION METHODS =====
    
    def handle_copy(self, event=None):
        """Handle copy with keyboard shortcut"""
        self.app.copy_selected()
        return "break"  # Prevent default behavior
    
    def select_all(self):
        """Select all text in the widget"""
        self.log_text.tag_add('sel', '1.0', 'end')
        self.log_text.mark_set(tk.INSERT, '1.0')
        self.log_text.see('1.0')
    
    def focus_search_filter(self, event=None):
        """Set focus to the search filter entry"""
        if hasattr(self.app, 'search_entry'):
            self.app.search_entry.focus_set()
            self.app.search_entry.select_range(0, tk.END)
        return "break"

    def highlight_selected(self, color="yellow"):
        """Highlight the currently selected text"""
        if not self.log_text.tag_ranges("sel"):
            self.app.status_left.set("No text selected to highlight")
            return
        
        # Create a unique tag name for this highlight
        import time
        tag_name = f"highlight_{int(time.time() * 1000)}"
        
        # Configure the tag with the chosen color
        self.log_text.tag_config(tag_name, background=color)
        
        # Apply the tag to the selected text
        self.log_text.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
        
        # Store this as the current highlight tag
        self.current_highlight_tag = tag_name
        
        # Update status
        self.app.status_left.set(f"Text highlighted with {color}")
        
        # Auto-clear selection after highlighting
        self.log_text.tag_remove("sel", "1.0", "end")
    
    def highlight_with_custom_color(self):
        """Open color picker for custom highlight color"""
        # Simple color dialog
        from tkinter import colorchooser
        
        color = colorchooser.askcolor(
            title="Choose highlight color",
            initialcolor="yellow"
        )
        
        if color[1]:  # User selected a color
            self.highlight_selected(color[1])
    
    def clear_highlight(self):
        """Remove highlight from currently selected text"""
        if not self.log_text.tag_ranges("sel"):
            self.app.status_left.set("Select text to clear highlight")
            return
        
        # Find all highlight tags in the selection
        selection_start = self.log_text.index(tk.SEL_FIRST)
        selection_end = self.log_text.index(tk.SEL_LAST)
        
        # Get all tags in the selection
        tags_in_selection = set()
        pos = selection_start
        
        while self.log_text.compare(pos, "<", selection_end):
            tags = self.log_text.tag_names(pos)
            # Filter for highlight tags
            highlight_tags = [t for t in tags if t.startswith("highlight_")]
            tags_in_selection.update(highlight_tags)
            pos = self.log_text.index(f"{pos}+1c")
        
        # Remove all highlight tags from the selection
        for tag in tags_in_selection:
            self.log_text.tag_remove(tag, selection_start, selection_end)
        
        if tags_in_selection:
            self.app.status_left.set(f"Cleared {len(tags_in_selection)} highlight(s)")
        else:
            self.app.status_left.set("No highlights in selection")
    
    def clear_all_highlights(self):
        """Remove all highlights from the entire document"""
        # Find all highlight tags
        all_tags = self.log_text.tag_names()
        highlight_tags = [t for t in all_tags if t.startswith("highlight_")]
        
        # Remove each highlight tag
        for tag in highlight_tags:
            self.log_text.tag_remove(tag, "1.0", "end")
        
        self.app.status_left.set(f"Cleared all highlights ({len(highlight_tags)} removed)")
    
    def get_all_highlights(self):
        """Return information about all highlights in the document"""
        highlights = []
        all_tags = self.log_text.tag_names()
        highlight_tags = [t for t in all_tags if t.startswith("highlight_")]
        
        for tag in highlight_tags:
            # Get tag configuration
            bg_color = self.log_text.tag_cget(tag, "background")
            
            # Find all ranges with this tag
            ranges = []
            start_idx = "1.0"
            
            while True:
                # Find next occurrence of this tag
                start_pos = self.log_text.tag_nextrange(tag, start_idx)
                if not start_pos:
                    break
                
                # Get the text at this range
                text = self.log_text.get(start_pos[0], start_pos[1])
                ranges.append({
                    'start': start_pos[0],
                    'end': start_pos[1],
                    'text': text[:50] + "..." if len(text) > 50 else text
                })
                
                # Move to next position
                start_idx = start_pos[1]
            
            if ranges:
                highlights.append({
                    'tag': tag,
                    'color': bg_color,
                    'ranges': ranges,
                    'count': len(ranges)
                })
        
        return highlights        