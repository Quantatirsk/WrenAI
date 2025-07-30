#!/usr/bin/env python3
"""
WrenAI NLP Core 测试脚本
快速测试自然语言转SQL功能
"""
import asyncio
import logging
import os
import sys
import yaml

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nlp_core import WrenNLPCore, QueryRequest
from providers.llm_provider import SimpleLLMProvider
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wren-nlp-test")

async def test_sql_generation():
    """测试SQL生成功能"""
    
    # 加载配置
    try:
        with open("config.yaml", "r") as f:
            config_dict = yaml.safe_load(f)
        config = Config.from_dict(config_dict)
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return
    
    # 检查API密钥
    if config.llm.api_key == "YOUR_API_KEY_HERE":
        # 尝试从环境变量获取
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ 请在config.yaml中设置API密钥或设置OPENAI_API_KEY环境变量")
            return
        config.llm.api_key = api_key
    
    # 创建LLM提供者
    llm_provider = SimpleLLMProvider(
        model=config.llm.model,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url,
        model_kwargs={
            "temperature": config.llm.temperature,
            "max_tokens": config.llm.max_tokens,
        }
    )
    
    # 创建核心引擎
    nlp_core = WrenNLPCore(
        llm_provider=llm_provider,
        enable_intent_classification=config.core.enable_intent_classification,
    )
    
    # 测试数据
    db_schemas = [
        """
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            registration_date DATE,
            is_active BOOLEAN
        );
        """,
        """
        CREATE TABLE orders (
            id INT PRIMARY KEY,
            user_id INT,
            order_date DATE,
            amount DECIMAL(10,2),
            status VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    ]
    
    test_queries = [
        "查询所有活跃用户的数量",
        "显示最近7天的订单金额总和",
        "查询每个用户的订单数量，按数量降序排列",
        "这个数据库有什么表？",  # 应该被识别为GENERAL
        "今天天气怎么样？",  # 应该被识别为MISLEADING_QUERY
    ]
    
    print("\n🚀 开始测试自然语言转SQL功能...\n")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试 {i}: {query}")
        print("-" * 40)
        
        # 创建查询请求
        request = QueryRequest(
            query=query,
            db_schemas=db_schemas,
            enable_intent_classification=True,
        )
        
        # 处理查询
        try:
            response = await nlp_core.query(request)
            
            print(f"状态: {response.status}")
            print(f"查询类型: {response.query_type}")
            
            if response.intent_reasoning:
                print(f"意图推理: {response.intent_reasoning}")
            
            if response.sql:
                print(f"生成的SQL:")
                print(f"{response.sql}")
            
            if response.error:
                print(f"错误: {response.error}")
            
            if response.meta.get("message"):
                print(f"消息: {response.meta['message']}")
                
        except Exception as e:
            print(f"执行异常: {e}")
        
        print("-" * 40)
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    asyncio.run(test_sql_generation())