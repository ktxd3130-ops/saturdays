#!/usr/bin/env python3
"""Generate Saturdays app icon + splash: a solid 7-point "shooting star"
(Composition B — spiky, short tail aimed at the bottom-left so it reads as
shooting up and to the right = growth). Supersampled 4x then downscaled for
crisp, anti-aliased edges.

Icon:   white star on indigo.
Splash: indigo star on the app's light ground (dark variant = light-indigo on slate)."""
import os
import math
from PIL import Image, ImageDraw

# ---- Brand colors ----
INDIGO      = (79, 70, 229)     # #4f46e5  — brand accent (Clinical deep indigo)
INDIGO_SOFT = (130, 128, 240)   # #8280f0  — lifted indigo for dark grounds
WHITE       = (255, 255, 255)
CLINICAL_BG = (246, 248, 252)   # #f6f8fc  — Clinical light ground (splash light)
SLATE_BG    = (20, 22, 29)      # #14161d  — Slate dark ground (splash dark)

# ---- Star geometry (Composition B, approved) ----
PTS   = 7
ROT   = math.radians(135)       # elongated point aims down-left -> shoots up-right
OUTER = 24.0
APEX  = 1.65                    # tail length multiplier on the elongated point
FAT   = 0.40                    # inner/outer ratio — spiky elegant
SS    = 4                       # supersample factor

HERE = os.path.dirname(os.path.abspath(__file__))


def star_points(span):
    """Star polygon vertices in a 0..100 box, auto-centered on (50,50) and
    scaled so its bounding box spans `span` units. Returns list of (x, y)."""
    inner = OUTER * FAT
    O, I = [], []
    for i in range(PTS):
        aO = ROT + i * 2 * math.pi / PTS
        ro = OUTER * (APEX if i == 0 else 1)
        O.append((50 + math.cos(aO) * ro, 50 + math.sin(aO) * ro))
        aI = aO + math.pi / PTS
        I.append((50 + math.cos(aI) * inner, 50 + math.sin(aI) * inner))
    xs = [p[0] for p in O]; ys = [p[1] for p in O]
    bcx = (min(xs) + max(xs)) / 2; bcy = (min(ys) + max(ys)) / 2
    s = span / max(max(xs) - min(xs), max(ys) - min(ys))
    pts = []
    for i in range(PTS):
        for P in (O[i], I[i]):
            pts.append((50 + (P[0] - bcx) * s, 50 + (P[1] - bcy) * s))
    return pts


def render(size, bg, star, span):
    """Render the star at `size` px. bg=None -> transparent RGBA ground."""
    W = size * SS
    if bg is None:
        img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    else:
        img = Image.new("RGB", (W, W), bg)
    d = ImageDraw.Draw(img)
    pts = [(x / 100 * W, y / 100 * W) for (x, y) in star_points(span)]
    d.polygon(pts, fill=star)
    return img.resize((size, size), Image.LANCZOS)


def main():
    # App icon — 1024, no alpha (App Store requirement). Bold white star, span 80.
    render(1024, INDIGO, WHITE, span=80).save(os.path.join(HERE, "icon-only.png"))
    # Android adaptive: transparent foreground star + solid indigo background.
    render(1024, None, WHITE, span=76).save(os.path.join(HERE, "icon-foreground.png"))
    Image.new("RGB", (1024, 1024), INDIGO).save(os.path.join(HERE, "icon-background.png"))

    # Splash — 2732 square, smaller centered mark. Light = indigo on clinical;
    # dark = lifted indigo on slate.
    render(2732, CLINICAL_BG, INDIGO, span=26).save(os.path.join(HERE, "splash.png"))
    render(2732, SLATE_BG, INDIGO_SOFT, span=26).save(os.path.join(HERE, "splash-dark.png"))
    print("wrote icon-only / icon-foreground / icon-background / splash / splash-dark")


if __name__ == "__main__":
    main()
