"""Blood pool footer: a pool of blood on a subwoofer. Every bass hit makes the
surface spike, droplets burst up and fall back with splashes, and ripples spread
out from the centre. Pure SVG/SMIL so it animates inside a GitHub README <img>.

Usage: python blood_pool.py <out.svg>
"""
import json
import math
import random
import sys
from pathlib import Path

T = json.loads((Path(__file__).resolve().parent.parent / "theme.json").read_text())
W, H = 1000, 180
Y0 = 128                 # resting surface height
DUR = 2.4                # loop length (s)
BOOMS = (0.0, 1.2)       # bass hits within the loop
G = 900.0                # gravity, px/s^2
rng = random.Random(11)


def since_boom(t):
    return min((t - b) % DUR for b in BOOMS)


# Crown spikes: where the surface jumps hardest on each hit (also droplet origins).
CROWNS = [rng.uniform(140, 860) for _ in range(9)]


def surface_y(x, t):
    dt = since_boom(t)
    env = math.exp(-dt * 3.4)
    wobble = math.cos(dt * 2 * math.pi * 6.5)
    fade_ends = min(1, x / 120, (W - x) / 120)
    y = 7 * env * wobble * math.sin(2 * math.pi * x / 83) + 3.5 * env * math.sin(2 * math.pi * x / 41 + dt * 9)
    spike = math.exp(-dt * 9)
    for c in CROWNS:
        y += 28 * spike * math.exp(-((x - c) / 12) ** 2)
    y += 1.2 * math.sin(2 * math.pi * (x / 310 + t / DUR))  # idle slosh
    return Y0 - y * fade_ends


def surface_path(t, closed):
    xs = [i * 20 for i in range(51)]
    pts = [(x, surface_y(x, t)) for x in xs]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx = (x0 + x1) / 2
        d += f" Q{x0:.1f},{y0:.1f} {mx:.1f},{(y0 + y1) / 2:.1f}"
    d += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
    if closed:
        d += f" L{W},{H} L0,{H} Z"
    return d


def fmt(v):
    return ";".join(v)


def anim(attr, values, key_times=None, calc="linear", extra=""):
    kt = f' keyTimes="{";".join(f"{k:.4f}" for k in key_times)}"' if key_times else ""
    return (f'<animate attributeName="{attr}" dur="{DUR}s" repeatCount="indefinite" '
            f'calcMode="{calc}" values="{fmt(values)}"{kt}{extra}/>')


def build():
    out = []
    add = out.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    add(f'''<defs>
  <linearGradient id="pool" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{T["crimson"]}"/>
    <stop offset="0.12" stop-color="{T["deepRed"]}"/>
    <stop offset="0.55" stop-color="#3a0610"/>
    <stop offset="1" stop-color="{T["bgDeep"]}"/>
  </linearGradient>
  <linearGradient id="ends" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.1" stop-color="#fff" stop-opacity="1"/>
    <stop offset="0.9" stop-color="#fff" stop-opacity="1"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="fade"><rect width="{W}" height="{H}" fill="url(#ends)"/></mask>
  <radialGradient id="drop" cx="0.35" cy="0.3" r="0.8">
    <stop offset="0" stop-color="{T["accent"]}"/>
    <stop offset="0.45" stop-color="{T["crimson"]}"/>
    <stop offset="1" stop-color="{T["deepRed"]}"/>
  </radialGradient>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{T["crimson"]}" stop-opacity="0.45"/>
    <stop offset="0.6" stop-color="{T["deepRed"]}" stop-opacity="0.15"/>
    <stop offset="1" stop-color="{T["bgDeep"]}" stop-opacity="0"/>
  </radialGradient>
</defs>''')

    frames = [i * DUR / 48 for i in range(49)]
    kts = [t / DUR for t in frames]

    # glow pulsing with the bass
    glow_op = [f"{0.25 + 0.75 * math.exp(-since_boom(t) * 4):.3f}" for t in frames]
    add(f'<ellipse cx="{W / 2}" cy="{Y0}" rx="{W * 0.55}" ry="70" fill="url(#glow)">{anim("opacity", glow_op, kts)}</ellipse>')

    add('<g mask="url(#fade)">')
    # pool body + glossy surface line
    body = [surface_path(t, True) for t in frames]
    line = [surface_path(t, False) for t in frames]
    add(f'<path fill="url(#pool)" d="{body[0]}">{anim("d", body, kts)}</path>')
    add(f'<path fill="none" stroke="{T["accent"]}" stroke-width="1.6" stroke-opacity="0.75" d="{line[0]}">{anim("d", line, kts)}</path>')

    # ripples spreading from the centre on each hit
    for b in BOOMS:
        for k in range(3):
            start = (b + k * 0.14) / DUR
            end = min(0.999, start + 1.0 / DUR)
            ks = [0, start, end, 1] if start > 0 else [0, end, 1]
            def seq(a, z, idle):
                return [idle, a, z, idle] if start > 0 else [a, z, idle]
            add(f'<ellipse cx="{W / 2}" cy="{Y0 + 8}" fill="none" stroke="{T["blood"]}" stroke-width="1.4">'
                f'{anim("rx", seq("8", str(W * 0.5), "8"), ks)}'
                f'{anim("ry", seq("1", "22", "1"), ks)}'
                f'{anim("opacity", seq("0.8", "0", "0"), ks)}</ellipse>')
    add('</g>')

    # droplets
    for b in BOOMS:
        for i in range(30):
            x0 = rng.choice(CROWNS) + rng.uniform(-14, 14) if rng.random() < 0.7 else rng.uniform(150, 850)
            centre = 1 - abs(x0 - W / 2) / (W * 0.62)
            h = rng.uniform(25, 125) * centre
            vy = math.sqrt(2 * G * h)
            flight = 2 * vy / G
            vx = rng.uniform(-60, 60)
            t0 = b + rng.uniform(0.0, 0.07)
            r = rng.uniform(1.8, 5.2)
            n = 10
            times = [t0 + flight * j / n for j in range(n + 1)]
            pos = [(vx * (tt - t0), -(vy * (tt - t0) - G * (tt - t0) ** 2 / 2)) for tt in times]
            ks = [0] + [tt / DUR for tt in times] + [1]
            tr = [f"0,0"] + [f"{px:.1f},{py:.1f}" for px, py in pos] + ["0,0"]
            op = ["0"] + ["1"] * n + ["0", "0"]
            add(f'<g transform="translate({x0:.1f},{Y0 - 2})"><g>'
                f'<animateTransform attributeName="transform" type="translate" dur="{DUR}s" repeatCount="indefinite" '
                f'values="{fmt(tr)}" keyTimes="{";".join(f"{k:.4f}" for k in ks)}"/>'
                f'<ellipse rx="{r:.1f}" ry="{r * 1.25:.1f}" fill="url(#drop)">{anim("opacity", op, ks, calc="discrete")}</ellipse>'
                f'</g></g>')
            # splash where it lands
            land_x = x0 + vx * flight
            ts, te = (t0 + flight) / DUR, min(0.999, (t0 + flight + 0.28) / DUR)
            add(f'<ellipse cx="{land_x:.1f}" cy="{Y0}" fill="none" stroke="{T["blood"]}" stroke-width="1.2">'
                f'{anim("rx", ["0", "0", f"{r * 4:.1f}", "0"], [0, ts, te, 1])}'
                f'{anim("ry", ["0", "0", f"{r * 1.1:.1f}", "0"], [0, ts, te, 1])}'
                f'{anim("opacity", ["0", "0.9", "0", "0"], [0, ts, te, 1])}</ellipse>')
    add("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "blood-pool.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build())
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
