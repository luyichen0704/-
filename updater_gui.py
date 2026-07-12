"""
一键更新工具 - GUI界面
双击运行，点击按钮即可更新
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path

class UpdaterGUI:
    """更新器GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("取证AI平台 - 一键更新")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 设置图标和样式
        self.root.configure(bg='#f0f0f0')
        
        self.setup_ui()
        self.check_update_on_start()
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🔍 取证AI平台 - 自动更新",
            font=('微软雅黑', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        ).pack(expand=True)
        
        # 主内容区
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 版本信息
        version_frame = tk.LabelFrame(
            main_frame,
            text="版本信息",
            font=('微软雅黑', 10),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        version_frame.pack(fill='x', pady=(0, 15))
        
        self.current_version_label = tk.Label(
            version_frame,
            text="当前版本: 检测中...",
            font=('微软雅黑', 10),
            bg='#f0f0f0',
            anchor='w'
        )
        self.current_version_label.pack(fill='x')
        
        self.remote_version_label = tk.Label(
            version_frame,
            text="最新版本: 检测中...",
            font=('微软雅黑', 10),
            bg='#f0f0f0',
            anchor='w'
        )
        self.remote_version_label.pack(fill='x')
        
        self.status_label = tk.Label(
            version_frame,
            text="状态: 等待检查...",
            font=('微软雅黑', 10),
            bg='#f0f0f0',
            anchor='w'
        )
        self.status_label.pack(fill='x')
        
        # 更新日志
        log_frame = tk.LabelFrame(
            main_frame,
            text="更新内容",
            font=('微软雅黑', 10),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        log_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=('Consolas', 9),
            wrap='word',
            state='disabled'
        )
        self.log_text.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # 按钮区
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x')
        
        # 检查更新按钮
        self.check_btn = tk.Button(
            button_frame,
            text="🔄 检查更新",
            font=('微软雅黑', 11),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.check_update
        )
        self.check_btn.pack(side='left', padx=(0, 10))
        
        # 一键更新按钮
        self.update_btn = tk.Button(
            button_frame,
            text="⬇️ 一键更新",
            font=('微软雅黑', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.do_update,
            state='disabled'
        )
        self.update_btn.pack(side='left', padx=(0, 10))
        
        # 关闭按钮
        self.close_btn = tk.Button(
            button_frame,
            text="关闭",
            font=('微软雅黑', 11),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.root.quit
        )
        self.close_btn.pack(side='right')
        
        # 进度条
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate'
        )
        self.progress.pack(fill='x', pady=(10, 0))
    
    def get_project_dir(self):
        """获取项目目录"""
        # 如果是打包后的exe
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        # 如果是脚本
        return os.path.dirname(os.path.abspath(__file__))
    
    def get_current_version(self):
        """获取当前版本"""
        version_file = os.path.join(self.get_project_dir(), "VERSION")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        return "未知"
    
    def run_git_command(self, cmd):
        """执行Git命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.get_project_dir(),
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令超时"
        except Exception as e:
            return False, "", str(e)
    
    def check_update_on_start(self):
        """启动时检查更新"""
        threading.Thread(target=self._check_update_thread, daemon=True).start()
    
    def check_update(self):
        """检查更新按钮"""
        self.check_btn.configure(state='disabled')
        threading.Thread(target=self._check_update_thread, daemon=True).start()
    
    def _check_update_thread(self):
        """检查更新线程"""
        self.root.after(0, lambda: self.status_label.configure(text="状态: 正在检查更新..."))
        self.root.after(0, lambda: self.progress.start())
        
        # fetch最新信息
        success, stdout, stderr = self.run_git_command(["git", "fetch", "origin"])
        
        if not success:
            self.root.after(0, lambda: self.status_label.configure(text="状态: 检查失败 - 请检查网络"))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.check_btn.configure(state='normal'))
            return
        
        # 获取当前版本
        current_version = self.get_current_version()
        
        # 获取远程版本
        success, remote_version, _ = self.run_git_command(["git", "show", "origin/main:VERSION"])
        remote_version = remote_version.strip() if success else "未知"
        
        # 更新UI
        self.root.after(0, lambda: self.current_version_label.configure(text=f"当前版本: {current_version}"))
        self.root.after(0, lambda: self.remote_version_label.configure(text=f"最新版本: {remote_version}"))
        
        # 检查是否有更新
        if current_version == remote_version:
            self.root.after(0, lambda: self.status_label.configure(text="状态: ✅ 已是最新版本!"))
            self.root.after(0, lambda: self.update_btn.configure(state='disabled'))
        else:
            self.root.after(0, lambda: self.status_label.configure(text="状态: 🔄 发现新版本!"))
            self.root.after(0, lambda: self.update_btn.configure(state='normal'))
            
            # 获取更新日志
            success, log, _ = self.run_git_command(
                ["git", "log", "HEAD..origin/main", "--oneline", "-10"]
            )
            if success and log:
                self.root.after(0, lambda: self._set_log_text(log))
        
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.check_btn.configure(state='normal'))
    
    def _set_log_text(self, text):
        """设置日志文本"""
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.insert('1.0', text)
        self.log_text.configure(state='disabled')
    
    def do_update(self):
        """执行更新"""
        # 确认更新
        if not messagebox.askyesno("确认更新", "确定要更新到最新版本吗？\n\n本地修改会被自动保存（git stash）。"):
            return
        
        self.update_btn.configure(state='disabled')
        self.check_btn.configure(state='disabled')
        threading.Thread(target=self._update_thread, daemon=True).start()
    
    def _update_thread(self):
        """更新线程"""
        self.root.after(0, lambda: self.status_label.configure(text="状态: 正在更新..."))
        self.root.after(0, lambda: self.progress.start())
        self.root.after(0, lambda: self._set_log_text("正在检查本地修改...\n"))
        
        # 检查本地修改
        success, status, _ = self.run_git_command(["git", "status", "--porcelain"])
        has_changes = bool(status.strip())
        
        if has_changes:
            self.root.after(0, lambda: self._append_log("检测到本地修改，正在暂存...\n"))
            self.run_git_command(["git", "stash"])
            self.root.after(0, lambda: self._append_log("本地修改已暂存\n"))
        
        # 执行更新
        self.root.after(0, lambda: self._append_log("\n正在拉取最新代码...\n"))
        success, stdout, stderr = self.run_git_command(["git", "pull", "origin", "main"])
        
        if success:
            self.root.after(0, lambda: self._append_log("✅ 代码更新成功!\n"))
            
            # 更新依赖
            self.root.after(0, lambda: self._append_log("\n正在更新依赖...\n"))
            req_file = os.path.join(self.get_project_dir(), "requirements.txt")
            if os.path.exists(req_file):
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", req_file, "-q"],
                    capture_output=True,
                    cwd=self.get_project_dir()
                )
                self.root.after(0, lambda: self._append_log("✅ 依赖更新完成!\n"))
            
            # 恢复本地修改
            if has_changes:
                self.root.after(0, lambda: self._append_log("\n正在恢复本地修改...\n"))
                success, _, _ = self.run_git_command(["git", "stash", "pop"])
                if success:
                    self.root.after(0, lambda: self._append_log("✅ 本地修改已恢复\n"))
                else:
                    self.root.after(0, lambda: self._append_log("⚠️ 恢复本地修改时有冲突，请手动解决\n"))
            
            # 更新版本显示
            new_version = self.get_current_version()
            self.root.after(0, lambda: self.current_version_label.configure(text=f"当前版本: {new_version}"))
            self.root.after(0, lambda: self.status_label.configure(text="状态: ✅ 更新完成!"))
            
            self.root.after(0, lambda: messagebox.showinfo("更新完成", "🎉 更新成功!\n\n可以关闭此窗口开始使用。"))
        else:
            self.root.after(0, lambda: self._append_log(f"❌ 更新失败: {stderr}\n"))
            self.root.after(0, lambda: self.status_label.configure(text="状态: ❌ 更新失败"))
            self.root.after(0, lambda: messagebox.showerror("更新失败", f"更新失败:\n{stderr}"))
        
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.check_btn.configure(state='normal'))
        self.root.after(0, lambda: self.update_btn.configure(state='normal'))
    
    def _append_log(self, text):
        """追加日志文本"""
        self.log_text.configure(state='normal')
        self.log_text.insert('end', text)
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = UpdaterGUI()
    app.run()

if __name__ == "__main__":
    main()
