"""QAAgent - 问答Agent

专门负责基于文档的问答功能。
"""

import re
from typing import List, Dict, Any, Optional
import logging

from .base import BaseAgent, Task, TaskResult, TaskStatus, AgentCapability

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """问答Agent"""
    
    def __init__(self):
        super().__init__("QAAgent")
        
    def get_capabilities(self) -> List[AgentCapability]:
        """获取QAAgent能力"""
        return [AgentCapability.QUESTION_ANSWERING]
    
    async def process(self, task: Task) -> TaskResult:
        """处理问答任务"""
        try:
            if task.task_type != "question_answering":
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"不支持的任务类型: {task.task_type}"
                )
            
            question = task.data.get("question")
            context = task.data.get("context", "")
            
            if not question:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error="缺少问题"
                )
            
            # 执行问答
            qa_result = await self._answer_question(question, context)
            
            # 保存问答历史
            self.save_memory(f"qa_{task.task_id}", {
                "question": question,
                "answer": qa_result["answer"],
                "confidence": qa_result["confidence"]
            })
            
            logger.info(f"问答任务完成: {task.task_id}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=qa_result
            )
            
        except Exception as e:
            logger.error(f"问答任务失败: {e}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    async def _answer_question(self, question: str, context: str) -> Dict[str, Any]:
        """回答问题"""
        # 问题类型分析
        question_type = self._analyze_question_type(question)
        
        # 根据问题类型选择不同的回答策略
        if question_type == "factual":
            answer = self._answer_factual_question(question, context)
        elif question_type == "summary":
            answer = self._answer_summary_question(question, context)
        elif question_type == "comparison":
            answer = self._answer_comparison_question(question, context)
        elif question_type == "explanation":
            answer = self._answer_explanation_question(question, context)
        else:
            answer = self._answer_general_question(question, context)
        
        # 计算置信度
        confidence = self._calculate_answer_confidence(question, context, answer)
        
        # 提取支持证据
        evidence = self._extract_evidence(question, context, answer)
        
        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "question_type": question_type,
            "evidence": evidence,
            "sources": self._identify_sources(context)
        }
    
    def _analyze_question_type(self, question: str) -> str:
        """分析问题类型"""
        question_lower = question.lower()
        
        # 事实性问题
        factual_keywords = ["什么", "谁", "哪里", "何时", "多少", "what", "who", "where", "when", "how many"]
        if any(keyword in question_lower for keyword in factual_keywords):
            return "factual"
        
        # 总结性问题
        summary_keywords = ["总结", "概括", "主要内容", "summarize", "summary", "main points"]
        if any(keyword in question_lower for keyword in summary_keywords):
            return "summary"
        
        # 比较性问题
        comparison_keywords = ["比较", "区别", "不同", "相同", "compare", "difference", "similar"]
        if any(keyword in question_lower for keyword in comparison_keywords):
            return "comparison"
        
        # 解释性问题
        explanation_keywords = ["为什么", "如何", "怎样", "原因", "why", "how", "explain", "reason"]
        if any(keyword in question_lower for keyword in explanation_keywords):
            return "explanation"
        
        return "general"
    
    def _answer_factual_question(self, question: str, context: str) -> str:
        """回答事实性问题"""
        # 提取问题中的关键词
        question_keywords = self._extract_question_keywords(question)
        
        # 在上下文中搜索相关句子
        sentences = re.split(r'[.!?。！？]+', context)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 计算句子与问题的相关性
            relevance_score = self._calculate_sentence_relevance(sentence, question_keywords)
            if relevance_score > 0:
                relevant_sentences.append((sentence, relevance_score))
        
        if relevant_sentences:
            # 选择最相关的句子
            relevant_sentences.sort(key=lambda x: x[1], reverse=True)
            return relevant_sentences[0][0]
        else:
            return "抱歉，无法在文档中找到相关信息。"
    
    def _answer_summary_question(self, question: str, context: str) -> str:
        """回答总结性问题"""
        # 简单的摘要生成
        sentences = re.split(r'[.!?。！？]+', context)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return ' '.join(sentences)
        
        # 选择关键句子
        keywords = self._extract_keywords_from_text(context)
        sentence_scores = []
        
        for sentence in sentences:
            score = sum(1 for keyword in keywords if keyword in sentence.lower())
            sentence_scores.append((sentence, score))
        
        # 选择得分最高的3个句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        summary_sentences = [s[0] for s in sentence_scores[:3]]
        
        return ' '.join(summary_sentences)
    
    def _answer_comparison_question(self, question: str, context: str) -> str:
        """回答比较性问题"""
        # 寻找包含比较词汇的句子
        comparison_words = ["比", "相比", "不同", "相同", "而", "但是", "然而", "versus", "compared", "different", "same"]
        
        sentences = re.split(r'[.!?。！？]+', context)
        comparison_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(word in sentence for word in comparison_words):
                comparison_sentences.append(sentence)
        
        if comparison_sentences:
            return ' '.join(comparison_sentences[:2])  # 返回前两个比较句子
        else:
            return "文档中没有找到明确的比较信息。"
    
    def _answer_explanation_question(self, question: str, context: str) -> str:
        """回答解释性问题"""
        # 寻找包含解释词汇的句子
        explanation_words = ["因为", "由于", "原因", "导致", "所以", "因此", "because", "due to", "reason", "cause"]
        
        sentences = re.split(r'[.!?。！？]+', context)
        explanation_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(word in sentence for word in explanation_words):
                explanation_sentences.append(sentence)
        
        if explanation_sentences:
            return ' '.join(explanation_sentences[:2])  # 返回前两个解释句子
        else:
            return "文档中没有找到明确的解释信息。"
    
    def _answer_general_question(self, question: str, context: str) -> str:
        """回答一般性问题"""
        return self._answer_factual_question(question, context)
    
    def _extract_question_keywords(self, question: str) -> List[str]:
        """从问题中提取关键词"""
        # 移除疑问词
        question_words = ["什么", "谁", "哪里", "何时", "为什么", "如何", "怎样", 
                         "what", "who", "where", "when", "why", "how", "which"]
        
        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [word for word in words if word not in question_words and len(word) > 2]
        
        return keywords
    
    def _calculate_sentence_relevance(self, sentence: str, keywords: List[str]) -> int:
        """计算句子与关键词的相关性"""
        sentence_lower = sentence.lower()
        return sum(1 for keyword in keywords if keyword in sentence_lower)
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # 计算词频并返回前10个
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _calculate_answer_confidence(self, question: str, context: str, answer: str) -> float:
        """计算答案置信度"""
        if "抱歉" in answer or "没有找到" in answer:
            return 0.1
        
        question_keywords = self._extract_question_keywords(question)
        answer_keywords = re.findall(r'\b\w+\b', answer.lower())
        
        # 计算关键词重叠度
        overlap = len(set(question_keywords) & set(answer_keywords))
        total_keywords = len(question_keywords)
        
        if total_keywords == 0:
            return 0.5
        
        base_confidence = overlap / total_keywords
        
        # 根据答案长度调整置信度
        if len(answer) < 10:
            return base_confidence * 0.7
        elif len(answer) > 100:
            return min(base_confidence * 1.2, 1.0)
        else:
            return base_confidence
    
    def _extract_evidence(self, question: str, context: str, answer: str) -> List[str]:
        """提取支持证据"""
        if "抱歉" in answer or "没有找到" in answer:
            return []
        
        # 寻找包含答案关键词的句子作为证据
        answer_keywords = re.findall(r'\b\w+\b', answer.lower())
        sentences = re.split(r'[.!?。！？]+', context)
        
        evidence = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            overlap = len(set(answer_keywords) & set(sentence_words))
            
            if overlap > 0:
                evidence.append(sentence)
        
        return evidence[:3]  # 返回前3个证据句子
    
    def _identify_sources(self, context: str) -> List[str]:
        """识别信息来源"""
        # 简单的来源识别
        sources = []
        
        # 寻找引用模式
        citation_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\(\d{4}\)',  # (2023), etc.
            r'根据.*?[，,]',  # 根据...，
            r'据.*?[，,]',   # 据...，
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, context)
            sources.extend(matches)
        
        return list(set(sources))  # 去重
    
    def get_qa_history(self) -> List[Dict[str, Any]]:
        """获取问答历史"""
        history = []
        for key, value in self.memory.items():
            if key.startswith("qa_"):
                history.append(value["value"])
        return history