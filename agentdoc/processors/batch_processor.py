# -*- coding: utf-8 -*-
"""
批处理器模块

提供批量处理文档的功能。
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseProcessor
from ..core.exceptions import ProcessingError
from ..core.logger import get_logger


class BatchProcessor(BaseProcessor):
    """批处理器
    
    用于批量处理多个文档。
    """
    
    def __init__(self, max_workers: int = 4, timeout: int = 300):
        """初始化批处理器
        
        Args:
            max_workers: 最大工作线程数
            timeout: 处理超时时间（秒）
        """
        super().__init__()
        self.max_workers = max_workers
        self.timeout = timeout
        self.logger = get_logger(__name__)
        
    async def process(self, input_path, output_dir, **kwargs):
        """处理单个文档（基类方法实现）
        
        Args:
            input_path: 输入文件路径
            output_dir: 输出目录路径
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        # 这里可以实现单个文档的处理逻辑
        return {"status": "success", "input_path": str(input_path), "output_dir": str(output_dir)}
    
    def validate_input(self, input_path):
        """验证输入文件
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            验证是否通过
        """
        path = Path(input_path)
        return path.exists() and path.is_file()
        
    def process_batch(self, 
                     file_paths: List[str], 
                     processor_func: Callable,
                     progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """批量处理文件
        
        Args:
            file_paths: 文件路径列表
            processor_func: 处理函数
            progress_callback: 进度回调函数
            
        Returns:
            处理结果字典，键为文件路径，值为处理结果
        """
        results = {}
        errors = {}
        
        self.logger.info(f"开始批量处理 {len(file_paths)} 个文件")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_path = {
                executor.submit(self._process_single_file, path, processor_func): path
                for path in file_paths
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_path, timeout=self.timeout):
                file_path = future_to_path[future]
                completed += 1
                
                try:
                    result = future.result()
                    results[file_path] = result
                    self.logger.debug(f"成功处理文件: {file_path}")
                except Exception as e:
                    error_msg = f"处理文件失败 {file_path}: {str(e)}"
                    self.logger.error(error_msg)
                    errors[file_path] = str(e)
                    
                # 调用进度回调
                if progress_callback:
                    progress_callback(completed, len(file_paths), file_path)
                    
        self.logger.info(f"批量处理完成: 成功 {len(results)} 个，失败 {len(errors)} 个")
        
        return {
            'results': results,
            'errors': errors,
            'summary': {
                'total': len(file_paths),
                'success': len(results),
                'failed': len(errors)
            }
        }
        
    def _process_single_file(self, file_path: str, processor_func: Callable) -> Any:
        """处理单个文件
        
        Args:
            file_path: 文件路径
            processor_func: 处理函数
            
        Returns:
            处理结果
        """
        try:
            # 检查文件是否存在
            if not Path(file_path).exists():
                raise ProcessingError(f"文件不存在: {file_path}")
                
            # 调用处理函数
            result = processor_func(file_path)
            return result
            
        except Exception as e:
            raise ProcessingError(f"处理文件失败 {file_path}: {str(e)}")
            
    async def process_batch_async(self, 
                                 file_paths: List[str], 
                                 processor_func: Callable,
                                 progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """异步批量处理文件
        
        Args:
            file_paths: 文件路径列表
            processor_func: 处理函数
            progress_callback: 进度回调函数
            
        Returns:
            处理结果字典
        """
        results = {}
        errors = {}
        
        self.logger.info(f"开始异步批量处理 {len(file_paths)} 个文件")
        
        # 创建任务
        tasks = []
        for file_path in file_paths:
            task = asyncio.create_task(
                self._process_single_file_async(file_path, processor_func)
            )
            tasks.append((task, file_path))
            
        # 等待所有任务完成
        completed = 0
        for task, file_path in tasks:
            try:
                result = await task
                results[file_path] = result
                self.logger.debug(f"成功处理文件: {file_path}")
            except Exception as e:
                error_msg = f"处理文件失败 {file_path}: {str(e)}"
                self.logger.error(error_msg)
                errors[file_path] = str(e)
                
            completed += 1
            if progress_callback:
                progress_callback(completed, len(file_paths), file_path)
                
        self.logger.info(f"异步批量处理完成: 成功 {len(results)} 个，失败 {len(errors)} 个")
        
        return {
            'results': results,
            'errors': errors,
            'summary': {
                'total': len(file_paths),
                'success': len(results),
                'failed': len(errors)
            }
        }
        
    async def _process_single_file_async(self, file_path: str, processor_func: Callable) -> Any:
        """异步处理单个文件
        
        Args:
            file_path: 文件路径
            processor_func: 处理函数
            
        Returns:
            处理结果
        """
        try:
            # 检查文件是否存在
            if not Path(file_path).exists():
                raise ProcessingError(f"文件不存在: {file_path}")
                
            # 在线程池中运行处理函数
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, processor_func, file_path)
            return result
            
        except Exception as e:
            raise ProcessingError(f"处理文件失败 {file_path}: {str(e)}")