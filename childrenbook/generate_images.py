#!/usr/bin/env python3
"""Generate colorful illustrated scenes for the Goldie & Draghino children's book."""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)

random.seed(42)

# ── colour palette ──────────────────────────────────────────────
SKY_BLUE = (135, 190, 235)
SKY_LIGHT = (185, 220, 245)
SKY_SUNSET = (245, 165, 100)
SKY_NIGHT = (20, 25, 60)
GRASS = (100, 180, 90)
GRASS_DARK = (70, 140, 65)
WATER = (80, 155, 210)
WATER_DARK = (40, 80, 130)
STONE = (160, 155, 145)
STONE_DK = (110, 105, 100)
STONE_LT = (195, 190, 180)
WOOD = (150, 110, 65)
WOOD_DK = (110, 80, 45)
WHITE = (255, 255, 255)
CLOUD = (245, 245, 250)
SNOW = (235, 240, 250)
YELLOW = (255, 220, 80)
RED = (210, 70, 60)
ORANGE = (240, 160, 60)
PINK = (240, 180, 190)
PURPLE = (170, 120, 200)
GREEN = (80, 190, 100)
TEAL = (70, 200, 190)

# Dragon colours
GOLDIE_BODY = (90, 150, 220)
GOLDIE_BELLY = (240, 200, 80)
GOLDIE_EYE = (220, 170, 50)
GOLDIE_WING = (50, 50, 55)

DRAGHINO_BODY = (240, 170, 190)
DRAGHINO_BELLY = (250, 200, 210)
DRAGHINO_EYE = (70, 195, 185)
DRAGHINO_HORN = (90, 140, 220)
DRAGHINO_WING = (60, 60, 70)
DRAGHINO_SPOTS = [(180, 130, 210), (250, 220, 90), (100, 200, 120), (250, 160, 90)]


def soft_blur(img, r=3):
    return img.filter(ImageFilter.GaussianBlur(r))


def draw_ellipse(draw, cx, cy, rx, ry, fill):
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)


def draw_cloud(draw, cx, cy, size=60):
    for dx, dy, r in [(-size*0.5, 0, size*0.45), (0, -size*0.15, size*0.55),
                       (size*0.5, 0, size*0.45), (0, size*0.1, size*0.5)]:
        draw_ellipse(draw, cx + dx, cy + dy, r, r * 0.7, CLOUD)


def draw_star(draw, cx, cy, size=4, fill=YELLOW):
    pts = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 0.4
        pts.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    draw.polygon(pts, fill=fill)


