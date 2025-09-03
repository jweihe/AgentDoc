"""处理器基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..core.config import get_settings
from ..core.exceptions import ProcessingError
from ..core.logger import get_logger

logger = get_logger(__name__)

class BaseProcessor(ABC):
    """处理器基类
    
    所有文档处理器的基类，定义了统一的处理接口。
    """
    
    def __init__(self, name: str = None):
        """初始化处理器
        
        Args:
            name: 处理器名称
        """
        self.name = name or self.__class__.__name__
        self.settings = get_settings()
        self.logger = get_logger(self.name)
    
    @abstractmethod
    async def process(self, input_path: Union[str, Path], output_dir: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """处理文档
        
        Args:
            input_path: 输入文件路径
            output_dir: 输出目录路径
            **kwargs: 其他参数
            
        Returns:
            处理结果字典
            
        Raises:
            ProcessingError: 处理失败时抛出
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_path: Union[str, Path]) -> bool:
        """验证输入文件
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            验证是否通过
            
        Raises:
            ProcessingError: 验证失败时抛出
        """
        pass
    
    def prepare_output_dir(self, output_dir: Union[str, Path]) -> Path:
        """准备输出目录
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            准备好的输出目录路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式
        
        Returns:
            支持的文件格式列表
        """
        return []
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("清理处理器资源")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()