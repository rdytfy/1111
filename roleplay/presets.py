"""人设预设库 —— 所有"角色设定"集中住在这里，可切换、可增删。

数据默认放在仓库根目录的 presets.json：想加人设直接改那个文件，不用碰代码；
文件丢了或者写坏了，自动退回代码里的内置预设，界面照常能跑。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# presets.json 放在仓库根目录（也就是 roleplay/ 的上一级）
PRESET_FILE: Path = Path(__file__).resolve().parent.parent / "presets.json"

DEFAULT_PRESET_NAME: str = "默认助手"

# 兜底用的内置预设：presets.json 读不出来时顶上，保证程序永远不裸奔
BUILTIN_PRESETS: dict[str, str] = {
    DEFAULT_PRESET_NAME: (
        "You are a helpful, respectful and honest assistant. Always answer as "
        "helpfully as possible, while being safe. Your answers should not include "
        "any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content."
    ),
    "猫娘": (
        "你要扮演一只活泼粘人的猫娘，说话带一点「喵」的口吻，"
        "动作、神态、心理活动放在括号里。请始终保持友好得体，不涉及任何不当内容。"
    ),
    "翻译官": (
        "你是一名专业的中英互译官。用户给什么你就译什么，只输出译文、不额外解释；"
        "遇到有歧义的地方，用括号标注另一种可能的译法。"
    ),
}

# 当前生效的预设表。reload_presets() / save_preset() 原地更新它，界面层的引用因此始终最新
PRESETS: dict[str, str] = dict(BUILTIN_PRESETS)


def _read_file() -> dict[str, str]:
    """读 presets.json；任何异常都退化成空字典，绝不把界面搞崩。"""
    if not PRESET_FILE.exists():
        return {}
    try:
        raw = json.loads(PRESET_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("读取 %s 失败（%s），改用内置预设", PRESET_FILE.name, exc)
        return {}
    if not isinstance(raw, dict):
        logger.warning("%s 格式不是字典，改用内置预设", PRESET_FILE.name)
        return {}
    return {str(k): str(v) for k, v in raw.items() if str(k).strip()}


def reload_presets() -> dict[str, str]:
    """从 presets.json 重新载入；文件有问题就退回内置预设。原地更新 PRESETS。"""
    data = _read_file() or dict(BUILTIN_PRESETS)
    PRESETS.clear()
    PRESETS.update(data)
    logger.debug("已载入 %d 个人设预设", len(PRESETS))
    return PRESETS


def save_preset(name: str, content: str) -> tuple[bool, str]:
    """把当前人设写回 presets.json，并立刻刷新内存里的预设表。

    返回 (是否成功, 给用户看的一句话)。
    """
    name = (name or "").strip()
    content = (content or "").strip()
    if not name:
        return False, "先给这个预设起个名字，再点保存～"
    if not content:
        return False, "人设内容还是空的，写点什么再保存吧。"

    data = _read_file() or dict(BUILTIN_PRESETS)
    data[name] = content
    try:
        PRESET_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        logger.warning("写入 %s 失败: %s", PRESET_FILE.name, exc)
        return False, f"写入 {PRESET_FILE.name} 失败: {exc}"

    reload_presets()
    return True, f"已保存「{name}」，下拉框里可以直接切换。"


def preset_names(presets: dict[str, str] | None = None) -> list[str]:
    """下拉框要的选项列表。"""
    return list(PRESETS.keys() if presets is None else presets.keys())


def default_prompt() -> str:
    """默认人设文本（人设框留空时用它兜底）。"""
    return PRESETS.get(DEFAULT_PRESET_NAME) or BUILTIN_PRESETS[DEFAULT_PRESET_NAME]


reload_presets()
