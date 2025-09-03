# AgentDoc 快速开始指南

## 简介

AgentDoc 是一个轻量级的多Agent文档处理框架，专为简单部署和快速使用而设计。

## 特点

- 🚀 **开箱即用**: 一行命令安装，无需复杂配置
- 🤖 **多Agent架构**: 智能任务分解和协作处理
- 📄 **多格式支持**: PDF、Word、Markdown、TXT等
- 🌐 **Web界面**: 简洁友好的用户界面
- 💻 **CLI工具**: 命令行批处理支持
- 🔧 **易于扩展**: 模块化设计，轻松添加新功能

## 安装

### 方式1: pip安装（推荐）

```bash
pip install agentdoc
```

### 方式2: 源码安装

```bash
git clone https://github.com/your-org/AgentDoc.git
cd AgentDoc
pip install -e .
```

## 快速使用

### 1. 启动API服务

```bash
# 启动API服务（默认端口5000）
agentdoc serve

# 指定端口
agentdoc serve --port 8000
```

### 2. 启动Web界面

```bash
# 启动Web界面（默认端口8080）
agentdoc web

# 指定端口
agentdoc web --port 9000
```

### 3. 命令行分析文档

```bash
# 分析单个文档
agentdoc analyze document.pdf

# 批量分析
agentdoc analyze *.pdf
```

## 使用示例

### Python API使用

```python
from agentdoc import AgentDoc

# 初始化AgentDoc
agent_doc = AgentDoc()

# 分析文档
result = agent_doc.analyze_document("example.pdf")

print(f"文档标题: {result['title']}")
print(f"页数: {result['pages']}")
print(f"摘要: {result['summary']}")
```

### REST API使用

```bash
# 分析文档
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_path": "document.pdf"}'

# 查看Agent状态
curl http://localhost:5000/api/v1/agents

# 健康检查
curl http://localhost:5000/api/v1/health
```

### Web界面使用

1. 打开浏览器访问 `http://localhost:8080`
2. 上传文档文件
3. 查看分析结果
4. 下载处理后的数据

## 配置

### 环境变量配置

创建 `.env` 文件：

```env
# 基础配置
AGENTDOC_DATA_DIR=./agentdoc_data
AGENTDOC_LOG_LEVEL=INFO

# API配置
API_HOST=0.0.0.0
API_PORT=5000

# Web配置
WEB_HOST=0.0.0.0
WEB_PORT=8080

# 模型配置
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_FILE_SIZE=50MB
```

### 配置文件

创建 `agentdoc.yaml`：

```yaml
# Agent配置
agents:
  document_agent:
    enabled: true
    max_file_size: "50MB"
    supported_formats: ["pdf", "docx", "txt", "md"]
  
  reasoning_agent:
    enabled: true
    max_context_length: 4096
  
  qa_agent:
    enabled: true
    response_format: "markdown"

# 存储配置
storage:
  data_dir: "./agentdoc_data"
  vector_store:
    model: "all-MiniLM-L6-v2"
    dimension: 384

# 日志配置
logging:
  level: "INFO"
  file: "agentdoc.log"
```

## 支持的文档格式

| 格式 | 扩展名 | 支持功能 |
|------|--------|----------|
| PDF | .pdf | 文本提取、结构分析 |
| Word | .docx | 文本提取、格式保留 |
| Markdown | .md | 文本解析、标题提取 |
| 纯文本 | .txt | 文本处理、编码检测 |

## 常用功能

### 文档分析

```python
# 基础分析
result = agent_doc.analyze_document("document.pdf")

# 详细分析
result = agent_doc.analyze_document(
    "document.pdf",
    options={
        "extract_images": True,
        "analyze_structure": True,
        "generate_summary": True
    }
)
```

### 问答系统

```python
# 基于文档的问答
response = agent_doc.ask_question(
    question="这个文档的主要内容是什么？",
    document="document.pdf"
)

print(response['answer'])
print(response['confidence'])
print(response['sources'])
```

### 知识提取

```python
# 提取关键信息
knowledge = agent_doc.extract_knowledge("document.pdf")

print("实体:", knowledge['entities'])
print("关系:", knowledge['relations'])
print("关键词:", knowledge['keywords'])
```

## 故障排除

### 常见问题

**Q: 安装时出现依赖错误**
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存重新安装
pip cache purge
pip install agentdoc
```

**Q: 文档解析失败**
```bash
# 检查文件格式
file document.pdf

# 检查文件权限
ls -la document.pdf

# 查看详细错误日志
agentdoc analyze document.pdf --verbose
```

**Q: 服务启动失败**
```bash
# 检查端口占用
netstat -tulpn | grep :5000

# 使用其他端口
agentdoc serve --port 5001
```

### 日志查看

```bash
# 查看实时日志
tail -f agentdoc.log

# 查看错误日志
grep ERROR agentdoc.log

# 调试模式运行
AGENTDOC_LOG_LEVEL=DEBUG agentdoc serve
```

## 性能优化

### 内存优化

```python
# 配置内存限制
agent_doc = AgentDoc(
    config={
        "max_memory_usage": "2GB",
        "cache_size": 1000,
        "batch_size": 10
    }
)
```

### 并发处理

```python
# 批量处理文档
files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = agent_doc.batch_analyze(files, max_workers=4)
```

## 扩展开发

### 自定义Agent

```python
from agentdoc.agents.base import BaseAgent, Task, TaskResult

class CustomAgent(BaseAgent):
    def get_capabilities(self):
        return ["custom_processing"]
    
    async def process(self, task: Task) -> TaskResult:
        # 自定义处理逻辑
        result = self.custom_logic(task.data)
        return TaskResult(
            task_id=task.task_id,
            result=result,
            status="completed"
        )

# 注册自定义Agent
agent_doc.register_agent(CustomAgent())
```

### 自定义处理器

```python
from agentdoc.processors.base import BaseProcessor

class CustomProcessor(BaseProcessor):
    def supports(self, file_path: str) -> bool:
        return file_path.endswith('.custom')
    
    async def process(self, file_path: str) -> dict:
        # 自定义文件处理逻辑
        return {"content": "processed content"}

# 注册自定义处理器
agent_doc.register_processor(CustomProcessor())
```

## 更多资源

- 📖 [完整文档](docs/README.md)
- 🔧 [API参考](docs/api_reference.md)
- 💡 [使用示例](examples/)
- 🐛 [问题反馈](https://github.com/your-org/AgentDoc/issues)
- 💬 [社区讨论](https://github.com/your-org/AgentDoc/discussions)

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**开始使用AgentDoc，让文档处理变得简单高效！** 🚀