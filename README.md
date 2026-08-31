# 智能体（AI Agent）完整示例

支持真实大模型、工具调用、对话记忆、Web 界面。

## 功能

- ✅ 接入真实大模型（Grok / OpenAI 兼容接口）
- ✅ 工具调用：获取时间、数学计算、网络搜索
- ✅ 对话记忆（记住上下文）
- ✅ 命令行模式 + Web 聊天界面（Gradio）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制示例文件并填入密钥：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
API_KEY=你的密钥
API_BASE=https://api.x.ai/v1
MODEL=grok-3
```

> 也支持 OpenAI：把 `API_BASE` 改成 `https://api.openai.com/v1`，`MODEL` 改成 `gpt-4o` 即可。

### 3. 运行

**命令行模式：**
```bash
python agent.py
```

**Web 界面模式：**
```bash
python agent.py web
```

浏览器打开提示的地址即可聊天。

## 工具说明

| 工具 | 功能 | 示例 |
|------|------|------|
| `get_current_time` | 获取当前时间 | 直接问「现在几点了」 |
| `calculate` | 数学计算 | 「帮我算 12 * (3+4)」 |
| `web_search` | 搜索信息 | 「搜索一下人工智能最新进展」 |

## 项目结构

```
ai-agent/
├── agent.py           # 智能体主程序
├── requirements.txt   # 依赖
├── .env.example       # 环境变量示例
├── .gitignore
└── README.md
```

## 后续可扩展

- 接入真实搜索 API（SerpAPI、Bing 等）
- 增加更多工具（文件读写、代码执行等）
- 多 Agent 协作
- 长期记忆（向量数据库）

有问题随时继续让我帮你改！
