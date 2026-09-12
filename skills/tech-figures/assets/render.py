# -*- coding: utf-8 -*-
"""HTML/CSS 配图渲染器 —— Playwright 驱动本机 Chrome，HTML 直出 PNG

不下载浏览器（用系统已装的 Chrome），不联网。

## 目录约定

    <项目根>/
      figs.conf          ← 可选，写「模板前缀 = 输出目录」
      fig/               ← 本脚本和模板所在处（名字随意，下面用 fig 代指）
        render.py
        t/*.html         ← 每张图一个模板
        _asset/          ← 底图素材
    输出落到 figs.conf 指定的目录，相对项目根。

figs.conf 长这样（`#` 开头是注释）：

    gen  = figs
    ddr  = figs/ddr
    pkg  = figs/pkg
    wcl  = figs/wcl

没写进配置的前缀，默认落到 `figs/`。

## 用法

    python fig/render.py fig/t/pkg-01-basic.html        # 单张，路径自动推导
    python fig/render.py --all                          # t/ 下全部
    python fig/render.py --check                        # 只列出会写到哪，不渲染

## 画布尺寸

每个模板自己在 <head> 里声明，没声明就用下面的默认值：

    <meta name="fig-size" content="1200x640">

输出按 DSF 倍像素密度渲染（1200×640 的画布出 2400×1280 的图），
文字在内容平台按栏宽缩放后依然锐利。
"""
import asyncio
import glob
import os
import re
import sys

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))          # …/fig
ROOT = os.path.normpath(os.path.join(HERE, ".."))          # 项目根
TPL = os.path.join(HERE, "t")
CONF = os.path.join(ROOT, "figs.conf")

W, H, DSF = 1200, 640, 2       # 默认画布与像素密度
DEFAULT_OUT = "figs"           # 配置里没提到的前缀，落到这里


def outdirs():
    """读 figs.conf：模板前缀 → 输出目录（相对项目根）"""
    m = {}
    if os.path.exists(CONF):
        for line in open(CONF, encoding="utf-8"):
            line = line.split("#", 1)[0].strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            m[k.strip()] = v.strip()
    return m


def size_of(path):
    """读模板声明的画布尺寸"""
    try:
        head = open(path, encoding="utf-8").read(2048)
    except OSError:
        return W, H
    m = re.search(r'name=["\']fig-size["\']\s+content=["\'](\d+)\s*[x×]\s*(\d+)', head)
    return (int(m.group(1)), int(m.group(2))) if m else (W, H)


def dest_of(src, dirs=None):
    """模板路径 → 输出 PNG 路径"""
    dirs = dirs if dirs is not None else outdirs()
    name = os.path.splitext(os.path.basename(src))[0]
    prefix = name.split("-")[0]
    return os.path.join(ROOT, dirs.get(prefix, DEFAULT_OUT), name + ".png")


async def shot(browser, src, dst, w, h):
    url = "file:///" + os.path.abspath(src).replace("\\", "/")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    pg = await browser.new_page(viewport={"width": w, "height": h},
                                device_scale_factor=DSF)
    await pg.goto(url, wait_until="networkidle")
    await pg.evaluate("document.fonts.ready")     # 等中文字体真正就位
    await pg.wait_for_timeout(250)                # 让 backdrop-filter 稳定
    await pg.screenshot(path=dst)
    await pg.close()
    print("  ok  %-30s -> %s  (%dx%d)" %
          (os.path.basename(src), os.path.relpath(dst, ROOT), w * DSF, h * DSF))


async def main(jobs):
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        for j in jobs:
            await shot(b, *j)
        await b.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    dirs = outdirs()

    if args and args[0] == "--check":
        for f in sorted(glob.glob(os.path.join(TPL, "*.html"))):
            w, h = size_of(f)
            print("  %-30s -> %-34s %dx%d" % (os.path.basename(f),
                  os.path.relpath(dest_of(f, dirs), ROOT), w, h))
        sys.exit()

    if args and args[0] == "--all":
        todo = []
        for f in sorted(glob.glob(os.path.join(TPL, "*.html"))):
            w, h = size_of(f)
            todo.append((f, dest_of(f, dirs), w, h))
        if not todo:
            sys.exit("t/ 下没有模板")
    else:
        if not args:
            sys.exit(__doc__)
        src = args[0]
        w, h = (int(args[2]), int(args[3])) if len(args) > 3 else size_of(src)
        todo = [(src, args[1] if len(args) > 1 else dest_of(src, dirs), w, h)]

    asyncio.run(main(todo))
