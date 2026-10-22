# 角色扮演聊天玩具

一个 Gradio + DeepSeek 的小玩具：人设自由输入、回复逐字流式上屏、人设可存成预设随时切换。

- 流式输出：文字一个字一个字长出来
- 人设预设：下拉框切换，还能把当前人设存成新预设
- 模块化分层：改模型 / 改文案 / 改界面互不干扰

---

## 一、三步跑起来

```bash
# 1. 装依赖（建议 Python 3.10+）
pip install -r requirements.txt

# 2. 填密钥 —— 见下一节，改一个 .py 文件就行，不用碰终端

# 3. 启动
python main.py
```

启动后浏览器打开终端里打印的地址（默认 <http://localhost:7860>）。

> **Gradio 版本**：5.x 和 6.x 都能跑。6.0 把 `Chatbot` 的 `type` 参数删了、把 `theme` 从 `Blocks` 搬到了 `launch()`，
> `roleplay/ui.py` 顶部会按签名自动判断该往哪儿传，你不用管。详见第六章最后一条。

---

## 二、API 密钥怎么填（重点：直接改 .py 文件）

> 不用配环境变量，不用在终端敲命令。改一行 Python，保存即可。

用任意编辑器打开 **`roleplay/config.py`**，找到开头这一段：

```python
# =================================================================== 填密钥
# 最常用的方式：把你的密钥直接粘进下面这对引号里，保存就生效，不用折腾终端。
# 例：HARDCODED_API_KEY = "sk-1234567890abcdef"
# 留空的话，程序会再去环境变量 MY_API_KEY 里找。
HARDCODED_API_KEY: str = ""
```

把密钥粘进引号里，保存：

```python
HARDCODED_API_KEY: str = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"   # ← 你的真实密钥
```

然后重新运行 `python main.py` 即可。**密钥是在程序启动时读取的，改完必须重启才生效。**

### 优先级

| 顺序 | 填写方式 | 说明 |
| --- | --- | --- |
| 1 | `roleplay/config.py` 里的 `HARDCODED_API_KEY` | **最高**，填了就用它 |
| 2 | 环境变量（按 `API_KEY_ENV_VARS` 名单找） | 文件里留空时才会去找 |
| 3 | 都没填 | 启动时报错、并列出环境里可用的变量名，不会静默失败 |

也就是说：**只要文件里填了，环境变量怎么设都不影响**，改文件永远立刻生效。

### 环境变量叫什么名字都可以

你的密钥不一定叫 `MY_API_KEY`。打开 `config.py` 就能看到这张**候选名单**，程序按顺序扫描，谁先有值就用谁：

```python
# 你的密钥叫别的名字？直接往列表里加一行就行，比如 "DEEPSEEK_API_KEY"、
# "OPENAI_API_KEY"、"DASHSCOPE_API_KEY"，顺序越靠前优先级越高。
API_KEY_ENV_VARS: list[str] = [
    "MY_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "API_KEY",
]
```

**加一行就完事**，比如你的变量叫 `DASHSCOPE_API_KEY`：

```python
API_KEY_ENV_VARS: list[str] = [
    "DASHSCOPE_API_KEY",   # ← 加在最前面，优先级最高
    "MY_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "API_KEY",
]
```

启动时终端会打印一行**「密钥来源」**，一眼就能确认到底用上了哪个（密钥打码显示，不会泄露）：

```
[INFO] app: 密钥来源：环境变量 DEEPSEEK_API_KEY（sk-dee******3456）
```

> 程序**不会**自作主张去猜别的变量——环境里常有 `xxx_API_KEY_DISABLED` 这类开关，误取会出事。
> 找不到时它会把环境里所有名字含 `API_KEY` 的变量名**列出来供你抄进名单**，但不擅自使用。

<details>
<summary>可选：临时在终端里设环境变量（只对当前窗口有效）</summary>

```bash
# Windows CMD
set DEEPSEEK_API_KEY=sk-xxxxxxxx
# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-xxxxxxxx"
# macOS / Linux / Git Bash
export DEEPSEEK_API_KEY=sk-xxxxxxxx
```
</details>

### 安全提醒

- 密钥一旦写进 `config.py`，就**别把这个仓库 push 到公开的 GitHub**——别人能看到你的密钥。
- 要公开仓库，请用环境变量方式，或 push 前把引号里的密钥清空。
- 万一密钥泄露，去 DeepSeek 控制台**立刻吊销重新生成一个**。

---

## 三、人设预设

人设都存在仓库根目录的 **`presets.json`** 里，内置三个：

| 预设名 | 说明 |
| --- | --- |
| 默认助手 | 人设框留空时的兜底人设 |
| 猫娘 | 活泼粘人，动作写在括号里 |
| 翻译官 | 中英互译，只输出译文 |

**两种改法：**

1. 直接编辑 `presets.json`（标准 JSON，键是预设名，值是人设内容）：
   ```json
   {
     "默认助手": "You are a helpful assistant...",
     "我的角色": "把你的新人设写在这里"
   }
   ```
