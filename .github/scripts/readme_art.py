"""Static README art in the night-sea header's visual language: section dividers,
wanted-poster project cards, link buttons, the voyage-log timeline and the closing quote.

Usage: python readme_art.py   (writes into assets/)
"""
import json
import math
import random
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent.parent
T = json.loads((ROOT / ".github/theme.json").read_text())
OUT = ROOT / "assets"
SLAB = "Rockwell,'Roboto Slab',Clarendon,Georgia,serif"
SERIF = "Georgia,'Times New Roman',serif"

GOLD = f"""<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{T['goldHi']}"/><stop offset=".48" stop-color="{T['gold']}"/>
  <stop offset=".52" stop-color="{T['goldLo']}"/><stop offset="1" stop-color="{T['gold']}"/></linearGradient>"""

# 48x48 icons for the section dividers
ICONS = {
    "hat": f'''<ellipse cx="24" cy="32" rx="22" ry="6.5" fill="{T['gold']}"/><ellipse cx="24" cy="31" rx="17" ry="4" fill="{T['goldLo']}" opacity=".5"/>
<path d="M11,31 Q11,13 24,13 Q37,13 37,31Z" fill="{T['gold']}"/><path d="M11.4,25 Q24,28.5 36.6,25 L37,31 Q24,34 11,31Z" fill="{T['red']}"/>
<path d="M16,19 Q24,16 32,19 M14,22 Q24,19.5 34,22" stroke="{T['goldLo']}" stroke-width="1" fill="none"/>''',
    "fruit": f'''<circle cx="24" cy="28" r="16" fill="#6E4A9E"/><path d="M14,24 q4,-6 8,0 t8,0 t6,-2 M12,31 q4,-6 8,0 t8,0 t8,0 M16,38 q4,-5 8,0 t8,0" stroke="#C7A9EC" stroke-width="2" fill="none" stroke-linecap="round"/>
<path d="M24,12 q1,-5 5,-7" stroke="{T['goldLo']}" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M27,8 q8,-5 12,2 q-7,3 -12,-2z" fill="#5E9B5A"/>''',
    "map": f'''<path d="M5,10 L17,6 L31,10 L43,6 V38 L31,42 L17,38 L5,42Z" fill="{T['parchment']}"/><path d="M17,6 V38 M31,10 V42" stroke="{T['parchmentDark']}" stroke-width="1.2"/>
<path d="M10,34 Q16,22 23,27 T35,16" stroke="{T['red']}" stroke-width="1.8" stroke-dasharray="2.5 2.5" fill="none"/><path d="M33,11 l6,6 M39,11 l-6,6" stroke="{T['red']}" stroke-width="2.4" stroke-linecap="round"/>''',
    "poster": f'''<rect x="9" y="4" width="30" height="40" rx="1.5" fill="{T['parchment']}"/><rect x="14" y="13" width="20" height="16" fill="{T['parchmentDark']}"/>
<path d="M13,9.5 H35 M15,33 H33 M17,38 H31" stroke="{T['ink']}" stroke-width="2"/><circle cx="24" cy="4.5" r="2.2" fill="{T['red']}"/>''',
    "logpose": f'''<rect x="12" y="38" width="24" height="7" rx="2" fill="{T['goldLo']}"/><path d="M14,38 Q8,24 14,12 Q24,0 34,12 Q40,24 34,38Z" fill="{T['seaHi']}" opacity=".35" stroke="{T['foam']}" stroke-width="1.4"/>
<circle cx="24" cy="25" r="9" fill="none" stroke="{T['gold']}" stroke-width="1.6"/><path d="M24,14 L27,25 L24,36 L21,25Z" fill="{T['red']}"/><path d="M24,25 L27,25 L24,36 L21,25Z" fill="{T['foam']}"/>''',
    "cannon": f'''<path d="M6,26 L36,14 L40,22 L10,34Z" fill="#2B2B33" stroke="{T['gold']}" stroke-width="1.2"/><rect x="36" y="12" width="6" height="12" rx="2" transform="rotate(-22 39 18)" fill="#2B2B33" stroke="{T['gold']}" stroke-width="1.2"/>
<circle cx="16" cy="36" r="7" fill="{T['ink']}" stroke="{T['gold']}" stroke-width="1.6"/><circle cx="16" cy="36" r="2" fill="{T['gold']}"/><circle cx="45" cy="9" r="2.5" fill="{T['goldHi']}"/>''',
}


