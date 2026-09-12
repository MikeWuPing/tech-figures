# 设计系统速查

`assets/figkit.css` 里定义的全部组件。**改风格只改这一个文件**，模板不用动。

## 调色板（CSS 变量）

| 变量 | 值 | 用途 |
|---|---|---|
| `--ink` | `#eef3f9` | 主文字 |
| `--sub` | `#a6b7c9` | 次级文字、说明 |
| `--dim` | `#74879c` | 图注、最弱的字 |
| `--hair` | `rgba(255,255,255,.10)` | 发丝线、边框 |
| `--hair2` | `rgba(255,255,255,.17)` | 强一级的边框 |
| `--acc` | `#7fb0dd` | 强调蓝 —— 本代 / 主角 |
| `--acc-soft` | `rgba(127,176,221,.20)` | 蓝色的浅底 |
| `--warm` | `#cfae74` | 暖琥珀 —— 对照方 / 上一代 |
| `--warm-soft` | `rgba(207,174,116,.18)` | 暖色的浅底 |
| `--red` | `#d98a80` | 代价 / 警示 |
| `--glass` | `rgba(15,21,28,.62)` | 面板底 |
| `--glass2` / `--glass3` | 逐级更亮 | 面板的层次 |
| `--serif` | Noto Serif SC | 标题 |
| `--sans` | Noto Sans SC | 正文 |
| `--mono` | Cascadia Mono | 数值、代号 |
| `--r` / `--r-sm` | 13px / 9px | 圆角 |
| `--pad` | 40px | 画布内边距 |

字体依赖本机已装的 **Noto Serif SC**（思源宋体）和 **Noto Sans SC**（思源黑体）。
Windows 上一般随 Office 或系统更新装上；没有就去 Google Fonts 下 OTF 装到系统。

## 画布骨架

```html
<div class="fig">
  <div class="bg" style="background-image:url('../../_asset/bg.png')"></div>
  <div class="veil"></div>
  <svg class="wires"></svg>

  <div class="hd">
    <h1>主标题</h1>
    <div class="sub">副标题</div>
  </div>

  <div class="bd"> …内容… </div>

  <div class="ft">底部图注</div>
</div>
```

四层缺一不可：`.bg` 底图 → `.veil` 暗角 → `.wires` 连线（z-index 最高）→ 内容。
`.hd` / `.bd` / `.ft` 三段式，`.bd` 自动撑满剩余高度。

## 组件

### 面板 `.card`

磨砂玻璃，带顶边高光和三层阴影。`.tone2` / `.tone3` 逐级更亮，用来区分主次。

```html
<div class="card grow">
  <div class="ct">标题<span class="en">English</span></div>
  …内容…
</div>
```

`.ct` 是面板标题（衬线体）。需要把内容压到底部时中间插一个 `<div class="spacer"></div>`。

### 节点 `.node`

最小的方块，表示一颗 die / 一个模块 / 一个环节。

```html
<div class="node acc">计算 die<span class="n">8 核</span></div>
```

变体：`.acc`（蓝）、`.warm`（暖）、`.flat`（无阴影，用于底板这类大块）。
`.n` 是节点内的小字说明。

### 对照矩阵 `.mx`

表格。用 `grid-template-columns` 控制列宽。

```html
<div class="mx fill" style="grid-template-columns:1.4fr 1fr 1fr 1fr 1fr">
  <div class="h"></div>
  <div class="h">A 方案</div>
  <div class="h col-hi">B 方案</div>

  <div class="c lbl">行标题</div>
  <div class="c v">值</div>
  <div class="c v col-hi">值</div>
</div>
```

- `.h` 表头、`.c.lbl` 行标签、`.c.v` 数值单元格、`.c.dim` 弱化
- `.col-hi` **整列**高亮（突出本代那一列）
- `.c.hi` / `.c.warm` / `.c.bad` **整行**高亮（按行分组时用）
- `gap:1px` 让背景透出来形成发丝分隔线

### 分层剖面 `.stack` / `.layer`

