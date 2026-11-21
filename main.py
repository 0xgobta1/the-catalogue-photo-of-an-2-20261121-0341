# LUMEN — the kettle that pours daylight.
# A catalogue photograph of an impossible gadget, rendered procedurally.
# makefun anchor: the-catalogue-photo-of-an-2-20261121-0341 — LUMEN daylight
# kettle, fresh from-scratch build for @sunny-sparrow-40.
#
# The gadget: a brushed-steel electric kettle that does not pour water.
# It pours daylight — a solid beam of warm morning light — straight into
# a mug, where it is brewed like tea. One accessory only: the tea-bag tag
# hanging from the mug. Clean studio backdrop, soft floor shadow, the
# product as hero. No network, fully deterministic, stdlib + Pillow only.

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

print("makefun anchor: the-catalogue-photo-of-an-2-20261121-0341 — LUMEN")

S = 2                      # supersample factor; final image is 1024x1024
W = H = 1024 * S
OUT = "/output/entry.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


def vgrad(w, h, stops):
    """Vertical gradient image. stops: list of (pos 0..1, (r,g,b))."""
    import numpy as np

    y = np.linspace(0.0, 1.0, h)
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for c in range(3):
        xs = [p for p, _ in stops]
        ys = [col[c] for _, col in stops]
        img[:, :, c] = np.interp(y, xs, ys)[:, None]
    return Image.fromarray(img, "RGB")


def hgrad(w, h, stops):
    import numpy as np

    x = np.linspace(0.0, 1.0, w)
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for c in range(3):
        xs = [p for p, _ in stops]
        ys = [col[c] for _, col in stops]
        img[:, :, c] = np.interp(x, xs, ys)[None, :]
    return Image.fromarray(img, "RGB")


def soft(mask_img, radius):
    return mask_img.filter(ImageFilter.GaussianBlur(radius * S))


def paste(base, layer, xy):
    base.paste(layer, xy, layer)


# ---------------------------------------------------------------- backdrop
def backdrop():
    bg = vgrad(W, H, [
        (0.00, (246, 242, 233)),
        (0.55, (238, 232, 219)),
        (0.78, (226, 218, 203)),
        (1.00, (205, 195, 179)),
    ]).convert("RGBA")
    # warm radial glow behind the product
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy, r = int(0.52 * W), int(0.42 * H), int(0.46 * W)
    for i in range(24, 0, -1):
        a = int(7 + 3 * (24 - i))
        gd.ellipse([cx - r * i / 24, cy - r * i / 24 * 0.82,
                    cx + r * i / 24, cy + r * i / 24 * 0.82],
                   fill=(255, 214, 140, a))
    bg.alpha_composite(soft(glow, 18))
    # faint horizon where wall meets floor
    d = ImageDraw.Draw(bg)
    d.line([(0, int(0.80 * H)), (W, int(0.80 * H))], fill=(120, 108, 92, 26),
           width=int(2 * S))
    return bg


