"""插件系统

提供灵活的插件架构，支持模型、处理器等各种类型的插件。
"""

from .base import BasePlugin, PluginMetadata, PluginInterface
from .manager import PluginManager, get_plugin_manager, register_plugin, load_plugin, get_plugin

__all__ = [
    "BasePlugin",
    "PluginMetadata", 
    "PluginInterface",
    "PluginManager",
    "get_plugin_manager",
    "register_plugin",
    "load_plugin",
    "get_plugin",
]