```html
<div class="stack">
  <div class="layer si">硅<span class="th">Si</span></div>
  <div class="layer sub">基板<span class="th">Substrate</span></div>
</div>
```

`.stack` 是 `column-reverse`，**HTML 里先写的在最下面**——按物理堆叠顺序写就行。
变体：`.si`（硅）、`.sub`（基板）、`.metal`（金属）。`.th` 是右对齐的注释。

### 标尺 `.scale`

表示量级、间距、时间轴。

```html
<div class="scale">
  <div class="rail"></div>
  <div class="tick" style="left:45%"></div>
  <div class="mk" style="left:45%">
    <div class="v">25 µm</div>
    <div class="l">凸点间距</div>
  </div>
</div>
```

`.rail` 是横线，`.tick` 是刻度，`.mk` 是标注（自动居中，**放两端时会被裁掉，改内联 left/right**）。

### 说明条与要点

```html
<div class="note key">一句话结论，<b>重点加粗</b>。</div>
<div class="notes warm"><div>要点一</div><div>要点二</div></div>
```

`.note.key` 左侧带蓝色竖线，用来放这张图的题眼。
`.notes` 是带圆点的要点列表，`.warm` 换成暖色点。

### 其它

| 类 | 用途 |
|---|---|
| `.spec` / `.sep` | 标题下的一行规格参数，`.sep` 是分隔点 |
| `.num` / `.num.big` / `.unit` | 等宽数值、大号数值、单位 |
| `.rule` / `.vrule` | 水平 / 垂直分隔线 |
| `.cap2` | 弱化的小字说明 |
| `.tag` | 胶囊标签 |
| `.grid` | 通用 grid 容器 |

## 布局工具

| 类 | 作用 |
|---|---|
| `.row` | 横排，`.tight` 缩小间距，`.mid` 垂直居中 |
| `.col` | 竖排，`.tight` 缩小间距 |
| `.grow` | 占据剩余空间（横向上） |
| `.fill` | 撑满高度（纵向上） |
| `.spacer` | 占位，把后面的内容压到底部 |
| `.center` | 居中 |

**不要手算坐标。** 用 flex 和 grid 排版，让浏览器算——这是换掉 matplotlib 的最大理由。

## 连线 `figkit.js`

```html
<script src="../figkit.js"></script>
<script>
window.addEventListener("load", function () {
  wire("#a", "#b", { from: "r", to: "l" });
});
</script>
```

参数：

| 选项 | 说明 |
|---|---|
| `from` / `to` | 起点 / 终点方向：`'t'` `'b'` `'l'` `'r'` |
| `straight` | `true` = 垂直直落，保持起点 x 一路走到底。**扇入到宽底板时用** |
| `color` / `w` | 颜色、线宽 |
| `dot` | 端点小圆点，默认 `true` |
| `arrow` | 箭头，默认 `true` |
| `dash` | 虚线，如 `"4 3"` |
| `mid` | 手动指定转折位置 |
| `padA` / `padB` | 端点外扩距离 |

**同一源点分出多根线时不要用 `straight`**，会塌成一条。用默认的正交路由。

## 版式配方

几种高频图型的搭法：

**两栏对照** —— 两个 `.card.grow` 并排，各自标题 + 节点行 + 说明；中间用 `.vrule` 分隔。
适合「上一代 vs 本代」这种二元对比。

**四方对照表** —— 一个 `.mx`，第一列是行标签，后四列是四方的值，本代那列加 `.col-hi`。

**流程 / 时序** —— 一排 `.node` 横向排列，之间用 `wire(from:'r', to:'l')` 连起来。
多档递进时用一个 `.row` 装多个节点。

**分层剖面** —— `.stack` + `.layer`，层次多时配 `wire(straight:true)` 画出上下关系。

**权衡曲线** —— 内联 SVG。用 `<path>` 画曲线，配 `<linearGradient>` 做面积填充，
坐标轴用 `<path>` 画折线。**不要用 div 拼曲线。**

**封面** —— 见 `cover.css`。左侧三分之二压暗放标题，右侧留出图像。主标题 ≤12 字、副标题 ≤2 行。