# ---------------------------------------------------------------- kettle
def kettle_layer():
    """Draw the kettle upright on its own layer; caller rotates it."""
    lw, lh = 640 * S, 700 * S
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # --- body profile: a softly bowed trapezoid -------------------------
    bx0, bx1 = 150 * S, 490 * S          # body x range
    top_y, bot_y = 130 * S, 560 * S
    pts = []
    n = 26
    for i in range(n + 1):               # left side, top -> bottom
        t = i / n
        y = top_y + (bot_y - top_y) * t
        x = bx0 + 26 * S * math.sin(t * math.pi) * 0.55 - 14 * S * t
        pts.append((x, y))
    for i in range(n + 1):               # bottom edge
        t = i / n
        pts.append((bx0 - 14 * S + (bx1 - bx0 + 28 * S) * t, bot_y))
    for i in range(n + 1):               # right side, bottom -> top
        t = i / n
        y = bot_y - (bot_y - top_y) * t
        x = bx1 - 26 * S * math.sin(t * math.pi) * 0.55 + 14 * S * t
        pts.append((x, y))
    for i in range(n + 1):               # top edge
        t = i / n
        pts.append((bx1 - (bx1 - bx0) * t, top_y))

    mask = Image.new("L", (lw, lh), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    mask = soft(mask, 1.2)

    steel = vgrad(lw, lh, [
        (0.00, (228, 231, 233)),
        (0.30, (196, 201, 205)),
        (0.55, (168, 173, 178)),
        (0.80, (139, 145, 150)),
        (1.00, (112, 118, 123)),
    ]).convert("RGBA")
    # brushed horizontal streaks
    streak = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streak)
    for i, yy in enumerate(range(140 * S, 560 * S, 7 * S)):
        a = 5 if i % 3 else 9
        sd.line([(bx0, yy), (bx1, yy)], fill=(255, 255, 255, a), width=S)
    steel.alpha_composite(streak)
    body = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    body.paste(steel, (0, 0), mask)
    layer.alpha_composite(body)

    # bright studio highlight band, left third of the body
    hl = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.rectangle([205 * S, top_y, 275 * S, bot_y], fill=(255, 255, 255, 120))
    hl = soft(hl, 9)
    hl.putalpha(hl.split()[3].point(lambda v: int(v * 0.55)))
    layer.alpha_composite(Image.composite(hl, Image.new("RGBA", (lw, lh), (0, 0, 0, 0)), mask))

    # dark edge on the right, for roundness
    edge = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    ed.rectangle([440 * S, top_y, 495 * S, bot_y], fill=(40, 44, 48, 90))
    edge = soft(edge, 8)
    layer.alpha_composite(Image.composite(edge, Image.new("RGBA", (lw, lh), (0, 0, 0, 0)), mask))

    # bottom trim ring
    d.rounded_rectangle([bx0 - 6 * S, bot_y - 14 * S, bx1 + 6 * S, bot_y + 10 * S],
                        radius=10 * S, fill=(58, 62, 66, 255))
    d.rounded_rectangle([bx0 - 6 * S, bot_y - 14 * S, bx1 + 6 * S, bot_y - 4 * S],
                        radius=10 * S, fill=(120, 126, 131, 255))

    # --- sight glass: glowing daylight level ----------------------------
    gx0, gx1 = 168 * S, 196 * S
    gy0, gy1 = 300 * S, 500 * S
    d.rounded_rectangle([gx0, gy0, gx1, gy1], radius=12 * S,
                        fill=(30, 32, 34, 255))
    gl = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(gl)
    gd2.rounded_rectangle([gx0 + 4 * S, gy0 + 60 * S, gx1 - 4 * S, gy1 - 4 * S],
                          radius=8 * S, fill=(255, 196, 80, 255))
    layer.alpha_composite(soft(gl, 2))

    # --- lid + knob ------------------------------------------------------
    d.ellipse([bx0 + 30 * S, top_y - 34 * S, bx1 - 30 * S, top_y + 26 * S],
              fill=(52, 56, 60, 255))
    d.ellipse([bx0 + 44 * S, top_y - 30 * S, bx1 - 44 * S, top_y + 6 * S],
              fill=(96, 101, 106, 255))
    d.ellipse([300 * S, top_y - 62 * S, 340 * S, top_y - 22 * S],
              fill=(38, 40, 43, 255))
    d.ellipse([308 * S, top_y - 58 * S, 326 * S, top_y - 40 * S],
              fill=(150, 155, 160, 255))

    # --- handle (right side, matte charcoal arc, ends ON the body) --------
    d.arc([420 * S, 180 * S, 600 * S, 500 * S], start=250, end=110,
          fill=(43, 46, 49, 255), width=int(30 * S))
    d.arc([420 * S, 180 * S, 600 * S, 500 * S], start=250, end=110,
          fill=(70, 74, 78, 255), width=int(8 * S))

    # --- spout: gooseneck sweeping left, then straight down --------------
    sp = [(bx0 + 6 * S, 230 * S), (96 * S, 280 * S), (62 * S, 360 * S),
          (54 * S, 460 * S), (58 * S, 540 * S),
          (116 * S, 540 * S), (112 * S, 450 * S), (122 * S, 350 * S),
          (158 * S, 300 * S), (bx0 + 40 * S, 262 * S)]
    smask = Image.new("L", (lw, lh), 0)
    ImageDraw.Draw(smask).polygon(sp, fill=255)
    smask = soft(smask, 1.2)
    spout = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    spout.paste(steel, (0, 0), smask)
    layer.alpha_composite(spout)
    # spout opening: dark mouth + bright rim, facing straight down
    d.ellipse([58 * S, 538 * S, 116 * S, 570 * S], fill=(28, 30, 32, 255))
    d.ellipse([65 * S, 544 * S, 109 * S, 565 * S], fill=(255, 214, 130, 255))
    d.ellipse([71 * S, 548 * S, 103 * S, 561 * S], fill=(255, 244, 200, 255))

    # --- label ------------------------------------------------------------
    fb = font(FONT_BOLD, 52)
    d.text((320 * S, 330 * S), "LUMEN", font=fb, fill=(38, 40, 43, 255),
           anchor="mm")
    fr = font(FONT_REG, 20)
    d.text((320 * S, 372 * S), "POURS DAYLIGHT", font=fr,
           fill=(52, 55, 58, 255), anchor="mm")
    fs = font(FONT_REG, 16)
    d.text((345 * S, 402 * S), "2400 W  ·  SUNRISE MODEL", font=fs,
           fill=(74, 78, 82, 255), anchor="mm")
    # glowing power dot
    d.ellipse([452 * S, 452 * S, 466 * S, 466 * S], fill=(255, 176, 32, 255))
    return layer


