"""
核心管道基础类
基于WrenAI核心逻辑，简化的管道执行框架
"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict
from collections.abc import Mapping


class BasicPipeline(metaclass=ABCMeta):
    """基础管道抽象类"""
    
    def __init__(self, components: Dict[str, Any] = None, configs: Dict[str, Any] = None):
        self._components = components or {}
        self._configs = configs or {}

    @abstractmethod
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """运行管道的主要方法，子类需要实现"""
        pass


@dataclass
class PipelineComponent(Mapping):
    """管道组件容器，用于存储各种提供者和引擎"""
    
    llm_provider: Any = None
    embedder_provider: Any = None
    document_store_provider: Any = None
    engine: Any = None

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)