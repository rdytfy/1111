"""消息格式工具 —— 把 Gradio 递过来的内容统一压成纯文本。

Gradio 的 content 可能是 [{"type": "text", "text": "你好"}] 这样的列表，
也可能是 "你好" 这样的字符串，而模型接口只认字符串，归一化在这一层做掉。
"""

from __future__ import annotations

from typing import Any

# 一条对话消息：{"role": "user"|"assistant"|"system", "content": ...}
Message = dict[str, Any]


def content_to_text(content: Any) -> str:
    """把一条消息的 content 变成字符串；是列表就把其中所有 text 片段拼起来。"""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    return str(content)


def build_messages(
    system_prompt: str,
    history: list[Message],
    user_message: Any,
) -> list[Message]:
    """拼出真正发给模型的 messages：人设 + 历史对话 + 当前这一句。"""
    messages: list[Message] = [{"role": "system", "content": system_prompt or ""}]
    for item in history:
        messages.append(
            {
                "role": item.get("role", "user"),
                "content": content_to_text(item.get("content")),
            }
        )
    messages.append({"role": "user", "content": content_to_text(user_message)})
    return messages


def last_user_text(history: list[Message]) -> str:
    """取历史里最后一条消息的文本（通常是用户刚发出来的那句）。"""
    if not history:
        return ""
    return content_to_text(history[-1].get("content"))
