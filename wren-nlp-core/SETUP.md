# WrenAI 自然语言转SQL核心引擎部署指南

本文档提供如何在本地部署和运行WrenAI自然语言转SQL核心引擎的详细步骤。

## 1. 环境准备

### 系统要求
- Python 3.8+
- pip (包管理器)

### 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv wren-env

# 激活虚拟环境
# Windows
wren-env\Scripts\activate
# MacOS/Linux
source wren-env/bin/activate
```

## 2. 安装依赖

```bash
# 安装依赖
pip install -r requirements.txt
```

## 3. 配置设置

1. 复制配置示例文件（如果没有config.yaml）:
```bash
cp config.example.yaml config.yaml
```

2. 编辑`config.yaml`文件，设置你的API密钥:
```yaml
llm:
  api_key: "your-openai-api-key"
```

或者，你可以设置环境变量:
```bash
# MacOS/Linux
export OPENAI_API_KEY="your-openai-api-key"

# Windows
set OPENAI_API_KEY=your-openai-api-key
```

## 4. 运行测试脚本

```bash
# 运行测试脚本
python run_test.py
```

## 5. 启动API服务（可选）

如果你想启动REST API服务:

```bash
# 启动API服务
python api.py
```

API服务默认将在 http://localhost:8000 运行。

你可以访问 http://localhost:8000/docs 查看API文档。

## 6. API使用示例

使用curl测试API:

```bash
# 测试直接SQL生成
curl -X POST "http://localhost:8000/generate-sql" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "查找所有活跃用户",
       "db_schemas": ["CREATE TABLE users (id INT, name VARCHAR(100), is_active BOOLEAN);"]
     }'
```

## 7. 故障排除

### 常见问题

1. **API密钥错误**:
   - 确认你已正确设置API密钥
   - 检查API密钥是否有效

2. **依赖安装问题**:
   - 尝试更新pip: `pip install --upgrade pip`
   - 逐个安装有问题的依赖包

3. **OpenAI API请求失败**:
   - 检查网络连接
   - 确认API密钥有足够的配额

如有其他问题，请检查日志输出，默认日志级别为INFO。可以在配置文件中将日志级别调整为DEBUG获取更详细信息。