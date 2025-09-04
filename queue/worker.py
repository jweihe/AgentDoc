"""任务工作器

提供任务执行的工作器实现。
"""

from typing import Optional, List, Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future
import threading
import time
import signal
import uuid

from .base import Task, TaskStatus, TaskResult
from .manager import QueueManager, get_queue_manager
from ..core.logger import get_logger
from ..core.exceptions import WorkerError

logger = get_logger(__name__)


class TaskWorker:
    """任务工作器
    
    负责从队列中获取任务并执行。
    """
    
    def __init__(
        self, 
        worker_id: Optional[str] = None,
        queue_manager: Optional[QueueManager] = None
    ):
        self.worker_id = worker_id or str(uuid.uuid4())
        self.queue_manager = queue_manager or get_queue_manager()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_task: Optional[Task] = None
        self._lock = threading.RLock()
        
        logger.info(f"初始化工作器: {self.worker_id}")
    
    def start(self) -> None:
        """启动工作器"""
        with self._lock:
            if self._running:
                logger.warning(f"工作器 {self.worker_id} 已在运行")
                return
            
            self._running = True
            self._thread = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{self.worker_id}",
                daemon=True
            )
            self._thread.start()
            
            logger.info(f"启动工作器: {self.worker_id}")
    
    def stop(self, timeout: float = 5.0) -> None:
        """停止工作器"""
        with self._lock:
            if not self._running:
                return
            
            self._running = False
            
            # 等待当前任务完成
            if self._thread:
                self._thread.join(timeout=timeout)
                
                if self._thread.is_alive():
                    logger.warning(
                        f"工作器 {self.worker_id} 在 {timeout}s 内未能停止"
                    )
            
            logger.info(f"停止工作器: {self.worker_id}")
    
    def is_running(self) -> bool:
        """检查工作器是否在运行"""
        return self._running
    
    def get_current_task(self) -> Optional[Task]:
        """获取当前执行的任务"""
        with self._lock:
            return self._current_task
    
    def execute_task(self, task: Task) -> TaskResult:
        """执行单个任务"""
        with self._lock:
            self._current_task = task
            task.worker_id = self.worker_id
        
        try:
            logger.info(f"工作器 {self.worker_id} 开始执行任务 {task.task_id}")
            
            # 更新任务状态
            self.queue_manager._task_manager.update_task_status(
                task.task_id, TaskStatus.RUNNING
            )
            
            # 执行任务
            result = task.execute()
            
            # 保存结果
            self.queue_manager._task_manager.save_result(result)
            
            logger.info(
                f"工作器 {self.worker_id} 完成任务 {task.task_id}，"
                f"状态: {result.status.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"工作器 {self.worker_id} 执行任务 {task.task_id} 时出错: {e}"
            )
            raise WorkerError(f"任务执行失败: {e}")
        
        finally:
            with self._lock:
                self._current_task = None
                task.worker_id = None
    
    def _worker_loop(self) -> None:
        """工作器主循环"""
        logger.info(f"工作器 {self.worker_id} 开始工作循环")
        
        while self._running:
            try:
                # 获取下一个任务
                task = self.queue_manager.get_next_task()
                
                if task is None:
                    # 没有任务，短暂休眠
                    time.sleep(0.1)
                    continue
                
                # 执行任务
                self.execute_task(task)
                
            except Exception as e:
                logger.error(f"工作器 {self.worker_id} 循环出错: {e}")
                time.sleep(1.0)  # 出错后稍长时间休眠
        
        logger.info(f"工作器 {self.worker_id} 结束工作循环")
    
    def get_status(self) -> dict:
        """获取工作器状态"""
        with self._lock:
            current_task_id = None
            if self._current_task:
                current_task_id = self._current_task.task_id
            
            return {
                "worker_id": self.worker_id,
                "running": self._running,
                "current_task": current_task_id,
                "thread_alive": self._thread.is_alive() if self._thread else False,
            }
    
    def __repr__(self) -> str:
        return f"TaskWorker(id={self.worker_id}, running={self._running})"


