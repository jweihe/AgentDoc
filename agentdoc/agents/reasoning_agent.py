"""ReasoningAgent - 推理分析Agent

负责文本分析、推理和内容理解。
"""

import re
from typing import List, Dict, Any, Optional
import logging

from .base import BaseAgent, Task, TaskResult, TaskStatus, AgentCapability

logger = logging.getLogger(__name__)


class ReasoningAgent(BaseAgent):
    """推理分析Agent"""
    
    def __init__(self):
        super().__init__("ReasoningAgent")
        
    def get_capabilities(self) -> List[AgentCapability]:
        """获取ReasoningAgent能力"""
        return [AgentCapability.TEXT_ANALYSIS, AgentCapability.REASONING]
    
    async def process(self, task: Task) -> TaskResult:
        """处理推理任务"""
        try:
            if task.task_type not in ["text_analysis", "reasoning"]:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"不支持的任务类型: {task.task_type}"
                )
            
            if task.task_type == "text_analysis":
                result = await self._analyze_text(task)
            else:  # reasoning
                result = await self._perform_reasoning(task)
            
            logger.info(f"推理任务完成: {task.task_id}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result
            )
            
        except Exception as e:
            logger.error(f"推理任务失败: {e}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    async def _analyze_text(self, task: Task) -> Dict[str, Any]:
        """分析文本内容"""
        text_content = task.data.get("text_content", "")
        if not text_content:
            raise ValueError("缺少文本内容")
        
        # 基础文本分析
        analysis = {
            "word_count": len(text_content.split()),
            "character_count": len(text_content),
            "sentence_count": len(re.split(r'[.!?]+', text_content)),
            "paragraph_count": len(text_content.split('\n\n')),
        }
        
        # 提取关键信息
        analysis.update({
            "keywords": self._extract_keywords(text_content),
            "entities": self._extract_entities(text_content),
            "summary": self._generate_summary(text_content),
            "topics": self._identify_topics(text_content)
        })
        
        return analysis
    
    async def _perform_reasoning(self, task: Task) -> Dict[str, Any]:
        """执行推理任务"""
        context = task.data.get("context", "")
        question = task.data.get("question", "")
        
        if not context or not question:
            raise ValueError("推理任务需要上下文和问题")
        
        # 简单的基于规则的推理
        reasoning_result = {
            "question": question,
            "context_analysis": self._analyze_context(context),
            "answer": self._generate_answer(context, question),
            "confidence": self._calculate_confidence(context, question),
            "reasoning_steps": self._get_reasoning_steps(context, question)
        }
        
        return reasoning_result
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（基于词频）
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # 计算词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的前10个词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """提取实体"""
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "numbers": []
        }
        
        # 简单的实体识别（基于正则表达式）
        
        # 日期模式
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ]
        for pattern in date_patterns:
            entities["dates"].extend(re.findall(pattern, text))
        
        # 数字模式
        number_patterns = [
            r'\d+\.\d+',  # 小数
            r'\d+%',      # 百分比
            r'\d+万',     # 万
            r'\d+亿',     # 亿
        ]
        for pattern in number_patterns:
            entities["numbers"].extend(re.findall(pattern, text))
        
        # 简单的人名识别（中文）
        person_pattern = r'[\u4e00-\u9fa5]{2,4}(?=先生|女士|教授|博士|主任|经理|总裁|CEO)'
        entities["persons"].extend(re.findall(person_pattern, text))
        
        return entities
    
    def _generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """生成摘要"""
        sentences = re.split(r'[.!?。！？]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences)
        
        # 简单的摘要生成：选择前几句和包含关键词最多的句子
        keywords = self._extract_keywords(text)[:5]
        
        sentence_scores = []
        for sentence in sentences:
            score = sum(1 for keyword in keywords if keyword in sentence.lower())
            sentence_scores.append((sentence, score))
        
        # 排序并选择得分最高的句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected_sentences = [s[0] for s in sentence_scores[:max_sentences]]
        
        return '. '.join(selected_sentences)
    
    def _identify_topics(self, text: str) -> List[str]:
        """识别主题"""
        # 基于关键词的简单主题识别
        keywords = self._extract_keywords(text)
        
        # 主题词典
        topic_keywords = {
            "技术": ["技术", "系统", "软件", "开发", "程序", "算法", "数据"],
            "商业": ["公司", "市场", "销售", "客户", "产品", "服务", "业务"],
            "教育": ["学习", "教育", "学校", "学生", "老师", "课程", "知识"],
            "医疗": ["医院", "医生", "病人", "治疗", "药物", "健康", "疾病"],
            "金融": ["银行", "投资", "金融", "资金", "贷款", "股票", "经济"]
        }
        
        identified_topics = []
        for topic, topic_words in topic_keywords.items():
            if any(keyword in topic_words for keyword in keywords):
                identified_topics.append(topic)
        
        return identified_topics
    
    def _analyze_context(self, context: str) -> Dict[str, Any]:
        """分析上下文"""
        return {
            "length": len(context),
            "complexity": self._calculate_text_complexity(context),
            "main_topics": self._identify_topics(context),
            "key_entities": self._extract_entities(context)
        }
    
    def _generate_answer(self, context: str, question: str) -> str:
        """生成答案"""
        # 简单的问答逻辑
        question_lower = question.lower()
        context_lower = context.lower()
        
        # 寻找相关句子
        sentences = re.split(r'[.!?。！？]+', context)
        relevant_sentences = []
        
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        for sentence in sentences:
            sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
            overlap = len(question_words & sentence_words)
            if overlap > 0:
                relevant_sentences.append((sentence.strip(), overlap))
        
        if relevant_sentences:
            # 选择重叠词最多的句子
            relevant_sentences.sort(key=lambda x: x[1], reverse=True)
            return relevant_sentences[0][0]
        else:
            return "抱歉，无法在给定上下文中找到相关答案。"
    
    def _calculate_confidence(self, context: str, question: str) -> float:
        """计算置信度"""
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        context_words = set(re.findall(r'\b\w+\b', context.lower()))
        
        overlap = len(question_words & context_words)
        total_question_words = len(question_words)
        
        if total_question_words == 0:
            return 0.0
        
        return min(overlap / total_question_words, 1.0)
    
    def _get_reasoning_steps(self, context: str, question: str) -> List[str]:
        """获取推理步骤"""
        return [
            "1. 分析问题关键词",
            "2. 在上下文中搜索相关信息",
            "3. 匹配问题与上下文内容",
            "4. 生成答案并评估置信度"
        ]
    
    def _calculate_text_complexity(self, text: str) -> str:
        """计算文本复杂度"""
        words = text.split()
        sentences = re.split(r'[.!?。！？]+', text)
        
        if len(sentences) == 0:
            return "简单"
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        if avg_words_per_sentence < 10:
            return "简单"
        elif avg_words_per_sentence < 20:
            return "中等"
        else:
            return "复杂"