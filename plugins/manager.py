"""
插件管理器 - 管理取证平台插件
支持动态加载、启用/禁用插件
"""
import os
import json
import importlib
import importlib.util
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

@dataclass
class PluginMeta:
    """插件元数据"""
    name: str
    version: str
    description: str
    author: str
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    entry_point: str = "plugin.py"
    hooks: List[str] = field(default_factory=list)

class ForensicPlugin(ABC):
    """取证插件基类"""
    
    @abstractmethod
    def get_meta(self) -> PluginMeta:
        """获取插件元数据"""
        pass
    
    @abstractmethod
    def initialize(self, agent) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行插件"""
        pass
    
    def cleanup(self):
        """清理插件资源"""
        pass

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugins_dir: str = None):
        """初始化插件管理器"""
        self.plugins_dir = plugins_dir or self._find_plugins_dir()
        self.plugins: Dict[str, ForensicPlugin] = {}
        self.plugin_metas: Dict[str, PluginMeta] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        
        # 加载插件
        self._discover_plugins()
    
    def _find_plugins_dir(self) -> str:
        """查找插件目录"""
        possible_paths = [
            Path(__file__).parent,
            Path("plugins"),
            Path.home() / "forensic-ai-platform" / "plugins"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return str(path)
        
        return ""
    
    def _discover_plugins(self):
        """发现插件"""
        if not self.plugins_dir or not os.path.exists(self.plugins_dir):
            logger.warning(f"插件目录不存在: {self.plugins_dir}")
            return
        
        plugins_path = Path(self.plugins_dir)
        
        # 扫描插件目录
        for plugin_dir in plugins_path.iterdir():
            if plugin_dir.is_dir() and plugin_dir.name != "__pycache__":
                plugin_file = plugin_dir / "plugin.py"
                if plugin_file.exists():
                    try:
                        self._load_plugin(plugin_dir.name, plugin_file)
                    except Exception as e:
                        logger.error(f"加载插件失败 {plugin_dir.name}: {e}")
        
        logger.info(f"发现 {len(self.plugins)} 个插件")
    
    def _load_plugin(self, plugin_name: str, plugin_path: Path):
        """加载插件"""
        try:
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}",
                str(plugin_path)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, ForensicPlugin) and 
                    attr != ForensicPlugin):
                    plugin_class = attr
                    break
            
            if plugin_class:
                plugin_instance = plugin_class()
                meta = plugin_instance.get_meta()
                
                self.plugins[plugin_name] = plugin_instance
                self.plugin_metas[plugin_name] = meta
                
                # 注册钩子
                for hook_name in meta.hooks:
                    if hook_name not in self.hooks:
                        self.hooks[hook_name] = []
                    self.hooks[hook_name].append(
                        getattr(plugin_instance, hook_name, None)
                    )
                
                logger.info(f"加载插件: {plugin_name} v{meta.version}")
            
        except Exception as e:
            logger.error(f"加载插件模块失败 {plugin_name}: {e}")
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        plugins = []
        for name, meta in self.plugin_metas.items():
            plugins.append({
                "name": meta.name,
                "version": meta.version,
                "description": meta.description,
                "author": meta.author,
                "enabled": meta.enabled,
                "hooks": meta.hooks
            })
        return plugins
    
    def get_plugin(self, name: str) -> Optional[ForensicPlugin]:
        """获取插件"""
        return self.plugins.get(name)
    
    def enable_plugin(self, name: str) -> bool:
        """启用插件"""
        if name in self.plugin_metas:
            self.plugin_metas[name].enabled = True
            logger.info(f"启用插件: {name}")
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """禁用插件"""
        if name in self.plugin_metas:
            self.plugin_metas[name].enabled = False
            logger.info(f"禁用插件: {name}")
            return True
        return False
    
    def execute_plugin(self, name: str, **kwargs) -> Dict[str, Any]:
        """执行插件"""
        if name not in self.plugins:
            return {"success": False, "error": f"插件 {name} 未找到"}
        
        meta = self.plugin_metas.get(name)
        if meta and not meta.enabled:
            return {"success": False, "error": f"插件 {name} 已禁用"}
        
        try:
            plugin = self.plugins[name]
            result = plugin.execute(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"执行插件失败 {name}: {e}")
            return {"success": False, "error": str(e)}
    
    def call_hook(self, hook_name: str, **kwargs) -> List[Any]:
        """调用钩子"""
        results = []
        
        if hook_name in self.hooks:
            for hook_func in self.hooks[hook_name]:
                if hook_func:
                    try:
                        result = hook_func(**kwargs)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"钩子执行失败 {hook_name}: {e}")
        
        return results
    
    def reload_plugins(self):
        """重新加载所有插件"""
        self.plugins.clear()
        self.plugin_metas.clear()
        self.hooks.clear()
        self._discover_plugins()
    
    def install_plugin(self, plugin_path: str) -> bool:
        """安装插件"""
        try:
            source = Path(plugin_path)
            if not source.exists():
                logger.error(f"插件路径不存在: {plugin_path}")
                return False
            
            # 复制插件到插件目录
            plugin_name = source.stem if source.is_file() else source.name
            dest = Path(self.plugins_dir) / plugin_name
            
            if source.is_file():
                dest.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(source, dest / "plugin.py")
            else:
                import shutil
                shutil.copytree(source, dest, dirs_exist_ok=True)
            
            # 重新加载
            self.reload_plugins()
            
            logger.info(f"安装插件成功: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"安装插件失败: {e}")
            return False
    
    def uninstall_plugin(self, name: str) -> bool:
        """卸载插件"""
        try:
            plugin_dir = Path(self.plugins_dir) / name
            if plugin_dir.exists():
                import shutil
                shutil.rmtree(plugin_dir)
                
                # 移除插件
                if name in self.plugins:
                    self.plugins[name].cleanup()
                    del self.plugins[name]
                if name in self.plugin_metas:
                    del self.plugin_metas[name]
                
                logger.info(f"卸载插件成功: {name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"卸载插件失败: {e}")
            return False

# 全局实例
plugin_manager = PluginManager()
