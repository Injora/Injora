"""Cinematic blood header. Usage: python blood_header.py assets/blood-header.svg"""
import random, sys
random.seed(11)
W, H, EDGE = 1000, 290, 176

# ── organic bottom edge: smoothed irregular wave ──
pts, x = [], 0
while x < W:
    pts.append((x, EDGE + random.uniform(-4, 5))); x += random.uniform(18, 34)
pts.append((W, EDGE))
d = f"M0,0 H{W} V{EDGE} L{pts[-1][0]},{pts[-1][1]:.1f}"
rev = list(reversed(pts))
for (x0, y0), (x1, y1) in zip(rev, rev[1:]):
    d += f" Q{x0:.1f},{y0:.1f} {(x0+x1)/2:.1f},{(y0+y1)/2:.1f}"
d += f" L0,{pts[0][1]:.1f} Z"
banner = d

def drip(cx, h, w, r):
    y = EDGE - 3
    return (f"M{cx-w:.1f},{y} C{cx-w*0.25:.1f},{y+h*0.35:.1f} {cx-r:.1f},{y+h-r*2.6:.1f} {cx-r:.1f},{y+h-r:.1f} "
            f"A{r:.1f},{r:.1f} 0 0 0 {cx+r:.1f},{y+h-r:.1f} "
            f"C{cx+r:.1f},{y+h-r*2.6:.1f} {cx+w*0.25:.1f},{y+h*0.35:.1f} {cx+w:.1f},{y} Z")

# static drips: mostly short, a few long
drips = ""
for _ in range(22):
    cx = random.uniform(15, 985)
    h = random.choice([random.uniform(8, 18)] * 3 + [random.uniform(26, 58)])
    w = random.uniform(7, 16); r = min(w * 0.42, random.uniform(2.6, 4.6))
    drips += f'<path d="{drip(cx, h, w, r)}"/>'

# slow animated drips: stretch, release a drop, recover
live = ""
for i, cx in enumerate([142, 388, 611, 857]):
    dur = random.uniform(8, 11); dl = -random.uniform(0, dur)
    st = f"animation-duration:{dur:.1f}s;animation-delay:{dl:.1f}s"
    live += (f'<rect class="lv" x="{cx-3:.0f}" y="{EDGE-4}" width="6" height="40" rx="3" style="{st}"/>'
             f'<ellipse class="dr" cx="{cx}" cy="{EDGE+38}" rx="3.6" ry="4.6" style="{st}"/>')

# binary rain: three depth layers
layers = [  # count, size, colour, opacity, speed range, spacing
    (30, 10, "#5E0B18", 0.55, (7.0, 10.0), 12),
    (22, 13, "#9A1024", 0.75, (4.8, 6.8), 15),
    (12, 16, "#E21D35", 0.95, (3.4, 4.6), 18),
]
def column(cx, size, colour, op, spd, gap, y0, travel):
    n = random.randint(5, 9)
    dur = random.uniform(*spd); dl = -random.uniform(0, dur)
    spans = "".join(
        f'<tspan x="{cx:.1f}" dy="{0 if k == 0 else gap}" fill-opacity="{(1 if k == n-1 else 0.85*(k+1)/n):.2f}">{random.choice("01")}</tspan>'
        for k in range(n))
    return (f'<text class="bn" y="{y0}" font-size="{size}" fill="{colour}" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:{dl:.2f}s;--t:{travel}px">{spans}</text>')
rain = ""
for cnt, size, colour, op, spd, gap in layers:
    rain += f'<g opacity="{op}">'
    for i in range(cnt):
        cx = (i + random.uniform(0.15, 0.85)) * W / cnt
        rain += column(cx, size, colour, op, spd, gap, EDGE - 110, 230)
    rain += '</g>'
# very faint rain inside the banner, behind the title
ghost = ""
for i in range(26):
    cx = (i + random.uniform(0.2, 0.8)) * W / 26
    ghost += column(cx, 11, "#FF4157", 1, (9, 14), 13, -120, 300)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ttl dsc">
