"""
配置管理
基于WrenAI核心逻辑的最小化配置系统
"""
import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM配置"""
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 1000
    context_window_size: int = 4096


@dataclass
class CoreConfig:
    """核心引擎配置"""
    enable_intent_classification: bool = True
    enable_sql_generation_reasoning: bool = False
    max_histories: int = 5
    log_level: str = "INFO"


@dataclass
class Config:
    """总配置"""
    llm: LLMConfig
    core: CoreConfig
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """从字典创建配置"""
        llm_config = LLMConfig(**config_dict.get('llm', {}))
        core_config = CoreConfig(**config_dict.get('core', {}))
        return cls(llm=llm_config, core=core_config)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """从YAML文件加载配置"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量创建配置"""
        llm_config = LLMConfig(
            model=os.getenv('WREN_LLM_MODEL', 'gpt-3.5-turbo'),
            api_key=os.getenv('WREN_LLM_API_KEY'),
            base_url=os.getenv('WREN_LLM_BASE_URL'),
            temperature=float(os.getenv('WREN_LLM_TEMPERATURE', '0.1')),
            max_tokens=int(os.getenv('WREN_LLM_MAX_TOKENS', '1000')),
            context_window_size=int(os.getenv('WREN_LLM_CONTEXT_WINDOW', '4096')),
        )
        
        core_config = CoreConfig(
            enable_intent_classification=os.getenv('WREN_ENABLE_INTENT_CLASSIFICATION', 'true').lower() == 'true',
            enable_sql_generation_reasoning=os.getenv('WREN_ENABLE_SQL_REASONING', 'false').lower() == 'true',
            max_histories=int(os.getenv('WREN_MAX_HISTORIES', '5')),
            log_level=os.getenv('WREN_LOG_LEVEL', 'INFO'),
        )
        
        return cls(llm=llm_config, core=core_config)


def get_default_config() -> Config:
    """获取默认配置"""
    return Config(
        llm=LLMConfig(),
        core=CoreConfig(),
    )