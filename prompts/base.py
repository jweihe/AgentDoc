"""提示词基础类"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from string import Template
from ..core.exceptions import ValidationError
from ..core.logger import get_logger

logger = get_logger(__name__)

class PromptTemplate:
    """提示词模板类
    
    封装单个提示词模板，支持变量替换和验证。
    """
    
    def __init__(self, name: str, template: str, description: str = "", 
                 required_vars: Optional[List[str]] = None):
        """
        Args:
            name: 模板名称
            template: 模板内容，使用$变量名格式
            description: 模板描述
            required_vars: 必需的变量列表
        """
        self.name = name
        self.template = template
        self.description = description
        self.required_vars = required_vars or []
        self._template_obj = Template(template)
        
    def render(self, **kwargs) -> str:
        """渲染模板
        
        Args:
            **kwargs: 模板变量
            
        Returns:
            渲染后的文本
            
        Raises:
            ValidationError: 缺少必需变量时抛出
        """
        # 验证必需变量
        missing_vars = [var for var in self.required_vars if var not in kwargs]
        if missing_vars:
            raise ValidationError(f"模板 '{self.name}' 缺少必需变量: {missing_vars}")
        
        try:
            return self._template_obj.substitute(**kwargs)
        except KeyError as e:
            raise ValidationError(f"模板 '{self.name}' 变量替换失败: {e}")
    
    def safe_render(self, **kwargs) -> str:
        """安全渲染模板，未提供的变量保持原样
        
        Args:
            **kwargs: 模板变量
            
        Returns:
            渲染后的文本
        """
        return self._template_obj.safe_substitute(**kwargs)
    
    def validate_vars(self, **kwargs) -> bool:
        """验证模板变量
        
        Args:
            **kwargs: 模板变量
            
        Returns:
            验证是否通过
        """
        try:
            self.render(**kwargs)
            return True
        except ValidationError:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取模板信息
        
        Returns:
            模板信息字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "required_vars": self.required_vars,
            "template_length": len(self.template)
        }

class BasePrompt(ABC):
    """提示词基础类
    
    所有提示词类的基类，定义了统一的接口。
    """
    
    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_templates()
        logger.info(f"初始化提示词类: {self.__class__.__name__}")
    
    @abstractmethod
    def _load_templates(self):
        """加载模板
        
        子类必须实现此方法来加载具体的模板。
        """
        pass
    
    def add_template(self, template: PromptTemplate):
        """添加模板
        
        Args:
            template: 提示词模板
        """
        self._templates[template.name] = template
        logger.debug(f"添加模板: {template.name}")
    
    def get_template(self, name: str) -> PromptTemplate:
        """获取模板
        
        Args:
            name: 模板名称
            
        Returns:
            提示词模板
            
        Raises:
            ValidationError: 模板不存在时抛出
        """
        if name not in self._templates:
            raise ValidationError(f"模板 '{name}' 不存在")
        return self._templates[name]
    
    def render(self, template_name: str, **kwargs) -> str:
        """渲染指定模板
        
        Args:
            template_name: 模板名称
            **kwargs: 模板变量
            
        Returns:
            渲染后的提示词
        """
        template = self.get_template(template_name)
        return template.render(**kwargs)
    
    def safe_render(self, template_name: str, **kwargs) -> str:
        """安全渲染指定模板
        
        Args:
            template_name: 模板名称
            **kwargs: 模板变量
            
        Returns:
            渲染后的提示词
        """
        template = self.get_template(template_name)
        return template.safe_render(**kwargs)
    
    def list_templates(self) -> List[str]:
        """列出所有模板名称
        
        Returns:
            模板名称列表
        """
        return list(self._templates.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """获取模板信息
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板信息字典
        """
        template = self.get_template(template_name)
        return template.get_info()
    
    def get_all_templates_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模板信息
        
        Returns:
            所有模板信息的字典
        """
        return {name: template.get_info() for name, template in self._templates.items()}
    
    def validate_template_vars(self, template_name: str, **kwargs) -> bool:
        """验证模板变量
        
        Args:
            template_name: 模板名称
            **kwargs: 模板变量
            
        Returns:
            验证是否通过
        """
        try:
            template = self.get_template(template_name)
            return template.validate_vars(**kwargs)
        except ValidationError:
            return False