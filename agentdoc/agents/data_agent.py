"""DataAgent - 数据分析Agent

负责处理数据分析、统计和可视化任务。
"""

import json
import csv
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .base import BaseAgent, Task, TaskResult, TaskStatus, AgentCapability

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """数据分析Agent"""
    
    def __init__(self):
        super().__init__("DataAgent")
        self.supported_formats = [".csv", ".json", ".xlsx"]
        
    def get_capabilities(self) -> List[AgentCapability]:
        """获取DataAgent能力"""
        return [AgentCapability.TEXT_ANALYSIS]
    
    async def process(self, task: Task) -> TaskResult:
        """处理数据分析任务"""
        try:
            if task.task_type not in ["data_analysis", "text_analysis"]:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"不支持的任务类型: {task.task_type}"
                )
            
            if task.task_type == "data_analysis":
                return await self._analyze_data(task)
            elif task.task_type == "text_analysis":
                return await self._analyze_text(task)
                
        except Exception as e:
            logger.error(f"数据分析失败: {e}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
    
    async def _analyze_data(self, task: Task) -> TaskResult:
        """分析结构化数据"""
        data = task.data.get("data")
        analysis_type = task.data.get("analysis_type", "basic")
        
        if not data:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="缺少数据"
            )
        
        if analysis_type == "basic":
            result = await self._basic_statistics(data)
        elif analysis_type == "frequency":
            result = await self._frequency_analysis(data)
        elif analysis_type == "correlation":
            result = await self._correlation_analysis(data)
        else:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=f"不支持的分析类型: {analysis_type}"
            )
        
        # 保存分析结果
        self.save_memory(f"analysis_{task.task_id}", result)
        
        logger.info(f"完成数据分析: {analysis_type}")
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            result=result
        )
    
    async def _analyze_text(self, task: Task) -> TaskResult:
        """分析文本数据"""
        text = task.data.get("text")
        analysis_type = task.data.get("analysis_type", "basic")
        
        if not text:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="缺少文本数据"
            )
        
        if analysis_type == "basic":
            result = await self._basic_text_analysis(text)
        elif analysis_type == "keywords":
            result = await self._keyword_extraction(text)
        elif analysis_type == "sentiment":
            result = await self._sentiment_analysis(text)
        else:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=f"不支持的文本分析类型: {analysis_type}"
            )
        
        # 保存分析结果
        self.save_memory(f"text_analysis_{task.task_id}", result)
        
        logger.info(f"完成文本分析: {analysis_type}")
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            result=result
        )
    
    async def _basic_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基础统计分析"""
        if not data:
            return {"error": "数据为空"}
        
        total_records = len(data)
        
        # 分析数值字段
        numeric_fields = {}
        for record in data:
            for key, value in record.items():
                if isinstance(value, (int, float)):
                    if key not in numeric_fields:
                        numeric_fields[key] = []
                    numeric_fields[key].append(value)
        
        statistics = {
            "total_records": total_records,
            "numeric_fields": {}
        }
        
        for field, values in numeric_fields.items():
            if values:
                statistics["numeric_fields"][field] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "sum": sum(values)
                }
        
        return statistics
    
    async def _frequency_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """频率分析"""
        if not data:
            return {"error": "数据为空"}
        
        frequency_analysis = {}
        
        for record in data:
            for key, value in record.items():
                if isinstance(value, str):
                    if key not in frequency_analysis:
                        frequency_analysis[key] = {}
                    
                    if value not in frequency_analysis[key]:
                        frequency_analysis[key][value] = 0
                    frequency_analysis[key][value] += 1
        
        # 排序频率结果
        for field in frequency_analysis:
            frequency_analysis[field] = dict(
                sorted(frequency_analysis[field].items(), 
                      key=lambda x: x[1], reverse=True)
            )
        
        return {
            "frequency_analysis": frequency_analysis,
            "total_records": len(data)
        }
    
    async def _correlation_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """相关性分析"""
        # 简化的相关性分析实现
        numeric_data = {}
        
        for record in data:
            for key, value in record.items():
                if isinstance(value, (int, float)):
                    if key not in numeric_data:
                        numeric_data[key] = []
                    numeric_data[key].append(value)
        
        if len(numeric_data) < 2:
            return {"error": "需要至少两个数值字段进行相关性分析"}
        
        correlations = {}
        fields = list(numeric_data.keys())
        
        for i, field1 in enumerate(fields):
            for field2 in fields[i+1:]:
                values1 = numeric_data[field1]
                values2 = numeric_data[field2]
                
                if len(values1) == len(values2) and len(values1) > 1:
                    # 简单的皮尔逊相关系数计算
                    n = len(values1)
                    sum1 = sum(values1)
                    sum2 = sum(values2)
                    sum1_sq = sum(x*x for x in values1)
                    sum2_sq = sum(x*x for x in values2)
                    sum_prod = sum(x*y for x, y in zip(values1, values2))
                    
                    numerator = n * sum_prod - sum1 * sum2
                    denominator = ((n * sum1_sq - sum1**2) * (n * sum2_sq - sum2**2))**0.5
                    
                    if denominator != 0:
                        correlation = numerator / denominator
                        correlations[f"{field1}_vs_{field2}"] = round(correlation, 4)
        
        return {
            "correlations": correlations,
            "fields_analyzed": fields
        }
    
    async def _basic_text_analysis(self, text: str) -> Dict[str, Any]:
        """基础文本分析"""
        words = text.split()
        sentences = text.split('。')
        paragraphs = text.split('\n\n')
        
        # 词频统计
        word_freq = {}
        for word in words:
            word = word.strip('，。！？；：""''()[]{}').lower()
            if word:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 排序词频
        top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20])
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in paragraphs if p.strip()]),
            "top_words": top_words,
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
        }
    
    async def _keyword_extraction(self, text: str) -> Dict[str, Any]:
        """关键词提取"""
        # 简单的关键词提取实现
        words = text.split()
        
        # 停用词列表（简化版）
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        # 过滤停用词并统计词频
        word_freq = {}
        for word in words:
            word = word.strip('，。！？；：""''()[]{}').lower()
            if word and word not in stop_words and len(word) > 1:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 提取关键词（高频词）
        keywords = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "keywords": keywords,
            "total_unique_words": len(word_freq),
            "extraction_method": "frequency_based"
        }
    
    async def _sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """情感分析（简化版）"""
        # 简单的情感词典
        positive_words = {'好', '棒', '优秀', '喜欢', '满意', '高兴', '开心', '成功', '完美', '赞'}
        negative_words = {'坏', '差', '糟糕', '讨厌', '失望', '难过', '失败', '问题', '错误', '烦'}
        
        words = text.split()
        positive_count = 0
        negative_count = 0
        
        for word in words:
            word = word.strip('，。！？；：""''()[]{}').lower()
            if word in positive_words:
                positive_count += 1
            elif word in negative_words:
                negative_count += 1
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment = "neutral"
            confidence = 0.0
        elif positive_count > negative_count:
            sentiment = "positive"
            confidence = positive_count / total_sentiment_words
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = negative_count / total_sentiment_words
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "positive_words_count": positive_count,
            "negative_words_count": negative_count,
            "analysis_method": "dictionary_based"
        }