# ---------------------------------------------------------------- stream
# Geometry (1024 canvas). Kettle layer is pasted upright at PASTE; its
# gooseneck tip sits at local (87, 552), so the stream starts there and
# pours straight down into the mug mouth directly below it.
PASTE_X, PASTE_Y = 310, 125
TIP_X, TIP_Y = PASTE_X + 87, PASTE_Y + 552          # (397, 677)
MUG_X, MUG_Y = 397, 758                              # mug mouth centre


def light_stream(img):
    """The beam of daylight from the spout tip into the mug."""
    # spout tip and mug mouth
    x0, y0 = TIP_X * S, TIP_Y * S
    x1, y1 = MUG_X * S, MUG_Y * S
    top_w, bot_w = 30 * S, 72 * S

    def beam_edges(t):
        # gentle S-curve: x drifts right then back
        cx = x0 + (x1 - x0) * t + 14 * S * math.sin(t * math.pi)
        w = top_w + (bot_w - top_w) * t
        return cx, w

    n = 40
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        cx, w = beam_edges(t)
        y = y0 + (y1 - y0) * t
        left.append((cx - w / 2, y))
        right.append((cx + w / 2, y))

    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).polygon(left + right[::-1], fill=(255, 196, 90, 110))
    img.alpha_composite(soft(halo, 16))

    mid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(mid).polygon(left + right[::-1], fill=(255, 214, 110, 200))
    img.alpha_composite(soft(mid, 5))

    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    cl, cr = [], []
    for i in range(n + 1):
        t = i / n
        cx, w = beam_edges(t)
        y = y0 + (y1 - y0) * t
        cl.append((cx - w / 5, y))
        cr.append((cx + w / 5, y))
    cd.polygon(cl + cr[::-1], fill=(255, 248, 220, 235))
    img.alpha_composite(soft(core, 2))

    # sparkles along the beam
    d = ImageDraw.Draw(img)
    for (sx, sy, r) in [(378, 700, 9), (420, 726, 7), (388, 742, 11),
                        (412, 692, 6)]:
        sx, sy, r = sx * S, sy * S, r * S
        d.polygon([(sx, sy - r), (sx + r * 0.28, sy - r * 0.28),
                   (sx + r, sy), (sx + r * 0.28, sy + r * 0.28),
                   (sx, sy + r), (sx - r * 0.28, sy + r * 0.28),
                   (sx - r, sy), (sx - r * 0.28, sy - r * 0.28)],
                  fill=(255, 244, 200, 255))


