# WrenAI自然语言转SQL核心引擎

基于WrenAI核心逻辑提取的最小化后端，专注于自然语言到SQL转换的核心功能，剥离了所有UI和Web依赖。

## 🎯 功能特性

- **意图分类**: 智能判断用户查询类型（TEXT_TO_SQL、GENERAL、MISLEADING_QUERY、USER_GUIDE）
- **SQL生成**: 基于自然语言和数据库模式生成准确的SQL查询
- **多模型支持**: 通过LiteLLM统一接口支持OpenAI、Anthropic、本地模型等
- **最小化设计**: 纯净的核心逻辑，无UI耦合，易于集成
- **配置灵活**: 支持环境变量、YAML文件、代码配置等多种方式

## 🏗️ 架构设计

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
├── nlp_core.py               # 主要核心引擎类
├── config.py                 # 配置管理
├── api.py                    # REST API接口
├── example.py                # 使用示例
└── requirements.txt          # 依赖清单
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 设置API密钥
export OPENAI_API_KEY="your-openai-api-key"

# 或其他配置
export WREN_LLM_MODEL="gpt-4"
export WREN_LLM_TEMPERATURE="0.1"
```

### 3. 基础使用

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
        "CREATE TABLE users (id INT, name VARCHAR(100), email VARCHAR(100));",
        "CREATE TABLE orders (id INT, user_id INT, amount DECIMAL(10,2));"
    ]
    
    # 创建查询请求
    request = QueryRequest(
        query="显示所有用户的订单总金额",
        db_schemas=db_schemas
    )
    
    # 处理查询  
    response = await nlp_core.query(request)
    
    print(f"查询类型: {response.query_type}")
    print(f"生成的SQL: {response.sql}")

asyncio.run(main())
```

### 4. 启动API服务

```bash
python api.py
```

然后访问 http://localhost:8000/docs 查看API文档。

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

## ⚙️ 配置说明

### 环境变量配置

```bash
# LLM配置
WREN_LLM_MODEL=gpt-3.5-turbo
WREN_LLM_API_KEY=your-api-key
WREN_LLM_BASE_URL=https://api.openai.com/v1
WREN_LLM_TEMPERATURE=0.1
WREN_LLM_MAX_TOKENS=1000

# 核心功能配置  
WREN_ENABLE_INTENT_CLASSIFICATION=true
WREN_MAX_HISTORIES=5
WREN_LOG_LEVEL=INFO
```

### YAML配置文件

```yaml
llm:
  model: "gpt-3.5-turbo"
  api_key: "your-api-key"
  temperature: 0.1
  max_tokens: 1000

core:
  enable_intent_classification: true
  max_histories: 5
  log_level: "INFO"
```

## 🔧 核心组件说明

### 1. WrenNLPCore - 主引擎

核心引擎类，整合所有管道提供统一接口：

- `query()` - 完整的查询处理流程
- `generate_sql()` - 直接SQL生成  
- `classify_intent()` - 意图分类

### 2. Pipeline - 管道系统

- `SQLGenerationPipeline` - SQL生成管道
- `IntentClassificationPipeline` - 意图分类管道

### 3. Provider - 服务提供者

- `SimpleLLMProvider` - LLM服务提供者
- 支持扩展其他提供者（嵌入模型、向量数据库等）

## 🎨 扩展开发

### 添加新的LLM提供者

```python
from core.provider import LLMProvider

class CustomLLMProvider(LLMProvider):
    def get_generator(self, *args, **kwargs):
        # 实现自定义LLM生成器
        return CustomGenerator(...)
```

### 添加新的管道

```python
from core.pipeline import BasicPipeline

class CustomPipeline(BasicPipeline):
    async def run(self, *args, **kwargs):
        # 实现自定义管道逻辑
        return result
```

## 🧪 测试

运行示例：

```bash
python example.py
```

运行API测试：

```bash
# 启动API
python api.py

# 在另一个终端测试
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "显示所有用户",
       "db_schemas": ["CREATE TABLE users (id INT, name VARCHAR(100));"]
     }'
```

## 📦 依赖说明

### 核心依赖

- **FastAPI + Uvicorn**: Web API框架
- **OpenAI + LiteLLM**: LLM统一接口  
- **SQLGlot**: SQL解析和处理
- **Pydantic**: 数据验证

### 与原WrenAI的差异

- ❌ 移除了Haystack-AI管道框架
- ❌ 移除了Qdrant向量数据库依赖
- ❌ 移除了Web UI相关依赖
- ❌ 移除了复杂的异步任务管理
- ✅ 保留了核心SQL生成逻辑
- ✅ 保留了意图分类功能
- ✅ 简化了配置和部署

## 🤝 与原系统集成

### 作为独立服务

```python
# 启动独立API服务
python api.py
```

### 作为Python模块

```python
from nlp_core import WrenNLPCore
from providers.llm_provider import SimpleLLMProvider

# 直接在代码中使用
nlp_core = WrenNLPCore(SimpleLLMProvider(...))
result = await nlp_core.query(request)
```

### 替换原WrenAI组件

将此核心引擎替换原WrenAI中的相应组件：

1. 替换 `src/web/v1/services/ask.py` 的核心逻辑
2. 移除Haystack管道依赖
3. 简化配置管理

## 📄 许可证

基于原WrenAI项目，遵循AGPL-3.0许可证。

## 🔗 相关链接

- [原WrenAI项目](https://github.com/Canner/WrenAI)
- [LiteLLM文档](https://docs.litellm.ai/)
- [FastAPI文档](https://fastapi.tiangolo.com/)