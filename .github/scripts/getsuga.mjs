// Renders the contribution grid "Getsuga Tenshō" animation: the grid starts fully
// charged, then a crescent slash sweeps across and reveals the real contributions.
// The character animation lives separately in assets/getsuga/ichigo-getsuga.gif.
// Usage: GITHUB_TOKEN=... node getsuga.mjs <username> <outDir>
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const [user = "Injora", outDir = "dist"] = process.argv.slice(2);
const token = process.env.GITHUB_TOKEN;
if (!token) throw new Error("GITHUB_TOKEN is required");

const res = await fetch("https://api.github.com/graphql", {
  method: "POST",
  headers: { Authorization: `bearer ${token}`, "Content-Type": "application/json" },
  body: JSON.stringify({
    query: `query($login:String!){ user(login:$login){ contributionsCollection{
      contributionCalendar{ weeks{ contributionDays{ weekday contributionLevel } } } } } }`,
    variables: { login: user },
  }),
});
const json = await res.json();
if (json.errors) throw new Error(JSON.stringify(json.errors));
const weeks = json.data.user.contributionsCollection.contributionCalendar.weeks;

const LEVEL = { NONE: 0, FIRST_QUARTILE: 1, SECOND_QUARTILE: 2, THIRD_QUARTILE: 3, FOURTH_QUARTILE: 4 };

const THEMES = {
  light: {
    levels: ["#ebedf0", "#fed7aa", "#fdba74", "#fb923c", "#ff6a00"],
    full: "#ff6a00", text: "#0a0a0a",
  },
  dark: {
    levels: ["#161b22", "#1e3a8a", "#7c2d12", "#c2410c", "#ff6a00"],
    full: "#ff6a00", text: "#f5f5f5",
  },
};

// Layout
const CELL = 12, PITCH = 15, GX = 24, GY = 34;
const cols = weeks.length;
const W = GX + cols * PITCH + GX;
const H = GY + 7 * PITCH + 22;
const MIDY = GY + (7 * PITCH) / 2;

// Timeline (percent of a DUR-second loop)
const DUR = 10;
const SLASH_START = 20, SLASH_END = 66, RESET_START = 90, RESET_END = 96;
const X0 = GX - 60, X1 = GX + cols * PITCH + 40; // crescent travel range
const FRONT = 24; // crescent tip offset from its origin
const pct = (n) => `${n.toFixed(2)}%`;
const hitTime = (i) => {
  const cx = GX + i * PITCH + CELL / 2;
  return SLASH_START + ((cx - FRONT - X0) / (X1 - X0)) * (SLASH_END - SLASH_START);
};

function render(t) {
  const base = [], overlay = [], keyframes = [];
  weeks.forEach((w, i) => {
    const x = GX + i * PITCH;
    const cells = w.contributionDays.map((d) => {
      const y = GY + d.weekday * PITCH;
      base.push(`<rect x="${x}" y="${y}" width="${CELL}" height="${CELL}" rx="2" fill="${t.levels[LEVEL[d.contributionLevel]]}"/>`);
      return `<rect x="${x}" y="${y}" width="${CELL}" height="${CELL}" rx="2"/>`;
    });
    overlay.push(`<g class="c${i}">${cells.join("")}</g>`);
    const h = hitTime(i);
    keyframes.push(
      `@keyframes c${i}{0%,${pct(h)}{opacity:1;fill:${t.full}}${pct(h + 0.5)}{opacity:1;fill:#fff}` +
      `${pct(h + 2.2)},${RESET_START}%{opacity:0;fill:${t.full}}${RESET_END}%,100%{opacity:1;fill:${t.full}}}` +
      `.c${i}{animation:c${i} ${DUR}s linear infinite}`,
    );
  });

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<defs>
  <linearGradient id="core" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#0a0a0a"/><stop offset="0.7" stop-color="#1a0500"/><stop offset="1" stop-color="#ff2a00"/>
  </linearGradient>
  <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ff6a00" stop-opacity="0"/><stop offset="1" stop-color="#ff6a00" stop-opacity="0.35"/>
  </linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<style>
  ${keyframes.join("\n  ")}
  .slash{animation:slash ${DUR}s linear infinite}
  @keyframes slash{0%,${SLASH_START - 0.5}%{transform:translateX(${X0}px);opacity:0}${SLASH_START}%{transform:translateX(${X0}px);opacity:1}${SLASH_END}%{transform:translateX(${X1}px);opacity:1}${SLASH_END + 3}%,100%{transform:translateX(${X1 + 30}px);opacity:0}}
  .name{font:italic 900 15px 'Segoe UI',Ubuntu,sans-serif;fill:#ff6a00;letter-spacing:3px;animation:name ${DUR}s ease-out infinite}
  @keyframes name{0%,18%{opacity:0}21%{opacity:1}45%{opacity:1}55%,100%{opacity:0}}
  .full{font:600 11px 'Segoe UI',Ubuntu,sans-serif;fill:${t.text};opacity:.6;animation:full ${DUR}s linear infinite}
  @keyframes full{0%,15%{opacity:.6}19%,${RESET_END}%{opacity:0}100%{opacity:.6}}
</style>

<text x="${GX}" y="${GY - 12}" class="full">reiatsu fully charged…</text>
<text x="${GX}" y="${GY - 12}" class="name">GETSUGA TENSHŌ!</text>

<g>${base.join("")}</g>
<g fill="${t.full}">${overlay.join("")}</g>

<!-- Crescent slash -->
<g class="slash">
  <g transform="translate(0 ${MIDY})">
    <rect x="-150" y="-58" width="150" height="116" fill="url(#trail)"/>
    <path d="M-2,-74 Q52,0 -2,74 Q20,0 -2,-74 Z" fill="#ff2a00" filter="url(#glow)" opacity="0.9"/>
    <path d="M0,-70 Q46,0 0,70 Q18,0 0,-70 Z" fill="url(#core)" stroke="#ff4500" stroke-width="1.5"/>
    <path d="M6,-50 Q34,0 6,50" fill="none" stroke="#fff" stroke-opacity="0.8" stroke-width="1.2"/>
  </g>
</g>

</svg>
`;
}

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "getsuga-tensho.svg"), render(THEMES.light));
writeFileSync(join(outDir, "getsuga-tensho-dark.svg"), render(THEMES.dark));
console.log(`wrote ${cols} weeks to ${outDir}/getsuga-tensho{,-dark}.svg`);
