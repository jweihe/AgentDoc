"""提示词系统模块"""

from .base import BasePrompt, PromptTemplate
from .toc_prompts import TOCPrompt, TOCWithPagesPrompt, IntegrationPrompt
from .manager import PromptManager

__all__ = [
    "BasePrompt",
    "PromptTemplate", 
    "TOCPrompt",
    "TOCWithPagesPrompt",
    "IntegrationPrompt",
    "PromptManager",
]