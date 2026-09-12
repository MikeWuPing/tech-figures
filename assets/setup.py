# -*- coding: utf-8 -*-
"""在新项目里铺开配图管线。

    python setup.py [项目根]        # 默认当前目录
    python setup.py --check         # 只探环境，不落文件

会做四件事：建目录、拷工具链、探运行环境、写一份 figs.conf 骨架。
**不覆盖已存在的文件**，重复跑是安全的。
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = "fig"                       # 工作目录名，可改

CHROME = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome", "/usr/bin/chromium",
]

CONF = """# 模板前缀 → 输出目录（相对项目根）
# 必须和文章里的 ![]() 引用路径一致。先看文章怎么引用，再定这里。
# 没列出的前缀默认落到 figs/
#
# gen  = figs
# ddr  = figs/ddr
# pkg  = figs/pkg
"""


def probe():
    ok = True

    print("运行环境：")
    exe = next((p for p in CHROME if os.path.exists(p)), None)
    print("  Chrome/Edge   %s" % (exe or "**没找到** —— render.py 需要它"))
    ok &= bool(exe)

    try:
        import playwright
        from playwright.sync_api import sync_playwright  # noqa
        print("  playwright    已安装")
    except ImportError:
        print("  playwright    **没装** —— pip install playwright")
        ok = False

    try:
        from PIL import Image  # noqa
        print("  Pillow        已安装")
    except ImportError:
        print("  Pillow        **没装** —— pip install pillow（make_bg.py 需要）")

    try:
        import numpy  # noqa
        print("  numpy         已安装")
    except ImportError:
        print("  numpy         **没装** —— pip install numpy")

    # 中文字体
    try:
        from matplotlib import font_manager
        names = {f.name for f in font_manager.fontManager.ttflist}
        got = [n for n in ("Noto Serif SC", "Noto Sans SC") if n in names]
        if len(got) == 2:
            print("  思源字体      宋体 + 黑体 都在")
        else:
            miss = {"Noto Serif SC", "Noto Sans SC"} - set(got)
            print("  思源字体      **缺 %s** —— 去 Google Fonts 下载装上" % "、".join(miss))
            ok = False
    except ImportError:
        print("  思源字体      跳过（没装 matplotlib，无法探测）")

    # ComfyUI（可选）
    desktop = os.path.expanduser("~/AppData/Local/Comfy-Desktop/ComfyUI-Installs")
    found = []
    if os.path.isdir(desktop):
        for d in os.listdir(desktop):
            m = os.path.join(desktop, d, "ComfyUI", "main.py")
            if os.path.exists(m):
                found.append(m)
    if found:
        print("  ComfyUI       找到 %d 份安装（用 GPU 前务必验 torch 是不是 CUDA 版，" % len(found))
        print("                见 references/ai-images.md）")
    else:
        print("  ComfyUI       没找到（可选，只影响 AI 生图）")

    return ok


def install(root):
    fig = os.path.join(root, FIG)
    for d in (fig, os.path.join(fig, "t"), os.path.join(fig, "_asset")):
        os.makedirs(d, exist_ok=True)

    copied, skipped = [], []
    for f in os.listdir(HERE):
        if f == "setup.py" or not f.endswith((".py", ".css", ".js")):
            continue
        dst = os.path.join(fig, f)
        if os.path.exists(dst):
            skipped.append(f)
        else:
            shutil.copy2(os.path.join(HERE, f), dst)
            copied.append(f)

    conf = os.path.join(root, "figs.conf")
    if not os.path.exists(conf):
        open(conf, "w", encoding="utf-8").write(CONF)

    print("\n铺设完成 -> %s" % fig)
    if copied:
        print("  拷入  %s" % "、".join(sorted(copied)))
    if skipped:
        print("  跳过  %s（已存在，没动）" % "、".join(sorted(skipped)))
    print("  模板放 %s/t/*.html，素材放 %s/_asset/" % (FIG, FIG))
    print("  渲染   python %s/render.py --all" % FIG)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--check":
        sys.exit(0 if probe() else 1)
    root = os.path.abspath(args[0]) if args else os.getcwd()
    probe()
    install(root)
