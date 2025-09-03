"""基础Agent框架

定义Agent的基础接口和通用功能。"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..core.logger import get_logger

logger = get_logger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentCapability(Enum):
    """Agent能力枚举"""
    DOCUMENT_PARSING = "document_parsing"
    TEXT_ANALYSIS = "text_analysis"
    QUESTION_ANSWERING = "question_answering"
    REASONING = "reasoning"
    TASK_COORDINATION = "task_coordination"


@dataclass
class Task:
    """任务定义"""
    task_id: str
    task_type: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    """Agent间消息"""
    sender: str
    receiver: str
    content: Any
    message_type: str = "data"
    timestamp: datetime = field(default_factory=datetime.now)


class AgentError(Exception):
    """Agent相关异常"""
    pass


class BaseAgent(ABC):
    """基础Agent类
    
    所有Agent的基类，定义了Agent的基本接口和行为。
    """
    
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.memory: Dict[str, Any] = {}
        self.state = TaskStatus.PENDING
        
        logger.info(f"Agent {self.name} ({self.id[:8]}) 初始化完成")
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """获取Agent能力列表"""
        pass
    
    @abstractmethod
    async def process(self, task: Task) -> TaskResult:
        """处理任务
        
        Args:
            task: 要处理的任务
            
        Returns:
            任务结果
        """
        pass
    
    def can_handle(self, task: Task) -> bool:
        """检查是否能处理指定任务"""
        capabilities = self.get_capabilities()
        # 简单的任务类型匹配
        for capability in capabilities:
            if capability.value in task.task_type:
                return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态信息"""
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "memory_size": len(self.memory)
        }
    
    def save_memory(self, key: str, value: Any) -> None:
        """保存记忆"""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now()
        }
    
    def get_memory(self, key: str) -> Any:
        """获取记忆"""
        memory_item = self.memory.get(key)
        return memory_item["value"] if memory_item else None
    
    def clear_memory(self) -> None:
        """清除记忆"""
        self.memory.clear()
    
    def __str__(self) -> str:
        return f"Agent({self.name}, {self.id[:8]}, {self.state.value})"
    
    def __repr__(self) -> str:
        return self.__str__()