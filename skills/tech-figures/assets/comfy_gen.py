# -*- coding: utf-8 -*-
"""本地 ComfyUI 调用器 —— 走 /prompt HTTP API，无需打开网页

用法：
    python comfy_gen.py "prompt 文本" out.png [宽 高 步数 种子]

依赖：ComfyUI 已在 127.0.0.1:8188 运行（torch cu130 那个 venv）。
"""
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import uuid

HOST = "http://127.0.0.1:8188"
CLIENT = str(uuid.uuid4())


def post(path, payload):
    req = urllib.request.Request(
        HOST + path, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def get(path, **params):
    url = HOST + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def build(prompt, w, h, steps, seed, ckpt_unet, clip_name, vae_name, cfg, neg="",
          clip_type="ideogram4", shift=None):
    """组装一个标准 txt2img 图：UNET+CLIP+VAE 分离加载 → 采样 → 解码 → 存盘

    shift: 若给出，则在采样前插一个 ModelSamplingAuraFlow 节点。
           Lumina2 系（含 Z-Image）靠它设 shift，官方取值 3.0。
    """
    g = {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": ckpt_unet, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": clip_name, "type": clip_type, "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": vae_name}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode",
              "inputs": {"text": neg, "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": w, "height": h, "batch_size": 1}},
        "7": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0],
                         "latent_image": ["6", 0], "seed": seed, "steps": steps,
                         "cfg": cfg, "sampler_name": "euler", "scheduler": "simple",
                         "denoise": 1.0}},
        "8": {"class_type": "VAEDecode",
              "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"images": ["8", 0], "filename_prefix": "apigen"}},
    }
    if shift is not None:
        g["10"] = {"class_type": "ModelSamplingAuraFlow",
                   "inputs": {"model": ["1", 0], "shift": shift}}
        g["7"]["inputs"]["model"] = ["10", 0]
    return g


# 两套模型栈。Z-Image 是 turbo 蒸馏模型：步数少、CFG 必须 1.0。
STACKS = {
    "ideogram": dict(ckpt_unet="ideogram4_fp8_scaled.safetensors",
                     clip_name="qwen3vl_8b_fp8_scaled.safetensors",
                     vae_name="flux2-vae.safetensors",
                     clip_type="ideogram4", shift=None, steps=26, cfg=1.0),
    "zimage":   dict(ckpt_unet="z_image_turbo_bf16.safetensors",
                     clip_name="qwen_3_4b.safetensors",
                     vae_name="ae.safetensors",
                     clip_type="qwen_image", shift=3.0, steps=10, cfg=1.0),
}


def run(graph, timeout=600):
    r = post("/prompt", {"prompt": graph, "client_id": CLIENT})
    pid = r["prompt_id"]
    print("  已提交 prompt_id =", pid)
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        hist = json.loads(get("/history/" + pid).decode("utf-8"))
        if pid in hist:
            h = hist[pid]
            st = h.get("status", {})
            if st.get("status_str") == "error" or not st.get("completed", True):
                print("  !! 执行出错：")
                for m in st.get("messages", []):
                    print("     ", m)
                return None
            outs = []
            for nid, out in h.get("outputs", {}).items():
                for im in out.get("images", []):
                    outs.append(im)
            print("  完成，用时 %.1fs" % (time.time() - t0))
            return outs
        # 显示队列状态
        q = json.loads(get("/queue").decode("utf-8"))
        if not q.get("queue_running") and not q.get("queue_pending"):
            print("  队列空但无结果，可能已失败")
            return None
    print("  超时")
    return None


def fetch(im, dest):
    data = get("/view", filename=im["filename"], subfolder=im.get("subfolder", ""),
               type=im.get("type", "output"))
    with open(dest, "wb") as f:
        f.write(data)
    print("  已保存:", dest, "(%d 字节)" % len(data))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    # 位置参数：提示词 输出 [宽 高 步数 种子 cfg]
    # 可选：--model zimage|ideogram   默认 zimage（出图快、少长伪文字）
    model = "zimage"
    if "--model" in a:
        i = a.index("--model")
        model = a[i + 1]
        a = a[:i] + a[i + 2:]
    st = STACKS[model]

    prompt, dest = a[0], a[1]
    w = int(a[2]) if len(a) > 2 else 1024
    h = int(a[3]) if len(a) > 3 else 1024
    steps = int(a[4]) if len(a) > 4 else st["steps"]
    seed = int(a[5]) if len(a) > 5 else 0
    cfg = float(a[6]) if len(a) > 6 else st["cfg"]

    g = build(prompt, w, h, steps, seed,
              ckpt_unet=st["ckpt_unet"], clip_name=st["clip_name"],
              vae_name=st["vae_name"], cfg=cfg,
              clip_type=st["clip_type"], shift=st["shift"])
    outs = run(g)
    if outs:
        fetch(outs[0], dest)
