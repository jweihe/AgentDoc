"""文档索引器

负责文档的分块、向量化和索引构建。
"""

import hashlib
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from ..core.config import Settings
from ..core.exceptions import DocumentError, IndexError
from .models import DocumentChunk


class DocumentIndexer:
    """文档索引器
    
    负责将文档内容分块、向量化并建立索引。
    """
    
    def __init__(self, config: Settings):
        """初始化索引器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 分块配置
        self.chunk_size = getattr(config.agent, 'chunk_size', 512)
        self.chunk_overlap = getattr(config.agent, 'chunk_overlap', 100)
        self.min_chunk_size = getattr(config.agent, 'min_chunk_size', 100)
        
        # 向量化模型
        self.embedding_model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.embedding_model = None
        self.embedding_dim = None
        
        # 索引存储
        self.chunks: Dict[str, DocumentChunk] = {}
        self.document_chunks: Dict[str, List[str]] = {}  # document_id -> chunk_ids
        self.embeddings: Dict[str, np.ndarray] = {}
        
    def _load_embedding_model(self) -> None:
        """加载向量化模型"""
        if self.embedding_model is None:
            try:
                self.logger.info(f"Loading embedding model: {self.embedding_model_name}")
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                # 获取向量维度
                test_embedding = self.embedding_model.encode(["test"])
                self.embedding_dim = test_embedding.shape[1]
                self.logger.info(f"Embedding model loaded, dimension: {self.embedding_dim}")
            except Exception as e:
                raise IndexError(f"Failed to load embedding model: {e}")
    
    def chunk_text(self, text: str, document_id: str, page_number: Optional[int] = None) -> List[DocumentChunk]:
        """将文本分块
        
        Args:
            text: 文本内容
            document_id: 文档ID
            page_number: 页码
            
        Returns:
            文档块列表
        """
        if not text or len(text.strip()) < self.min_chunk_size:
            return []
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # 计算块的结束位置
            end = min(start + self.chunk_size, len(text))
            
            # 如果不是最后一块，尝试在句子边界分割
            if end < len(text):
                # 寻找最近的句号、问号或感叹号
                for i in range(end, max(start + self.min_chunk_size, end - 100), -1):
                    if text[i] in '.!?。！？':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) >= self.min_chunk_size:
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=chunk_text,
                    page_number=page_number,
                    start_position=start,
                    end_position=end,
                    metadata={
                        'chunk_index': chunk_index,
                        'text_length': len(chunk_text)
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # 移动到下一个块的开始位置（考虑重叠）
            start = max(start + 1, end - self.chunk_overlap)
        
        return chunks
    
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """为文档块生成向量嵌入
        
        Args:
            chunks: 文档块列表
            
        Returns:
            包含嵌入向量的文档块列表
        """
        if not chunks:
            return chunks
        
        self._load_embedding_model()
        
        try:
            # 提取文本内容
            texts = [chunk.content for chunk in chunks]
            
            # 生成嵌入向量
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            
            # 将嵌入向量添加到块中
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding.tolist()
                
            return chunks
            
        except Exception as e:
            raise IndexError(f"Failed to generate embeddings: {e}")
    
    def index_document(self, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """索引文档
        
        Args:
            document_id: 文档ID
            content: 文档内容
            metadata: 文档元数据
            
        Returns:
            生成的块ID列表
        """
        try:
            self.logger.info(f"Indexing document: {document_id}")
            
            # 如果文档已存在，先删除
            if document_id in self.document_chunks:
                self.remove_document(document_id)
            
            # 分块
            chunks = self.chunk_text(content, document_id)
            if not chunks:
                self.logger.warning(f"No chunks generated for document: {document_id}")
                return []
            
            # 生成嵌入向量
            chunks = self.embed_chunks(chunks)
            
            # 存储块和嵌入
            chunk_ids = []
            for chunk in chunks:
                # 添加文档元数据到块
                if metadata:
                    chunk.metadata.update(metadata)
                
                self.chunks[chunk.chunk_id] = chunk
                self.embeddings[chunk.chunk_id] = np.array(chunk.embedding)
                chunk_ids.append(chunk.chunk_id)
            
            # 记录文档的块ID
            self.document_chunks[document_id] = chunk_ids
            
            self.logger.info(f"Document indexed: {document_id}, {len(chunk_ids)} chunks")
            return chunk_ids
            
        except Exception as e:
            raise IndexError(f"Failed to index document {document_id}: {e}")
    
    def index_document_with_pages(self, document_id: str, pages_content: List[Tuple[int, str]], 
                                 metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """索引带页码的文档
        
        Args:
            document_id: 文档ID
            pages_content: 页码和内容的元组列表 [(page_num, content), ...]
            metadata: 文档元数据
            
        Returns:
            生成的块ID列表
        """
        try:
            self.logger.info(f"Indexing document with pages: {document_id}")
            
            # 如果文档已存在，先删除
            if document_id in self.document_chunks:
                self.remove_document(document_id)
            
            all_chunks = []
            
            # 按页处理
            for page_num, content in pages_content:
                if content.strip():
                    page_chunks = self.chunk_text(content, document_id, page_num)
                    all_chunks.extend(page_chunks)
            
            if not all_chunks:
                self.logger.warning(f"No chunks generated for document: {document_id}")
                return []
            
            # 生成嵌入向量
            all_chunks = self.embed_chunks(all_chunks)
            
            # 存储块和嵌入
            chunk_ids = []
            for chunk in all_chunks:
                # 添加文档元数据到块
                if metadata:
                    chunk.metadata.update(metadata)
                
                self.chunks[chunk.chunk_id] = chunk
                self.embeddings[chunk.chunk_id] = np.array(chunk.embedding)
                chunk_ids.append(chunk.chunk_id)
            
            # 记录文档的块ID
            self.document_chunks[document_id] = chunk_ids
            
            self.logger.info(f"Document with pages indexed: {document_id}, {len(chunk_ids)} chunks")
            return chunk_ids
            
        except Exception as e:
            raise IndexError(f"Failed to index document with pages {document_id}: {e}")
    
    def remove_document(self, document_id: str) -> bool:
        """移除文档索引
        
        Args:
            document_id: 文档ID
            
        Returns:
            是否成功移除
        """
        if document_id not in self.document_chunks:
            return False
        
        try:
            # 删除所有相关的块和嵌入
            chunk_ids = self.document_chunks[document_id]
            for chunk_id in chunk_ids:
                self.chunks.pop(chunk_id, None)
                self.embeddings.pop(chunk_id, None)
            
            # 删除文档记录
            del self.document_chunks[document_id]
            
            self.logger.info(f"Document removed from index: {document_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove document {document_id}: {e}")
            return False
    
    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """获取文档的所有块
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档块列表
        """
        if document_id not in self.document_chunks:
            return []
        
        chunk_ids = self.document_chunks[document_id]
        return [self.chunks[chunk_id] for chunk_id in chunk_ids if chunk_id in self.chunks]
    
    def get_chunk(self, chunk_id: str) -> Optional[DocumentChunk]:
        """获取指定的块
        
        Args:
            chunk_id: 块ID
            
        Returns:
            文档块或None
        """
        return self.chunks.get(chunk_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_documents': len(self.document_chunks),
            'total_chunks': len(self.chunks),
            'total_embeddings': len(self.embeddings),
            'embedding_dimension': self.embedding_dim,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'embedding_model': self.embedding_model_name
        }
    
    def clear(self) -> None:
        """清空所有索引"""
        self.chunks.clear()
        self.document_chunks.clear()
        self.embeddings.clear()
        self.logger.info("Index cleared")