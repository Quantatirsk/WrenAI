"""
意图分类管道
基于WrenAI核心逻辑，判断用户查询的意图类型
"""
import json
import logging
from typing import Any, Dict, List, Literal, Optional

from core.pipeline import BasicPipeline
from core.provider import LLMProvider

logger = logging.getLogger("wren-nlp-core")


class IntentClassificationPipeline(BasicPipeline):
    """意图分类管道"""
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        **kwargs,
    ):
        self.llm_provider = llm_provider
        self.system_prompt = self._get_system_prompt()
        
        # 初始化组件
        self._components = {
            "generator": llm_provider.get_generator(
                system_prompt=self.system_prompt,
                generation_kwargs={
                    "temperature": 0.1,
                    "max_tokens": 500,
                },
            ),
        }
        
        super().__init__(self._components)
    
    def _get_system_prompt(self) -> str:
        """获取意图分类的系统提示词"""
        return """你是一个专业的查询意图分类专家。根据用户的问题和数据库模式，将用户意图分类为以下类别之一：

1. **TEXT_TO_SQL** - 用户想要生成SQL查询
   - 问题涉及具体的数据查询、筛选、统计等
   - 可以基于提供的数据库模式生成有效的SQL

2. **GENERAL** - 用户询问数据库或数据的一般信息
   - 询问数据库包含什么数据
   - 询问如何使用或分析数据
   - 缺少具体的查询参数

3. **MISLEADING_QUERY** - 与数据库无关的问题
   - 闲聊、问候等
   - 与数据查询完全无关的问题

4. **USER_GUIDE** - 询问系统使用指南
   - 如何使用这个系统
   - 系统功能介绍等

请返回JSON格式的分类结果：
{
    "intent": "TEXT_TO_SQL|GENERAL|MISLEADING_QUERY|USER_GUIDE",
    "reasoning": "分类理由（最多20字）",
    "rephrased_question": "重新表述的问题（如果需要）"
}"""

    def _build_prompt(
        self,
        query: str,
        db_schemas: List[str] = None,
        histories: List[Dict] = None,
    ) -> str:
        """构建意图分类提示词"""
        
        prompt_parts = []
        
        # 数据库模式
        if db_schemas:
            prompt_parts.append("### 数据库模式 ###")
            for schema in db_schemas:
                prompt_parts.append(schema)
            prompt_parts.append("")
        
        # 历史对话
        if histories:
            prompt_parts.append("### 历史对话 ###")
            for history in histories:
                prompt_parts.append(f"问题: {history.get('question', '')}")
                prompt_parts.append(f"SQL: {history.get('sql', '')}")
                prompt_parts.append("")
        
        # 当前问题
        prompt_parts.append("### 当前问题 ###")
        prompt_parts.append(f"用户问题: {query}")
        prompt_parts.append("")
        
        prompt_parts.append("请分析用户意图并返回JSON格式的分类结果：")
        
        return "\n".join(prompt_parts)
    
    async def run(
        self,
        query: str,
        db_schemas: List[str] = None,
        histories: List[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """运行意图分类管道"""
        
        logger.info("开始意图分类...")
        
        try:
            # 构建提示词
            prompt = self._build_prompt(
                query=query,
                db_schemas=db_schemas or [],
                histories=histories,
            )
            
            # 调用LLM进行分类
            generator = self._components["generator"]
            result = await generator(prompt=prompt)
            
            # 解析结果
            if result and result.get("replies"):
                try:
                    response_text = result["replies"][0]
                    # 尝试提取JSON
                    if "{" in response_text and "}" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        json_text = response_text[json_start:json_end]
                        parsed_result = json.loads(json_text)
                        
                        return {
                            "status": "success",
                            "intent": parsed_result.get("intent", "TEXT_TO_SQL"),
                            "reasoning": parsed_result.get("reasoning", ""),
                            "rephrased_question": parsed_result.get("rephrased_question", query),
                            "raw_response": response_text,
                        }
                    else:
                        # 如果没有JSON格式，默认返回TEXT_TO_SQL
                        return {
                            "status": "success",
                            "intent": "TEXT_TO_SQL",
                            "reasoning": "默认分类",
                            "rephrased_question": query,
                            "raw_response": response_text,
                        }
                        
                except json.JSONDecodeError:
                    logger.warning("意图分类结果解析失败，使用默认分类")
                    return {
                        "status": "success",
                        "intent": "TEXT_TO_SQL",
                        "reasoning": "解析失败，默认分类",
                        "rephrased_question": query,
                    }
            else:
                return {
                    "status": "failed",
                    "error": "未能获得分类结果",
                    "intent": "TEXT_TO_SQL",
                }
                
        except Exception as e:
            logger.error(f"意图分类失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "intent": "TEXT_TO_SQL",  # 默认返回SQL生成意图
            }