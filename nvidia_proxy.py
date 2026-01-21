#!/usr/bin/env python3
"""
NVIDIA API 格式转换代理（简化版，仅使用标准库）
将 Claude API 格式转换为 OpenAI 格式，用于 CC Switch
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import time

# NVIDIA API 配置
NVIDIA_API_KEY = "nvapi-XXX"
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# 模型映射
MODEL_MAPPING = {
    # "claude-3-5-sonnet-20241022": "qwen/qwen2.5-coder-7b-instruct",
    # "claude-3-5-haiku-20241022": "google/gemma-3-4b-it",
    # "claude-3-opus-20240229": "qwen/qwen3-235b-a22b",
    # "claude-sonnet-4-20250514": "qwen/qwen2.5-coder-7b-instruct",
    # "default": "qwen/qwen2.5-coder-7b-instruct"
    # 主力模型：GLM‑4.7
    "claude-3-5-sonnet-20241022": "z-ai/glm4.7",
    "claude-3-opus-20240229": "z-ai/glm4.7",
    "claude-sonnet-4-20250514": "z-ai/glm4.7",

    # 轻量模型：MiniMax M2.1
    "claude-3-5-haiku-20241022": "minimaxai/minimax-m2.1",

    # 默认模型（兜底）
    "default": "z-ai/glm4.7"
}

class ProxyHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/v1/messages':
            self.handle_messages()
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_error(404)

    def handle_messages(self):
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            claude_request = json.loads(body.decode('utf-8'))

            print(f"\n{'='*60}")
            print(f"收到 Claude 请求: {claude_request.get('model', 'unknown')}")

            # 转换为 OpenAI 格式
            openai_request = self.convert_claude_to_openai(claude_request)
            print(f"转换为 NVIDIA 模型: {openai_request['model']}")

            # 调用 NVIDIA API
            req = urllib.request.Request(
                NVIDIA_API_URL,
                data=json.dumps(openai_request).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {NVIDIA_API_KEY}',
                    'Content-Type': 'application/json'
                }
            )

            start_time = time.time()
            with urllib.request.urlopen(req, timeout=60) as response:
                elapsed_time = time.time() - start_time
                openai_response = json.loads(response.read().decode('utf-8'))

            print(f"NVIDIA API 响应: {response.status} ({elapsed_time:.2f}秒)")

            # 转换为 Claude 格式
            claude_response = self.convert_openai_to_claude(openai_response)
            print(f"✓ 成功转换为 Claude 格式")
            print(f"{'='*60}\n")

            # 发送响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(claude_response).encode('utf-8'))

        except Exception as e:
            print(f"✗ 错误: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                "type": "error",
                "error": {"type": "api_error", "message": str(e)}
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def convert_claude_to_openai(self, claude_request):
        """将 Claude API 请求转换为 OpenAI 格式"""
        claude_model = claude_request.get("model", "default")
        nvidia_model = MODEL_MAPPING.get(claude_model, MODEL_MAPPING["default"])

        messages = []

        # 处理 system 参数
        if "system" in claude_request:
            messages.append({
                "role": "system",
                "content": claude_request["system"]
            })

        # 转换 messages
        for msg in claude_request.get("messages", []):
            content = msg.get("content", "")
            if isinstance(content, list):
                text_parts = [item.get("text", "") for item in content if item.get("type") == "text"]
                content = "\n".join(text_parts)

            messages.append({
                "role": msg.get("role", "user"),
                "content": content
            })

        return {
            "model": nvidia_model,
            "messages": messages,
            "temperature": claude_request.get("temperature", 0.7),
            "max_tokens": claude_request.get("max_tokens", 4096),
        }

    def convert_openai_to_claude(self, openai_response):
        """将 OpenAI API 响应转换为 Claude 格式"""
        choice = openai_response.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")

        return {
            "id": openai_response.get("id", ""),
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
            "model": openai_response.get("model", ""),
            "stop_reason": "end_turn" if choice.get("finish_reason") == "stop" else choice.get("finish_reason"),
            "stop_sequence": None,
            "usage": {
                "input_tokens": openai_response.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": openai_response.get("usage", {}).get("completion_tokens", 0)
            }
        }

    def log_message(self, format, *args):
        # 禁用默认日志
        pass

if __name__ == '__main__':
    PORT = 18080
    print("="*60)
    print("NVIDIA API 格式转换代理（简化版）")
    print("="*60)
    print()
    print(f"监听: http://127.0.0.1:{PORT}")
    print()
    print("CC Switch 配置:")
    print(f"  请求地址: http://127.0.0.1:{PORT}/v1")
    print("  API Key: 任意值（例如：test-key）")
    print()
    print("按 Ctrl+C 停止")
    print("="*60)
    print()

    server = HTTPServer(('127.0.0.1', PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n代理已停止")
        server.shutdown()
