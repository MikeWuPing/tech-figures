# AI 生成配图素材

> **这一节是可选的。** 本 skill 不依赖 ComfyUI——机器上没装、模型不对、或者你就是不想用 AI，
> 就跳到最后的「没有 ComfyUI 时的替代」，底图改用公有领域照片或纯色渐变。
> 下面写的都是「**有** ComfyUI 时，怎么把它用好」。

**用途只有一个：出底图、封面底图、意境图。** 不画技术内容。

---

## 一、用哪个模型（先看这节）

**优先 Z-Image-Turbo。不要用 Ideogram。**

同一批提示词、同一个题材（深色科技氛围底），实测差距是压倒性的：

| | Ideogram 4 | Z-Image-Turbo |
|---|---|---|
| **干净出图率** | **2 / 24（8%）** | **8 / 8（100%）** |
| 出图速度 | 约 12 秒 / 26 步 | **9～18 秒 / 10 步** |
| 典型失败 | 画面里长出成片伪文字；安全过滤误伤 | 未出现 |

原因是两个模型的路子不同：**Ideogram 4 是按平面设计／海报调过的，天生要往画面上放排版**。
提示词里只要出现「电路板」「数据流」「芯片表面」这类有设计感的词，它就往上贴看起来像字的
乱码——加 `no text` 也没用，换成「photograph of…」的措辞也没用。

Z-Image 是通用图像模型，不干这事。同一个「暗色水面波纹」的提示词，Ideogram 给了一只鸭子，
Z-Image 给的是真正的波纹。

**代价**：Z-Image 是 turbo 蒸馏模型，参数和常规模型不同，配错了会出糊图——

- **步数 10**（不是 20～30）
- **CFG 必须 1.0**
- 采样前要挂 `ModelSamplingAuraFlow`，**shift = 3.0**（Lumina2 系的要求）

`comfy_gen.py` 里已经封装好，用 `--model zimage` 即可（默认就是它）。

---

## 二、找到 ComfyUI

### 步骤 1：定位安装与模型目录

ComfyUI Desktop 的**程序目录**和**模型目录**常常是分开的，中间隔着 Electron 外壳：

```
<安装盘>/AI/AI Tools/ComfyUI/          ← 只有 ComfyUI.exe 和 Chromium 库，不是服务端
%LOCALAPPDATA%/Comfy-Desktop/ComfyUI-Installs/<名字>/ComfyUI/   ← 真正的服务端在这里
```

**模型目录要从配置文件读**，别在程序目录里找：

```bash
cat ~/AppData/Roaming/ComfyUI/config.json     # 看 "basePath"
```

### 步骤 2：验 torch 是不是 CUDA 版

一份机器上可能有好几套装法，**只有装了 CUDA 版 torch 的那份能用 GPU**。逐个试，别猜：

```bash
"<服务端目录>/.venv/Scripts/python.exe" -c "import torch;print(torch.__version__, torch.cuda.is_available())"
# 要看到 2.10.0+cu130 True；如果是 2.x.x+cpu False 就换下一个
```

### 步骤 3：验模型文件是完整的 ← **这一步不能省**

**踩过的坑**：ComfyUI 的模型下载器会启动下载然后卡死，留下一个只有文件头的残file。
safetensors 的头部在文件**最前面**，所以 ComfyUI **照样能在下拉框里列出这个模型**——
看起来「有」，点下去才报错。光看目录列表会被骗。

模型目录里的 `.dl-meta` 记录了应该有多大：

```bash
cat <模型目录>/diffusion_models/xxx.safetensors.dl-meta
# {"url":"https://huggingface.co/...","expectedSize":12309866400,...}
```

或者用张量偏移直接算：

```python
import json, struct, os
p = r"<模型文件>"
size = os.path.getsize(p)
with open(p, "rb") as f:
    n = struct.unpack("<Q", f.read(8))[0]
    hdr = json.loads(f.read(n))
tensors = {k: v for k, v in hdr.items() if k != "__metadata__"}
need = max(v["data_offsets"][1] for v in tensors.values()) + 8 + n
print("实际 %.1f MB / 需要 %.1f MB → %s" % (size/1048576, need/1048576,
      "完整" if size >= need else "**截断 %.1f%%**" % (100*size/need)))
```

---

## 三、启动与调用

```bash
# 启动：服务端用装了 CUDA torch 的那套，模型目录指到完整的那份
"<服务端>/.venv/Scripts/python.exe" "<服务端>/main.py" \
  --port 8188 --listen 127.0.0.1 \
  --base-directory "<完整的模型目录>"
# 日志出现 "To see the GUI go to" 即就绪。不需要打开网页，全程走 HTTP API。
```

```bash
# 生成
python comfy_gen.py "提示词" 输出.png [宽 高 步数 种子 cfg] [--model zimage|ideogram]
# 默认 zimage。1600×900 / 10 步约 10～18 秒一张。
```

`comfy_gen.py` 走 `/prompt` 提交图、轮询 `/history`、从 `/view` 取回图片，不碰浏览器。

**如果 ComfyUI 不在 8188**，改脚本顶部的 `HOST`。

**如果模型文件名不同**，先查 `/object_info`：

```bash
curl -s http://127.0.0.1:8188/object_info -o oi.json   # Windows 上别写 /tmp，Python 不认
python -c "import json;d=json.load(open('oi.json',encoding='utf-8'));
print(d['UNETLoader']['input']['required']['unet_name'][0])"
```

然后相应改 `comfy_gen.py` 里的 `STACKS`。