2. 在界面上改：下拉框里**敲一个新名字**（下拉框支持手输），在人设框里写好内容，点「把上面这段人设存成预设」——自动写回 `presets.json` 并出现在下拉列表里。

> `presets.json` 丢了或写坏了也没关系，程序会自动退回代码里的内置预设，界面照常能跑。

---

## 四、目录结构

```
DS-roleplay/
├── main.py             启动入口（读配置 → 造客户端 → 搭界面 → launch）
├── presets.json        人设预设数据，随手改
├── requirements.txt
└── roleplay/
    ├── __init__.py     统一导出
    ├── config.py       ★ 密钥和所有配置都在这里
    ├── presets.py      预设的读写与回退逻辑
    ├── messages.py     消息格式归一化
    ├── llm.py          模型客户端（流式 / 非流式）
    └── ui.py           Gradio 界面与事件
```

依赖方向严格单向：`presets → config → messages → llm → ui → main.py`，改任何一层都不会牵动上游。

---

## 五、可选环境变量怎么改

都是选填，不配也能跑。**每个开关都有两种改法**：

- **改法 A（推荐）**：改 `roleplay/config.py` 里的默认值 → 永久生效
- **改法 B**：在终端里临时设 → 只对当前窗口有效

> ⚠️ **优先级：终端设的值 > 文件里的默认值。**（跟第二章的密钥是反的——密钥是"文件优先"。）
> 所以如果你在终端设过某个值，之后改文件会被它盖掉。
> **不管用哪种改法，都要重启 `python main.py` 才生效。**

### 先找到地方：`roleplay/config.py` 的「运行开关」段

```python
# ------------------------------------------------------------------ 运行开关
DEBUG: bool = _env_flag("MY_DEBUG")
SERVER_PORT: int = int(os.environ.get("MY_PORT", "7860"))
SHARE_LINK: bool = _env_flag("MY_SHARE")
STREAM: bool = _env_flag("MY_STREAM", default=True)
```

一句话总览：

| 想改的东西 | config.py 里叫 | 环境变量名 | 默认值 |
| --- | --- | --- | --- |
| 端口 | `SERVER_PORT` | `MY_PORT` | `7860` |
| 调试日志 | `DEBUG` | `MY_DEBUG` | 关 |
| 公网分享 | `SHARE_LINK` | `MY_SHARE` | 关 |
| 流式输出 | `STREAM` | `MY_STREAM` | **开** |
| 模型名 | `MODEL` | `MY_MODEL` | `deepseek-chat` |
| 接口地址 | `BASE_URL` | `MY_BASE_URL` | `https://api.deepseek.com` |
| 界面主题 | `THEME` | 无（只能改文件） | `glass` |

---

### 5.0 最短路径（只想改一个值，不想看原理）

以"把端口从 7860 改成 8080"为例，三步：

1. 用记事本 / VS Code 打开 **`roleplay\config.py`**
2. 找到这一行，把引号里的 `7860` 改成 `8080`，**保存**：
   ```python
   SERVER_PORT: int = int(os.environ.get("MY_PORT", "7860"))
   ```
3. 关掉正在运行的程序，重新 `python main.py`

其余五个开关都是同一个套路：找到那一行 → 改引号里的默认值（开关类的补个 `default=True/False`）→ 保存 → 重启。下面 5.1～5.6 逐个给了现成的例子，照抄即可。

---

### 5.1 端口（端口被占用时改这个）

**改法 A**：把 `"7860"` 换成别的数字

```python
SERVER_PORT: int = int(os.environ.get("MY_PORT", "8080"))   # ← 改成 8080
```

**改法 B（临时）**：

```bash
set MY_PORT=8080        # Windows CMD
$env:MY_PORT="8080"     # Windows PowerShell
export MY_PORT=8080     # macOS / Linux / Git Bash
```

**怎么确认改成功了**：启动后终端会打印 `Running on local URL: http://127.0.0.1:8080`。

---

### 5.2 调试日志（出问题要排错时打开）

**改法 A**：在括号里补上 `default=True`

```python
DEBUG: bool = _env_flag("MY_DEBUG", default=True)   # ← 加了 default=True
```

**改法 B（临时）**：`set MY_DEBUG=1`

**开了能看到什么**：每次请求几条消息、回复多少字；出错时打印完整报错堆栈。排完错记得改回 `False`。

---

### 5.3 流式输出（想让回复整段出现就关掉）

默认是**开**的（一个字一个字往外蹦）。

**改法 A**：把 `default=True` 改成 `default=False`

```python
STREAM: bool = _env_flag("MY_STREAM", default=False)   # ← 关掉流式
```

**改法 B（临时）**：`set MY_STREAM=0`

---

### 5.4 公网分享链接（要发给别人用时才开）

**改法 A**：`SHARE_LINK: bool = _env_flag("MY_SHARE", default=True)`

**改法 B（临时）**：`set MY_SHARE=1`

开了之后终端会多打印一个 `https://xxx.gradio.live` 的公网地址，任何人都能访问你本机这个界面。
默认关着，用完建议关回去。

---