class WorkerPool:
    """工作器池
    
    管理多个工作器的生命周期。
    """
    
    def __init__(
        self, 
        pool_size: int = 4,
        queue_manager: Optional[QueueManager] = None
    ):
        self.pool_size = pool_size
        self.queue_manager = queue_manager or get_queue_manager()
        self._workers: List[TaskWorker] = []
        self._running = False
        self._lock = threading.RLock()
        
        logger.info(f"初始化工作器池，大小: {pool_size}")
    
    def start(self) -> None:
        """启动工作器池"""
        with self._lock:
            if self._running:
                logger.warning("工作器池已在运行")
                return
            
            self._running = True
            
            # 创建并启动工作器
            for i in range(self.pool_size):
                worker = TaskWorker(
                    worker_id=f"worker-{i+1}",
                    queue_manager=self.queue_manager
                )
                worker.start()
                self._workers.append(worker)
            
            logger.info(f"启动工作器池，包含 {len(self._workers)} 个工作器")
    
    def stop(self, timeout: float = 10.0) -> None:
        """停止工作器池"""
        with self._lock:
            if not self._running:
                return
            
            self._running = False
            
            # 停止所有工作器
            for worker in self._workers:
                try:
                    worker.stop(timeout=timeout / len(self._workers))
                except Exception as e:
                    logger.error(f"停止工作器 {worker.worker_id} 时出错: {e}")
            
            self._workers.clear()
            
            logger.info("停止工作器池")
    
    def resize(self, new_size: int) -> None:
        """调整工作器池大小"""
        with self._lock:
            if not self._running:
                self.pool_size = new_size
                return
            
            current_size = len(self._workers)
            
            if new_size > current_size:
                # 增加工作器
                for i in range(current_size, new_size):
                    worker = TaskWorker(
                        worker_id=f"worker-{i+1}",
                        queue_manager=self.queue_manager
                    )
                    worker.start()
                    self._workers.append(worker)
                
                logger.info(f"工作器池扩展到 {new_size} 个工作器")
            
            elif new_size < current_size:
                # 减少工作器
                workers_to_stop = self._workers[new_size:]
                self._workers = self._workers[:new_size]
                
                for worker in workers_to_stop:
                    try:
                        worker.stop()
                    except Exception as e:
                        logger.error(f"停止工作器 {worker.worker_id} 时出错: {e}")
                
                logger.info(f"工作器池缩减到 {new_size} 个工作器")
            
            self.pool_size = new_size
    
    def get_workers(self) -> List[TaskWorker]:
        """获取所有工作器"""
        with self._lock:
            return self._workers.copy()
    
    def get_active_workers(self) -> List[TaskWorker]:
        """获取活跃的工作器"""
        with self._lock:
            return [w for w in self._workers if w.is_running()]
    
    def get_busy_workers(self) -> List[TaskWorker]:
        """获取正在执行任务的工作器"""
        with self._lock:
            return [w for w in self._workers if w.get_current_task() is not None]
    
    def get_status(self) -> dict:
        """获取工作器池状态"""
        with self._lock:
            active_workers = self.get_active_workers()
            busy_workers = self.get_busy_workers()
            
            worker_statuses = [w.get_status() for w in self._workers]
            
            return {
                "pool_size": self.pool_size,
                "total_workers": len(self._workers),
                "active_workers": len(active_workers),
                "busy_workers": len(busy_workers),
                "idle_workers": len(active_workers) - len(busy_workers),
                "running": self._running,
                "workers": worker_statuses,
            }
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """等待所有任务完成"""
        start_time = time.time()
        
        while True:
            busy_workers = self.get_busy_workers()
            if not busy_workers:
                return True
            
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"等待任务完成超时，仍有 {len(busy_workers)} 个工作器忙碌")
                return False
            
            time.sleep(0.1)
    
    def __del__(self):
        """析构函数"""
        try:
            self.stop()
        except Exception:
            pass
    
    def __repr__(self) -> str:
        return (
            f"WorkerPool(size={self.pool_size}, "
            f"running={self._running}, "
            f"workers={len(self._workers)})"
        )


# 全局工作器池实例
_worker_pool = WorkerPool()


def get_worker_pool() -> WorkerPool:
    """获取全局工作器池实例"""
    return _worker_pool


def start_workers(pool_size: int = 4) -> None:
    """便捷函数：启动工作器池"""
    global _worker_pool
    _worker_pool.pool_size = pool_size
    _worker_pool.start()


def stop_workers() -> None:
    """便捷函数：停止工作器池"""
    _worker_pool.stop()