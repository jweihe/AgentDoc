# AgentDoc - 智能文档分析系统

[English Version](README.md) | 中文版本

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 项目简介

AgentDoc 是一个轻量级、高效的智能文档分析系统，专注于文档解析、智能问答和内容检索。系统采用模块化架构设计，支持多种文档格式处理，提供精确的引用管理和智能推理功能。

## 核心特性

- 🤖 **智能问答**: 基于文档内容的精确问答，支持上下文理解和推理
- 📍 **精确引用**: 自动标注答案来源，提供准确的文档位置引用
- 🚀 **多模型支持**: 灵活的模型管理系统，支持多种语言模型
- 📄 **文档处理**: 支持PDF、DOCX等多种文档格式的智能解析
- 🔧 **模块化架构**: 可扩展的插件系统和处理器架构
- 🔍 **智能检索**: 高效的文档索引和检索系统
- 📊 **任务队列**: 支持异步任务处理和批量操作
- ⚡ **轻量高效**: 优化的性能和资源使用

## 快速开始

### 环境要求

- Python 3.8+
- 推荐使用虚拟环境

### 安装

```bash
# 克隆项目
git clone https://github.com/jweihe/AgentDoc.git
cd AgentDoc

# 创建虚拟环境
python -m venv agentdoc-env
source agentdoc-env/bin/activate  # Linux/Mac
# 或 agentdoc-env\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

```python
from agentdoc import ModelManager, PDFProcessor
from agentdoc.qa import QAEngine, DocumentIndexer

# 初始化组件
model_manager = ModelManager()
pdf_processor = PDFProcessor()
qa_engine = QAEngine()

# 处理文档
document = pdf_processor.process("document.pdf")

# 建立索引
indexer = DocumentIndexer()
chunks = indexer.index_document(document)

# 智能问答
result = qa_engine.answer_question(
    question="文档的主要内容是什么？",
    chunks=chunks
)

