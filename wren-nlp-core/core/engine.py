"""
SQL执行引擎抽象层
基于WrenAI核心逻辑，提供SQL执行和处理工具
"""
import logging
import re
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel

logger = logging.getLogger("wren-nlp-core")


class EngineConfig(BaseModel):
    """引擎配置"""
    provider: str = "local"
    config: dict = {}


class Engine(metaclass=ABCMeta):
    """SQL执行引擎抽象基类"""
    
    @abstractmethod
    async def execute_sql(
        self,
        sql: str,
        dry_run: bool = True,
        **kwargs,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """执行SQL查询"""
        pass


def clean_generation_result(result: str) -> str:
    """清理生成的SQL结果，移除多余的格式字符"""
    def _normalize_whitespace(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    return (
        _normalize_whitespace(result)
        .replace("\\n", " ")
        .replace("```sql", "")
        .replace("```json", "")
        .replace('"""', "")
        .replace("'''", "")
        .replace("```", "")
        .replace(";", "")
    )


def remove_limit_statement(sql: str) -> str:
    """移除SQL中的LIMIT语句"""
    pattern = r"\s*LIMIT\s+\d+(\s*;?\s*--.*|\s*;?\s*)$"
    modified_sql = re.sub(pattern, "", sql, flags=re.IGNORECASE)
    return modified_sql


def add_quotes(sql: str) -> Tuple[str, str]:
    """为SQL标识符添加引号（简化版，可根据需要扩展）"""
    try:
        # 这里简化处理，实际使用时可能需要更复杂的SQL解析
        return sql, ""
    except Exception as e:
        logger.exception(f"Error processing SQL {sql}: {e}")
        return "", str(e)