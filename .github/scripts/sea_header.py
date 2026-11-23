"""Night-sea header: moonlit sky, an original pirate ship riding looping waves,
a gold INJORA title. Pure SVG + CSS keyframes so it animates inside a README <img>.

Usage: python sea_header.py assets/sea-header.svg
"""
import json, math, random, sys
from pathlib import Path

T = json.loads((Path(__file__).resolve().parent.parent / "theme.json").read_text())
random.seed(11)
W, H = 1000, 300
SLAB = "Rockwell,'Roboto Slab',Clarendon,Georgia,serif"


def wave(y, amp, length, phase=0.0, bottom=H):
    """Smooth sine band two screens wide; translating it by `length` loops seamlessly."""
    step = length / 8
    pts = [(x * step - length, y + amp * math.sin(2 * math.pi * x / 8 + phase)) for x in range(int((2 * W + 2 * length) / step) + 1)]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d += f" Q{x0:.1f},{y0:.1f} {(x0+x1)/2:.1f},{(y0+y1)/2:.1f}"
    crest = d
    return crest, d + f" L{pts[-1][0]:.1f},{bottom} L{pts[0][0]:.1f},{bottom} Z"


# sea layers: back to front (y, amplitude, wavelength, speed s, fill, crest colour, crest opacity)
LAYERS = [
    (206, 3, 120, 14, "#0B2E48", T["seaHi"], .35),
    (222, 4, 160, 10, "#0A2A42", T["seaHi"], .45),
    (244, 6, 210, 7, "#07223A", T["foam"], .55),
    (268, 7, 260, 5, "#051A2D", T["foam"], .8),
]
sea = ""
for i, (y, a, L, s, fill, crest, op) in enumerate(LAYERS):
    c, band = wave(y, a, L, phase=i)
    sea += (f'<g class="wv" style="--l:-{L}px;animation-duration:{s}s"><path d="{band}" fill="{fill}"/>'
            f'<path d="{c}" fill="none" stroke="{crest}" stroke-opacity="{op}" stroke-width="1.4"/></g>')
    if i == 1:
        SHIP_AT = len(sea)  # ship rides between layer 2 and 3

stars = ""
for _ in range(70):
    x, y = random.uniform(0, W), random.uniform(4, 190)
    r = random.choice([.6, .8, .8, 1.1, 1.5])
    dur, dl = random.uniform(2.5, 6), random.uniform(0, 6)
    stars += f'<circle class="tw" cx="{x:.0f}" cy="{y:.0f}" r="{r}" style="animation-duration:{dur:.1f}s;animation-delay:-{dl:.1f}s"/>'

# moon glitter on the water: short dashes that flicker
glitter = ""
for _ in range(34):
    x = 170 + random.gauss(0, 36); y = random.uniform(208, 290)
    w = random.uniform(6, 22) * (1 - (290 - y) / 160)
    glitter += (f'<rect class="tw" x="{x - w/2:.0f}" y="{y:.0f}" width="{w:.0f}" height="1.6" rx=".8" '
                f'style="animation-duration:{random.uniform(1.2, 3):.1f}s;animation-delay:-{random.uniform(0, 3):.1f}s"/>')

gulls = "".join(
    f'<path class="gull" d="M0,0 q5,-5 10,0 q5,-5 10,0" style="animation-duration:{d}s;animation-delay:-{dl}s;--y:{y}px"/>'
    for d, dl, y in ((26, 3, 58), (34, 15, 84), (30, 24, 40)))

# original brigantine, ~190 wide, bow to the right; origin at the waterline centre
SHIP = f'''<g class="bob">
  <g class="hull">
    <path d="M-92,-30 L-70,-30 L-70,-20 L88,-24 L104,-34 L98,-20 L70,6 Q0,14 -70,8 Z" fill="#1B1210"/>
    <path d="M-70,-20 L88,-24 L84,-17 L-72,-13 Z" fill="{T['gold']}" opacity=".85"/>
    <path d="M-70,-6 L76,-9 L70,6 Q0,14 -70,8 Z" fill="#120B0A"/>
    {''.join(f'<rect x="{x}" y="-10" width="7" height="5" fill="{T["goldLo"]}"/>' for x in (-48, -24, 0, 24, 48))}
    <circle cx="-84" cy="-24" r="3" fill="{T['goldHi']}"/><circle class="lamp" cx="-84" cy="-24" r="14" fill="url(#lamp)"/>
  </g>
  <path d="M-20,-22 V-150 M40,-24 V-128 M88,-28 L132,-48" stroke="#2A1A12" stroke-width="4" fill="none"/>
  <g class="sail">
    <path d="M-62,-140 Q-20,-148 22,-140 Q34,-100 22,-50 Q-20,-44 -62,-50 Q-50,-95 -62,-140Z" fill="url(#sail)"/>
    <path d="M6,-118 Q40,-124 74,-118 Q84,-88 74,-56 Q40,-52 6,-56 Q14,-88 6,-118Z" fill="url(#sail)"/>
    <path d="M44,-124 L128,-48 L50,-54 Q60,-90 44,-124Z" fill="url(#sail)" opacity=".9"/>
    <g transform="translate(-20,-96)" fill="#2A1A12">
      <circle r="11"/><rect x="-6" y="6" width="12" height="7" rx="2"/>
      <path d="M-20,-14 L20,18 M20,-14 L-20,18" stroke="#2A1A12" stroke-width="5" stroke-linecap="round"/>
      <circle cx="-4" cy="-1" r="3" fill="{T['parchment']}"/><circle cx="4" cy="-1" r="3" fill="{T['parchment']}"/>
    </g>
  </g>
  <g transform="translate(-18,-150)"><path class="flag" d="M0,0 Q14,-4 28,0 T56,0 V22 Q42,26 28,22 T0,22Z" fill="#0A0A0A" stroke="{T['gold']}" stroke-width=".8"/>
    <g fill="{T['text']}" transform="translate(26,11)"><circle r="5"/><path d="M-9,-6 L9,6 M9,-6 L-9,6" stroke="{T['text']}" stroke-width="2"/></g></g>
</g>'''

