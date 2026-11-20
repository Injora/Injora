"""Static README art in the same visual language as the blood header:
section dividers, project cards, link buttons and the closing quote.

Usage: python readme_art.py   (writes into assets/)
"""
import json
import random
import re
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent.parent
T = json.loads((ROOT / ".github/theme.json").read_text())
OUT = ROOT / "assets"
DISPLAY = "'Helvetica Neue','Arial Black',Arial,sans-serif"
MONO = "'SF Mono',Menlo,Consolas,'Courier New',monospace"

METAL = """<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset=".46" stop-color="#E9E6EC"/>
  <stop offset=".54" stop-color="#ABA6B0"/><stop offset="1" stop-color="#F2F0F4"/></linearGradient>"""
DRIP = f"""<linearGradient id="drip" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{T['deepRed']}"/><stop offset="1" stop-color="{T['crimson']}"/></linearGradient>"""


def drip(cx, y, h, w, r):
    return (f"M{cx-w:.1f},{y} C{cx-w*0.25:.1f},{y+h*0.35:.1f} {cx-r:.1f},{y+h-r*2.6:.1f} {cx-r:.1f},{y+h-r:.1f} "
            f"A{r:.1f},{r:.1f} 0 0 0 {cx+r:.1f},{y+h-r:.1f} "
            f"C{cx+r:.1f},{y+h-r*2.6:.1f} {cx+w*0.25:.1f},{y+h*0.35:.1f} {cx+w:.1f},{y} Z")


def icon(name, x, y, h):
    """Inline one of assets/icons as a nested <svg>."""
    src = (OUT / "icons" / f"{name}.svg").read_text()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    vw, vh = map(float, vb.split()[2:])
    inner = src[src.index(">") + 1: src.rindex("</svg>")]
    return f'<svg x="{x}" y="{y}" width="{h*vw/vh:.1f}" height="{h}" viewBox="{vb}">{inner}</svg>'


def save(name, svg):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


