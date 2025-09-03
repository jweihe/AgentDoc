"""任务队列管理器

提供任务队列的管理功能，包括任务调度、状态跟踪等。
"""

from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime, timedelta
import threading
import heapq
import time

from .base import Task, TaskStatus, TaskPriority, TaskResult
from ..core.logger import get_logger
from ..core.exceptions import QueueError

logger = get_logger(__name__)


class TaskManager:
    """任务管理器
    
    负责单个任务的生命周期管理。
    """
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._results: Dict[str, TaskResult] = {}
        self._lock = threading.RLock()
        
        logger.info("初始化任务管理器")
    
    def add_task(self, task: Task) -> str:
        """添加任务"""
        with self._lock:
            if task.task_id in self._tasks:
                raise QueueError(f"任务 {task.task_id} 已存在")
            
            self._tasks[task.task_id] = task
            logger.info(f"添加任务: {task.task_id}")
            return task.task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self._lock:
            return self._tasks.get(task_id)
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks.pop(task_id)
                logger.info(f"移除任务: {task_id}")
                return True
            return False
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """更新任务状态"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].status = status
                logger.debug(f"更新任务 {task_id} 状态为 {status.value}")
                return True
            return False
    
    def save_result(self, result: TaskResult) -> None:
        """保存任务结果"""
        with self._lock:
            self._results[result.task_id] = result
            logger.debug(f"保存任务结果: {result.task_id}")
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        with self._lock:
            return self._results.get(task_id)
    
    def list_tasks(
        self, 
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """列出任务"""
        with self._lock:
            tasks = list(self._tasks.values())
            
            if status:
                tasks = [t for t in tasks if t.status == status]
            
            if priority:
                tasks = [t for t in tasks if t.priority == priority]
            
            return tasks
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            status_counts = defaultdict(int)
            priority_counts = defaultdict(int)
            
            for task in self._tasks.values():
                status_counts[task.status.value] += 1
                priority_counts[task.priority.value] += 1
            
            return {
                "total_tasks": len(self._tasks),
                "total_results": len(self._results),
                "status_counts": dict(status_counts),
                "priority_counts": dict(priority_counts),
            }
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """清理已完成的旧任务"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            tasks_to_remove = []
            for task_id, task in self._tasks.items():
                if (
                    task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                    task.created_at < cutoff_time
                ):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                self._tasks.pop(task_id, None)
                self._results.pop(task_id, None)
            
            logger.info(f"清理了 {len(tasks_to_remove)} 个旧任务")
            return len(tasks_to_remove)


class QueueManager:
    """队列管理器
    
    负责任务队列的调度和执行管理。
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.max_queue_size = max_queue_size
        self._queue: List[Task] = []
        self._task_manager = TaskManager()
        self._lock = threading.RLock()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        
        logger.info(f"初始化队列管理器，最大队列大小: {max_queue_size}")
    
    def submit_task(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        scheduled_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """提交任务到队列"""
        with self._lock:
            if len(self._queue) >= self.max_queue_size:
                raise QueueError(f"队列已满，最大容量: {self.max_queue_size}")
            
            # 创建任务
            task = Task(
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority,
                timeout=timeout,
                max_retries=max_retries,
                scheduled_at=scheduled_at,
                metadata=metadata or {}
            )
            
            # 添加到任务管理器
            self._task_manager.add_task(task)
            
            # 添加到队列
            heapq.heappush(self._queue, task)
            
            logger.info(
                f"提交任务 {task.task_id}，优先级: {priority.value}"
            )
            
            return task.task_id
    
    def get_next_task(self) -> Optional[Task]:
        """获取下一个待执行的任务"""
        with self._lock:
            while self._queue:
                task = heapq.heappop(self._queue)
                
                # 检查任务是否准备执行
                if task.is_ready():
                    return task
                
                # 如果任务还没到执行时间，重新放回队列
                if task.status == TaskStatus.PENDING:
                    heapq.heappush(self._queue, task)
                    break
            
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            task = self._task_manager.get_task(task_id)
            if not task:
                return False
            
            if task.status == TaskStatus.RUNNING:
                logger.warning(f"任务 {task_id} 正在运行，无法取消")
                return False
            
            task.cancel()
            
            # 从队列中移除
            self._queue = [t for t in self._queue if t.task_id != task_id]
            heapq.heapify(self._queue)
            
            logger.info(f"取消任务: {task_id}")
            return True
    
    def retry_task(self, task_id: str) -> bool:
        """重试失败的任务"""
        with self._lock:
            task = self._task_manager.get_task(task_id)
            if not task or not task.can_retry():
                return False
            
            task.reset_for_retry()
            heapq.heappush(self._queue, task)
            
            logger.info(f"重试任务: {task_id}")
            return True
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        task = self._task_manager.get_task(task_id)
        return task.status if task else None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self._task_manager.get_result(task_id)
    
    def wait_for_task(
        self, 
        task_id: str, 
        timeout: Optional[float] = None
    ) -> Optional[TaskResult]:
        """等待任务完成"""
        start_time = time.time()
        
        while True:
            result = self.get_task_result(task_id)
            if result:
                return result
            
            task = self._task_manager.get_task(task_id)
            if not task or task.status in [
                TaskStatus.COMPLETED, 
                TaskStatus.FAILED, 
                TaskStatus.CANCELLED
            ]:
                break
            
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"等待任务 {task_id} 超时")
                break
            
            time.sleep(0.1)
        
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        with self._lock:
            stats = self._task_manager.get_statistics()
            stats.update({
                "queue_size": len(self._queue),
                "max_queue_size": self.max_queue_size,
                "is_running": self._running,
            })
            return stats
    
    def start_scheduler(self) -> None:
        """启动调度器"""
        if self._running:
            logger.warning("调度器已在运行")
            return
        
        self._running = True
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self._scheduler_thread.start()
        
        logger.info("启动任务调度器")
    
    def stop_scheduler(self) -> None:
        """停止调度器"""
        if not self._running:
            return
        
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
        
        logger.info("停止任务调度器")
    
    def _scheduler_loop(self) -> None:
        """调度器主循环"""
        while self._running:
            try:
                # 这里可以添加自动调度逻辑
                # 比如检查延迟任务、清理过期任务等
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"调度器循环出错: {e}")
    
    def cleanup(self) -> None:
        """清理资源"""
        self.stop_scheduler()
        with self._lock:
            self._queue.clear()
        
        logger.info("清理队列管理器")
    
    def __del__(self):
        """析构函数"""
        try:
            self.cleanup()
        except Exception:
            pass


# 全局队列管理器实例
_queue_manager = QueueManager()


def get_queue_manager() -> QueueManager:
    """获取全局队列管理器实例"""
    return _queue_manager


def submit_task(
    func: Callable,
    *args,
    priority: TaskPriority = TaskPriority.NORMAL,
    **kwargs
) -> str:
    """便捷函数：提交任务"""
    return _queue_manager.submit_task(func, *args, priority=priority, **kwargs)