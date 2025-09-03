"""CoordinatorAgent - 协调代理

负责管理和协调多个代理之间的任务分配和协作。
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .base import BaseAgent, Task, TaskResult, TaskStatus, AgentCapability, Message

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """协调代理
    
    负责任务分发、代理协调和结果汇总。
    """
    
    def __init__(self):
        super().__init__("CoordinatorAgent")
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        
    def get_capabilities(self) -> List[AgentCapability]:
        """获取CoordinatorAgent能力"""
        return [AgentCapability.TASK_COORDINATION]
    
    async def process(self, task: Task) -> TaskResult:
        """处理协调任务"""
        try:
            if task.task_type == "task_coordination":
                return await self._coordinate_task(task)
            elif task.task_type == "agent_management":
                return await self._manage_agents(task)
            elif task.task_type == "workflow_execution":
                return await self._execute_workflow(task)
            else:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"不支持的任务类型: {task.task_type}"
                )
                
        except Exception as e:
            logger.error(f"协调任务失败: {e}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """注册代理"""
        try:
            self.registered_agents[agent.id] = agent
            logger.info(f"代理 {agent.name} ({agent.id[:8]}) 注册成功")
            return True
        except Exception as e:
            logger.error(f"代理注册失败: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """注销代理"""
        try:
            if agent_id in self.registered_agents:
                agent = self.registered_agents.pop(agent_id)
                logger.info(f"代理 {agent.name} ({agent_id[:8]}) 注销成功")
                return True
            else:
                logger.warning(f"代理 {agent_id[:8]} 未找到")
                return False
        except Exception as e:
            logger.error(f"代理注销失败: {e}")
            return False
    
    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """获取已注册的代理列表"""
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "capabilities": [cap.value for cap in agent.get_capabilities()],
                "status": agent.get_status()
            }
            for agent in self.registered_agents.values()
        ]
    
    async def _coordinate_task(self, task: Task) -> TaskResult:
        """协调任务分配"""
        subtasks = task.data.get("subtasks", [])
        coordination_strategy = task.data.get("strategy", "parallel")
        
        if not subtasks:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="缺少子任务"
            )
        
        if coordination_strategy == "parallel":
            results = await self._execute_parallel_tasks(subtasks)
        elif coordination_strategy == "sequential":
            results = await self._execute_sequential_tasks(subtasks)
        elif coordination_strategy == "pipeline":
            results = await self._execute_pipeline_tasks(subtasks)
        else:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=f"不支持的协调策略: {coordination_strategy}"
            )
        
        # 汇总结果
        summary = self._summarize_results(results)
        
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            result={
                "strategy": coordination_strategy,
                "subtask_results": results,
                "summary": summary
            }
        )
    
    async def _execute_parallel_tasks(self, subtasks: List[Dict[str, Any]]) -> List[TaskResult]:
        """并行执行任务"""
        tasks_to_execute = []
        
        for subtask_data in subtasks:
            task = Task(
                task_id=f"subtask_{len(self.active_tasks)}_{datetime.now().timestamp()}",
                task_type=subtask_data.get("task_type"),
                data=subtask_data.get("data", {}),
                metadata=subtask_data.get("metadata", {})
            )
            
            # 找到合适的代理
            agent = self._find_suitable_agent(task)
            if agent:
                tasks_to_execute.append((task, agent))
            else:
                logger.warning(f"未找到合适的代理处理任务: {task.task_type}")
        
        # 并行执行
        results = await asyncio.gather(
            *[agent.process(task) for task, agent in tasks_to_execute],
            return_exceptions=True
        )
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                task, _ = tasks_to_execute[i]
                processed_results.append(TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_sequential_tasks(self, subtasks: List[Dict[str, Any]]) -> List[TaskResult]:
        """顺序执行任务"""
        results = []
        
        for subtask_data in subtasks:
            task = Task(
                task_id=f"subtask_{len(self.active_tasks)}_{datetime.now().timestamp()}",
                task_type=subtask_data.get("task_type"),
                data=subtask_data.get("data", {}),
                metadata=subtask_data.get("metadata", {})
            )
            
            # 找到合适的代理
            agent = self._find_suitable_agent(task)
            if agent:
                try:
                    result = await agent.process(task)
                    results.append(result)
                    
                    # 如果任务失败且设置了停止策略，则停止执行
                    if (result.status == TaskStatus.FAILED and 
                        subtask_data.get("stop_on_failure", False)):
                        logger.warning(f"任务失败，停止后续执行: {task.task_id}")
                        break
                        
                except Exception as e:
                    results.append(TaskResult(
                        task_id=task.task_id,
                        status=TaskStatus.FAILED,
                        error=str(e)
                    ))
                    if subtask_data.get("stop_on_failure", False):
                        break
            else:
                results.append(TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error="未找到合适的代理"
                ))
        
        return results
    
    async def _execute_pipeline_tasks(self, subtasks: List[Dict[str, Any]]) -> List[TaskResult]:
        """管道式执行任务（前一个任务的输出作为后一个任务的输入）"""
        results = []
        pipeline_data = None
        
        for i, subtask_data in enumerate(subtasks):
            # 如果不是第一个任务，使用前一个任务的结果作为输入
            if i > 0 and pipeline_data is not None:
                if "data" not in subtask_data:
                    subtask_data["data"] = {}
                subtask_data["data"]["pipeline_input"] = pipeline_data
            
            task = Task(
                task_id=f"pipeline_{i}_{datetime.now().timestamp()}",
                task_type=subtask_data.get("task_type"),
                data=subtask_data.get("data", {}),
                metadata=subtask_data.get("metadata", {})
            )
            
            # 找到合适的代理
            agent = self._find_suitable_agent(task)
            if agent:
                try:
                    result = await agent.process(task)
                    results.append(result)
                    
                    # 更新管道数据
                    if result.status == TaskStatus.COMPLETED:
                        pipeline_data = result.result
                    else:
                        logger.warning(f"管道任务失败: {task.task_id}")
                        break
                        
                except Exception as e:
                    results.append(TaskResult(
                        task_id=task.task_id,
                        status=TaskStatus.FAILED,
                        error=str(e)
                    ))
                    break
            else:
                results.append(TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error="未找到合适的代理"
                ))
                break
        
        return results
    
    def _find_suitable_agent(self, task: Task) -> Optional[BaseAgent]:
        """找到合适的代理处理任务"""
        suitable_agents = []
        
        for agent in self.registered_agents.values():
            if agent.can_handle(task):
                suitable_agents.append(agent)
        
        # 简单的负载均衡：选择第一个合适的代理
        return suitable_agents[0] if suitable_agents else None
    
    def _summarize_results(self, results: List[TaskResult]) -> Dict[str, Any]:
        """汇总任务结果"""
        total_tasks = len(results)
        completed_tasks = sum(1 for r in results if r.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for r in results if r.status == TaskStatus.FAILED)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "execution_summary": {
                "successful": [r.task_id for r in results if r.status == TaskStatus.COMPLETED],
                "failed": [r.task_id for r in results if r.status == TaskStatus.FAILED]
            }
        }
    
    async def _manage_agents(self, task: Task) -> TaskResult:
        """管理代理"""
        action = task.data.get("action")
        
        if action == "list":
            agents_info = self.get_registered_agents()
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result={"agents": agents_info}
            )
        elif action == "status":
            agent_id = task.data.get("agent_id")
            if agent_id in self.registered_agents:
                agent = self.registered_agents[agent_id]
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.COMPLETED,
                    result=agent.get_status()
                )
            else:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"代理未找到: {agent_id}"
                )
        else:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=f"不支持的管理操作: {action}"
            )
    
    async def _execute_workflow(self, task: Task) -> TaskResult:
        """执行工作流"""
        workflow_definition = task.data.get("workflow")
        
        if not workflow_definition:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="缺少工作流定义"
            )
        
        workflow_type = workflow_definition.get("type", "sequential")
        steps = workflow_definition.get("steps", [])
        
        # 将工作流步骤转换为子任务
        subtasks = []
        for step in steps:
            subtasks.append({
                "task_type": step.get("task_type"),
                "data": step.get("data", {}),
                "metadata": step.get("metadata", {}),
                "stop_on_failure": step.get("stop_on_failure", True)
            })
        
        # 执行工作流
        if workflow_type == "parallel":
            results = await self._execute_parallel_tasks(subtasks)
        elif workflow_type == "sequential":
            results = await self._execute_sequential_tasks(subtasks)
        elif workflow_type == "pipeline":
            results = await self._execute_pipeline_tasks(subtasks)
        else:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=f"不支持的工作流类型: {workflow_type}"
            )
        
        # 汇总工作流结果
        summary = self._summarize_results(results)
        
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            result={
                "workflow_type": workflow_type,
                "step_results": results,
                "summary": summary
            }
        )
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """获取协调状态"""
        return {
            "registered_agents_count": len(self.registered_agents),
            "active_tasks_count": len(self.active_tasks),
            "completed_tasks_count": len(self.completed_tasks),
            "queue_size": len(self.task_queue),
            "registered_agents": self.get_registered_agents()
        }