# ── section dividers ────────────────────────────────────────────────
def section(slug, title, icon_name, seed):
    rng = random.Random(seed)
    W, H, cy = 1000, 92, 38
    tw = len(title) * 17.5 + 6               # rough width of 30px heavy type
    iw = 36
    gw = iw + 14 + tw
    x0 = W / 2 - gw / 2
    lx, rx = x0 - 34, x0 + gw + 34
    drips = "".join(
        f'<path d="{drip(x0 + iw + 14 + tw * f, cy + 21, rng.uniform(5, 13), rng.uniform(2.6, 4), 1.7)}"/>'
        for f in (rng.uniform(.12, .3), rng.uniform(.45, .6), rng.uniform(.75, .92)))
    save(f"sections/{slug}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
<defs>{METAL}{DRIP}
  <linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{T['crimson']}" stop-opacity="0"/><stop offset="1" stop-color="{T['blood']}"/></linearGradient>
  <linearGradient id="r" x1="1" x2="0"><stop offset="0" stop-color="{T['crimson']}" stop-opacity="0"/><stop offset="1" stop-color="{T['blood']}"/></linearGradient>
  <linearGradient id="slash" x1="0" x2="1"><stop offset="0" stop-color="{T['deepRed']}" stop-opacity="0"/><stop offset=".2" stop-color="{T['crimson']}"/><stop offset=".8" stop-color="{T['crimson']}"/><stop offset="1" stop-color="{T['deepRed']}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="60" y="{cy-.6}" width="{lx-60:.1f}" height="1.2" fill="url(#l)"/>
<rect x="{rx:.1f}" y="{cy-.6}" width="{W-60-rx:.1f}" height="1.2" fill="url(#r)"/>
<path d="M{lx+3:.1f},{cy} l-5,-5 l-5,5 l5,5z M{rx-3:.1f},{cy} l5,-5 l5,5 l-5,5z" fill="{T['blood']}"/>
{icon(icon_name, round(x0), cy - 19, 54)}
<text x="{x0 + iw + 14:.1f}" y="{cy + 11}" font-family="{DISPLAY}" font-weight="900" font-size="30" letter-spacing="1.5" fill="url(#metal)" stroke="{T['crimson']}" stroke-width=".6" paint-order="stroke">{escape(title)}</text>
<path d="M{x0 + iw + 10:.1f},{cy + 19} L{x0 + gw + 4:.1f},{cy + 18} L{x0 + gw:.1f},{cy + 22} L{x0 + iw + 14:.1f},{cy + 22.5}Z" fill="url(#slash)"/>
<g fill="url(#drip)">{drips}</g>
</svg>''')


# ── project cards ───────────────────────────────────────────────────
def card(slug, title, body, tags, seed):
    rng = random.Random(seed)
    W, H, pad = 500, 270, 30
    lines = textwrap.wrap(body, 58)
    text = "".join(f'<tspan x="{pad}" dy="{0 if i == 0 else 22}">{escape(l)}</tspan>' for i, l in enumerate(lines))
    pills, px = "", pad
    for t in tags:
        w = len(t) * 7.8 + 22
        pills += (f'<rect x="{px}" y="{H-50}" width="{w:.1f}" height="26" rx="3" fill="#1A0D11" stroke="{T["borderHi"]}" stroke-width="1"/>'
                  f'<text x="{px + w/2:.1f}" y="{H-32.5}" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{T["text"]}">{escape(t)}</text>')
        px += w + 8
    drips = "".join(f'<path d="{drip(rng.uniform(40, W-40), 3, rng.choice([rng.uniform(6, 12)]*3 + [rng.uniform(16, 26)]), rng.uniform(4, 7), 2.2)}"/>'
                    for _ in range(7))
    binary = "".join(f'<tspan x="{W-22}" dy="{0 if k == 0 else 15}">{rng.choice("01")}</tspan>' for k in range(14))
    save(f"cards/{slug}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}: {escape(body)}">
<defs>{METAL}{DRIP}
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140A0E"/><stop offset=".45" stop-color="{T['panel']}"/></linearGradient>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="8"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <text y="44" font-family="{MONO}" font-size="12" font-weight="700" fill="{T['crimson']}" opacity=".16" text-anchor="middle">{binary}</text>
  <rect width="{W}" height="4" fill="{T['crimson']}"/>
  <g fill="url(#drip)">{drips}</g>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="none" stroke="{T['border']}"/>
{icon("marker", pad - 4, 37, 27)}
<text x="{pad + 26}" y="58" font-family="{DISPLAY}" font-weight="900" font-size="25" letter-spacing=".5" fill="url(#metal)">{escape(title)}</text>
<text y="96" font-family="{DISPLAY}" font-size="15" fill="{T['text2']}">{text}</text>
{pills}
</svg>''')


# ── link buttons ────────────────────────────────────────────────────
def button(slug, label):
    W, H, c = 200, 50, 12
    save(f"buttons/{slug}.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<defs>{METAL}
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5A0914"/><stop offset="1" stop-color="#2A050C"/></linearGradient></defs>
<path d="M{c},1 H{W-1} V{H-c} L{W-c},{H-1} H1 V{c}Z" fill="url(#bg)" stroke="{T['blood']}" stroke-width="1.2"/>
<path d="M{c+4},5 H{W-5}" stroke="#FF4157" stroke-opacity=".35"/>
<path d="M24,25 l5,-8 l5,8 l-5,8z" fill="{T['blood']}"/>
<text x="{W/2 + 10}" y="31" text-anchor="middle" font-family="{DISPLAY}" font-weight="800" font-size="17" letter-spacing="1" fill="url(#metal)">{label}</text>
</svg>''')


# ── closing quote ───────────────────────────────────────────────────
def quote(text):
    W, H = 1000, 110
    save("quote.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(text)}">
<defs>{METAL}
  <linearGradient id="b" x1="0" x2="1"><stop offset="0" stop-color="{T['crimson']}" stop-opacity="0"/><stop offset=".5" stop-color="{T['blood']}"/><stop offset="1" stop-color="{T['crimson']}" stop-opacity="0"/></linearGradient></defs>
<text x="500" y="50" text-anchor="middle" font-family="{DISPLAY}" font-style="italic" font-weight="300" font-size="27" fill="url(#metal)">{escape(text)}</text>
<path d="M250,74 L750,72 L742,76 L258,77Z" fill="url(#b)"/>
</svg>''')


if __name__ == "__main__":
    section("profile", "Shinigami Profile", "mask", 1)
    section("arsenal", "Zanpakutō Arsenal", "blade", 2)
    section("releases", "Bankai Releases", "flame", 3)
    section("readings", "Reiatsu Readings", "pulse", 4)
    section("getsuga", "Getsuga Tenshō", "crescent", 5)
    card("compass", "OpenSource Compass",
         "Helps beginners find GSoC and open-source orgs that actually fit them. Researches real orgs "
         "(GitHub activity, contribution docs, good first issues) and returns an evidence-backed top 5 "
         "with a personalised 30-day roadmap.",
         ["TypeScript", "Prisma", "PostgreSQL", "GitHub API"], 11)
    card("shuttle", "Shuttle Tracker",
         "Live shuttle tracking for a college's off-campus hostel network, with student, driver and admin "
         "roles. PostGIS geofenced pickups, quorum-triggered dispatch and real-time GPS streaming, all "
         "enforced server-side.",
         ["React Native", "Expo", "Supabase", "PostGIS"], 12)
    card("funds", "NST-Funds",
         "Fund request and expense tracking portal for college clubs: line-item budget requests, admin "
         "review and partial approvals, UPI payment proofs, bill uploads and settlement, plus a public "
         "event gallery.",
         ["Go", "Astro", "TypeScript", "PostgreSQL"], 13)
    card("arena", "Bleach Battle Arena",
         "Two-player drafting and battle simulator powered by a live Bleach API. Draft teams of three, "
         "clash on spiritual pressure with race multipliers, and trigger one-time Bankai and "
         "Resurrección revivals.",
         ["JavaScript", "HTML", "CSS", "REST API"], 14)
    button("linkedin", "LinkedIn")
    button("portfolio", "Portfolio")
    button("email", "Email")
    quote("“The code is my zanpakutō, and every commit sharpens the blade.”")
