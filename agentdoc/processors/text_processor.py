"""文本文档处理器"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import re

from .base import BaseProcessor
from ..core.exceptions import ProcessingError, ValidationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class TextProcessor(BaseProcessor):
    """文本文档处理器
    
    负责处理纯文本文档，包括txt和markdown文件。
    支持文本分块、元数据提取和结构化处理。
    """
    
    def __init__(self, name: str = None):
        super().__init__(name)
        
        # 文本处理配置
        self.chunk_size = getattr(self.settings.agent, 'chunk_size', 1000)
        self.chunk_overlap = getattr(self.settings.agent, 'chunk_overlap', 100)
        self.max_text_length = getattr(self.settings.agent, 'max_text_length', 10000)
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return [".txt", ".md", ".markdown"]
    
    def validate_input(self, input_path: Union[str, Path]) -> bool:
        """验证文本文件
        
        Args:
            input_path: 文本文件路径
            
        Returns:
            验证是否通过
            
        Raises:
            ValidationError: 验证失败时抛出
        """
        text_path = Path(input_path)
        
        # 检查文件是否存在
        if not text_path.exists():
            raise ValidationError(f"文本文件不存在: {text_path}")
        
        # 检查文件扩展名
        if text_path.suffix.lower() not in self.get_supported_formats():
            raise ValidationError(f"不支持的文件格式: {text_path.suffix}")
        
        # 检查文件大小
        file_size = text_path.stat().st_size
        max_size = getattr(self.settings.processing, 'max_file_size', 50 * 1024 * 1024)
        if file_size > max_size:
            raise ValidationError(f"文件过大: {file_size} bytes > {max_size} bytes")
        
        # 尝试读取文件以验证编码
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # 读取前1024字符进行验证
        except UnicodeDecodeError:
            try:
                with open(text_path, 'r', encoding='gbk') as f:
                    f.read(1024)
            except UnicodeDecodeError:
                raise ValidationError(f"无法解码文件: {text_path}")
        
        return True
    
    async def process(self, input_path: Union[str, Path], output_dir: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """处理文本文档
        
        Args:
            input_path: 输入文件路径
            output_dir: 输出目录路径
            **kwargs: 其他参数
            
        Returns:
            处理结果字典
            
        Raises:
            ProcessingError: 处理失败时抛出
        """
        try:
            # 验证输入
            self.validate_input(input_path)
            
            input_path = Path(input_path)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"开始处理文本文件: {input_path}")
            
            # 读取文本内容
            text_content = self._read_text_file(input_path)
            
            # 提取元数据
            metadata = self._extract_metadata(input_path, text_content)
            
            # 文本分块
            chunks = self._chunk_text(text_content)
            
            # 结构化处理（针对markdown）
            structure = self._extract_structure(text_content, input_path.suffix)
            
            # 生成输出文件
            result = {
                "file_path": str(input_path),
                "file_name": input_path.name,
                "file_type": input_path.suffix,
                "metadata": metadata,
                "content": text_content,
                "chunks": chunks,
                "structure": structure,
                "processing_time": metadata.get("processing_time", 0)
            }
            
            # 保存结果
            output_file = output_dir / f"{input_path.stem}_processed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"文本处理完成: {output_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"处理文本文件失败: {e}")
            raise ProcessingError(f"处理文本文件失败: {e}")
    
    def _read_text_file(self, file_path: Path) -> str:
        """读取文本文件内容"""
        try:
            # 首先尝试UTF-8编码
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试GBK编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果都失败，尝试latin-1编码
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
        
        # 限制文本长度
        if len(content) > self.max_text_length:
            logger.warning(f"文本长度超过限制，截取前{self.max_text_length}字符")
            content = content[:self.max_text_length]
        
        return content
    
    def _extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """提取文件元数据"""
        import time
        from datetime import datetime
        
        stat = file_path.stat()
        
        metadata = {
            "file_size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "character_count": len(content),
            "line_count": len(content.splitlines()),
            "word_count": len(content.split()),
            "processing_time": time.time()
        }
        
        # 针对markdown文件提取额外信息
        if file_path.suffix.lower() in [".md", ".markdown"]:
            metadata.update(self._extract_markdown_metadata(content))
        
        return metadata
    
    def _extract_markdown_metadata(self, content: str) -> Dict[str, Any]:
        """提取markdown特有的元数据"""
        metadata = {}
        
        # 统计标题数量
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        metadata["header_count"] = len(headers)
        metadata["headers"] = headers[:10]  # 只保留前10个标题
        
        # 统计链接数量
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        metadata["link_count"] = len(links)
        
        # 统计图片数量
        images = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
        metadata["image_count"] = len(images)
        
        # 统计代码块数量
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        metadata["code_block_count"] = len(code_blocks)
        
        return metadata
    
    def _chunk_text(self, content: str) -> List[Dict[str, Any]]:
        """将文本分块"""
        chunks = []
        
        # 按段落分割
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 如果当前块加上新段落超过限制，保存当前块
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append({
                    "chunk_id": chunk_id,
                    "content": current_chunk.strip(),
                    "character_count": len(current_chunk),
                    "word_count": len(current_chunk.split())
                })
                
                # 开始新块，保留重叠部分
                if self.chunk_overlap > 0:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                
                chunk_id += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # 添加最后一个块
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "content": current_chunk.strip(),
                "character_count": len(current_chunk),
                "word_count": len(current_chunk.split())
            })
        
        return chunks
    
    def _extract_structure(self, content: str, file_type: str) -> Dict[str, Any]:
        """提取文档结构"""
        structure = {
            "type": "text",
            "sections": []
        }
        
        if file_type.lower() in [".md", ".markdown"]:
            structure["type"] = "markdown"
            structure["sections"] = self._extract_markdown_structure(content)
        else:
            structure["sections"] = self._extract_text_structure(content)
        
        return structure
    
    def _extract_markdown_structure(self, content: str) -> List[Dict[str, Any]]:
        """提取markdown文档结构"""
        sections = []
        lines = content.splitlines()
        
        current_section = None
        
        for i, line in enumerate(lines):
            # 检查是否是标题
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                # 保存前一个section
                if current_section:
                    sections.append(current_section)
                
                # 创建新section
                level = len(header_match.group(1))
                title = header_match.group(2)
                
                current_section = {
                    "level": level,
                    "title": title,
                    "line_start": i + 1,
                    "content": ""
                }
            elif current_section:
                current_section["content"] += line + "\n"
        
        # 添加最后一个section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_text_structure(self, content: str) -> List[Dict[str, Any]]:
        """提取纯文本文档结构"""
        sections = []
        paragraphs = content.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                sections.append({
                    "paragraph_id": i,
                    "content": paragraph.strip(),
                    "character_count": len(paragraph),
                    "word_count": len(paragraph.split())
                })
        
        return sections