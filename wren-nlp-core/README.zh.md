# WrenAI 自然语言转SQL核心引擎

这是基于WrenAI项目提取的自然语言转SQL核心引擎，已经剥离了UI和Web相关的依赖，专注于提供纯净的自然语言到SQL转换功能。

## 🎯 功能特性

- **意图分类**: 智能判断用户查询类型（TEXT_TO_SQL、GENERAL、MISLEADING_QUERY、USER_GUIDE）
- **SQL生成**: 基于自然语言和数据库模式生成准确的SQL查询
- **多模型支持**: 通过统一接口支持OpenAI、Anthropic等多种LLM
- **最小化设计**: 纯净的核心逻辑，无UI耦合，易于集成
- **API服务**: 提供REST API接口，方便调用

## 🏗️ 项目结构

```
wren-nlp-core/
├── core/                      # 核心框架
│   ├── pipeline.py           # 管道基础类
│   ├── engine.py             # SQL执行引擎抽象
│   └── provider.py           # 服务提供者抽象
├── providers/                # 服务提供者实现
│   └── llm_provider.py       # LLM服务提供者
├── pipelines/                # 核心管道
│   ├── sql_generation.py     # SQL生成管道
│   └── intent_classification.py # 意图分类管道
├── api.py                    # REST API接口
├── config.py                 # 配置管理
├── nlp_core.py               # 主核心引擎类
├── config.example.yaml       # 配置示例
├── run_test.py               # 测试脚本
├── test_api_client.py        # API客户端测试脚本
├── SETUP.md                  # 部署指南
└── requirements.txt          # 依赖清单
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

编辑`config.yaml`文件，设置你的LLM API密钥：

```yaml
llm:
  model: "gpt-3.5-turbo"
  api_key: "your-api-key-here"
```

或者设置环境变量：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 运行测试脚本

```bash
python run_test.py
```

### 4. 启动API服务

```bash
python api.py
# 或者
./start_api.sh
```

访问 http://localhost:8000/docs 查看API文档。

### 5. 测试API服务

```bash
python test_api_client.py
```

## 📋 API接口

### POST /query - 完整查询处理

```json
{
    "query": "显示最近一个月的销售总额",
    "db_schemas": [
        "CREATE TABLE sales (id INT, amount DECIMAL(10,2), sale_date DATE);"
    ],
    "sql_samples": [
        {
            "question": "总销售额是多少？",
            "sql": "SELECT SUM(amount) FROM sales"
        }
    ],
    "instructions": ["使用标准SQL语法"],
    "enable_intent_classification": true
}
```

### POST /generate-sql - 直接生成SQL

```json
{
    "query": "查找活跃用户",
    "db_schemas": [
        "CREATE TABLE users (id INT, status VARCHAR(20));"
    ]
}
```

### POST /classify-intent - 意图分类

```json
{
    "query": "这个数据库包含什么？",
    "db_schemas": ["..."]
}
```

## 💡 代码示例

```python
import asyncio
from nlp_core import WrenNLPCore, QueryRequest
from providers.llm_provider import SimpleLLMProvider

async def main():
    # 创建LLM提供者
    llm_provider = SimpleLLMProvider(
        model="gpt-3.5-turbo",
        api_key="your-api-key"
    )
    
    # 创建核心引擎
    nlp_core = WrenNLPCore(llm_provider=llm_provider)
    
    # 准备数据库模式
    db_schemas = [
        "CREATE TABLE users (id INT, name VARCHAR(100), email VARCHAR(100));"
    ]
    
    # 创建查询请求
    request = QueryRequest(
        query="显示所有用户",
        db_schemas=db_schemas
    )
    
    # 处理查询  
    response = await nlp_core.query(request)
    
    print(f"生成的SQL: {response.sql}")

asyncio.run(main())
```

## 📦 依赖说明

核心依赖：
- **OpenAI/LiteLLM**: LLM接口调用
- **FastAPI + Uvicorn**: API服务框架
- **PyYAML**: 配置管理
- **SQLGlot**: SQL解析和处理

## 🔧 定制和扩展

请参考 `SETUP.md` 获取详细的部署和配置说明。

## 📄 许可证

基于原WrenAI项目，遵循AGPL-3.0许可证。