def draw_tree(draw, x, y, scale=1.0, autumn=False):
    trunk_w = int(12 * scale)
    trunk_h = int(50 * scale)
    draw.rectangle([x - trunk_w // 2, y - trunk_h, x + trunk_w // 2, y], fill=WOOD)
    foliage_r = int(40 * scale)
    if autumn:
        colours = [(220, 120, 40), (200, 80, 30), (230, 180, 50), (180, 60, 30)]
    else:
        colours = [(80, 170, 80), (60, 150, 60), (100, 190, 90)]
    for i, c in enumerate(colours):
        dx = (i - 1) * foliage_r * 0.4
        dy = -trunk_h - foliage_r * 0.3 + i * foliage_r * 0.15
        draw_ellipse(draw, x + dx, y + dy, foliage_r * 0.7, foliage_r * 0.6, c)


def draw_snow_tree(draw, x, y, scale=1.0):
    trunk_w = int(10 * scale)
    trunk_h = int(45 * scale)
    draw.rectangle([x - trunk_w // 2, y - trunk_h, x + trunk_w // 2, y], fill=WOOD_DK)
    # Snow-covered branches
    for dy_off in range(3):
        w = int((30 - dy_off * 8) * scale)
        yy = y - trunk_h + int(dy_off * 18 * scale)
        draw.polygon([(x - w, yy + int(15 * scale)), (x, yy - int(5 * scale)),
                       (x + w, yy + int(15 * scale))], fill=SNOW)


def draw_willow(draw, x, y, scale=1.0):
    trunk_w = int(14 * scale)
    trunk_h = int(55 * scale)
    draw.rectangle([x - trunk_w // 2, y - trunk_h, x + trunk_w // 2, y], fill=WOOD)
    # Drooping foliage
    for i in range(8):
        angle = -0.8 + i * 0.23
        length = int((50 + random.randint(0, 30)) * scale)
        ex = x + int(math.sin(angle) * length)
        ey = y - trunk_h + int(abs(math.cos(angle)) * length * 0.3) + length
        draw.line([(x, y - trunk_h + int(10 * scale)), (ex, min(ey, y + int(20 * scale)))],
                  fill=(80, 170, 70), width=max(2, int(4 * scale)))


# ── dragon drawing ──────────────────────────────────────────────
def draw_goldie(draw, cx, cy, scale=1.0, facing=1, flying=False):
    s = scale
    f = facing  # 1=right, -1=left
    # Wing
    wx = cx + f * int(25 * s)
    wy = cy - int(20 * s)
    if flying:
        wing_pts = [(wx, wy), (wx + f * int(50 * s), wy - int(45 * s)),
                    (wx + f * int(35 * s), wy - int(10 * s)),
                    (wx + f * int(60 * s), wy - int(30 * s)),
                    (wx + f * int(20 * s), wy + int(10 * s))]
    else:
        wing_pts = [(wx, wy), (wx + f * int(35 * s), wy - int(25 * s)),
                    (wx + f * int(25 * s), wy), (wx + f * int(40 * s), wy - int(10 * s)),
                    (wx + f * int(15 * s), wy + int(15 * s))]
    draw.polygon(wing_pts, fill=GOLDIE_WING)
    # Body
    draw_ellipse(draw, cx, cy, int(35 * s), int(28 * s), GOLDIE_BODY)
    # Belly
    draw_ellipse(draw, cx - f * int(5 * s), cy + int(5 * s), int(22 * s), int(18 * s), GOLDIE_BELLY)
    # Head
    hx = cx + f * int(30 * s)
    hy = cy - int(22 * s)
    draw_ellipse(draw, hx, hy, int(22 * s), int(20 * s), GOLDIE_BODY)
    # Eyes (big Beanie Boo style)
    ex = hx + f * int(8 * s)
    ey = hy - int(2 * s)
    er = int(12 * s)
    draw_ellipse(draw, ex, ey, er, er, WHITE)
    draw_ellipse(draw, ex, ey, int(9 * s), int(9 * s), GOLDIE_EYE)
    draw_ellipse(draw, ex, ey, int(5 * s), int(5 * s), (30, 30, 30))
    draw_ellipse(draw, ex + f * int(2 * s), ey - int(3 * s), int(3 * s), int(3 * s), WHITE)
    # Nose
    draw_ellipse(draw, hx + f * int(18 * s), hy + int(2 * s), int(4 * s), int(3 * s), YELLOW)
    # Tail
    tx = cx - f * int(35 * s)
    ty = cy + int(10 * s)
    draw.line([(cx - f * int(30 * s), cy + int(5 * s)), (tx, ty),
               (tx - f * int(10 * s), ty - int(10 * s))],
              fill=GOLDIE_BODY, width=max(2, int(8 * s)))
    # Feet
    if not flying:
        for dx in [-10, 10]:
            fx = cx + int(dx * s)
            fy = cy + int(28 * s)
            draw_ellipse(draw, fx, fy, int(8 * s), int(5 * s), GOLDIE_BODY)
    # Sparkles
    for _ in range(4):
        sx = cx + random.randint(int(-40 * s), int(40 * s))
        sy = cy + random.randint(int(-35 * s), int(5 * s))
        draw_star(draw, sx, sy, size=int(3 * s), fill=(255, 255, 200))


def draw_draghino(draw, cx, cy, scale=1.0, facing=1, flying=False):
    s = scale
    f = facing
    # Wing
    wx = cx + f * int(25 * s)
    wy = cy - int(20 * s)
    if flying:
        wing_pts = [(wx, wy), (wx + f * int(50 * s), wy - int(45 * s)),
                    (wx + f * int(35 * s), wy - int(10 * s)),
                    (wx + f * int(60 * s), wy - int(30 * s)),
                    (wx + f * int(20 * s), wy + int(10 * s))]
    else:
        wing_pts = [(wx, wy), (wx + f * int(35 * s), wy - int(25 * s)),
                    (wx + f * int(25 * s), wy), (wx + f * int(40 * s), wy - int(10 * s)),
                    (wx + f * int(15 * s), wy + int(15 * s))]
    draw.polygon(wing_pts, fill=DRAGHINO_WING)
    # Blue wing tips
    draw_ellipse(draw, wx + f * int(40 * s), wy - int(18 * s), int(6 * s), int(4 * s), DRAGHINO_HORN)
    # Body
    draw_ellipse(draw, cx, cy, int(35 * s), int(28 * s), DRAGHINO_BODY)
    # Spots
    for i, c in enumerate(DRAGHINO_SPOTS):
        sx = cx + int(((i - 1.5) * 14) * s)
        sy = cy + int(((i % 2) * 10 - 5) * s)
        draw_ellipse(draw, sx, sy, int(7 * s), int(6 * s), c)
    # Belly
    draw_ellipse(draw, cx - f * int(5 * s), cy + int(5 * s), int(20 * s), int(16 * s), DRAGHINO_BELLY)
    # Head
    hx = cx + f * int(30 * s)
    hy = cy - int(22 * s)
    draw_ellipse(draw, hx, hy, int(22 * s), int(20 * s), DRAGHINO_BODY)
    # Snout
    draw_ellipse(draw, hx + f * int(14 * s), hy + int(5 * s), int(10 * s), int(8 * s), (250, 220, 225))
    # Eyes (big teal Beanie Boo)
    ex = hx + f * int(6 * s)
    ey = hy - int(2 * s)
    er = int(12 * s)
    draw_ellipse(draw, ex, ey, er, er, WHITE)
    draw_ellipse(draw, ex, ey, int(9 * s), int(9 * s), DRAGHINO_EYE)
    draw_ellipse(draw, ex, ey, int(5 * s), int(5 * s), (30, 30, 30))
    draw_ellipse(draw, ex + f * int(2 * s), ey - int(3 * s), int(3 * s), int(3 * s), WHITE)
    # Horns
    for i in range(3):
        horn_x = hx + int((i - 1) * 8 * s)
        horn_y = hy - int(18 * s)
        draw.polygon([(horn_x - int(4 * s), hy - int(14 * s)),
                       (horn_x, horn_y - int(8 * s)),
                       (horn_x + int(4 * s), hy - int(14 * s))], fill=DRAGHINO_HORN)
    # Tail
    tx = cx - f * int(35 * s)
    ty = cy + int(10 * s)
    draw.line([(cx - f * int(30 * s), cy + int(5 * s)), (tx, ty),
               (tx - f * int(10 * s), ty - int(10 * s))],
              fill=DRAGHINO_BODY, width=max(2, int(8 * s)))
    # Feet with blue tips
    if not flying:
        for dx in [-10, 10]:
            fx = cx + int(dx * s)
            fy = cy + int(28 * s)
            draw_ellipse(draw, fx, fy, int(8 * s), int(5 * s), DRAGHINO_BODY)
            draw_ellipse(draw, fx + f * int(4 * s), fy + int(2 * s), int(4 * s), int(3 * s), DRAGHINO_HORN)


def sky_gradient(img, top, bottom, y_start=0, y_end=None):
    """Draw a vertical gradient from top colour to bottom colour."""
    d = ImageDraw.Draw(img)
    if y_end is None:
        y_end = H
    for y in range(y_start, y_end):
        t = (y - y_start) / max(1, y_end - y_start)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))


def save(img, page_num):
    # Apply a slight blur for watercolour feel
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    img.save(os.path.join(OUT, f"page-{page_num:02d}.png"))
    print(f"  Saved page-{page_num:02d}.png")


# ════════════════════════════════════════════════════════════════
# PAGE 1 — Title Page
# ════════════════════════════════════════════════════════════════
def page_01():
    img = Image.new("RGB", (W, H), SKY_LIGHT)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # Cloud
    for cx, cy, sz in [(512, 400, 120), (460, 410, 90), (560, 410, 90)]:
        draw_cloud(d, cx, cy, sz)
    # Dragons on cloud
    draw_goldie(d, 400, 370, 1.5, 1)
    draw_draghino(d, 620, 370, 1.5, -1)
    # Split scene below
    # Rochester (left)
    d.rectangle([0, 550, 512, H], fill=(60, 50, 80))
    sky_gradient(img, SKY_SUNSET, (60, 50, 80), 550, 700)
    # Skyline silhouettes
    for bx, bw, bh in [(50, 40, 120), (110, 50, 180), (180, 35, 140),
                        (230, 45, 100), (290, 55, 160), (360, 40, 130),
                        (410, 50, 110), (470, 35, 90)]:
        d.rectangle([bx, H - bh, bx + bw, H], fill=(40, 35, 55))
    # Kodak tower (taller)
    d.rectangle([140, H - 250, 175, H], fill=(50, 45, 65))
    d.rectangle([148, H - 270, 167, H - 250], fill=(55, 50, 70))

    # Cambridge (right)
    d.rectangle([512, 600, W, H], fill=GRASS)
    sky_gradient(img, (170, 210, 240), (140, 190, 220), 550, 700)
    # King's College silhouette
    d.rectangle([600, 650, 850, H], fill=STONE_LT)
    for tx in [610, 650, 800, 840]:
        d.rectangle([tx, 600, tx + 25, 650], fill=STONE)
        d.polygon([(tx, 600), (tx + 12, 570), (tx + 25, 600)], fill=STONE)
    # Gothic windows
    for wx in [660, 720, 780]:
        d.rectangle([wx, 700, wx + 25, 800], fill=(170, 200, 230))
        d.polygon([(wx, 700), (wx + 12, 680), (wx + 25, 700)], fill=(170, 200, 230))

    # Divider
    d.line([(512, 550), (512, H)], fill=WHITE, width=3)

    d.rectangle([512, H - 40, W, H], fill=GRASS)
    save(img, 1)


# ════════════════════════════════════════════════════════════════
# PAGE 2 — Meet Goldie (cave)
# ════════════════════════════════════════════════════════════════
def page_02():
    img = Image.new("RGB", (W, H), (80, 70, 60))
    d = ImageDraw.Draw(img)
    # Cave walls
    d.rectangle([0, 0, W, H], fill=(80, 70, 60))
    # Cave opening (bright)
    d.ellipse([300, 100, 900, 700], fill=SKY_BLUE)
    # Valley through opening
    d.rectangle([350, 450, 850, 700], fill=GRASS)
    d.line([(400, 500), (500, 520), (600, 510), (750, 530), (800, 520)],
           fill=WATER, width=8)
    # Cave floor
    d.rectangle([0, 650, W, H], fill=(90, 80, 65))
    # Golden rocks
    for _ in range(12):
        rx = random.randint(50, 950)
        ry = random.randint(700, 950)
        rr = random.randint(10, 25)
        draw_ellipse(d, rx, ry, rr, rr * 0.7,
                     (200 + random.randint(0, 50), 180 + random.randint(0, 40), 50))
    # Goldie
    draw_goldie(d, 500, 580, 2.5, 1)
    save(img, 2)


# ════════════════════════════════════════════════════════════════
# PAGE 3 — Meet Draghino (garden)
# ════════════════════════════════════════════════════════════════
def page_03():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    draw_cloud(d, 200, 120, 80)
    draw_cloud(d, 700, 150, 70)
    # Ground
    d.rectangle([0, 550, W, H], fill=GRASS)
    # Fence
    for fx in range(0, W, 60):
        d.rectangle([fx, 380, fx + 10, 550], fill=WOOD)
    d.rectangle([0, 420, W, 430], fill=WOOD)
    d.rectangle([0, 490, W, 500], fill=WOOD)
    # Flowers
    flower_colors = [RED, YELLOW, PINK, PURPLE, ORANGE, (100, 100, 255), WHITE]
    for _ in range(50):
        fx = random.randint(30, 990)
        fy = random.randint(560, 980)
        fc = random.choice(flower_colors)
        stem_h = random.randint(30, 70)
        d.line([(fx, fy), (fx, fy - stem_h)], fill=(50, 140, 50), width=3)
        draw_ellipse(d, fx, fy - stem_h, 12, 12, fc)
        draw_ellipse(d, fx, fy - stem_h, 5, 5, YELLOW)
    # Butterfly
    d.polygon([(800, 300), (820, 280), (830, 310)], fill=YELLOW)
    d.polygon([(800, 300), (780, 280), (770, 310)], fill=ORANGE)
    # Draghino
    draw_draghino(d, 500, 480, 2.5, 1)
    save(img, 3)


# ════════════════════════════════════════════════════════════════
# PAGE 4 — Best Friends (Genesee River, autumn)
# ════════════════════════════════════════════════════════════════
def page_04():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # River
    d.rectangle([0, 600, W, H], fill=GRASS_DARK)
    # River winding through
    river_pts = [(0, 750), (200, 720), (400, 760), (600, 730), (800, 770), (W, 740)]
    for i in range(len(river_pts) - 1):
        x1, y1 = river_pts[i]
        x2, y2 = river_pts[i + 1]
        d.polygon([(x1, y1 - 30), (x2, y2 - 30), (x2, y2 + 30), (x1, y1 + 30)], fill=WATER)
    # Autumn trees
    for tx in [80, 200, 350, 650, 800, 920]:
        draw_tree(d, tx, 600, 1.5, autumn=True)
    # Falling leaves
    for _ in range(20):
        lx = random.randint(50, 950)
        ly = random.randint(200, 700)
        lc = random.choice([(220, 120, 40), (200, 80, 30), (230, 180, 50)])
        draw_ellipse(d, lx, ly, 6, 4, lc)
    # Path
    d.rectangle([0, 660, W, 690], fill=(180, 160, 130))
    # Dragons walking
    draw_goldie(d, 350, 590, 2.0, 1)
    draw_draghino(d, 650, 590, 2.0, -1)
    save(img, 4)


# ════════════════════════════════════════════════════════════════
# PAGE 5 — High Falls
# ════════════════════════════════════════════════════════════════
def page_05():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # Cliff walls
    d.rectangle([0, 200, 300, H], fill=STONE_DK)
    d.rectangle([700, 200, W, H], fill=STONE_DK)
    # Trees on cliffs
    for tx in [80, 180, 800, 900]:
        draw_tree(d, tx, 200, 1.2)
    # Waterfall
    for wy in range(300, 800, 8):
        ww = 60 + random.randint(-10, 10)
        alpha = 200 + random.randint(-30, 30)
        d.rectangle([500 - ww, wy, 500 + ww, wy + 10],
                    fill=(200, 220, 255))
    # Mist at bottom
    for _ in range(8):
        mx = random.randint(350, 650)
        my = random.randint(750, 900)
        mr = random.randint(40, 80)
        draw_ellipse(d, mx, my, mr, mr * 0.5, (220, 235, 250))
    # Pool at bottom
    draw_ellipse(d, 500, 850, 200, 80, WATER)
    # Bridge at top
    d.rectangle([280, 250, 720, 270], fill=STONE)
    # Stone railing
    for bx in range(290, 720, 30):
        d.rectangle([bx, 230, bx + 8, 250], fill=STONE_LT)
    d.rectangle([280, 225, 720, 235], fill=STONE_LT)
    # Dragons on bridge
    draw_goldie(d, 420, 180, 1.5, 1)
    draw_draghino(d, 580, 180, 1.5, -1)
    save(img, 5)


# ════════════════════════════════════════════════════════════════
# PAGE 6 — Strong Museum
# ════════════════════════════════════════════════════════════════
def page_06():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    draw_cloud(d, 200, 100, 70)
    draw_cloud(d, 750, 130, 60)
    # Ground
    d.rectangle([0, 650, W, H], fill=GRASS)
    # Museum building — colorful modern facade
    d.rectangle([150, 350, 850, 650], fill=WHITE)
    # Colorful panels
    panel_colors = [RED, (50, 120, 220), GREEN, YELLOW, ORANGE, PURPLE]
    for i, px in enumerate(range(170, 830, 110)):
        d.rectangle([px, 370, px + 95, 520], fill=panel_colors[i % len(panel_colors)])
    # PLAY sign
    d.rectangle([350, 540, 650, 600], fill=WHITE)
    # Spell "PLAY" with colored blocks
    for i, (letter_x, color) in enumerate([(380, RED), (450, (50, 120, 220)),
                                            (520, GREEN), (580, YELLOW)]):
        d.rectangle([letter_x, 550, letter_x + 50, 590], fill=color)
    # Entrance
    d.rectangle([450, 580, 550, 650], fill=(60, 60, 60))
    # Flowers along path
    for fx in range(200, 800, 40):
        fc = random.choice([RED, YELLOW, PINK, PURPLE])
        draw_ellipse(d, fx, 670, 8, 8, fc)
    # Path
    d.polygon([(450, 650), (550, 650), (600, H), (400, H)], fill=(200, 190, 170))
    # Dragons
    draw_goldie(d, 320, 580, 1.8, 1)
    draw_draghino(d, 700, 580, 1.8, -1)
    save(img, 6)


# ════════════════════════════════════════════════════════════════
# PAGE 7 — Rochester Winter
# ════════════════════════════════════════════════════════════════
def page_07():
    img = Image.new("RGB", (W, H), (200, 215, 235))
    d = ImageDraw.Draw(img)
    sky_gradient(img, (200, 215, 235), (180, 200, 225))
    # Snowy ground
    d.rectangle([0, 500, W, H], fill=SNOW)
    # Snowy hills
    d.ellipse([-100, 450, 500, 650], fill=SNOW)
    d.ellipse([400, 480, 1100, 680], fill=SNOW)
    # Snow trees
    for tx in [100, 300, 700, 900]:
        draw_snow_tree(d, tx, 500, 1.5)
    # Snow-dragon (snowman but dragon shaped)
    draw_ellipse(d, 750, 600, 40, 35, WHITE)
    draw_ellipse(d, 750, 555, 30, 25, WHITE)
    draw_ellipse(d, 760, 545, 4, 3, (30, 30, 30))  # eye
    # Snowflakes
    for _ in range(40):
        sx = random.randint(20, 1000)
        sy = random.randint(20, 600)
        sr = random.randint(3, 7)
        draw_ellipse(d, sx, sy, sr, sr, WHITE)
    # Dragons playing
    draw_goldie(d, 350, 520, 2.0, 1)
    draw_draghino(d, 580, 540, 2.0, -1)
    save(img, 7)


# ════════════════════════════════════════════════════════════════
# PAGE 8 — Garbage Plate
# ════════════════════════════════════════════════════════════════
def page_08():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    draw_cloud(d, 250, 100, 70)
    draw_cloud(d, 700, 80, 60)
    # Ground
    d.rectangle([0, 600, W, H], fill=GRASS)
    # Picnic table
    d.rectangle([200, 480, 800, 520], fill=WOOD)  # table top
    d.rectangle([250, 520, 290, 620], fill=WOOD_DK)  # leg
    d.rectangle([710, 520, 750, 620], fill=WOOD_DK)  # leg
    d.rectangle([220, 560, 780, 580], fill=WOOD)  # bench
    # Giant plate
    draw_ellipse(d, 500, 460, 160, 50, WHITE)
    # Food!
    draw_ellipse(d, 420, 450, 45, 25, (240, 210, 100))  # mac salad
    draw_ellipse(d, 500, 445, 50, 20, (150, 100, 60))   # meat
    draw_ellipse(d, 560, 455, 35, 20, RED)               # hot sauce
    draw_ellipse(d, 460, 465, 30, 15, YELLOW)             # fries
    draw_ellipse(d, 540, 465, 25, 12, (240, 230, 200))   # onions
    # Dragons at table
    draw_goldie(d, 300, 420, 1.8, 1)
    draw_draghino(d, 700, 420, 1.8, -1)
    save(img, 8)


# ════════════════════════════════════════════════════════════════
# PAGE 9 — The Letter
# ════════════════════════════════════════════════════════════════
def page_09():
    img = Image.new("RGB", (W, H), (250, 235, 210))
    d = ImageDraw.Draw(img)
    # Warm indoor walls
    d.rectangle([0, 0, W, H], fill=(250, 235, 210))
    # Floor
    d.rectangle([0, 650, W, H], fill=(200, 175, 140))
    # Door
    d.rectangle([80, 250, 320, 650], fill=WOOD)
    draw_ellipse(d, 300, 450, 10, 10, YELLOW)  # doorknob
    # Mail slot
    d.rectangle([130, 420, 270, 445], fill=WOOD_DK)
    # Letter falling
    d.rectangle([160, 480, 280, 560], fill=WHITE)
    # Red seal
    d.polygon([(160, 480), (220, 520), (280, 480)], fill=(200, 60, 50))
    draw_ellipse(d, 220, 540, 12, 12, (180, 40, 30))
    # Dragons looking at letter
    draw_goldie(d, 480, 530, 2.2, -1)
    draw_draghino(d, 750, 530, 2.2, -1)
    save(img, 9)


# ════════════════════════════════════════════════════════════════
# PAGE 10 — Rochester Skyline at Sunset
# ════════════════════════════════════════════════════════════════
def page_10():
    img = Image.new("RGB", (W, H), SKY_SUNSET)
    d = ImageDraw.Draw(img)
    sky_gradient(img, (245, 180, 140), (200, 100, 120))
    # Sun
    draw_ellipse(d, 500, 350, 80, 80, (255, 210, 130))
    # Hill
    d.ellipse([-200, 550, 1200, 1200], fill=GRASS_DARK)
    # City skyline silhouette
    for bx, bw, bh in [(200, 40, 120), (260, 50, 180), (330, 35, 140),
                        (380, 45, 100), (440, 55, 160), (510, 40, 130),
                        (560, 50, 110), (630, 35, 90), (680, 40, 100),
                        (730, 55, 140)]:
        d.rectangle([bx, 550 - bh, bx + bw, 550], fill=(60, 40, 50))
    # Kodak Tower (prominent)
    d.rectangle([280, 300, 310, 550], fill=(70, 50, 60))
    d.rectangle([285, 280, 305, 300], fill=(80, 60, 70))
    # Dragons on hilltop
    draw_goldie(d, 380, 580, 2.0, 1)
    draw_draghino(d, 620, 580, 2.0, -1)
    save(img, 10)


# ════════════════════════════════════════════════════════════════
# PAGE 11 — Packing
# ════════════════════════════════════════════════════════════════
def page_11():
    img = Image.new("RGB", (W, H), (250, 235, 210))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 650, W, H], fill=(200, 175, 140))
    # Suitcases
    d.rectangle([80, 500, 280, 640], fill=(80, 120, 200))
    d.rectangle([80, 490, 280, 510], fill=(60, 100, 180))
    d.rectangle([320, 480, 520, 650], fill=(200, 70, 60))
    d.rectangle([320, 470, 520, 490], fill=(180, 50, 40))
    d.rectangle([600, 530, 740, 640], fill=(80, 180, 80))
    # Hot sauce jars
    for jx in [770, 830, 890]:
        d.rectangle([jx, 550, jx + 35, 640], fill=RED)
        d.rectangle([jx, 540, jx + 35, 555], fill=(160, 30, 20))
    for jx in [770, 830, 890]:
        d.rectangle([jx, 440, jx + 35, 530], fill=RED)
        d.rectangle([jx, 430, jx + 35, 445], fill=(160, 30, 20))
    # More jars on suitcase
    for jx in [110, 170, 230]:
        d.rectangle([jx, 420, jx + 35, 500], fill=RED)
        d.rectangle([jx, 410, jx + 35, 425], fill=(160, 30, 20))
    # Books
    d.rectangle([560, 570, 590, 640], fill=ORANGE)
    d.rectangle([555, 580, 575, 630], fill=PURPLE)
    # Dragons
    draw_draghino(d, 400, 400, 2.0, 1)
    draw_goldie(d, 650, 520, 2.0, -1)
    save(img, 11)


# ════════════════════════════════════════════════════════════════
# PAGE 12 — Saying Goodbye (flying away)
# ════════════════════════════════════════════════════════════════
def page_12():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    draw_cloud(d, 150, 200, 100)
    draw_cloud(d, 600, 150, 80)
    draw_cloud(d, 400, 300, 70)
    # Rochester far below
    d.rectangle([0, 700, W, H], fill=(140, 190, 160))
    # Tiny city
    for bx, bw, bh in [(300, 15, 40), (330, 18, 65), (365, 12, 35),
                        (390, 16, 30), (420, 20, 50), (450, 14, 45),
                        (475, 18, 35)]:
        d.rectangle([bx, 750 - bh, bx + bw, 750], fill=STONE_DK)
    # Tiny river
    d.line([(200, 780), (350, 770), (500, 790), (700, 775), (900, 780)],
           fill=WATER, width=4)
    # Dragons flying upward
    draw_goldie(d, 350, 450, 2.2, 1, flying=True)
    draw_draghino(d, 650, 380, 2.2, -1, flying=True)
    save(img, 12)


# ════════════════════════════════════════════════════════════════
# PAGE 13 — Over the Atlantic (day)
# ════════════════════════════════════════════════════════════════
def page_13():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    draw_cloud(d, 200, 200, 90)
    draw_cloud(d, 700, 250, 80)
    draw_cloud(d, 450, 350, 70)
    # Ocean
    d.rectangle([0, 600, W, H], fill=WATER)
    # Waves
    for wy in range(620, H, 30):
        for wx in range(0, W, 60):
            d.arc([wx, wy, wx + 50, wy + 20], 0, 180, fill=(100, 180, 230), width=2)
    # Tiny sailboat
    d.polygon([(500, 750), (510, 700), (520, 750)], fill=WHITE)
    d.rectangle([508, 700, 512, 760], fill=WOOD)
    draw_ellipse(d, 510, 760, 20, 6, WOOD)
    # Dragons flying
    draw_goldie(d, 300, 400, 2.2, 1, flying=True)
    draw_draghino(d, 650, 350, 2.2, 1, flying=True)
    save(img, 13)


# ════════════════════════════════════════════════════════════════
# PAGE 14 — Over the Atlantic (night)
# ════════════════════════════════════════════════════════════════
def page_14():
    img = Image.new("RGB", (W, H), SKY_NIGHT)
    d = ImageDraw.Draw(img)
    sky_gradient(img, (20, 25, 60), (10, 15, 40))
    # Stars
    for _ in range(80):
        sx = random.randint(20, 1000)
        sy = random.randint(20, 500)
        draw_star(d, sx, sy, random.randint(2, 5), YELLOW)
    # Crescent moon
    draw_ellipse(d, 800, 150, 50, 50, YELLOW)
    draw_ellipse(d, 820, 140, 45, 45, SKY_NIGHT)
    # Dark ocean
    d.rectangle([0, 650, W, H], fill=WATER_DARK)
    # Moonlight reflection
    for wy in range(660, H, 15):
        mw = random.randint(5, 25)
        d.rectangle([790 - mw + random.randint(-10, 10), wy,
                     810 + mw + random.randint(-10, 10), wy + 8],
                    fill=(60, 100, 150))
    # Dragons flying
    draw_goldie(d, 350, 400, 2.0, 1, flying=True)
    draw_draghino(d, 650, 370, 2.0, 1, flying=True)
    save(img, 14)


# ════════════════════════════════════════════════════════════════
# PAGE 15 — First Sight of England
# ════════════════════════════════════════════════════════════════
def page_15():
    img = Image.new("RGB", (W, H), (220, 200, 170))
    d = ImageDraw.Draw(img)
    sky_gradient(img, (240, 210, 180), (200, 220, 240))
    # Patchwork fields from above
    field_colors = [(80, 170, 70), (100, 190, 80), (120, 180, 60),
                    (160, 200, 80), (80, 160, 90), (200, 190, 100),
                    (90, 180, 75), (140, 185, 70)]
    for row in range(5):
        for col in range(6):
            x = col * 180 + random.randint(-20, 20)
            y = 450 + row * 120 + random.randint(-15, 15)
            w = 160 + random.randint(-20, 20)
            h = 100 + random.randint(-10, 10)
            fc = random.choice(field_colors)
            d.rectangle([x, y, x + w, y + h], fill=fc)
    # Hedgerows (dark lines between fields)
    for row in range(5):
        y = 450 + row * 120
        d.line([(0, y), (W, y)], fill=(40, 80, 30), width=3)
    for col in range(6):
        x = col * 180
        d.line([(x, 450), (x, H)], fill=(40, 80, 30), width=3)
    # River winding through
    pts = [(100, 600), (250, 650), (400, 620), (550, 680), (700, 640),
           (850, 700), (W, 670)]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=WATER, width=8)
    # Tiny village
    for vx in [400, 430, 460, 490]:
        d.rectangle([vx, 560, vx + 20, 580], fill=WHITE)
        d.polygon([(vx - 3, 560), (vx + 10, 548), (vx + 23, 560)], fill=RED)
    # Dragons flying above
    draw_goldie(d, 350, 300, 2.0, 1, flying=True)
    draw_draghino(d, 650, 260, 2.0, 1, flying=True)
    save(img, 15)


# ════════════════════════════════════════════════════════════════
# PAGE 16 — Arriving in Cambridge (King's College)
# ════════════════════════════════════════════════════════════════
def page_16():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    draw_cloud(d, 200, 100, 70)
    draw_cloud(d, 750, 120, 60)
    # Green lawn
    d.rectangle([0, 650, W, H], fill=(60, 180, 70))
    # King's College Chapel — grand Gothic building
    d.rectangle([200, 300, 800, 650], fill=STONE_LT)
    # Towers
    for tx in [200, 250, 720, 770]:
        d.rectangle([tx, 180, tx + 40, 300], fill=STONE)
        # Pinnacles
        d.polygon([(tx, 180), (tx + 20, 130), (tx + 40, 180)], fill=STONE)
    # Large Gothic windows
    for wx in [300, 420, 540, 660]:
        d.rectangle([wx, 380, wx + 60, 580], fill=(170, 200, 240))
        d.polygon([(wx, 380), (wx + 30, 340), (wx + 60, 380)], fill=(170, 200, 240))
        # Window mullions
        d.line([(wx + 30, 340), (wx + 30, 580)], fill=STONE, width=2)
        d.line([(wx, 480), (wx + 60, 480)], fill=STONE, width=2)
    # Buttresses
    for bx in [280, 400, 520, 640]:
        d.polygon([(bx, 650), (bx, 400), (bx + 15, 350), (bx + 15, 650)], fill=STONE_DK)
    # Stone path
    d.polygon([(450, 650), (550, 650), (620, H), (380, H)], fill=(190, 180, 165))
    # Dragons on the lawn
    draw_goldie(d, 350, 580, 2.0, 1)
    draw_draghino(d, 650, 580, 2.0, -1)
    save(img, 16)


# ════════════════════════════════════════════════════════════════
# PAGE 17 — Punting on the Cam
# ════════════════════════════════════════════════════════════════
def page_17():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # River banks
    d.rectangle([0, 400, W, H], fill=WATER)
    d.rectangle([0, 350, 200, H], fill=GRASS)
    d.rectangle([800, 350, W, H], fill=GRASS)
    # Willow trees
    draw_willow(d, 100, 400, 2.0)
    draw_willow(d, 880, 420, 1.8)
    # Punt boat
    d.polygon([(350, 600), (650, 600), (680, 620), (320, 620)], fill=WOOD)
    d.polygon([(320, 620), (350, 600), (350, 610), (325, 615)], fill=WOOD_DK)
    d.polygon([(680, 620), (650, 600), (650, 610), (675, 615)], fill=WOOD_DK)
    # Pole
    d.line([(580, 350), (590, 650)], fill=WOOD, width=4)
    # Duck watching disapprovingly
    draw_ellipse(d, 250, 530, 18, 14, WHITE)
    draw_ellipse(d, 265, 518, 12, 10, WHITE)
    draw_ellipse(d, 273, 516, 4, 3, YELLOW)  # beak
    draw_ellipse(d, 263, 514, 3, 3, (20, 20, 20))  # eye
    # Dappled sunlight on water
    for _ in range(20):
        sx = random.randint(220, 780)
        sy = random.randint(450, 750)
        draw_ellipse(d, sx, sy, random.randint(8, 20), random.randint(4, 10),
                     (120, 190, 230))
    # Dragons in punt
    draw_goldie(d, 460, 540, 1.6, 1)
    draw_draghino(d, 590, 540, 1.6, -1)
    save(img, 17)


# ════════════════════════════════════════════════════════════════
# PAGE 18 — Mathematical Bridge
# ════════════════════════════════════════════════════════════════
def page_18():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # River
    d.rectangle([0, 550, W, H], fill=WATER)
    # Left bank — red brick
    d.rectangle([0, 300, 250, 550], fill=(180, 90, 70))
    for wy in range(310, 540, 20):
        for wx in range(10, 240, 30):
            d.rectangle([wx, wy, wx + 25, wy + 15], fill=(170, 80, 60))
    # Windows
    for wx in [50, 120, 180]:
        d.rectangle([wx, 350, wx + 30, 400], fill=(200, 220, 240))
    # Right bank — stone
    d.rectangle([750, 280, W, 550], fill=STONE_LT)
    for wx in [800, 870, 940]:
        d.rectangle([wx, 340, wx + 30, 390], fill=(200, 220, 240))
    # Mathematical Bridge — wooden arch with geometric beams
    # Main arch
    arch_pts = []
    for t in range(20):
        x = 250 + t * 25
        y = 480 - int(80 * math.sin(math.pi * t / 19))
        arch_pts.append((x, y))
    # Draw the tangent beams (geometric pattern)
    for i in range(0, len(arch_pts) - 2, 2):
        d.line([arch_pts[i], arch_pts[i + 2]], fill=WOOD, width=4)
    for i in range(1, len(arch_pts) - 2, 2):
        d.line([arch_pts[i], arch_pts[i + 2]], fill=WOOD_DK, width=3)
    # Deck of bridge
    for i in range(len(arch_pts) - 1):
        x1, y1 = arch_pts[i]
        x2, y2 = arch_pts[i + 1]
        d.line([(x1, y1), (x2, y2)], fill=WOOD, width=6)
    # Railing
    for i in range(0, len(arch_pts), 3):
        x, y = arch_pts[i]
        d.line([(x, y), (x, y - 25)], fill=WOOD, width=3)
    d.line([(250, 480 - 25), (750, 480 - 25)], fill=WOOD, width=3)
    # Green banks
    d.rectangle([0, 550, 250, H], fill=GRASS)
    d.rectangle([750, 550, W, H], fill=GRASS)
    # Dragons on bridge
    draw_goldie(d, 420, 370, 1.5, 1)
    draw_draghino(d, 580, 370, 1.5, -1)
    save(img, 18)


# ════════════════════════════════════════════════════════════════
# PAGE 19 — Market Square
# ════════════════════════════════════════════════════════════════
def page_19():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # Historic buildings backdrop
    for bx, bw in [(0, 180), (200, 160), (380, 200), (600, 180), (800, 220)]:
        bh = random.randint(280, 380)
        d.rectangle([bx, 400 - bh + 300, bx + bw, 700], fill=STONE_LT)
        # Roof
        d.polygon([(bx, 400 - bh + 300), (bx + bw // 2, 400 - bh + 260),
                   (bx + bw, 400 - bh + 300)], fill=STONE_DK)
        # Windows
        for wx in range(bx + 15, bx + bw - 15, 35):
            for wy in range(400 - bh + 330, 680, 50):
                d.rectangle([wx, wy, wx + 20, wy + 30], fill=(200, 220, 240))
    # Ground / square
    d.rectangle([0, 700, W, H], fill=(190, 180, 165))
    # Market stalls with awnings
    stall_colors = [(RED, WHITE), ((50, 100, 200), WHITE), (GREEN, WHITE)]
    for i, (sx, (c1, c2)) in enumerate(zip([120, 400, 680], stall_colors)):
        # Stall frame
        d.rectangle([sx, 550, sx + 200, 700], fill=WOOD)
        d.rectangle([sx + 10, 580, sx + 190, 690], fill=WHITE)
        # Striped awning
        for stripe_x in range(sx, sx + 200, 20):
            colour = c1 if (stripe_x // 20) % 2 == 0 else c2
            d.polygon([(stripe_x, 550), (stripe_x + 20, 550),
                       (stripe_x + 25, 520), (stripe_x + 5, 520)], fill=colour)
        # Items on stall
        for ix in range(sx + 20, sx + 180, 25):
            item_c = random.choice([RED, YELLOW, PURPLE, ORANGE, PINK])
            draw_ellipse(d, ix, 640, 8, 8, item_c)
    # Dragons shopping
    draw_goldie(d, 200, 640, 1.6, 1)
    draw_draghino(d, 780, 640, 1.6, -1)
    save(img, 19)


# ════════════════════════════════════════════════════════════════
# PAGE 20 — Making Friends
# ════════════════════════════════════════════════════════════════
def page_20():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # College courtyard — stone buildings with arched windows
    d.rectangle([0, 250, 250, H], fill=STONE_LT)
    d.rectangle([750, 250, W, H], fill=STONE_LT)
    d.rectangle([0, 650, W, H], fill=GRASS)
    # Arched windows on buildings
    for wx in [40, 120]:
        d.rectangle([wx, 350, wx + 50, 480], fill=(180, 200, 220))
        d.ellipse([wx, 330, wx + 50, 380], fill=(180, 200, 220))
    for wx in [800, 880]:
        d.rectangle([wx, 350, wx + 50, 480], fill=(180, 200, 220))
        d.ellipse([wx, 330, wx + 50, 380], fill=(180, 200, 220))
    # Green quad
    d.rectangle([250, 500, 750, H], fill=(70, 180, 70))
    # "Keep Off the Grass" sign
    d.rectangle([490, 550, 530, 620], fill=WOOD)
    d.rectangle([470, 530, 550, 560], fill=WHITE)
    # Hedgehog
    draw_ellipse(d, 500, 640, 18, 14, (140, 100, 60))
    draw_ellipse(d, 515, 630, 8, 7, (160, 120, 80))
    draw_ellipse(d, 520, 627, 3, 3, (20, 20, 20))
    # Fox
    draw_ellipse(d, 750, 630, 22, 16, (200, 120, 50))
    draw_ellipse(d, 730, 622, 12, 10, (200, 120, 50))
    draw_ellipse(d, 722, 618, 4, 3, (20, 20, 20))
    # Robin on wall
    draw_ellipse(d, 270, 340, 10, 8, (140, 100, 60))
    draw_ellipse(d, 270, 335, 7, 6, RED)
    draw_ellipse(d, 277, 332, 5, 5, (140, 100, 60))
    draw_ellipse(d, 280, 330, 3, 3, (20, 20, 20))
    # Dragons
    draw_goldie(d, 380, 580, 1.8, 1)
    draw_draghino(d, 620, 580, 1.8, -1)
    save(img, 20)


# ════════════════════════════════════════════════════════════════
# PAGE 21 — Missing Rochester
# ════════════════════════════════════════════════════════════════
def page_21():
    img = Image.new("RGB", (W, H), (220, 215, 210))
    d = ImageDraw.Draw(img)
    # Cozy room
    d.rectangle([0, 0, W, H], fill=(240, 230, 200))
    # Window
    d.rectangle([200, 150, 800, 550], fill=(160, 175, 195))
    # Window frame
    d.rectangle([200, 150, 210, 550], fill=WHITE)
    d.rectangle([790, 150, 800, 550], fill=WHITE)
    d.rectangle([200, 150, 800, 160], fill=WHITE)
    d.rectangle([200, 540, 800, 550], fill=WHITE)
    d.rectangle([495, 150, 505, 550], fill=WHITE)
    d.rectangle([200, 345, 800, 355], fill=WHITE)
    # Rain streaks
    for _ in range(30):
        rx = random.randint(210, 790)
        ry = random.randint(160, 540)
        d.line([(rx, ry), (rx - 5, ry + 30)], fill=(180, 195, 210), width=2)
    # Window seat / cushion
    d.rectangle([200, 550, 800, 620], fill=(180, 140, 100))
    draw_ellipse(d, 500, 570, 280, 30, (200, 160, 120))
    # Floor
    d.rectangle([0, 620, W, H], fill=(190, 165, 130))
    # Thought bubble (Rochester landmarks)
    draw_ellipse(d, 700, 120, 150, 90, WHITE)
    # Mini waterfall in thought bubble
    d.rectangle([660, 80, 680, 160], fill=WATER)
    # Mini garbage plate in thought bubble
    draw_ellipse(d, 740, 130, 30, 12, WHITE)
    draw_ellipse(d, 735, 128, 10, 6, YELLOW)
    draw_ellipse(d, 748, 128, 8, 5, RED)
    # Thought bubble trail
    draw_ellipse(d, 640, 200, 12, 12, WHITE)
    draw_ellipse(d, 620, 240, 8, 8, WHITE)
    # Dragons on window seat
    draw_goldie(d, 380, 480, 1.8, 1)
    draw_draghino(d, 620, 480, 1.8, -1)
    save(img, 21)


# ════════════════════════════════════════════════════════════════
# PAGE 22 — Home Is Who You're With
# ════════════════════════════════════════════════════════════════
def page_22():
    img = Image.new("RGB", (W, H), SKY_BLUE)
    d = ImageDraw.Draw(img)
    sky_gradient(img, SKY_LIGHT, SKY_BLUE)
    # Park scene
    d.rectangle([0, 550, W, H], fill=GRASS)
    # Trees
    draw_tree(d, 100, 500, 2.0)
    draw_tree(d, 850, 480, 2.2)
    draw_tree(d, 200, 530, 1.5)
    # Flowers
    for _ in range(15):
        fx = random.randint(50, 950)
        fy = random.randint(650, 950)
        fc = random.choice([RED, YELLOW, PINK, PURPLE])
        draw_ellipse(d, fx, fy, 6, 6, fc)
    # Stone path
    d.line([(400, 700), (0, 950)], fill=(190, 180, 165), width=30)
    d.line([(600, 700), (W, 950)], fill=(190, 180, 165), width=30)
    # Park bench
    d.rectangle([350, 560, 650, 575], fill=WOOD)
    d.rectangle([350, 590, 650, 605], fill=WOOD)
    d.rectangle([360, 530, 370, 605], fill=WOOD_DK)
    d.rectangle([630, 530, 640, 605], fill=WOOD_DK)
    d.rectangle([350, 520, 650, 535], fill=WOOD)
    # Warm golden light effect
    draw_ellipse(d, 500, 300, 300, 250, (255, 240, 200))
    # Re-draw sky area to blend
    # Dragons on bench
    draw_goldie(d, 430, 470, 1.8, 1)
    draw_draghino(d, 570, 470, 1.8, -1)
    save(img, 22)


# ════════════════════════════════════════════════════════════════
# PAGE 23 — Cambridge at Night
# ════════════════════════════════════════════════════════════════
def page_23():
    img = Image.new("RGB", (W, H), SKY_NIGHT)
    d = ImageDraw.Draw(img)
    sky_gradient(img, (20, 25, 60), (15, 20, 45))
    # Stars
    for _ in range(60):
        sx = random.randint(20, 1000)
        sy = random.randint(20, 350)
        draw_star(d, sx, sy, random.randint(2, 5), YELLOW)
    # Crescent moon
    draw_ellipse(d, 150, 100, 40, 40, YELLOW)
    draw_ellipse(d, 165, 90, 38, 38, SKY_NIGHT)
    # Cambridge buildings below
    d.rectangle([0, 600, W, H], fill=(30, 35, 50))
    # King's College Chapel lit up
    d.rectangle([300, 500, 700, 700], fill=(50, 45, 60))
    # Glowing windows
    for wx in [340, 420, 500, 580, 650]:
        d.rectangle([wx, 530, wx + 35, 650], fill=(255, 220, 120))
        d.polygon([(wx, 530), (wx + 17, 510), (wx + 35, 530)], fill=(255, 220, 120))
    # Towers
    for tx in [300, 680]:
        d.rectangle([tx, 440, tx + 30, 500], fill=(50, 45, 60))
        d.polygon([(tx, 440), (tx + 15, 400), (tx + 30, 440)], fill=(50, 45, 60))
    # Other buildings with warm windows
    for bx, bw, bh in [(50, 100, 120), (170, 80, 90), (750, 120, 140), (900, 80, 100)]:
        d.rectangle([bx, 700 - bh, bx + bw, 700], fill=(40, 35, 55))
        for wx in range(bx + 10, bx + bw - 10, 25):
            d.rectangle([wx, 700 - bh + 20, wx + 12, 700 - bh + 35], fill=(255, 200, 100))
    # River Cam reflection
    d.rectangle([0, 750, W, H], fill=(15, 25, 45))
    # Moon reflection
    draw_ellipse(d, 150, 800, 20, 40, (40, 50, 80))
    # Rooftop where dragons sit
    d.polygon([(350, 430), (500, 380), (650, 430)], fill=(60, 55, 70))
    # Dragons on rooftop
    draw_goldie(d, 440, 370, 1.8, 1)
    draw_draghino(d, 560, 370, 1.8, -1)
    save(img, 23)


# ════════════════════════════════════════════════════════════════
# PAGE 24 — The End (cozy room)
# ════════════════════════════════════════════════════════════════
def page_24():
    img = Image.new("RGB", (W, H), (240, 225, 200))
    d = ImageDraw.Draw(img)
    # Warm room
    d.rectangle([0, 0, W, H], fill=(240, 225, 200))
    # Floor
    d.rectangle([0, 650, W, H], fill=(190, 165, 130))
    # Window (night outside)
    d.rectangle([600, 150, 850, 400], fill=SKY_NIGHT)
    d.rectangle([600, 150, 610, 400], fill=WHITE)
    d.rectangle([840, 150, 850, 400], fill=WHITE)
    d.rectangle([600, 150, 850, 160], fill=WHITE)
    d.rectangle([600, 390, 850, 400], fill=WHITE)
    d.rectangle([720, 150, 730, 400], fill=WHITE)
    d.rectangle([600, 270, 850, 280], fill=WHITE)
    # Stars through window
    for _ in range(8):
        sx = random.randint(615, 835)
        sy = random.randint(165, 385)
        draw_star(d, sx, sy, 3, YELLOW)
    # Bookshelf
    d.rectangle([100, 200, 350, 500], fill=WOOD)
    # Books
    book_colors = [RED, (50, 100, 200), GREEN, PURPLE, ORANGE, YELLOW, PINK]
    for i, bx in enumerate(range(115, 340, 25)):
        bh = random.randint(40, 80)
        d.rectangle([bx, 220, bx + 20, 220 + bh], fill=book_colors[i % len(book_colors)])
    for i, bx in enumerate(range(115, 340, 25)):
        bh = random.randint(40, 80)
        d.rectangle([bx, 320, bx + 20, 320 + bh], fill=book_colors[(i + 3) % len(book_colors)])
    # Rochester pennant (blue)
    d.polygon([(420, 180), (520, 180), (520, 280), (470, 250), (420, 280)],
              fill=(50, 100, 200))
    # Cambridge scarf (dark blue with light blue stripe)
    d.rectangle([540, 180, 580, 300], fill=(100, 50, 50))
    d.rectangle([540, 220, 580, 235], fill=(200, 180, 140))
    d.rectangle([540, 250, 580, 265], fill=(200, 180, 140))
    # Blanket pile
    draw_ellipse(d, 400, 620, 250, 80, (200, 160, 180))
    draw_ellipse(d, 400, 610, 230, 70, (180, 200, 220))
    draw_ellipse(d, 380, 605, 200, 55, (220, 180, 160))
    # Hot sauce jars on shelf
    for jx in [115, 145, 175, 205, 235, 265, 295, 325]:
        if jx < 310:
            d.rectangle([jx, 430, jx + 18, 480], fill=RED)
            d.rectangle([jx, 425, jx + 18, 435], fill=(160, 30, 20))
    # Dragons sleeping in blankets
    draw_goldie(d, 330, 560, 1.8, 1)
    draw_draghino(d, 500, 560, 1.8, -1)
    save(img, 24)


# ── Generate all pages ──────────────────────────────────────────
if __name__ == "__main__":
    print("Generating 24 illustrated pages...")
    for i in range(1, 25):
        func = globals().get(f"page_{i:02d}")
        if func:
            func()
    print("Done! All images saved to", OUT)
