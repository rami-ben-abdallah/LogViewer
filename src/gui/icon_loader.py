import os
import sys

class IconLoader:   
    def __init__(self):
        self.icon_paths = self.get_all_possible_paths()
    
    def get_pyinstaller_path(self):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, "assets", "icon.png")
        return None
    
    def get_development_paths(self):
        return [
            "assets/icon.png",
            os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png"),
            os.path.join(os.getcwd(), "assets", "icon.png"),
        ]
    
    def get_all_possible_paths(self):
        paths = []
        
        pyinstaller_path = self.get_pyinstaller_path()
        if pyinstaller_path:
            paths.append(pyinstaller_path)
        
        paths.extend(self.get_development_paths())
        
        return paths
    
    def find_icon(self):
        for icon_path in self.icon_paths:
            if os.path.exists(icon_path):
                return icon_path
        return None
    
    def load_icon(self, icon_path):
        try:
            from tkinter import PhotoImage
            return PhotoImage(file=icon_path)
        except Exception as e:
            print(f"Error loading icon: {e}")
            return None
    
    def set_application_icon(self, root_window):
        icon_path = self.find_icon()
        
        if not icon_path:
            print("Icon not found in any location")
            return None
        
        icon = self.load_icon(icon_path)
        
        if icon:
            root_window.iconphoto(True, icon)
            print(f"Icon loaded: {icon_path}")
            return icon
        
        return None