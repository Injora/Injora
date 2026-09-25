// Renders a 31-day contribution activity graph as a themed SVG.
// Usage: GITHUB_TOKEN=... node activity-graph.mjs <username> <out.svg>
import { writeFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname } from "node:path";

const [user = "Injora", out = "dist/activity-graph.svg"] = process.argv.slice(2);
const token = process.env.GITHUB_TOKEN;
if (!token) throw new Error("GITHUB_TOKEN is required");

const THEME = JSON.parse(readFileSync(new URL("../theme.json", import.meta.url)));
const C = { bg: THEME.bg, text: THEME.text, line: THEME.blood, point: THEME.accent, glow: THEME.deepRed, violet: THEME.violetDark, muted: THEME.muted, grid: THEME.grid, border: THEME.border };
const DAYS = 31;

const to = new Date();
const from = new Date(to.getTime() - (DAYS - 1) * 864e5);
from.setUTCHours(0, 0, 0, 0);

const res = await fetch("https://api.github.com/graphql", {
  method: "POST",
  headers: { Authorization: `bearer ${token}`, "Content-Type": "application/json" },
  body: JSON.stringify({
    query: `query($login:String!,$from:DateTime!,$to:DateTime!){
      user(login:$login){ contributionsCollection(from:$from,to:$to){
        contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }`,
    variables: { login: user, from: from.toISOString(), to: to.toISOString() },
  }),
});
const json = await res.json();
if (json.errors) throw new Error(JSON.stringify(json.errors));

const days = json.data.user.contributionsCollection.contributionCalendar.weeks
  .flatMap((w) => w.contributionDays)
  .slice(-DAYS);

const W = 1000, H = 320, L = 56, R = 24, T = 64, B = 48;
const max = Math.max(4, ...days.map((d) => d.contributionCount));
const step = Math.ceil(max / 4);
const top = step * 4;
const x = (i) => L + (i * (W - L - R)) / (days.length - 1);
const y = (v) => T + (H - T - B) * (1 - v / top);

const pts = days.map((d, i) => [x(i), y(d.contributionCount)]);
const line = pts.map(([px, py], i) => `${i ? "L" : "M"}${px.toFixed(1)},${py.toFixed(1)}`).join(" ");
const area = `${line} L${x(days.length - 1).toFixed(1)},${y(0)} L${L},${y(0)} Z`;
const total = days.reduce((s, d) => s + d.contributionCount, 0);

const grid = [0, 1, 2, 3, 4].map((k) => {
  const v = k * step, gy = y(v).toFixed(1);
  return `<line x1="${L}" x2="${W - R}" y1="${gy}" y2="${gy}" stroke="${C.grid}" stroke-dasharray="3 4"/>` +
    `<text x="${L - 10}" y="${gy}" dy="4" text-anchor="end" class="axis">${v}</text>`;
}).join("");

const labels = days.map((d, i) => i % 5 === 0 || i === days.length - 1
  ? `<text x="${x(i).toFixed(1)}" y="${H - B + 22}" text-anchor="middle" class="axis">${d.date.slice(5).replace("-", "/")}</text>`
  : "").join("");

const dots = pts.map(([px, py], i) =>
  `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="3.5" fill="${C.bg}" stroke="${C.point}" stroke-width="2">` +
  `<title>${days[i].date}: ${days[i].contributionCount}</title></circle>`).join("");

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<style>
  .title{font:700 20px 'Segoe UI',Ubuntu,sans-serif;fill:${C.line}}
  .sub{font:500 13px 'Segoe UI',Ubuntu,sans-serif;fill:${C.muted}}
  .axis{font:500 11px 'Segoe UI',Ubuntu,sans-serif;fill:${C.muted}}
  .draw{stroke-dasharray:4000;stroke-dashoffset:4000;animation:draw 2.4s ease-out forwards}
  @keyframes draw{to{stroke-dashoffset:0}}
</style>
<defs>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="${C.line}" stop-opacity="0.35"/>
    <stop offset="0.6" stop-color="${C.glow}" stop-opacity="0.18"/>
    <stop offset="1" stop-color="${C.violet}" stop-opacity="0.05"/>
  </linearGradient>
  <linearGradient id="stroke" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="${C.glow}"/><stop offset="1" stop-color="${C.line}"/>
  </linearGradient>
</defs>
<rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="10" fill="${C.bg}" stroke="${C.border}"/>
<text x="${L - 30}" y="36" class="title">${user}'s Reiatsu Flow</text>
<text x="${W - R}" y="36" text-anchor="end" class="sub">${total} contributions · last ${DAYS} days</text>
${grid}${labels}
<path d="${area}" fill="url(#fill)"/>
<path d="${line}" fill="none" stroke="url(#stroke)" stroke-width="3" stroke-linejoin="round" class="draw"/>
${dots}
</svg>
`;

mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, svg);
console.log(`wrote ${out} (${total} contributions)`);
