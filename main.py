"""启动入口 —— 读配置、造客户端、搭界面、点火。

用法（在仓库根目录执行）：
    1. 打开 roleplay/config.py，把密钥粘进 HARDCODED_API_KEY = "" 的引号里
    2. python main.py

密钥也可以走环境变量（export MY_API_KEY=sk-xxx），但文件里填的优先。
可选开关：MY_DEBUG=1 打开请求级日志，MY_PORT=8080 换端口，MY_STREAM=0 关闭流式。
"""

from __future__ import annotations

import logging
import sys

from roleplay import (
    API_KEY,
    BASE_URL,
    DEBUG,
    KEY_SOURCE,
    MODEL,
    SERVER_PORT,
    SHARE_LINK,
    ChatClient,
    LAUNCH_KWARGS,
    build_demo,
    env_key_hint,
    mask_key,
)


def configure_logging(debug: bool) -> None:
    """统一日志格式；MY_DEBUG=1 时降到 DEBUG 级别，方便排查请求内容。"""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> int:
    configure_logging(DEBUG)
    logging.getLogger(__name__).info(
        "密钥来源：%s（%s）", KEY_SOURCE, mask_key(API_KEY)
    )

    try:
        client = ChatClient(api_key=API_KEY, base_url=BASE_URL, model=MODEL)
    except ValueError as exc:
        logger = logging.getLogger(__name__)
        logger.error("%s", exc)
        if hint := env_key_hint():
            logger.info(
                "当前环境里名字含 API_KEY 的变量有：%s。"
                "想用其中哪个，把它的名字加进 config.py 的 API_KEY_ENV_VARS 就行。",
                "、".join(hint),
            )
        return 1

    demo = build_demo(client)
    demo.launch(server_port=SERVER_PORT, share=SHARE_LINK, **LAUNCH_KWARGS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
