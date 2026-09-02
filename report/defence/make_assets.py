"""Backgrounds and decorative art for the premium deck (PIL).

Generates:
  figs/bg_main.png    dark navy gradient with a soft blue glow (content slides)
  figs/bg_hero.png    deeper gradient with two glows (title/statement slides)
  figs/wave_hero.png  smooth gradient waveform ribbon (title/closing)
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).parent / "figs"
OUT.mkdir(exist_ok=True)

W, H = 1920, 1080


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        c = lerp(top, bottom, y / (H - 1))
        for x in range(W):
            px[x, y] = c
    return img


def add_glow(img, cx, cy, radius, color, strength=90):
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.55))
    return Image.blend(img, Image.composite(glow, img, glow.convert("L").point(lambda v: min(v, strength))), 0.5)


def bg_main():
    img = vertical_gradient((13, 24, 42), (7, 13, 26))
    img = add_glow(img, int(W * 0.85), int(H * 0.12), 420, (24, 64, 110), 70)
    img.save(OUT / "bg_main.png")


def bg_hero():
    img = vertical_gradient((11, 21, 38), (5, 10, 20))
    img = add_glow(img, int(W * 0.22), int(H * 0.20), 500, (20, 60, 105), 80)
    img = add_glow(img, int(W * 0.80), int(H * 0.85), 560, (16, 52, 92), 70)
    img.save(OUT / "bg_hero.png")


def wave_hero():
    """Gradient waveform ribbon on transparent background."""
    ww, wh = 1920, 360
    img = Image.new("RGBA", (ww, wh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    n = 74
    bar_w = 12
    gap = (ww - n * bar_w) / (n + 1)
    c1 = (90, 180, 240)   # blue
    c2 = (37, 99, 235)    # deeper blue
    for i in range(n):
        t = abs(math.sin(i * 0.53) * 0.65 + math.sin(i * 0.19) * 0.35)
        h = int(30 + t * (wh - 60))
        x = int(gap + i * (bar_w + gap))
        col = lerp(c1, c2, i / (n - 1))
        alpha = int(120 + t * 120)
        d.rounded_rectangle([x, wh - h, x + bar_w, wh],
                            radius=6, fill=col + (alpha,))
    img.save(OUT / "wave_hero.png")


if __name__ == "__main__":
    bg_main()
    bg_hero()
    wave_hero()
    print("wrote", sorted(p.name for p in OUT.glob("bg_*.png"))
          + ["wave_hero.png"])
