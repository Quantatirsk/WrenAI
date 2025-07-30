"""
简单的REST API接口
基于FastAPI，提供自然语言转SQL的HTTP接口
"""
import logging
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from nlp_core import WrenNLPCore, QueryRequest, QueryResponse
from providers.llm_provider import SimpleLLMProvider
from config import Config, get_default_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wren-nlp-api")

# 创建FastAPI应用
app = FastAPI(
    title="WrenAI NLP Core API",
    description="自然语言转SQL核心引擎API",
    version="1.0.0"
)

# 全局变量存储核心引擎实例
nlp_core: Optional[WrenNLPCore] = None


class QueryRequestAPI(BaseModel):
    """API查询请求模型"""
    query: str
    project_id: Optional[str] = None
    db_schemas: List[str] = []
    sql_samples: List[Dict] = []
    instructions: List[str] = []
    histories: List[Dict] = []
    enable_intent_classification: bool = True


class QueryResponseAPI(BaseModel):
    """API查询响应模型"""
    status: str
    query_type: str
    intent_reasoning: str = ""
    rephrased_question: str = ""
    sql: str = ""
    error: str = ""
    meta: Dict[str, Any] = {}


class SQLGenerationRequest(BaseModel):
    """SQL生成请求"""
    query: str
    db_schemas: List[str] = []
    sql_samples: List[Dict] = []
    instructions: List[str] = []


class IntentClassificationRequest(BaseModel):
    """意图分类请求"""
    query: str
    db_schemas: List[str] = []
    histories: List[Dict] = []


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化核心引擎"""
    global nlp_core
    
    try:
        # 从环境变量或配置文件加载配置
        config = Config.from_env()
        
        # 创建LLM提供者
        llm_provider = SimpleLLMProvider(
            model=config.llm.model,
            api_key=config.llm.api_key,
            base_url=config.llm.base_url,
            model_kwargs={
                "temperature": config.llm.temperature,
                "max_tokens": config.llm.max_tokens,
            },
            context_window_size=config.llm.context_window_size,
        )
        
        # 创建核心引擎
        nlp_core = WrenNLPCore(
            llm_provider=llm_provider,
            enable_intent_classification=config.core.enable_intent_classification,
        )
        
        logger.info("WrenAI NLP Core API启动成功")
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "WrenAI自然语言转SQL核心引擎",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "core_initialized": nlp_core is not None}


@app.post("/query", response_model=QueryResponseAPI)
async def query_endpoint(request: QueryRequestAPI):
    """
    自然语言查询接口
    支持意图分类和SQL生成的完整流程
    """
    if not nlp_core:
        raise HTTPException(status_code=500, detail="核心引擎未初始化")
    
    try:
        # 转换请求格式
        query_request = QueryRequest(
            query=request.query,
            project_id=request.project_id,
            db_schemas=request.db_schemas,
            sql_samples=request.sql_samples,
            instructions=request.instructions,
            histories=request.histories,
            enable_intent_classification=request.enable_intent_classification,
        )
        
        # 处理查询
        response = await nlp_core.query(query_request)
        
        # 转换响应格式
        return QueryResponseAPI(
            status=response.status,
            query_type=response.query_type,
            intent_reasoning=response.intent_reasoning,
            rephrased_question=response.rephrased_question,
            sql=response.sql,
            error=response.error,
            meta=response.meta or {},
        )
        
    except Exception as e:
        logger.error(f"查询处理异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-sql")
async def generate_sql_endpoint(request: SQLGenerationRequest):
    """
    直接SQL生成接口
    跳过意图分类，直接生成SQL
    """
    if not nlp_core:
        raise HTTPException(status_code=500, detail="核心引擎未初始化")
    
    try:
        result = await nlp_core.generate_sql(
            query=request.query,
            db_schemas=request.db_schemas,
            sql_samples=request.sql_samples,
            instructions=request.instructions,
        )
        
        return {
            "status": result.get("status"),
            "sql": result.get("sql", ""),
            "raw_sql": result.get("raw_sql", ""),
            "error": result.get("error", ""),
            "meta": result.get("meta", {}),
        }
        
    except Exception as e:
        logger.error(f"SQL生成异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify-intent")
async def classify_intent_endpoint(request: IntentClassificationRequest):
    """
    意图分类接口
    仅进行意图分类，不生成SQL
    """
    if not nlp_core:
        raise HTTPException(status_code=500, detail="核心引擎未初始化")
    
    try:
        result = await nlp_core.classify_intent(
            query=request.query,
            db_schemas=request.db_schemas,
            histories=request.histories,
        )
        
        return {
            "status": result.get("status"),
            "intent": result.get("intent"),
            "reasoning": result.get("reasoning", ""),
            "rephrased_question": result.get("rephrased_question", ""),
        }
        
    except Exception as e:
        logger.error(f"意图分类异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )