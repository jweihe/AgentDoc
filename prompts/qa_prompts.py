"""问答相关的提示词"""

from .base import BasePrompt, PromptTemplate

class QAPrompt(BasePrompt):
    """问答提示词类"""
    
    def _load_templates(self):
        """加载问答模板"""
        
        # 基础问答模板
        basic_qa_template = PromptTemplate(
            name="basic_qa",
            description="基础问答模板",
            required_vars=["context", "question"],
            template="""基于以下上下文信息，请回答用户的问题。

上下文信息：
$context

用户问题：
$question

请根据上下文信息准确回答问题。如果上下文中没有相关信息，请明确说明。

回答："""
        )
        
        # 多轮对话问答模板
        multi_turn_qa_template = PromptTemplate(
            name="multi_turn_qa",
            description="多轮对话问答模板",
            required_vars=["context", "history", "question"],
            template="""基于以下上下文信息和对话历史，请回答用户的问题。

上下文信息：
$context

对话历史：
$history

当前问题：
$question

请结合上下文信息和对话历史，准确回答当前问题。保持对话的连贯性。

回答："""
        )
        
        # 推理问答模板
        reasoning_qa_template = PromptTemplate(
            name="reasoning_qa",
            description="推理问答模板",
            required_vars=["context", "question"],
            template="""基于以下上下文信息，请通过逐步推理来回答用户的问题。

上下文信息：
$context

用户问题：
$question

请按照以下步骤进行推理：
1. 分析问题的关键信息
2. 从上下文中找到相关证据
3. 进行逻辑推理
4. 得出结论

推理过程：

最终答案："""
        )
        
        # 比较问答模板
        comparison_qa_template = PromptTemplate(
            name="comparison_qa",
            description="比较问答模板",
            required_vars=["context", "question"],
            template="""基于以下上下文信息，请回答涉及比较的问题。

上下文信息：
$context

比较问题：
$question

请从以下角度进行比较分析：
1. 相同点
2. 不同点
3. 优缺点
4. 适用场景

比较分析："""
        )
        
        # 总结问答模板
        summary_qa_template = PromptTemplate(
            name="summary_qa",
            description="总结问答模板",
            required_vars=["context", "question"],
            template="""基于以下上下文信息，请回答总结性问题。

上下文信息：
$context

总结问题：
$question

请提供简洁而全面的总结，包括：
1. 主要观点
2. 关键信息
3. 重要结论

总结："""
        )
        
        self.add_template(basic_qa_template)
        self.add_template(multi_turn_qa_template)
        self.add_template(reasoning_qa_template)
        self.add_template(comparison_qa_template)
        self.add_template(summary_qa_template)

class DocumentQAPrompt(BasePrompt):
    """文档问答提示词类"""
    
    def _load_templates(self):
        """加载文档问答模板"""
        
        # 文档理解模板
        doc_understanding_template = PromptTemplate(
            name="doc_understanding",
            description="文档理解模板",
            required_vars=["document", "question"],
            template="""请仔细阅读以下文档内容，然后回答相关问题。

文档内容：
$document

问题：
$question

请基于文档内容准确回答问题，并引用相关段落作为支撑。

回答："""
        )
        
        # 文档摘要模板
        doc_summary_template = PromptTemplate(
            name="doc_summary",
            description="文档摘要模板",
            required_vars=["document"],
            template="""请为以下文档生成摘要。

文档内容：
$document

请生成一个简洁而全面的摘要，包括：
1. 文档主题
2. 主要内容
3. 关键观点
4. 重要结论

摘要："""
        )
        
        # 文档关键信息提取模板
        key_info_extraction_template = PromptTemplate(
            name="key_info_extraction",
            description="关键信息提取模板",
            required_vars=["document", "info_type"],
            template="""请从以下文档中提取指定类型的关键信息。

文档内容：
$document

需要提取的信息类型：
$info_type

请按照以下格式提取信息：
- 信息1：[具体内容]
- 信息2：[具体内容]
- ...

提取结果："""
        )
        
        self.add_template(doc_understanding_template)
        self.add_template(doc_summary_template)
        self.add_template(key_info_extraction_template)