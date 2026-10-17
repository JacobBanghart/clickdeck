"""Render the full device's side profile at several tilt angles, side by side.

    .venv/bin/python cad/angle_compare.py 20 35 45 55
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import model  # noqa: E402
import params as P  # noqa: E402
import render  # noqa: E402

OUT = Path(__file__).parent / "out"


def main():
    angles = [float(a) for a in sys.argv[1:]] or [20, 35, 45, 55]
    tiles = []
    for a in angles:
        P.TILT_DEG = a
        items, _, info = model.full_device()
        path = OUT / f"_angle_{a:g}.png"
        render.render(items, str(path), az=0, el=0, size=(700, 560), ss=1, margin=0.02)
        tiles.append((a, Image.open(path), info["tilted_mm"]))
        path.unlink()

    # Same scale for every tile would need a shared camera; instead label sizes.
    w, h = 700, 560
    cols = min(len(tiles), 2)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 50)), (245, 245, 247))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    for i, (a, img, (wid, dep, hei)) in enumerate(tiles):
        x, y = (i % cols) * w, (i // cols) * (h + 50)
        sheet.paste(img, (x, y + 50))
        draw.text((x + 20, y + 12), f"{a:g}°   {dep:g} mm deep x {hei:g} mm tall",
                  fill=(20, 20, 25), font=font)
    sheet.save(OUT / "angle_compare.png")
    print("wrote", OUT / "angle_compare.png")


if __name__ == "__main__":
    main()
