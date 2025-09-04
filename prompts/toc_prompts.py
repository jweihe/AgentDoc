"""目录提取相关的提示词"""

from .base import BasePrompt, PromptTemplate

class TOCPrompt(BasePrompt):
    """基础目录提取提示词"""
    
    def _load_templates(self):
        """加载目录提取模板"""
        
        # 基础目录提取模板
        base_template = PromptTemplate(
            name="base_toc",
            description="基础目录提取，不包含页码",
            required_vars=[],
            template="""请仔细分析这张图片，识别并提取其中的标题信息。

要求：
1. 识别所有标题文本，包括主标题、副标题等
2. 判断标题的层级关系（如一级标题、二级标题等）
3. 保持标题的原始顺序
4. 去除重复的标题
5. 忽略页眉、页脚、页码等非标题内容

输出格式：
请按以下JSON格式输出：
{
  "titles": [
    {
      "text": "标题文本",
      "level": 1,
      "order": 1
    }
  ]
}

注意：
- level表示标题层级，1为最高级
- order表示标题在文档中的出现顺序
- 只输出JSON，不要其他解释文字"""
        )
        
        self.add_template(base_template)

class TOCWithPagesPrompt(BasePrompt):
    """带页码的目录提取提示词"""
    
    def _load_templates(self):
        """加载带页码的目录提取模板"""
        
        # 带页码的目录提取模板
        with_pages_template = PromptTemplate(
            name="toc_with_pages",
            description="目录提取，包含页码信息",
            required_vars=["page_number"],
            template="""请仔细分析这张图片（第$page_number页），识别并提取其中的标题信息。

要求：
1. 识别所有标题文本，包括主标题、副标题等
2. 判断标题的层级关系（如一级标题、二级标题等）
3. 保持标题的原始顺序
4. 去除重复的标题
5. 忽略页眉、页脚、页码等非标题内容
6. 记录标题所在的页码

输出格式：
请按以下JSON格式输出：
{
  "titles": [
    {
      "text": "标题文本",
      "level": 1,
      "order": 1,
      "page": $page_number
    }
  ]
}

注意：
- level表示标题层级，1为最高级
- order表示标题在文档中的出现顺序
- page表示标题所在的页码
- 只输出JSON，不要其他解释文字"""
        )
        
        self.add_template(with_pages_template)

class IntegrationPrompt(BasePrompt):
    """结果整合提示词"""
    
    def _load_templates(self):
        """加载结果整合模板"""
        
        # 基础整合模板
        integration_template = PromptTemplate(
            name="integration",
            description="整合多个批次的提取结果",
            required_vars=["batch_results"],
            template="""请整合以下多个批次的标题提取结果，生成最终的目录结构。

输入数据：
$batch_results

整合要求：
1. 合并所有批次的标题
2. 去除重复的标题（文本完全相同的标题）
3. 保持标题的正确顺序（按页码和在页面中的位置）
4. 修正标题层级关系，确保层级的连续性和逻辑性
5. 统一标题格式，去除多余的空格和特殊字符

输出格式：
请按以下JSON格式输出最终的目录结构：
{
  "toc": [
    {
      "text": "标题文本",
      "level": 1,
      "order": 1,
      "page": 1
    }
  ],
  "summary": {
    "total_titles": 0,
    "max_level": 0,
    "page_range": [1, 10]
  }
}

注意：
- 确保level从1开始，且连续递增
- order表示最终的全局顺序
- summary包含统计信息
- 只输出JSON，不要其他解释文字"""
        )
        
        # 带页码的整合模板
        integration_with_pages_template = PromptTemplate(
            name="integration_with_pages",
            description="整合多个批次的提取结果，包含详细页码信息",
            required_vars=["batch_results", "total_pages"],
            template="""请整合以下多个批次的标题提取结果，生成最终的目录结构。

输入数据：
$batch_results

文档总页数：$total_pages

整合要求：
1. 合并所有批次的标题
2. 去除重复的标题（文本完全相同且页码相近的标题）
3. 保持标题的正确顺序（按页码和在页面中的位置）
4. 修正标题层级关系，确保层级的连续性和逻辑性
5. 统一标题格式，去除多余的空格和特殊字符
6. 验证页码的合理性（1-$total_pages）

输出格式：
请按以下JSON格式输出最终的目录结构：
{
  "toc": [
    {
      "text": "标题文本",
      "level": 1,
      "order": 1,
      "page": 1
    }
  ],
  "summary": {
    "total_titles": 0,
    "max_level": 0,
    "page_range": [1, $total_pages],
    "pages_with_titles": [1, 3, 5]
  }
}

注意：
- 确保level从1开始，且连续递增
- order表示最终的全局顺序
- page必须在1-$total_pages范围内
- pages_with_titles列出包含标题的页码
- 只输出JSON，不要其他解释文字"""
        )
        
        self.add_template(integration_template)
        self.add_template(integration_with_pages_template)