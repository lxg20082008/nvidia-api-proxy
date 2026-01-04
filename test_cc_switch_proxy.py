#!/usr/bin/env python3
"""
测试 CC Switch 代理
模拟 CC Switch 发送 Claude API 格式请求
"""

import json
import urllib.request
import urllib.error

# 代理配置（与 CC Switch 配置一致）
PROXY_URL = "http://127.0.0.1:8080/v1/messages"
API_KEY = "test-key"

# 测试请求（Claude API 格式）
test_request = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": "你好，请用一句话介绍你自己。"
        }
    ]
}

print("=" * 60)
print("测试 CC Switch 代理")
print("=" * 60)
print()
print(f"代理地址: {PROXY_URL}")
print(f"测试模型: {test_request['model']}")
print(f"测试消息: {test_request['messages'][0]['content']}")
print()
print("发送请求...")
print()

try:
    # 构建请求
    req = urllib.request.Request(
        PROXY_URL,
        data=json.dumps(test_request).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'x-api-key': API_KEY,
            'anthropic-version': '2023-06-01'
        }
    )

    # 发送请求
    with urllib.request.urlopen(req, timeout=30) as response:
        response_data = json.loads(response.read().decode('utf-8'))

    print("✓ 请求成功！")
    print()
    print("响应内容:")
    print("-" * 60)

    # 提取响应文本
    if response_data.get("content") and len(response_data["content"]) > 0:
        text = response_data["content"][0].get("text", "")
        print(text)
    else:
        print("(无内容)")

    print("-" * 60)
    print()
    print("响应详情:")
    print(f"  模型: {response_data.get('model', 'unknown')}")
    print(f"  停止原因: {response_data.get('stop_reason', 'unknown')}")
    print(f"  输入 tokens: {response_data.get('usage', {}).get('input_tokens', 0)}")
    print(f"  输出 tokens: {response_data.get('usage', {}).get('output_tokens', 0)}")
    print()
    print("=" * 60)
    print("✓ 代理工作正常！CC Switch 可以正常使用。")
    print("=" * 60)

except urllib.error.HTTPError as e:
    print(f"✗ HTTP 错误: {e.code}")
    print(f"错误信息: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"✗ 错误: {str(e)}")
