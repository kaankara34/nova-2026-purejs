"""Builds the design-page material register maps: albedo, normal and roughness."""
import io
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageFilter

OUT = "/app/frontend/media/images/design/"

SRC = {
    "walnut": "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/e03815e4a1aecc445dac08d1701749824e60d491265e8cb6093e8f360c5feba6.jpeg",
    "stone": "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/eb5684b5bc6148fb6c9dd92cf3e8034438744db29f82f173bfde91f83e47b990.jpeg",
    "bronze": "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/13ab4a2c2526d23ff9045c006064ab64a9aebc4bec862d4fdf835fdaf259f3e9.jpeg",
    "leather": "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/49c4cf02092989c53e3b877cb1013aa4aad8b3346db2bfa550730b9f851f16d5.jpeg",
}

# per material: (normal strength, roughness floor, roughness span, invert luminance)
GRADE = {
    "walnut": (2.6, 0.36, 0.20, True),
    "stone": (1.1, 0.14, 0.12, True),
    "bronze": (2.2, 0.30, 0.26, True),
    "leather": (3.4, 0.58, 0.22, True),
}


def fetch(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=90).read()
    return Image.open(io.BytesIO(data)).convert("RGB")


def bookmatch(img: Image.Image, size: int = 1024) -> Image.Image:
    """Two consecutive slabs opened around a central seam."""
    img = img.resize((size, size), Image.LANCZOS)
    half = img.crop((size // 4, 0, size // 4 + size // 2, size))
    out = Image.new("RGB", (size, size))
    out.paste(half.transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    out.paste(half, (size // 2, 0))
    return out


def normal_map(img: Image.Image, strength: float) -> Image.Image:
    grey = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255.0
    dx = np.gradient(grey, axis=1) * strength * 8.0
    dy = np.gradient(grey, axis=0) * strength * 8.0
    nz = np.ones_like(grey)
    length = np.sqrt(dx * dx + dy * dy + nz * nz)
    rgb = np.stack([(-dx / length + 1) * 0.5, (dy / length + 1) * 0.5, (nz / length + 1) * 0.5], axis=-1)
    return Image.fromarray((rgb * 255).astype(np.uint8), "RGB")


def roughness_map(img: Image.Image, floor: float, span: float, invert: bool) -> Image.Image:
    grey = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255.0
    lo, hi = np.percentile(grey, 3), np.percentile(grey, 97)
    grey = np.clip((grey - lo) / max(hi - lo, 1e-4), 0, 1)
    if invert:
        grey = 1.0 - grey
    out = floor + grey * span
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "L").convert("RGB")


def main() -> None:
    for name, url in SRC.items():
        img = fetch(url)
        img = bookmatch(img) if name == "stone" else img.resize((1024, 1024), Image.LANCZOS)
        strength, floor, span, invert = GRADE[name]
        img.save(f"{OUT}tex-{name}.webp", "WEBP", quality=82, method=6)
        normal_map(img, strength).resize((512, 512), Image.LANCZOS).save(
            f"{OUT}tex-{name}-n.webp", "WEBP", quality=80, method=6)
        roughness_map(img, floor, span, invert).resize((384, 384), Image.LANCZOS).save(
            f"{OUT}tex-{name}-r.webp", "WEBP", quality=72, method=6)
        print("built", name)


if __name__ == "__main__":
    sys.exit(main())
