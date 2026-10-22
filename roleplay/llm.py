"""大模型客户端 —— 只负责"把话说出去、把回答拿回来"，完全不认识界面。

想换服务商？改 config.py 里的 BASE_URL / MODEL 就够了，这个文件不用动。
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Sequence

from openai import OpenAI

from .config import BASE_URL, ERROR_NO_API_KEY, MODEL
from .messages import Message, build_messages, last_user_text

logger = logging.getLogger(__name__)


class ChatClient:
    """OpenAI 兼容接口的一层薄封装，DeepSeek / OpenAI / 其它兼容服务都能套。"""

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        model: str = MODEL,
    ) -> None:
        if not api_key:
            raise ValueError(ERROR_NO_API_KEY)
        self.model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def _payload(self, system_prompt: str, history: Sequence[Message]) -> list[Message]:
        """把人设 + 历史拼成模型认识的 messages（最后一条历史是用户刚发的）。"""
        return build_messages(system_prompt, list(history[:-1]), last_user_text(history))

    def stream(
        self,
        system_prompt: str,
        history: Sequence[Message],
    ) -> Iterator[str]:
        """流式回复：一收到文本片段就 yield 出去，调用方可以边收边显示。

        出错时不往外抛异常，而是把错误翻译成一句能直接显示给用户的话，
        免得整个界面因为一次网络抖动就崩掉。
        """
        payload = self._payload(system_prompt, history)
        logger.debug("准备发起流式请求，共 %d 条消息", len(payload))

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=payload,
                stream=True,
            )
            for chunk in response:
                # 流式最后一个分片可能只带 usage，choices 会为空，所以要挡一下
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:  # 网络抖动、密钥失效、限流……全归到这里
            logger.exception("流式调用模型接口失败")
            yield f"哎呀，出错了: {exc}"

    def reply(self, system_prompt: str, history: Sequence[Message]) -> str:
        """一次性回复：等模型说完再整体返回（流式版之上包一层即可）。"""
        answer = "".join(self.stream(system_prompt, history))
        logger.debug("收到完整回复，共 %d 个字符", len(answer))
        return answer
