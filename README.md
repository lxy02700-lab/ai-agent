# 智能体（AI Agent）完善版

支持真实大模型、官方 Function Calling 工具调用、对话记忆、Web 界面。

## 功能

- ✅ 接入真实大模型（Grok / OpenAI 兼容接口）
- ✅ **官方 Function Calling**（比文本解析更稳定）
- ✅ 工具：获取时间、数学计算、网络搜索
- ✅ 对话记忆（最近 8 轮）
- ✅ 命令行模式 + Gradio Web 聊天界面
- ✅ 支持一键生成临时公网链接（`--share`）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# 推荐使用 xAI Grok
API_KEY=你的密钥
API_BASE=https://api.x.ai/v1
MODEL=grok-3

# 或使用 OpenAI
# API_KEY=sk-xxxx
# API_BASE=https://api.openai.com/v1
# MODEL=gpt-4o
```

### 3. 运行

**命令行模式：**
```bash
python agent.py
```
输入「清空」可清除记忆，输入「退出」结束。

**Web 界面（本地）：**
```bash
python agent.py web
```
浏览器打开显示的地址（通常是 http://127.0.0.1:7860）。

**Web 界面 + 公网临时链接：**
```bash
python agent.py web --share
```
会生成一个类似 `https://xxxx.gradio.live` 的链接，可分享给别人临时使用。

## 工具说明

| 工具 | 触发示例 |
|------|----------|
| 获取时间 | 「现在几点了」「今天星期几」 |
| 数学计算 | 「帮我算 12*(3+4)」「2的10次方」 |
| 网络搜索 | 「搜索一下人工智能最新进展」（目前为演示结果） |

## 项目结构

```
ai-agent/
├── agent.py           # 主程序
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 后续可扩展方向

- 接入真实搜索 API（Tavily / SerpAPI / Bing）
- 增加更多工具（天气、文件操作、代码执行等）
- 长期记忆（向量数据库）
- 多 Agent 协作
- 流式输出

有问题随时继续让我帮你改！
