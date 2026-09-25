"""Pixel-art Getsuga Tenshō contribution animation.

A pixel Ichigo stands at the left of the contribution grid, charges, swings
Zangetsu and fires a Getsuga Tenshō that sweeps left -> right through the grid,
igniting every cell orange. Everything is drawn at a low logical resolution and
upscaled with nearest-neighbour so it stays crisp pixel art.

Usage: GITHUB_TOKEN=... python getsuga_gif.py <username> <out.gif> [--sprites out.png]
"""
import json
import math
import os
import random
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

# ── Canvas ───────────────────────────────────────────────────────────────────
SCALE = 3
W, H = 346, 78                # logical pixels -> 1038x234 output
FPS = 20
CYCLE = 84                    # one slash: 4.2 s
FRAMES = CYCLE * 2            # slash 1 ignites the grid, slash 2 restores it
GRID_X, GRID_Y = 76, 25       # top-left of the contribution grid
CELL, PITCH = 4, 5
HERO_X, HERO_Y = 18, 24       # top-left of Ichigo's body sprite

# ── Palette ──────────────────────────────────────────────────────────────────
THEME = json.loads((Path(__file__).resolve().parent.parent / "theme.json").read_text())


def rgb(key):
    h = THEME[key].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


C = {
    "bg": rgb("bg"), "rim": rgb("violet"), "ground": (20, 20, 28),
    "K": (8, 8, 14), "H": (255, 122, 26), "h": (196, 74, 0), "L": (255, 184, 92),
    "S": (242, 198, 160), "s": (201, 143, 106), "E": (20, 20, 30), "W": (232, 232, 240),
    "w": (170, 170, 190), "B": (32, 32, 48), "b": (66, 66, 98), "R": (138, 42, 42),
    "N": (96, 60, 36),
    "blade": (184, 194, 207), "bladeDark": (74, 82, 96), "bladeEdge": (255, 255, 255),
    "red": rgb("crimson"), "redHi": rgb("accent"), "redLo": rgb("deepRed"),
    "energy": rgb("blood"), "energyHi": rgb("accent"), "energyLo": rgb("borderHi"),
    "violet": rgb("violetCold"), "violetHi": rgb("violetPale"), "core": rgb("bgDeep"), "white": rgb("text"),
}
DIM = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in THEME["cellLevels"]]
LIT = [(255, 255, 255), (255, 196, 204), (255, 110, 128), C["energy"]]
RESTORE = [(255, 255, 255), (214, 198, 232), (150, 120, 182)]  # then the real level colour

# Ichigo (no arms/sword): 24 x 41, facing right.
BODY = """
........K..K............
.......KHK.KK...K.......
...K...KHHKHLK.KHK......
..KHK.KHHHHHLHKHHK......
..KHHKHHHHHHHLHHHK.K....
.KHHHHHHHHHHHHHHHKKHK...
KHHHHhHHHHHHHHLHHHHHK...
.KKHhHHHHHHHHHHHHHHK....
..KhHHHHHHHHHHHHHHHHK...
.KhhHHHHHHHHHHHHHHHK....
..KhHHHHHHSSSSHHHHK.....
..KhHHHHSSKKSSSKKK......
..KhHHHSSSEWSSSEWK......
..KKhHSsSSSSSSSSSK......
...KhHsSSSSSSSKKK.......
....KKsSSSSSSSSK........
.....KKsSSSSSKK.........
......KKSSSSK...........
....KKBBWWWWBBKK........
...KBBBBWWWWBBBBK.......
..KBBBBBBWWBBRRBBK......
..KBBBBBBBWBRRBBBBK.....
..KBBBBBBBBRRBBBBBK.....
..KBBBBBBBRRBBBBBBK.....
..KBBBBBBRRBBBBBBBK.....
..KBBBBBRRBBBBBBBBK.....
..KWWWWWWWWWWWWWWWK.....
..KBBBBBBBBBBBBBBBBK....
.KBBBBBBBbBBBBBBBBBK....
.KBBBBBBBbBBBBBBBBBBK...
.KBBBBBBBKBBBBBBBBBBK...
KBBBBBBBK.KBBBBBBBBBBK..
KBBBBBBK...KBBBBBBBBBK..
KBBBBBBK...KBBBBBBBBBBK.
KBBBBBK.....KBBBBBBBBBK.
KBBBBBK.....KBBBBBBBBBBK
KKKKKKK.....KKKKKKKKKKKK
KWWWWK.......KWWWWWK....
KNNNNNK......KNNNNNNK...
""".strip("\n").splitlines()
SHOULDER = (14, 20)  # front shoulder, body-local
BACK_SHOULDER = (6, 21)

