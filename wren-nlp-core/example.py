"""
WrenAI NLP Core 使用示例
演示如何使用最小化后端进行自然语言到SQL的转换
"""
import asyncio
import logging
import os
from typing import List

from nlp_core import WrenNLPCore, QueryRequest
from providers.llm_provider import SimpleLLMProvider
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """主函数示例"""
    
    # 1. 配置LLM
    # 确保设置了API密钥
    api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"
    if api_key == "your-api-key-here":
        print("请设置 OPENAI_API_KEY 环境变量或修改 api_key 变量")
        return
    
    # 创建LLM提供者
    llm_provider = SimpleLLMProvider(
        model="gpt-3.5-turbo",
        api_key=api_key,
        model_kwargs={
            "temperature": 0.1,
            "max_tokens": 1000,
        }
    )
    
    # 2. 创建核心引擎
    nlp_core = WrenNLPCore(
        llm_provider=llm_provider,
        enable_intent_classification=True,
    )
    
    # 3. 准备示例数据
    # 数据库模式示例
    db_schemas = [
        """
        CREATE TABLE customers (
            customer_id INT PRIMARY KEY,
            customer_name VARCHAR(100),
            email VARCHAR(100),
            registration_date DATE,
            status VARCHAR(20)
        );
        """,
        """
        CREATE TABLE orders (
            order_id INT PRIMARY KEY,
            customer_id INT,
            order_date DATE,
            total_amount DECIMAL(10,2),
            status VARCHAR(20),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """,
        """
        CREATE TABLE products (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(100),
            category VARCHAR(50),
            price DECIMAL(10,2),
            stock_quantity INT
        );
        """
    ]
    
    # SQL示例
    sql_samples = [
        {
            "question": "有多少客户？",
            "sql": "SELECT COUNT(*) FROM customers"
        },
        {
            "question": "最近一个月的订单总金额是多少？",
            "sql": "SELECT SUM(total_amount) FROM orders WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
        }
    ]
    
    # 用户指令
    instructions = [
        "总是使用标准SQL语法",
        "对于日期计算使用MySQL函数",
        "结果应该包含清晰的列名"
    ]
    
    # 4. 测试查询
    test_queries = [
        "显示所有活跃客户的信息",
        "查找最近7天的订单",
        "哪些产品库存不足20件？",
        "今天天气怎么样？",  # 这个应该被分类为MISLEADING_QUERY
        "这个数据库包含什么信息？",  # 这个应该被分类为GENERAL
    ]
    
    print("🚀 开始测试WrenAI NLP Core...")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 测试查询 {i}: {query}")
        print("-" * 30)
        
        # 创建查询请求
        request = QueryRequest(
            query=query,
            db_schemas=db_schemas,
            sql_samples=sql_samples,
            instructions=instructions,
            enable_intent_classification=True,
        )
        
        # 处理查询
        try:
            response = await nlp_core.query(request)
            
            print(f"✅ 状态: {response.status}")
            print(f"🎯 查询类型: {response.query_type}")
            
            if response.intent_reasoning:
                print(f"💭 意图推理: {response.intent_reasoning}")
            
            if response.rephrased_question != query:
                print(f"🔄 重新表述: {response.rephrased_question}")
            
            if response.sql:
                print(f"🗃️  生成的SQL:")
                print(f"   {response.sql}")
            
            if response.error:
                print(f"❌ 错误: {response.error}")
                
            if response.meta.get("message"):
                print(f"💬 消息: {response.meta['message']}")
                
        except Exception as e:
            print(f"❌ 处理异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")


async def test_direct_sql_generation():
    """测试直接SQL生成（跳过意图分类）"""
    
    print("\n🔧 测试直接SQL生成功能...")
    print("=" * 50)
    
    # 配置（简化）
    api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"
    if api_key == "your-api-key-here":
        print("请设置API密钥")
        return
    
    llm_provider = SimpleLLMProvider(model="gpt-3.5-turbo", api_key=api_key)
    nlp_core = WrenNLPCore(llm_provider=llm_provider)
    
    # 直接生成SQL
    result = await nlp_core.generate_sql(
        query="查找注册超过1年的所有客户",
        db_schemas=[
            "CREATE TABLE customers (customer_id INT, customer_name VARCHAR(100), registration_date DATE);"
        ],
    )
    
    print(f"状态: {result.get('status')}")
    print(f"SQL: {result.get('sql')}")


if __name__ == "__main__":
    # 运行主示例
    asyncio.run(main())
    
    # 运行直接SQL生成示例
    # asyncio.run(test_direct_sql_generation())