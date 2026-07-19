#!/usr/bin/env python3
"""Generate the Saturdays "Horizon Arc" app icon with Pillow.

A 240-degree circular sweep (the top 120 degrees left open) on true black,
with a dark-slate inactive track under an accent-colored active arc and a
glowing white leading dot at the arc's terminus. Renders both the amber
(default) and indigo (alternate) brand variants at 1024x1024.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))

SIZE = 1024
SS = 4  # supersample factor for crisp, anti-aliased strokes

BLACK = (0, 0, 0, 255)
TRACK = (30, 41, 59, 255)    # #1E293B — dark slate, inactive track
WHITE = (255, 255, 255, 255)

AMBER = (240, 160, 75, 255)   # #F0A04B — Live Amber
INDIGO = (99, 102, 241, 255)  # #6366F1 — Indigo Iris

STROKE_FRAC = 64 / 1024   # 64px stroke at 1024 canvas
DOT_FRAC = 80 / 1024      # 80px leading-dot diameter at 1024 canvas
GLOW_BLUR_FRAC = 12 / 1024  # 12px blur at 1024 canvas

# PIL's arc() measures 0deg at 3 o'clock, increasing clockwise (y-down).
# -30 -> 210 sweeps 240 degrees through the bottom of the circle, leaving a
# 120-degree gap centered on the top (between 210 and 330/-30).
ARC_START = -30
ARC_END = 210


def _arc_layer(size, color, stroke, cx, cy, radius):
    # PIL's arc(..., width=) approximates thick strokes with sampled line
    # segments, which leaves a faceted, imprecise cut at the endpoints.
    # A pieslice with the inner circle punched out gives an exact radial
    # edge instead, so the round-cap circles stamped on top align flush.
    outer_r = radius + stroke / 2
    inner_r = radius - stroke / 2
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.pieslice(
        [cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
        ARC_START, ARC_END, fill=color,
    )
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=(0, 0, 0, 0))

    r = stroke / 2
    for angle_deg in (ARC_START, ARC_END):
        a = math.radians(angle_deg)
        x = cx + radius * math.cos(a)
        y = cy + radius * math.sin(a)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
    return layer


def build_icon(accent):
    W = SIZE * SS
    stroke = round(W * STROKE_FRAC)
    pad = stroke / 2 + W * 0.06
    cx = cy = W / 2
    radius = W / 2 - pad

    canvas = Image.new("RGBA", (W, W), BLACK)
    canvas.alpha_composite(_arc_layer(W, TRACK, stroke, cx, cy, radius))
    canvas.alpha_composite(_arc_layer(W, accent, stroke, cx, cy, radius))

    # Leading dot at the arc's terminus, with an accent-colored glow behind it.
    a = math.radians(ARC_START)
    dot_x = cx + radius * math.cos(a)
    dot_y = cy + radius * math.sin(a)
    dot_r = W * DOT_FRAC / 2

    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    glow_r = dot_r * 1.9
    gdraw.ellipse(
        [dot_x - glow_r, dot_y - glow_r, dot_x + glow_r, dot_y + glow_r],
        fill=(accent[0], accent[1], accent[2], 170),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=W * GLOW_BLUR_FRAC))
    canvas.alpha_composite(glow)

    dot = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(dot)
    ddraw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=WHITE)
    canvas.alpha_composite(dot)

    canvas = canvas.resize((SIZE, SIZE), Image.LANCZOS)
    return canvas.convert("RGB")  # flatten onto black — App Store icons need no alpha


# Classic iOS icon point sizes (the asset catalog here uses a single 1024
# "universal" master and Xcode derives these at build time, but they're
# generated too for reference / marketing use).
IOS_SIZES = (20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024)


def main():
    variants = {"amber": AMBER, "indigo": INDIGO}
    for name, color in variants.items():
        icon = build_icon(color)
        path = os.path.join(HERE, f"icon-{name}-1024.png")
        icon.save(path)
        print("wrote", path)

        size_dir = os.path.join(HERE, "ios-sizes", name)
        os.makedirs(size_dir, exist_ok=True)
        for sz in IOS_SIZES:
            resized = icon.resize((sz, sz), Image.LANCZOS)
            resized.save(os.path.join(size_dir, f"icon-{sz}.png"))
        print(f"wrote {len(IOS_SIZES)} sizes to {size_dir}")


if __name__ == "__main__":
    main()
