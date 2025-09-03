# AgentDoc - Intelligent Document Analysis System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Overview

AgentDoc is a lightweight, efficient intelligent document analysis system focused on document parsing, intelligent Q&A, and content retrieval. The system adopts a modular architecture design, supports multiple document format processing, and provides precise citation management and intelligent reasoning capabilities.

## Core Features

- 🤖 **Intelligent Q&A**: Precise question-answering based on document content with context understanding and reasoning
- 📍 **Precise Citations**: Automatic answer source annotation with accurate document location references
- 🚀 **Multi-Model Support**: Flexible model management system supporting various language models
- 📄 **Document Processing**: Intelligent parsing of multiple document formats including PDF, DOCX
- 🔧 **Modular Architecture**: Extensible plugin system and processor architecture
- 🔍 **Smart Retrieval**: Efficient document indexing and retrieval system
- 📊 **Task Queue**: Support for asynchronous task processing and batch operations
- ⚡ **Lightweight & Efficient**: Optimized performance and resource usage

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
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

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

## Project Structure

```
AgentDoc/
├── agentdoc/              # Main package
│   ├── core/              # Core modules (config, logging, exception handling)
│   ├── models/            # Model management (model factory, manager)
│   ├── processors/        # Document processors (PDF, batch processing)
│   ├── qa/                # Intelligent Q&A (engine, indexing, retrieval, reasoning)
│   ├── plugins/           # Plugin system (extensible processors)
│   ├── queue/             # Task queue (async task management)
│   ├── agents/            # Agent modules (intelligent agents)
│   ├── prompts/           # Prompt templates (predefined prompts)
│   ├── web/               # Web interface
│   ├── api/               # API services
│   └── cli/               # Command line tools
├── tests/                 # Test code
├── requirements.txt       # Project dependencies
├── pyproject.toml         # Project configuration
└── README.md              # Project documentation
```

## Core Module Description

### QA Module (agentdoc.qa)
- **QAEngine**: Intelligent Q&A engine supporting complex question processing
- **DocumentIndexer**: Document indexer for efficient document indexing
- **DocumentRetriever**: Document retriever for precise content retrieval
- **CitationManager**: Citation manager for automatic accurate citation generation
- **SimpleReasoner**: Reasoner supporting logical reasoning and analysis

### Models Module (agentdoc.models)
- **ModelManager**: Model manager for unified management of various language models
- **ModelFactory**: Model factory for dynamic model instance creation
- **BaseModel**: Base model class defining unified interface

### Plugins Module (agentdoc.plugins)
- **PluginManager**: Plugin manager supporting dynamic plugin loading
- **BasePlugin**: Base plugin class defining plugin interface
- **ProcessorPlugin**: Processor plugin extending document processing capabilities

### Queue Module (agentdoc.queue)
- **TaskQueue**: Task queue supporting asynchronous task processing
- **TaskManager**: Task manager for managing task lifecycle
- **Worker**: Worker process for executing specific tasks

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