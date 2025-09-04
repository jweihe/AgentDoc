"""任务队列基础类

定义任务、任务状态、任务结果等基础数据结构。
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime
import uuid
import json

from ..core.logger import get_logger

logger = get_logger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"      # 执行超时


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """从字典创建实例"""
        return cls(
            task_id=data["task_id"],
            status=TaskStatus(data["status"]),
            result=data.get("result"),
            error=data.get("error"),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            execution_time=data.get("execution_time"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Task:
    """任务类"""
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 运行时状态
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    worker_id: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not callable(self.func):
            raise ValueError("func must be callable")
        
        # 如果没有指定调度时间，使用创建时间
        if self.scheduled_at is None:
            self.scheduled_at = self.created_at
    
    def execute(self) -> TaskResult:
        """执行任务"""
        start_time = datetime.now()
        
        try:
            logger.info(f"开始执行任务 {self.task_id}")
            self.status = TaskStatus.RUNNING
            
            # 执行任务函数
            result = self.func(*self.args, **self.kwargs)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 创建成功结果
            task_result = TaskResult(
                task_id=self.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                metadata=self.metadata.copy()
            )
            
            self.status = TaskStatus.COMPLETED
            self.result = task_result
            
            logger.info(
                f"任务 {self.task_id} 执行成功，耗时 {execution_time:.2f}s"
            )
            
            return task_result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_msg = str(e)
            logger.error(f"任务 {self.task_id} 执行失败: {error_msg}")
            
            # 创建失败结果
            task_result = TaskResult(
                task_id=self.task_id,
                status=TaskStatus.FAILED,
                error=error_msg,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                metadata=self.metadata.copy()
            )
            
            self.status = TaskStatus.FAILED
            self.result = task_result
            
            return task_result
    
    def can_retry(self) -> bool:
        """检查是否可以重试"""
        return (
            self.status == TaskStatus.FAILED and 
            self.retry_count < self.max_retries
        )
    
    def reset_for_retry(self) -> None:
        """重置任务状态以便重试"""
        if not self.can_retry():
            raise ValueError("任务不能重试")
        
        self.retry_count += 1
        self.status = TaskStatus.PENDING
        self.result = None
        self.worker_id = None
        
        logger.info(f"任务 {self.task_id} 准备第 {self.retry_count} 次重试")
    
    def cancel(self) -> None:
        """取消任务"""
        if self.status == TaskStatus.RUNNING:
            logger.warning(f"任务 {self.task_id} 正在运行，无法取消")
            return
        
        self.status = TaskStatus.CANCELLED
        logger.info(f"任务 {self.task_id} 已取消")
    
    def is_ready(self) -> bool:
        """检查任务是否准备执行"""
        if self.status != TaskStatus.PENDING:
            return False
        
        if self.scheduled_at and self.scheduled_at > datetime.now():
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "task_id": self.task_id,
            "func_name": getattr(self.func, '__name__', str(self.func)),
            "args": self.args,
            "kwargs": self.kwargs,
            "priority": self.priority.value,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "metadata": self.metadata,
            "status": self.status.value,
            "worker_id": self.worker_id,
        }
    
    def __lt__(self, other: "Task") -> bool:
        """用于优先级队列排序"""
        if not isinstance(other, Task):
            return NotImplemented
        
        # 优先级高的任务排在前面
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        
        # 相同优先级按创建时间排序
        return self.created_at < other.created_at
    
    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id[:8]}, "
            f"func={getattr(self.func, '__name__', 'unknown')}, "
            f"status={self.status.value}, "
            f"priority={self.priority.value})"
        )