> 两套栈的差别：Z-Image 用 `qwen_3_4b` 文本编码器，CLIPLoader 的 type 填 `qwen_image`
> （**不能填 flux / flux2**，否则会被路由到 Flux 的编码器）；Ideogram 用 `qwen3vl_8b`，
> type 填 `ideogram4`。Z-Image 的识别是**按模型名自动路由**的——名字里有 `qwen3_4b`
> 就走 Z-Image 那条分支。

**跑完就关**，它会一直占着显存：

```bash
netstat -ano | grep ":8188" | grep LISTENING
taskkill //F //PID <PID>
```

---

## 四、写提示词

对**底图**（要暗、要能压住）：

- 明确写 `very dark`、`cinematic`，否则出来偏亮
- 写清材质和结构：`circuit board`、`silicon chip`、`silk fabric folds`、`water ripples`、
  `frosted glass`、`brushed metal`
- 色调跟配图系统对齐：`deep blue`、`dark navy`、`cool blue light`
- **别写尺寸、别写比例**——宽高用参数给
- 加 `no text` 有一点帮助，但不是保险

对**封面**：构图要留出放字的位置，写 `left side in shadow` 之类；
出来后再用遮罩把底图限制在**不压字的那半边**（见下面的「底图怎么用」）。

---

## 五、挑图

Z-Image 的干净率很高，但仍要**逐张看一眼**再采用。重点查两样：

1. **画面里有没有长出伪文字。** 放大看——缩略图上糊成一团，看不出是字。
2. **是不是被安全过滤拦了。** 会返回一张写着 `Image blocked by safety filter` 的灰图。
   实测容易误伤的措辞：`delidded`、`cross-section`、`wafer texture`、`long exposure`。
   换个说法通常就过——**不要以为是提示词写错了**。

用 Ideogram 时这一条尤其要紧（一轮 6 张废 5 张是常事）；用 Z-Image 则很少出问题。

---

## 六、底图怎么用

### 处理成底纹

```bash
python make_bg.py 源图.png 输出.png [模糊px 去饱和 目标均值]
```

处理链：裁到目标比例 → 缩放 → 高斯模糊 → 去饱和 → **亮度二分校准**。

**自动校准是关键。** 前景元素的对比度是照着底图亮度调的，新底图亮度不同，
深色面板就会发灰或发死。

| 用途 | 模糊 | 饱和 | 目标均值 |
|---|---|---|---|
| 配图底纹 | 6～11px | 0.32～0.40 | **30** |
| 意境图 | 0.6px | 0.95 | **24** |

### 封面：底图只铺半边 ← **踩过的坑**

把 AI 底图**铺满整幅封面**，标题会立刻发灰、读不清——背景比原来的纯色亮，
文字对比度直接垮掉。

正确做法是**让 AI 纹理只在放截图的那半边浮现**，文字区留给深色渐变：

```css
.cv .bg{                     /* 打底：程序渐变，保证文字区对比度 */
  background:radial-gradient(...), linear-gradient(155deg,#10161f,#070a0f);
}
.cv .tex{                    /* AI 纹理：左侧淡出到全透明 */
  background:url('...png') center/cover no-repeat;
  filter:brightness(.75) saturate(.92);
  -webkit-mask-image:linear-gradient(90deg,transparent 0%,transparent 30%,rgba(0,0,0,.30) 52%,#000 72%);
  mask-image:linear-gradient(90deg,transparent 0%,transparent 30%,rgba(0,0,0,.30) 52%,#000 72%);
}
```

---

## 七、本机已知配置

> 换机器时改这里。这一节是作者本机的现状，不是通用值。

| 项 | 值 |
|---|---|
| 服务端 | `C:\Users\mikew\AppData\Local\Comfy-Desktop\ComfyUI-Installs\comcom1\ComfyUI` |
| 服务端解释器 | 同目录 `.venv\Scripts\python.exe`（torch 2.10.0+cu130，CUDA 可用） |
| **模型目录** | **`E:\AI\AI Tools\ComfyUI_R`**（Desktop 的 basePath，配置在 `%APPDATA%\ComfyUI\config.json`） |
| 显卡 | RTX 4090 24GB |

**启动命令**（照抄）：

```bash
"C:/Users/mikew/AppData/Local/Comfy-Desktop/ComfyUI-Installs/comcom1/ComfyUI/.venv/Scripts/python.exe" \
  "C:/Users/mikew/AppData/Local/Comfy-Desktop/ComfyUI-Installs/comcom1/ComfyUI/main.py" \
  --port 8188 --listen 127.0.0.1 --base-directory "E:\AI\AI Tools\ComfyUI_R"
```

`E:\AI\AI Tools\ComfyUI_R\models` 里的可用模型：

| 目录 | 文件 | 用途 |
|---|---|---|
| diffusion_models | `z_image_turbo_bf16.safetensors`（11.7 GB） | **首选** |
| text_encoders | `qwen_3_4b.safetensors`（7.7 GB） | Z-Image 的文本编码器 |
| vae | `ae.safetensors`（320 MB） | Z-Image 的 VAE |
| diffusion_models | `ideogram4_fp8_scaled.safetensors`（8.9 GB） | 备选，伪文字多 |
| text_encoders | `qwen3vl_8b_fp8_scaled.safetensors`（10.1 GB） | Ideogram 的文本编码器 |
| vae | `flux2-vae.safetensors`（321 MB） | Ideogram 的 VAE |

> ⚠️ `%LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Shared\models` 下另有一套同名文件，
> 但**是残的（1%～2%）**——在 UI 里列得出来却加载不了。别用那套。

---

## 八、没有 ComfyUI 时的替代

**公有领域照片往往够用，甚至更好。** 真实的版图结构自带细节，虚化之后质感自然，
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
