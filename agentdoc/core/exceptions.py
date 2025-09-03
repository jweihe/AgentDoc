"""AgentDoc 异常类定义

定义系统中使用的所有异常类。"""


class AgentDocError(Exception):
    """AgentDoc基础异常类"""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ModelError(AgentDocError):
    """模型相关异常"""
    pass


class ProcessingError(AgentDocError):
    """处理相关异常"""
    pass


class DocumentError(ProcessingError):
    """文档处理异常"""
    pass


class IndexError(AgentDocError):
    """索引相关异常"""
    pass


class ConfigError(AgentDocError):
    """配置相关异常"""
    pass


class ValidationError(AgentDocError):
    """验证相关异常"""
    pass


class TaskError(AgentDocError):
    """任务相关异常"""
    pass


class AgentError(AgentDocError):
    """Agent相关异常"""
    pass


class ModelLoadError(ModelError):
    """模型加载异常"""
    pass


class QueueError(AgentDocError):
    """队列相关异常"""
    pass


class WorkerError(AgentDocError):
    """工作器相关异常"""
    pass


class PluginError(AgentDocError):
    """插件相关异常"""
    pass


class QAError(AgentDocError):
    """问答系统异常"""
    pass