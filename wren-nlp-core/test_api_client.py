#!/usr/bin/env python3
"""
WrenAI NLP Core API 客户端测试脚本
"""
import json
import requests
import sys
import time

# API服务URL
API_URL = "http://localhost:8000"

def test_api():
    """测试API服务的各个端点"""
    
    print("🚀 开始测试API服务...")
    print("=" * 50)
    
    # 1. 测试健康检查端点
    try:
        print("\n1️⃣ 测试健康检查...")
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print(f"✅ 健康检查成功: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 请求失败，API服务可能未运行: {e}")
        print("请先运行 'python api.py' 启动服务")
        return
    
    # 2. 测试SQL生成端点
    print("\n2️⃣ 测试SQL生成...")
    sql_data = {
        "query": "查询所有活跃用户",
        "db_schemas": ["CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), is_active BOOLEAN);"],
        "sql_samples": [],
        "instructions": ["使用标准SQL语法"]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/generate-sql",
            json=sql_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SQL生成成功:")
            print(f"SQL: {result.get('sql', '')}")
        else:
            print(f"❌ SQL生成失败: {response.status_code}")
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 测试意图分类端点
    print("\n3️⃣ 测试意图分类...")
    intent_data = {
        "query": "今天天气怎么样？",
        "db_schemas": ["CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), is_active BOOLEAN);"],
        "histories": []
    }
    
    try:
        response = requests.post(
            f"{API_URL}/classify-intent",
            json=intent_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 意图分类成功:")
            print(f"意图类型: {result.get('intent', '')}")
            print(f"推理过程: {result.get('reasoning', '')}")
        else:
            print(f"❌ 意图分类失败: {response.status_code}")
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 4. 测试完整查询端点
    print("\n4️⃣ 测试完整查询流程...")
    query_data = {
        "query": "列出所有用户的订单总数",
        "db_schemas": [
            "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));",
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount DECIMAL(10,2), FOREIGN KEY (user_id) REFERENCES users(id));"
        ],
        "sql_samples": [],
        "instructions": [],
        "enable_intent_classification": True
    }
    
    try:
        response = requests.post(
            f"{API_URL}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 查询处理成功:")
            print(f"状态: {result.get('status', '')}")
            print(f"查询类型: {result.get('query_type', '')}")
            
            if result.get('intent_reasoning'):
                print(f"意图推理: {result.get('intent_reasoning', '')}")
                
            if result.get('sql'):
                print(f"生成的SQL: {result.get('sql', '')}")
        else:
            print(f"❌ 查询处理失败: {response.status_code}")
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API测试完成!")

if __name__ == "__main__":
    test_api()