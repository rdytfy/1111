"""配置中心 —— 项目里所有"想改就能改"的旋钮都住在这一个文件里。

换模型、换接口地址、改默认人设、调端口、开调试日志，都只动这里，
其它模块一行都不用碰。

支持的环境变量：
    密钥    见下面 API_KEY_ENV_VARS，按顺序找第一个有值的（不限定某一个名字）
    MY_BASE_URL 选填，接口地址，默认 https://api.deepseek.com
    MY_MODEL    选填，模型名，默认 deepseek-chat
    MY_DEBUG    选填，设为 1 打开调试日志
    MY_PORT     选填，服务端口，默认 7860
    MY_SHARE    选填，设为 1 生成公网分享链接
    MY_STREAM   选填，设为 0 关闭流式输出
"""

from __future__ import annotations

import os

from .presets import DEFAULT_PRESET_NAME, default_prompt


# =================================================================== 填密钥
# 方式一（最省事）：把密钥直接粘进下面这对引号里，保存就生效，不用碰终端。
# 例：HARDCODED_API_KEY = "sk-1234567890abcdef"
# 注意：一旦把密钥写进文件，就别把这个仓库推到公开的 GitHub 上了。
HARDCODED_API_KEY: str = ""

# 方式二：让程序去环境变量里找。下面这张名单按顺序扫描，谁先有值就用谁。
# 你的密钥叫别的名字？直接往列表里加一行就行，比如 "DEEPSEEK_API_KEY"、
# "OPENAI_API_KEY"、"DASHSCOPE_API_KEY"，顺序越靠前优先级越高。
API_KEY_ENV_VARS: list[str] = [
    
    "MY_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "API_KEY",
]

# 只认上面这张名单，不会去猜别的变量（免得误抓 xxx_API_KEY_DISABLED 这类开关）


def _env_flag(name: str, default: bool = False) -> bool:
    """把 "1" / "true" / "yes" / "on" 这类环境变量读成布尔值。"""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_env_key() -> tuple[str, str]:
    """按 API_KEY_ENV_VARS 的顺序找第一个非空的环境变量，返回 (值, 变量名)。"""
    for name in API_KEY_ENV_VARS:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value, name
    return "", ""


def env_key_hint() -> list[str]:
    """列出当前环境里名字含 API_KEY 的变量名（只用于提示，不会拿它当密钥用）。"""
    return sorted(name for name in os.environ if "API_KEY" in name.upper())


def mask_key(key: str) -> str:
    """把密钥打码后再打日志，别把整串钥匙印在终端上。"""
    if not key:
        return "(空)"
    if len(key) <= 10:
        return key[:2] + "*" * max(len(key) - 2, 1)
    return f"{key[:6]}{'*' * 6}{key[-4:]}"


_KEY_FROM_ENV, _KEY_ENV_NAME = _read_env_key()

# ------------------------------------------------------------------ 模型服务
# 优先级：config.py 里手填的 HARDCODED_API_KEY > 环境变量（按上面的名单找）
API_KEY: str = HARDCODED_API_KEY or _KEY_FROM_ENV

if HARDCODED_API_KEY:
    KEY_SOURCE: str = "config.py 里的 HARDCODED_API_KEY"
elif _KEY_ENV_NAME:
    KEY_SOURCE: str = f"环境变量 {_KEY_ENV_NAME}"
else:
    KEY_SOURCE: str = "没找到（去 config.py 填，或把你的变量名加进 API_KEY_ENV_VARS）"
BASE_URL: str = os.environ.get("MY_BASE_URL", "https://api.deepseek.com")
MODEL: str = os.environ.get("MY_MODEL", "deepseek-chat")

# ------------------------------------------------------------------ 默认人设
# 人设框留空时用它兜底；内容取自 presets.json 的「默认助手」
DEFAULT_SYSTEM_PROMPT: str = default_prompt()

# ------------------------------------------------------------------ 界面文案
APP_TITLE: str = "给你们的小玩具，可以角色扮演，人设自由输入"
APP_HEADING: str = "# 角色扮演"
APP_SUBTITLE: str = "在这里，你可以和你想要的角色对话，只要输入 ta 的人设即可"
LABEL_PRESET: str = "人设预设（选一个，或直接在下面自己写）"
LABEL_SYSTEM_PROMPT: str = "在这里输入人设（随意改），不填就是默认设定"
PLACEHOLDER_SYSTEM_PROMPT: str = "你可以在这里输入任何设定"
LABEL_MESSAGE: str = "输入你想说的话，按回车发送，动作可以写在括号里"
CLEAR_BUTTON_TEXT: str = "清空对话"
SAVE_PRESET_BUTTON_TEXT: str = "把上面这段人设存成预设"
CHATBOT_HEIGHT: int = 400
CHATBOT_TYPE: str = "messages"
# 界面主题。可选：default / soft / glass / monochrome / origin / citrus / ocean / mario
THEME: str = "glass"

# ------------------------------------------------------------------ 运行开关
DEBUG: bool = _env_flag("MY_DEBUG")
SERVER_PORT: int = int(os.environ.get("MY_PORT", "7860"))
SHARE_LINK: bool = _env_flag("MY_SHARE")
# 流式输出（一个字一个字往外蹦）。MY_STREAM=0 可退回"憋完整段再显示"
STREAM: bool = _env_flag("MY_STREAM", default=True)

# ------------------------------------------------------------------ 提示文案
ERROR_NO_API_KEY: str = (
    "还没填密钥。最快的办法：打开 roleplay/config.py，把密钥粘进 "
    "HARDCODED_API_KEY = \"\" 的引号里保存；或者设置下面任意一个环境变量（按此顺序查找）："
    + "、".join(API_KEY_ENV_VARS)
    + "。环境变量叫什么名字可以在 config.py 的 API_KEY_ENV_VARS 里改。"
)
ERROR_EMPTY_REPLY: str = "(网络开小差了，请重试)"
