"""roleplay —— 一个可以自定义人设的角色扮演聊天玩具。

分层结构（依赖方向严格自上而下，不会出现循环引用）：

    presets    人设预设库（读写仓库根目录的 presets.json）
      ↓
    config     配置常量（改这里就能换模型 / 换文案 / 换端口）
      ↓
    messages   消息格式归一化（Gradio 格式 ↔ 模型格式）
      ↓
    llm        模型客户端（发请求、收回复、兜住异常）
      ↓
    ui         Gradio 界面（组件 + 事件绑定）

main.py 是唯一的装配与启动入口。
"""

from .config import (
    API_KEY,
    API_KEY_ENV_VARS,
    APP_TITLE,
    BASE_URL,
    DEBUG,
    DEFAULT_SYSTEM_PROMPT,
    ERROR_NO_API_KEY,
    KEY_SOURCE,
    MODEL,
    SERVER_PORT,
    SHARE_LINK,
    THEME,
    env_key_hint,
    mask_key,
)
from .llm import ChatClient
from .messages import Message, content_to_text
from .presets import DEFAULT_PRESET_NAME, PRESETS, preset_names, save_preset
from .ui import LAUNCH_KWARGS, build_demo

__all__ = [
    "API_KEY",
    "API_KEY_ENV_VARS",
    "APP_TITLE",
    "BASE_URL",
    "DEBUG",
    "DEFAULT_SYSTEM_PROMPT",
    "ERROR_NO_API_KEY",
    "KEY_SOURCE",
    "MODEL",
    "SERVER_PORT",
    "SHARE_LINK",
    "THEME",
    "env_key_hint",
    "mask_key",
    "ChatClient",
    "Message",
    "DEFAULT_PRESET_NAME",
    "LAUNCH_KWARGS",
    "PRESETS",
    "build_demo",
    "content_to_text",
    "preset_names",
    "save_preset",
]
