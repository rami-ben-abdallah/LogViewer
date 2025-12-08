from gui.app_window import AppWindow
import tkinter as tk

def main():
    root = tk.Tk()
    AppWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()