#!/usr/bin/env python3
"""
智能体（AI Agent）完善版
功能：
- 真实大模型（Grok / OpenAI 兼容）
- 官方 Function Calling 工具调用
- 对话记忆
- 命令行 + Gradio Web 界面
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==================== 配置 ====================
API_BASE = os.getenv("API_BASE", "https://api.x.ai/v1")
API_KEY = os.getenv("API_KEY") or os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "grok-3")


# ==================== 工具实现 ====================
def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.now()
    weekdays = "一二三四五六日"
    return now.strftime(f"%Y年%m月%d日 %H:%M:%S 星期{weekdays[now.weekday()]}")


def calculate(expression: str) -> str:
    """安全计算数学表达式"""
    try:
        if not re.match(r"^[\d\s\+\-\*\/\(\)\.\^\%]+$", expression.strip()):
            return "错误：表达式包含非法字符，只支持数字和 + - * / ( ) . ^ %"
        expr = expression.replace("^", "**")
        result = eval(expr, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算失败：{e}"


def web_search(query: str) -> str:
    """网络搜索（演示版，可后续接入真实搜索 API）"""
    return (
        f"【搜索「{query}」的结果（演示）】\n"
        "目前为演示模式。要获得真实搜索结果，可接入 SerpAPI / Bing Search / Tavily 等服务。\n"
        "建议下一步：在 .env 中配置 SEARCH_API_KEY 并扩展此函数。"
    )


# OpenAI 格式的 tools 定义（官方 Function Calling）
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间，当用户询问现在几点、今天几号、星期几时调用",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，例如 12*(3+4)、2^10、100/4 等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如 12*(3+4)"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "搜索互联网上的最新信息或知识",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "get_current_time": lambda **kwargs: get_current_time(),
    "calculate": lambda expression, **kwargs: calculate(expression),
    "web_search": lambda query, **kwargs: web_search(query),
}


# ==================== 智能体核心 ====================
class SmartAgent:
    def __init__(self, name: str = "智能体"):
        self.name = name
        self.memory: List[Dict[str, Any]] = []
        self.system_prompt = (
            "你是一个友好、专业、乐于助人的中文智能助手。\n"
            "你可以使用工具来获取实时信息或进行计算。\n"
            "回答时请用清晰、自然的中文，必要时分点说明。\n"
            "如果工具返回的结果是演示/模拟数据，请如实告知用户。"
        )

    def _get_client(self):
        if not API_KEY:
            return None
        from openai import OpenAI
        return OpenAI(api_key=API_KEY, base_url=API_BASE)

    def _call_llm(self, messages: List[Dict], use_tools: bool = True) -> Any:
        """调用大模型，返回完整 response 对象或错误字符串"""
        client = self._get_client()
        if client is None:
            return (
                "【配置提示】尚未设置 API_KEY。\n\n"
                "请按以下步骤配置：\n"
                "1. 复制 .env.example 为 .env\n"
                "2. 填入你的 API_KEY\n"
                "3. 推荐配置（Grok）：\n"
                "   API_KEY=你的密钥\n"
                "   API_BASE=https://api.x.ai/v1\n"
                "   MODEL=grok-3\n\n"
                "配置完成后重新运行即可。"
            )

        try:
            kwargs = {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.7,
            }
            if use_tools:
                kwargs["tools"] = TOOLS_SCHEMA
                kwargs["tool_choice"] = "auto"

            return client.chat.completions.create(**kwargs)
        except Exception as e:
            return f"调用大模型失败：{type(e).__name__}: {e}"

    def chat(self, user_input: str) -> str:
        """核心对话：支持多轮工具调用 + 记忆"""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]

        # 加入历史记忆（最近 8 轮）
        for mem in self.memory[-8:]:
            messages.append({"role": "user", "content": mem["input"]})
            messages.append({"role": "assistant", "content": mem["response"]})

        messages.append({"role": "user", "content": user_input})

        # 第一次调用
        response = self._call_llm(messages)
        if isinstance(response, str):
            self.memory.append({"input": user_input, "response": response})
            return response

        message = response.choices[0].message
        final = message.content or ""

        # 处理工具调用（可能多轮）
        max_tool_rounds = 3
        for _ in range(max_tool_rounds):
            if not getattr(message, "tool_calls", None):
                break

            # 把 assistant 的 tool_calls 消息加入
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # 执行每个工具
            for tc in message.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                func = TOOL_FUNCTIONS.get(name)
                if func:
                    result = func(**args)
                else:
                    result = f"未知工具：{name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)
                })

            # 再次调用模型，让它根据工具结果生成最终回答
            response = self._call_llm(messages, use_tools=True)
            if isinstance(response, str):
                final = response
                break
            message = response.choices[0].message
            final = message.content or final

        if not final:
            final = "抱歉，我暂时无法回答。"

        self.memory.append({"input": user_input, "response": final})
        return final

    def clear_memory(self):
        self.memory.clear()

    def run_cli(self):
        print(f"=== {self.name} 已启动（命令行模式）===")
        print("输入内容开始对话，输入「退出」结束，输入「清空」清除记忆。\n")

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
            if user_input in ["清空", "清除记忆", "clear"]:
                self.clear_memory()
                print(f"{self.name}：已清空对话记忆。\n")
                continue

            reply = self.chat(user_input)
            print(f"{self.name}：{reply}\n")


# ==================== Gradio Web 界面 ====================
def create_web_ui(share: bool = False):
    try:
        import gradio as gr
    except ImportError:
        print("请先安装：pip install gradio")
        return

    agent = SmartAgent("智能体")

    def respond(message: str, history: list):
        if not message or not message.strip():
            return history, ""
        reply = agent.chat(message.strip())
        history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": reply}]
        return history, ""

    def clear_chat():
        agent.clear_memory()
        return [], ""

    with gr.Blocks(
        title="智能体",
        theme=gr.themes.Soft(primary_hue="blue"),
        css=".gradio-container {max-width: 900px !important;}"
    ) as demo:
        gr.Markdown("# 🤖 智能体")
        gr.Markdown("支持真实大模型 · 工具调用（时间 / 计算 / 搜索）· 对话记忆")

        chatbot = gr.Chatbot(
            height=480,
            label="对话",
            show_copy_button=True,
            type="messages"
        )
        with gr.Row():
            msg = gr.Textbox(
                placeholder="输入你的问题，例如：现在几点了？帮我算 15*8+3",
                label="消息",
                lines=2,
                scale=5
            )
            submit_btn = gr.Button("发送", variant="primary", scale=1)

        with gr.Row():
            clear_btn = gr.Button("清空对话")
            gr.Markdown(
                "<small>提示：未配置 API_KEY 时会显示配置说明。"
                "运行 `python agent.py web --share` 可生成公网临时链接。</small>"
            )

        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        submit_btn.click(respond, [msg, chatbot], [chatbot, msg])
        clear_btn.click(clear_chat, None, [chatbot, msg])

    print("正在启动 Web 界面...")
    demo.launch(share=share, server_name="0.0.0.0", show_error=True)


# ==================== 入口 ====================
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if "web" in args:
        share = "--share" in args
        create_web_ui(share=share)
    else:
        agent = SmartAgent("智能体")
        agent.run_cli()