print(f"答案: {result.answer}")
print(f"引用: {result.citations}")
```

## 项目结构

```
AgentDoc/
├── agentdoc/              # 主包
│   ├── core/              # 核心模块 (配置、日志、异常处理)
│   ├── models/            # 模型管理 (模型工厂、管理器)
│   ├── processors/        # 文档处理器 (PDF、批量处理)
│   ├── qa/                # 智能问答 (引擎、索引、检索、推理)
│   ├── plugins/           # 插件系统 (可扩展处理器)
│   ├── queue/             # 任务队列 (异步任务管理)
│   ├── agents/            # Agent模块 (智能代理)
│   ├── prompts/           # 提示模板 (预定义提示)
│   ├── web/               # Web界面
│   ├── api/               # API服务
│   └── cli/               # 命令行工具
├── tests/                 # 测试代码
├── requirements.txt       # 项目依赖
├── pyproject.toml         # 项目配置
└── README.md              # 项目文档
```

## 核心模块说明

### 🧠 QA模块 (agentdoc.qa)
智能问答系统的核心引擎，采用RAG (Retrieval-Augmented Generation) 架构

- **QAEngine**: 智能问答引擎
  - 支持多轮对话和上下文理解
  - 集成向量检索和语义匹配
  - 支持复杂查询分解和重写
  - 提供置信度评分和答案质量评估

- **DocumentIndexer**: 高性能文档索引器
  - 基于向量数据库的语义索引
  - 支持增量索引和实时更新
  - 多级索引策略：章节级、段落级、句子级
  - 智能文档分块和重叠处理

- **DocumentRetriever**: 精准文档检索器
  - 混合检索策略：向量检索 + BM25 + 重排序
  - 支持多模态检索（文本、图片、表格）
  - 动态检索策略调整
  - 检索结果去重和聚合

- **CitationManager**: 智能引用管理器
  - 自动生成精确的页码和段落引用
  - 支持多种引用格式（APA、MLA、Chicago等）
  - 引用链追踪和验证
  - 批量引用导出功能

- **SimpleReasoner**: 逻辑推理引擎
  - 支持因果推理和逻辑链构建
  - 多步推理和中间结果缓存
  - 推理路径可视化和解释
  - 支持假设验证和反驳论证

### 🤖 Models模块 (agentdoc.models)
企业级模型管理和调度系统

- **ModelManager**: 统一模型管理器
  - 支持多种LLM：OpenAI、Claude、Qwen、GLM等
  - 模型负载均衡和故障转移
  - 实时性能监控和成本统计
  - 模型版本管理和A/B测试

- **ModelFactory**: 智能模型工厂
  - 动态模型实例化和配置
  - 模型能力自动检测和匹配
  - 支持模型组合和级联调用
  - 模型缓存和预热机制

- **BaseModel**: 统一模型接口
  - 标准化API接口设计
  - 支持流式输出和批量处理
  - 内置重试机制和错误处理
  - 模型调用链路追踪

### 🔌 Plugins模块 (agentdoc.plugins)
可扩展的插件生态系统

- **PluginManager**: 插件生命周期管理器
  - 热插拔插件加载和卸载
  - 插件依赖管理和版本控制
  - 插件安全沙箱和权限控制
  - 插件性能监控和资源限制

- **BasePlugin**: 插件开发框架
  - 标准化插件接口和生命周期
  - 插件配置管理和参数验证
  - 插件间通信和事件机制
  - 插件错误处理和日志记录

- **ProcessorPlugin**: 文档处理插件
  - 支持自定义文档格式解析
  - 文档预处理和后处理管道
  - 多语言文档处理支持
  - 文档质量评估和优化

### ⚡ Queue模块 (agentdoc.queue)
高性能异步任务处理系统

- **TaskQueue**: 分布式任务队列
  - 支持Redis、RabbitMQ等消息队列
  - 任务优先级和延迟执行
  - 任务去重和幂等性保证
  - 死信队列和任务重试机制

- **TaskManager**: 任务调度管理器
  - 任务生命周期全程跟踪
  - 动态工作进程扩缩容
  - 任务执行统计和性能分析
  - 任务依赖管理和批量操作

- **Worker**: 高效任务执行器
  - 多进程/多线程并发执行
  - 任务执行环境隔离
  - 资源使用监控和限制
  - 任务执行日志和错误追踪

### 📄 Processors模块 (agentdoc.processors)
多格式文档处理引擎

- **PDFProcessor**: PDF文档专业处理器
  - 高精度文本提取和版面分析
  - 表格、图片、公式识别
  - OCR集成和文字识别
  - 文档结构化和元数据提取

- **BatchProcessor**: 批量处理调度器
  - 大规模文档并行处理
  - 处理进度实时监控
  - 错误恢复和断点续传
  - 处理结果统计和报告

### 🎯 Agents模块 (agentdoc.agents)
智能代理和自动化系统

- **DocumentAgent**: 文档智能代理
  - 自动文档分析和摘要生成
  - 文档质量评估和改进建议
  - 多文档关联分析和对比
  - 文档知识图谱构建

### 🌐 Web模块 (agentdoc.web)
现代化Web界面

- **WebUI**: 响应式用户界面
  - 拖拽式文档上传和管理
  - 实时问答和结果展示
  - 可视化分析和图表展示
  - 多用户协作和权限管理

### 🔧 Utils模块 (agentdoc.utils)
通用工具和辅助功能

- **ConfigManager**: 配置管理器
- **Logger**: 结构化日志系统
- **FileHandler**: 文件操作工具
- **TextProcessor**: 文本处理工具

## 高级用法

### 自定义插件开发

```python
from agentdoc.plugins import BasePlugin, PluginManager

class CustomProcessor(BasePlugin):
    def process(self, document):
        # 自定义处理逻辑
        return processed_document

# 注册插件
plugin_manager = PluginManager()
plugin_manager.register_plugin("custom", CustomProcessor())
```

### 批量文档处理

```python
from agentdoc.processors import BatchProcessor
from agentdoc.queue import TaskQueue

# 批量处理
batch_processor = BatchProcessor()
task_queue = TaskQueue()

# 添加任务
for pdf_file in pdf_files:
    task_queue.add_task("process_pdf", {"file_path": pdf_file})

# 执行批量处理
results = batch_processor.process_batch(task_queue)
```

### 配置管理

```python
from agentdoc.core import Settings

# 自定义配置
settings = Settings(
    model_name="qwen2.5",
    max_chunk_size=1000,
    overlap_size=100,
    citation_enabled=True
)
```

## 开发指南

### 环境设置

```bash
# 安装开发依赖
pip install pytest black flake8

# 代码格式化
black agentdoc/

# 代码检查
flake8 agentdoc/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
python test_qa_module.py
python test_plugins.py
```