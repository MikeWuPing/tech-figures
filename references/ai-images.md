# AI 生成配图素材

> **这一节是可选的。** 本 skill 不依赖 ComfyUI——机器上没装、模型不对、或者你就是不想用 AI，
> 就跳过整节，底图改用公有领域照片或纯色渐变（见 SKILL.md 的「底图从哪来」）。
> 下面写的都是「**有** ComfyUI 时，怎么把它用好」。

**用途只有一个：出底图、封面底图、意境图。** 不画技术内容。

## 能力边界（实测）

| 能力 | 结果 |
|---|---|
| 抽象科技底纹、PCB 微距、die shot 质感、层叠结构 | **很好**，可作底图 |
| 中文单行短词 | 准确（如「内存控制器」） |
| 英文文字 | **不可靠**，`DDR5 Channel` 会渲染成 `D: DПk5(Channel` |
| 技术框图、时序图、准确连线 | **做不到** |
| 伪造文字 | **会自己长出来**——见下面的「挑图」 |
| 安全过滤 | 会误伤 |

**结论**：AI 出画面，代码出文字。任何需要准确表达的东西都不交给模型。

## 本地 ComfyUI

### 找到它

ComfyUI 可能有多份安装，**只有装了 CUDA 版 torch 的那份能用 GPU**。
逐个试，别猜：

```bash
# 1. 找到所有安装
ls ~/AppData/Local/Comfy-Desktop/ComfyUI-Installs/*/ComfyUI/main.py 2>/dev/null

# 2. 逐个验 torch 是不是 CUDA 版（这一步不能省）
"<装目录>/.venv/Scripts/python.exe" -c "import torch;print(torch.__version__, torch.cuda.is_available())"
# 要看到类似 2.10.0+cu130 True；如果是 2.x.x+cpu False 就换下一个
```

### 启动

```bash
cd "<装目录>"
"<装目录>/.venv/Scripts/python.exe" main.py --port 8188 --listen 127.0.0.1 &
# 日志出现 "To see the GUI go to" 即就绪。轮询 /system_stats 确认。
```

**不需要打开网页。** 全程走 HTTP API。

### 调用

`assets/comfy_gen.py` 已经封装好：`/prompt` 提交 → 轮询 `/history` → 从 `/view` 取图。

```bash
python comfy_gen.py "提示词" 输出.png [宽 高 步数 种子]
# 实测：1280×720 / 26 步约 12 秒一张（RTX 4090 + Ideogram 4 fp8）
```

**如果 ComfyUI 不在 8188**，改脚本顶部的 `HOST`。

如果机器上没有 Ideogram 4，先查 `/object_info` 看有什么模型：

```bash
curl -s http://127.0.0.1:8188/object_info | python -c "
import sys,json; d=json.load(sys.stdin)
for k in ['CheckpointLoaderSimple','UNETLoader']:
    if k in d: print(k, list(d[k]['input']['required'].values())[0][0])"
```

然后相应改 `comfy_gen.py` 里的 `build()`——它现在用的是
`UNETLoader + CLIPLoader(ideogram4) + VAELoader + KSampler` 这套组合。

### 关闭

跑完就关，它会一直占着显存（Ideogram 4 约占 19GB）：

```bash
netstat -ano | grep ":8188" | grep LISTENING
taskkill //F //PID <PID>
```

## 写提示词

对**底图**（要暗、要能压住）：

- 明确写 `very dark and moody`、`cinematic`，否则出来偏亮
- 写清材质和结构：`die shot`、`PCB macro`、`stacked silicon layers`、`copper traces`
- 色调跟配图系统对齐：`deep navy blue`、`graphite`、`subtle cyan glow`、`warm amber accent`
- **别写尺寸、别写比例**——宽高用参数给

对**封面**：构图要留出放字的位置，写 `left side in shadow` 之类；
出来后再用 `cover.css` 压暗左侧叠加标题。

## 挑图（这一步不能省）

**必须逐张放大看。** 一轮 9 张里报废弃掉 4 张是常事。三类问题：

1. **画面里长出了伪文字。** 模型会在不该有字的地方生成看起来像字的乱码，
   缩略图上是糊的，放大才看得见。**中了就废，没法修。**
2. **被安全过滤拦下。** 返回一张写着 `Image blocked by safety filter` 的灰图。
   实测会误伤的措辞：`delidded`、`cross-section`、`wafer texture`。
   换个说法通常就过了——**不要以为是提示词写错了**。
3. **太暗或太亮。** 用 `make_bg.py` 的自动校准救，别手调。

## 处理成底纹

```bash
python make_bg.py 源图.png 输出.png [模糊px 去饱和 目标均值]
# 例：python make_bg.py raw.png bg.png 11 0.32 30
```

处理链：裁到目标比例 → 缩放 → 高斯模糊 → 去饱和 → **亮度二分校准**。

**自动校准是关键。** 前景元素的对比度是照着底图亮度调的，新底图亮度不同，
深色面板就会发灰或发死。脚本用二分法把全图均值精确校到目标值。

| 用途 | 模糊 | 饱和 | 目标均值 |
|---|---|---|---|
| 配图底纹 | 6～11px | 0.32～0.40 | **30** |
| 意境图 | 0.6px | 0.95 | **24** |

模糊越大，背景的结构越不明显、越不抢戏。**11px 是个好起点**——还能认出是芯片，
但不会让人去读背景的形状。6px 时功能块太清楚，会分散注意力。

## 免费在线接口（备查，不推荐）

`https://image.pollinations.ai/prompt/<提示词>` 免注册、直接 GET 就能拿回 JPEG，实测可用。
但画不了技术内容，质量不如本地模型，且有速率限制。本管线不采用。

## 版权

本地模型生成，**无第三方版权**。但发表时标「示意图 / 概念图」，
**不声称是摄影作品，不声称对应任何真实产品**。

## 没有 ComfyUI 时的替代

**公有领域照片往往比 AI 生成更好。** 真实的版图结构自带细节，虚化之后质感更自然，
而且 CC0 素材没有任何版权顾虑——不用在括号里写「AI 生成」。

### 找素材

- **Wikimedia Commons**（`commons.wikimedia.org`）—— 大量 CC0 / 公有领域的芯片裸片
  显微摄影。检索 `die shot`、`silicon wafer`、`processor die`，Fritzchens Fritz 那一批
  质量很高，适合直接拿来当底纹。
- 厂商官方媒体素材包（注意授权范围，通常只许报道用途）
- Unsplash / Pexels 之类（CC0 类，但技术题材少）

⚠️ **国内网络访问 Wikimedia 常需要代理。** 先试直连，不行再挂：

```bash
curl -sL --max-time 30 -x http://127.0.0.1:<端口> -o out.jpg "<图片直链>"
```

端口按自己机器的填（常见是 1080 / 7890 / 10809）。挂了还超时就换素材，别死磕。

### 处理成底纹

走同一条路，参数按素材本身的明暗微调：

```bash
python make_bg.py 素材.jpg _asset/bg.png 7 0.38 30
```

**CC0 素材也要记一笔出处**（作者、来源、授权）。不是为了履行署名义务——CC0 不要求——
而是半年后你自己或读者会问「这张哪来的」，那时翻记录比翻聊天记录快。

### 纯色 / 渐变

`.bg` 直接留空，`.fig` 的兜底色 `#0f1319` 就会生效；或者给一点层次：

```html
<div class="bg" style="background:linear-gradient(160deg,#141a22,#0d1117)"></div>
```

没有质感，但干净、可控、零风险。快速出图时够用。
