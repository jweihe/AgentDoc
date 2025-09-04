"""MetaAgent - 任务协调和分解Agent

负责接收用户请求，分解任务，协调其他Agent执行。
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging

from .base import BaseAgent, Task, TaskResult, TaskStatus, AgentCapability

logger = logging.getLogger(__name__)


class MetaAgent(BaseAgent):
    """元Agent - 负责任务分解和协调"""
    
    def __init__(self):
        super().__init__("MetaAgent")
        self.registered_agents: Dict[str, BaseAgent] = {}
        
    def get_capabilities(self) -> List[AgentCapability]:
        """获取MetaAgent能力"""
        return [AgentCapability.TASK_COORDINATION]
    
    def register_agent(self, agent: BaseAgent) -> None:
        """注册Agent"""
        self.registered_agents[agent.id] = agent
        logger.info(f"注册Agent: {agent.name} ({agent.id[:8]})")
    
    def unregister_agent(self, agent_id: str) -> None:
        """注销Agent"""
        if agent_id in self.registered_agents:
            agent = self.registered_agents.pop(agent_id)
            logger.info(f"注销Agent: {agent.name} ({agent_id[:8]})")
    
    async def process(self, task: Task) -> TaskResult:
        """处理任务 - 分解并协调执行"""
        try:
            logger.info(f"MetaAgent开始处理任务: {task.task_id}")
            
            # 分解任务
            subtasks = await self._decompose_task(task)
            
            # 分配任务给合适的Agent
            results = []
            for subtask in subtasks:
                agent = self._find_suitable_agent(subtask)
                if agent:
                    result = await agent.process(subtask)
                    results.append(result)
                else:
                    logger.warning(f"未找到合适的Agent处理任务: {subtask.task_type}")
                    results.append(TaskResult(
                        task_id=subtask.task_id,
                        status=TaskStatus.FAILED,
                        error="未找到合适的Agent"
                    ))
            
            # 合并结果
            final_result = await self._merge_results(task, results)
            
            logger.info(f"MetaAgent完成任务: {task.task_id}")
            return final_result
            
        except Exception as e:
            logger.error(f"MetaAgent处理任务失败: {e}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    async def _decompose_task(self, task: Task) -> List[Task]:
        """分解任务"""
        subtasks = []
        
        if task.task_type == "document_analysis":
            # 文档分析任务分解
            subtasks.extend([
                Task(
                    task_id=f"{task.task_id}_parse",
                    task_type="document_parsing",
                    data=task.data,
                    metadata={"parent_task": task.task_id}
                ),
                Task(
                    task_id=f"{task.task_id}_analyze",
                    task_type="text_analysis",
                    data=task.data,
                    metadata={"parent_task": task.task_id}
                )
            ])
        
        elif task.task_type == "question_answering":
            # 问答任务可能需要先分析文档
            if "document" in task.data:
                subtasks.append(Task(
                    task_id=f"{task.task_id}_parse",
                    task_type="document_parsing",
                    data={"file_path": task.data["document"]},
                    metadata={"parent_task": task.task_id}
                ))
            
            subtasks.append(Task(
                task_id=f"{task.task_id}_qa",
                task_type="question_answering",
                data=task.data,
                metadata={"parent_task": task.task_id}
            ))
        
        else:
            # 默认不分解
            subtasks.append(task)
        
        logger.info(f"任务 {task.task_id} 分解为 {len(subtasks)} 个子任务")
        return subtasks
    
    def _find_suitable_agent(self, task: Task) -> Optional[BaseAgent]:
        """找到合适的Agent处理任务"""
        for agent in self.registered_agents.values():
            if agent.can_handle(task):
                return agent
        return None
    
    async def _merge_results(self, original_task: Task, results: List[TaskResult]) -> TaskResult:
        """合并子任务结果"""
        # 检查是否有失败的子任务
        failed_results = [r for r in results if r.status == TaskStatus.FAILED]
        if failed_results:
            return TaskResult(
                task_id=original_task.task_id,
                status=TaskStatus.FAILED,
                error=f"子任务失败: {[r.error for r in failed_results]}"
            )
        
        # 合并成功结果
        merged_data = {}
        for result in results:
            if result.result:
                merged_data.update(result.result)
        
        return TaskResult(
            task_id=original_task.task_id,
            status=TaskStatus.COMPLETED,
            result=merged_data
        )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有注册Agent的状态"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.registered_agents.items()
        }
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """根据能力获取Agent列表"""
        return [
            agent for agent in self.registered_agents.values()
            if capability in agent.get_capabilities()
        ]