#!/usr/bin/env python3
"""Generate Saturdays app icon + splash from the app's own visual language:
near-black background, amber 'life in weeks' dot grid glowing from the center.
Supersampled 2x then downscaled for crisp, anti-aliased dots."""
import os
from PIL import Image, ImageDraw

BG_TOP   = (10, 10, 11)     # #0a0a0b  — app --bg
BG_BOT   = (22, 18, 16)     # #161210  — share-canvas bottom
AMBER    = (240, 160, 75)   # #f0a04b  — app accent
DIM      = (54, 48, 42)     # dim ember for "remaining" dots
SS       = 2                # supersample factor

HERE = os.path.dirname(os.path.abspath(__file__))


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(w, h):
    """Vertical background gradient."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        c = lerp(BG_TOP, BG_BOT, y / max(1, h - 1))
        for x in range(w):
            px[x, y] = c
    return img


def radial_glow(img, cx, cy, radius, color, strength):
    """Additive amber radial glow blended over the background."""
    w, h = img.size
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gp = glow.load()
    for y in range(h):
        for x in range(w):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            t = max(0.0, 1.0 - d / radius)
            t = t * t  # falloff
            if t > 0:
                gp[x, y] = tuple(round(color[i] * t * strength) for i in range(3))
    base = img.load()
    bp = base
    for y in range(h):
        for x in range(w):
            r, g, b = bp[x, y]
            gr, gg, gb = gp[x, y]
            bp[x, y] = (min(255, r + gr), min(255, g + gg), min(255, b + gb))
    return img


def draw_grid(draw, x0, y0, area, cols, rows, fill_frac):
    """'Life in weeks' grid read top-left → bottom-right. The first `fill_frac`
    of cells are weeks lived (bright amber); the rest are weeks remaining (dim
    ember). A one-cell feather softens the boundary so it glows rather than
    snaps. This is the memento-mori story, legible even at 60px."""
    cell = area / cols
    r = cell * 0.36          # dots nearly touch, echoing the app's tight grid
    total = cols * rows
    edge = fill_frac * total
    for idx in range(total):
        i, j = idx % cols, idx // cols
        cx = x0 + (i + 0.5) * cell
        cy = y0 + (j + 0.5) * cell
        # 1 = solidly lived, 0 = solidly remaining, smooth across ~1.5 cells
        t = max(0.0, min(1.0, (edge - idx) / 1.5 + 0.5))
        t = t ** 0.8
        color = lerp(DIM, AMBER, t)
        rr = r * (0.86 + 0.18 * t)
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color)


def build(size, cols, rows, pad_frac, fill_frac, glow_strength=0.9,
          center_glow=False):
    W = H = size * SS
    img = vgrad(W, H)
    pad = W * pad_frac
    area = W - 2 * pad
    cell = area / cols
    grid_h = cell * rows
    y0 = (H - grid_h) / 2
    if center_glow:
        gcx, gcy = W / 2, H / 2
    else:
        # Glow sits over the lived (amber) cluster so the composition is
        # intentional (a light source) rather than a centered blob.
        edge_idx = fill_frac * cols * rows
        gi, gj = (edge_idx * 0.55) % cols, (edge_idx * 0.55) // cols
        gcx = pad + (gi + 0.5) * cell
        gcy = y0 + (gj + 0.5) * cell
    img = radial_glow(img, gcx, gcy, W * 0.5, AMBER, glow_strength)
    draw = ImageDraw.Draw(img)
    draw_grid(draw, pad, y0, area, cols, rows, fill_frac)
    return img.resize((size, size), Image.LANCZOS)


def main():
    # Master icon — 1024, no alpha (App Store requirement). 8x8 grid reads at
    # 60px; ~42% lived in bright amber, the rest dim ember.
    icon = build(1024, cols=8, rows=8, pad_frac=0.18, fill_frac=0.42, glow_strength=1.0)
    icon.save(os.path.join(HERE, "icon-only.png"))
    # Android adaptive foreground/background reuse the same look (forward-looking).
    icon.save(os.path.join(HERE, "icon-foreground.png"))
    Image.new("RGB", (1024, 1024), BG_TOP).save(os.path.join(HERE, "icon-background.png"))

    # Splash — 2732 square, smaller centered mark on flat dark.
    splash = build(2732, cols=8, rows=8, pad_frac=0.36, fill_frac=0.42,
                   glow_strength=0.75, center_glow=True)
    splash.save(os.path.join(HERE, "splash.png"))
    splash.save(os.path.join(HERE, "splash-dark.png"))
    print("wrote icon-only / icon-foreground / icon-background / splash / splash-dark")


if __name__ == "__main__":
    main()
