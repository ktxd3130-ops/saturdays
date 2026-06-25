#!/usr/bin/env python3
"""
generate_screenshots.py — App Store marketing screenshot generator for "Saturdays".

Draws 5 marketing screenshots (caption + illustrative app panel) entirely with
Pillow — there's no live app to capture. Each screen is rendered at two Apple-
required resolutions:

    6.7" (iPhone 15 Pro Max): 1290 x 2796
    6.1" (iPhone 15 Pro):     1179 x 2556

Output lands in:
    screenshots/6.7-inch/01-..05-*.png
    screenshots/6.1-inch/01-..05-*.png

Everything is laid out proportionally to (width, height) so both sizes look
correct from a single render function. No hardcoded coordinates for one size.

Run:
    python3 scripts/generate_screenshots.py
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
# Palette — pulled exactly from the Saturdays app aesthetic.
# ----------------------------------------------------------------------------
BG_TOP      = (10, 10, 11)     # #0a0a0b  near-black (top of gradient)
BG_BOTTOM   = (22, 22, 24)     # #161618  slightly lifted (bottom of gradient)
SURFACE     = (22, 22, 24)     # #161618  card / panel surface
BORDER      = (38, 38, 43)     # #26262b  hairline border
INK         = (244, 241, 234)  # #f4f1ea  primary ink (headings, big numbers)
INK_DIM     = (154, 149, 140)  # #9a958c  dim ink (body)
INK_FAINT   = (92, 88, 79)     # #5c584f  faint ink
ACCENT      = (240, 160, 75)   # #f0a04b  signature warm amber
GREEN       = (127, 176, 105)  # #7fb069
TEAL        = (122, 184, 160)  # #7ab8a0
RED         = (217, 106, 91)   # #d96a5b

# ----------------------------------------------------------------------------
# Font loading — robust against missing files. Tries a list of candidate paths
# per logical face, falls back to Pillow's default so it never crashes.
# ----------------------------------------------------------------------------
FONT_CANDIDATES = {
    "text":    ["/System/Library/Fonts/SFNS.ttf",
                "/System/Library/Fonts/HelveticaNeue.ttc",
                "/Library/Fonts/Arial.ttf"],
    "rounded": ["/System/Library/Fonts/SFNSRounded.ttf",
                "/System/Library/Fonts/SFNS.ttf",
                "/System/Library/Fonts/HelveticaNeue.ttc"],
}

_font_cache: dict = {}


def load_font(face: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a truetype font by logical face name at a pixel size.

    Walks the candidate paths for `face`; on total failure returns Pillow's
    default bitmap font so rendering still succeeds.
    """
    key = (face, int(size))
    if key in _font_cache:
        return _font_cache[key]

    font = None
    for path in FONT_CANDIDATES.get(face, []):
        try:
            if os.path.exists(path):
                font = ImageFont.truetype(path, int(size))
                break
        except Exception:
            continue
    if font is None:
        try:
            font = ImageFont.load_default(size=int(size))
        except Exception:
            font = ImageFont.load_default()

    _font_cache[key] = font
    return font


# ----------------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------------
def vertical_gradient(width: int, height: int,
                      top: tuple, bottom: tuple) -> Image.Image:
    """Return an RGB image with a smooth top->bottom vertical gradient."""
    base = Image.new("RGB", (width, height), top)
    grad = Image.new("L", (1, height))
    for y in range(height):
        t = y / max(1, height - 1)
        grad.putpixel((0, y), int(round(t * 255)))
    grad = grad.resize((width, height))
    bottom_img = Image.new("RGB", (width, height), bottom)
    return Image.composite(bottom_img, base, grad)


