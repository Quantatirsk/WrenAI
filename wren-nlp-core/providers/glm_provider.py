"""
GLM模型服务提供者实现
支持智谱AI的大语言模型服务
"""
import logging
import json
import aiohttp
from typing import Any, Dict, Optional, List

from core.provider import LLMProvider

logger = logging.getLogger("wren-nlp-core")


class GLMProvider(LLMProvider):
    """智谱GLM模型提供者"""
    
    def __init__(
        self,
        model: str = "glm-4",
        api_key: str = "3623aee5bd864513855af0fec9956c54.GMQ293gc9B7ck4aG",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        model_kwargs: Dict[str, Any] = None,
        context_window_size: int = 8192,
    ):
        self._model = model
        self._api_key = api_key
        self._base_url = base_url
        self._model_kwargs = model_kwargs or {}
        self._context_window_size = context_window_size
        
    def get_generator(self, system_prompt: str = "", generation_kwargs: Dict[str, Any] = None):
        """获取GLM生成器"""
        return GLMGenerator(
            model=self._model,
            api_key=self._api_key,
            base_url=self._base_url,
            system_prompt=system_prompt,
            generation_kwargs=generation_kwargs or {},
            model_kwargs=self._model_kwargs,
        )


class GLMGenerator:
    """GLM生成器实现"""
    
    def __init__(
        self,
        model: str,
        api_key: str = None,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
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
        """调用GLM模型生成响应"""
        try:
            # 构建请求消息
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # 构建API请求参数
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.generation_kwargs.get("temperature", 0.1),
                "top_p": self.generation_kwargs.get("top_p", 0.7),
                "max_tokens": self.generation_kwargs.get("max_tokens", 1000),
            }
            
            # 添加其他模型参数
            for key, value in self.model_kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送API请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    json=payload,
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
            # 处理响应
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                return {
                    "replies": [content],
                    "meta": {
                        "model": self.model,
                        "usage": response_data.get("usage", {})
                    }
                }
            else:
                error_msg = response_data.get("error", {}).get("message", "未知错误")
                logger.error(f"GLM API调用失败: {error_msg}")
                return {
                    "replies": ["抱歉，SQL生成失败。请检查API密钥或稍后再试。"],
                    "meta": {"error": error_msg}
                }
                
        except Exception as e:
            logger.error(f"GLM generation failed: {e}")
            return {
                "replies": ["抱歉，SQL生成失败，请检查配置或重试。"],
                "meta": {"error": str(e)}
            }