def icon(name, x, y, h):
    return f'<svg x="{x}" y="{y}" width="{h}" height="{h}" viewBox="0 0 48 48">{ICONS[name]}</svg>'


def save(name, svg):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


def rope(x0, x1, y, grad):
    """Two offset dashed strokes read as twisted rope."""
    return (f'<path d="M{x0:.1f},{y} H{x1:.1f}" stroke="url(#{grad})" stroke-width="3" stroke-dasharray="5 2"/>'
            f'<path d="M{x0:.1f},{y} H{x1:.1f}" stroke="{T["bgDeep"]}" stroke-opacity=".55" stroke-width="1" stroke-dasharray="1.5 5.5" stroke-dashoffset="-3"/>')


# ── section dividers ────────────────────────────────────────────────
def section(slug, title, icon_name):
    W, H, cy = 1000, 92, 40
    tw = len(title) * 18.5
    iw = 48
    gw = iw + 14 + tw
    x0 = W / 2 - gw / 2
    lx, rx = x0 - 34, x0 + gw + 34
    tx = x0 + iw + 14
    squiggle = "".join(f"q{5},{-4 if k % 2 else 4} 10,0 " for k in range(int(tw / 10)))
    save(f"sections/{slug}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
<defs>{GOLD}
  <linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{T['goldLo']}" stop-opacity="0"/><stop offset="1" stop-color="{T['gold']}"/></linearGradient>
  <linearGradient id="r" x1="1" x2="0"><stop offset="0" stop-color="{T['goldLo']}" stop-opacity="0"/><stop offset="1" stop-color="{T['gold']}"/></linearGradient>
</defs>
{rope(60, lx, cy, "l")}{rope(rx, W - 60, cy, "r")}
<circle cx="{lx + 4:.1f}" cy="{cy}" r="4" fill="none" stroke="{T['gold']}" stroke-width="2"/><circle cx="{rx - 4:.1f}" cy="{cy}" r="4" fill="none" stroke="{T['gold']}" stroke-width="2"/>
{icon(icon_name, round(x0), cy - 26, iw)}
<text x="{tx:.1f}" y="{cy + 11}" font-family="{SLAB}" font-weight="900" font-size="30" letter-spacing="1" fill="url(#gold)" stroke="{T['ink']}" stroke-width=".8" paint-order="stroke">{escape(title)}</text>
<path d="M{tx:.1f},{cy + 24} {squiggle}" fill="none" stroke="{T['seaHi']}" stroke-width="1.6" stroke-linecap="round"/>
</svg>''')


# ── project cards: wanted posters ───────────────────────────────────
PICTOS = {  # drawn in ink inside a 150x164 photo frame
    "compass": f'''<circle cx="75" cy="82" r="46" fill="none" stroke="{T['ink']}" stroke-width="3"/><circle cx="75" cy="82" r="38" fill="none" stroke="{T['ink']}" stroke-width="1" stroke-dasharray="2 4"/>
<path d="M75,30 L84,82 L75,134 L66,82Z" fill="{T['ink']}"/><path d="M23,82 L75,73 L127,82 L75,91Z" fill="{T['ink']}" opacity=".7"/><path d="M75,30 L84,82 L66,82Z" fill="{T['red']}"/>
<text x="75" y="24" text-anchor="middle" font-family="{SLAB}" font-weight="900" font-size="15" fill="{T['ink']}">N</text>''',
    "shuttle": f'''<rect x="30" y="38" width="90" height="86" rx="12" fill="{T['ink']}"/><rect x="38" y="48" width="74" height="34" rx="4" fill="{T['parchment']}" opacity=".85"/>
<circle cx="47" cy="102" r="7" fill="{T['goldHi']}"/><circle cx="103" cy="102" r="7" fill="{T['goldHi']}"/><rect x="62" y="96" width="26" height="10" rx="2" fill="{T['parchmentDark']}"/>
<rect x="36" y="124" width="16" height="12" rx="3" fill="{T['ink']}"/><rect x="98" y="124" width="16" height="12" rx="3" fill="{T['ink']}"/><path d="M50,30 H100" stroke="{T['ink']}" stroke-width="5" stroke-linecap="round"/>''',
    "funds": "".join(f'<ellipse cx="{x}" cy="{y}" rx="26" ry="8" fill="{T["ink"]}" stroke="{T["parchment"]}" stroke-width="1.5"/>'
                     for x, ys in ((46, (128, 120, 112, 104)), (100, (128, 120, 112, 104, 96, 88, 80))) for y in ys)
             + f'''<circle cx="74" cy="56" r="28" fill="{T['goldHi']}" stroke="{T['ink']}" stroke-width="3"/>
<text x="74" y="67" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="32" fill="{T['ink']}">฿</text>''',
    "arena": f'''<g stroke="{T['ink']}" stroke-linecap="round"><path d="M34,128 L114,40" stroke-width="7"/><path d="M116,128 L36,40" stroke-width="7"/>
<path d="M36,108 L52,124 M114,108 L98,124" stroke-width="6"/></g><path d="M114,40 L121,28 L108,35Z M36,40 L29,28 L42,35Z" fill="{T['ink']}"/>
<circle cx="75" cy="84" r="9" fill="{T['red']}" stroke="{T['ink']}" stroke-width="2"/>''',
}


def card(slug, title, bounty, body, tags, seed):
    rng = random.Random(seed)
    W, H = 500, 300
    # slightly torn outline
    pts = []
    for (ax, ay), (bx, by) in (((4, 4), (W - 4, 4)), ((W - 4, 4), (W - 4, H - 4)), ((W - 4, H - 4), (4, H - 4)), ((4, H - 4), (4, 4))):
        n = 14
        for k in range(n):
            t = k / n
            pts.append((ax + (bx - ax) * t + rng.uniform(-2, 2), ay + (by - ay) * t + rng.uniform(-2, 2)))
    edge = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"
    lines = textwrap.wrap(body, 38)
    text = "".join(f'<tspan x="196" dy="{0 if i == 0 else 19}">{escape(l)}</tspan>' for i, l in enumerate(lines))
    pills, px = "", 24
    for t in tags:
        w = len(t) * 7.4 + 20
        pills += (f'<rect x="{px:.1f}" y="244" width="{w:.1f}" height="26" rx="13" fill="none" stroke="{T["ink"]}" stroke-width="1.3"/>'
                  f'<text x="{px + w/2:.1f}" y="261.5" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="13" fill="{T["ink"]}">{escape(t)}</text>')
        px += w + 8
    save(f"cards/{slug}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Wanted: {escape(title)}, bounty {bounty} berries. {escape(body)}">
<defs>
  <radialGradient id="burn" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="{T['parchment']}"/><stop offset=".9" stop-color="{T['parchmentDark']}"/><stop offset="1" stop-color="#7A5530"/></radialGradient>
  <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="{seed}"/>
    <feColorMatrix values="0 0 0 0 .23  0 0 0 0 .14  0 0 0 0 .07  0 0 0 .5 -.12"/></filter>
  <clipPath id="c"><path d="{edge}"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#burn)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)"/>
</g>
<rect x="24" y="24" width="150" height="164" fill="#D9BE88" stroke="{T['ink']}" stroke-width="2.5"/>
<g transform="translate(24,24)">{PICTOS[slug]}</g>
<text x="99" y="214" text-anchor="middle" font-family="{SLAB}" font-weight="900" font-size="15" letter-spacing="2" fill="{T['ink']}">DEAD OR ALIVE</text>
<text x="196" y="66" font-family="{SLAB}" font-weight="900" font-size="50" letter-spacing="5" fill="{T['ink']}">WANTED</text>
<text x="196" y="100" font-family="{SLAB}" font-weight="700" font-size="22" fill="{T['ink']}">{escape(title)}</text>
<text x="196" y="134" font-family="{SLAB}" font-weight="900" font-size="24" fill="{T['red']}">฿ {bounty}-</text>
<text y="166" font-family="{SERIF}" font-size="14.5" fill="{T['ink']}">{text}</text>
{pills}
<circle cx="250" cy="12" r="5" fill="{T['red']}" stroke="#5A1A14" stroke-width="1.5"/>
</svg>''')


