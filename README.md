# AgentDoc - Intelligent Document Analysis System

English Version | [中文版本](README_EN.md)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/jweihe/AgentDoc?style=social)](https://github.com/jweihe/AgentDoc)
[![GitHub Forks](https://img.shields.io/github/forks/jweihe/AgentDoc?style=social)](https://github.com/jweihe/AgentDoc)

## Project Overview

AgentDoc is a production-ready, lightweight intelligent document analysis system designed for enterprise-grade document processing, intelligent Q&A, and content retrieval. Built with a modular architecture, it provides seamless integration capabilities, precise citation management, and advanced reasoning functionalities for modern AI applications.

## 🚀 Core Features

### 🤖 **Advanced Intelligent Q&A**
- **Context-Aware Understanding**: Deep comprehension of document context with multi-turn conversation support
- **Complex Query Processing**: Handle sophisticated questions requiring cross-document reasoning
- **Multi-Language Support**: Native support for Chinese, English, and other major languages
- **Confidence Scoring**: Provides reliability scores for generated answers

### 📍 **Precision Citation System**
- **Source Traceability**: Automatic annotation of answer sources with exact document locations
- **Multi-Format References**: Support for page numbers, line numbers, and section references
- **Citation Validation**: Ensures accuracy and reliability of all citations
- **Export Compatibility**: Generate citations in academic formats (APA, MLA, Chicago)

### 🚀 **Enterprise Model Management**
- **Multi-Model Architecture**: Seamless integration with OpenAI, Anthropic, local models, and custom APIs
- **Dynamic Model Switching**: Runtime model selection based on task requirements
- **Performance Optimization**: Intelligent caching and request batching
- **Cost Management**: Built-in usage tracking and cost optimization

### 📄 **Advanced Document Processing**
- **Universal Format Support**: PDF, DOCX, TXT, Markdown, HTML, and more
- **OCR Integration**: Extract text from scanned documents and images
- **Structure Recognition**: Intelligent parsing of tables, headers, and document hierarchy
- **Metadata Extraction**: Automatic extraction of document properties and annotations

### 🔧 **Production-Ready Architecture**
- **Plugin Ecosystem**: Extensible architecture with hot-swappable components
- **Microservices Ready**: Docker support with horizontal scaling capabilities
- **API-First Design**: RESTful APIs with comprehensive documentation
- **Configuration Management**: Environment-based configuration with validation

### 🔍 **High-Performance Retrieval**
- **Vector Search**: Advanced semantic search with embedding models
- **Hybrid Retrieval**: Combines keyword and semantic search for optimal results
- **Real-time Indexing**: Incremental updates without full reindexing
- **Search Analytics**: Query performance monitoring and optimization

### 📊 **Scalable Task Management**
- **Async Processing**: Non-blocking task execution with queue management
- **Batch Operations**: Efficient processing of large document collections
- **Progress Tracking**: Real-time status updates and completion notifications
- **Error Handling**: Robust retry mechanisms and failure recovery

### ⚡ **Performance & Reliability**
- **Memory Optimization**: Efficient memory usage for large document processing
- **Caching Strategy**: Multi-level caching for improved response times
- **Monitoring Integration**: Built-in metrics and health checks
- **Production Logging**: Structured logging with configurable levels

## Quick Start

### Requirements

- Python 3.8+
- Virtual environment recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/jweihe/AgentDoc.git
cd AgentDoc

# Create virtual environment
python -m venv agentdoc-env
source agentdoc-env/bin/activate  # Linux/Mac
# or agentdoc-env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from agentdoc import ModelManager, PDFProcessor
from agentdoc.qa import QAEngine, DocumentIndexer

# Initialize components
model_manager = ModelManager()
pdf_processor = PDFProcessor()
qa_engine = QAEngine()

# Process document
document = pdf_processor.process("document.pdf")

# Build index
indexer = DocumentIndexer()
chunks = indexer.index_document(document)

# Intelligent Q&A
result = qa_engine.answer_question(
    question="What is the main content of the document?",
    chunks=chunks
)

print(f"Answer: {result.answer}")
print(f"Citations: {result.citations}")
```

## 📁 Project Architecture

```
AgentDoc/
├── agentdoc/                    # 🏗️ Core Application Package
│   ├── core/                    # 🔧 Foundation Layer
│   │   ├── config.py            #   ⚙️ Configuration management
│   │   ├── logger.py            #   📝 Structured logging system
│   │   └── exceptions.py        #   🚨 Custom exception handling
│   ├── models/                  # 🤖 AI Model Integration
│   │   ├── manager.py           #   🎯 Unified model management
│   │   ├── factory.py           #   🏭 Dynamic model instantiation
│   │   └── base.py              #   📋 Model interface definitions
│   ├── processors/              # 📄 Document Processing Engine
│   │   ├── text_processor.py    #   📝 Text extraction & cleaning
│   │   ├── batch_processor.py   #   📦 Bulk document processing
│   │   └── factory.py           #   🔄 Processor selection logic
│   ├── qa/                      # 🧠 Intelligent Q&A System
│   │   ├── engine.py            #   🎯 Main Q&A orchestration
│   │   ├── indexer.py           #   🗂️ Document indexing & chunking
│   │   ├── retriever.py         #   🔍 Semantic & keyword search
│   │   ├── reasoning.py         #   🤔 Logic reasoning engine
│   │   └── citation.py          #   📚 Citation management
│   ├── plugins/                 # 🔌 Extensibility Framework
│   │   ├── manager.py           #   🎛️ Plugin lifecycle management
│   │   ├── base.py              #   📐 Plugin interface standards
│   │   ├── model_plugins.py     #   🤖 Model integration plugins
│   │   └── processor_plugins.py #   📄 Document processor plugins
│   ├── queue/                   # ⚡ Async Task Management
│   │   ├── manager.py           #   📋 Task orchestration
│   │   ├── worker.py            #   👷 Background task execution
│   │   └── base.py              #   🏗️ Queue abstractions
│   ├── agents/                  # 🤖 Intelligent Agent System
│   │   └── document_agent.py    #   📖 Document analysis agents
│   ├── prompts/                 # 💬 Prompt Engineering
│   │   ├── manager.py           #   🎭 Prompt template management
│   │   ├── qa_prompts.py        #   ❓ Q&A specific prompts
│   │   ├── code_prompts.py      #   💻 Code analysis prompts
│   │   └── advanced_prompts.py  #   🚀 Complex reasoning prompts
│   ├── web/                     # 🌐 Web Interface
│   │   └── templates/           #   🎨 HTML templates
│   ├── api/                     # 🔗 RESTful API Layer
│   │   ├── routes.py            #   🛣️ API endpoint definitions
│   │   └── models.py            #   📊 API data models
│   ├── cli/                     # 💻 Command Line Interface
│   │   └── main.py              #   ⌨️ CLI entry point
│   └── utils/                   # 🛠️ Utility Functions
│       ├── text_analyzer.py     #   📊 Text analysis utilities
│       └── document_enhancer.py #   ✨ Document enhancement tools
├── tests/                       # 🧪 Comprehensive Test Suite
│   ├── unit/                    #   🔬 Unit tests
│   ├── integration/             #   🔗 Integration tests
│   └── e2e/                     #   🎯 End-to-end tests
├── docs/                        # 📚 Documentation
│   ├── api/                     #   🔗 API documentation
│   ├── guides/                  #   📖 User guides
│   └── examples/                #   💡 Usage examples
├── docker/                      # 🐳 Containerization
│   ├── Dockerfile               #   📦 Production container
│   └── docker-compose.yml       #   🎼 Multi-service orchestration
├── scripts/                     # 🔧 Development & Deployment
│   ├── setup.sh                 #   🚀 Environment setup
│   └── deploy.sh                #   📤 Deployment automation
├── requirements.txt             # 📋 Python dependencies
├── pyproject.toml               # ⚙️ Project configuration
├── .env.example                 # 🔐 Environment variables template
└── README.md                    # 📖 Project documentation
```

## Core Module Description

### 🧠 QA Module (agentdoc.qa)
Core engine of the intelligent Q&A system, built on RAG (Retrieval-Augmented Generation) architecture

- **QAEngine**: Intelligent Q&A Engine
  - Multi-turn dialogue and context understanding
  - Integrated vector retrieval and semantic matching
  - Complex query decomposition and rewriting
  - Confidence scoring and answer quality assessment

- **DocumentIndexer**: High-Performance Document Indexer
  - Semantic indexing based on vector databases
  - Incremental indexing and real-time updates
  - Multi-level indexing strategy: chapter, paragraph, sentence levels
  - Intelligent document chunking and overlap processing

- **DocumentRetriever**: Precision Document Retriever
  - Hybrid retrieval strategy: Vector retrieval + BM25 + Re-ranking
  - Multi-modal retrieval support (text, images, tables)
  - Dynamic retrieval strategy adjustment
  - Result deduplication and aggregation

- **CitationManager**: Intelligent Citation Manager
  - Automatic generation of precise page and paragraph citations
  - Multiple citation format support (APA, MLA, Chicago, etc.)
  - Citation chain tracking and verification
  - Batch citation export functionality

- **SimpleReasoner**: Logic Reasoning Engine
  - Causal reasoning and logic chain construction
  - Multi-step reasoning with intermediate result caching
  - Reasoning path visualization and explanation
  - Hypothesis verification and counter-argument support

### 🤖 Models Module (agentdoc.models)
Enterprise-grade model management and scheduling system

- **ModelManager**: Unified Model Manager
  - Support for multiple LLMs: OpenAI, Claude, Qwen, GLM, etc.
  - Model load balancing and failover
  - Real-time performance monitoring and cost tracking
  - Model version management and A/B testing

- **ModelFactory**: Intelligent Model Factory
  - Dynamic model instantiation and configuration
  - Automatic model capability detection and matching
  - Model composition and cascaded calling support
  - Model caching and warm-up mechanisms

- **BaseModel**: Unified Model Interface
  - Standardized API interface design
  - Streaming output and batch processing support
  - Built-in retry mechanisms and error handling
  - Model call chain tracing

### 🔌 Plugins Module (agentdoc.plugins)
Extensible plugin ecosystem

- **PluginManager**: Plugin Lifecycle Manager
  - Hot-swappable plugin loading and unloading
  - Plugin dependency management and version control
  - Plugin security sandbox and permission control
  - Plugin performance monitoring and resource limiting

- **BasePlugin**: Plugin Development Framework
  - Standardized plugin interface and lifecycle
  - Plugin configuration management and parameter validation
  - Inter-plugin communication and event mechanisms
  - Plugin error handling and logging

- **ProcessorPlugin**: Document Processing Plugin
  - Custom document format parsing support
  - Document preprocessing and postprocessing pipelines
  - Multi-language document processing support
  - Document quality assessment and optimization

### ⚡ Queue Module (agentdoc.queue)
High-performance asynchronous task processing system

- **TaskQueue**: Distributed Task Queue
  - Support for Redis, RabbitMQ and other message queues
  - Task prioritization and delayed execution
  - Task deduplication and idempotency guarantee
  - Dead letter queue and task retry mechanisms

- **TaskManager**: Task Scheduling Manager
  - Full lifecycle task tracking
  - Dynamic worker process scaling
  - Task execution statistics and performance analysis
  - Task dependency management and batch operations

- **Worker**: Efficient Task Executor
  - Multi-process/multi-thread concurrent execution
  - Task execution environment isolation
  - Resource usage monitoring and limiting
  - Task execution logging and error tracking

### 📄 Processors Module (agentdoc.processors)
Multi-format document processing engine

- **PDFProcessor**: Professional PDF Document Processor
  - High-precision text extraction and layout analysis
  - Table, image, and formula recognition
  - OCR integration and text recognition
  - Document structuring and metadata extraction

- **BatchProcessor**: Batch Processing Scheduler
  - Large-scale document parallel processing
  - Real-time processing progress monitoring
  - Error recovery and checkpoint resume
  - Processing result statistics and reporting

### 🎯 Agents Module (agentdoc.agents)
Intelligent agents and automation system

- **DocumentAgent**: Document Intelligence Agent
  - Automatic document analysis and summary generation
  - Document quality assessment and improvement suggestions
  - Multi-document correlation analysis and comparison
  - Document knowledge graph construction

### 🌐 Web Module (agentdoc.web)
Modern web interface

- **WebUI**: Responsive User Interface
  - Drag-and-drop document upload and management
  - Real-time Q&A and result display
  - Visual analysis and chart presentation
  - Multi-user collaboration and permission management

### 🔧 Utils Module (agentdoc.utils)
Common utilities and auxiliary functions

- **ConfigManager**: Configuration Manager
- **Logger**: Structured Logging System
- **FileHandler**: File Operation Tools
- **TextProcessor**: Text Processing Tools

## Advanced Usage

### Custom Plugin Development

```python
from agentdoc.plugins import BasePlugin, PluginManager

class CustomProcessor(BasePlugin):
    def process(self, document):
        # Custom processing logic
        return processed_document

# Register plugin
plugin_manager = PluginManager()
plugin_manager.register_plugin("custom", CustomProcessor())
```

### Batch Document Processing

```python
from agentdoc.processors import BatchProcessor
from agentdoc.queue import TaskQueue

# Batch processing
batch_processor = BatchProcessor()
task_queue = TaskQueue()

# Add tasks
for pdf_file in pdf_files:
    task_queue.add_task("process_pdf", {"file_path": pdf_file})

# Execute batch processing
results = batch_processor.process_batch(task_queue)
```

### Configuration Management

```python
from agentdoc.core import Settings

# Custom configuration
settings = Settings(
    model_name="qwen2.5",
    max_chunk_size=1000,
    overlap_size=100,
    citation_enabled=True
)
```

## Development Guide

### Environment Setup

```bash
# Install development dependencies
pip install pytest black flake8

# Code formatting
black agentdoc/

# Code linting
flake8 agentdoc/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific module tests
python test_qa_module.py
python test_plugins.py
```

### Contributing Guidelines

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contact

- Project Homepage: [GitHub Repository](https://github.com/jweihe/AgentDoc)
- Issue Reporting: [Issues](https://github.com/jweihe/AgentDoc/issues)
- Email: team@agentdoc.ai

---

[中文版本](README.md) | English Version