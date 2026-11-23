"""Pixel-art cannon blast contribution animation.

A pixel pirate ship rides the swell at the left of the contribution grid, lights
the fuse and fires a cannon blast that sweeps left -> right through the grid,
turning every cell to gold. The second blast restores the real data. Everything
is drawn at a low logical resolution and upscaled with nearest-neighbour.

Usage: GITHUB_TOKEN=... python cannon_gif.py <username> <out.gif>
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
CYCLE = 84                    # one blast: 4.2 s
FRAMES = CYCLE * 2            # blast 1 gilds the grid, blast 2 restores it
GRID_X, GRID_Y = 76, 22       # top-left of the contribution grid
CELL, PITCH = 4, 5
SHIP_X, SHIP_Y = 4, 26        # top-left of the ship; its waterline is local y=36
SEA_Y = 62

# ── Palette ──────────────────────────────────────────────────────────────────
THEME = json.loads((Path(__file__).resolve().parent.parent / "theme.json").read_text())


def rgb(key):
    h = THEME[key].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


C = {
    "bg": rgb("bg"), "K": (10, 8, 12),
    "wood": (110, 70, 40), "woodLo": (64, 40, 24), "mast": (58, 36, 22),
    "sail": rgb("parchment"), "sailLo": rgb("parchmentDark"), "ink": rgb("ink"),
    "gold": rgb("gold"), "goldHi": rgb("goldHi"), "goldLo": rgb("goldLo"),
    "red": rgb("red"), "iron": (44, 44, 54), "ironHi": (110, 110, 126),
    "sea": rgb("sea"), "seaLo": rgb("panel"), "seaHi": rgb("seaHi"), "foam": rgb("foam"),
    "fire": (255, 140, 40), "white": (255, 255, 255),
    "smoke": (120, 130, 146), "smokeLo": (72, 82, 98),
}
DIM = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in THEME["cellLevels"]]
LIT = [C["white"], C["fire"], C["gold"], C["goldHi"]]
RESTORE = [C["white"], C["foam"], C["seaHi"]]  # then the real level colour
MUZZLE = (61, 26)  # ship-local


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


def draw_ship(f, ox, oy, recoil=0, silhouette=None):
    """An original brigantine, bow to the right, on a transparent full-canvas layer."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    P = lambda pts: [(ox + x, oy + y) for x, y in pts]
    a = lambda c: (*C[c], 255)

    # rigging behind the sails
    d.line(P([(54, 29), (65, 23)]), fill=a("mast"), width=1)           # bowsprit
    d.polygon(P([(41, 8), (63, 24), (43, 26)]), fill=a("sailLo"))       # jib
    # sails
    d.polygon(P([(16, 5), (31, 5), (33, 12), (32, 21), (16, 21), (18, 13)]), fill=a("sail"))
    d.polygon(P([(16, 5), (19, 5), (20, 13), (19, 21), (16, 21), (18, 13)]), fill=a("sailLo"))
    d.polygon(P([(34, 10), (46, 10), (48, 16), (46, 24), (34, 24), (35, 17)]), fill=a("sail"))
    d.polygon(P([(34, 10), (37, 10), (37, 24), (34, 24), (35, 17)]), fill=a("sailLo"))
    # sail emblem: tiny skull and crossbones
    for x, y in ((24, 11), (25, 11), (26, 11), (24, 12), (26, 12), (23, 14), (27, 14), (25, 15), (23, 16), (27, 16)):
        d.point((ox + x, oy + y), fill=a("ink"))
    # masts
    d.line(P([(24, 1), (24, 30)]), fill=a("mast"), width=2)
    d.line(P([(40, 6), (40, 29)]), fill=a("mast"), width=2)
    # flag streaming right from the main mast, waving
    for x in range(26, 34):
        wave = round(math.sin(2 * math.pi * (x / 6 - 8 * f / FRAMES)) * 0.8)
        for y in range(0, 4):
            d.point((ox + x, oy + y + wave), fill=a("K") if (x, y) != (29, 1) else a("white"))
    # hull
    d.polygon(P([(2, 25), (14, 25), (14, 31), (2, 31)]), fill=a("wood"))
    d.polygon(P([(2, 31), (56, 28), (52, 35), (48, 40), (10, 41), (4, 36)]), fill=a("wood"))
    d.polygon(P([(4, 36), (52, 35), (48, 40), (10, 41)]), fill=a("woodLo"))
    d.line(P([(2, 31), (56, 28)]), fill=a("gold"), width=1)
    d.line(P([(2, 25), (14, 25)]), fill=a("gold"), width=1)
    for x in (18, 26, 34, 42):
        d.rectangle(P([(x, 32), (x + 1, 33)]), fill=a("K"))
    # deck cannon at the bow
    d.line(P([(50 - recoil, 27), (60 - recoil, 25)]), fill=a("iron"), width=2)
    d.point((ox + 53 - recoil, oy + 25), fill=a("ironHi"))
    d.point((ox + 52 - recoil, oy + 27), fill=a("gold"))
    # stern lantern blinks
    if (f // 6) % 3:
        d.point((ox + 1, oy + 23), fill=a("goldHi"))

    layer = outline(layer)
    if silhouette:
        arr = np.array(layer)
        arr[arr[:, :, 3] > 0, :3] = silhouette
        layer = Image.fromarray(arr, "RGBA")
    return layer


def draw_sea(arr, f):
    """Two rolling bands across the bottom; 6 whole wave cycles per loop so it repeats seamlessly."""
    ph = 2 * math.pi * 6 * f / FRAMES
    for x in range(W):
        top = SEA_Y + round(1.3 * math.sin(2 * math.pi * x / 26 + ph))
        arr[top:, x] = C["sea"]
        low = SEA_Y + 6 + round(1.1 * math.sin(2 * math.pi * x / 18 - ph * 1.5))
        arr[low:, x] = C["seaLo"]
        if (x + f // 2) % 7 < 3:
            arr[top, x] = C["foam"]
        elif (x + f) % 5 == 0:
            arr[top, x] = C["seaHi"]


# ── Pixel font (3x5) for the callout ─────────────────────────────────────────
FONT = {
    "C": ".##|#..|#..|#..|.##", "A": ".#.|#.#|###|#.#|#.#", "N": "##.|#.#|#.#|#.#|#.#",
    "O": ".#.|#.#|#.#|#.#|.#.", "B": "##.|#.#|##.|#.#|##.", "L": "#..|#..|#..|#..|###",
    "S": ".##|#..|.#.|..#|##.", "T": "###|.#.|.#.|.#.|.#.", "!": ".#.|.#.|.#.|...|.#.",
    " ": "...|...|...|...|...",
}


def draw_text(img, text, x, y, color):
    for ch in text:
        for gy, row in enumerate(FONT[ch].split("|")):
            for gx, px in enumerate(row):
                if px == "#":
                    img.putpixel((x + gx, y + gy), color)
        x += 4


# ── Cannon blast ─────────────────────────────────────────────────────────────
YY, XX = np.mgrid[0:H, 0:W]


def dilate(m, n=1):
    for _ in range(n):
        g = m.copy()
        g[1:, :] |= m[:-1, :]; g[:-1, :] |= m[1:, :]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
        m = g
    return m


def erode(m, n=1):
    return ~dilate(~m, n)


def draw_blast(arr, cx, cy, ry, f, streaks):
    """Crescent shockwave with a cannonball riding in its hollow. Returns the leading edge x."""
    rx, d = max(5, ry * 0.58), max(4, ry * 0.5)
    outer = ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2 <= 1
    inner = ((XX - (cx - d)) / rx) ** 2 + ((YY - cy) / (ry - 1)) ** 2 <= 1
    cres = outer & ~inner
    for (oy, length, col) in streaks:  # fire trail behind the wave
        y = int(cy + oy * ry)
        for x in range(max(0, int(cx - d - length)), min(W, int(cx - d + 2))):
            if 0 <= y < H and (x * 7 + y * 3 + f) % 5:
                arr[y, x] = col
    checker = (XX + YY + f) % 2 == 0
    arr[dilate(outer, 2) & ~outer & (XX > cx - 1) & checker] = C["goldLo"]
    arr[cres] = C["fire"]
    arr[cres & dilate(inner, 1) & checker] = C["red"]
    arr[cres & ~erode(outer, 2)] = C["gold"]
    arr[cres & ~erode(outer, 1) & (XX > cx + rx * 0.5)] = C["white"] if f % 2 else C["goldHi"]
    ball = ((XX - (cx - 2)) ** 2 + (YY - cy) ** 2) <= 9
    arr[dilate(ball, 1) & ~ball] = C["K"]
    arr[ball] = C["iron"]
    arr[ball & (XX == int(cx) - 2) & (YY == int(cy) - 1)] = C["ironHi"]
    return cx + rx


# ── Frames ───────────────────────────────────────────────────────────────────
def render(weeks):
    rng = random.Random(7)
    cells = [(GRID_X + wi * PITCH, GRID_Y + wd * PITCH, lvl) for wi, w in enumerate(weeks) for wd, lvl in w]
    hit, particles, smoke = {}, [], []
    streaks = [(rng.uniform(-0.6, 0.6), rng.randint(6, 26),
                rng.choice([C["fire"], C["gold"], C["red"], C["goldLo"], C["smokeLo"]])) for _ in range(12)]
    grid_cy = GRID_Y + 7 * PITCH // 2
    WAVE_START, WAVE_END = 34, 64
    frames = []

    for f in range(FRAMES):
        cycle, t = divmod(f, CYCLE)
        if t == 0:
            hit.clear()
        impact = t == 33
        img = Image.new("RGB", (W, H), C["white"] if impact else C["bg"])
        arr = np.array(img)

        bob = round(math.sin(2 * math.pi * 4 * f / FRAMES))
        shake = rng.choice((-1, 0, 1)) if 24 <= t < 33 else 0
        recoil = 2 if 33 <= t < 37 else (1 if 37 <= t < 40 else 0)
        ox, oy = SHIP_X + shake - recoil // 2, SHIP_Y + bob
        mx, my = ox + MUZZLE[0] - recoil, oy + MUZZLE[1]
        ship = draw_ship(f, ox, oy, recoil, silhouette=C["K"] if impact else None)

        if WAVE_START <= t < WAVE_END + 4:
            if t == WAVE_START:
                m0 = (mx, my)
            prog = (t - WAVE_START) / (WAVE_END - WAVE_START)
            cx = m0[0] - 2 + (W + 40 - m0[0]) * (prog ** 1.15)
            ry = min(22, 6 + (t - WAVE_START) * 4)
            cy = grid_cy + (m0[1] - grid_cy) * max(0, 1 - (t - WAVE_START) / 4)

        for (x, y, lvl) in cells:
            key = (x, y)
            if WAVE_START <= t < WAVE_END + 4 and key not in hit and cx + max(5, ry * 0.58) >= x + CELL / 2:
                hit[key] = t
            if impact:
                col = C["K"]
            elif cycle == 0:      # blast 1: real data -> gold
                col = LIT[min(t - hit[key], 3)] if key in hit else DIM[lvl]
            elif key in hit:      # blast 2: gold -> real data
                age = t - hit[key]
                col = RESTORE[age] if age < len(RESTORE) else DIM[lvl]
            else:
                col = C["goldHi"]
            arr[y:y + CELL, x:x + CELL] = col

        # fuse sparks climbing to the cannon, then sparks converging on the muzzle
        if 14 <= t < 33:
            fx, fy = ox + 51, oy + 25
            for _ in range(3):
                particles.append([fx + rng.uniform(-1, 1), fy, rng.uniform(-0.6, 0.6), -rng.uniform(0.4, 1.2),
                                  rng.randint(3, 6), rng.choice([C["goldHi"], C["fire"], C["white"]])])
        if 22 <= t < 33:
            for _ in range(3):
                a = rng.uniform(0, 2 * math.pi); r = rng.uniform(10, 18)
                particles.append([mx + math.cos(a) * r, my + math.sin(a) * r, -math.cos(a) * r / 5, -math.sin(a) * r / 5,
                                  5, rng.choice([C["goldHi"], C["gold"], C["white"]])])
        if impact:  # muzzle flash rays
            for _ in range(18):
                a = rng.uniform(-math.pi / 2, math.pi / 2); r0, r1 = rng.uniform(4, 10), rng.uniform(30, 140)
                for k in range(int(r0), int(r1)):
                    px, py = int(mx + math.cos(a) * k), int(my + math.sin(a) * k)
                    if 0 <= px < W and 0 <= py < H:
                        arr[py, px] = C["gold"]
        if 33 <= t < 40:  # smoke puffs roll back over the deck
            for _ in range(2):
                smoke.append([mx + rng.uniform(-2, 3), my + rng.uniform(-2, 2), -rng.uniform(0.3, 0.9), -rng.uniform(0, 0.4),
                              rng.uniform(1.5, 2.5), rng.randint(14, 26)])

        if WAVE_START <= t < WAVE_END + 4:
            front = draw_blast(arr, cx, cy, ry, f, streaks)
            for _ in range(6):
                particles.append([front - rng.uniform(4, 20), cy + rng.uniform(-ry, ry), -rng.uniform(0.5, 2.5),
                                  rng.uniform(-0.6, 0.6), rng.randint(6, 14),
                                  rng.choice([C["fire"], C["gold"], C["goldHi"], C["white"]])])
        # glints rise off the gilded grid; bubbles off the restored one
        if WAVE_END <= t < 74 and t % 2 == 0:
            for _ in range(3):
                particles.append([rng.uniform(GRID_X, GRID_X + len(weeks) * PITCH), GRID_Y + rng.uniform(0, 34),
                                  rng.uniform(-0.2, 0.2), -rng.uniform(0.3, 0.8), rng.randint(8, 14),
                                  rng.choice([C["goldHi"], C["white"]] if cycle == 0 else [C["foam"], C["seaHi"]])])

        alive = []
        for p in particles:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                arr[y, x] = p[5]
            p[0] += p[2]; p[1] += p[3]; p[4] -= 1
            if p[4] > 0:
                alive.append(p)
        particles = alive

        img = Image.fromarray(arr)
        img.paste(ship, (0, 0), ship)
        arr = np.array(img)
        puffs = []
        for s in smoke:
            disc = (XX - s[0]) ** 2 + (YY - s[1]) ** 2 <= s[4] ** 2
            arr[disc & ((XX + YY + f) % 2 == 0)] = C["smokeLo"]
            arr[disc & ~dilate(~disc, 1) & ((XX + YY) % 3 == 0)] = C["smoke"]
            s[0] += s[2]; s[1] += s[3]; s[4] += 0.25; s[5] -= 1
            if s[5] > 0:
                puffs.append(s)
        smoke = puffs
        if not impact:
            draw_sea(arr, f)
        img = Image.fromarray(arr)
        if 34 <= t < 70:
            draw_text(img, "CANNON BLAST!", GRID_X, GRID_Y - 9, C["gold"] if f % 4 else C["goldHi"])
        frames.append(img.resize((W * SCALE, H * SCALE), Image.NEAREST))
    return frames


def save_gif(frames, out):
    colors = {}
    for fr in frames:
        for _, c in fr.getcolors(1 << 16):
            colors[c] = 1
    if len(colors) > 256:
        raise SystemExit(f"{len(colors)} colours; palette overflow")
    pal = [v for c in colors for v in c] + [0] * (768 - 3 * len(colors))
    pimg = Image.new("P", (1, 1)); pimg.putpalette(pal)
    q = [fr.quantize(palette=pimg, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(out, save_all=True, append_images=q[1:], duration=1000 // FPS, loop=0, optimize=False, disposal=1)


if __name__ == "__main__":
    user, out = sys.argv[1], sys.argv[2]
    frames = render(fetch_weeks(user, os.environ["GITHUB_TOKEN"]))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    save_gif(frames, out)
    print(f"wrote {out}: {len(frames)} frames")
