<a id="top"></a>

# tech-figures

**用 HTML/CSS 给技术文章画配图 —— 不写绘图代码算坐标，排版交给浏览器。**

**Draw technical figures with HTML/CSS — let the browser do the layout.**

[中文](#中文) · [English](#english)

---

<a id="中文"></a>

## 中文

### 这是什么

一个 [Claude Code](https://claude.com/claude-code) Skill：把技术文章的配图从「写绘图代码摆坐标」
换成「写 HTML/CSS，用 Chromium 截图」。附带一整套设计系统、渲染器、底纹处理工具和 AI 生图调用器。

### 为什么不再用 matplotlib

用 matplotlib 画示意图，你还得**在脑子里维护一张坐标系**：每个方块放在第几行第几列、
文字多长会不会溢出、箭头从哪个点连到哪个点。图画得越复杂，这张脑内坐标系越难维护，
最后你的精力花在摆位置上，而不是内容上。

更麻烦的是表现力有天花板。想要磨砂玻璃面板？做不出。想要真正的柔和投影？只能近似。
想要圆角、字距、行高都精确？一件件凑。

换到 HTML/CSS 之后：

| | matplotlib / PIL | HTML + CSS |
|---|---|---|
| 排版 | 手算坐标 | flex / grid，浏览器算 |
| 文字溢出 | 常见，要反复调 | 容器自己撑开，不会发生 |
| 磨砂玻璃 | 画不出 | `backdrop-filter` 原生支持 |
| 阴影 | 近似 | 多层 `box-shadow`，含内阴影高光 |
| 字体 | 有限 | 系统全部字体，字距行高随意调 |
| 连线 | 手算端点 | `wire('#a', '#b')` 按元素布线 |
| 改版 | 改代码重跑 | 改 CSS，全部生效 |

### 快速开始

```bash
# 1. 把 skill 的 assets 铺进你的项目（会建目录、拷工具、探环境）
python <skill>/assets/setup.py

# 2. 从 examples/ 抄一个样板，改成你的内容
cp <skill>/examples/example-panels.html fig/t/myfig-01.html

# 3. 渲染
cd <项目根> && python fig/render.py --all
```

`setup.py` **不覆盖已存在的文件**，重复跑是安全的。它会顺带检查 Chrome、playwright、
Pillow、中文字体（思源宋体/黑体）是否就位。

### 目录结构

```
<项目根>/
  figs.conf                模板前缀 → 输出目录，和文章里的 ![]() 引用一致
  fig/
    render.py              渲染器
    figkit.css             配图设计系统
    figkit.js              连线绘制
    setup.py               铺开工具链
    make_bg.py             把任意图处理成底纹（自动校准亮度）
    comfy_gen.py           本地 ComfyUI 调用器（可选）
    cover.css              封面版式
    t/*.html               每张图一个模板
    _asset/                底图素材
```

### 设计系统

`figkit.css` 提供一整套组件，改风格只改这一个文件：

| 组件 | 类名 | 用途 |
|---|---|---|
| 画布 | `.fig` + `.bg` + `.veil` | 深色底 + 底图 + 暗角 |
| 磨砂面板 | `.card` | 带顶边高光和三层阴影 |
| 节点方块 | `.node` | 一颗芯片 / 一个模块 / 一个环节 |
| 对照矩阵 | `.mx` | 多方规格表，支持整列/整行高亮 |
| 分层剖面 | `.stack` / `.layer` | 堆叠结构 |
| 标尺 | `.scale` | 量级、间距、时间轴 |
| 说明条 | `.note` / `.notes` | 结论与要点 |
| 连线 | `wire()` | 按元素自动布线，横平竖直 |

**用色语义**（三者不要混用）：

| 颜色 | 含义 |
|---|---|
| 蓝 `--acc` | 本代 / 主角 / 新方案 |
| 暖 `--warm` | 对照方 / 上一代 / 竞品 |
| 红 `--red` | 代价 / 警示 |

### 六条铁律

按踩过的坑的严重程度排：

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
| **本地 ComfyUI** | 构图色调可控；`comfy_gen.py` 已封装 HTTP API 调用 |
| **公有领域照片** | Wikimedia Commons 等，真实质感往往更好 |
| **纯色 / 渐变** | 最省事，观感平 |

`make_bg.py` 能处理任意来源的图，**自动把亮度校准到目标值**——前景元素的对比度是
照着底图亮度调的，换底不校准，深色面板就会发灰或发死。

### 依赖

- Python 3.8+、`playwright`（用本机已装的 Chrome，**不下载浏览器**）、`Pillow`、`numpy`
- 中文字体 **Noto Serif SC**（思源宋体）+ **Noto Sans SC**（思源黑体）
- 可选：本地 ComfyUI（用于生成底图）

### 许可

[MIT](LICENSE)

---

<a id="english"></a>

## English

[中文](#中文) · [↑ Top](#top)

### What it is

A [Claude Code](https://claude.com/claude-code) Skill that replaces "write drawing code and
place coordinates" with "write HTML/CSS and screenshot it with Chromium" for technical article
figures. Ships with a design system, a renderer, background-processing tools, and an optional
local image-generation driver.

### Why not matplotlib

With matplotlib, you maintain **a coordinate system in your head** — which row and column each
box goes in, whether the text will overflow, where each arrow starts and ends. The more complex
the figure, the harder that mental model is to keep straight. You end up spending effort on
positioning instead of on content.

Expressiveness hits a ceiling too. Frosted glass? Can't. Real soft shadows? Only approximated.
Precise corner radius, letter-spacing, line-height? Piece by piece.

With HTML/CSS:

| | matplotlib / PIL | HTML + CSS |
|---|---|---|
| Layout | Manual coordinates | flex / grid, computed by the browser |
| Text overflow | Common, needs iteration | Containers grow; it doesn't happen |
| Frosted glass | Not possible | Native `backdrop-filter` |
| Shadows | Approximated | Layered `box-shadow` with inset highlight |
| Typography | Limited | Any system font, full tracking control |
| Connectors | Manual endpoints | `wire('#a', '#b')` routes between elements |
| Restyling | Edit code, re-run | Edit CSS, applies everywhere |

### Quick start

```bash
# 1. Install the toolkit into your project (creates dirs, copies files, probes env)
python <skill>/assets/setup.py

# 2. Copy an example template and adapt it
cp <skill>/examples/example-panels.html fig/t/myfig-01.html

# 3. Render
cd <project-root> && python fig/render.py --all
```

`setup.py` **never overwrites existing files** — re-running it is safe. It also checks for
Chrome, playwright, Pillow, and CJK fonts (Noto Serif SC / Noto Sans SC).

### Layout

```
<project-root>/
  figs.conf                template prefix → output dir, must match ![]() paths in your article
  fig/
    render.py              renderer
    figkit.css             figure design system
    figkit.js              connector routing
    setup.py               bootstrap
    make_bg.py             turn any image into a background (auto brightness calibration)
    comfy_gen.py           local ComfyUI driver (optional)
    cover.css              cover layout
    t/*.html               one template per figure
    _asset/                background assets
```

### Design system

`figkit.css` ships the full component set. Restyling means editing this one file.

| Component | Class | Purpose |
|---|---|---|
| Canvas | `.fig` + `.bg` + `.veil` | Dark base + background image + vignette |
| Frosted panel | `.card` | Top highlight and three-layer shadow |
| Node block | `.node` | A die / a module / a stage |
| Comparison matrix | `.mx` | Multi-column spec table, row/column highlight |
| Layer stack | `.stack` / `.layer` | Stacked structures |
| Scale | `.scale` | Magnitude, pitch, timeline |
| Callout | `.note` / `.notes` | Conclusion and key points |
| Connector | `wire()` | Element-to-element orthogonal routing |

**Color semantics** — do not mix these three:

| Color | Meaning |
|---|---|
| Blue `--acc` | Current generation / protagonist / new approach |
| Warm `--warm` | Counterpart / previous generation / competitor |
| Red `--red` | Cost / warning |

### Six hard rules

Ordered by how badly we got burned:

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
| **Local ComfyUI** | Controllable composition and tone; `comfy_gen.py` wraps the HTTP API |
| **Public-domain photos** | Wikimedia Commons etc.; real photos often look better |
| **Solid color / gradient** | Least effort, flattest look |

`make_bg.py` handles any source and **auto-calibrates brightness to a target mean** — foreground
contrast is tuned against the background's brightness, so swapping backgrounds without
calibrating makes dark panels look washed out or muddy.

### Requirements

- Python 3.8+, `playwright` (drives your installed Chrome — **no browser download**), `Pillow`, `numpy`
- CJK fonts: **Noto Serif SC** + **Noto Sans SC**
- Optional: local ComfyUI, for generating backgrounds

### License

[MIT](LICENSE)
