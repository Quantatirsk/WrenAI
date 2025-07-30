# WrenAI自然语言转SQL演示部署指南

本文档提供如何在本地部署和运行WrenAI自然语言转SQL演示系统的详细步骤。

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

## 3. 配置GLM模型

您需要获取[智谱AI](https://open.bigmodel.cn/)的API密钥。

1. 修改`config.yaml`文件：

```yaml
llm:
  provider: "glm"
  model: "glm-4"  # 或 "glm-3-turbo"
  api_key: "YOUR_GLM_API_KEY_HERE" # 修改为您的智谱API密钥
```

2. 或者，您可以设置环境变量:

```bash
# MacOS/Linux
export WREN_LLM_PROVIDER="glm"
export WREN_LLM_MODEL="glm-4"
export WREN_LLM_API_KEY="your-glm-api-key"

# Windows
set WREN_LLM_PROVIDER=glm
set WREN_LLM_MODEL=glm-4
set WREN_LLM_API_KEY=your-glm-api-key
```

## 4. 启动演示系统

```bash
# 启动API服务和Web界面
python api.py
```

访问 http://localhost:8000 查看Web演示界面。

## 5. 使用演示系统

1. 在Web界面中，您可以：
   - 输入自然语言查询
   - 查看或修改数据库模式
   - 生成SQL查询
   - 查看生成的SQL结果

2. 提供的默认数据库模式包含：
   - 用户(users)表
   - 订单(orders)表

3. 示例查询：
   - "查询所有活跃用户的数量"
   - "显示最近7天的订单金额总和"
   - "查询每个用户的订单数量，按数量降序排列"

## 6. 故障排除

### 常见问题

1. **API密钥错误**:
   - 确认您已正确设置智谱API密钥
   - 检查API密钥是否有效

2. **前端无法连接到后端**:
   - 确保API服务正在运行（端口8000）
   - 检查浏览器控制台是否有错误信息

3. **GLM API请求失败**:
   - 检查网络连接
   - 确认API密钥有足够的配额
   - 查看服务器日志中的详细错误信息

如有其他问题，请检查日志输出，默认日志级别为INFO。可以在配置文件中将日志级别调整为DEBUG获取更详细信息。

## 7. 切换至其他模型

如果您想使用OpenAI而不是GLM，可以修改配置：

```yaml
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  api_key: "YOUR_OPENAI_API_KEY"
```

或通过环境变量：

```bash
export WREN_LLM_PROVIDER="openai"
export WREN_LLM_MODEL="gpt-3.5-turbo"
export WREN_LLM_API_KEY="your-openai-api-key"
```