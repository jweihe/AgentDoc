# -*- coding: utf-8 -*-
"""日志模块

基于标准库logging的轻量级日志系统。"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import get_settings


def setup_logger(
    name: str = "agentdoc",
    level: Optional[str] = None,
    file_path: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """设置日志配置"""
    settings = get_settings()
    
    # 使用配置或参数值
    level = level or settings.logging.level
    file_path = file_path or settings.logging.file_path
    format_string = format_string or "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 创建格式器
    formatter = logging.Formatter(format_string)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器（如果指定了文件路径）
    if file_path:
        log_path = Path(file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "agentdoc") -> logging.Logger:
    """获取日志器实例"""
    return setup_logger(name)


# 默认日志器
default_logger = get_logger()