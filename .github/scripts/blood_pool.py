"""Blood pool footer: a pool of blood on a subwoofer. Every bass hit makes the
surface spike, droplets burst up and fall back with splashes, and ripples spread
out from the centre. Pure SVG + CSS keyframes (no SMIL/JS) so it animates inside a GitHub README <img>.

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


def pct(t):
    return f"{100 * t / DUR:.2f}%"


def build():
    css, body = [], []
    add = body.append
    defs = f"""<defs>
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
</defs>"""
    css.append(f".a{{animation-duration:{DUR}s;animation-iteration-count:infinite}}"
               ".c{transform-box:fill-box;transform-origin:center}")

    # glow pulsing with the bass
    steps = [i * DUR / 24 for i in range(25)]
    css.append("@keyframes glow{" + "".join(
        f"{pct(t)}{{opacity:{0.25 + 0.75 * math.exp(-since_boom(t) * 4):.2f}}}" for t in steps) + "}")
    add(f'<ellipse class="a" style="animation-name:glow" cx="{W / 2}" cy="{Y0}" rx="{W * 0.55}" ry="70" fill="url(#glow)"/>')

    # surface flipbook: one path per frame, each visible only in its own slot
    n = 48
    add('<g mask="url(#fade)">')
    for i in range(n):
        t = i * DUR / n
        a, b = 100 * i / n, 100 * (i + 1) / n
        kf = f"0%,{a:.3f}%{{opacity:0}}" if i else ""
        kf += f"{a:.3f}%,{b - 0.001:.3f}%{{opacity:1}}{b:.3f}%,100%{{opacity:0}}"
        css.append(f"@keyframes s{i}{{{kf}}}")
        add(f'<g class="a" style="animation-name:s{i};animation-timing-function:step-end" opacity="{1 if i == 0 else 0}">'
            f'<path fill="url(#pool)" d="{surface_path(t, True)}"/>'
            f'<path fill="none" stroke="{T["accent"]}" stroke-width="1.6" stroke-opacity="0.75" d="{surface_path(t, False)}"/></g>')

    # ripples spreading from the centre on each hit
    for bi, b in enumerate(BOOMS):
        for k in range(3):
            t0 = b + k * 0.14
            t1 = t0 + 1.0
            name = f"r{bi}{k}"
            css.append(f"@keyframes {name}{{0%{{transform:scale(0.02);opacity:0}}"
                       f"{pct(t0)}{{transform:scale(0.02);opacity:0.8}}{pct(t1)}{{transform:scale(1);opacity:0}}"
                       f"{pct(min(t1 + 0.01, DUR))},100%{{transform:scale(1);opacity:0}}}}")
            add(f'<ellipse class="a c" style="animation-name:{name};animation-timing-function:linear" opacity="0" '
                f'cx="{W / 2}" cy="{Y0 + 8}" rx="{W * 0.5}" ry="22" fill="none" stroke="{T["blood"]}" stroke-width="1.4" vector-effect="non-scaling-stroke"/>')
    add('</g>')

    # droplets + splashes
    d = 0
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
            name = f"d{d}"
            frames = [f"0%,{pct(max(0, t0 - 0.001))}{{transform:translate(0px,0px);opacity:0}}"]
            for j in range(11):
                tt = flight * j / 10
                x, y = vx * tt, -(vy * tt - G * tt * tt / 2)
                frames.append(f"{pct(t0 + tt)}{{transform:translate({x:.1f}px,{y:.1f}px);opacity:1}}")
            frames.append(f"{pct(min(t0 + flight + 0.001, DUR))},100%{{transform:translate({vx * flight:.1f}px,0px);opacity:0}}")
            css.append(f"@keyframes {name}{{{''.join(frames)}}}")
            add(f'<g transform="translate({x0:.1f},{Y0 - 2})"><ellipse class="a" style="animation-name:{name};animation-timing-function:linear" '
                f'opacity="0" rx="{r:.1f}" ry="{r * 1.25:.1f}" fill="url(#drop)"/></g>')
            # splash ring where it lands
            ts, te = t0 + flight, min(t0 + flight + 0.28, DUR - 0.001)
            css.append(f"@keyframes p{d}{{0%,{pct(ts)}{{transform:scale(0.05);opacity:0}}{pct(ts + 0.001)}{{transform:scale(0.05);opacity:0.9}}"
                       f"{pct(te)}{{transform:scale(1);opacity:0}}100%{{transform:scale(1);opacity:0}}}}")
            add(f'<ellipse class="a c" style="animation-name:p{d};animation-timing-function:ease-out" opacity="0" '
                f'cx="{x0 + vx * flight:.1f}" cy="{Y0}" rx="{r * 4:.1f}" ry="{r * 1.1:.1f}" fill="none" stroke="{T["blood"]}" stroke-width="1.2" vector-effect="non-scaling-stroke"/>')
            d += 1

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'{defs}\n<style>{"".join(css)}</style>\n' + "\n".join(body) + "\n</svg>")


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "blood-pool.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build())
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