# ── link buttons ────────────────────────────────────────────────────
def button(slug, label):
    W, H = 200, 50
    save(f"buttons/{slug}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<defs>{GOLD}
  <linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6B4628"/><stop offset="1" stop-color="#3A2414"/></linearGradient></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="6" fill="url(#wood)" stroke="{T['gold']}" stroke-width="1.4"/>
<path d="M10,17 H{W-10} M10,33 H{W-10}" stroke="#2A190E" stroke-opacity=".5"/>
<circle cx="12" cy="25" r="2.6" fill="{T['gold']}"/><circle cx="{W-12}" cy="25" r="2.6" fill="{T['gold']}"/>
<text x="{W/2}" y="31.5" text-anchor="middle" font-family="{SLAB}" font-weight="900" font-size="18" letter-spacing="1" fill="url(#gold)">{label}</text>
</svg>''')


# ── voyage log: animated timeline from the portfolio's journey ──────
def voyage(stops):
    W, H, DUR = 1000, 330, 22.0
    n = len(stops)
    pts = [(70 + i * (860 / (n - 1)), 120 if i % 2 == 0 else 212) for i in range(n)]
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    # timeline: sail each leg, hold 0.5 s at each island, rest at the end
    hold, sail = 0.5, DUR - 0.5 * (n - 1) - 3.0
    t, keys, arrive = 0.0, [], [0.0]
    for i, (p, L) in enumerate(zip(pts, [0] + seg)):
        t += sail * L / total
        if i:
            arrive.append(t)
        done = sum(seg[:i])
        ang = math.degrees(math.atan2(pts[min(i + 1, n - 1)][1] - p[1], 120)) * .6 if i < n - 1 else 0
        keys.append((t, p, done, ang))
        t += hold
        keys.append((t, p, done, ang))
    pct = lambda s: f"{100 * min(s, DUR) / DUR:.2f}%"
    ship_kf = "".join(f"{pct(s)}{{transform:translate({x:.1f}px,{y:.1f}px) rotate({a:.1f}deg)}}" for s, (x, y), _, a in keys)
    trail_kf = "".join(f"{pct(s)}{{stroke-dashoffset:{total - d:.1f}}}" for s, _, d, _ in keys)
    route = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    css = (f"@keyframes ship{{{ship_kf}96%{{opacity:1}}100%{{transform:translate({pts[-1][0]:.1f}px,{pts[-1][1]:.1f}px);opacity:0}}}}"
           f"@keyframes trail{{{trail_kf}96%{{opacity:1}}100%{{stroke-dashoffset:0;opacity:0}}}}"
           f".ship{{animation:ship {DUR}s linear infinite}}.trail{{stroke-dasharray:{total:.1f};animation:trail {DUR}s linear infinite}}"
           ".bob{animation:bob 1.6s ease-in-out infinite alternate}@keyframes bob{to{transform:translateY(-3px)}}"
           ".ring{transform-box:fill-box;transform-origin:center;opacity:0}"
           ".x{animation:glow 1.8s ease-in-out infinite alternate}@keyframes glow{from{opacity:.45}to{opacity:1}}"
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}.ring{opacity:0}}")
    body = ""
    for i, ((x, y), (date, label), ta) in enumerate(zip(pts, stops, arrive)):
        a0 = 100 * ta / DUR
        css += (f"@keyframes r{i}{{0%,{a0:.2f}%{{opacity:0;transform:scale(.3)}}{a0 + .3:.2f}%{{opacity:.9}}"
                f"{a0 + 6:.2f}%,100%{{opacity:0;transform:scale(2.2)}}}}")
        body += f'<ellipse class="ring" style="animation:r{i} {DUR}s linear infinite" cx="{x:.1f}" cy="{y + 3}" rx="16" ry="7" fill="none" stroke="{T["goldHi"]}" stroke-width="1.5"/>'
        if i == n - 1:
            body += (f'<circle cx="{x:.1f}" cy="{y}" r="17" fill="none" stroke="{T["gold"]}" stroke-width="1.2" stroke-dasharray="3 4"/>'
                     f'<path class="x" d="M{x-7:.1f},{y-7} l14,14 M{x+7:.1f},{y-7} l-14,14" stroke="{T["red"]}" stroke-width="4" stroke-linecap="round"/>')
        else:
            body += (f'<ellipse cx="{x:.1f}" cy="{y + 3}" rx="15" ry="6" fill="#C9A86A"/>'
                     f'<path d="M{x-10:.1f},{y + 2} Q{x-3:.1f},{y - 9} {x + 4:.1f},{y - 3} Q{x + 9:.1f},{y - 7} {x + 11:.1f},{y + 2}Z" fill="#3F6B4A"/>')
        above = i % 2 == 0
        dy, ly = (-52, -35) if above else (34, 51)
        col = T["gold"] if i < n - 1 else T["goldHi"]
        body += (f'<text x="{x:.1f}" y="{y + dy}" text-anchor="middle" font-family="{SLAB}" font-weight="700" font-size="13" fill="{col}">{escape(date)}</text>'
                 f'<text x="{x:.1f}" y="{y + ly}" text-anchor="middle" font-family="{SERIF}" font-size="13.5" fill="{T["text"]}">{escape(label)}</text>')
    grid = "".join(f'<path d="M{gx},18 V{H-18}" />' for gx in range(100, W, 100)) + "".join(f'<path d="M18,{gy} H{W-18}" />' for gy in range(70, H, 80))
    rose = "".join(f'<path d="M0,-34 L5,0 L0,34 L-5,0Z" transform="rotate({a})"/>' for a in (0, 90)) + \
           "".join(f'<path d="M0,-24 L3,0 L0,24 L-3,0Z" transform="rotate({a})"/>' for a in (45, 135))
    ship = (f'<path d="M-14,0 L14,0 L9,7 L-10,7Z" fill="{T["ink"]}" stroke="{T["gold"]}" stroke-width="1"/>'
            f'<path d="M-1,-1 V-22" stroke="{T["parchment"]}" stroke-width="1.4"/><path d="M0,-21 Q11,-13 0,-3Z M-2,-19 Q-11,-12 -2,-4Z" fill="{T["parchment"]}"/>'
            f'<path d="M-1,-22 h7 l-2,2 l2,2 h-7Z" fill="{T["red"]}"/>')
    save("voyage.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Voyage log: {escape('; '.join(f'{d}, {l}' for d, l in stops))}">
<style>{css}</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{T['panel']}" stroke="{T['border']}"/>
<g stroke="{T['grid']}" stroke-width="1">{grid}</g>
<g transform="translate(948,56)" fill="{T['border']}" opacity=".8">{rose}<circle r="24" fill="none" stroke="{T['border']}"/></g>
<path d="{route}" fill="none" stroke="{T['muted']}" stroke-width="1.6" stroke-dasharray="4 6"/>
<path class="trail" d="{route}" fill="none" stroke="{T['gold']}" stroke-width="2.4" stroke-linejoin="round"/>
{body}
<g class="ship" style="transform:translate({pts[0][0]}px,{pts[0][1]}px)"><g class="bob"><g transform="translate(0,-6)">{ship}</g></g></g>
</svg>''')


