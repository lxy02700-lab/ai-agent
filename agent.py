#!/usr/bin/env python3
"""
智能体（AI Agent）完整示例
支持：
- 接入真实大模型（Grok / OpenAI 兼容接口）
- 工具调用（时间、计算、网络搜索）
- 对话记忆
- 命令行 + Web 界面
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# 尝试加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ========== 配置 ==========
# 优先使用 Grok（xAI），也兼容 OpenAI
API_BASE = os.getenv("API_BASE", "https://api.x.ai/v1")  # Grok 默认
API_KEY = os.getenv("API_KEY") or os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "grok-3")  # 可改为 gpt-4o 等


# ========== 工具定义 ==========
def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S 星期") + "一二三四五六日"[now.weekday()]


def calculate(expression: str) -> str:
    """安全计算数学表达式，例如 12 * (3 + 4)"""
    try:
        # 只允许安全字符
        if not re.match(r"^[\d\s\+\-\*\/\(\)\.\^\%]+$", expression):
            return "错误：表达式包含非法字符"
        # 简单替换 ^ 为 **
        expression = expression.replace("^", "**")
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"


def web_search(query: str) -> str:
    """简单网络搜索（占位实现，实际可接入搜索 API）"""
    # 这里用模拟结果，真实环境可接入 SerpAPI / Bing / Google 等
    return (
        f"【搜索结果（模拟）】关于「{query}」：\n"
        "1. 相关信息请参考权威来源。\n"
        "2. 如需真实搜索，请配置搜索 API Key。\n"
        "（当前为演示模式）"
    )


# 工具注册表
TOOLS = {
    "get_current_time": {
        "name": "get_current_time",
        "description": "获取当前的日期和时间",
        "parameters": {},
        "function": get_current_time,
    },
    "calculate": {
        "name": "calculate",
        "description": "计算数学表达式，例如 12*(3+4) 或 2^10",
        "parameters": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式"
            }
        },
        "function": calculate,
    },
    "web_search": {
        "name": "web_search",
        "description": "搜索互联网上的信息",
        "parameters": {
            "query": {
                "type": "string",
                "description": "搜索关键词"
            }
        },
        "function": web_search,
    },
}


# ========== 智能体核心 ==========
class SmartAgent:
    def __init__(self, name: str = "智能体"):
        self.name = name
        self.memory: List[Dict[str, str]] = []
        self.system_prompt = (
            "你是一个有用的中文智能助手。你可以调用工具来帮助用户。\n"
            "可用工具：\n"
            "- get_current_time：获取当前时间\n"
            "- calculate：计算数学表达式（参数 expression）\n"
            "- web_search：搜索信息（参数 query）\n\n"
            "如果需要使用工具，请按以下格式回复：\n"
            "TOOL_CALL: 工具名 | 参数名=参数值\n"
            "例如：TOOL_CALL: calculate | expression=12*5\n"
            "如果不需要工具，直接用自然语言回答用户。"
        )

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """调用大模型 API（OpenAI 兼容格式）"""
        if not API_KEY:
            return (
                "【提示】未配置 API_KEY。\n"
                "请在 .env 文件中设置：\n"
                "API_KEY=你的密钥\n"
                "API_BASE=https://api.x.ai/v1   # Grok\n"
                "MODEL=grok-3\n\n"
                "或者设置 OPENAI_API_KEY / XAI_API_KEY。"
            )

        try:
            from openai import OpenAI
            client = OpenAI(api_key=API_KEY, base_url=API_BASE)

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"调用大模型失败：{e}"

    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """解析工具调用格式：TOOL_CALL: 工具名 | 参数=值"""
        match = re.search(r"TOOL_CALL:\s*(\w+)\s*(?:\|\s*(.+))?", text, re.IGNORECASE)
        if not match:
            return None

        tool_name = match.group(1).strip()
        params_str = match.group(2) or ""

        params = {}
        if params_str:
            for part in params_str.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k.strip()] = v.strip()

        return {"name": tool_name, "params": params}

    def _execute_tool(self, tool_name: str, params: Dict[str, str]) -> str:
        """执行工具"""
        tool = TOOLS.get(tool_name)
        if not tool:
            return f"未知工具：{tool_name}"

        func = tool["function"]
        try:
            if tool_name == "get_current_time":
                return func()
            elif tool_name == "calculate":
                return func(params.get("expression", ""))
            elif tool_name == "web_search":
                return func(params.get("query", ""))
            else:
                return func(**params)
        except Exception as e:
            return f"工具执行错误：{e}"

    def chat(self, user_input: str) -> str:
        """核心对话方法（带记忆 + 工具）"""
        # 构建消息
        messages = [{"role": "system", "content": self.system_prompt}]

        # 加入最近记忆（最多保留 10 轮）
        for mem in self.memory[-10:]:
            messages.append({"role": "user", "content": mem["input"]})
            messages.append({"role": "assistant", "content": mem["response"]})

        messages.append({"role": "user", "content": user_input})

        # 第一次调用
        reply = self._call_llm(messages)

        # 检查是否需要调用工具
        tool_call = self._parse_tool_call(reply)
        if tool_call:
            tool_result = self._execute_tool(tool_call["name"], tool_call["params"])
            # 把工具结果再喂给模型，生成最终回答
            messages.append({"role": "assistant", "content": reply})
            messages.append({
                "role": "user",
                "content": f"工具 {tool_call['name']} 的执行结果：{tool_result}\n请根据这个结果用自然语言回答用户。"
            })
            reply = self._call_llm(messages)

        # 保存记忆
        self.memory.append({"input": user_input, "response": reply})
        return reply

    def run_cli(self):
        """命令行模式"""
        print(f"=== {self.name} 已启动（命令行模式）===")
        print("输入内容开始对话，输入「退出」结束。\n")

        while True:
            try:
                user_input = input("你：").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            if not user_input:
                continue
            if user_input.lower() in ["退出", "exit", "quit", "q"]:
                print(f"{self.name}：再见！")
                break

            reply = self.chat(user_input)
            print(f"{self.name}：{reply}\n")


# ========== Web 界面（Gradio）==========
def create_web_ui():
    try:
        import gradio as gr
    except ImportError:
        print("请先安装 gradio：pip install gradio")
        return

    agent = SmartAgent("智能体")

    def respond(message, history):
        if not message.strip():
            return history, ""
        reply = agent.chat(message)
        history = history + [(message, reply)]
        return history, ""

    with gr.Blocks(title="智能体 Web 界面", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🤖 智能体 Web 聊天")
        gr.Markdown("支持真实大模型 + 工具调用 + 对话记忆")

        chatbot = gr.Chatbot(height=500, label="对话")
        msg = gr.Textbox(placeholder="输入你的问题...", label="消息", lines=2)
        clear = gr.Button("清空对话")

        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        clear.click(lambda: ([], ""), None, [chatbot, msg], queue=False)

    demo.launch(share=False, server_name="0.0.0.0")


# ========== 入口 ==========
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "web":
        print("启动 Web 界面...")
        create_web_ui()
    else:
        agent = SmartAgent("智能体")
        agent.run_cli()
