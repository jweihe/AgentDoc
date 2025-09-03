"""API路由定义"""

import asyncio
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, JSONResponse

from .models import (
    ProcessRequest, ProcessResponse, TaskStatus, TaskResponse,
    ModelInfo, ProcessorInfo, PluginInfo, SystemInfo
)
from .dependencies import get_model_manager, get_processor_factory, get_plugin_manager
from ..core.logger import get_logger
from ..core.exceptions import AgentDocError
from ..processors.pdf_processor import PDFProcessor
from ..processors.batch_processor import BatchProcessor

logger = get_logger(__name__)
router = APIRouter()

# 任务存储（生产环境应使用Redis或数据库）
tasks: Dict[str, Dict[str, Any]] = {}

@router.get("/", summary="API根路径")
async def api_root():
    """API根路径"""
    return {
        "message": "DocuMind API v1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 文档处理相关API
@router.post("/process/pdf", response_model=ProcessResponse, summary="处理PDF文档")
async def process_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF文件"),
    model_name: str = Form("qwen2.5-vl-7b", description="模型名称"),
    include_pages: bool = Form(True, description="是否包含页码"),
    cpu_mode: bool = Form(False, description="是否使用CPU模式"),
    model_manager = Depends(get_model_manager)
):
    """处理PDF文档
    
    上传PDF文件并提取目录结构。
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    try:
        # 生成任务ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 创建任务记录
        tasks[task_id] = {
            "status": "pending",
            "file_path": tmp_file_path,
            "filename": file.filename,
            "model_name": model_name,
            "include_pages": include_pages,
            "cpu_mode": cpu_mode,
            "result": None,
            "error": None
        }
        
        # 添加后台任务
        background_tasks.add_task(
            process_pdf_task,
            task_id,
            tmp_file_path,
            model_name,
            include_pages,
            cpu_mode
        )
        
        return ProcessResponse(
            task_id=task_id,
            status="pending",
            message="PDF处理任务已提交"
        )
    
    except Exception as e:
        logger.error(f"PDF处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

async def process_pdf_task(
    task_id: str,
    file_path: str,
    model_name: str,
    include_pages: bool,
    cpu_mode: bool
):
    """PDF处理后台任务"""
    try:
        tasks[task_id]["status"] = "processing"
        
        # 加载模型
        from ..models.manager import get_model_manager
        model_manager = get_model_manager()
        
        model = await model_manager.load_model(model_name)
        
        # 创建处理器
        config = {
            "include_pages": include_pages,
            "cpu_mode": cpu_mode
        }
        processor = PDFProcessor(config)
        
        # 处理PDF
        with tempfile.TemporaryDirectory() as output_dir:
            result = await processor.process(file_path, output_dir, model)
            
            # 保存结果
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = result
    
    except Exception as e:
        logger.error(f"PDF处理任务失败 {task_id}: {e}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
    
    finally:
        # 清理临时文件
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")

@router.post("/process/batch", response_model=ProcessResponse, summary="批量处理文档")
async def process_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="文档文件列表"),
    model_name: str = Form("qwen2.5-vl-7b", description="模型名称"),
    include_pages: bool = Form(True, description="是否包含页码"),
    cpu_mode: bool = Form(False, description="是否使用CPU模式"),
    max_concurrent: int = Form(3, description="最大并发数")
):
    """批量处理文档"""
    try:
        # 生成任务ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # 保存上传的文件
        temp_files = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_files.append({
                    "path": tmp_file.name,
                    "filename": file.filename
                })
        
        if not temp_files:
            raise HTTPException(status_code=400, detail="没有有效的PDF文件")
        
        # 创建任务记录
        tasks[task_id] = {
            "status": "pending",
            "files": temp_files,
            "model_name": model_name,
            "include_pages": include_pages,
            "cpu_mode": cpu_mode,
            "max_concurrent": max_concurrent,
            "result": None,
            "error": None
        }
        
        # 添加后台任务
        background_tasks.add_task(
            process_batch_task,
            task_id,
            temp_files,
            model_name,
            include_pages,
            cpu_mode,
            max_concurrent
        )
        
        return ProcessResponse(
            task_id=task_id,
            status="pending",
            message=f"批量处理任务已提交，共{len(temp_files)}个文件"
        )
    
    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

async def process_batch_task(
    task_id: str,
    files: List[Dict[str, str]],
    model_name: str,
    include_pages: bool,
    cpu_mode: bool,
    max_concurrent: int
):
    """批量处理后台任务"""
    try:
        tasks[task_id]["status"] = "processing"
        
        # 加载模型
        from ..models.manager import get_model_manager
        model_manager = get_model_manager()
        
        model = await model_manager.load_model(model_name)
        
        # 创建批量处理器
        config = {
            "include_pages": include_pages,
            "cpu_mode": cpu_mode,
            "max_concurrent": max_concurrent
        }
        processor = BatchProcessor(config)
        
        # 处理文件
        with tempfile.TemporaryDirectory() as output_dir:
            file_paths = [f["path"] for f in files]
            result = await processor.process(file_paths, output_dir, model)
            
            # 保存结果
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = result
    
    except Exception as e:
        logger.error(f"批量处理任务失败 {task_id}: {e}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
    
    finally:
        # 清理临时文件
        for file_info in files:
            try:
                Path(file_info["path"]).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")

@router.get("/task/{task_id}", response_model=TaskResponse, summary="获取任务状态")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error")
    )

@router.delete("/task/{task_id}", summary="删除任务")
async def delete_task(task_id: str):
    """删除任务"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del tasks[task_id]
    return {"message": "任务已删除"}

