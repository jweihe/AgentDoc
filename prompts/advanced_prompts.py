"""高级提示词模板

包含更丰富的文本处理和分析功能的提示词模板。
"""

from .base import BasePrompt, PromptTemplate

class AdvancedTextPrompt(BasePrompt):
    """高级文本处理提示词类"""
    
    def _load_templates(self):
        """加载高级文本处理模板"""
        
        # 深度文本分析模板
        deep_analysis_template = PromptTemplate(
            name="deep_analysis",
            description="深度文本分析模板",
            required_vars=["text"],
            template="""请对以下文本进行深度分析：

文本内容：
$text

请从以下维度进行分析：

1. **主题分析**
   - 核心主题
   - 次要主题
   - 主题关联性

2. **结构分析**
   - 文本结构
   - 逻辑层次
   - 段落关系

3. **语言特征**
   - 写作风格
   - 语言特点
   - 修辞手法

4. **内容质量**
   - 信息密度
   - 论证逻辑
   - 可信度评估

5. **关键信息**
   - 核心观点
   - 重要数据
   - 关键结论

分析结果："""
        )
        
        # 智能摘要模板
        intelligent_summary_template = PromptTemplate(
            name="intelligent_summary",
            description="智能摘要生成模板",
            required_vars=["text", "summary_type"],
            template="""请为以下文本生成$summary_type摘要：

原文内容：
$text

摘要要求：
- 准确提取核心信息
- 保持逻辑清晰
- 语言简洁明了
- 突出重点内容

$summary_type摘要："""
        )
        
        # 多角度问答模板
        multi_perspective_qa_template = PromptTemplate(
            name="multi_perspective_qa",
            description="多角度问答模板",
            required_vars=["context", "question"],
            template="""基于以下上下文，请从多个角度回答问题：

上下文：
$context

问题：
$question

请从以下角度进行分析和回答：

1. **直接回答**
   基于文本内容的直接答案

2. **深层分析**
   问题背后的深层含义和影响

3. **相关联想**
   与问题相关的其他信息和观点

4. **实践应用**
   答案在实际中的应用价值

5. **延伸思考**
   由此问题引发的进一步思考

多角度回答："""
        )
        
        # 文本对比分析模板
        text_comparison_template = PromptTemplate(
            name="text_comparison",
            description="文本对比分析模板",
            required_vars=["text1", "text2"],
            template="""请对以下两个文本进行详细对比分析：

文本A：
$text1

文本B：
$text2

对比分析：

1. **内容对比**
   - 共同点：
   - 差异点：
   - 互补性：

2. **观点对比**
   - 一致观点：
   - 分歧观点：
   - 观点冲突：

3. **质量对比**
   - 论证强度：
   - 证据充分性：
   - 逻辑严密性：

4. **风格对比**
   - 写作风格：
   - 表达方式：
   - 语言特色：

5. **价值对比**
   - 信息价值：
   - 实用价值：
   - 学术价值：

对比结论："""
        )
        
        # 创意写作辅助模板
        creative_writing_template = PromptTemplate(
            name="creative_writing",
            description="创意写作辅助模板",
            required_vars=["topic", "style", "length"],
            template="""请基于以下要求进行创意写作：

写作主题：$topic
写作风格：$style
文本长度：$length

写作指导：

1. **主题发展**
   - 核心思想的展开
   - 相关素材的整合
   - 创新角度的挖掘

2. **结构设计**
   - 开头的吸引力
   - 中间的逻辑性
   - 结尾的感染力

3. **语言运用**
   - 词汇的丰富性
   - 句式的多样性
   - 修辞的恰当性

4. **情感表达**
   - 情感的真实性
   - 情感的层次性
   - 情感的感染力

创作内容："""
        )
        
        # 学术写作辅助模板
        academic_writing_template = PromptTemplate(
            name="academic_writing",
            description="学术写作辅助模板",
            required_vars=["topic", "field", "requirement"],
            template="""请协助完成以下学术写作任务：

研究主题：$topic
学科领域：$field
具体要求：$requirement

写作指导：

1. **文献综述**
   - 相关研究梳理
   - 研究现状分析
   - 研究空白识别

2. **论证结构**
   - 论点的明确性
   - 论据的充分性
   - 论证的逻辑性

3. **学术规范**
   - 术语的准确性
   - 引用的规范性
   - 格式的标准性

4. **创新价值**
   - 理论贡献
   - 实践意义
   - 方法创新

学术内容："""
        )
        
        # 文本润色模板
        text_polishing_template = PromptTemplate(
            name="text_polishing",
            description="文本润色优化模板",
            required_vars=["original_text", "polish_focus"],
            template="""请对以下文本进行润色优化：

原始文本：
$original_text

润色重点：$polish_focus

润色要求：

1. **语言优化**
   - 词汇精准性
   - 句式流畅性
   - 表达清晰性

2. **结构调整**
   - 逻辑顺序
   - 段落衔接
   - 层次分明

3. **风格统一**
   - 语言风格
   - 表达方式
   - 整体基调

4. **错误修正**
   - 语法错误
   - 用词不当
   - 逻辑漏洞

润色后文本："""
        )
        
        # 添加所有模板
        self.add_template(deep_analysis_template)
        self.add_template(intelligent_summary_template)
        self.add_template(multi_perspective_qa_template)
        self.add_template(text_comparison_template)
        self.add_template(creative_writing_template)
        self.add_template(academic_writing_template)
        self.add_template(text_polishing_template)

