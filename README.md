# AgentDoc - 智能文档分析系统

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
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

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

### QA模块 (agentdoc.qa)
- **QAEngine**: 智能问答引擎，支持复杂问题处理
- **DocumentIndexer**: 文档索引器，建立高效的文档索引
- **DocumentRetriever**: 文档检索器，精确检索相关内容
- **CitationManager**: 引用管理器，自动生成准确引用
- **SimpleReasoner**: 推理器，支持逻辑推理和分析

### Models模块 (agentdoc.models)
- **ModelManager**: 模型管理器，统一管理各种语言模型
- **ModelFactory**: 模型工厂，动态创建模型实例
- **BaseModel**: 模型基类，定义统一接口

### Plugins模块 (agentdoc.plugins)
- **PluginManager**: 插件管理器，支持动态加载插件
- **BasePlugin**: 插件基类，定义插件接口
- **ProcessorPlugin**: 处理器插件，扩展文档处理能力

### Queue模块 (agentdoc.queue)
- **TaskQueue**: 任务队列，支持异步任务处理
- **TaskManager**: 任务管理器，管理任务生命周期
- **Worker**: 工作进程，执行具体任务

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

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/jweihe/AgentDoc)
- 问题反馈: [Issues](https://github.com/jweihe/AgentDoc/issues)
- 邮箱: team@agentdoc.ai

---

中文版本 | [English Version](README_EN.md)