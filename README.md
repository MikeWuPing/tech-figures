<a id="top"></a>

# tech-figures

**用 HTML/CSS 给技术文章画配图 —— 不写绘图代码算坐标，排版交给浏览器。**

**Draw technical figures with HTML/CSS — let the browser do the layout.**

一个 [Agent Skill](https://agentskills.io) · 装好之后跟 AI 说一句话就行，不用敲命令。
An [Agent Skill](https://agentskills.io) · Install it, then just ask your agent. No CLI required.

[中文](#中文) · [English](#english) · [↑ Top](#top)

---

<a id="中文"></a>

## 中文

[English](#english) · [↑ Top](#top)

### 这是什么

一个遵循 **[Agent Skills](https://agentskills.io)** 开放标准的 Skill，用来给技术文章做配图。

**它不是给你敲命令的 CLI 工具。** 装进 AI 客户端之后，配图这件事就变成一句对话——
你描述要什么、看图后说哪里不对，剩下的（建目录、写模板、渲染、逐张检查）AI 自己做。

这里面的 Python 脚本是**给 AI 用的工具**，不是给你用的命令行。

### 兼容哪些客户端

凡是支持 Agent Skills 标准的都能用，包括但不限于：

| 客户端 | 技能目录 |
|---|---|
| **Claude Code** | `~/.claude/skills/` 或 `<项目>/.claude/skills/` |
| **OpenClaw** | `~/.openclaw/skills/` 或 `<工作区>/skills/` |
| **通用目录**（Codex CLI、Gemini CLI、GitHub Copilot、OpenCode、Amp、Kimi Code CLI 等共用） | `~/.agents/skills/` |

OpenClaw 遵循同一标准，其 skill 是本标准的**超集**——本 skill 不含任何客户端专属字段，
所以在哪边都能用。触发方式、加载时机由各客户端自己决定。

### 安装

**通用方式**（自动识别本机的 AI 客户端并全部链接过去）：

```bash
npx skills add MikeWuPing/tech-figures
```

**手动装到某个客户端**（改路径即可）：

```bash
# Claude Code（用户级）
git clone https://github.com/MikeWuPing/tech-figures.git ~/.claude/skills/tech-figures

# Claude Code（项目级，团队共享）
git clone https://github.com/MikeWuPing/tech-figures.git <项目>/.claude/skills/tech-figures

# OpenClaw
git clone https://github.com/MikeWuPing/tech-figures.git ~/.openclaw/skills/tech-figures

# 通用目录（多个客户端共用一份）
git clone https://github.com/MikeWuPing/tech-figures.git ~/.agents/skills/tech-figures
```

装完**开个新会话**让它被发现（Claude Code 用 `/clear` 或重开；OpenClaw 可
`openclaw gateway restart`）。

### 怎么用

装好之后**不用敲任何命令**，直接对 AI 说：

> 帮我给这篇文章配图，深色风格，图要和正文对得上

> 这篇文章里的配图太简陋了，换成更精致的版本

> 给这篇文章做一张知乎封面，横版

> 这几张图的底纹太亮了，压暗一点再看看

> 把 `figs/` 下那批 matplotlib 画的图迁移过来

AI 拿到任务后会自己走完这一串：

1. 读本 skill 的说明（设计系统、组件、铁律）
2. 探环境（Chrome、playwright、中文字体、可选的 ComfyUI）
3. 在项目里铺开工具链，建 `fig/t/` 和 `fig/_asset/`
4. 写 HTML 模板
5. 渲染成 PNG，**逐张看图检查**
6. 有溢出、重叠、连线没画出来就改了重渲

**你只需要做两件事**：说清楚要什么，以及看完图后指出哪里不对。

第一次在某个项目里用时它会自动铺开工具链，之后一直复用。

### 它能画出什么

| 组件 | 用途 |
|---|---|
| 磨砂玻璃面板 | 带顶边高光和三层阴影的容器 |
| 节点方块 | 一颗芯片 / 一个模块 / 一个环节 |
| 对照矩阵 | 多方规格表，支持整列 / 整行高亮 |
| 分层剖面 | 堆叠结构、封装层次 |
| 标尺 | 量级、间距、时间轴 |
| 说明条 | 结论与要点 |
| 连线 | 按元素自动布线，横平竖直 |
| 封面版式 | 16:9，左侧压暗放标题 |

**用色语义**（三者不要混用）：

| 颜色 | 含义 |
|---|---|
| 蓝 | 本代 / 主角 / 新方案 |
| 暖（琥珀） | 对照方 / 上一代 / 竞品 |
| 红 | 代价 / 警示 |

### 为什么不用 matplotlib

用 matplotlib 画示意图，你得**在脑子里维护一张坐标系**：每个方块放在第几行第几列、
文字多长会不会溢出、箭头从哪连到哪。图画得越复杂，这张脑内坐标系越难维护。

换到 HTML/CSS 之后：

| | matplotlib / PIL | HTML + CSS |
|---|---|---|
| 排版 | 手算坐标 | flex / grid，浏览器算 |
| 文字溢出 | 常见，要反复调 | 容器自己撑开，不会发生 |
| 磨砂玻璃 | 画不出 | `backdrop-filter` 原生支持 |
| 阴影 | 近似 | 多层 `box-shadow`，含内阴影高光 |
| 字体 | 有限 | 系统全部字体，字距行高随意调 |
| 连线 | 手算端点 | 按元素布线 |
| 改版 | 改代码重跑 | 改 CSS，全部生效 |

### 六条铁律

按踩过的坑的严重程度排，都写进了 skill，AI 会自己遵守：

1. **图内不出现「图 N」编号** —— 作者要能自由调整图片顺序
2. **从旧图迁移时内容一字不漏** —— 图变好看了但少了内容，价值反而下降
3. **图里的数值必须和正文对得上** —— 正文改了图没跟上就是自相矛盾
4. **厂商内部块名换成功能性描述** —— 写它做什么，不写它叫什么
5. **AI 生成的字一个都不能用** —— 模型会长出伪文字，图内所有文字由代码叠加
6. **不声称 AI 生成图是实物** —— 标「示意图」，不标「摄影」

### 底图从哪来

三条路，没有哪条是必须的：

| 来源 | 说明 |
|---|---|
| **本地 ComfyUI** | 构图色调可控；skill 内置 HTTP API 调用器 |
| **公有领域照片** | Wikimedia Commons 等，真实质感往往更好 |
| **纯色 / 渐变** | 最省事，观感平 |

不论用哪种，都会**自动把亮度校准到目标值**——前景元素的对比度是照着底图亮度调的，
换底不校准，深色面板就会发灰或发死。

### 环境要求

AI 会自己检查这些，缺什么它会告诉你：

- **Python 3.8+**
- **playwright** —— 驱动本机已装的 Chrome，**不下载浏览器、不联网**
- **Pillow**、**numpy**
- 中文字体 **Noto Serif SC** + **Noto Sans SC**（思源宋体 / 思源黑体）
- 可选：本地 ComfyUI，用于生成底图

### Skill 内部结构

```
tech-figures/
  SKILL.md                    给 AI 读的说明书（触发条件、工作流、铁律）
  references/
    design-system.md          组件清单、变量、版式配方
    ai-images.md              底图素材：ComfyUI 调用、能力边界、替代路线
    checklist.md              交付前核对清单
  assets/
    setup.py                  铺进项目 + 探环境
    figkit.css / figkit.js    配图设计系统 + 连线布线
    render.py                 Playwright 渲染器
    cover.css                 封面版式
    make_bg.py                底纹处理，亮度自动校准
    comfy_gen.py              本地 ComfyUI 调用器（可选）
  examples/                   四个可直接抄的样板
```

### 许可

[MIT](LICENSE)

---

<a id="english"></a>

## English

[中文](#中文) · [↑ Top](#top)

### What it is

A Skill following the **[Agent Skills](https://agentskills.io)** open standard, for drawing
figures in technical articles.

**It is not a CLI you type commands into.** Once installed into an AI client, making figures
becomes a conversation — you describe what you want and point out what looks wrong, and the
agent handles the rest: scaffolding directories, writing templates, rendering, and inspecting
each result.

The Python scripts here are **tools the agent uses**, not a command line for you.

### Compatible clients

Anything that implements the Agent Skills standard, including but not limited to:

| Client | Skill directory |
|---|---|
| **Claude Code** | `~/.claude/skills/` or `<project>/.claude/skills/` |
| **OpenClaw** | `~/.openclaw/skills/` or `<workspace>/skills/` |
| **Shared directory** (used by Codex CLI, Gemini CLI, GitHub Copilot, OpenCode, Amp, Kimi Code CLI, …) | `~/.agents/skills/` |

OpenClaw follows the same standard and its skills are a **superset** of it — this skill carries
no client-specific fields, so it works anywhere. Triggering and load timing are up to each client.

### Installation

**Universal** (detects installed clients and links the skill into all of them):

```bash
npx skills add MikeWuPing/tech-figures
```

**Manual, into a specific client** (adjust the path):

```bash
# Claude Code (user level)
git clone https://github.com/MikeWuPing/tech-figures.git ~/.claude/skills/tech-figures

# Claude Code (project level, shared with the team)
git clone https://github.com/MikeWuPing/tech-figures.git <project>/.claude/skills/tech-figures

# OpenClaw
git clone https://github.com/MikeWuPing/tech-figures.git ~/.openclaw/skills/tech-figures

# Shared directory (one copy serves several clients)
git clone https://github.com/MikeWuPing/tech-figures.git ~/.agents/skills/tech-figures
```

**Start a new session** so it gets discovered (`/clear` or restart in Claude Code;
`openclaw gateway restart` in OpenClaw).

### Using it

Once installed, **there is nothing to type**. Just tell the agent:

> Draw the figures for this article — dark theme, and make them match the prose

> The figures in this article look crude. Make them better.

> Make a landscape cover image for this article

> The backgrounds on these figures are too bright. Darken them and show me again.

> Migrate the matplotlib figures under `figs/` to the new pipeline

The agent then works through the whole chain on its own:

1. Reads this skill's instructions (design system, components, hard rules)
2. Probes the environment (Chrome, playwright, CJK fonts, optional ComfyUI)
3. Scaffolds the toolkit into your project, creating `fig/t/` and `fig/_asset/`
4. Writes HTML templates
5. Renders them to PNG and **visually inspects every one**
6. Fixes and re-renders anything with overflow, overlap, or missing connectors

**Your job is two things**: say what you want, and say what looks wrong after seeing the result.

The toolkit is scaffolded automatically the first time you use the skill in a project, and
reused from then on.

### What it can draw

| Component | Purpose |
|---|---|
| Frosted panel | Container with a top highlight and three-layer shadow |
| Node block | A die / a module / a stage |
| Comparison matrix | Multi-column spec table, row/column highlighting |
| Layer stack | Stacked structures, package cross-sections |
| Scale | Magnitude, pitch, timeline |
| Callout | Conclusions and key points |
| Connector | Element-to-element orthogonal routing |
| Cover layout | 16:9, darkened left side for the title |

**Color semantics** — do not mix these three:

| Color | Meaning |
|---|---|
| Blue | Current generation / protagonist / new approach |
| Warm (amber) | Counterpart / previous generation / competitor |
| Red | Cost / warning |

### Why not matplotlib

With matplotlib, you maintain **a coordinate system in your head** — which row and column each
box goes in, whether the text will overflow, where each arrow starts and ends. The more complex
the figure, the harder that mental model is to keep straight.

With HTML/CSS:

| | matplotlib / PIL | HTML + CSS |
|---|---|---|
| Layout | Manual coordinates | flex / grid, computed by the browser |
| Text overflow | Common, needs iteration | Containers grow; it doesn't happen |
| Frosted glass | Not possible | Native `backdrop-filter` |
| Shadows | Approximated | Layered `box-shadow` with inset highlight |
| Typography | Limited | Any system font, full tracking control |
| Connectors | Manual endpoints | Routed between elements |
| Restyling | Edit code, re-run | Edit CSS, applies everywhere |

### Six hard rules

Ordered by how badly we got burned. They are encoded in the skill, so the agent follows them.

1. **No "Figure N" numbers inside images** — the author must be free to reorder figures
2. **When porting an old figure, carry over every piece of text** — a prettier figure that
   lost content is worth less, not more
3. **Numbers in the figure must match the article** — the prose gets fixed, the figure gets
   forgotten, and they contradict each other
4. **Replace vendor-internal block names with functional descriptions** — say what it does,
   not what it's called
5. **Never use AI-generated text** — models hallucinate pseudo-text; all in-figure text is
   composed by code
6. **Never claim an AI-generated image is a photograph** — label it a diagram

### Where backgrounds come from

Three options, none of them required:

| Source | Notes |
|---|---|
| **Local ComfyUI** | Controllable composition and tone; the skill wraps its HTTP API |
| **Public-domain photos** | Wikimedia Commons etc.; real photos often look better |
| **Solid color / gradient** | Least effort, flattest look |

Whichever you use, brightness is **auto-calibrated to a target mean** — foreground contrast is
tuned against the background's brightness, so swapping backgrounds without calibrating makes
dark panels look washed out or muddy.

### Requirements

The agent checks these itself and will tell you what's missing:

- **Python 3.8+**
- **playwright** — drives your installed Chrome; **no browser download, no network**
- **Pillow**, **numpy**
- CJK fonts: **Noto Serif SC** + **Noto Sans SC**
- Optional: local ComfyUI, for generating backgrounds

### Repository layout

```
tech-figures/
  SKILL.md                    instructions the agent reads (triggers, workflow, hard rules)
  references/
    design-system.md          component inventory, variables, layout recipes
    ai-images.md              backgrounds: ComfyUI usage, limits, fallback routes
    checklist.md              pre-delivery checklist
  assets/
    setup.py                  scaffold into a project + probe the environment
    figkit.css / figkit.js    figure design system + connector routing
    render.py                 Playwright renderer
    cover.css                 cover layout
    make_bg.py                background processing with auto brightness calibration
    comfy_gen.py              local ComfyUI driver (optional)
  examples/                   four templates to copy from
```

### License

[MIT](LICENSE)
