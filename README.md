# NVIDIA API 格式转换代理

将 Claude API 格式转换为 OpenAI 格式，用于 CC Switch 等工具调用 NVIDIA 免费 API。

## 项目简介

NVIDIA Build 提供了 150+ 免费 AI 模型的 API 访问，但使用的是 OpenAI API 格式。而 CC Switch 等工具期望的是 Claude API 格式。本项目提供了一个轻量级的格式转换代理，让你可以在 CC Switch 中无缝使用 NVIDIA 的免费模型。

### 特点

- ✅ **零依赖**：仅使用 Python 标准库
- ✅ **轻量级**：单文件实现，代码简洁
- ✅ **双向转换**：Claude API ↔ OpenAI API
- ✅ **模型映射**：自动映射 Claude 模型名到 NVIDIA 模型
- ✅ **免费使用**：基于 NVIDIA Build 免费 API

## 快速开始

### 1. 获取 NVIDIA API Key

访问 [NVIDIA Build](https://build.nvidia.com) 注册并获取免费 API Key（有效期 6 个月）。

### 2. 配置 API Key

编辑 `nvidia_proxy.pyw`，修改第 14 行：

```python
NVIDIA_API_KEY = "你的-NVIDIA-API-Key"
```

### 3. 启动代理

```bash
python3 nvidia_proxy.pyw
```

代理将在 `http://127.0.0.1:18080` 启动。

### 4. 配置 CC Switch

在 CC Switch 中添加新的供应商：

| 配置项 | 值 |
|--------|-----|
| 供应商名称 | NVIDIA Proxy |
| 请求地址 | `http://127.0.0.1:18080/v1` |
| API Key | `test-key`（任意值） |
| 主模型 | `claude-3-5-sonnet-20241022` |
| Haiku 模型 | `claude-3-5-haiku-20241022` |
| Sonnet 模型 | `claude-sonnet-4-20250514` |
| Opus 模型 | `claude-3-opus-20240229` |

## 模型映射

：

| CC‑Switch 选择的 Claude 模型 | 实际调用的 NVIDIA 模型 |
| --- | --- |
| claude-3-5-sonnet-20241022 | z-ai/glm4.7 |
| claude-3-5-haiku-20241022 | minimaxai/minimax-m2.1 |
| claude-3-opus-20240229 | z-ai/glm4.7 |
| claude-sonnet-4-20250514 | z-ai/glm4.7 |

你

你可以在 `nvidia_proxy.pyw` 中修改 `MODEL_MAPPING` 字典来自定义模型映射。

## 测试

运行测试脚本验证代理是否正常工作：

```bash
python3 test_cc_switch_proxy.py
```

成功输出示例：

```
============================================================
测试 CC Switch 代理
============================================================

代理地址: http://127.0.0.1:18080/v1/messages
测试模型: claude-3-5-sonnet-20241022
测试消息: 你好，请用一句话介绍你自己。

发送请求...

✓ 请求成功！

响应内容:
------------------------------------------------------------
你好，我是一个由阿里云开发的人工智能助手。
------------------------------------------------------------

响应详情:
  模型: qwen/qwen2.5-coder-7b-instruct
  停止原因: end_turn
  输入 tokens: 36
  输出 tokens: 13

============================================================
✓ 代理工作正常！CC Switch 可以正常使用。
============================================================
```

## 工作原理

```
CC Switch (Claude API 格式)
    ↓
代理接收请求 (/v1/messages)
    ↓
转换为 OpenAI 格式
    ↓
调用 NVIDIA API
    ↓
转换响应为 Claude 格式
    ↓
返回给 CC Switch
```

### 格式转换示例

**Claude API 请求：**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "max_tokens": 1024
}
```

**转换为 OpenAI 格式：**
```json
{
  "model": "qwen/qwen2.5-coder-7b-instruct",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "max_tokens": 1024
}
```

## 后台运行

### macOS/Linux

```bash
# 后台启动
nohup python3 nvidia_proxy.pyw > proxy.log 2>&1 &

# 查看日志
tail -f proxy.log

# 停止代理
pkill -f nvidia_proxy.pyw
```

### Windows

```powershell
# 后台启动
Start-Process python -ArgumentList "nvidia_proxy.pyw" -WindowStyle Hidden

# 停止代理
Stop-Process -Name python -Force
```

## 常见问题

### 1. 代理启动失败

**问题**：端口 18080 已被占用

**解决**：修改 `nvidia_proxy.pyw` 第 154 行的端口号：
```python
PORT = 8081  # 改为其他端口
```

同时更新 CC Switch 配置中的请求地址。

### 2. CC Switch 返回 404

**问题**：请求地址配置错误

**解决**：确保请求地址为 `http://127.0.0.1:18080/v1`（注意末尾的 `/v1`）

### 3. NVIDIA API 返回 401

**问题**：API Key 无效或过期

**解决**：访问 [NVIDIA Build](https://build.nvidia.com) 重新生成 API Key

### 4. 响应速度慢

**问题**：NVIDIA API 服务器响应慢

**解决**：
- 尝试切换到更轻量的模型（如 `google/gemma-3-4b-it`）
- 检查网络连接
- NVIDIA API 免费服务可能有速率限制

## 高级配置

### 自定义模型映射

编辑 `MODEL_MAPPING` 字典添加更多模型：

```python
MODEL_MAPPING = {
    "claude-3-5-sonnet-20241022": "qwen/qwen2.5-coder-7b-instruct",
    "claude-3-5-haiku-20241022": "google/gemma-3-4b-it",
    # 添加你的自定义映射
    "my-custom-model": "nvidia/model-name",
}
```

查看所有可用的 NVIDIA 模型：
```bash
curl https://integrate.api.nvidia.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 修改超时时间

编辑第 68 行：
```python
with urllib.request.urlopen(req, timeout=120) as response:  # 改为 120 秒
```

## 安全建议

1. **不要公开分享你的 API Key**
2. **仅在本地使用**：代理默认监听 `127.0.0.1`，不对外网开放
3. **定期更新 API Key**：NVIDIA API Key 有效期为 6 个月
4. **使用环境变量**：生产环境建议使用环境变量存储 API Key

## 限制

- NVIDIA Build 免费 API 有使用限制（具体限制请查看官方文档）
- API Key 有效期为 6 个月
- 部分模型可能不可用或响应较慢
- 不支持流式响应（streaming）

## 相关链接

- [NVIDIA Build](https://build.nvidia.com) - 获取免费 API Key
- [NVIDIA API 文档](https://docs.api.nvidia.com/nim/reference)
- [CC Switch](https://github.com/Yidadaa/ChatGPT-Next-Web) - Claude Code Switch 工具

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2025-01-04)

- 初始版本
- 支持 Claude API 到 OpenAI API 的双向转换
- 支持 CC Switch 集成
- 包含测试脚本