# ---------------------------------------------------------------- mug
def mug(img):
    mx, my = MUG_X * S, MUG_Y * S      # mug mouth centre
    mw, mh = 250 * S, 190 * S
    # warm light pool on the floor under the mug
    pool = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(pool).ellipse(
        [mx - 190 * S, my + 128 * S, mx + 190 * S, my + 196 * S],
        fill=(255, 200, 110, 90))
    img.alpha_composite(soft(pool, 14))

    # mug body: soft white cylinder with warm reflected light on the left
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([mx - mw / 2, my, mx + mw / 2, my + mh],
                         radius=26 * S, fill=(250, 248, 244, 255))
    warm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(warm)
    wd.rectangle([mx - mw / 2, my, mx - mw / 2 + 52 * S, my + mh],
                 fill=(255, 214, 140, 110))
    warm = soft(warm, 10)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [mx - mw / 2, my, mx + mw / 2, my + mh], radius=26 * S, fill=255)
    body.alpha_composite(Image.composite(warm, Image.new("RGBA", (W, H), (0, 0, 0, 0)), m))
    # soft grey shading on the right edge
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [mx + mw / 2 - 44 * S, my, mx + mw / 2, my + mh],
        fill=(120, 116, 108, 70))
    body.alpha_composite(Image.composite(soft(sh, 8), Image.new("RGBA", (W, H), (0, 0, 0, 0)), m))
    img.alpha_composite(body)

    # handle (right side, ends ON the mug body)
    d = ImageDraw.Draw(img)
    d.arc([mx + 65 * S, my + 30 * S, mx + 165 * S, my + 140 * S],
          start=270, end=90, fill=(244, 241, 236, 255), width=int(20 * S))
    d.arc([mx + 65 * S, my + 30 * S, mx + 165 * S, my + 140 * S],
          start=270, end=90, fill=(178, 172, 162, 255), width=int(3 * S))

    # glowing interior: the daylight pooling in the mug
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([mx - mw / 2 + 8 * S, my - 26 * S, mx + mw / 2 - 8 * S,
                my + 30 * S], fill=(255, 226, 130, 255))
    img.alpha_composite(soft(glow, 6))
    d.ellipse([mx - mw / 2 + 22 * S, my - 14 * S, mx + mw / 2 - 22 * S,
               my + 18 * S], fill=(255, 246, 205, 255))
    # rim
    d.ellipse([mx - mw / 2, my - 22 * S, mx + mw / 2, my + 22 * S],
              outline=(214, 208, 198, 255), width=int(4 * S))
    # rising light rays (steam made of light)
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for rx, top in [(348, 700), (397, 682), (446, 702)]:
        rd.line([(rx * S, my - 20 * S), (rx * S, top * S)],
                fill=(255, 220, 130, 150), width=int(5 * S))
    img.alpha_composite(soft(rays, 3))

    # --- the ONE accessory: tea-bag tag on a string from the LEFT rim ----
    d.line([(mx - 88 * S, my + 2 * S), (mx - 118 * S, my + 66 * S)],
           fill=(90, 82, 70, 255), width=int(2 * S))
    tag = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rounded_rectangle([mx - 150 * S, my + 62 * S, mx - 96 * S, my + 102 * S],
                         radius=5 * S, fill=(250, 240, 214, 255),
                         outline=(176, 160, 130, 255), width=int(2 * S))
    img.alpha_composite(tag)
    tf = font(FONT_BOLD, 13)
    d.text((mx - 123 * S, my + 82 * S), "LUMEN", font=tf,
           fill=(120, 96, 52, 255), anchor="mm")
    return img


# ---------------------------------------------------------------- shadows
def floor_shadows(img):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    # long soft shadow under the floating kettle
    sd.ellipse([440 * S, 946 * S, 880 * S, 990 * S], fill=(60, 52, 42, 110))
    # contact shadow under the mug
    sd.ellipse([290 * S, 954 * S, 510 * S, 990 * S], fill=(52, 46, 38, 130))
    img.alpha_composite(soft(sh, 10))


def main():
    img = backdrop()
    # kettle, upright — gooseneck spout pours straight down into the mug
    kl = kettle_layer()
    paste(img, kl, (PASTE_X * S, PASTE_Y * S))
    floor_shadows(img)
    light_stream(img)
    mug(img)
    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    os.makedirs("/output", exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} 1024x1024 PNG {size} bytes")
    assert size <= 1_048_576, "over the 1 MiB gate"


if __name__ == "__main__":
    main()
