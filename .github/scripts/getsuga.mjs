// Renders the contribution grid "Getsuga Tenshō" animation: the grid starts fully
// charged, a swordsman swings, and a crescent slash reveals the real contributions.
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
    full: "#ff6a00", ink: "#0a0a0a", outline: "none", text: "#0a0a0a",
  },
  dark: {
    levels: ["#161b22", "#1e3a8a", "#7c2d12", "#c2410c", "#ff6a00"],
    full: "#ff6a00", ink: "#0a0a0a", outline: "#f5f5f5", text: "#f5f5f5",
  },
};

// Layout
const CELL = 12, PITCH = 15, GX = 150, GY = 46;
const cols = weeks.length;
const W = GX + cols * PITCH + 24;
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

  const stroke = t.outline === "none" ? "" : ` stroke="${t.outline}" stroke-width="1"`;

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
  .swing{animation:swing ${DUR}s ease-in-out infinite}
  @keyframes swing{0%,12%{transform:rotate(-35deg)}17%{transform:rotate(-65deg)}20.5%{transform:rotate(100deg)}40%{transform:rotate(100deg)}55%,100%{transform:rotate(-35deg)}}
  .aura{animation:aura ${DUR}s ease-in-out infinite}
  @keyframes aura{0%,2%{opacity:0}8%{opacity:.5}12%{opacity:.25}16%{opacity:.9}21%,100%{opacity:0}}
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

<!-- Swordsman (original silhouette) -->
<g transform="translate(18 ${H - 128})">
  <ellipse cx="58" cy="120" rx="40" ry="4" fill="${t.ink}" opacity="0.25"/>
  <!-- hakama + legs -->
  <path d="M44,74 L34,118 L50,118 L56,92 L62,118 L80,118 L70,74 Z" fill="${t.ink}"${stroke}/>
  <!-- torso -->
  <path d="M44,40 L70,40 L73,78 L41,78 Z" fill="${t.ink}"${stroke}/>
  <path d="M41,70 L73,70" stroke="#f5f5f5" stroke-width="2"/>
  <!-- head + hair -->
  <circle cx="57" cy="28" r="9" fill="${t.ink}"${stroke}/>
  <path d="M46,26 L42,14 L50,18 L50,8 L56,16 L60,5 L62,15 L70,9 L68,19 L75,18 L68,26 Q57,17 46,26 Z" fill="#ff6a00"/>
  <!-- arm + blade -->
  <g transform="translate(66 46)">
    <g class="swing">
      <ellipse class="aura" cx="18" cy="-40" rx="14" ry="44" fill="#ff4500" filter="url(#glow)"/>
      <path d="M0,0 L18,0" stroke="${t.ink}" stroke-width="6" stroke-linecap="round"/>
      <rect x="15" y="-6" width="6" height="14" fill="#7c2d12"/>
      <rect x="11" y="-9" width="14" height="3" fill="#9ca3af"/>
      <path d="M13,-9 L23,-9 L22,-78 L18,-86 L14,-78 Z" fill="#0a0a0a" stroke="#f5f5f5" stroke-width="1"/>
    </g>
  </g>
</g>
</svg>
`;
}

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "getsuga-tensho.svg"), render(THEMES.light));
writeFileSync(join(outDir, "getsuga-tensho-dark.svg"), render(THEMES.dark));
console.log(`wrote ${cols} weeks to ${outDir}/getsuga-tensho{,-dark}.svg`);
