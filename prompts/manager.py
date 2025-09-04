"""提示词管理器"""

from typing import Dict, List, Optional, Type
from .base import BasePrompt
from .toc_prompts import TOCPrompt, TOCWithPagesPrompt, IntegrationPrompt
from .qa_prompts import QAPrompt, DocumentQAPrompt
from .advanced_prompts import AdvancedTextPrompt, SpecializedPrompt, InteractivePrompt
from ..core.exceptions import ValidationError
from ..core.logger import get_logger

logger = get_logger(__name__)

class PromptManager:
    """提示词管理器
    
    统一管理所有提示词类和模板。
    """
    
    def __init__(self):
        self._prompt_classes: Dict[str, Type[BasePrompt]] = {}
        self._prompt_instances: Dict[str, BasePrompt] = {}
        self._register_default_prompts()
    
    def _register_default_prompts(self):
        """注册默认的提示词类"""
        # 基础提示词
        self.register_prompt_class("toc", TOCPrompt)
        self.register_prompt_class("toc_with_pages", TOCWithPagesPrompt)
        self.register_prompt_class("integration", IntegrationPrompt)
        
        # 问答提示词
        self.register_prompt_class("qa", QAPrompt)
        self.register_prompt_class("document_qa", DocumentQAPrompt)
        
        # 高级提示词
        self.register_prompt_class("advanced_text", AdvancedTextPrompt)
        self.register_prompt_class("specialized", SpecializedPrompt)
        self.register_prompt_class("interactive", InteractivePrompt)
        
        logger.info("已注册所有默认提示词类")
    
    def register_prompt_class(self, name: str, prompt_class: Type[BasePrompt]):
        """注册提示词类
        
        Args:
            name: 提示词类名称
            prompt_class: 提示词类
        """
        if not issubclass(prompt_class, BasePrompt):
            raise ValidationError(f"提示词类必须继承自BasePrompt: {prompt_class}")
        
        self._prompt_classes[name] = prompt_class
        logger.info(f"注册提示词类: {name}")
    
    def get_prompt(self, name: str) -> BasePrompt:
        """获取提示词实例
        
        Args:
            name: 提示词类名称
            
        Returns:
            提示词实例
            
        Raises:
            ValidationError: 提示词类不存在时抛出
        """
        if name not in self._prompt_instances:
            if name not in self._prompt_classes:
                raise ValidationError(f"提示词类 '{name}' 不存在")
            
            # 创建实例
            prompt_class = self._prompt_classes[name]
            self._prompt_instances[name] = prompt_class()
            logger.info(f"创建提示词实例: {name}")
        
        return self._prompt_instances[name]
    
    def list_prompt_classes(self) -> List[str]:
        """列出所有已注册的提示词类
        
        Returns:
            提示词类名称列表
        """
        return list(self._prompt_classes.keys())
    
    def list_templates(self, prompt_name: str) -> List[str]:
        """列出指定提示词类的所有模板
        
        Args:
            prompt_name: 提示词类名称
            
        Returns:
            模板名称列表
        """
        prompt = self.get_prompt(prompt_name)
        return prompt.list_templates()
    
    def render_template(self, prompt_name: str, template_name: str, **kwargs) -> str:
        """渲染指定模板
        
        Args:
            prompt_name: 提示词类名称
            template_name: 模板名称
            **kwargs: 模板变量
            
        Returns:
            渲染后的提示词
        """
        prompt = self.get_prompt(prompt_name)
        return prompt.render(template_name, **kwargs)
    
    def get_template_info(self, prompt_name: str, template_name: str) -> Dict:
        """获取模板信息
        
        Args:
            prompt_name: 提示词类名称
            template_name: 模板名称
            
        Returns:
            模板信息字典
        """
        prompt = self.get_prompt(prompt_name)
        return prompt.get_template_info(template_name)
    
    def get_all_templates_info(self) -> Dict[str, Dict[str, Dict]]:
        """获取所有模板信息
        
        Returns:
            所有模板信息的嵌套字典
        """
        all_info = {}
        
        for prompt_name in self.list_prompt_classes():
            prompt = self.get_prompt(prompt_name)
            templates = prompt.list_templates()
            
            all_info[prompt_name] = {}
            for template_name in templates:
                all_info[prompt_name][template_name] = prompt.get_template_info(template_name)
        
        return all_info
    
    def validate_template_vars(self, prompt_name: str, template_name: str, **kwargs) -> bool:
        """验证模板变量
        
        Args:
            prompt_name: 提示词类名称
            template_name: 模板名称
            **kwargs: 模板变量
            
        Returns:
            验证是否通过
        """
        try:
            prompt = self.get_prompt(prompt_name)
            template = prompt.get_template(template_name)
            return template.validate_vars(**kwargs)
        except Exception:
            return False
    
    def clear_instances(self):
        """清理所有实例"""
        self._prompt_instances.clear()
        logger.info("清理所有提示词实例")

# 全局提示词管理器实例
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """获取全局提示词管理器实例
    
    Returns:
        提示词管理器实例
    """
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager