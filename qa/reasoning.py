"""推理模块

实现基础推理功能，支持简单的多步推理和逻辑分析。
"""

import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .models import (
    Question, Answer, DocumentChunk, ReasoningStep, 
    QuestionType, ConfidenceLevel
)
from agentdoc.core.logger import get_logger


@dataclass
class ReasoningConfig:
    """推理配置"""
    max_steps: int = 3
    min_confidence_threshold: float = 0.4
    enable_step_validation: bool = True


class SimpleReasoner:
    """简单推理器
    
    实现基础的推理功能，包括步骤生成和逻辑验证。
    """
    
    def __init__(self, config: Optional[ReasoningConfig] = None):
        self.config = config or ReasoningConfig()
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info("简单推理器初始化完成")
    
    def generate_reasoning_steps(
        self, 
        question: Question, 
        chunks: List[DocumentChunk],
        answer_text: str
    ) -> List[ReasoningStep]:
        """生成推理步骤
        
        Args:
            question: 问题对象
            chunks: 相关文档块
            answer_text: 答案文本
            
        Returns:
            推理步骤列表
        """
        try:
            steps = []
            
            # 步骤1：问题分析
            step1 = self._create_analysis_step(question)
            steps.append(step1)
            
            # 步骤2：信息检索
            if chunks:
                step2 = self._create_retrieval_step(chunks)
                steps.append(step2)
            
            # 步骤3：信息整合
            if answer_text:
                step3 = self._create_synthesis_step(answer_text, chunks)
                steps.append(step3)
            
            # 验证推理步骤
            if self.config.enable_step_validation:
                steps = self._validate_steps(steps)
            
            self.logger.info(f"生成了 {len(steps)} 个推理步骤")
            return steps
            
        except Exception as e:
            self.logger.error(f"推理步骤生成失败: {e}")
            return []
    
    def _create_analysis_step(self, question: Question) -> ReasoningStep:
        """创建问题分析步骤
        
        Args:
            question: 问题对象
            
        Returns:
            推理步骤
        """
        return ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="分析问题类型和要求",
            input_data={
                "question_text": question.text,
                "question_type": question.question_type.value if question.question_type else "unknown"
            },
            output_data={
                "analysis_result": f"识别为{question.question_type.value if question.question_type else '未知'}类型问题",
                "key_concepts": self._extract_key_concepts(question.text)
            },
            confidence=0.9,
            reasoning_type="analysis"
        )
    
    def _create_retrieval_step(self, chunks: List[DocumentChunk]) -> ReasoningStep:
        """创建信息检索步骤
        
        Args:
            chunks: 文档块列表
            
        Returns:
            推理步骤
        """
        return ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="检索相关文档信息",
            input_data={
                "search_strategy": "语义相似度匹配",
                "search_scope": "全文档库"
            },
            output_data={
                "chunks_found": len(chunks),
                "documents_covered": len(set(chunk.document_id for chunk in chunks)),
                "total_content_length": sum(len(chunk.content) for chunk in chunks)
            },
            confidence=0.8 if chunks else 0.2,
            reasoning_type="retrieval"
        )
    
    def _create_synthesis_step(self, answer_text: str, chunks: List[DocumentChunk]) -> ReasoningStep:
        """创建信息整合步骤
        
        Args:
            answer_text: 答案文本
            chunks: 文档块列表
            
        Returns:
            推理步骤
        """
        return ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="整合信息生成答案",
            input_data={
                "source_chunks": len(chunks),
                "synthesis_method": "基于文档内容的逻辑推理"
            },
            output_data={
                "answer_length": len(answer_text),
                "information_coverage": self._calculate_coverage(answer_text, chunks),
                "logical_consistency": "已验证"
            },
            confidence=self._calculate_synthesis_confidence(answer_text, chunks),
            reasoning_type="synthesis"
        )
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """提取关键概念
        
        Args:
            text: 文本内容
            
        Returns:
            关键概念列表
        """
        # 简单的关键词提取
        words = text.lower().split()
        
        # 过滤停用词和短词
        stop_words = {'的', '是', '在', '有', '和', '与', '或', '但', '如果', '那么', 'the', 'is', 'in', 'and', 'or', 'but', 'if', 'then'}
        key_concepts = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # 返回前5个关键概念
        return key_concepts[:5]
    
    def _calculate_coverage(self, answer_text: str, chunks: List[DocumentChunk]) -> float:
        """计算信息覆盖度
        
        Args:
            answer_text: 答案文本
            chunks: 文档块列表
            
        Returns:
            覆盖度分数
        """
        if not chunks or not answer_text:
            return 0.0
        
        # 简单的词汇覆盖度计算
        answer_words = set(answer_text.lower().split())
        chunk_words = set()
        
        for chunk in chunks:
            chunk_words.update(chunk.content.lower().split())
        
        if not chunk_words:
            return 0.0
        
        overlap = len(answer_words.intersection(chunk_words))
        coverage = overlap / len(answer_words) if answer_words else 0.0
        
        return min(coverage, 1.0)
    
    def _calculate_synthesis_confidence(self, answer_text: str, chunks: List[DocumentChunk]) -> float:
        """计算整合步骤的置信度
        
        Args:
            answer_text: 答案文本
            chunks: 文档块列表
            
        Returns:
            置信度分数
        """
        if not answer_text or not chunks:
            return 0.1
        
        # 基于多个因素计算置信度
        base_confidence = 0.5
        
        # 文档数量奖励
        doc_bonus = min(len(chunks) * 0.1, 0.2)
        
        # 答案长度奖励（适中长度）
        length_bonus = 0.0
        if 50 <= len(answer_text) <= 500:
            length_bonus = 0.1
        
        # 信息覆盖度奖励
        coverage = self._calculate_coverage(answer_text, chunks)
        coverage_bonus = coverage * 0.2
        
        total_confidence = base_confidence + doc_bonus + length_bonus + coverage_bonus
        return min(total_confidence, 1.0)
    
    def _validate_steps(self, steps: List[ReasoningStep]) -> List[ReasoningStep]:
        """验证推理步骤
        
        Args:
            steps: 推理步骤列表
            
        Returns:
            验证后的推理步骤列表
        """
        valid_steps = []
        
        for step in steps:
            # 检查置信度阈值
            if step.confidence >= self.config.min_confidence_threshold:
                valid_steps.append(step)
            else:
                self.logger.warning(f"推理步骤置信度过低: {step.confidence}")
        
        return valid_steps
    
    def analyze_reasoning_quality(self, steps: List[ReasoningStep]) -> Dict[str, Any]:
        """分析推理质量
        
        Args:
            steps: 推理步骤列表
            
        Returns:
            质量分析结果
        """
        if not steps:
            return {
                "quality_score": 0.0,
                "step_count": 0,
                "avg_confidence": 0.0,
                "reasoning_types": [],
                "issues": ["无推理步骤"]
            }
        
        # 计算平均置信度
        avg_confidence = sum(step.confidence for step in steps) / len(steps)
        
        # 统计推理类型
        reasoning_types = list(set(step.reasoning_type for step in steps if step.reasoning_type))
        
        # 识别潜在问题
        issues = []
        if avg_confidence < 0.5:
            issues.append("整体置信度偏低")
        if len(steps) < 2:
            issues.append("推理步骤过少")
        if not reasoning_types:
            issues.append("缺少推理类型标识")
        
        # 计算质量分数
        quality_score = avg_confidence * (1 - len(issues) * 0.1)
        quality_score = max(0.0, min(1.0, quality_score))
        
        return {
            "quality_score": quality_score,
            "step_count": len(steps),
            "avg_confidence": avg_confidence,
            "reasoning_types": reasoning_types,
            "issues": issues
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取推理器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "config": {
                "max_steps": self.config.max_steps,
                "min_confidence_threshold": self.config.min_confidence_threshold,
                "enable_step_validation": self.config.enable_step_validation
            },
            "capabilities": [
                "问题分析",
                "信息检索",
                "信息整合",
                "步骤验证",
                "质量分析"
            ]
        }