class SpecializedPrompt(BasePrompt):
    """专业化提示词类"""
    
    def _load_templates(self):
        """加载专业化模板"""
        
        # 技术文档分析模板
        tech_doc_analysis_template = PromptTemplate(
            name="tech_doc_analysis",
            description="技术文档分析模板",
            required_vars=["document"],
            template="""请对以下技术文档进行专业分析：

技术文档：
$document

分析维度：

1. **技术内容**
   - 核心技术点
   - 技术难点
   - 创新之处

2. **实现方案**
   - 技术架构
   - 实现路径
   - 关键步骤

3. **应用价值**
   - 实用性评估
   - 适用场景
   - 推广前景

4. **技术风险**
   - 潜在问题
   - 风险评估
   - 应对策略

技术分析报告："""
        )
        
        # 商业文档分析模板
        business_doc_analysis_template = PromptTemplate(
            name="business_doc_analysis",
            description="商业文档分析模板",
            required_vars=["document"],
            template="""请对以下商业文档进行深度分析：

商业文档：
$document

分析框架：

1. **商业模式**
   - 价值主张
   - 收入模式
   - 成本结构

2. **市场分析**
   - 目标市场
   - 竞争态势
   - 市场机会

3. **运营策略**
   - 运营模式
   - 执行计划
   - 资源配置

4. **风险评估**
   - 市场风险
   - 运营风险
   - 财务风险

5. **发展前景**
   - 增长潜力
   - 扩展机会
   - 长期价值

商业分析报告："""
        )
        
        # 法律文档分析模板
        legal_doc_analysis_template = PromptTemplate(
            name="legal_doc_analysis",
            description="法律文档分析模板",
            required_vars=["document"],
            template="""请对以下法律文档进行专业分析：

法律文档：
$document

分析要点：

1. **法律条款**
   - 核心条款
   - 关键权利
   - 重要义务

2. **法律风险**
   - 潜在风险
   - 风险等级
   - 防范措施

3. **合规性**
   - 法规符合性
   - 标准一致性
   - 程序完整性

4. **执行性**
   - 可操作性
   - 执行难度
   - 监督机制

法律分析意见："""
        )
        
        # 学术论文分析模板
        academic_paper_analysis_template = PromptTemplate(
            name="academic_paper_analysis",
            description="学术论文分析模板",
            required_vars=["paper"],
            template="""请对以下学术论文进行深度分析：

学术论文：
$paper

分析框架：

1. **研究问题**
   - 问题定义
   - 研究意义
   - 创新价值

2. **研究方法**
   - 方法选择
   - 方法适用性
   - 方法局限性

3. **研究结果**
   - 主要发现
   - 数据分析
   - 结果可信度

4. **理论贡献**
   - 理论创新
   - 实践指导
   - 学术影响

5. **研究局限**
   - 方法局限
   - 数据局限
   - 结论局限

学术评议报告："""
        )
        
        # 添加所有模板
        self.add_template(tech_doc_analysis_template)
        self.add_template(business_doc_analysis_template)
        self.add_template(legal_doc_analysis_template)
        self.add_template(academic_paper_analysis_template)

class InteractivePrompt(BasePrompt):
    """交互式提示词类"""
    
    def _load_templates(self):
        """加载交互式模板"""
        
        # 引导式问答模板
        guided_qa_template = PromptTemplate(
            name="guided_qa",
            description="引导式问答模板",
            required_vars=["context", "question", "user_level"],
            template="""基于用户水平（$user_level）和以下上下文，请提供引导式回答：

上下文：
$context

用户问题：
$question

回答策略：

1. **直接回答**
   简洁明了地回答核心问题

2. **背景解释**
   提供必要的背景知识

3. **深入分析**
   根据用户水平提供适当的深度分析

4. **相关拓展**
   推荐相关的学习内容或延伸阅读

5. **互动引导**
   提出进一步的思考问题

引导式回答："""
        )
        
        # 教学辅助模板
        teaching_assistant_template = PromptTemplate(
            name="teaching_assistant",
            description="教学辅助模板",
            required_vars=["content", "learning_objective"],
            template="""作为教学助手，请基于以下内容设计学习方案：

教学内容：
$content

学习目标：
$learning_objective

教学设计：

1. **知识点梳理**
   - 核心概念
   - 重点难点
   - 知识结构

2. **学习路径**
   - 学习顺序
   - 学习方法
   - 时间安排

3. **练习设计**
   - 基础练习
   - 进阶练习
   - 综合应用

4. **评估方式**
   - 理解检查
   - 应用评估
   - 反馈机制

教学方案："""
        )
        
        # 添加所有模板
        self.add_template(guided_qa_template)
        self.add_template(teaching_assistant_template)