"""Download the generated Build Beyond Living lifestyle images and write full + small webp variants."""
import io
import pathlib
import urllib.request

from PIL import Image

OUT = pathlib.Path(__file__).resolve().parent.parent / "frontend" / "media" / "images" / "bbl"
BASE = "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/"

IMAGES = {
    "hero": "4a78f2c1be41768835ef144a17d2420457489b312ba2746ddc80087d3180c248.jpeg",
    "arrival": "4df4b284114f7d6a9767b09f03c4ca6197875193355df24e9841e2534411c1c5.jpeg",
    "concierge": "442be52f4b91033d5f6bcafd1afe44758e271a1dcc4cb962898c86917388775b.jpeg",
    "lounge": "af6e7f7bd11f8ba77c9080cfadfb590ac704536335609e959ab664daeedf18c7.jpeg",
    "amenity-pool": "e2a9c3b846cbe9bcc73fa667cbac3ed14b7c89e68691b3e15641b1ade4113d39.jpeg",
    "amenity-cinema": "d6854ed2a68e26f05fa0deb9713c582fefcda8e594c699619312b48dae6a6a1a.jpeg",
    "amenity-courtyard": "13b1bb9fe60650e8ba45c383d70aedb97516b3a35a13ecbdad8d096017f57baa.jpeg",
    "amenity-fitness": "e52d378d6e8091d8753b26d65d7c6a7bc5c1d7427f12bc6610e5093b14518b70.jpeg",
    "hospitality": "7c02937ef42298fa218117f9cd75181e0984f4b7533678da1145d19cc6dbb963.jpeg",
    "nb-avenue": "ff55164329b46ff2e12d0ea16823caad39db0875b0e753dd40b9a01d55ae1855.jpeg",
    "nb-dining": "6f4066dcbfabe756b105b320d22c9b50af78081e4aa9147a86bce6dbe8676b68.jpeg",
    "nb-cafe": "9829a129e47c700bed4fcc0118e2115c559d5ae500dc7834f5f153142ed0ebe3.jpeg",
    "nb-coast": "d10667764740e923ea52bd6e1c83994aa4eddd2a734cffc2ed8114db35d91a88.jpeg",
    "closing": "2de3196b14441b426d05968f3cfed5e61aa054ab3f2d9bded3b6043e26d5c446.jpeg",
}

for old in OUT.glob("*.webp"):
    old.unlink()

for name, key in IMAGES.items():
    raw = urllib.request.urlopen(BASE + key, timeout=90).read()
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.save(OUT / f"{name}.webp", "WEBP", quality=80, method=5)
    small = img.resize((760, round(img.height * 760 / img.width)), Image.LANCZOS)
    small.save(OUT / f"{name}-sm.webp", "WEBP", quality=76, method=5)
    print(name, img.size, "->", small.size)
