"""API数据模型"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessRequest(BaseModel):
    """处理请求模型"""
    model_name: str = Field(default="qwen2.5-vl-7b", description="模型名称")
    include_pages: bool = Field(default=True, description="是否包含页码")
    cpu_mode: bool = Field(default=False, description="是否使用CPU模式")
    max_concurrent: Optional[int] = Field(default=3, description="最大并发数（批量处理）")
    
    class Config:
        schema_extra = {
            "example": {
                "model_name": "qwen2.5-vl-7b",
                "include_pages": True,
                "cpu_mode": False,
                "max_concurrent": 3
            }
        }

class ProcessResponse(BaseModel):
    """处理响应模型"""
    task_id: str = Field(description="任务ID")
    status: TaskStatus = Field(description="任务状态")
    message: str = Field(description="响应消息")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "pending",
                "message": "PDF处理任务已提交"
            }
        }

class TOCItem(BaseModel):
    """目录项模型"""
    title: str = Field(description="标题")
    level: int = Field(description="层级")
    page: Optional[int] = Field(default=None, description="页码")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "第一章 引言",
                "level": 1,
                "page": 1
            }
        }

class ProcessResult(BaseModel):
    """处理结果模型"""
    filename: str = Field(description="文件名")
    toc: List[TOCItem] = Field(description="目录结构")
    total_pages: Optional[int] = Field(default=None, description="总页数")
    processing_time: float = Field(description="处理时间（秒）")
    model_used: str = Field(description="使用的模型")
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "document.pdf",
                "toc": [
                    {"title": "第一章 引言", "level": 1, "page": 1},
                    {"title": "1.1 背景", "level": 2, "page": 2}
                ],
                "total_pages": 100,
                "processing_time": 15.5,
                "model_used": "qwen2.5-vl-7b"
            }
        }

class BatchProcessResult(BaseModel):
    """批量处理结果模型"""
    total_files: int = Field(description="总文件数")
    successful_files: int = Field(description="成功处理的文件数")
    failed_files: int = Field(description="失败的文件数")
    results: List[ProcessResult] = Field(description="处理结果列表")
    errors: List[Dict[str, str]] = Field(description="错误信息列表")
    total_processing_time: float = Field(description="总处理时间（秒）")
    
    class Config:
        schema_extra = {
            "example": {
                "total_files": 3,
                "successful_files": 2,
                "failed_files": 1,
                "results": [
                    {
                        "filename": "doc1.pdf",
                        "toc": [{"title": "Chapter 1", "level": 1, "page": 1}],
                        "total_pages": 50,
                        "processing_time": 10.2,
                        "model_used": "qwen2.5-vl-7b"
                    }
                ],
                "errors": [
                    {"filename": "doc3.pdf", "error": "文件损坏"}
                ],
                "total_processing_time": 25.8
            }
        }

class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str = Field(description="任务ID")
    status: TaskStatus = Field(description="任务状态")
    result: Optional[Union[ProcessResult, BatchProcessResult]] = Field(default=None, description="处理结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    progress: Optional[float] = Field(default=None, description="进度百分比")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "result": {
                    "filename": "document.pdf",
                    "toc": [{"title": "Chapter 1", "level": 1, "page": 1}],
                    "total_pages": 100,
                    "processing_time": 15.5,
                    "model_used": "qwen2.5-vl-7b"
                },
                "error": None,
                "progress": 100.0
            }
        }

class ModelInfo(BaseModel):
    """模型信息模型"""
    name: str = Field(description="模型名称")
    description: str = Field(description="模型描述")
    loaded: bool = Field(description="是否已加载")
    size: Optional[str] = Field(default=None, description="模型大小")
    parameters: Optional[str] = Field(default=None, description="参数数量")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "qwen2.5-vl-7b",
                "description": "Qwen2.5-VL 7B 多模态模型",
                "loaded": True,
                "size": "14.2GB",
                "parameters": "7B"
            }
        }

class ProcessorInfo(BaseModel):
    """处理器信息模型"""
    name: str = Field(description="处理器名称")
    description: str = Field(description="处理器描述")
    supported_formats: List[str] = Field(description="支持的文件格式")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "pdf_processor",
                "description": "PDF文档处理器",
                "supported_formats": [".pdf"]
            }
        }

class PluginInfo(BaseModel):
    """插件信息模型"""
    name: str = Field(description="插件名称")
    version: str = Field(description="插件版本")
    description: str = Field(description="插件描述")
    category: str = Field(description="插件类别")
    loaded: bool = Field(description="是否已加载")
    dependencies: Optional[List[str]] = Field(default=None, description="依赖列表")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "word_processor",
                "version": "1.0.0",
                "description": "Word文档处理插件",
                "category": "processor",
                "loaded": False,
                "dependencies": ["python-docx"]
            }
        }

class SystemInfo(BaseModel):
    """系统信息模型"""
    cpu_percent: float = Field(description="CPU使用率")
    memory_total: int = Field(description="总内存（字节）")
    memory_used: int = Field(description="已用内存（字节）")
    memory_percent: float = Field(description="内存使用率")
    disk_total: int = Field(description="总磁盘空间（字节）")
    disk_used: int = Field(description="已用磁盘空间（字节）")
    disk_percent: float = Field(description="磁盘使用率")
    gpu_available: bool = Field(description="GPU是否可用")
    gpu_count: int = Field(description="GPU数量")
    gpu_memory: List[Dict[str, Any]] = Field(description="GPU内存信息")
    
    class Config:
        schema_extra = {
            "example": {
                "cpu_percent": 25.5,
                "memory_total": 17179869184,
                "memory_used": 8589934592,
                "memory_percent": 50.0,
                "disk_total": 1073741824000,
                "disk_used": 536870912000,
                "disk_percent": 50.0,
                "gpu_available": True,
                "gpu_count": 1,
                "gpu_memory": [
                    {
                        "device": 0,
                        "name": "NVIDIA GeForce RTX 4090",
                        "total_memory": 25769803776
                    }
                ]
            }
        }

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(description="错误类型")
    message: str = Field(description="错误消息")
    detail: Optional[str] = Field(default=None, description="详细信息")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "输入参数无效",
                "detail": "model_name字段不能为空"
            }
        }

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(description="服务状态")
    version: str = Field(description="版本号")
    timestamp: str = Field(description="时间戳")
    uptime: float = Field(description="运行时间（秒）")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-01T12:00:00Z",
                "uptime": 3600.0
            }
        }