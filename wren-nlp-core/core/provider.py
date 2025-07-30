"""
服务提供者抽象层
基于WrenAI核心逻辑，定义LLM、嵌入模型、文档存储等提供者接口
"""
from abc import ABCMeta, abstractmethod
from typing import Any


class LLMProvider(metaclass=ABCMeta):
    """LLM服务提供者抽象基类"""
    
    @abstractmethod
    def get_generator(self, *args, **kwargs):
        """获取LLM生成器"""
        pass

    def get_model(self):
        """获取模型名称"""
        return getattr(self, '_model', 'unknown')

    def get_model_kwargs(self):
        """获取模型参数"""
        return getattr(self, '_model_kwargs', {})

    def get_context_window_size(self):
        """获取上下文窗口大小"""
        return getattr(self, '_context_window_size', 4096)


class EmbedderProvider(metaclass=ABCMeta):
    """嵌入模型提供者抽象基类"""
    
    @abstractmethod
    def get_text_embedder(self, *args, **kwargs):
        """获取文本嵌入器"""
        pass

    @abstractmethod
    def get_document_embedder(self, *args, **kwargs):
        """获取文档嵌入器"""
        pass

    def get_model(self):
        """获取嵌入模型名称"""
        return getattr(self, '_embedding_model', 'unknown')


class DocumentStoreProvider(metaclass=ABCMeta):
    """文档存储提供者抽象基类"""
    
    @abstractmethod
    def get_store(self, *args, **kwargs):
        """获取文档存储实例"""
        pass

    @abstractmethod
    def get_retriever(self, *args, **kwargs):
        """获取检索器实例"""
        pass