### 5.5 换模型

**改法 A**：把引号里的模型名换掉

```python
MODEL: str = os.environ.get("MY_MODEL", "deepseek-reasoner")   # ← 换成你要的模型
```

**改法 B（临时）**：`set MY_MODEL=deepseek-reasoner`

---

### 5.6 换接口地址（换服务商时用）

**改法 A**：

```python
BASE_URL: str = os.environ.get("MY_BASE_URL", "https://你的服务商地址/v1")
```

**改法 B（临时）**：`set MY_BASE_URL=https://...`

> 换服务商时，**地址、密钥、模型名这三个要配套一起换**，只换一个会报错。

---

### 5.7 换界面主题

主题写在 `roleplay/config.py` 的「界面文案」段，**只能改文件**，没有对应的环境变量：

```python
THEME: str = "glass"      # ← 换成下面任意一个
```

可选的现成主题名（Gradio 内置）：

| 名字 | 观感 |
| --- | --- |
| `default` | 默认，白底简洁 |
| `soft` | 柔和圆角，偏"果冻感" |
| `glass` | 玻璃拟态（当前用的这个） |
| `monochrome` | 黑白极简 |
| `origin` | 带一点复古配色 |
| `citrus` | 橙黄明亮 |
| `ocean` | 蓝青冷色 |
| `mario` | 红黄撞色 |

填错了不会崩，只会退回默认主题。

---

### 5.8 开关类变量（DEBUG / SHARE / STREAM）怎么写值

| 意思 | 可以写成 |
| --- | --- |
| 开 | `1`、`true`、`yes`、`on` |
| 关 | `0`、`false`、`no`、`off`、留空 |

大小写不敏感，`True`、`YES`、`On` 都认。

---

### 5.9 想让终端的改动永久生效

| 系统 | 做法 |
| --- | --- |
| Windows CMD | `setx MY_PORT 8080`（**要重开一个终端窗口**才生效） |
| Windows 图形界面 | 此电脑 → 属性 → 高级系统设置 → 环境变量 → 新建 |
| macOS / Linux | 把 `export MY_PORT=8080` 写进 `~/.bashrc` 或 `~/.zshrc`，再执行 `source ~/.bashrc` |

不过既然改法 A 本来就是永久的，一般没必要折腾这个。

---

### 5.10 改了没反应？按顺序自查

1. **重启了吗？** 配置只在程序启动时读一次。
2. **终端里是不是设过同名变量？** 它会盖掉文件里的值。Windows 用 `set MY_PORT=` 清空，macOS/Linux 用 `unset MY_PORT`。
3. **数字类填了非数字**：`SERVER_PORT` 必须是纯数字，写 `"8080"` 或 `8080` 都行，写成 `"八千"` 会直接崩。
4. **开关类写了无效值**：只有 5.8 那张表里的写法才认，写 `MY_DEBUG=是` 不生效。

---

## 六、常见问题

**启动时报「还没填密钥」** → 打开 `roleplay/config.py`，密钥没粘进 `HARDCODED_API_KEY` 的引号里，或者粘完没重启。
同时看一眼终端打印的「密钥来源」，以及下面那行「当前环境里名字含 API_KEY 的变量有：…」——想用哪个，把它的名字加进 `API_KEY_ENV_VARS` 就行。

**回复显示「哎呀，出错了: ...」** → 一般是密钥无效、余额不足或网络不通；按 5.2 打开调试日志看完整报错。

**端口被占用** → 按 5.1 把端口改成 `8080` 之类的空闲端口。

**想换模型** → 按 5.5 改。

**回复不是逐字冒出来的** → 按 5.3 确认 `STREAM` 是不是被关了（或 `MY_STREAM=0`）。

**改了配置没生效** → 看 5.10 的自查清单（多半是没重启，或者终端里的同名变量盖掉了文件里的值）。

---

### 关于 Gradio 6.0 的报错（已修好，留个记录）

如果你在旧版本代码里见过这两条，是 Gradio 从 5.x 升到 6.0 的破坏性改动：

```
TypeError: Chatbot.__init__() got an unexpected keyword argument 'type'
UserWarning: The parameters have been moved from the Blocks constructor to the launch() method in Gradio 6.0: theme
```

| 6.0 改了什么 | 现在的写法 |
| --- | --- |
| `gr.Chatbot(type="messages")` 的 `type` 参数被删（只剩 messages 一种格式） | `ui.py` 先看签名里有没有 `type`，有才传，没有就不传 |
| `gr.Blocks(theme=...)` 的 `theme` 搬到了 `demo.launch(theme=...)` | `ui.py` 判断该往哪传，`main.py` 用 `**LAUNCH_KWARGS` 接上 |
| 返回组件实例当更新（`gr.Dropdown(...)`）的老写法 | 换成官方写法 `gr.update(choices=..., value=...)` |

所以你**不需要降级 gradio**，也不用改任何代码，`pip install -r requirements.txt` 装到的版本直接能跑（本机实测 6.30.0：页面 HTTP 200、主题 glass 生效、流式与非流式均正常）。
