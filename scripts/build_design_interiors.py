"""Replaces the two design-page interior photographs with the commissioned set."""
import io
import urllib.request

from PIL import Image

OUT = "/app/frontend/media/images/design/"
SRC = {
    "proportion-interior": "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/e8fb0a0e2b21147bbc5214dcaf581deefc39f72d03993c44ce4cea130caf1a38.jpeg",
    "light-wide": "https://static.prod-images.emergentagent.com/jobs/98214041-2973-42cf-b923-136a486faf23/images/109cba7a718bb88d8567ca6fb8bd751a16c5f12c9af7a45243aba49801305f85.jpeg",
}

for name, url in SRC.items():
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    img = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=90).read())).convert("RGB")
    img = img.resize((1264, 848), Image.LANCZOS)
    img.save(f"{OUT}{name}.webp", "WEBP", quality=86, method=6)
    print("wrote", name, img.size)