@router.get("/tasks", summary="获取所有任务")
async def list_tasks():
    """获取所有任务列表"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "filename": task.get("filename") or f"{len(task.get('files', []))} files"
            }
            for task_id, task in tasks.items()
        ]
    }

# 模型管理API
@router.get("/models", response_model=List[ModelInfo], summary="获取可用模型列表")
async def list_models(model_manager = Depends(get_model_manager)):
    """获取可用模型列表"""
    try:
        from ..models.factory import get_model_factory
        factory = get_model_factory()
        
        models = factory.list_models()
        model_infos = []
        
        for model_name in models:
            try:
                info = factory.get_model_info(model_name)
                model_infos.append(ModelInfo(
                    name=model_name,
                    description=info.get("description", ""),
                    loaded=model_manager.is_model_loaded(model_name)
                ))
            except Exception as e:
                logger.warning(f"获取模型信息失败 {model_name}: {e}")
        
        return model_infos
    
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@router.post("/models/{model_name}/load", summary="加载模型")
async def load_model(model_name: str, model_manager = Depends(get_model_manager)):
    """加载指定模型"""
    try:
        model = await model_manager.load_model(model_name)
        return {
            "message": f"模型 {model_name} 加载成功",
            "model_info": model.get_model_info()
        }
    
    except Exception as e:
        logger.error(f"加载模型失败 {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"加载模型失败: {str(e)}")

@router.post("/models/{model_name}/unload", summary="卸载模型")
async def unload_model(model_name: str, model_manager = Depends(get_model_manager)):
    """卸载指定模型"""
    try:
        await model_manager.unload_model(model_name)
        return {"message": f"模型 {model_name} 卸载成功"}
    
    except Exception as e:
        logger.error(f"卸载模型失败 {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"卸载模型失败: {str(e)}")

# 处理器管理API
@router.get("/processors", response_model=List[ProcessorInfo], summary="获取可用处理器列表")
async def list_processors(factory = Depends(get_processor_factory)):
    """获取可用处理器列表"""
    try:
        processors = factory.list_processors()
        processor_infos = []
        
        for processor_name in processors:
            try:
                info = factory.get_processor_info(processor_name)
                processor_infos.append(ProcessorInfo(
                    name=processor_name,
                    description=info.get("description", ""),
                    supported_formats=info.get("supported_formats", [])
                ))
            except Exception as e:
                logger.warning(f"获取处理器信息失败 {processor_name}: {e}")
        
        return processor_infos
    
    except Exception as e:
        logger.error(f"获取处理器列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取处理器列表失败: {str(e)}")

# 插件管理API
@router.get("/plugins", response_model=List[PluginInfo], summary="获取插件列表")
async def list_plugins(plugin_manager = Depends(get_plugin_manager)):
    """获取插件列表"""
    try:
        available_plugins = plugin_manager.list_available_plugins()
        loaded_plugins = plugin_manager.list_loaded_plugins()
        
        plugin_infos = []
        for plugin_name in available_plugins:
            try:
                info = plugin_manager.get_plugin_info(plugin_name)
                plugin_infos.append(PluginInfo(
                    name=plugin_name,
                    version=info.get("version", ""),
                    description=info.get("description", ""),
                    category=info.get("category", ""),
                    loaded=plugin_name in loaded_plugins
                ))
            except Exception as e:
                logger.warning(f"获取插件信息失败 {plugin_name}: {e}")
        
        return plugin_infos
    
    except Exception as e:
        logger.error(f"获取插件列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取插件列表失败: {str(e)}")

# 系统信息API
@router.get("/system/info", response_model=SystemInfo, summary="获取系统信息")
async def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        import torch
        
        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU信息
        gpu_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count() if gpu_available else 0
        gpu_memory = []
        
        if gpu_available:
            for i in range(gpu_count):
                gpu_mem = torch.cuda.get_device_properties(i)
                gpu_memory.append({
                    "device": i,
                    "name": gpu_mem.name,
                    "total_memory": gpu_mem.total_memory
                })
        
        return SystemInfo(
            cpu_percent=cpu_percent,
            memory_total=memory.total,
            memory_used=memory.used,
            memory_percent=memory.percent,
            disk_total=disk.total,
            disk_used=disk.used,
            disk_percent=(disk.used / disk.total) * 100,
            gpu_available=gpu_available,
            gpu_count=gpu_count,
            gpu_memory=gpu_memory
        )
    
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")