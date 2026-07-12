"""
Forensic AI Platform - Installer with Tool Detection
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import shutil

class Installer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forensic AI Platform - Installer")
        self.root.geometry("650x600")
        
        self.install_path = tk.StringVar(value=r"D:\forensic-ai-platform")
        self.opt_project = tk.BooleanVar(value=True)
        self.opt_deps = tk.BooleanVar(value=True)
        self.opt_tools = tk.BooleanVar(value=True)
        
        # Tool status
        self.tool_status = {}
        
        self.create_ui()
        self.check_tools_on_start()
    
    def create_ui(self):
        # Title
        tk.Label(self.root, text="Forensic AI Platform Installer", 
                font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white', pady=10).pack(fill='x')
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tab 1: Install
        tab1 = tk.Frame(self.notebook, padx=20, pady=10)
        self.notebook.add(tab1, text="  Install  ")
        
        # Step 1: Path
        tk.Label(tab1, text="Step 1: Install Path", font=('Arial', 11, 'bold')).pack(anchor='w')
        path_frame = tk.Frame(tab1)
        path_frame.pack(fill='x', pady=5)
        tk.Entry(path_frame, textvariable=self.install_path, width=45).pack(side='left', padx=(0,10))
        tk.Button(path_frame, text="Browse", command=self.browse).pack(side='left')
        
        quick = tk.Frame(tab1)
        quick.pack(anchor='w', pady=5)
        for d in ['D', 'E', 'F']:
            if os.path.exists(f"{d}:\\"):
                tk.Button(quick, text=f"{d}:\\forensic-ai-platform",
                         command=lambda x=d: self.install_path.set(f"{x}:\\forensic-ai-platform")).pack(side='left', padx=3)
        
        ttk.Separator(tab1, orient='horizontal').pack(fill='x', pady=10)
        
        # Step 2: Options
        tk.Label(tab1, text="Step 2: Components", font=('Arial', 11, 'bold')).pack(anchor='w')
        tk.Checkbutton(tab1, text="Project Files (code, web UI, API)", variable=self.opt_project).pack(anchor='w')
        tk.Checkbutton(tab1, text="Python Dependencies", variable=self.opt_deps).pack(anchor='w')
        tk.Checkbutton(tab1, text="Forensic Tools (skip installed)", variable=self.opt_tools).pack(anchor='w')
        
        ttk.Separator(tab1, orient='horizontal').pack(fill='x', pady=10)
        
        # Step 3: Progress
        tk.Label(tab1, text="Step 3: Progress", font=('Arial', 11, 'bold')).pack(anchor='w')
        self.progress = ttk.Progressbar(tab1, mode='determinate', length=450)
        self.progress.pack(fill='x', pady=5)
        self.status = tk.Label(tab1, text="Ready", anchor='w')
        self.status.pack(fill='x')
        
        self.log = tk.Text(tab1, height=12, width=65, font=('Consolas', 9))
        self.log.pack(fill='both', expand=True, pady=5)
        
        # Tab 2: Tool Status
        tab2 = tk.Frame(self.notebook, padx=20, pady=10)
        self.notebook.add(tab2, text="  Tool Status  ")
        
        tk.Label(tab2, text="Installed Tools", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0,10))
        
        # Tool list frame
        self.tool_list_frame = tk.Frame(tab2)
        self.tool_list_frame.pack(fill='both', expand=True)
        
        tk.Button(tab2, text="Refresh Status", command=self.check_tools_on_start).pack(pady=10)
        
        # Bottom buttons
        btn_frame = tk.Frame(self.root, bg='#f0f0f0', pady=8)
        btn_frame.pack(fill='x', side='bottom')
        
        self.install_btn = tk.Button(btn_frame, text="START INSTALL", font=('Arial', 12, 'bold'),
                                    bg='#27ae60', fg='white', padx=20, pady=5, command=self.start_install)
        self.install_btn.pack(side='left', padx=20)
        
        tk.Button(btn_frame, text="EXIT", font=('Arial', 11), bg='#95a5a6', fg='white',
                 padx=15, pady=5, command=self.root.quit).pack(side='right', padx=20)
    
    def check_tools_on_start(self):
        """Check which tools are already installed"""
        # Clear tool list
        for widget in self.tool_list_frame.winfo_children():
            widget.destroy()
        
        tools = {
            "Git": {"cmd": "git --version", "required": True},
            "Python": {"cmd": "python --version", "required": True},
            "pip": {"cmd": "pip --version", "required": True},
            "Scoop": {"cmd": "scoop --version", "required": False},
            "sleuthkit": {"cmd": "fls -V", "required": False},
            "wireshark/tshark": {"cmd": "tshark --version", "required": False},
            "yara": {"cmd": "yara --version", "required": False},
            "hashcat": {"cmd": "hashcat --version", "required": False},
            "7zip": {"cmd": "7z", "required": False},
            "exiftool": {"cmd": "exiftool -ver", "required": False},
            "ffmpeg": {"cmd": "ffmpeg -version", "required": False},
            "sqlite3": {"cmd": "sqlite3 --version", "required": False},
            "openssl": {"cmd": "openssl version", "required": False},
            "jadx": {"cmd": "jadx --version", "required": False},
            "radare2": {"cmd": "r2 -v", "required": False},
        }
        
        # Header
        header = tk.Frame(self.tool_list_frame)
        header.pack(fill='x')
        tk.Label(header, text="Tool", font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        tk.Label(header, text="Status", font=('Arial', 10, 'bold'), width=15).pack(side='left')
        tk.Label(header, text="Required", font=('Arial', 10, 'bold'), width=10).pack(side='left')
        
        ttk.Separator(self.tool_list_frame, orient='horizontal').pack(fill='x', pady=2)
        
        for name, info in tools.items():
            row = tk.Frame(self.tool_list_frame)
            row.pack(fill='x', pady=1)
            
            tk.Label(row, text=name, width=20, anchor='w').pack(side='left')
            
            # Check if installed
            installed = self._check_tool(info["cmd"])
            self.tool_status[name] = installed
            
            if installed:
                tk.Label(row, text="✅ Installed", fg='green', width=15).pack(side='left')
            else:
                tk.Label(row, text="❌ Missing", fg='red', width=15).pack(side='left')
            
            req_text = "Yes" if info["required"] else "Optional"
            tk.Label(row, text=req_text, width=10).pack(side='left')
    
    def _check_tool(self, cmd):
        """Check if a tool is installed"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.install_path.set(os.path.join(path, "forensic-ai-platform"))
    
    def log_msg(self, msg):
        self.root.after(0, lambda: self._do_log(msg))
    
    def _do_log(self, msg):
        self.log.insert('end', msg + '\n')
        self.log.see('end')
    
    def update_ui(self, text, progress):
        self.root.after(0, lambda: self.status.configure(text=text))
        self.root.after(0, lambda: self.progress.configure(value=progress))
    
    def start_install(self):
        if not self.install_path.get():
            messagebox.showerror("Error", "Select install path!")
            return
        if not messagebox.askyesno("Confirm", f"Install to:\n{self.install_path.get()}\n\nContinue?"):
            return
        self.install_btn.configure(state='disabled')
        self.notebook.select(0)  # Switch to install tab
        threading.Thread(target=self._install, daemon=True).start()
    
    def _install(self):
        path = self.install_path.get()
        try:
            self.log_msg("=" * 50)
            self.log_msg("Starting installation...")
            self.log_msg(f"Path: {path}")
            self.log_msg("=" * 50)
            
            # Check Git
            self.update_ui("Checking Git...", 5)
            if not self.tool_status.get("Git"):
                self.log_msg("\nERROR: Git not installed!")
                self.log_msg("Please install Git from: https://git-scm.com/downloads")
                self.log_msg("Or download ZIP manually from GitHub")
                messagebox.showerror("Error", "Git not installed!\n\nInstall Git or download ZIP manually.")
                return
            
            self.log_msg("\n✓ Git installed")
            
            # Create dir
            self.update_ui("Creating directory...", 10)
            self.log_msg("\n[1/4] Creating directory...")
            os.makedirs(path, exist_ok=True)
            self.log_msg("  ✓ Directory created")
            
            # Download project
            if self.opt_project.get():
                self.update_ui("Downloading project...", 20)
                self.log_msg("\n[2/4] Downloading project...")
                
                if os.path.exists(os.path.join(path, '.git')):
                    self.log_msg("  Existing project found, updating...")
                    r = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd=path)
                    self.log_msg(f"  ✓ Updated: {r.stdout.strip()[:50]}")
                else:
                    self.log_msg("  Cloning repository...")
                    r = subprocess.run(["git", "clone", "https://github.com/luyichen0704/forensic-ai-platform.git", "."],
                                      capture_output=True, text=True, cwd=path)
                    if r.returncode != 0:
                        raise Exception(f"Git clone failed: {r.stderr[:100]}")
                    self.log_msg("  ✓ Project downloaded")
            
            # Install Python deps
            if self.opt_deps.get():
                self.update_ui("Installing Python dependencies...", 40)
                self.log_msg("\n[3/4] Python dependencies...")
                
                if self.tool_status.get("pip"):
                    req = os.path.join(path, "requirements.txt")
                    if os.path.exists(req):
                        self.log_msg("  Installing packages...")
                        r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", req, "-q"], 
                                          capture_output=True, text=True)
                        if r.returncode == 0:
                            self.log_msg("  ✓ Dependencies installed")
                        else:
                            self.log_msg(f"  ⚠ Some failed: {r.stderr[:100]}")
                    else:
                        self.log_msg("  ⚠ requirements.txt not found")
                else:
                    self.log_msg("  ⚠ pip not available, skipping")
            
            # Install forensic tools
            if self.opt_tools.get():
                self.update_ui("Installing forensic tools...", 60)
                self.log_msg("\n[4/4] Forensic tools...")
                
                # Install Scoop if needed
                if not self.tool_status.get("Scoop"):
                    self.log_msg("  Installing Scoop...")
                    subprocess.run(["powershell", "-Command", "iwr -useb get.scoop.sh | iex"], 
                                  capture_output=True, shell=True)
                    self.log_msg("  ✓ Scoop installed")
                else:
                    self.log_msg("  ✓ Scoop already installed")
                
                # Install tools - skip if already installed
                tools_to_install = [
                    ("sleuthkit", "sleuthkit"),
                    ("wireshark/tshark", "wireshark"),
                    ("yara", "yara"),
                    ("hashcat", "hashcat"),
                    ("7zip", "7zip"),
                    ("exiftool", "exiftool"),
                    ("ffmpeg", "ffmpeg"),
                    ("sqlite3", "sqlite"),
                    ("openssl", "openssl"),
                    ("jadx", "jadx"),
                    ("radare2", "radare2"),
                ]
                
                total = len(tools_to_install)
                for i, (name, pkg) in enumerate(tools_to_install):
                    progress = 60 + (i / total) * 35
                    self.update_ui(f"Checking {name}...", progress)
                    
                    # Skip if already installed
                    if self.tool_status.get(name):
                        self.log_msg(f"  ✓ {name} - already installed, skipping")
                        continue
                    
                    self.log_msg(f"  Installing {name}...")
                    scoop = os.path.expanduser("~/scoop/shims/scoop.cmd")
                    if not os.path.exists(scoop):
                        scoop = "scoop"
                    
                    r = subprocess.run([scoop, "install", pkg], capture_output=True, text=True)
                    if r.returncode == 0:
                        self.log_msg(f"    ✓ {name} installed")
                    else:
                        self.log_msg(f"    ⚠ {name} install failed (may already exist)")
                
                self.log_msg("  ✓ Tool installation complete")
            
            # Done
            self.update_ui("Complete!", 100)
            self.log_msg("\n" + "=" * 50)
            self.log_msg("✓ INSTALLATION COMPLETE!")
            self.log_msg("=" * 50)
            self.log_msg(f"\nInstalled to: {path}")
            self.log_msg("\nNext steps:")
            self.log_msg("1. Edit config/llm_config.json (add API key)")
            self.log_msg("2. Run start.bat to begin")
            
            messagebox.showinfo("Success", f"Installation complete!\n\nPath: {path}\n\nRun start.bat to begin!")
            
        except Exception as e:
            self.log_msg(f"\n❌ ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.root.after(0, lambda: self.install_btn.configure(state='normal'))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    Installer().run()
