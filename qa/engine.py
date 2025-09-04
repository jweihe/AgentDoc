"""问答引擎核心模块

实现智能问答系统的核心逻辑，包括问题理解、文档检索、答案生成等。
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from .models import (
    Question, Answer, QAResult, QASession, 
    QuestionType, ConfidenceLevel, ReasoningStep, Citation
)
from .indexer import DocumentIndexer
from .retriever import DocumentRetriever, RetrievalConfig
from .citation import CitationManager, CitationConfig
from agentdoc.core.logger import get_logger
from agentdoc.core.exceptions import QAError


@dataclass
class QAConfig:
    """问答系统配置"""
    max_context_length: int = 4000
    max_reasoning_steps: int = 5
    enable_multi_hop: bool = True
    confidence_threshold: float = 0.6
    max_answer_length: int = 1000
    enable_citation: bool = True
    retrieval_config: Optional[RetrievalConfig] = None
    citation_config: Optional[CitationConfig] = None


class QAEngine:
    """问答引擎
    
    智能问答系统的核心引擎，整合文档检索、推理和答案生成。
    """
    
    def __init__(self, config: Optional[QAConfig] = None):
        """初始化问答引擎
        
        Args:
            config: 问答系统配置
        """
        self.config = config or QAConfig()
        self.logger = get_logger(self.__class__.__name__)
        
        # 初始化组件
        from ..core.config import get_settings
        settings = get_settings()
        self.indexer = DocumentIndexer(settings)
        self.retriever = DocumentRetriever(self.config.retrieval_config)
        self.citation_manager = CitationManager(self.config.citation_config)
        
        # 会话管理
        self.sessions: Dict[str, QASession] = {}
        
        self.logger.info("问答引擎初始化完成")
    
    def ask(
        self, 
        question_text: str, 
        session_id: Optional[str] = None,
        question_type: Optional[QuestionType] = None,
        context: Optional[str] = None
    ) -> QAResult:
        """处理问答请求
        
        Args:
            question_text: 问题文本
            session_id: 会话ID
            question_type: 问题类型
            context: 上下文信息
            
        Returns:
            问答结果
        """
        start_time = time.time()
        
        try:
            # 创建问题对象
            question = Question(
                question_id=str(uuid.uuid4()),
                text=question_text,
                question_type=question_type or self._classify_question(question_text),
                context=context
            )
            
            self.logger.info(f"处理问题: {question_text[:100]}...")
            
            # 获取或创建会话
            session = self._get_or_create_session(session_id)
            
            # 检索相关文档
            relevant_chunks = self.retriever.retrieve(question_text)
            
            if not relevant_chunks:
                return self._create_no_answer_result(question, "未找到相关文档")
            
            # 生成答案
            answer = self._generate_answer(question, relevant_chunks, session)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 创建结果
            result = QAResult(
                question=question,
                answer=answer,
                processing_time=processing_time,
                model_used="default",
                retrieval_results=relevant_chunks
            )
            
            # 更新会话
            session.add_qa_result(result)
            
            self.logger.info(f"问答完成，置信度: {answer.confidence}")
            return result
            
        except Exception as e:
            self.logger.error(f"问答处理失败: {e}")
            return self._create_error_result(question_text, str(e))
    
    def _classify_question(self, question_text: str) -> QuestionType:
        """分类问题类型
        
        Args:
            question_text: 问题文本
            
        Returns:
            问题类型
        """
        text_lower = question_text.lower()
        
        # 简单的规则分类
        if any(word in text_lower for word in ['what', 'who', 'where', 'when', '什么', '谁', '哪里', '什么时候']):
            return QuestionType.FACTUAL
        elif any(word in text_lower for word in ['how', 'why', '如何', '为什么', '怎么']):
            return QuestionType.REASONING
        elif any(word in text_lower for word in ['compare', 'difference', '比较', '区别']):
            return QuestionType.COMPARISON
        elif any(word in text_lower for word in ['summarize', 'summary', '总结', '概括']):
            return QuestionType.SUMMARIZATION
        else:
            return QuestionType.FACTUAL
    
    def _generate_answer(
        self, 
        question: Question, 
        chunks: List, 
        session: QASession
    ) -> Answer:
        """生成答案
        
        Args:
            question: 问题对象
            chunks: 相关文档块
            session: 会话对象
            
        Returns:
            答案对象
        """
        try:
            # 构建上下文
            context = self._build_context(chunks)
            
            # 生成答案文本（简化实现）
            answer_text = self._generate_answer_text(question, context)
            
            # 生成推理步骤
            reasoning_steps = self._generate_reasoning_steps(question, chunks)
            
            # 提取引用
            citations = []
            if self.config.enable_citation:
                citations = self.citation_manager.extract_citations(answer_text, chunks)
            
            # 计算置信度
            confidence = self._calculate_confidence(answer_text, chunks, citations)
            confidence_level = self._get_confidence_level(confidence)
            
            return Answer(
                answer_id=str(uuid.uuid4()),
                text=answer_text,
                confidence=confidence,
                confidence_level=confidence_level,
                citations=citations,
                reasoning_steps=reasoning_steps
            )
            
        except Exception as e:
            self.logger.error(f"答案生成失败: {e}")
            return Answer(
                answer_id=str(uuid.uuid4()),
                text="抱歉，我无法生成答案。",
                confidence=0.0,
                confidence_level=ConfidenceLevel.LOW,
                citations=[],
                reasoning_steps=[]
            )
    
    def _build_context(self, chunks: List) -> str:
        """构建上下文
        
        Args:
            chunks: 文档块列表
            
        Returns:
            上下文字符串
        """
        context_parts = []
        total_length = 0
        
        for chunk in chunks:
            chunk_text = getattr(chunk, 'content', str(chunk))
            if total_length + len(chunk_text) > self.config.max_context_length:
                break
            context_parts.append(chunk_text)
            total_length += len(chunk_text)
        
        return "\n\n".join(context_parts)
    
    def _generate_answer_text(self, question: Question, context: str) -> str:
        """生成答案文本（简化实现）
        
        Args:
            question: 问题对象
            context: 上下文
            
        Returns:
            答案文本
        """
        # 这里应该调用语言模型，现在使用简化实现
        if not context.strip():
            return "抱歉，我没有找到相关信息来回答您的问题。"
        
        # 简单的模板回答
        if question.question_type == QuestionType.SUMMARIZATION:
            return f"根据文档内容，主要信息如下：{context[:500]}..."
        else:
            return f"根据相关文档，{question.text}的答案是：{context[:300]}..."
    
    def _generate_reasoning_steps(self, question: Question, chunks: List) -> List[ReasoningStep]:
        """生成推理步骤
        
        Args:
            question: 问题对象
            chunks: 文档块列表
            
        Returns:
            推理步骤列表
        """
        steps = []
        
        # 步骤1：文档检索
        step1 = ReasoningStep(
            step_id=str(uuid.uuid4()),
            description="检索相关文档",
            input_data={"question": question.text},
            output_data={"chunks_found": len(chunks)},
            confidence=0.9 if chunks else 0.1
        )
        steps.append(step1)
        
        # 步骤2：信息提取
        if chunks:
            step2 = ReasoningStep(
                step_id=str(uuid.uuid4()),
                description="从文档中提取相关信息",
                input_data={"chunks": len(chunks)},
                output_data={"relevant_info": "已提取"},
                confidence=0.8
            )
            steps.append(step2)
        
        return steps
    
    def _calculate_confidence(self, answer_text: str, chunks: List, citations: List[Citation]) -> float:
        """计算置信度
        
        Args:
            answer_text: 答案文本
            chunks: 文档块列表
            citations: 引用列表
            
        Returns:
            置信度分数
        """
        if not answer_text or "抱歉" in answer_text or "无法" in answer_text:
            return 0.1
        
        # 基于文档数量和引用数量的简单计算
        base_confidence = min(0.5 + len(chunks) * 0.1, 0.9)
        citation_bonus = min(len(citations) * 0.05, 0.1)
        
        return min(base_confidence + citation_bonus, 1.0)
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """获取置信度等级
        
        Args:
            confidence: 置信度分数
            
        Returns:
            置信度等级
        """
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _get_or_create_session(self, session_id: Optional[str]) -> QASession:
        """获取或创建会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = QASession(session_id=session_id)
        
        return self.sessions[session_id]
    
    def _create_no_answer_result(self, question: Question, reason: str) -> QAResult:
        """创建无答案结果
        
        Args:
            question: 问题对象
            reason: 无答案原因
            
        Returns:
            问答结果
        """
        answer = Answer(
            answer_id=str(uuid.uuid4()),
            text=f"抱歉，{reason}。",
            confidence=0.0,
            confidence_level=ConfidenceLevel.LOW,
            citations=[],
            reasoning_steps=[]
        )
        
        return QAResult(
            question=question,
            answer=answer,
            processing_time=0.0,
            model_used="default",
            retrieval_results=[]
        )
    
    def _create_error_result(self, question_text: str, error_message: str) -> QAResult:
        """创建错误结果
        
        Args:
            question_text: 问题文本
            error_message: 错误信息
            
        Returns:
            问答结果
        """
        question = Question(
            question_id=str(uuid.uuid4()),
            text=question_text,
            question_type=QuestionType.FACTUAL
        )
        
        answer = Answer(
            answer_id=str(uuid.uuid4()),
            text=f"处理问题时发生错误：{error_message}",
            confidence=0.0,
            confidence_level=ConfidenceLevel.LOW,
            citations=[],
            reasoning_steps=[]
        )
        
        return QAResult(
            question=question,
            answer=answer,
            processing_time=0.0,
            model_used="default",
            retrieval_results=[]
        )
    
    def get_session(self, session_id: str) -> Optional[QASession]:
        """获取会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象或None
        """
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[str]:
        """列出所有会话ID
        
        Returns:
            会话ID列表
        """
        return list(self.sessions.keys())
    
    def clear_session(self, session_id: str) -> bool:
        """清除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功清除
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            统计信息字典
        """
        total_questions = sum(len(session.qa_results) for session in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "total_questions": total_questions,
            "active_sessions": len([s for s in self.sessions.values() if s.qa_results]),
            "config": {
                "max_context_length": self.config.max_context_length,
                "confidence_threshold": self.config.confidence_threshold,
                "enable_citation": self.config.enable_citation,
            }
        }