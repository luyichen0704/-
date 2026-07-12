"""
Forensic AI Platform - Simple Uninstaller
"""
import os
import sys
import shutil
import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forensic AI Platform Uninstaller")
        self.root.geometry("400x300")
        
        self.path = os.path.dirname(os.path.abspath(__file__))
        
        self.build_ui()
        self.root.mainloop()
    
    def build_ui(self):
        tk.Label(self.root, text="Forensic AI Platform Uninstaller", 
                font=('Arial', 14, 'bold'), bg='#e74c3c', fg='white', pady=10).pack(fill='x')
        
        tk.Label(self.root, text=f"\nInstall location:\n{self.path}", 
                font=('Arial', 10), pady=10).pack()
        
        self.opt_config = tk.BooleanVar(value=False)
        self.opt_cases = tk.BooleanVar(value=False)
        tk.Checkbutton(self.root, text="Delete config files", variable=self.opt_config).pack()
        tk.Checkbutton(self.root, text="Delete case data", variable=self.opt_cases).pack()
        
        tk.Label(self.root, text="\nThis will delete the project files.\nThis cannot be undone!",
                font=('Arial', 10), fg='red', pady=10).pack()
        
        f = tk.Frame(self.root, pady=10)
        f.pack()
        tk.Button(f, text="UNINSTALL", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white', padx=20, command=self.do_uninstall).pack(side='left', padx=10)
        tk.Button(f, text="CANCEL", font=('Arial', 10), padx=15, command=self.root.quit).pack(side='left')
    
    def do_uninstall(self):
        if not messagebox.askyesno("Confirm", "Are you sure you want to uninstall?\n\nThis cannot be undone!"):
            return
        
        try:
            deleted = []
            
            # Delete dirs
            for d in ["agent", "web", "api", "plugins", "skills", "scripts", "knowledge", "data", ".git"]:
                p = os.path.join(self.path, d)
                if os.path.exists(p):
                    shutil.rmtree(p)
                    deleted.append(d)
            
            # Delete files
            for f in ["start.bat", "update.bat", "install.bat", "uninstall.bat", 
                      "create_shortcut.bat", "installer_gui.py", "updater_gui.py", 
                      "uninstaller_gui.py", "requirements.txt", "VERSION",
                      "README.md", "INSTALL.md", ".gitignore", "LICENSE"]:
                p = os.path.join(self.path, f)
                if os.path.exists(p):
                    os.remove(p)
                    deleted.append(f)
            
            if self.opt_config.get():
                p = os.path.join(self.path, "config")
                if os.path.exists(p):
                    shutil.rmtree(p)
                    deleted.append("config")
            
            if self.opt_cases.get():
                p = os.path.join(self.path, "cases")
                if os.path.exists(p):
                    shutil.rmtree(p)
                    deleted.append("cases")
            
            # Delete desktop shortcut
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut = os.path.join(desktop, "Forensic AI Platform.bat")
            if os.path.exists(shortcut):
                os.remove(shortcut)
                deleted.append("desktop shortcut")
            
            messagebox.showinfo("Done", f"Uninstall complete!\n\nDeleted: {', '.join(deleted)}")
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Error", f"Uninstall failed:\n{e}")

if __name__ == "__main__":
    App()
