"""处理器工厂"""

from typing import Any, Dict, List, Optional, Type, Union
from pathlib import Path

from .base import BaseProcessor
from ..core.exceptions import ProcessingError, ValidationError
from ..core.logger import get_logger

logger = get_logger(__name__)

class ProcessorFactory:
    """处理器工厂
    
    负责创建和管理不同类型的文档处理器。
    """
    
    def __init__(self):
        """初始化处理器工厂"""
        self.logger = get_logger(self.__class__.__name__)
        self._processors: Dict[str, Type[BaseProcessor]] = {}
        self._format_mapping: Dict[str, str] = {}  # 文件格式到处理器的映射
        
        # 注册内置处理器
        self._register_builtin_processors()
    
    def _register_builtin_processors(self):
        """注册内置处理器"""
        try:
            from .text_processor import TextProcessor
            
            # 注册文本处理器
            self.register_processor("text", TextProcessor, [".txt", ".md", ".markdown"])
            
            self.logger.info("内置处理器注册完成")
        
        except Exception as e:
            self.logger.error(f"注册内置处理器失败: {e}")
    
    def register_processor(
        self, 
        name: str, 
        processor_class: Type[BaseProcessor], 
        supported_formats: List[str]
    ):
        """注册处理器
        
        Args:
            name: 处理器名称
            processor_class: 处理器类
            supported_formats: 支持的文件格式列表
        """
        if not issubclass(processor_class, BaseProcessor):
            raise ValidationError(f"处理器类必须继承自BaseProcessor: {processor_class}")
        
        if name in self._processors:
            self.logger.warning(f"处理器已存在，将被覆盖: {name}")
        
        # 注册处理器
        self._processors[name] = processor_class
        
        # 注册格式映射
        for fmt in supported_formats:
            if not fmt.startswith("."):
                fmt = f".{fmt}"
            self._format_mapping[fmt.lower()] = name
        
        self.logger.info(f"注册处理器: {name}, 支持格式: {supported_formats}")
    
    def unregister_processor(self, name: str):
        """注销处理器
        
        Args:
            name: 处理器名称
        """
        if name not in self._processors:
            self.logger.warning(f"处理器不存在: {name}")
            return
        
        # 移除处理器
        del self._processors[name]
        
        # 移除格式映射
        formats_to_remove = []
        for fmt, processor_name in self._format_mapping.items():
            if processor_name == name:
                formats_to_remove.append(fmt)
        
        for fmt in formats_to_remove:
            del self._format_mapping[fmt]
        
        self.logger.info(f"注销处理器: {name}")
    
    def create_processor(
        self, 
        processor_name: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None
    ) -> BaseProcessor:
        """创建处理器实例
        
        Args:
            processor_name: 处理器名称（可选）
            file_path: 文件路径（用于自动检测处理器类型）
            
        Returns:
            处理器实例
        """
        if processor_name:
            # 直接使用指定的处理器
            if processor_name not in self._processors:
                raise ProcessingError(f"处理器不存在: {processor_name}")
            
            processor_class = self._processors[processor_name]
            return processor_class(processor_name)
        
        elif file_path:
            # 根据文件扩展名自动选择处理器
            file_path = Path(file_path)
            file_ext = file_path.suffix.lower()
            
            if file_ext not in self._format_mapping:
                raise ProcessingError(f"不支持的文件格式: {file_ext}")
            
            processor_name = self._format_mapping[file_ext]
            processor_class = self._processors[processor_name]
            return processor_class(processor_name)
        
        else:
            raise ValidationError("必须指定处理器名称或文件路径")
    
    def get_processor_for_format(self, file_format: str) -> Optional[str]:
        """根据文件格式获取处理器名称
        
        Args:
            file_format: 文件格式（如 .pdf, .docx）
            
        Returns:
            处理器名称或None
        """
        if not file_format.startswith("."):
            file_format = f".{file_format}"
        
        return self._format_mapping.get(file_format.lower())
    
    def list_processors(self) -> List[str]:
        """列出所有可用的处理器
        
        Returns:
            处理器名称列表
        """
        return list(self._processors.keys())
    
    def list_supported_formats(self) -> List[str]:
        """列出所有支持的文件格式
        
        Returns:
            文件格式列表
        """
        return list(self._format_mapping.keys())
    
    def get_processor_info(self, processor_name: str) -> Dict[str, Any]:
        """获取处理器信息
        
        Args:
            processor_name: 处理器名称
            
        Returns:
            处理器信息
        """
        if processor_name not in self._processors:
            raise ProcessingError(f"处理器不存在: {processor_name}")
        
        processor_class = self._processors[processor_name]
        
        # 获取支持的格式
        supported_formats = []
        for fmt, name in self._format_mapping.items():
            if name == processor_name:
                supported_formats.append(fmt)
        
        return {
            "name": processor_name,
            "class": processor_class.__name__,
            "module": processor_class.__module__,
            "supported_formats": supported_formats,
            "description": processor_class.__doc__ or "无描述"
        }
    
    def is_format_supported(self, file_format: str) -> bool:
        """检查文件格式是否支持
        
        Args:
            file_format: 文件格式
            
        Returns:
            是否支持
        """
        if not file_format.startswith("."):
            file_format = f".{file_format}"
        
        return file_format.lower() in self._format_mapping
    
    def get_format_info(self) -> Dict[str, str]:
        """获取格式映射信息
        
        Returns:
            格式到处理器的映射字典
        """
        return self._format_mapping.copy()
    
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """验证文件是否可以处理
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否可以处理
        """
        file_path = Path(file_path)
        
        # 检查文件是否存在
        if not file_path.exists():
            return False
        
        # 检查是否为文件
        if not file_path.is_file():
            return False
        
        # 检查文件格式是否支持
        return self.is_format_supported(file_path.suffix)
    
    def auto_detect_processor(self, file_path: Union[str, Path]) -> Optional[str]:
        """自动检测文件应该使用的处理器
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理器名称或None
        """
        file_path = Path(file_path)
        
        if not self.validate_file(file_path):
            return None
        
        return self.get_processor_for_format(file_path.suffix)

# 全局处理器工厂实例
_processor_factory = None

def get_processor_factory() -> ProcessorFactory:
    """获取全局处理器工厂实例
    
    Returns:
        处理器工厂实例
    """
    global _processor_factory
    if _processor_factory is None:
        _processor_factory = ProcessorFactory()
    return _processor_factory