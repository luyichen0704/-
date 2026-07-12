"""
取证AI平台 - 一键卸载工具
"""
import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

class UninstallerGUI:
    """卸载向导GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("取证AI平台 - 卸载工具")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        # 查找安装目录
        self.install_path = self._find_install_path()
        
        self.setup_ui()
    
    def _find_install_path(self):
        """查找安装目录"""
        # 常见安装路径
        possible_paths = [
            os.path.join(os.path.expanduser("~"), "forensic-ai-platform"),
            r"D:\forensic-ai-platform",
            r"E:\forensic-ai-platform",
            r"C:\forensic-ai-platform",
            os.path.dirname(os.path.abspath(__file__))
        ]
        
        for path in possible_paths:
            if os.path.exists(os.path.join(path, "agent")):
                return path
        
        return os.path.dirname(os.path.abspath(__file__))
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title_frame = tk.Frame(self.root, bg='#e74c3c', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🗑️ 取证AI平台 - 卸载工具",
            font=('微软雅黑', 16, 'bold'),
            fg='white',
            bg='#e74c3c'
        ).pack(expand=True)
        
        # 主内容区
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 安装路径
        path_frame = tk.LabelFrame(
            main_frame, text="安装位置",
            font=('微软雅黑', 10, 'bold'), bg='#f0f0f0', padx=10, pady=10
        )
        path_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            path_frame, text=self.install_path,
            font=('Consolas', 10), bg='#f0f0f0', anchor='w'
        ).pack(fill='x')
        
        # 卸载选项
        options_frame = tk.LabelFrame(
            main_frame, text="卸载选项",
            font=('微软雅黑', 10, 'bold'), bg='#f0f0f0', padx=10, pady=10
        )
        options_frame.pack(fill='x', pady=(0, 15))
        
        self.remove_project = tk.BooleanVar(value=True)
        self.remove_config = tk.BooleanVar(value=False)
        self.remove_cases = tk.BooleanVar(value=False)
        self.remove_desktop = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            options_frame, text="删除项目文件",
            variable=self.remove_project, font=('微软雅黑', 10), bg='#f0f0f0'
        ).pack(anchor='w', pady=2)
        
        tk.Checkbutton(
            options_frame, text="删除配置文件 (config/)",
            variable=self.remove_config, font=('微软雅黑', 10), bg='#f0f0f0'
        ).pack(anchor='w', pady=2)
        
        tk.Checkbutton(
            options_frame, text="删除案例数据 (cases/)",
            variable=self.remove_cases, font=('微软雅黑', 10), bg='#f0f0f0'
        ).pack(anchor='w', pady=2)
        
        tk.Checkbutton(
            options_frame, text="删除桌面快捷方式",
            variable=self.remove_desktop, font=('微软雅黑', 10), bg='#f0f0f0'
        ).pack(anchor='w', pady=2)
        
        # 警告信息
        warning_frame = tk.LabelFrame(
            main_frame, text="⚠️ 警告",
            font=('微软雅黑', 10, 'bold'), bg='#fff3cd', padx=10, pady=10
        )
        warning_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            warning_frame,
            text="卸载将删除选定的文件和目录。\n此操作不可撤销，请谨慎操作！",
            font=('微软雅黑', 10), bg='#fff3cd', fg='#856404', anchor='w'
        ).pack(fill='x')
        
        # 注意：不会卸载Scoop和Python
        tk.Label(
            warning_frame,
            text="\n注意：不会卸载 Scoop、Python 和已安装的系统工具",
            font=('微软雅黑', 9), bg='#fff3cd', fg='#666666', anchor='w'
        ).pack(fill='x')
        
        # 按钮区
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(fill='x')
        
        tk.Button(
            btn_frame, text="🗑️ 开始卸载",
            font=('微软雅黑', 12, 'bold'),
            bg='#e74c3c', fg='white', padx=30, pady=8,
            command=self.start_uninstall
        ).pack(side='left')
        
        tk.Button(
            btn_frame, text="取消",
            font=('微软雅黑', 11),
            bg='#95a5a6', fg='white', padx=20, pady=8,
            command=self.root.quit
        ).pack(side='right')
    
    def start_uninstall(self):
        """开始卸载"""
        if not messagebox.askyesno("确认卸载", 
            "确定要卸载取证AI平台吗？\n\n此操作不可撤销！"):
            return
        
        removed_items = []
        
        try:
            # 删除桌面快捷方式
            if self.remove_desktop.get():
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                shortcut = os.path.join(desktop, "取证AI平台.bat")
                if os.path.exists(shortcut):
                    os.remove(shortcut)
                    removed_items.append("桌面快捷方式")
            
            # 删除配置文件
            if self.remove_config.get():
                config_dir = os.path.join(self.install_path, "config")
                if os.path.exists(config_dir):
                    shutil.rmtree(config_dir)
                    removed_items.append("配置文件")
            
            # 删除案例数据
            if self.remove_cases.get():
                cases_dir = os.path.join(self.install_path, "cases")
                if os.path.exists(cases_dir):
                    shutil.rmtree(cases_dir)
                    removed_items.append("案例数据")
            
            # 删除项目文件
            if self.remove_project.get():
                # 删除主要目录
                dirs_to_remove = [
                    "agent", "web", "api", "plugins", "skills",
                    "scripts", "knowledge", "data", "logs", "temp"
                ]
                
                files_to_remove = [
                    "start.bat", "update.bat", "update.sh",
                    "安装.bat", "更新工具.bat", "installer_gui.py",
                    "updater_gui.py", "requirements.txt", "setup.py",
                    "VERSION", "README.md", "INSTALL.md", "QUICKSTART.md",
                    "UPDATE_GUIDE.md", ".gitignore", "LICENSE"
                ]
                
                for dir_name in dirs_to_remove:
                    dir_path = os.path.join(self.install_path, dir_name)
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)
                        removed_items.append(dir_name)
                
                for file_name in files_to_remove:
                    file_path = os.path.join(self.install_path, file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        removed_items.append(file_name)
                
                # 删除.git目录
                git_dir = os.path.join(self.install_path, ".git")
                if os.path.exists(git_dir):
                    shutil.rmtree(git_dir)
                    removed_items.append(".git")
                
                # 删除空目录
                try:
                    os.rmdir(self.install_path)
                    removed_items.append("安装目录")
                except:
                    pass
            
            # 显示结果
            if removed_items:
                result_text = "已删除:\n" + "\n".join(f"  ✅ {item}" for item in removed_items)
                messagebox.showinfo("卸载完成", f"🎉 卸载完成！\n\n{result_text}")
            else:
                messagebox.showinfo("卸载完成", "没有删除任何文件。")
            
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("卸载失败", f"卸载过程中出错:\n{e}")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = UninstallerGUI()
    app.run()

if __name__ == "__main__":
    main()