sea = sea[:SHIP_AT] + f'<g transform="translate(872,236) scale(.8)">{SHIP}</g>' + sea[SHIP_AT:]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ttl dsc">
<title id="ttl">INJORA, Full-Stack Pirate</title>
<desc id="dsc">A moonlit night sea. A pirate ship bobs on rolling waves while a gold INJORA title shimmers above.</desc>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{T['bgDeep']}"/><stop offset=".6" stop-color="#0A2238"/><stop offset="1" stop-color="#16405F"/>
  </linearGradient>
  <radialGradient id="moonGlow"><stop offset="0" stop-color="{T['goldHi']}" stop-opacity=".35"/><stop offset="1" stop-color="{T['goldHi']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="moon" cx=".4" cy=".35"><stop offset="0" stop-color="#FFF6DA"/><stop offset="1" stop-color="#E9CF8C"/></radialGradient>
  <radialGradient id="lamp"><stop offset="0" stop-color="{T['goldHi']}" stop-opacity=".7"/><stop offset="1" stop-color="{T['goldHi']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="sail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9A27A"/><stop offset="1" stop-color="{T['parchment']}"/></linearGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{T['goldHi']}"/><stop offset=".48" stop-color="{T['gold']}"/>
    <stop offset=".52" stop-color="{T['goldLo']}"/><stop offset="1" stop-color="{T['gold']}"/>
  </linearGradient>
  <linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <clipPath id="titleClip"><text class="title" x="{W/2 + 9}" y="112" text-anchor="middle">INJORA</text></clipPath>
  <filter id="shade"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#000" flood-opacity=".8"/></filter>
</defs>
<style>
  .tw{{fill:#FFF6DA;animation:tw ease-in-out infinite alternate}}
  @keyframes tw{{from{{opacity:.15}}to{{opacity:1}}}}
  .wv{{animation:roll linear infinite}}
  @keyframes roll{{to{{transform:translateX(var(--l))}}}}
  .bob{{animation:bob 5s ease-in-out infinite;transform-box:fill-box;transform-origin:50% 90%}}
  @keyframes bob{{0%,100%{{transform:translateY(0) rotate(-2.5deg)}}50%{{transform:translateY(5px) rotate(2deg)}}}}
  .flag{{animation:flap .9s ease-in-out infinite alternate;transform-origin:0 11px}}
  @keyframes flap{{from{{transform:skewY(-6deg) scaleX(.94)}}to{{transform:skewY(5deg)}}}}
  .lamp{{animation:tw 1.4s ease-in-out infinite alternate}}
  .gull{{fill:none;stroke:{T['text2']};stroke-width:1.6;stroke-linecap:round;animation:fly linear infinite}}
  @keyframes fly{{from{{transform:translate(-40px,var(--y))}}to{{transform:translate(1040px,calc(var(--y) - 30px))}}}}
  .shine{{animation:shine 6s ease-in-out infinite}}
  @keyframes shine{{0%,55%{{transform:translateX(-260px)}}100%{{transform:translateX(1100px)}}}}
  .title{{font-family:{SLAB};font-weight:900;font-size:96px;letter-spacing:16px}}
  .sub{{font-family:{SLAB};font-style:italic;font-size:19px;letter-spacing:3px}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>

<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g>{stars}</g>
<circle cx="170" cy="92" r="110" fill="url(#moonGlow)"/>
<circle cx="170" cy="92" r="42" fill="url(#moon)"/>
<circle cx="156" cy="80" r="7" fill="#D9BE7A" opacity=".5"/><circle cx="186" cy="106" r="5" fill="#D9BE7A" opacity=".45"/>
{gulls}
{sea}
<g opacity=".7">{glitter}</g>

<text class="title" x="{W/2 + 9}" y="112" text-anchor="middle" fill="{T['bgDeep']}" filter="url(#shade)">INJORA</text>
<text class="title" x="{W/2 + 9}" y="112" text-anchor="middle" fill="url(#gold)" stroke="{T['ink']}" stroke-width="1.5" paint-order="stroke">INJORA</text>
<g clip-path="url(#titleClip)"><g transform="skewX(-20)"><rect class="shine" x="0" y="20" width="160" height="110" fill="url(#shine)" opacity=".55"/></g></g>
<text class="sub" x="{W/2 + 3}" y="150" text-anchor="middle" fill="{T['parchment']}">Full-Stack Pirate, sailing for the next island</text>
</svg>'''
Path(sys.argv[1]).write_text(svg)
print(f"wrote {sys.argv[1]} ({len(svg) // 1024} KB)")