<title id="ttl">INJORA, Full-Stack Shinigami</title>
<desc id="dsc">A deep crimson banner with a metallic INJORA title, its lower edge dripping blood while red binary digits fall below it.</desc>
<defs>
  <linearGradient id="base" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5A0914"/><stop offset=".45" stop-color="#7E0E1F"/>
    <stop offset=".85" stop-color="#5E0B18"/><stop offset="1" stop-color="#3A0610"/>
  </linearGradient>
  <linearGradient id="vignette" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#050507" stop-opacity=".75"/><stop offset=".22" stop-color="#050507" stop-opacity="0"/>
    <stop offset=".78" stop-color="#050507" stop-opacity="0"/><stop offset="1" stop-color="#050507" stop-opacity=".75"/>
  </linearGradient>
  <radialGradient id="light" cx=".5" cy=".42" r=".5">
    <stop offset="0" stop-color="#C8142E" stop-opacity=".55"/><stop offset="1" stop-color="#C8142E" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="dripfill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3A0610"/><stop offset=".6" stop-color="#5E0B18"/><stop offset="1" stop-color="#8A0F20"/>
  </linearGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFFFFF"/><stop offset=".46" stop-color="#E9E6EC"/>
    <stop offset=".54" stop-color="#ABA6B0"/><stop offset="1" stop-color="#F2F0F4"/>
  </linearGradient>
  <linearGradient id="fadeLow" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="rainMask"><rect y="{EDGE-6}" width="{W}" height="{H-EDGE+6}" fill="url(#fadeLow)"/></mask>
  <clipPath id="bannerClip"><path d="{banner}"/></clipPath>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".9 .35" numOctaves="2" seed="4"/>
    <feColorMatrix values="0 0 0 0 .05  0 0 0 0 0  0 0 0 0 .01  0 0 0 .55 -.18"/>
  </filter>
  <filter id="veins" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="turbulence" baseFrequency=".012 .03" numOctaves="3" seed="9"/>
    <feColorMatrix values="0 0 0 0 .02  0 0 0 0 0  0 0 0 0 .01  0 0 0 -1.6 1.05"/>
  </filter>
  <filter id="shade" x="-5%" y="-5%" width="110%" height="130%">
    <feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#000" flood-opacity=".7"/>
  </filter>
  <filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
    <feGaussianBlur stdDeviation="9"/>
  </filter>
</defs>
<style>
  .bn{{font-family:'SF Mono',Menlo,Consolas,'Courier New',monospace;font-weight:700;text-anchor:middle;
      animation:fall linear infinite}}
  @keyframes fall{{0%{{transform:translateY(0);opacity:0}}12%{{opacity:1}}85%{{opacity:1}}100%{{transform:translateY(var(--t));opacity:0}}}}
  .lv{{fill:url(#dripfill);transform-box:fill-box;transform-origin:top;animation:stretch ease-in-out infinite}}
  .dr{{fill:#8A0F20;animation:drop ease-in infinite}}
  @keyframes stretch{{0%{{transform:scaleY(.12)}}70%{{transform:scaleY(1)}}74%{{transform:scaleY(.55)}}100%{{transform:scaleY(.12)}}}}
  @keyframes drop{{0%,69%{{transform:translateY(0);opacity:0}}71%{{opacity:1}}100%{{transform:translateY(110px);opacity:0}}}}
  .pulse{{animation:pulse 6s ease-in-out infinite}}
  @keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:.8}}}}
  .drift{{animation:drift 18s ease-in-out infinite alternate}}
  @keyframes drift{{from{{transform:translateX(-120px)}}to{{transform:translateX(120px)}}}}
  .title{{font-family:'Helvetica Neue','Arial Black',Arial,sans-serif;font-weight:900;font-size:92px;letter-spacing:18px}}
  .sub{{font-family:'Helvetica Neue',Arial,sans-serif;font-weight:500;font-size:17px;letter-spacing:7px}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>

<rect width="{W}" height="{H}" fill="#050507"/>

<!-- rain below the banner -->
<g mask="url(#rainMask)">{rain}</g>

<!-- banner: gradient, drifting light, ghost rain, texture, vignette -->
<g filter="url(#shade)">
  <path d="{banner}" fill="url(#base)"/>
  <g fill="url(#dripfill)">{drips}</g>
</g>
<g clip-path="url(#bannerClip)">
  <ellipse class="drift" cx="500" cy="80" rx="420" ry="150" fill="url(#light)"/>
  <g opacity=".08">{ghost}</g>
  <rect width="{W}" height="{EDGE+8}" filter="url(#veins)" opacity=".35"/>
  <rect width="{W}" height="{EDGE+8}" filter="url(#grain)" opacity=".5"/>
  <rect width="{W}" height="{EDGE+8}" fill="url(#vignette)"/>
  <rect width="{W}" height="1.2" fill="#FF4157" opacity=".35"/>
</g>
{live}

<!-- title -->
<text class="title pulse" x="{W/2 + 9}" y="104" text-anchor="middle" fill="#E21D35" filter="url(#glow)">INJORA</text>
<text class="title" x="{W/2 + 9}" y="104" text-anchor="middle" fill="url(#metal)" stroke="#B5122A" stroke-width="1.1" paint-order="stroke">INJORA</text>
<text class="sub" x="{W/2 + 3.5}" y="140" text-anchor="middle" fill="#E7C9CE">Full-Stack Shinigami</text>
</svg>'''
open(sys.argv[1], "w").write(svg)