# ── closing quote ───────────────────────────────────────────────────
def quote(text):
    W, H = 1000, 110
    save("quote.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(text)}">
<defs>{GOLD}
  <linearGradient id="b" x1="0" x2="1"><stop offset="0" stop-color="{T['goldLo']}" stop-opacity="0"/><stop offset=".5" stop-color="{T['gold']}"/><stop offset="1" stop-color="{T['goldLo']}" stop-opacity="0"/></linearGradient></defs>
<text x="500" y="52" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="28" fill="{T['parchment']}">{escape(text)}</text>
{rope(250, 750, 78, "b")}
</svg>''')


if __name__ == "__main__":
    section("profile", "Captain's Profile", "hat")
    section("arsenal", "Devil Fruit Arsenal", "fruit")
    section("voyage", "Voyage Log", "map")
    section("bounties", "Bounty Board", "poster")
    section("readings", "Log Pose Readings", "logpose")
    section("blast", "Cannon Blast", "cannon")
    card("compass", "OpenSource Compass", "1,500,000,000",
         "Matches beginners with open-source orgs that actually fit, backed by real GitHub evidence and a 30-day roadmap.",
         ["TypeScript", "Prisma", "PostgreSQL", "GitHub API"], 11)
    card("shuttle", "Shuttle Tracker", "1,200,000,000",
         "Live shuttle tracking for an off-campus hostel network, with geofenced pickups and real-time GPS.",
         ["React Native", "Expo", "Supabase", "PostGIS"], 12)
    card("funds", "NST-Funds", "900,000,000",
         "Fund requests and expense tracking for college clubs: budgets, partial approvals, UPI proofs and settlement.",
         ["Go", "Astro", "TypeScript", "PostgreSQL"], 13)
    card("arena", "Bleach Battle Arena", "2,000,000,000",
         "Two-player drafting and battle simulator on a live API, with screen shakes, dashes and floating damage.",
         ["JavaScript", "HTML", "CSS", "REST API"], 14)
    button("linkedin", "LinkedIn")
    button("portfolio", "Portfolio")
    button("email", "Email")
    voyage([
        ("Jun 2025", "Set sail"), ("Oct 2025", "First contributions"), ("Nov 2025", "Joined NST-SDC"),
        ("Jan 2026", "Established orgs"), ("Mar 2026", "Battle Arena ships"), ("Apr 2026", "First AI build"),
        ("May 2026", "Realtime"), ("Aug 2026", "Systems era"), ("Sep 2026", "Java in production"), ("Next", "AI / ML"),
    ])
    quote("“Every commit is one more island on the Grand Line.”")
