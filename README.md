# 简单智能体（AI Agent）示例

这是一个基础的智能体项目模板，适合快速上手。

## 功能
- 接收用户输入
- 简单对话循环
- 可扩展接入真实大模型 API（Grok / OpenAI 等）
- 预留工具调用接口

## 文件结构
```
ai-agent/
├── README.md          # 项目说明
├── agent.py           # 智能体主程序
├── requirements.txt   # 依赖（后续扩展用）
└── .gitignore
```

## 快速开始

1. 进入目录：
   ```bash
   cd ai-agent
   ```

2. 运行：
   ```bash
   python agent.py
   ```

3. 输入内容与智能体对话，输入 `退出` 结束。

## 后续可扩展方向
1. 接入真实 LLM API（推荐 Grok API 或 OpenAI）
2. 添加工具调用（搜索、计算、文件读写等）
3. 加入长期记忆（向量数据库）
4. 支持多 Agent 协作
5. 做成 Web 界面或 API 服务

有需要我可以继续帮你扩展这个项目。