# Pose = (grip x, grip y, blade angle in degrees; 0 = pointing right, -90 = up)
POSES = {
    "idle":   (19, 27, -58),
    "charge": (13, 14, -128),
    "windup": (17, 17, -100),
    "swing":  (23, 24, 8),
    "follow": (23, 28, 24),
    "finish": (22, 29, 28),
}
BLADE_LEN, BLADE_W, HILT_LEN = 34, 6, 7


# ── Data ─────────────────────────────────────────────────────────────────────
def fetch_weeks(user, token):
    query = """query($login:String!){ user(login:$login){ contributionsCollection{
      contributionCalendar{ weeks{ contributionDays{ weekday contributionLevel } } } } } }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    level = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [[(d["weekday"], level[d["contributionLevel"]]) for d in w["contributionDays"]] for w in weeks]


# ── Drawing helpers ──────────────────────────────────────────────────────────
def rot(px, py, ang):
    a = math.radians(ang)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)


def blade_polys(gx, gy, ang):
    """Zangetsu (shikai cleaver) polygons in canvas-local coords around the grip."""
    def pts(local):
        return [(gx + x, gy + y) for x, y in (rot(px, py, ang) for px, py in local)]
    L, w = BLADE_LEN, BLADE_W
    blade = pts([(3, -w / 2), (L - 3, -w / 2), (L, w / 2), (3, w / 2)])
    back = pts([(3, -w / 2), (L - 3, -w / 2), (L - 2.5, -w / 2 + 1.5), (3, -w / 2 + 1.5)])
    edge = pts([(3, w / 2 - 0.2), (L, w / 2 - 0.2)])
    hilt = pts([(-HILT_LEN, -1.2), (3, -1.2), (3, 1.2), (-HILT_LEN, 1.2)])
    tip = pts([(L, w / 2)])[0]
    pommel = pts([(-HILT_LEN, 0)])[0]
    return blade, back, edge, hilt, tip, pommel


def outline(layer, color=C["K"]):
    """Add a 1px pixel-art outline around every opaque pixel of an RGBA layer."""
    a = np.array(layer)[:, :, 3] > 0
    grown = a.copy()
    grown[1:, :] |= a[:-1, :]; grown[:-1, :] |= a[1:, :]
    grown[:, 1:] |= a[:, :-1]; grown[:, :-1] |= a[:, 1:]
    ring = grown & ~a
    arr = np.array(layer)
    arr[ring] = (*color, 255)
    return Image.fromarray(arr, "RGBA")


def draw_hero(pose, bob=0, flutter=0, glow=0.0, silhouette=None, rng=None):
    """Render Ichigo + Zangetsu on a transparent full-canvas layer."""
    gx, gy, ang = POSES[pose]
    ox, oy = HERO_X, HERO_Y + bob
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    blade, back, edge, hilt, tip, pommel = blade_polys(ox + gx, oy + gy, ang)
    hand_front = (round(ox + gx), round(oy + gy))
    bx, by = rot(-4, 0, ang)
    hand_back = (round(ox + gx + bx), round(oy + gy + by))

    # back arm (behind the body)
    bsx, bsy = ox + BACK_SHOULDER[0], oy + BACK_SHOULDER[1]
    d.line([(bsx, bsy), hand_back], fill=(*C["B"], 255), width=4)

    # body sprite
    for y, row in enumerate(BODY):
        for x, ch in enumerate(row):
            if ch != ".":
                layer.putpixel((ox + x, oy + y), (*C[ch], 255))
    # coat-tail flutter: shift a couple of hem pixels on alternate frames
    if flutter:
        for y in (30, 31, 32):
            layer.putpixel((ox + 20 + (y - 30), oy + y), (*C["B"], 255))

    # blade glow (charge) drawn behind the sword
    if glow > 0:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.polygon(blade, fill=(*C["violet"], 255))
        for _ in range(int(1 + glow * 2)):
            g = outline(g, C["violetHi"] if rng.random() < 0.5 else C["energy"])
        layer = Image.alpha_composite(g, layer)
        d = ImageDraw.Draw(layer)

    # arm: wide black sleeve from shoulder to grip, then hand
    sx, sy = ox + SHOULDER[0], oy + SHOULDER[1]
    hx, hy = ox + gx, oy + gy
    d.line([(sx, sy), (hx, hy)], fill=(*C["B"], 255), width=5)
    d.line([(sx, sy + 1), ((sx + hx) / 2, (sy + hy) / 2 + 1)], fill=(*C["b"], 255), width=1)

    # Zangetsu
    d.polygon(hilt, fill=(*C["W"], 255))
    d.polygon(blade, fill=(*C["blade"], 255))
    d.polygon(back, fill=(*C["bladeDark"], 255))
    d.line(edge, fill=(*C["bladeEdge"], 255), width=1)
    # trailing hilt cloth
    cx, cy = pommel
    for i in range(6):
        wave = math.sin((i + flutter * 2) * 0.9) * 1.2
        d.point((cx - 1 - i, cy + 1 + i // 2 + wave), fill=(*C["W"], 255))
    # two outlined fists gripping the hilt
    for fx, fy in (hand_back, hand_front):
        d.rectangle([fx - 2, fy - 2, fx + 2, fy + 2], fill=(*C["K"], 255))
        d.rectangle([fx - 1, fy - 1, fx + 1, fy + 1], fill=(*C["S"], 255))
        d.line([(fx - 1, fy + 1), (fx + 1, fy + 1)], fill=(*C["s"], 255))

    layer = outline(outline(layer), C["rim"])
    if silhouette:
        arr = np.array(layer)
        arr[arr[:, :, 3] > 0, :3] = silhouette
        layer = Image.fromarray(arr, "RGBA")
    return layer, tip


# ── Sprite sheet preview ────────────────────────────────────────────────────
def sprite_sheet(path):
    tiles = []
    rng = random.Random(1)
    for pose in POSES:
        lay, _ = draw_hero(pose, glow=1.0 if pose == "charge" else 0, rng=rng)
        tile = Image.new("RGBA", (70, 100), (*C["bg"], 255))
        tile.alpha_composite(lay.crop((0, 0, 70, 100)))
        tiles.append(tile)
    sheet = Image.new("RGBA", (70 * len(tiles), 100))
    for i, t in enumerate(tiles):
        sheet.paste(t, (70 * i, 0))
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save(path)


# ── Pixel font (3x5) for the callout ─────────────────────────────────────────
FONT = {
    "G": ".##|#..|#.#|#.#|.##", "E": "###|#..|##.|#..|###", "T": "###|.#.|.#.|.#.|.#.",
    "S": ".##|#..|.#.|..#|##.", "U": "#.#|#.#|#.#|#.#|###", "A": ".#.|#.#|###|#.#|#.#",
    "N": "##.|#.#|#.#|#.#|#.#", "H": "#.#|#.#|###|#.#|#.#", "O": ".#.|#.#|#.#|#.#|.#.",
    "!": ".#.|.#.|.#.|...|.#.", " ": "...|...|...|...|...",
}


def draw_text(img, text, x, y, color):
    for ch in text:
        macron = ch == "Ō"
        glyph = FONT["O" if macron else ch].split("|")
        for gy, row in enumerate(glyph):
            for gx, px in enumerate(row):
                if px == "#":
                    img.putpixel((x + gx, y + gy), color)
        if macron:
            for gx in range(3):
                img.putpixel((x + gx, y - 2), color)
        x += 4


# ── Getsuga Tenshō ───────────────────────────────────────────────────────────
YY, XX = np.mgrid[0:H, 0:W]


def dilate(m, n=1):
    for _ in range(n):
        g = m.copy()
        g[1:, :] |= m[:-1, :]; g[:-1, :] |= m[1:, :]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
        m = g
    return m


def erode(m, n=1):
    return ~dilate(~m, n)


def paint(arr, mask, color):
    arr[mask] = color


def draw_getsuga(arr, cx, cy, ry, f, streaks):
    rx, d = max(5, ry * 0.58), max(4, ry * 0.5)
    outer = ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2 <= 1
    inner = ((XX - (cx - d)) / rx) ** 2 + ((YY - cy) / (ry - 1)) ** 2 <= 1
    cres = outer & ~inner
    # energy trail behind the wave
    for (oy, length, col) in streaks:
        y = int(cy + oy * ry)
        x0 = int(cx - d - length)
        for x in range(max(0, x0), min(W, int(cx - d + 2))):
            if 0 <= y < H and (x * 7 + y * 3 + f) % 5:
                arr[y, x] = col
    checker = (XX + YY + f) % 2 == 0
    glow = dilate(outer, 2) & ~outer & (XX > cx - 1) & checker
    paint(arr, glow, C["energyLo"])
    paint(arr, cres, C["core"])
    paint(arr, cres & dilate(inner, 2), C["violet"])
    paint(arr, cres & dilate(inner, 1) & checker, C["violetHi"])
    paint(arr, cres & ~erode(outer, 2), C["energy"])
    lead = cres & ~erode(outer, 1) & (XX > cx + rx * 0.5)
    paint(arr, lead, C["white"] if f % 2 else C["energyHi"])
    return cx + rx  # leading edge


# ── Red reiatsu aura ─────────────────────────────────────────────────────────
def draw_aura(arr, mask, f, charging, rng):
    pulse = (math.sin(2 * math.pi * 12 * f / FRAMES) + 1) / 2     # 12 pulses per loop (~1.4/s), seamless
    r = 2 + round(pulse * 2) + (2 if charging else 0)
    inner = dilate(mask, 1)
    mid = dilate(mask, max(2, r - 1))
    outer = dilate(mask, r)
    checker = (XX + YY + f) % 2 == 0
    paint(arr, outer & ~mid & checker, C["redLo"])
    paint(arr, mid & ~inner, C["red"] if pulse > 0.35 or charging else C["redLo"])
    paint(arr, inner & ~mask & ((XX * 3 + YY + f) % 4 == 0), C["redHi"])
    # flame licks rising off the aura
    ys, xs = np.nonzero(outer & ~mid)
    if len(xs):
        for i in rng.sample(range(len(xs)), min(len(xs), 10 if charging else 5)):
            x, y = xs[i], ys[i]
            for k in range(rng.randint(1, 4)):
                if y - k >= 0:
                    arr[y - k, x] = C["red"] if k < 2 else C["redLo"]


# ── Frames ───────────────────────────────────────────────────────────────────
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render(weeks):
    rng = random.Random(7)
    cells = [(GRID_X + wi * PITCH, GRID_Y + wd * PITCH, lvl) for wi, w in enumerate(weeks) for wd, lvl in w]
    hit = {}
    particles = []
    streaks = [(rng.uniform(-0.7, 0.7), rng.randint(6, 26),
                rng.choice([C["violet"], C["violetHi"], C["energy"], C["energyLo"], C["core"]])) for _ in range(12)]
    grid_cy = GRID_Y + 7 * PITCH // 2
    WAVE_START, WAVE_END = 34, 64
    frames = []

    for f in range(FRAMES):
        cycle, t = divmod(f, CYCLE)
        if t == 0:
            hit.clear()
        img = Image.new("RGB", (W, H), C["bg"])
        d = ImageDraw.Draw(img)
        impact = t == 33
        if impact:
            img.paste(C["white"], (0, 0, W, H))
        # ground shadow under Ichigo
        d.line([(HERO_X - 2, HERO_Y + 39), (HERO_X + 26, HERO_Y + 39)], fill=C["ground"])

        # pose timeline
        if t < 16 or t >= 78:
            pose = "idle"
        elif t < 30:
            pose = "charge"
        elif t < 32:
            pose = "windup"
        elif t < 36:
            pose = "swing"
        elif t < 41:
            pose = "follow"
        else:
            pose = "finish"
        bob = -1 if pose == "idle" and (t // 5) % 2 else 0
        glow = (t - 16) / 13 if pose == "charge" else 0
        hero, tip = draw_hero(pose, bob=bob, flutter=(f // 3) % 2, glow=glow,
                              silhouette=C["K"] if impact else None, rng=rng)

        if t == WAVE_START:
            tip0 = tip
        # wave position
        front = -1
        arr = np.array(img)
        if WAVE_START <= t < WAVE_END + 4:
            prog = (t - WAVE_START) / (WAVE_END - WAVE_START)
            x0, x1 = tip0[0] - 4, W + 40
            cx = x0 + (x1 - x0) * (prog ** 1.15)
            ry = min(27, 9 + (t - WAVE_START) * 5)
            cy = grid_cy + (tip0[1] - grid_cy) * max(0, 1 - (t - WAVE_START) / 4)
        # cells
        for (x, y, lvl) in cells:
            key = (x, y)
            if WAVE_START <= t < WAVE_END + 4:
                front_est = cx + max(5, ry * 0.58)
                if key not in hit and front_est >= x + CELL / 2:
                    hit[key] = t
            if impact:
                col = C["K"]
            elif cycle == 0:      # slash 1: real data -> orange
                col = LIT[min(t - hit[key], 3)] if key in hit else DIM[lvl]
            elif key in hit:      # slash 2: orange -> real data
                age = t - hit[key]
                col = RESTORE[age] if age < len(RESTORE) else DIM[lvl]
            else:
                col = C["energy"]
            arr[y:y + CELL, x:x + CELL] = col

        # charge particles converge on the blade tip
        if 16 <= t < 32:
            for _ in range(4):
                a = rng.uniform(0, 2 * math.pi); r = rng.uniform(14, 24)
                particles.append([tip[0] + math.cos(a) * r, tip[1] + math.sin(a) * r,
                                  -math.cos(a) * r / 5, -math.sin(a) * r / 5, 5,
                                  rng.choice([C["violetHi"], C["energy"], C["white"]])])
        # reiatsu aura rising around Ichigo while charging
        if 14 <= t < 32:
            for _ in range(2 + (t - 14) // 4):
                particles.append([HERO_X + rng.uniform(-2, 26), HERO_Y + rng.uniform(10, 40),
                                  rng.uniform(-0.2, 0.2), -rng.uniform(0.8, 1.8), rng.randint(4, 9),
                                  rng.choice([C["violetHi"], C["violet"], C["energy"]])])
        # swing smear arc
        if t == 32:
            sx, sy = HERO_X + SHOULDER[0], HERO_Y + SHOULDER[1]
            for ang in range(-110, 12, 2):
                for rr in (38, 39, 40):
                    px, py = sx + math.cos(math.radians(ang)) * rr, sy + math.sin(math.radians(ang)) * rr
                    if 0 <= px < W and 0 <= py < H:
                        arr[int(py), int(px)] = C["white"] if rr == 39 else C["energyHi"]
        if impact:
            for _ in range(18):
                a = rng.uniform(-math.pi, math.pi); r0, r1 = rng.uniform(6, 14), rng.uniform(40, 160)
                for k in range(int(r0), int(r1), 1):
                    px, py = int(tip[0] + math.cos(a) * k), int(tip[1] + math.sin(a) * k)
                    if 0 <= px < W and 0 <= py < H:
                        arr[py, px] = C["energy"]

        # wave + trailing particles
        if WAVE_START <= t < WAVE_END + 4:
            front = draw_getsuga(arr, cx, cy, ry, f, streaks)
            for _ in range(7):
                particles.append([front - rng.uniform(4, 20), cy + rng.uniform(-ry, ry),
                                  -rng.uniform(0.5, 2.5), rng.uniform(-0.6, 0.6), rng.randint(6, 14),
                                  rng.choice([C["energy"], C["energyHi"], C["violetHi"], C["white"]])])
        # embers drift up from the lit grid
        if WAVE_END <= t < 74 and t % 2 == 0:
            for _ in range(3):
                particles.append([rng.uniform(GRID_X, GRID_X + len(weeks) * PITCH), GRID_Y + rng.uniform(0, 34),
                                  rng.uniform(-0.2, 0.2), -rng.uniform(0.3, 0.8), rng.randint(8, 14),
                                  rng.choice([C["energy"], C["energyHi"]] if cycle == 0 else [C["violetHi"], C["violet"]])])
        alive = []
        for p in particles:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                arr[y, x] = p[5]
            p[0] += p[2]; p[1] += p[3]; p[4] -= 1
            if p[4] > 0:
                alive.append(p)
        particles = alive

        if not impact:
            draw_aura(arr, np.array(hero)[:, :, 3] > 0, f, charging=16 <= t < 30, rng=rng)
        img = Image.fromarray(arr)
        img.paste(hero, (0, 0), hero)
        if 34 <= t < 70:
            draw_text(img, "GETSUGA TENSHŌ!", GRID_X, GRID_Y - 10, C["energy"] if f % 4 else C["energyHi"])
        frames.append(img.resize((W * SCALE, H * SCALE), Image.NEAREST))
    return frames


def save_gif(frames, out):
    colors = {}
    for fr in frames[::1]:
        for _, c in fr.getcolors(1 << 16):
            colors[c] = 1
    if len(colors) > 256:
        raise SystemExit(f"{len(colors)} colours; palette overflow")
    pal = [v for c in colors for v in c] + [0] * (768 - 3 * len(colors))
    pimg = Image.new("P", (1, 1)); pimg.putpalette(pal)
    q = [fr.quantize(palette=pimg, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(out, save_all=True, append_images=q[1:], duration=1000 // FPS, loop=0, optimize=False, disposal=1)


if __name__ == "__main__":
    if "--sprites" in sys.argv:
        sprite_sheet(sys.argv[sys.argv.index("--sprites") + 1])
        raise SystemExit
    user, out = sys.argv[1], sys.argv[2]
    frames = render(fetch_weeks(user, os.environ["GITHUB_TOKEN"]))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    save_gif(frames, out)
    print(f"wrote {out}: {len(frames)} frames")
