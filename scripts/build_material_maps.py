"""Builds the design-page material maps: albedo, normal and roughness.

Nero Portoro is delivered as two consecutive slabs; the bookmatch itself is done
in the viewer by mirroring the second slab's UVs, so the scan stays a single slab.
"""
import io
import urllib.request

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

OUT = "/app/frontend/media/images/design/"
JOB = "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/"

SRC = {
    "walnut": JOB + "ba85cee7208675f07e74f96323f13371dbcd511f82b510657d9fb8685376d7e7.jpeg",
    "pietra": JOB + "cf0809a956dec43835044a879dcaa49bbe63a13f4f74948b0631fe20eb0a0163.jpeg",
    "bronze": JOB + "e084464d8e49d2cc2adf1af434c5ec751278c5198d5aa6d2e430f413208e4405.jpeg",
    "leather": JOB + "f222b988d76b3883bc318f34bf96a2b10787f02377738db9fae01e3eaca105bf.jpeg",
}

# normal strength, roughness floor, roughness span, invert luminance, rgb gain
GRADE = {
    "walnut": (1.8, 0.40, 0.16, True, (1.0, 0.98, 0.96)),
    "pietra": (1.0, 0.40, 0.14, True, (0.99, 1.0, 1.02)),
    "bronze": (1.3, 0.20, 0.22, True, (1.42, 1.20, 0.98)),
    "leather": (2.0, 0.64, 0.18, True, (0.84, 0.86, 0.94)),
}


def fetch(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=90).read())).convert("RGB")


def grade(img: Image.Image, gain) -> Image.Image:
    arr = np.asarray(img, dtype=np.float32) * np.array(gain, dtype=np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def soft_bookmatch(img: Image.Image, strength: float = 0.5, spread: float = 0.2) -> Image.Image:
    """Blends a mirrored copy of the field into the middle of the slab so a quiet
    mirrored relationship reads on close inspection, with no axis, seam or V."""
    a = np.asarray(img, dtype=np.float32)
    b = a[:, ::-1, :]
    x = np.linspace(0, 1, a.shape[1], dtype=np.float32)
    w = strength * np.exp(-((x - 0.5) ** 2) / (2 * spread * spread))
    mask = w[None, :, None]
    return Image.fromarray(np.clip(a * (1 - mask) + b * mask, 0, 255).astype(np.uint8), "RGB")


def normal_map(img: Image.Image, strength: float) -> Image.Image:
    grey = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(0.7)), dtype=np.float32) / 255.0
    dx = np.gradient(grey, axis=1) * strength * 8.0
    dy = np.gradient(grey, axis=0) * strength * 8.0
    nz = np.ones_like(grey)
    length = np.sqrt(dx * dx + dy * dy + nz * nz)
    rgb = np.stack([(-dx / length + 1) * 0.5, (dy / length + 1) * 0.5, (nz / length + 1) * 0.5], axis=-1)
    return Image.fromarray((rgb * 255).astype(np.uint8), "RGB")


def roughness_map(img: Image.Image, floor: float, span: float, invert: bool) -> Image.Image:
    grey = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(1.4)), dtype=np.float32) / 255.0
    lo, hi = np.percentile(grey, 3), np.percentile(grey, 97)
    grey = np.clip((grey - lo) / max(hi - lo, 1e-4), 0, 1)
    if invert:
        grey = 1.0 - grey
    out = floor + grey * span
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "L").convert("RGB")


for name, url in SRC.items():
    strength, floor, span, invert, gain = GRADE[name]
    img = grade(fetch(url).resize((1024, 1024), Image.LANCZOS), gain)
    if name == "leather":
        img = ImageEnhance.Color(img).enhance(0.62)
    if name == "pietra":
        img = ImageEnhance.Color(img).enhance(0.68)
    if name == "pietra":
        img = soft_bookmatch(img)
    img.save(f"{OUT}tex-{name}.webp", "WEBP", quality=82, method=6)
    normal_map(img, strength).resize((512, 512), Image.LANCZOS).save(
        f"{OUT}tex-{name}-n.webp", "WEBP", quality=80, method=6)
    roughness_map(img, floor, span, invert).resize((384, 384), Image.LANCZOS).save(
        f"{OUT}tex-{name}-r.webp", "WEBP", quality=72, method=6)
    print("built", name)
