# -*- coding: utf-8 -*-
"""把 AI 生成的图 / 任意照片处理成配图底纹

处理链：裁到目标比例 → 缩放 → 高斯模糊 → 去饱和 → 压暗 → 自动校准到目标亮度

自动校准是关键：前景元素的对比度是照着底图亮度调的，现有底图的均值约 30。
新底图若亮度不同，深色面板就会显得发灰或发死。这里统一校到同一个均值。

用法：
    python make_bg.py 输入.png 输出.png [模糊px 去饱和 目标均值]
"""
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def build(src, dst, width=2560, height=1440, blur=6.0, desat=0.40,
          target=30.0, crop=None, steps=24):
    im = Image.open(src).convert("RGB")
    if crop:
        im = im.crop(crop)

    # 居中裁到目标宽高比
    tr = width / height
    w, h = im.size
    if w / h > tr:
        nw = int(h * tr)
        im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / tr)
        im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))

    im = im.resize((width, height), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if desat is not None:
        im = ImageEnhance.Color(im).enhance(desat)

    # 二分校准亮度，使全图均值命中 target
    lo, hi = 0.05, 3.0
    for _ in range(steps):
        mid = (lo + hi) / 2
        a = np.asarray(ImageEnhance.Brightness(im).enhance(mid), float)
        if a.mean() < target:
            lo = mid
        else:
            hi = mid
    out = ImageEnhance.Brightness(im).enhance((lo + hi) / 2)
    out.save(dst)

    a = np.asarray(out, float)
    print("  %s -> %s" % (src.split("/")[-1], dst.split("/")[-1]))
    print("     尺寸 %dx%d  均值亮度 %.1f  RGB [%.0f,%.0f,%.0f]  模糊 %.0fpx  饱和 %.2f"
          % (out.size[0], out.size[1], a.mean(),
             a[..., 0].mean(), a[..., 1].mean(), a[..., 2].mean(), blur, desat))


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    kw = {}
    if len(a) > 2:
        kw["blur"] = float(a[2])
    if len(a) > 3:
        kw["desat"] = float(a[3])
    if len(a) > 4:
        kw["target"] = float(a[4])
    build(a[0], a[1], **kw)
