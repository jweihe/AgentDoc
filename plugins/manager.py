"""插件管理器

负责插件的加载、管理和生命周期控制。
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from concurrent.futures import ThreadPoolExecutor
import threading

from .base import BasePlugin, PluginMetadata
from agentdoc.core.logger import get_logger
from agentdoc.core.exceptions import PluginError, ValidationError


class PluginManager:
    """插件管理器
    
    负责插件的发现、加载、管理和生命周期控制。
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """初始化插件管理器
        
        Args:
            plugin_dirs: 插件目录列表
        """
        self.logger = get_logger(self.__class__.__name__)
        self.plugin_dirs = plugin_dirs or []
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="plugin")
        
    def add_plugin_dir(self, plugin_dir: str) -> None:
        """添加插件目录
        
        Args:
            plugin_dir: 插件目录路径
        """
        if plugin_dir not in self.plugin_dirs:
            self.plugin_dirs.append(plugin_dir)
            self.logger.info(f"添加插件目录: {plugin_dir}")
    
    def discover_plugins(self) -> List[str]:
        """发现插件
        
        Returns:
            发现的插件文件路径列表
        """
        plugin_files = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                self.logger.warning(f"插件目录不存在: {plugin_dir}")
                continue
                
            for root, dirs, files in os.walk(plugin_dir):
                for file in files:
                    if file.endswith('.py') and not file.startswith('_'):
                        plugin_files.append(os.path.join(root, file))
        
        self.logger.info(f"发现 {len(plugin_files)} 个插件文件")
        return plugin_files
    
    def register_plugin_class(self, plugin_class: Type[BasePlugin]) -> bool:
        """注册插件类
        
        Args:
            plugin_class: 插件类
            
        Returns:
            注册是否成功
        """
        try:
            # 创建临时实例获取元数据
            temp_instance = plugin_class()
            metadata = temp_instance.metadata
            
            with self._lock:
                # 检查名称冲突
                if metadata.name in self._plugin_classes:
                    self.logger.warning(f"插件名称已存在: {metadata.name}")
                    return False
                
                # 注册插件类
                self._plugin_classes[metadata.name] = plugin_class
                
                # 按类别分组
                if metadata.category not in self._categories:
                    self._categories[metadata.category] = []
                self._categories[metadata.category].append(metadata.name)
                
                self.logger.info(f"注册插件类: {metadata.name} ({metadata.category})")
                return True
                
        except Exception as e:
            self.logger.error(f"注册插件类失败: {e}")
            return False
    
    def create_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BasePlugin]:
        """创建插件实例
        
        Args:
            plugin_name: 插件名称
            config: 插件配置
            
        Returns:
            插件实例或None
        """
        with self._lock:
            if plugin_name not in self._plugin_classes:
                self.logger.error(f"插件类不存在: {plugin_name}")
                return None
            
            try:
                plugin_class = self._plugin_classes[plugin_name]
                plugin = plugin_class(config)
                
                # 验证配置
                if config and not plugin.validate_config(config):
                    self.logger.error(f"插件配置验证失败: {plugin_name}")
                    return None
                
                self.logger.info(f"创建插件实例: {plugin_name}")
                return plugin
                
            except Exception as e:
                self.logger.error(f"创建插件实例失败 {plugin_name}: {e}")
                return None
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """加载并初始化插件
        
        Args:
            plugin_name: 插件名称
            config: 插件配置
            
        Returns:
            加载是否成功
        """
        with self._lock:
            if plugin_name in self._plugins:
                self.logger.warning(f"插件已加载: {plugin_name}")
                return True
            
            # 创建插件实例
            plugin = self.create_plugin(plugin_name, config)
            if plugin is None:
                return False
            
            try:
                # 初始化插件
                if plugin.initialize():
                    self._plugins[plugin_name] = plugin
                    plugin._initialized = True
                    self.logger.info(f"插件加载成功: {plugin_name}")
                    return True
                else:
                    self.logger.error(f"插件初始化失败: {plugin_name}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"插件初始化异常 {plugin_name}: {e}")
                return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            卸载是否成功
        """
        with self._lock:
            if plugin_name not in self._plugins:
                self.logger.warning(f"插件未加载: {plugin_name}")
                return True
            
            try:
                plugin = self._plugins[plugin_name]
                plugin.cleanup()
                plugin._initialized = False
                del self._plugins[plugin_name]
                self.logger.info(f"插件卸载成功: {plugin_name}")
                return True
                
            except Exception as e:
                self.logger.error(f"插件卸载失败 {plugin_name}: {e}")
                return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件实例
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件实例或None
        """
        return self._plugins.get(plugin_name)
    
    def list_plugins(self, category: Optional[str] = None, loaded_only: bool = False) -> List[str]:
        """列出插件
        
        Args:
            category: 插件类别（可选）
            loaded_only: 是否只列出已加载的插件
            
        Returns:
            插件名称列表
        """
        if loaded_only:
            plugins = list(self._plugins.keys())
            if category:
                # 过滤类别
                filtered = []
                for name in plugins:
                    plugin = self._plugins[name]
                    if plugin.metadata.category == category:
                        filtered.append(name)
                return filtered
            return plugins
        
        if category:
            return self._categories.get(category, [])
        return list(self._plugin_classes.keys())
    
    def list_categories(self) -> List[str]:
        """列出所有类别
        
        Returns:
            类别列表
        """
        return list(self._categories.keys())
    
    def get_plugin_status(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取插件状态
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件状态信息
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.get_status()
        
        # 检查是否有注册的类
        if plugin_name in self._plugin_classes:
            return {
                "name": plugin_name,
                "registered": True,
                "loaded": False,
                "initialized": False,
            }
        
        return None
    
    def cleanup(self) -> None:
        """清理资源"""
        self.logger.info("清理插件管理器")
        
        # 卸载所有插件
        for plugin_name in list(self._plugins.keys()):
            self.unload_plugin(plugin_name)
        
        # 关闭线程池
        self._executor.shutdown(wait=True)
        
        # 清理注册信息
        with self._lock:
            self._plugins.clear()
            self._plugin_classes.clear()
            self._categories.clear()


# 全局插件管理器实例
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器实例
    
    Returns:
        插件管理器实例
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def register_plugin(plugin_class: Type[BasePlugin]) -> bool:
    """注册插件类的便捷函数
    
    Args:
        plugin_class: 插件类
        
    Returns:
        注册是否成功
    """
    return get_plugin_manager().register_plugin_class(plugin_class)


def load_plugin(plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """加载插件的便捷函数
    
    Args:
        plugin_name: 插件名称
        config: 插件配置
        
    Returns:
        加载是否成功
    """
    return get_plugin_manager().load_plugin(plugin_name, config)


def get_plugin(plugin_name: str) -> Optional[BasePlugin]:
    """获取插件实例的便捷函数
    
    Args:
        plugin_name: 插件名称
        
    Returns:
        插件实例或None
    """
    return get_plugin_manager().get_plugin(plugin_name)