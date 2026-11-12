#!/usr/bin/env python3
"""Generate entry.png: a colossal aurora whale swimming over a tiny night city.
Pure PIL + numpy, procedural, no external assets. Renders at 2x then downscales.
Concept: the night sky itself is an ocean; a whale made of aurora light and
stars drifts above a sleeping city, moon behind its tail.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)
np.random.seed(42)
W = H = 1024
S = 2  # supersample
SW, SH = W * S, H * S


def catmull(points, samples=24, closed=False):
    pts = list(points)
    if closed:
        ext = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        ext = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(len(ext) - 3):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for j in range(samples):
            t = j / samples
            t2, t3 = t * t, t * t * t
            out.append((
                0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3),
            ))
    out.append(pts[-1] if not closed else pts[0])
    return out


# ---------- sky ----------
def make_sky():
    y = np.linspace(0, 1, SH)[:, None]
    x = np.linspace(0, 1, SW)[None, :]
    top = np.array([7, 9, 34], float)
    mid = np.array([13, 32, 76], float)
    low = np.array([12, 84, 98], float)
    img = np.zeros((SH, SW, 3), float)
    for c in range(3):
        col = np.where(y < 0.62, top[c] + (mid[c] - top[c]) * (y / 0.62),
                       mid[c] + (low[c] - mid[c]) * ((y - 0.62) / 0.38))
        img[:, :, c] = col
    cx, cy = 0.40, 1.04
    d = np.sqrt((x - cx) ** 2 * 1.6 + (y - cy) ** 2)
    warm = np.exp(-(d ** 2) / 0.07) * 0.5
    img[:, :, 0] += warm * 118
    img[:, :, 1] += warm * 60
    img[:, :, 2] += warm * 8
    small = np.random.rand(32, 32).astype(float)
    neb = np.array(Image.fromarray((small * 255).astype(np.uint8)).resize((SW, SH), Image.BICUBIC), float) / 255.0
    neb2 = np.array(Image.fromarray((np.random.rand(16, 16) * 255).astype(np.uint8)).resize((SW, SH), Image.BICUBIC), float) / 255.0
    m = (neb * 0.6 + neb2 * 0.4 - 0.5)
    img[:, :, 0] += m * 13
    img[:, :, 1] += m * 20
    img[:, :, 2] += m * 32
    return np.clip(img, 0, 255).astype(np.uint8)


img = Image.fromarray(make_sky()).convert("RGBA")

# ---------- moon (upper right, behind whale tail) ----------
moon = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
md = ImageDraw.Draw(moon)
mx, my, mr = 806 * S, 172 * S, 134 * S
for r, a in [(mr * 2.1, 16), (mr * 1.55, 30), (mr * 1.22, 52)]:
    md.ellipse([mx - r, my - r, mx + r, my + r], fill=(190, 225, 255, int(a)))
img = Image.alpha_composite(img, moon.filter(ImageFilter.GaussianBlur(18 * S)))
moon2 = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
md2 = ImageDraw.Draw(moon2)
md2.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(222, 234, 248, 255))
moon2 = moon2.filter(ImageFilter.GaussianBlur(1.2 * S))
img = Image.alpha_composite(img, moon2)  # clean graphic moon, no craters (they read as blobs)

# ---------- stars ----------
star_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
sd = ImageDraw.Draw(star_layer)
for _ in range(560):
    sx, sy = random.uniform(0, SW), random.uniform(0, SH * 0.85)
    r = random.choice([1, 1, 1, 2, 2, 3]) * S // 2
    a = random.randint(55, 230)
    col = (210, 235, 255, a) if random.random() < 0.7 else (255, 225, 190, a)
    sd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    if r >= 2 and random.random() < 0.28:
        L = r * 4
        sd.line([sx - L, sy, sx + L, sy], fill=(200, 230, 255, a // 3), width=S)
        sd.line([sx, sy - L, sx, sy + L], fill=(200, 230, 255, a // 3), width=S)
img = Image.alpha_composite(img, star_layer)

# ---------- aurora ribbons in the sky ----------
aurora = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
ad = ImageDraw.Draw(aurora)
for band, (base_y, amp, col, alpha, thick) in enumerate([
    (120, 55, (46, 230, 190), 40, 80),
    (205, 75, (60, 160, 255), 30, 110),
    (70, 40, (150, 90, 255), 22, 60),
]):
    pts_top, pts_bot = [], []
    for xi in range(0, SW + 16, 16):
        t = xi / SW
        yy = (base_y + amp * math.sin(t * 4.2 + band * 1.7) + 38 * math.sin(t * 9.0 + band)) * S
        pts_top.append((xi, yy))
        pts_bot.append((xi, yy + thick * S))
    ad.polygon(pts_top + pts_bot[::-1], fill=col + (alpha,))
img = Image.alpha_composite(img, aurora.filter(ImageFilter.GaussianBlur(26 * S)))

# ---------- whale silhouette ----------
# Diagonal composition: head low-left, tail high-right (swimming up through the sky).
body_ctrl = [
    (92, 520), (130, 452), (225, 408), (360, 380), (510, 366),
    (650, 366), (752, 378), (818, 392),
    (880, 344), (930, 272), (946, 306), (916, 380),
    (892, 410),
    (914, 478), (934, 540), (896, 528), (852, 452),
    (818, 434),
    (712, 478), (566, 516), (412, 534), (272, 546), (168, 548), (106, 538),
]
body = [(x * S, y * S) for x, y in catmull(body_ctrl, samples=20, closed=True)]
whale_mask = Image.new("L", (SW, SH), 0)
wd = ImageDraw.Draw(whale_mask)
wd.polygon(body, fill=255)
fin_ctrl = [(322, 516), (350, 524), (364, 602), (348, 664), (324, 606), (308, 538)]
fin = [(x * S, y * S) for x, y in catmull(fin_ctrl, samples=16, closed=True)]
wd.polygon(fin, fill=255)
whale_mask = whale_mask.filter(ImageFilter.GaussianBlur(1.2 * S))

# whale interior: flowing aurora curtains (diagonal, irregular) + bright core
wx = np.linspace(0, 1, SW)[None, :]
wy = np.linspace(0, 1, SH)[:, None]
interior = np.zeros((SH, SW, 3), float)
c_deep = np.array([9, 20, 58], float)
c_teal = np.array([18, 168, 178], float)
grad = np.clip((wx * 0.72 + (1 - wy) * 0.38), 0, 1)
for c in range(3):
    interior[:, :, c] = c_deep[c] + (c_teal[c] - c_deep[c]) * grad
u = wx * 9.5 - wy * 3.4
flow = np.clip(np.sin(u * math.pi + 1.1 * np.sin(wx * 9.0) + 0.7 * np.sin(wy * 14.0)), 0, 1) ** 2.5
interior[:, :, 0] += flow * 84
interior[:, :, 1] += flow * 158
interior[:, :, 2] += flow * 160
v = wx * 4.2 + wy * 1.8
flow2 = np.clip(np.sin(v * math.pi + 2.0 + 0.9 * np.sin(wx * 7.0)), 0, 1) ** 4
interior[:, :, 0] += flow2 * 92
interior[:, :, 1] += flow2 * 34
interior[:, :, 2] += flow2 * 142
# dark nebula patches inside the body, for depth against the bright curtains
patch = np.clip(np.sin((wx * 3.1 + wy * 4.6) * math.pi + 4.2 + 1.3 * np.sin(wx * 5.0)), 0, 1) ** 3
interior[:, :, 0] -= patch * 6
interior[:, :, 1] -= patch * 52
interior[:, :, 2] -= patch * 44
# bright core glow along the body's spine
spine = np.exp(-(((wy - (0.44 - 0.055 * wx)) / 0.055) ** 2))
interior[:, :, 0] += spine * 26
interior[:, :, 1] += spine * 66
interior[:, :, 2] += spine * 62
interior_img = Image.fromarray(np.clip(interior, 0, 255).astype(np.uint8)).convert("RGBA")
inner_stars = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
isd = ImageDraw.Draw(inner_stars)
for _ in range(430):
    sx, sy = random.uniform(80 * S, 960 * S), random.uniform(250 * S, 580 * S)
    r = random.choice([1, 2, 2, 3])
    isd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(235, 250, 255, random.randint(90, 230)))
inner_stars.putalpha(Image.composite(inner_stars.split()[3], Image.new("L", (SW, SH), 0), whale_mask))
interior_img = Image.alpha_composite(interior_img, inner_stars)
img.paste(interior_img, (0, 0), whale_mask)

# soft outer glow of the whale
glow_np = np.zeros((SH, SW, 4), np.uint8)
glow_alpha = np.clip(np.array(whale_mask.filter(ImageFilter.GaussianBlur(16 * S)), float) * 0.42, 0, 108)
glow_np[:, :, 0] = 60; glow_np[:, :, 1] = 205; glow_np[:, :, 2] = 215
glow_np[:, :, 3] = glow_alpha.astype(np.uint8)
img = Image.alpha_composite(Image.fromarray(glow_np, "RGBA"), img) if False else img
img = Image.alpha_composite(img, Image.fromarray(glow_np, "RGBA"))

# rim light: cyan-white on the top edge, warm bounce underneath
rim_np = np.zeros((SH, SW, 4), np.uint8)
mask_f = np.array(whale_mask, float)
# PIL AFFINE samples input at y+f: f negative moves content down, so mask minus that = TOP strip
content_down = np.array(whale_mask.transform((SW, SH), Image.AFFINE, (1, 0, 0, 0, 1, -9 * S)), float)
upper = np.clip(mask_f - content_down, 0, 255)
edge = np.clip(np.array(whale_mask.filter(ImageFilter.GaussianBlur(5 * S)), float) - mask_f, 0, 255)
rim_np[:, :, 0] = 168; rim_np[:, :, 1] = 246; rim_np[:, :, 2] = 255
rim_np[:, :, 3] = np.clip(upper * 1.0 + edge * 0.55, 0, 255).astype(np.uint8)
img = Image.alpha_composite(img, Image.fromarray(rim_np, "RGBA").filter(ImageFilter.GaussianBlur(1.6 * S)))
belly_np = np.zeros((SH, SW, 4), np.uint8)
# f positive moves content up, so mask minus that = BOTTOM strip
content_up = np.array(whale_mask.transform((SW, SH), Image.AFFINE, (1, 0, 0, 0, 1, 13 * S)), float)
lower = np.clip(mask_f - content_up, 0, 255)
belly_np[:, :, 0] = 255; belly_np[:, :, 1] = 172; belly_np[:, :, 2] = 88
belly_np[:, :, 3] = (lower * 0.32).astype(np.uint8)
img = Image.alpha_composite(img, Image.fromarray(belly_np, "RGBA").filter(ImageFilter.GaussianBlur(3 * S)))

# eye: one warm glowing eye
eye_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
ed = ImageDraw.Draw(eye_layer)
ex, ey = 196 * S, 492 * S
for r, a in [(17, 42), (10, 95), (4, 255)]:
    ed.ellipse([ex - r * S // 2, ey - r * S // 2, ex + r * S // 2, ey + r * S // 2], fill=(255, 198, 112, a))
img = Image.alpha_composite(img, eye_layer)

# stardust: trail from tail, sparkles from blowhole
trail = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
td = ImageDraw.Draw(trail)
for i in range(240):
    t = random.random()
    px = (896 + t * 128 + random.gauss(0, 15)) * S
    py = (452 - t * 150 + 24 * math.sin(t * 7) + random.gauss(0, 20 * (0.4 + t))) * S
    r = max(1.0, random.choice([1, 2, 2, 3, 4]) * (1 - t * 0.5))
    td.ellipse([px - r, py - r, px + r, py + r], fill=(150, 235, 255, int(200 * (1 - t) + 30)))
for i in range(80):
    t = random.random()
    px = (208 + random.gauss(0, 13) + t * 30) * S
    py = (412 - t * 104 + random.gauss(0, 10)) * S
    r = random.choice([1, 2, 3])
    td.ellipse([px - r, py - r, px + r, py + r], fill=(190, 245, 255, int(210 * (1 - t) + 40)))
img = Image.alpha_composite(img, trail.filter(ImageFilter.GaussianBlur(1.0 * S)))

# ---------- sea of clouds above the city ----------
clouds = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
cld = ImageDraw.Draw(clouds)
rngc = random.Random(11)
for i in range(40):
    cxp = rngc.uniform(-40, 1060) * S
    cyp = rngc.uniform(772, 918) * S
    rx = rngc.uniform(56, 168) * S
    ry = rx * rngc.uniform(0.30, 0.45)
    shade = rngc.uniform(0.7, 1.05)
    col = (int(26 * shade + 8), int(72 * shade + 12), int(96 * shade + 16), 238)
    cld.ellipse([cxp - rx, cyp - ry, cxp + rx, cyp + ry], fill=col)
clouds = clouds.filter(ImageFilter.GaussianBlur(7 * S))
# cloud top highlights (moon/teal lit)
hl = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
hd = ImageDraw.Draw(hl)
for i in range(34):
    cxp = rngc.uniform(-40, 1060) * S
    cyp = rngc.uniform(772, 852) * S
    rx = rngc.uniform(50, 130) * S
    ry = rx * 0.30
    hd.ellipse([cxp - rx, cyp - ry, cxp + rx, cyp + ry], fill=(120, 205, 210, 52))
img = Image.alpha_composite(img, clouds)
img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(12 * S)))

# ---------- tiny night city ----------
city = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
cd = ImageDraw.Draw(city)
base_y = SH
rng = random.Random(7)
x = -10
while x < SW + 20:
    bw = rng.randint(28, 64) * S // 2
    bh = rng.randint(90, 210) * S // 2
    cd.rectangle([x, base_y - bh, x + bw, base_y], fill=(9, 14, 30, 255))
    x += bw + rng.randint(2, 10) * S // 2
buildings = []
x = -10
while x < SW + 20:
    bw = rng.randint(36, 86) * S // 2
    bh = rng.randint(64, 178) * S // 2
    cd.rectangle([x, base_y - bh, x + bw, base_y], fill=(4, 6, 14, 255))
    if rng.random() < 0.38:
        ax = x + bw // 2
        cd.line([ax, base_y - bh, ax, base_y - bh - 17 * S], fill=(4, 6, 14, 255), width=2 * S)
        cd.ellipse([ax - 3 * S, base_y - bh - 20 * S, ax + 3 * S, base_y - bh - 14 * S], fill=(255, 92, 82, 205))
    buildings.append((x, bw, bh))
    x += bw + rng.randint(2, 8) * S // 2
for (bx, bw, bh) in buildings:
    cols = max(1, bw // (11 * S))
    rows = max(1, bh // (13 * S))
    for ci in range(cols):
        for ri in range(rows):
            if rng.random() < 0.44:
                wxp = bx + 5 * S + ci * 11 * S
                wyp = base_y - bh + 6 * S + ri * 13 * S
                col = (255, 186, 96, rng.randint(150, 255)) if rng.random() < 0.82 else (170, 225, 255, rng.randint(120, 220))
                cd.rectangle([wxp, wyp, wxp + 4 * S, wyp + 6 * S], fill=col)
img = Image.alpha_composite(img, city)

img = img.convert("RGB").resize((W, H), Image.LANCZOS)

# ---------- painterly finish: grain + vignette ----------
arr = np.array(img).astype(float)
arr += np.random.normal(0, 4.2, arr.shape[:2])[..., None]
yy, xx = np.mgrid[0:H, 0:W]
dist = np.sqrt(((xx - W / 2) / (W * 0.74)) ** 2 + ((yy - H / 2) / (H * 0.74)) ** 2)
vig = np.clip(1 - 0.36 * np.clip(dist - 0.55, 0, 1) ** 2, 0.64, 1)
arr *= vig[..., None]
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=66, threshold=2))
img.save("entry.png", optimize=True)
import os
if os.path.getsize("entry.png") > 1048576:  # gate: <= 1 MiB; palette-quantize with dithering
    q = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
    q.save("entry.png", optimize=True)
print("saved entry.png", img.size, os.path.getsize("entry.png"), "bytes")
