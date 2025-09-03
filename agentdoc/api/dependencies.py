"""API依赖注入"""

from typing import Optional
from fastapi import Depends, HTTPException
from functools import lru_cache

from ..core.config import get_settings
from ..core.logger import get_logger
from ..models.manager import ModelManager, get_model_manager as _get_model_manager
from ..processors.factory import ProcessorFactory, get_processor_factory as _get_processor_factory
from ..plugins.manager import PluginManager, get_plugin_manager as _get_plugin_manager
from ..prompts.manager import PromptManager, get_prompt_manager as _get_prompt_manager

logger = get_logger(__name__)

# 全局实例缓存
_model_manager_instance: Optional[ModelManager] = None
_processor_factory_instance: Optional[ProcessorFactory] = None
_plugin_manager_instance: Optional[PluginManager] = None
_prompt_manager_instance: Optional[PromptManager] = None

@lru_cache()
def get_settings_dependency():
    """获取配置依赖"""
    return get_settings()

async def get_model_manager() -> ModelManager:
    """获取模型管理器依赖"""
    global _model_manager_instance
    
    if _model_manager_instance is None:
        try:
            _model_manager_instance = _get_model_manager()
            logger.info("模型管理器初始化成功")
        except Exception as e:
            logger.error(f"模型管理器初始化失败: {e}")
            raise HTTPException(status_code=500, detail="模型管理器初始化失败")
    
    return _model_manager_instance

async def get_processor_factory() -> ProcessorFactory:
    """获取处理器工厂依赖"""
    global _processor_factory_instance
    
    if _processor_factory_instance is None:
        try:
            _processor_factory_instance = _get_processor_factory()
            logger.info("处理器工厂初始化成功")
        except Exception as e:
            logger.error(f"处理器工厂初始化失败: {e}")
            raise HTTPException(status_code=500, detail="处理器工厂初始化失败")
    
    return _processor_factory_instance

async def get_plugin_manager() -> PluginManager:
    """获取插件管理器依赖"""
    global _plugin_manager_instance
    
    if _plugin_manager_instance is None:
        try:
            _plugin_manager_instance = _get_plugin_manager()
            
            # 如果插件管理器未初始化，则进行初始化
            if not hasattr(_plugin_manager_instance, '_initialized'):
                settings = get_settings()
                await _plugin_manager_instance.initialize(settings.dict())
                _plugin_manager_instance._initialized = True
            
            logger.info("插件管理器初始化成功")
        except Exception as e:
            logger.error(f"插件管理器初始化失败: {e}")
            raise HTTPException(status_code=500, detail="插件管理器初始化失败")
    
    return _plugin_manager_instance

async def get_prompt_manager() -> PromptManager:
    """获取提示词管理器依赖"""
    global _prompt_manager_instance
    
    if _prompt_manager_instance is None:
        try:
            _prompt_manager_instance = _get_prompt_manager()
            logger.info("提示词管理器初始化成功")
        except Exception as e:
            logger.error(f"提示词管理器初始化失败: {e}")
            raise HTTPException(status_code=500, detail="提示词管理器初始化失败")
    
    return _prompt_manager_instance

async def verify_model_loaded(model_name: str, model_manager: ModelManager = Depends(get_model_manager)):
    """验证模型是否已加载"""
    if not model_manager.is_model_loaded(model_name):
        try:
            await model_manager.load_model(model_name)
        except Exception as e:
            logger.error(f"加载模型失败 {model_name}: {e}")
            raise HTTPException(status_code=500, detail=f"加载模型失败: {str(e)}")
    
    return model_manager.get_model(model_name)

async def verify_processor_available(processor_name: str, factory: ProcessorFactory = Depends(get_processor_factory)):
    """验证处理器是否可用"""
    if not factory.is_processor_registered(processor_name):
        raise HTTPException(status_code=404, detail=f"处理器 {processor_name} 不存在")
    
    return factory

async def get_current_user():
    """获取当前用户（占位符，用于未来的认证功能）"""
    # TODO: 实现用户认证逻辑
    return {"user_id": "anonymous", "username": "anonymous"}

class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def check_rate_limit(self, client_id: str) -> bool:
        """检查速率限制"""
        import time
        
        current_time = time.time()
        
        # 清理过期记录
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_id] = []
        
        # 检查是否超过限制
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[client_id].append(current_time)
        return True

# 全局速率限制器实例
rate_limiter = RateLimiter()

async def check_rate_limit(client_ip: str = None):
    """检查速率限制依赖"""
    if client_ip is None:
        client_ip = "default"
    
    if not await rate_limiter.check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    
    return True

async def cleanup_dependencies():
    """清理依赖资源"""
    global _model_manager_instance, _processor_factory_instance
    global _plugin_manager_instance, _prompt_manager_instance
    
    try:
        # 清理模型管理器
        if _model_manager_instance:
            await _model_manager_instance.cleanup()
            _model_manager_instance = None
            logger.info("模型管理器已清理")
        
        # 清理插件管理器
        if _plugin_manager_instance:
            await _plugin_manager_instance.cleanup()
            _plugin_manager_instance = None
            logger.info("插件管理器已清理")
        
        # 重置其他实例
        _processor_factory_instance = None
        _prompt_manager_instance = None
        
        logger.info("所有依赖已清理")
    
    except Exception as e:
        logger.error(f"清理依赖时发生错误: {e}")

# 健康检查依赖
async def health_check_dependencies():
    """健康检查依赖"""
    health_status = {
        "model_manager": False,
        "processor_factory": False,
        "plugin_manager": False,
        "prompt_manager": False
    }
    
    try:
        # 检查模型管理器
        model_manager = await get_model_manager()
        health_status["model_manager"] = model_manager is not None
    except Exception:
        pass
    
    try:
        # 检查处理器工厂
        processor_factory = await get_processor_factory()
        health_status["processor_factory"] = processor_factory is not None
    except Exception:
        pass
    
    try:
        # 检查插件管理器
        plugin_manager = await get_plugin_manager()
        health_status["plugin_manager"] = plugin_manager is not None
    except Exception:
        pass
    
    try:
        # 检查提示词管理器
        prompt_manager = await get_prompt_manager()
        health_status["prompt_manager"] = prompt_manager is not None
    except Exception:
        pass
    
    return health_status