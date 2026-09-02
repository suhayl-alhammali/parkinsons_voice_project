"""Assets for deck v3 — 'sound ripples' design (violet + amber).

  figs/bg3_light.png  near-white bg, faint violet tint, ripple rings corner
  figs/bg3_dark.png   deep violet gradient, rings, soft glow
  figs/adc3.png       analog wave (violet) -> sampled stems (amber)
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).parent / "figs"
OUT.mkdir(exist_ok=True)
W, H = 1920, 1080

VIOLET = (67, 48, 122)
DEEP1 = (42, 30, 79)
DEEP2 = (23, 16, 52)
AMBER = (242, 169, 59)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        c = lerp(top, bottom, y / (H - 1))
        for x in range(W):
            px[x, y] = c
    return img


def rings(draw, cx, cy, radii, color, width=10):
    for r in radii:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=color, width=width)


def bg_light():
    img = vgrad((252, 251, 254), (242, 239, 249))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rings(d, W + 60, -60, range(120, 760, 110), VIOLET + (26,), 12)
    rings(d, -80, H + 80, range(120, 560, 110), VIOLET + (18,), 12)
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    img.save(OUT / "bg3_light.png")


def bg_dark():
    img = vgrad(DEEP1, DEEP2)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.6, -300, W * 1.15, 420], fill=(66, 46, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(260))
    img = Image.blend(img, Image.blend(img, glow, 0.55), 0.7)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rings(d, W + 40, -40, range(130, 900, 120), (255, 255, 255, 16), 12)
    rings(d, -60, H + 60, range(130, 640, 120), AMBER + (22,), 12)
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    img.save(OUT / "bg3_dark.png")


def adc3():
    ww, wh = 1600, 620
    img = Image.new("RGBA", (ww, wh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    GRAY = (140, 135, 165, 255)
    mid = wh // 2
    half = ww // 2 - 60

    def f(u):
        return (math.sin(u * 6.0 * math.pi) * 0.55
                + math.sin(u * 15.0 * math.pi) * 0.25
                + math.sin(u * 2.0 * math.pi) * 0.20)

    pts = []
    for i in range(0, half, 3):
        u = i / half
        pts.append((40 + i, mid - int(f(u) * (wh * 0.36))))
    d.line(pts, fill=VIOLET + (255,), width=9, joint="curve")
    d.line([(40, mid), (40 + half, mid)], fill=GRAY, width=2)

    ax = ww // 2
    d.line([(ax - 24, mid), (ax + 24, mid)], fill=GRAY, width=8)
    d.polygon([(ax + 24, mid - 16), (ax + 24, mid + 16), (ax + 48, mid)],
              fill=GRAY)

    x0 = ww // 2 + 80
    n = 22
    for i in range(n):
        u = i / (n - 1)
        x = x0 + int(u * (half - 40))
        y = mid - int(f(u) * (wh * 0.36))
        d.line([(x, mid), (x, y)], fill=AMBER + (255,), width=6)
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=AMBER + (255,))
    d.line([(x0, mid), (x0 + half - 40, mid)], fill=GRAY, width=2)
    img.save(OUT / "adc3.png")


if __name__ == "__main__":
    bg_light()
    bg_dark()
    adc3()
    print("assets v3 done")
