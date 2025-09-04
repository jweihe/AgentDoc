"""模型插件"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Type

from .base import BasePlugin, PluginMetadata
from ..models.base import BaseModel
from ..core.exceptions import ModelError, PluginError
from ..core.logger import get_logger

logger = get_logger(__name__)

class ModelPlugin(BasePlugin):
    """模型插件基类
    
    用于扩展支持新的视觉语言模型。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化模型插件
        
        Args:
            config: 插件配置
        """
        super().__init__(config)
        self._model_class = None
        self._model_instance = None
    
    @property
    @abstractmethod
    def model_class(self) -> Type[BaseModel]:
        """获取模型类
        
        Returns:
            模型类
        """
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """获取支持的模型列表
        
        Returns:
            模型名称列表
        """
        pass
    
    async def initialize(self) -> bool:
        """初始化模型插件
        
        Returns:
            初始化是否成功
        """
        try:
            # 验证模型类
            if not issubclass(self.model_class, BaseModel):
                raise PluginError(f"模型类必须继承自BaseModel: {self.model_class}")
            
            self._model_class = self.model_class
            
            # 注册模型到工厂
            from ..models.factory import get_model_factory
            factory = get_model_factory()
            
            for model_name in self.supported_models:
                factory.register_model(model_name, self._model_class)
                self.logger.info(f"注册模型: {model_name}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"模型插件初始化失败: {e}")
            return False
    
    async def cleanup(self):
        """清理模型插件资源"""
        try:
            # 从工厂注销模型
            from ..models.factory import get_model_factory
            factory = get_model_factory()
            
            for model_name in self.supported_models:
                try:
                    factory.unregister_model(model_name)
                    self.logger.info(f"注销模型: {model_name}")
                except Exception as e:
                    self.logger.warning(f"注销模型失败 {model_name}: {e}")
            
            # 清理模型实例
            if self._model_instance:
                await self._model_instance.unload()
                self._model_instance = None
        
        except Exception as e:
            self.logger.error(f"模型插件清理失败: {e}")
    
    def create_model(self, model_name: str, config: Optional[Dict[str, Any]] = None) -> BaseModel:
        """创建模型实例
        
        Args:
            model_name: 模型名称
            config: 模型配置
            
        Returns:
            模型实例
        """
        if model_name not in self.supported_models:
            raise ModelError(f"不支持的模型: {model_name}")
        
        if not self._model_class:
            raise PluginError("模型插件未初始化")
        
        return self._model_class(model_name, config)
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息
        """
        if model_name not in self.supported_models:
            raise ModelError(f"不支持的模型: {model_name}")
        
        # 创建临时实例获取信息
        temp_model = self.create_model(model_name)
        return temp_model.get_model_info()

class HuggingFaceModelPlugin(ModelPlugin):
    """HuggingFace模型插件
    
    支持从HuggingFace Hub加载模型。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="huggingface_model",
            version="1.0.0",
            description="HuggingFace模型插件",
            author="DocuMind Team",
            category="model",
            dependencies=["transformers", "torch"],
            min_documind_version="1.0.0"
        )
    
    @property
    def model_class(self) -> Type[BaseModel]:
        from .models.huggingface import HuggingFaceModel
        return HuggingFaceModel
    
    @property
    def supported_models(self) -> List[str]:
        return [
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-large",
            "facebook/blenderbot-400M-distill",
            "facebook/blenderbot-1B-distill"
        ]

class OpenAIModelPlugin(ModelPlugin):
    """OpenAI模型插件
    
    支持OpenAI API模型。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="openai_model",
            version="1.0.0",
            description="OpenAI模型插件",
            author="DocuMind Team",
            category="model",
            dependencies=["openai"],
            min_documind_version="1.0.0"
        )
    
    @property
    def model_class(self) -> Type[BaseModel]:
        from .models.openai import OpenAIModel
        return OpenAIModel
    
    @property
    def supported_models(self) -> List[str]:
        return [
            "gpt-4-vision-preview",
            "gpt-4o",
            "gpt-4o-mini"
        ]

class AnthropicModelPlugin(ModelPlugin):
    """Anthropic模型插件
    
    支持Anthropic Claude模型。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="anthropic_model",
            version="1.0.0",
            description="Anthropic模型插件",
            author="DocuMind Team",
            category="model",
            dependencies=["anthropic"],
            min_documind_version="1.0.0"
        )
    
    @property
    def model_class(self) -> Type[BaseModel]:
        from .models.anthropic import AnthropicModel
        return AnthropicModel
    
    @property
    def supported_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

# 自动注册插件
def register_model_plugins():
    """注册所有模型插件"""
    from .base import get_plugin_registry
    
    registry = get_plugin_registry()
    
    # 注册内置模型插件
    plugins = [
        HuggingFaceModelPlugin,
        OpenAIModelPlugin,
        AnthropicModelPlugin
    ]
    
    for plugin_class in plugins:
        try:
            registry.register(plugin_class)
        except Exception as e:
            logger.warning(f"注册模型插件失败 {plugin_class.__name__}: {e}")

# 模块加载时自动注册
register_model_plugins()