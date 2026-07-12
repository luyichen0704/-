"""
Forensic AI Platform - Simple Updater
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading

def check_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        return False

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forensic AI Platform Updater")
        self.root.geometry("450x300")
        
        self.build_ui()
        self.check_update()
        self.root.mainloop()
    
    def build_ui(self):
        tk.Label(self.root, text="Forensic AI Platform Updater", 
                font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white', pady=10).pack(fill='x')
        
        self.status = tk.Label(self.root, text="Checking for updates...", font=('Arial', 11), pady=10)
        self.status.pack()
        
        self.log_text = tk.Text(self.root, height=8, width=50, font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, padx=20, pady=5)
        
        f = tk.Frame(self.root, pady=10)
        f.pack(fill='x', padx=20)
        self.btn = tk.Button(f, text="UPDATE", font=('Arial', 11, 'bold'),
                            bg='#27ae60', fg='white', padx=20, command=self.do_update)
        self.btn.pack(side='left')
        tk.Button(f, text="EXIT", font=('Arial', 10), padx=15, command=self.root.quit).pack(side='right')
    
    def log(self, msg):
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
    
    def check_update(self):
        if not check_cmd("git --version"):
            self.status.config(text="Git not installed!")
            self.log("Git not found. Cannot check updates.")
            return
        
        r = subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True, cwd=os.getcwd())
        if r.returncode != 0:
            self.status.config(text="Cannot connect to GitHub")
            self.log("Failed to fetch updates")
            return
        
        r = subprocess.run(["git", "rev-parse", "HEAD", "origin/main"], capture_output=True, text=True, cwd=os.getcwd())
        lines = r.stdout.strip().split('\n')
        if len(lines) == 2 and lines[0] == lines[1]:
            self.status.config(text="Already up to date!")
            self.log("No updates available")
            self.btn.config(state='disabled')
        else:
            self.status.config(text="Update available!")
            self.log("New version found. Click UPDATE to download.")
    
    def do_update(self):
        self.btn.config(state='disabled')
        threading.Thread(target=self._update, daemon=True).start()
    
    def _update(self):
        self.log("\nUpdating...")
        r = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, cwd=os.getcwd())
        if r.returncode == 0:
            self.log(r.stdout)
            self.log("\nUpdate complete!")
            self.status.config(text="Update complete!")
            messagebox.showinfo("Success", "Update complete!")
        else:
            self.log(f"Error: {r.stderr}")
            messagebox.showerror("Error", "Update failed!")
        self.btn.config(state='normal')

if __name__ == "__main__":
    App()
