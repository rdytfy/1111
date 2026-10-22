"""界面层 —— Gradio 组件与事件绑定，只跟 ChatClient 打交道，不碰 API 细节。"""

from __future__ import annotations

import inspect
import logging
from collections.abc import Iterator

import gradio as gr

from .config import (
    APP_HEADING,
    APP_SUBTITLE,
    APP_TITLE,
    CHATBOT_HEIGHT,
    CHATBOT_TYPE,
    CLEAR_BUTTON_TEXT,
    DEFAULT_SYSTEM_PROMPT,
    ERROR_EMPTY_REPLY,
    LABEL_MESSAGE,
    LABEL_PRESET,
    LABEL_SYSTEM_PROMPT,
    PLACEHOLDER_SYSTEM_PROMPT,
    SAVE_PRESET_BUTTON_TEXT,
    STREAM,
    THEME,
)
from .llm import ChatClient
from .messages import Message
from .presets import DEFAULT_PRESET_NAME, PRESETS, preset_names, save_preset

logger = logging.getLogger(__name__)

# ------------------------------------------------------------- Gradio 版本适配
# 6.0 改了两处：Chatbot 删掉 type 参数（只剩 messages 格式），
# theme 从 Blocks 构造器搬到了 launch()。下面按签名探测，5.x / 6.x 都能跑。
if "theme" in inspect.signature(gr.Blocks.launch).parameters:
    _BLOCKS_KWARGS: dict[str, object] = {}
    LAUNCH_KWARGS: dict[str, object] = {"theme": THEME}
else:
    _BLOCKS_KWARGS = {"theme": THEME}
    LAUNCH_KWARGS = {}

_CHATBOT_KWARGS: dict[str, object] = (
    {"type": CHATBOT_TYPE}
    if "type" in inspect.signature(gr.Chatbot.__init__).parameters
    else {}
)


def build_demo(client: ChatClient) -> gr.Blocks:
    """搭出整个聊天界面，把事件接到 client 上，返回可 launch 的 Blocks。

    回复默认走流式（config.STREAM 控制）：生成器每收到一段文本就 yield 一次
    完整的消息列表，Gradio 会把它渲染成"文字逐渐长出来"的效果。
    """
    with gr.Blocks(title=APP_TITLE, **_BLOCKS_KWARGS) as demo:
        gr.Markdown(APP_HEADING)
        gr.Markdown(APP_SUBTITLE)

        with gr.Row():
            preset_dropdown = gr.Dropdown(
                choices=preset_names(),
                value=DEFAULT_PRESET_NAME,
                label=LABEL_PRESET,
                allow_custom_value=True,
                scale=3,
            )
            save_preset_btn = gr.Button(SAVE_PRESET_BUTTON_TEXT, scale=1)

        prompt_box = gr.Textbox(
            value="",
            label=LABEL_SYSTEM_PROMPT,
            placeholder=PLACEHOLDER_SYSTEM_PROMPT,
            lines=4,
        )
        preset_status = gr.Markdown("")

        chatbot = gr.Chatbot(height=CHATBOT_HEIGHT, **_CHATBOT_KWARGS)
        msg = gr.Textbox(label=LABEL_MESSAGE)
        clear = gr.Button(CLEAR_BUTTON_TEXT)

        def on_submit(user_message: str, history: list[Message]) -> tuple[str, list[Message]]:
            """用户按下回车：消息立刻上屏，输入框清空。"""
            return "", history + [{"role": "user", "content": user_message}]

        def reply_once(
            history: list[Message], system_prompt: str
        ) -> list[Message]:
            """非流式：等模型说完，一次性上屏。"""
            answer = client.reply(system_prompt or DEFAULT_SYSTEM_PROMPT, history)
            return history + [
                {"role": "assistant", "content": answer or ERROR_EMPTY_REPLY}
            ]

        def reply_stream(
            history: list[Message], system_prompt: str
        ) -> Iterator[list[Message]]:
            """流式：先挂一个空气泡，然后每收到一段就 yield 一次，文字逐字长出来。"""
            answer = ""
            yield history + [{"role": "assistant", "content": answer}]
            for chunk in client.stream(system_prompt or DEFAULT_SYSTEM_PROMPT, history):
                answer += chunk
                yield history + [{"role": "assistant", "content": answer}]
            if not answer.strip():
                yield history + [
                    {"role": "assistant", "content": ERROR_EMPTY_REPLY}
                ]

        def on_clear() -> list[Message]:
            """清空对话。"""
            return []

        def on_preset_change(name: str) -> str:
            """选了预设：把内容填进人设框（填完仍可随手改）。"""
            return PRESETS.get(name, "")

        def on_save_preset(name: str, content: str) -> tuple[dict, str]:
            """把人设框里的内容存成预设，并刷新下拉框选项。"""
            ok, message = save_preset(name, content)
            updated = gr.update(
                choices=preset_names(),
                value=name if ok else DEFAULT_PRESET_NAME,
            )
            return updated, message

        # 生成器必须走队列，所以这一环显式 queue=True
        msg.submit(on_submit, [msg, chatbot], [msg, chatbot], queue=False).then(
            reply_stream if STREAM else reply_once,
            [chatbot, prompt_box],
            chatbot,
            queue=True,
        )
        clear.click(on_clear, None, chatbot, queue=False)

        preset_dropdown.change(on_preset_change, [preset_dropdown], [prompt_box])
        save_preset_btn.click(
            on_save_preset,
            [preset_dropdown, prompt_box],
            [preset_dropdown, preset_status],
        )

    logger.debug("界面组装完成")
    return demo
