#!/usr/bin/env python3
"""
简单智能体示例
可以后续接入真实的大模型 API（如 xAI Grok、OpenAI 等）
"""

from typing import List, Dict


class SimpleAgent:
    def __init__(self, name: str = "我的智能体"):
        self.name = name
        self.memory: List[Dict[str, str]] = []
        self.system_prompt = (
            "你是一个友好、有帮助的智能助手。"
            "请用简洁清晰的中文回答用户的问题。"
        )

    def think(self, user_input: str) -> str:
        """
        当前是模拟思考。
        后续可在这里调用真实 LLM API。
        """
        # 简单规则回复（占位）
        lower = user_input.lower().strip()

        if any(kw in lower for kw in ["你好", "hello", "hi"]):
            response = f"你好！我是 {self.name}，有什么可以帮你的吗？"
        elif any(kw in lower for kw in ["你是谁", "名字"]):
            response = f"我是 {self.name}，一个简单的智能体示例。"
        elif any(kw in lower for kw in ["时间", "日期"]):
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response = f"当前时间是：{now}"
        elif "帮助" in lower or "help" in lower:
            response = (
                "我目前支持：\n"
                "1. 基础对话\n"
                "2. 查询当前时间\n"
                "3. 输入「退出」结束对话\n"
                "后续可以接入大模型实现更强大的能力。"
            )
        else:
            response = (
                f"[{self.name}] 收到你的消息：{user_input}\n"
                "（当前是模拟回复，接入真实大模型后会更智能）"
            )

        # 记录对话
        self.memory.append({
            "input": user_input,
            "response": response
        })
        return response

    def run(self):
        print(f"=== {self.name} 已启动 ===")
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
                print(f"{self.name}：再见，期待下次聊天！")
                break

            reply = self.think(user_input)
            print(f"{self.name}：{reply}\n")


if __name__ == "__main__":
    agent = SimpleAgent("智能体")
    agent.run()
