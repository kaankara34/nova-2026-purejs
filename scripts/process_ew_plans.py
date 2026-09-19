"""Make East West floor plans transparent, trim, and normalise to one canvas."""
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path("/tmp/plans")
OUT = Path("/app/frontend/media/images/ew/plans")
OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    "east-3plus1": "t2xhqv4e.png",
    "east-4plus1": "xmy3f4x3.png",
    "east-duplex-lower": "myckmqfk.png",
    "east-duplex-upper": "pedl1ofc.png",
    "west-3plus1": "llglcuv5.png",
    "west-4plus1": "i0tzg7yt.png",
    "west-duplex-lower": "xbzywfuz.png",
    "west-duplex-upper": "ivysy09s.png",
}

CANVAS = (1240, 1860)
TARGET_W = 1180


def transparent(img: Image.Image) -> Image.Image:
    a = np.array(img.convert("RGBA")).astype(np.int16)
    rgb = a[:, :, :3]
    light = rgb.min(axis=2) > 232
    g = rgb[:, :, 1]
    greenish = (g > 205) & (g > rgb[:, :, 0] + 3) & (g > rgb[:, :, 2] + 3)
    a[:, :, 3] = np.where(light | greenish, 0, a[:, :, 3])
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def trim(img: Image.Image) -> Image.Image:
    alpha = np.array(img.getchannel("A"))
    solid = alpha > 40
    cols = np.where(solid.any(axis=0))[0]
    rows = np.where(solid.any(axis=1))[0]
    return img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))


for key, name in FILES.items():
    img = trim(transparent(Image.open(SRC / name)))
    scale = min(TARGET_W / img.width, (CANVAS[1] - 40) / img.height)
    w, h = round(img.width * scale), round(img.height * scale)
    resized = img.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.paste(resized, ((CANVAS[0] - w) // 2, (CANVAS[1] - h) // 2), resized)
    dest = OUT / f"{key}.webp"
    canvas.save(dest, format="WEBP", quality=90, method=6)
    print(key, "bytes", dest.stat().st_size, "drawn", (w, h))
