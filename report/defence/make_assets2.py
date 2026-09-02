"""Assets for the light-theme lecture deck (v2).

  figs/bg2_main.png   soft light gradient with a gentle teal glow
  figs/bg2_hero.png   slightly deeper light gradient, two glows
  figs/wave_teal.png  teal gradient waveform ribbon (transparent)
  figs/adc_wave.png   analog wave -> sampled bars illustration
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).parent / "figs"
OUT.mkdir(exist_ok=True)
W, H = 1920, 1080


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


def glow(img, cx, cy, r, color, blend=0.35):
    layer = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.6))
    return Image.blend(img, layer, blend)


def bg_main():
    img = vgrad((250, 252, 254), (235, 242, 247))
    img = glow(img, int(W * 0.88), int(H * 0.10), 380, (208, 236, 238), 0.30)
    img.save(OUT / "bg2_main.png")


def bg_hero():
    img = vgrad((246, 250, 253), (228, 238, 245))
    img = glow(img, int(W * 0.18), int(H * 0.18), 470, (198, 232, 234), 0.35)
    img = glow(img, int(W * 0.85), int(H * 0.85), 520, (214, 238, 232), 0.30)
    img.save(OUT / "bg2_hero.png")


def wave_teal():
    ww, wh = 1920, 340
    img = Image.new("RGBA", (ww, wh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    n = 74
    bw = 12
    gap = (ww - n * bw) / (n + 1)
    c1 = (2, 128, 144)
    c2 = (124, 197, 184)
    for i in range(n):
        t = abs(math.sin(i * 0.53) * 0.65 + math.sin(i * 0.19) * 0.35)
        h = int(26 + t * (wh - 52))
        x = int(gap + i * (bw + gap))
        col = lerp(c1, c2, i / (n - 1))
        alpha = int(110 + t * 120)
        d.rounded_rectangle([x, wh - h, x + bw, wh], radius=6,
                            fill=col + (alpha,))
    img.save(OUT / "wave_teal.png")


def adc_wave():
    """Left: smooth analog wave. Right: the same wave as sampled bars."""
    ww, wh = 1600, 640
    img = Image.new("RGBA", (ww, wh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    TEAL = (2, 128, 144, 255)
    CORAL = (233, 90, 90, 255)
    GRAY = (110, 130, 145, 255)
    mid = wh // 2
    half = ww // 2 - 60

    def f(u):  # composite wave, u in 0..1
        return (math.sin(u * 6.0 * math.pi) * 0.55
                + math.sin(u * 15.0 * math.pi) * 0.25
                + math.sin(u * 2.0 * math.pi) * 0.20)

    # analog: smooth polyline
    pts = []
    for i in range(0, half, 3):
        u = i / half
        pts.append((40 + i, mid - int(f(u) * (wh * 0.36))))
    d.line(pts, fill=TEAL, width=9, joint="curve")
    d.line([(40, mid), (40 + half, mid)], fill=GRAY, width=2)

    # arrow between halves
    ax = ww // 2
    d.line([(ax - 24, mid), (ax + 24, mid)], fill=GRAY, width=8)
    d.polygon([(ax + 24, mid - 16), (ax + 24, mid + 16), (ax + 48, mid)],
              fill=GRAY)

    # digital: sampled stems + dots
    x0 = ww // 2 + 80
    n = 22
    for i in range(n):
        u = i / (n - 1)
        x = x0 + int(u * (half - 40))
        y = mid - int(f(u) * (wh * 0.36))
        d.line([(x, mid), (x, y)], fill=CORAL, width=6)
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=CORAL)
    d.line([(x0, mid), (x0 + half - 40, mid)], fill=GRAY, width=2)

    img.save(OUT / "adc_wave.png")


if __name__ == "__main__":
    bg_main()
    bg_hero()
    wave_teal()
    adc_wave()
    print("assets v2 done")
