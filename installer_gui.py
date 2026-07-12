"""
Forensic AI Platform - Simple Reliable Installer
No complex GUI, just works
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
import threading

def check_cmd(cmd):
    """Check if command exists"""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        return False

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forensic AI Platform Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.path = tk.StringVar(value=r"D:\forensic-ai-platform")
        self.log_text = None
        self.btn = None
        
        self.build_ui()
        self.root.mainloop()
    
    def build_ui(self):
        # Title
        tk.Label(self.root, text="Forensic AI Platform", font=('Arial', 18, 'bold'), 
                bg='#2c3e50', fg='white', pady=10).pack(fill='x')
        
        # Path
        f1 = tk.Frame(self.root, pady=10)
        f1.pack(fill='x', padx=20)
        tk.Label(f1, text="Install Path:", font=('Arial', 10)).pack(anchor='w')
        f1b = tk.Frame(f1)
        f1b.pack(fill='x')
        tk.Entry(f1b, textvariable=self.path, width=40).pack(side='left', padx=(0,5))
        tk.Button(f1b, text="Browse", command=self.browse).pack(side='left')
        
        # Options
        self.opt_deps = tk.BooleanVar(value=True)
        self.opt_tools = tk.BooleanVar(value=True)
        tk.Checkbutton(f1, text="Install Python dependencies", variable=self.opt_deps).pack(anchor='w')
        tk.Checkbutton(f1, text="Install forensic tools (scoop)", variable=self.opt_tools).pack(anchor='w')
        
        # Log
        self.log_text = tk.Text(self.root, height=12, width=55, font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, padx=20, pady=5)
        
        # Buttons
        f2 = tk.Frame(self.root, pady=10)
        f2.pack(fill='x', padx=20)
        self.btn = tk.Button(f2, text="INSTALL", font=('Arial', 12, 'bold'),
                            bg='#27ae60', fg='white', padx=30, command=self.do_install)
        self.btn.pack(side='left')
        tk.Button(f2, text="EXIT", font=('Arial', 10), padx=15, command=self.root.quit).pack(side='right')
    
    def browse(self):
        d = filedialog.askdirectory()
        if d:
            self.path.set(os.path.join(d, "forensic-ai-platform"))
    
    def log(self, msg):
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.root.update()
    
    def do_install(self):
        self.btn.config(state='disabled')
        threading.Thread(target=self._install, daemon=True).start()
    
    def _install(self):
        p = self.path.get()
        
        try:
            self.log("=" * 40)
            self.log("Starting installation...")
            self.log(f"Path: {p}")
            self.log("=" * 40)
            
            # 1. Create dir
            self.log("\n[1/3] Creating directory...")
            os.makedirs(p, exist_ok=True)
            self.log("  OK")
            
            # 2. Download
            self.log("\n[2/3] Downloading project...")
            
            # Check git
            if not check_cmd("git --version"):
                self.log("  Git not found!")
                self.log("")
                self.log("  SOLUTION: Download manually")
                self.log("  1. Go to: https://github.com/luyichen0704/forensic-ai-platform")
                self.log("  2. Click Code -> Download ZIP")
                self.log(f"  3. Extract to: {p}")
                self.log("")
                self.log("  Or install Git: https://git-scm.com/downloads")
                messagebox.showerror("Error", "Git not installed!\n\nDownload ZIP manually from GitHub.")
                return
            
            if os.path.exists(os.path.join(p, '.git')):
                self.log("  Updating...")
                subprocess.run(["git", "pull"], capture_output=True, cwd=p)
            else:
                self.log("  Cloning...")
                r = subprocess.run(["git", "clone", "https://github.com/luyichen0704/forensic-ai-platform.git", "."],
                                  capture_output=True, text=True, cwd=p)
                if r.returncode != 0:
                    self.log(f"  Clone failed: {r.stderr[:100]}")
                    self.log("  Try downloading ZIP manually")
                    return
            self.log("  OK")
            
            # 3. Python deps
            if self.opt_deps.get():
                self.log("\n[3/3] Python dependencies...")
                req = os.path.join(p, "requirements.txt")
                if os.path.exists(req):
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", req, "-q"], capture_output=True)
                    self.log("  OK")
                else:
                    self.log("  requirements.txt not found")
            
            # Done
            self.log("\n" + "=" * 40)
            self.log("INSTALLATION COMPLETE!")
            self.log("=" * 40)
            self.log(f"\nPath: {p}")
            self.log("\nNext: Run start.bat")
            
            messagebox.showinfo("Success", f"Installed to:\n{p}\n\nRun start.bat to begin!")
            
        except Exception as e:
            self.log(f"\nERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn.config(state='normal')

if __name__ == "__main__":
    App()
