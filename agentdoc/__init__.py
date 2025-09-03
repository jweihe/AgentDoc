# -*- coding: utf-8 -*-
"""AgentDoc - 智能文档处理系统

基于大型语言模型的文本文档处理工具。"""

__version__ = "0.1.0"
__author__ = "AgentDoc Team"
__email__ = "team@agentdoc.ai"
__description__ = "智能文档处理系统 - 基于大型语言模型的文本文档处理工具"

from .core.config import Settings
from .core.logger import get_logger
from .core.exceptions import AgentDocError, ModelError, ProcessingError

# 导出主要类和函数
from .models.manager import ModelManager
from .processors.text_processor import TextProcessor
from .processors.batch_processor import BatchProcessor

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "Settings",
    "get_logger",
    "AgentDocError",
    "ModelError",
    "ProcessingError",
    "ModelManager",
    "TextProcessor",
    "BatchProcessor",
]

# 设置默认日志配置
get_logger("agentdoc")