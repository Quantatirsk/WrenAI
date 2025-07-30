"""
SQL生成管道
基于WrenAI核心逻辑，实现自然语言到SQL的转换
"""
import logging
from typing import Any, Dict, List, Optional

from core.pipeline import BasicPipeline
from core.provider import LLMProvider
from core.engine import clean_generation_result

logger = logging.getLogger("wren-nlp-core")


class SQLGenerationPipeline(BasicPipeline):
    """SQL生成管道"""
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        system_prompt: str = None,
        **kwargs,
    ):
        self.llm_provider = llm_provider
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # 初始化组件
        self._components = {
            "generator": llm_provider.get_generator(
                system_prompt=self.system_prompt,
                generation_kwargs={"temperature": 0.1, "max_tokens": 1000},
            ),
        }
        
        super().__init__(self._components)
    
    def _get_default_system_prompt(self) -> str:
        """获取默认的系统提示词"""
        return """你是一个专业的SQL查询生成专家。根据用户的自然语言描述和提供的数据库模式，生成准确的SQL查询语句。

要求：
1. 仔细分析用户的查询意图
2. 基于提供的数据库模式生成SQL
3. 确保SQL语法正确
4. 只返回SQL语句，不要包含其他解释
5. 如果需求不明确，生成最合理的查询

请根据以下信息生成SQL："""

    def _build_prompt(
        self,
        query: str,
        db_schemas: List[str],
        sql_samples: List[Dict] = None,
        instructions: List[str] = None,
        sql_generation_reasoning: str = None,
    ) -> str:
        """构建完整的提示词"""
        
        prompt_parts = []
        
        # 数据库模式
        if db_schemas:
            prompt_parts.append("### 数据库模式 ###")
            for schema in db_schemas:
                prompt_parts.append(schema)
            prompt_parts.append("")
        
        # SQL示例
        if sql_samples:
            prompt_parts.append("### SQL示例 ###")
            for sample in sql_samples:
                prompt_parts.append(f"问题: {sample.get('question', '')}")
                prompt_parts.append(f"SQL: {sample.get('sql', '')}")
                prompt_parts.append("")
        
        # 用户指令
        if instructions:
            prompt_parts.append("### 用户指令 ###")
            for i, instruction in enumerate(instructions, 1):
                prompt_parts.append(f"{i}. {instruction}")
            prompt_parts.append("")
        
        # 用户问题
        prompt_parts.append("### 用户问题 ###")
        prompt_parts.append(f"用户问题: {query}")
        prompt_parts.append("")
        
        # 推理计划
        if sql_generation_reasoning:
            prompt_parts.append("### 推理计划 ###")
            prompt_parts.append(sql_generation_reasoning)
            prompt_parts.append("")
        
        prompt_parts.append("请逐步思考并生成SQL查询：")
        
        return "\n".join(prompt_parts)
    
    async def run(
        self,
        query: str,
        db_schemas: List[str] = None,
        sql_samples: List[Dict] = None,
        instructions: List[str] = None,
        sql_generation_reasoning: str = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """运行SQL生成管道"""
        
        logger.info("开始SQL生成...")
        
        try:
            # 构建提示词
            prompt = self._build_prompt(
                query=query,
                db_schemas=db_schemas or [],
                sql_samples=sql_samples,
                instructions=instructions,
                sql_generation_reasoning=sql_generation_reasoning,
            )
            
            # 调用LLM生成SQL
            generator = self._components["generator"]
            result = await generator(prompt=prompt)
            
            # 处理生成结果
            if result and result.get("replies"):
                raw_sql = result["replies"][0]
                cleaned_sql = clean_generation_result(raw_sql)
                
                return {
                    "status": "success",
                    "sql": cleaned_sql,
                    "raw_sql": raw_sql,
                    "meta": result.get("meta", {}),
                }
            else:
                return {
                    "status": "failed",
                    "error": "未能生成SQL查询",
                    "sql": "",
                }
                
        except Exception as e:
            logger.error(f"SQL生成失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "sql": "",
            }