# -*- coding: utf-8 -*-
"""配置管理模块

使用Pydantic进行配置验证和管理。"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class AgentConfig(BaseModel):
    """Agent配置"""
    
    # 基本配置
    max_iterations: int = Field(default=10, description="最大迭代次数")
    timeout: int = Field(default=300, description="超时时间(秒)")
    enable_memory: bool = Field(default=True, description="是否启用记忆")
    
    # 文本处理
    max_text_length: int = Field(default=10000, description="最大文本长度")
    chunk_size: int = Field(default=1000, description="文本分块大小")
    chunk_overlap: int = Field(default=100, description="分块重叠大小")


class ProcessingConfig(BaseModel):
    """处理配置"""
    
    # 文档处理
    supported_formats: List[str] = Field(
        default=["txt", "md", "markdown"],
        description="支持的文档格式"
    )
    
    # 输出配置
    output_formats: List[str] = Field(
        default=["txt", "json"],
        description="输出格式列表"
    )
    
    # 临时文件
    temp_dir: str = Field(default="temp", description="临时文件目录")
    cleanup_temp: bool = Field(default=True, description="是否清理临时文件")
    
    # 性能配置
    max_file_size: int = Field(default=50 * 1024 * 1024, description="最大文件大小(字节)")
    concurrent_tasks: int = Field(default=4, description="并发任务数")


class WebConfig(BaseModel):
    """Web服务配置"""
    
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, ge=1, le=65535, description="服务器端口")
    debug: bool = Field(default=False, description="调试模式")
    
    # 文件上传
    max_file_size: int = Field(default=10 * 1024 * 1024, description="最大文件大小(字节)")  # 减小到10MB
    allowed_extensions: List[str] = Field(
        default=[".txt", ".md", ".markdown"],
        description="允许的文件扩展名"
    )


class StorageConfig(BaseModel):
    """存储配置"""
    
    data_dir: str = Field(default="data", description="数据存储目录")
    memory_dir: str = Field(default="data/memory", description="记忆存储目录")
    results_dir: str = Field(default="data/results", description="结果存储目录")
    enable_backup: bool = Field(default=True, description="是否启用备份")


class ModelConfig(BaseModel):
    """模型配置"""
    
    # 默认模型
    default_model: str = Field(default="Qwen/Qwen2.5-7B-Instruct", description="默认LLM模型")
    
    # 模型参数
    max_tokens: int = Field(default=2048, description="最大token数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="生成温度")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Top-p采样")
    top_k: int = Field(default=50, ge=1, description="Top-k采样")
    
    # 生成参数
    max_new_tokens: int = Field(default=1024, description="最大新生成token数")
    repetition_penalty: float = Field(default=1.1, ge=1.0, description="重复惩罚")
    
    # 设备配置
    cpu_only: bool = Field(default=False, description="仅使用CPU")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('温度必须在0.0到2.0之间')
        return v
    
    @validator('top_p')
    def validate_top_p(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('top_p必须在0.0到1.0之间')
        return v


class LoggingConfig(BaseModel):
    """日志配置"""
    
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        description="日志格式"
    )
    file_path: Optional[str] = Field(default=None, description="日志文件路径")
    rotation: str = Field(default="1 day", description="日志轮转")
    retention: str = Field(default="30 days", description="日志保留时间")
    
    @validator('level')
    def validate_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'日志级别必须是 {allowed_levels} 之一')
        return v.upper()


class Settings(BaseSettings):
    """主配置类"""
    
    # 基本信息
    app_name: str = Field(default="AgentDoc", description="应用名称")
    version: str = Field(default="1.0.0", description="版本号")
    description: str = Field(
        default="基于大型语言模型的文本文档处理工具",
        description="应用描述"
    )
    
    # 子配置
    agent: AgentConfig = Field(default_factory=AgentConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    web: WebConfig = Field(default_factory=WebConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # 环境配置
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False


# 全局设置实例
_settings = None

def get_settings() -> Settings:
    """获取全局设置实例
    
    Returns:
        设置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def update_settings(**kwargs) -> Settings:
    """更新配置"""
    global _settings
    if _settings is None:
        _settings = Settings()
    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
    return _settings