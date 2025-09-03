"""插件基础模块

定义插件系统的基础类和接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from agentdoc.core.logger import get_logger
from agentdoc.core.exceptions import PluginError, ValidationError


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str
    description: str
    author: str
    category: str = "general"
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    entry_point: Optional[str] = None
    min_agentdoc_version: Optional[str] = None
    max_agentdoc_version: Optional[str] = None
    
    def __post_init__(self):
        """验证元数据"""
        if not self.name:
            raise ValidationError("插件名称不能为空")
        if not self.version:
            raise ValidationError("插件版本不能为空")
        if not self.category:
            raise ValidationError("插件类别不能为空")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "category": self.category,
            "enabled": self.enabled,
            "dependencies": self.dependencies,
            "config_schema": self.config_schema,
            "entry_point": self.entry_point,
            "min_agentdoc_version": self.min_agentdoc_version,
            "max_agentdoc_version": self.max_agentdoc_version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """从字典创建实例"""
        return cls(**data)


class BasePlugin(ABC):
    """插件基类
    
    所有插件的基类，定义了插件的基本接口。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化插件
        
        Args:
            config: 插件配置
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)
        self._metadata = None
        self._initialized = False
        self._enabled = True
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """获取插件元数据
        
        Returns:
            插件元数据
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件
        
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理插件资源"""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证插件配置
        
        Args:
            config: 配置字典
            
        Returns:
            验证是否通过
        """
        if not self.metadata.config_schema:
            return True
        
        # 简单的配置验证
        try:
            schema = self.metadata.config_schema
            for key, value_type in schema.items():
                if key in config:
                    if not isinstance(config[key], value_type):
                        self.logger.error(f"配置项 {key} 类型错误")
                        return False
            return True
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def is_initialized(self) -> bool:
        """检查插件是否已初始化"""
        return self._initialized
    
    def is_enabled(self) -> bool:
        """检查插件是否启用"""
        return self._enabled and self.metadata.enabled
    
    def enable(self) -> None:
        """启用插件"""
        self._enabled = True
        self.logger.info(f"插件 {self.metadata.name} 已启用")
    
    def disable(self) -> None:
        """禁用插件"""
        self._enabled = False
        self.logger.info(f"插件 {self.metadata.name} 已禁用")
    
    def get_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "category": self.metadata.category,
            "initialized": self._initialized,
            "enabled": self.is_enabled(),
            "config": self.config,
        }
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.metadata.name}, "
            f"version={self.metadata.version}, "
            f"enabled={self.is_enabled()})"
        )


class PluginInterface(ABC):
    """插件接口基类
    
    定义特定类型插件的接口。
    """
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        pass
    
    @abstractmethod
    def supports(self, capability: str) -> bool:
        """检查是否支持特定能力"""
        pass