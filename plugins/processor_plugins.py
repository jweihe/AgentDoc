"""处理器插件"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Type

from .base import BasePlugin, PluginMetadata
from ..processors.base import BaseProcessor
from ..core.exceptions import ProcessingError, PluginError
from ..core.logger import get_logger

logger = get_logger(__name__)

class ProcessorPlugin(BasePlugin):
    """处理器插件基类
    
    用于扩展支持新的文档处理器。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化处理器插件
        
        Args:
            config: 插件配置
        """
        super().__init__(config)
        self._processor_class = None
    
    @property
    @abstractmethod
    def processor_class(self) -> Type[BaseProcessor]:
        """获取处理器类
        
        Returns:
            处理器类
        """
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """获取支持的文件格式
        
        Returns:
            文件格式列表
        """
        pass
    
    @property
    @abstractmethod
    def processor_name(self) -> str:
        """获取处理器名称
        
        Returns:
            处理器名称
        """
        pass
    
    async def initialize(self) -> bool:
        """初始化处理器插件
        
        Returns:
            初始化是否成功
        """
        try:
            # 验证处理器类
            if not issubclass(self.processor_class, BaseProcessor):
                raise PluginError(f"处理器类必须继承自BaseProcessor: {self.processor_class}")
            
            self._processor_class = self.processor_class
            
            # 注册处理器到工厂
            from ..processors.factory import get_processor_factory
            factory = get_processor_factory()
            
            factory.register_processor(
                self.processor_name,
                self._processor_class,
                self.supported_formats
            )
            
            self.logger.info(f"注册处理器: {self.processor_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"处理器插件初始化失败: {e}")
            return False
    
    async def cleanup(self):
        """清理处理器插件资源"""
        try:
            # 从工厂注销处理器
            from ..processors.factory import get_processor_factory
            factory = get_processor_factory()
            
            factory.unregister_processor(self.processor_name)
            self.logger.info(f"注销处理器: {self.processor_name}")
        
        except Exception as e:
            self.logger.error(f"处理器插件清理失败: {e}")
    
    def create_processor(self, config: Optional[Dict[str, Any]] = None) -> BaseProcessor:
        """创建处理器实例
        
        Args:
            config: 处理器配置
            
        Returns:
            处理器实例
        """
        if not self._processor_class:
            raise PluginError("处理器插件未初始化")
        
        return self._processor_class(config)
    
    def get_processor_info(self) -> Dict[str, Any]:
        """获取处理器信息
        
        Returns:
            处理器信息
        """
        return {
            "name": self.processor_name,
            "supported_formats": self.supported_formats,
            "description": self.metadata.description,
            "version": self.metadata.version
        }

class WordProcessorPlugin(ProcessorPlugin):
    """Word文档处理器插件
    
    支持处理Word文档(.docx, .doc)。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="word_processor",
            version="1.0.0",
            description="Word文档处理器插件",
            author="DocuMind Team",
            category="processor",
            dependencies=["python-docx", "python-docx2txt"],
            min_documind_version="1.0.0"
        )
    
    @property
    def processor_class(self) -> Type[BaseProcessor]:
        from ..processors.word_processor import WordProcessor
        return WordProcessor
    
    @property
    def supported_formats(self) -> List[str]:
        return [".docx", ".doc"]
    
    @property
    def processor_name(self) -> str:
        return "word"

class PowerPointProcessorPlugin(ProcessorPlugin):
    """PowerPoint处理器插件
    
    支持处理PowerPoint文档(.pptx, .ppt)。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="powerpoint_processor",
            version="1.0.0",
            description="PowerPoint处理器插件",
            author="DocuMind Team",
            category="processor",
            dependencies=["python-pptx"],
            min_documind_version="1.0.0"
        )
    
    @property
    def processor_class(self) -> Type[BaseProcessor]:
        from ..processors.powerpoint_processor import PowerPointProcessor
        return PowerPointProcessor
    
    @property
    def supported_formats(self) -> List[str]:
        return [".pptx", ".ppt"]
    
    @property
    def processor_name(self) -> str:
        return "powerpoint"

class ExcelProcessorPlugin(ProcessorPlugin):
    """Excel处理器插件
    
    支持处理Excel文档(.xlsx, .xls)。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="excel_processor",
            version="1.0.0",
            description="Excel处理器插件",
            author="DocuMind Team",
            category="processor",
            dependencies=["openpyxl", "xlrd"],
            min_documind_version="1.0.0"
        )
    
    @property
    def processor_class(self) -> Type[BaseProcessor]:
        from ..processors.excel_processor import ExcelProcessor
        return ExcelProcessor
    
    @property
    def supported_formats(self) -> List[str]:
        return [".xlsx", ".xls"]
    
    @property
    def processor_name(self) -> str:
        return "excel"

class ImageProcessorPlugin(ProcessorPlugin):
    """图像处理器插件
    
    支持处理各种图像格式。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="image_processor",
            version="1.0.0",
            description="图像处理器插件",
            author="DocuMind Team",
            category="processor",
            dependencies=["Pillow", "opencv-python"],
            min_documind_version="1.0.0"
        )
    
    @property
    def processor_class(self) -> Type[BaseProcessor]:
        from ..processors.image_processor import ImageProcessor
        return ImageProcessor
    
    @property
    def supported_formats(self) -> List[str]:
        return [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
    
    @property
    def processor_name(self) -> str:
        return "image"

class MarkdownProcessorPlugin(ProcessorPlugin):
    """Markdown处理器插件
    
    支持处理Markdown文档。
    """
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="markdown_processor",
            version="1.0.0",
            description="Markdown处理器插件",
            author="DocuMind Team",
            category="processor",
            dependencies=["markdown", "beautifulsoup4"],
            min_documind_version="1.0.0"
        )
    
    @property
    def processor_class(self) -> Type[BaseProcessor]:
        from ..processors.markdown_processor import MarkdownProcessor
        return MarkdownProcessor
    
    @property
    def supported_formats(self) -> List[str]:
        return [".md", ".markdown"]
    
    @property
    def processor_name(self) -> str:
        return "markdown"

# 自动注册插件
def register_processor_plugins():
    """注册所有处理器插件"""
    from .base import get_plugin_registry
    
    registry = get_plugin_registry()
    
    # 注册内置处理器插件
    plugins = [
        WordProcessorPlugin,
        PowerPointProcessorPlugin,
        ExcelProcessorPlugin,
        ImageProcessorPlugin,
        MarkdownProcessorPlugin
    ]
    
    for plugin_class in plugins:
        try:
            registry.register(plugin_class)
        except Exception as e:
            logger.warning(f"注册处理器插件失败 {plugin_class.__name__}: {e}")

# 模块加载时自动注册
register_processor_plugins()