def measure(draw: ImageDraw.ImageDraw, text: str,
            font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    """Return (w, h) of `text` using a real bbox (handles asc/descenders)."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    return r - l, b - t


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple, radius: int,
                  fill=SURFACE, outline=BORDER, width: int = 2) -> None:
    """Draw the standard Saturdays card: rounded rect, surface fill, hairline."""
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def pill_toggle(draw: ImageDraw.ImageDraw, x: int, y: int,
                w: int, h: int, on: bool) -> None:
    """Draw an iOS-style pill switch. On = amber track + right knob."""
    r = h // 2
    track = ACCENT if on else (48, 48, 54)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=r, fill=track)
    knob_r = int(h * 0.40)
    cy = y + h // 2
    cx = (x + w - r) if on else (x + r)
    draw.ellipse((cx - knob_r, cy - knob_r, cx + knob_r, cy + knob_r),
                 fill=(244, 241, 234))


# ----------------------------------------------------------------------------
# Shared frame: background gradient + top caption block.
# Returns the y-coordinate where caption content ends (panel should start below).
# ----------------------------------------------------------------------------
def draw_frame(img: Image.Image, draw: ImageDraw.ImageDraw,
               width: int, height: int, headline: str,
               sub: str | None) -> int:
    """Paint gradient bg and the top marketing caption. Return caption bottom y."""
    # caption headline ~ proportional; spec says ~64-72px on the 6.7" (1290w)
    head_size = int(width * 0.055)          # ~71px @1290
    sub_size  = int(width * 0.030)          # ~39px @1290
    head_font = load_font("text", head_size)
    sub_font  = load_font("text", sub_size)

    cx = width // 2
    y = int(height * 0.058)

    # Headline may wrap to 2 lines — keep it within side margins.
    margin = int(width * 0.075)
    max_w = width - 2 * margin
    lines = wrap_text(draw, headline, head_font, max_w)
    line_gap = int(head_size * 0.18)
    for line in lines:
        draw.text((cx, y), line, font=head_font, fill=INK, anchor="ma")
        _, lh = measure(draw, line, head_font)
        y += lh + line_gap

    if sub:
        y += int(height * 0.012)
        for line in wrap_text(draw, sub, sub_font, max_w):
            draw.text((cx, y), line, font=sub_font, fill=INK_DIM, anchor="ma")
            _, lh = measure(draw, line, sub_font)
            y += lh + int(sub_size * 0.25)

    return y


def wrap_text(draw: ImageDraw.ImageDraw, text: str,
              font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word-wrap so a line never exceeds max_w."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(draw, trial, font)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------------------
# Week-grid motif — subtle "life in weeks" dot grid. A small share of cells are
# lived (amber), the rest faint. Used on the hero screen.
# ----------------------------------------------------------------------------
def week_grid(draw: ImageDraw.ImageDraw, box: tuple,
              cols: int, rows: int, lived_frac: float) -> None:
    x0, y0, x1, y1 = box
    gw, gh = x1 - x0, y1 - y0
    # cell pitch
    px = gw / cols
    py = gh / rows
    dot = max(2, int(min(px, py) * 0.34))
    lived_cells = int(cols * rows * lived_frac)
    idx = 0
    for r in range(rows):
        for c in range(cols):
            cx = x0 + px * c + px / 2
            cy = y0 + py * r + py / 2
            lived = idx < lived_cells
            color = ACCENT if lived else (44, 44, 50)
            draw.ellipse((cx - dot, cy - dot, cx + dot, cy + dot), fill=color)
            idx += 1


# ----------------------------------------------------------------------------
# Per-screen content renderers. Each receives the area BELOW the caption.
# ----------------------------------------------------------------------------
def screen_hero(draw, width, height, top):
    """1. Big reveal number + faint week-grid motif."""
    margin = int(width * 0.062)
    panel = (margin, top + int(height * 0.015),
             width - margin, height - int(height * 0.05))
    rounded_panel(draw, panel, radius=int(width * 0.025))

    px0, py0, px1, py1 = panel
    pcx = (px0 + px1) // 2
    pw = px1 - px0

    ph = py1 - py0

    # Subtle week-grid in the upper third of the panel.
    grid_box = (px0 + int(pw * 0.10), py0 + int(ph * 0.10),
                px1 - int(pw * 0.10), py0 + int(ph * 0.34))
    week_grid(draw, grid_box, cols=26, rows=10, lived_frac=0.46)

    # Big hero number — centered in the lower-middle of the panel.
    big_font = load_font("rounded", int(width * 0.21))
    num_y = py0 + int(ph * 0.62)
    draw.text((pcx, num_y), "1,847", font=big_font, fill=ACCENT, anchor="mm")

    # "Saturdays left" beneath.
    sub_font = load_font("text", int(width * 0.045))
    _, nh = measure(draw, "1,847", big_font)
    draw.text((pcx, num_y + nh // 2 + int(height * 0.028)),
              "Saturdays left", font=sub_font, fill=INK_DIM, anchor="mm")


def screen_health(draw, width, height, top):
    """2. Habit toggles bending the curve + delta."""
    margin = int(width * 0.062)
    panel = (margin, top + int(height * 0.015),
             width - margin, height - int(height * 0.05))
    rounded_panel(draw, panel, radius=int(width * 0.025))
    px0, py0, px1, py1 = panel
    pw = px1 - px0
    pad = int(pw * 0.085)

    label_font = load_font("text", int(width * 0.044))
    head_font  = load_font("text", int(width * 0.038))

    # Small section heading inside panel.
    draw.text((px0 + pad, py0 + pad), "Daily habits",
              font=head_font, fill=INK_FAINT, anchor="la")

    habits = [("Exercise", True), ("Sleep 7h+", True),
              ("No smoking", True), ("Low stress", False)]
    row_top = py0 + pad + int(height * 0.045)
    row_h = int(height * 0.085)
    sw_w = int(width * 0.135)
    sw_h = int(height * 0.040)
    for name, on in habits:
        ry = row_top
        # row separator
        draw.line((px0 + pad, ry, px1 - pad, ry), fill=BORDER, width=1)
        cy = ry + row_h // 2
        draw.text((px0 + pad, cy), name, font=label_font,
                  fill=INK, anchor="lm")
        pill_toggle(draw, px1 - pad - sw_w, cy - sw_h // 2,
                    sw_w, sw_h, on)
        row_top += row_h

    # Delta callout near the bottom: habits add Saturdays.
    delta_font = load_font("rounded", int(width * 0.085))
    cap_font   = load_font("text", int(width * 0.034))
    dcx = (px0 + px1) // 2
    dy = py1 - int((py1 - py0) * 0.18)
    draw.text((dcx, dy), "+312 Saturdays", font=delta_font,
              fill=GREEN, anchor="mm")
    draw.text((dcx, dy + int(height * 0.05)),
              "your habits are bending the curve",
              font=cap_font, fill=INK_DIM, anchor="mm")


def screen_logger(draw, width, height, top):
    """3. Daily check-in + streak dots."""
    margin = int(width * 0.062)
    panel = (margin, top + int(height * 0.015),
             width - margin, height - int(height * 0.05))
    rounded_panel(draw, panel, radius=int(width * 0.025))
    px0, py0, px1, py1 = panel
    pcx = (px0 + px1) // 2
    pw = px1 - px0

    q_font = load_font("text", int(width * 0.058))
    draw.text((pcx, py0 + int((py1 - py0) * 0.18)),
              "Were you present today?",
              font=q_font, fill=INK, anchor="mm")

    # Yes / Not really choice chips.
    chip_font = load_font("text", int(width * 0.040))
    chip_w = int(pw * 0.34)
    chip_h = int(height * 0.07)
    gap = int(pw * 0.05)
    cy = py0 + int((py1 - py0) * 0.36)
    yes_x = pcx - chip_w - gap // 2
    no_x  = pcx + gap // 2
    # "Yes" — selected (amber)
    draw.rounded_rectangle((yes_x, cy, yes_x + chip_w, cy + chip_h),
                           radius=chip_h // 2, fill=ACCENT)
    draw.text((yes_x + chip_w // 2, cy + chip_h // 2), "Yes",
              font=chip_font, fill=(10, 10, 11), anchor="mm")
    # "Not really" — unselected
    draw.rounded_rectangle((no_x, cy, no_x + chip_w, cy + chip_h),
                           radius=chip_h // 2, outline=BORDER, width=2)
    draw.text((no_x + chip_w // 2, cy + chip_h // 2), "Not really",
              font=chip_font, fill=INK_DIM, anchor="mm")

    # Streak label.
    streak_font = load_font("text", int(width * 0.044))
    sy = py0 + int((py1 - py0) * 0.66)
    draw.text((pcx, sy), "12 week streak", font=streak_font,
              fill=INK, anchor="mm")

    # Row of filled streak dots.
    dot_count = 12
    dot_r = int(width * 0.013)
    spacing = int(pw * 0.78 / (dot_count - 1))
    total_w = spacing * (dot_count - 1)
    dx = pcx - total_w // 2
    dyy = sy + int(height * 0.055)
    for i in range(dot_count):
        col = ACCENT if i < 11 else (60, 60, 66)
        draw.ellipse((dx - dot_r, dyy - dot_r, dx + dot_r, dyy + dot_r),
                     fill=col)
        dx += spacing


def screen_people(draw, width, height, top):
    """4. Relationship visit-frequency cards."""
    margin = int(width * 0.062)
    panel = (margin, top + int(height * 0.015),
             width - margin, height - int(height * 0.05))
    rounded_panel(draw, panel, radius=int(width * 0.025))
    px0, py0, px1, py1 = panel
    pw = px1 - px0
    pad = int(pw * 0.075)

    head_font = load_font("text", int(width * 0.034))
    draw.text((px0 + pad, py0 + pad),
              "Saturdays you'll realistically share",
              font=head_font, fill=INK_FAINT, anchor="la")

    people = [("Mom", "48 visits left", ACCENT),
              ("Dad", "41 visits left", TEAL),
              ("Grandma", "12 visits left", RED)]

    card_top = py0 + pad + int(height * 0.05)
    card_h = int(height * 0.115)
    card_gap = int(height * 0.028)
    name_font = load_font("text", int(width * 0.050))
    sub_font  = load_font("text", int(width * 0.034))
    big_font  = load_font("rounded", int(width * 0.075))

    for name, visits, dotcol in people:
        cx0, cy0 = px0 + pad, card_top
        cx1, cy1 = px1 - pad, card_top + card_h
        draw.rounded_rectangle((cx0, cy0, cx1, cy1),
                               radius=int(width * 0.022),
                               fill=(28, 28, 32), outline=BORDER, width=1)
        # avatar dot
        av_r = int(card_h * 0.30)
        av_cx = cx0 + int(pw * 0.10)
        av_cy = (cy0 + cy1) // 2
        draw.ellipse((av_cx - av_r, av_cy - av_r, av_cx + av_r, av_cy + av_r),
                     fill=dotcol)
        # initial
        init_font = load_font("text", int(av_r * 1.1))
        draw.text((av_cx, av_cy), name[0], font=init_font,
                  fill=(10, 10, 11), anchor="mm")
        # name + visits
        text_x = av_cx + av_r + int(pw * 0.05)
        draw.text((text_x, av_cy - int(card_h * 0.16)), name,
                  font=name_font, fill=INK, anchor="lm")
        draw.text((text_x, av_cy + int(card_h * 0.18)), visits,
                  font=sub_font, fill=INK_DIM, anchor="lm")
        # big number on the right
        num = visits.split()[0]
        draw.text((cx1 - int(pw * 0.06), av_cy), num,
                  font=big_font, fill=dotcol, anchor="rm")

        card_top += card_h + card_gap


def screen_share(draw, width, height, top):
    """5. Polished centered share card."""
    margin = int(width * 0.062)
    panel = (margin, top + int(height * 0.015),
             width - margin, height - int(height * 0.05))
    rounded_panel(draw, panel, radius=int(width * 0.025))
    px0, py0, px1, py1 = panel
    pcx = (px0 + px1) // 2
    pw = px1 - px0

    # Inner share card — a tighter, brighter framed card to feel "shareable".
    inset = int(pw * 0.10)
    card = (px0 + inset, py0 + int((py1 - py0) * 0.12),
            px1 - inset, py1 - int((py1 - py0) * 0.12))
    draw.rounded_rectangle(card, radius=int(width * 0.03),
                           fill=(16, 16, 18), outline=ACCENT, width=2)
    ccx = (card[0] + card[2]) // 2
    cy_top, cy_bot = card[1], card[3]

    # faint mini week grid at the top of the share card
    gb = (card[0] + int(pw * 0.10), cy_top + int(pw * 0.10),
          card[2] - int(pw * 0.10), cy_top + int(pw * 0.24))
    week_grid(draw, gb, cols=22, rows=4, lived_frac=0.46)

    big_font = load_font("rounded", int(width * 0.20))
    draw.text((ccx, (cy_top + cy_bot) // 2 - int(height * 0.02)),
              "1,847", font=big_font, fill=ACCENT, anchor="mm")

    word_font = load_font("text", int(width * 0.052))
    _, nh = measure(draw, "1,847", big_font)
    word_y = (cy_top + cy_bot) // 2 - int(height * 0.02) + nh // 2 + int(height * 0.025)
    draw.text((ccx, word_y), "Saturdays", font=word_font,
              fill=INK, anchor="mm")

    tag_font = load_font("text", int(width * 0.034))
    draw.text((ccx, cy_bot - int((cy_bot - cy_top) * 0.10)),
              "Spend this one like it counts.",
              font=tag_font, fill=INK_DIM, anchor="mm")


# ----------------------------------------------------------------------------
# Screen specs
# ----------------------------------------------------------------------------
SCREENS = [
    {
        "name": "01-reveal",
        "headline": "1,847 Saturdays left",
        "sub": "A life is about 4,000 Saturdays. See yours.",
        "render": screen_hero,
    },
    {
        "name": "02-habits",
        "headline": "Your daily choices compound",
        "sub": "Small habits, decades of difference.",
        "render": screen_health,
    },
    {
        "name": "03-checkin",
        "headline": "One question, every Saturday",
        "sub": "A 5-second check-in keeps you honest.",
        "render": screen_logger,
    },
    {
        "name": "04-people",
        "headline": "Hold your people close",
        "sub": "See how many visits you really have left.",
        "render": screen_people,
    },
    {
        "name": "05-share",
        "headline": "Make it impossible to ignore",
        "sub": "Share your number. Live like it's true.",
        "render": screen_share,
    },
]

# Apple-required resolutions: (folder, width, height)
SIZES = [
    ("6.7-inch", 1290, 2796),
    ("6.1-inch", 1179, 2556),
]


def render_screenshot(spec: dict, width: int, height: int) -> Image.Image:
    """Render one screenshot spec at the given resolution."""
    img = vertical_gradient(width, height, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    caption_bottom = draw_frame(img, draw, width, height,
                                spec["headline"], spec.get("sub"))
    spec["render"](draw, width, height, caption_bottom)
    return img


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_root = os.path.join(root, "screenshots")
    results = []
    for folder, w, h in SIZES:
        out_dir = os.path.join(out_root, folder)
        os.makedirs(out_dir, exist_ok=True)
        for spec in SCREENS:
            img = render_screenshot(spec, w, h)
            path = os.path.join(out_dir, f"{spec['name']}.png")
            img.save(path, "PNG")
            results.append((path, img.size))
            print(f"  wrote {path}  {img.size[0]}x{img.size[1]}")
    print(f"\nDone. {len(results)} screenshots written to {out_root}")


if __name__ == "__main__":
    main()
