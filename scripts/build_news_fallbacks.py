"""Generates the local NOVA editorial category covers used when no lawful, sharp
article image is available. Abstract/typographic only — never a pretend photograph.
Run: python3 scripts/build_news_fallbacks.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/app/frontend/media/news/fallback"
CATEGORIES = {
    "ART": ("Art", (0.18, 0.62)),
    "EXHIBITIONS": ("Exhibitions", (0.30, 0.48)),
    "GALLERIES_AND_MUSEUMS": ("Galleries & Museums", (0.22, 0.55)),
    "ARCHITECTURE_AND_DESIGN": ("Architecture & Design", (0.40, 0.34)),
    "CONSTRUCTION": ("Construction", (0.52, 0.28)),
    "URBAN_TRANSFORMATION": ("Urban Transformation", (0.36, 0.44)),
    "KADIKOY": ("Kadıköy", (0.26, 0.58)),
    "TECHNICAL_AND_LEGAL": ("Technical & Legal", (0.46, 0.32)),
}
GROUND = (239, 238, 236)
INK = (33, 37, 41)
BRONZE = (111, 98, 67)
SIZES = {"card": (1200, 750), "detail": (1600, 900)}

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_cover(key, label, weights, size):
    w, h = size
    img = Image.new("RGB", (w, h), GROUND)
    d = ImageDraw.Draw(img)
    a, b = weights

    # Structured architectural field: stacked bronze hairlines + one solid block.
    d.rectangle([0, 0, int(w * a), h], fill=(226, 224, 219))
    d.rectangle([int(w * a), 0, int(w * a) + max(2, w // 600), h], fill=BRONZE)
    step = h / 26
    for i in range(1, 26):
        y = int(i * step)
        thin = max(1, w // 1400)
        x0 = int(w * a) + int(w * 0.04)
        x1 = x0 + int(w * b * (0.35 + 0.65 * ((i * 7) % 11) / 11))
        d.rectangle([x0, y, x1, y + thin], fill=(206, 203, 196))
    block_w = int(w * 0.16)
    d.rectangle([int(w * a) - block_w, int(h * 0.62), int(w * a) - int(block_w * 0.25), h],
                fill=BRONZE)

    pad = int(w * 0.055)
    d.text((pad, int(h * 0.12)), "NOVA JOURNAL", font=font(int(h * 0.032)), fill=BRONZE)
    label_font = font(int(h * 0.072))
    lines = label.split(" & ")
    text = label if len(lines) == 1 else lines[0] + " &"
    d.text((pad, int(h * 0.20)), text.upper(), font=label_font, fill=INK)
    if len(lines) > 1:
        d.text((pad, int(h * 0.20) + int(h * 0.085)), lines[1].upper(), font=label_font, fill=INK)
    d.rectangle([pad, int(h * 0.42), pad + int(w * 0.07), int(h * 0.42) + max(1, h // 500)],
                fill=BRONZE)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for key, (label, weights) in CATEGORIES.items():
        for variant, size in SIZES.items():
            path = f"{OUT}/{key.lower().replace('_', '-')}-{variant}.webp"
            draw_cover(key, label, weights, size).save(path, "WEBP", quality=88, method=6)
            print(path)


if __name__ == "__main__":
    main()
