"""
WrenAI自然语言转SQL核心引擎
整合所有管道，提供统一的接口
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.provider import LLMProvider
from pipelines.sql_generation import SQLGenerationPipeline
from pipelines.intent_classification import IntentClassificationPipeline

logger = logging.getLogger("wren-nlp-core")


@dataclass
class DatabaseSchema:
    """数据库模式定义"""
    table_name: str
    table_ddl: str
    description: str = ""


@dataclass
class QueryRequest:
    """查询请求"""
    query: str  # 用户自然语言查询
    project_id: Optional[str] = None
    db_schemas: List[str] = None  # 数据库模式DDL列表
    sql_samples: List[Dict] = None  # SQL示例
    instructions: List[str] = None  # 用户指令
    histories: List[Dict] = None  # 历史对话
    enable_intent_classification: bool = True
    enable_sql_generation_reasoning: bool = False


@dataclass 
class QueryResponse:
    """查询响应"""
    status: str  # "success" | "failed"
    query_type: str  # "TEXT_TO_SQL" | "GENERAL" | "MISLEADING_QUERY" | "USER_GUIDE"
    intent_reasoning: str = ""
    rephrased_question: str = ""
    sql: str = ""
    raw_sql: str = ""
    error: str = ""
    meta: Dict[str, Any] = None


class WrenNLPCore:
    """WrenAI自然语言转SQL核心引擎"""
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        enable_intent_classification: bool = True,
        **kwargs,
    ):
        self.llm_provider = llm_provider
        self.enable_intent_classification = enable_intent_classification
        
        # 初始化管道
        self.intent_classification_pipeline = IntentClassificationPipeline(
            llm_provider=llm_provider
        ) if enable_intent_classification else None
        
        self.sql_generation_pipeline = SQLGenerationPipeline(
            llm_provider=llm_provider
        )
        
        logger.info("WrenNLPCore初始化完成")
    
    async def query(self, request: QueryRequest) -> QueryResponse:
        """
        处理自然语言查询请求
        
        Args:
            request: 查询请求对象
            
        Returns:
            QueryResponse: 查询响应对象
        """
        
        logger.info(f"处理查询: {request.query}")
        
        response = QueryResponse(
            status="success",
            query_type="TEXT_TO_SQL",
            rephrased_question=request.query,
            meta={}
        )
        
        try:
            # 1. 意图分类（可选）
            if self.enable_intent_classification and self.intent_classification_pipeline:
                intent_result = await self.intent_classification_pipeline.run(
                    query=request.query,
                    db_schemas=request.db_schemas or [],
                    histories=request.histories or [],
                )
                
                if intent_result.get("status") == "success":
                    response.query_type = intent_result.get("intent", "TEXT_TO_SQL")
                    response.intent_reasoning = intent_result.get("reasoning", "")
                    response.rephrased_question = intent_result.get("rephrased_question", request.query)
                    
                    logger.info(f"意图分类结果: {response.query_type}")
                    
                    # 如果不是SQL生成请求，直接返回
                    if response.query_type != "TEXT_TO_SQL":
                        response.sql = ""
                        response.meta["message"] = self._get_non_sql_response(response.query_type)
                        return response
            
            # 2. SQL生成
            if response.query_type == "TEXT_TO_SQL":
                sql_result = await self.sql_generation_pipeline.run(
                    query=response.rephrased_question,
                    db_schemas=request.db_schemas or [],
                    sql_samples=request.sql_samples or [],
                    instructions=request.instructions or [],
                )
                
                if sql_result.get("status") == "success":
                    response.sql = sql_result.get("sql", "")
                    response.raw_sql = sql_result.get("raw_sql", "")
                    response.meta.update(sql_result.get("meta", {}))
                    
                    logger.info(f"SQL生成成功: {response.sql}")
                else:
                    response.status = "failed"
                    response.error = sql_result.get("error", "SQL生成失败")
                    logger.error(f"SQL生成失败: {response.error}")
            
            return response
            
        except Exception as e:
            logger.error(f"查询处理异常: {e}")
            response.status = "failed"
            response.error = str(e)
            return response
    
    def _get_non_sql_response(self, query_type: str) -> str:
        """获取非SQL查询类型的响应消息"""
        
        responses = {
            "GENERAL": "这是一个关于数据的一般性询问。请提供更具体的查询条件以生成SQL。",
            "MISLEADING_QUERY": "抱歉，您的问题似乎与数据查询无关。请提出与数据库相关的问题。",
            "USER_GUIDE": "这是一个关于系统使用的问题。请查看用户指南或提供具体的数据查询需求。",
        }
        
        return responses.get(query_type, "未知查询类型")
    
    async def generate_sql(
        self,
        query: str,
        db_schemas: List[str] = None,
        sql_samples: List[Dict] = None,
        instructions: List[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        直接生成SQL（跳过意图分类）
        
        Args:
            query: 自然语言查询
            db_schemas: 数据库模式列表
            sql_samples: SQL示例
            instructions: 用户指令
            
        Returns:
            Dict: SQL生成结果
        """
        
        return await self.sql_generation_pipeline.run(
            query=query,
            db_schemas=db_schemas or [],
            sql_samples=sql_samples or [],
            instructions=instructions or [],
            **kwargs,
        )
    
    async def classify_intent(
        self,
        query: str,
        db_schemas: List[str] = None,
        histories: List[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        查询意图分类
        
        Args:
            query: 用户查询
            db_schemas: 数据库模式列表
            histories: 历史对话
            
        Returns:
            Dict: 意图分类结果
        """
        
        if not self.intent_classification_pipeline:
            return {
                "status": "disabled",
                "intent": "TEXT_TO_SQL",
                "reasoning": "意图分类功能已禁用",
            }
        
        return await self.intent_classification_pipeline.run(
            query=query,
            db_schemas=db_schemas or [],
            histories=histories or [],
            **kwargs,
        )