"""
LLM服务提供者实现
基于WrenAI核心逻辑，使用LiteLLM统一接口支持多种LLM提供商
"""
import logging
from typing import Any, Dict, Optional

from core.provider import LLMProvider

logger = logging.getLogger("wren-nlp-core")


class SimpleLLMProvider(LLMProvider):
    """简化的LLM提供者实现"""
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: str = None,
        base_url: str = None,
        model_kwargs: Dict[str, Any] = None,
        context_window_size: int = 4096,
    ):
        self._model = model
        self._api_key = api_key
        self._base_url = base_url
        self._model_kwargs = model_kwargs or {}
        self._context_window_size = context_window_size
        
    def get_generator(self, system_prompt: str = "", generation_kwargs: Dict[str, Any] = None):
        """获取LLM生成器"""
        return SimpleLLMGenerator(
            model=self._model,
            api_key=self._api_key,
            base_url=self._base_url,
            system_prompt=system_prompt,
            generation_kwargs=generation_kwargs or {},
            model_kwargs=self._model_kwargs,
        )


class SimpleLLMGenerator:
    """简化的LLM生成器"""
    
    def __init__(
        self,
        model: str,
        api_key: str = None,
        base_url: str = None,
        system_prompt: str = "",
        generation_kwargs: Dict[str, Any] = None,
        model_kwargs: Dict[str, Any] = None,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.system_prompt = system_prompt
        self.generation_kwargs = generation_kwargs or {}
        self.model_kwargs = model_kwargs or {}
    
    async def __call__(self, prompt: str) -> Dict[str, Any]:
        """调用LLM生成响应"""
        try:
            # 这里是简化的实现，实际使用时需要集成litellm或其他LLM库
            # 示例：使用OpenAI API
            import openai
            
            if self.api_key:
                openai.api_key = self.api_key
            if self.base_url:
                openai.base_url = self.base_url
                
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await openai.chat.completions.create(
                model=self.model,
                messages=messages,
                **self.generation_kwargs,
                **self.model_kwargs,
            )
            
            return {
                "replies": [response.choices[0].message.content],
                "meta": {
                    "model": self.model,
                    "usage": dict(response.usage) if hasattr(response, 'usage') else {}
                }
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return {
                "replies": ["抱歉，SQL生成失败，请检查配置或重试。"],
                "meta": {"error": str(e)}
            }