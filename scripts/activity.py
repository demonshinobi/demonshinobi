#!/usr/bin/env python3
"""Render activity.svg: the last year of contributions as an ASCII density field.

Stdlib only. Reads a token from GITHUB_TOKEN / GH_TOKEN and writes ../activity.svg.
"""
import datetime as dt
import json
import math
import os
import pathlib
import urllib.request

LOGIN = "demonshinobi"
OUT = pathlib.Path(__file__).resolve().parent.parent / "activity.svg"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      restrictedContributionsCount
      totalCommitContributions totalIssueContributions totalPullRequestContributions
      totalPullRequestReviewContributions totalRepositoryContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}"""

W, H = 869, 236
PAD_X = 44
GRID_Y = 84
PITCH_X = (W - 2 * PAD_X) / 53
PITCH_Y = 14
RAMP = ["·", ":", "+", "#", "@"]
INK = [0.16, 0.40, 0.62, 0.84, 1.0]
RED = "#ff3547"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def fetch():
    token = os.environ.get("GITHUB_TOKEN") or os.environ["GH_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]["contributionsCollection"]


def levels(days):
    """Log-scale levels: counts span 1..hundreds, so rank or GitHub quartiles flatten the field."""
    active = sorted(d["contributionCount"] for d in days if d["contributionCount"])
    top = math.log(active[-1] + 1) if active else 1
    hot = active[int(len(active) * 0.97)] if active else 1
    for d in days:
        n = d["contributionCount"]
        d["lvl"] = 0 if not n else 1 + min(3, int(4 * math.log(n) / top))
        d["hot"] = bool(n) and n >= hot


def busiest_month(days):
    totals = {}
    for d in days:
        totals[d["date"][:7]] = totals.get(d["date"][:7], 0) + d["contributionCount"]
    ym = max(totals, key=totals.get)
    return dt.date.fromisoformat(ym + "-01").strftime("%b '%y").upper(), totals[ym]


def render(c):
    cal = c["contributionCalendar"]
    weeks = cal["weeks"][-53:]
    days = [d for w in weeks for d in w["contributionDays"]]
    levels(days)
    total = cal["totalContributions"]
    public = sum(c[k] for k in (
        "totalCommitContributions", "totalIssueContributions", "totalPullRequestContributions",
        "totalPullRequestReviewContributions", "totalRepositoryContributions"))
    private = max(c["restrictedContributionsCount"], total - public)
    counts = [d["contributionCount"] for d in days]
    month, month_total = busiest_month(days)
    pct = 100 * private / total if total else 0
    today = days[-1]["date"]

    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
      f'aria-label="{total:,} contributions in the last year, {pct:.1f}% private">')
    a(f"<title>{total:,} contributions in the last year</title>")
    a(f"""<defs>
  <pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="0.6" fill="#9fb4d8" opacity="0.10"/>
  </pattern>
  <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ff3547" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#ff3547" stop-opacity="0.30"/>
    <stop offset="1" stop-color="#ff3547" stop-opacity="0"/>
  </linearGradient>
  <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="panel"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>""")
    a(f"""<style>
  text {{ font-family: {MONO}; }}
  .g {{ font-size: 12px; fill: #eef2f8; text-anchor: middle; }}
  .h {{ fill: {RED}; filter: url(#glow); animation: fl 5s steps(1,end) infinite; }}
  .lab {{ font-size: 9px; fill: #eef2f8; opacity: 0.38; letter-spacing: 2.2px; }}
  .meta {{ font-size: 10px; fill: #eef2f8; opacity: 0.55; letter-spacing: 3px; }}
  .leg {{ font-size: 9px; fill: #eef2f8; letter-spacing: 2.2px; }}
  .big {{ font-size: 22px; fill: #eef2f8; letter-spacing: 1px; }}
  .red {{ fill: {RED}; }}
  .scan {{ animation: sw 9s ease-in-out infinite; }}
  .cur {{ animation: bl 1.1s steps(1,end) infinite; }}
  @keyframes sw {{ 0% {{ transform: translateX(-12%); }} 60%, 100% {{ transform: translateX(112%); }} }}
  @keyframes bl {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: 0.15; }} }}
  @keyframes fl {{ 0%, 86%, 100% {{ opacity: 1; }} 89% {{ opacity: 0.2; }} 92% {{ opacity: 1; }} 95% {{ opacity: 0.45; }} }}
  @media (prefers-reduced-motion: reduce) {{ .scan, .cur, .h {{ animation: none; }} }}
</style>""")
    a('<g clip-path="url(#panel)">')
    a(f'<rect width="{W}" height="{H}" fill="#05070b"/><rect width="{W}" height="{H}" fill="url(#dots)"/>')

    a(f'<text class="meta" x="{PAD_X}" y="38">// ACTIVITY</text>')
    a(f'<text class="meta" x="{W - PAD_X}" y="38" text-anchor="end">LAST 365D · SYNC {today}</text>')

    seen = set()
    for wi, w in enumerate(weeks):
        first = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        m = first.strftime("%b").upper()
        if first.day <= 7 and m not in seen and wi < 51:
            seen.add(m)
            a(f'<text class="lab" x="{PAD_X + wi * PITCH_X:.1f}" y="{GRID_Y - 18}">{m}</text>')

    a("<g>")
    for wi, w in enumerate(weeks):
        x = PAD_X + wi * PITCH_X + PITCH_X / 2
        for d in w["contributionDays"]:
            y = GRID_Y + d["weekday"] * PITCH_Y
            if d["date"] == today:
                a(f'<rect class="cur" x="{x - 4:.1f}" y="{y - 9}" width="8" height="11" fill="{RED}"/>')
                continue
            glyph = RAMP[d["lvl"]]
            if d["hot"]:
                delay = (int(d["date"].replace("-", "")) * 7919) % 50 / 10
                a(f'<text class="g h" x="{x:.1f}" y="{y}" style="animation-delay:{delay}s">{glyph}</text>')
            else:
                a(f'<text class="g" x="{x:.1f}" y="{y}" opacity="{INK[d["lvl"]]}">{glyph}</text>')
    a("</g>")

    a(f'<rect class="scan" x="{PAD_X - 60}" y="{GRID_Y - 12}" width="60" height="{7 * PITCH_Y + 4}" fill="url(#scan)"/>')

    fy = H - 34
    stats = [
        (f"{total:,}", "CONTRIBUTIONS"),
        (f"{pct:.1f}%", "PRIVATE"),
        (f"{max(counts):,}", "PEAK DAY"),
        (month, f"BUSIEST \u00b7 {month_total:,}"),
    ]
    x = PAD_X
    for i, (v, k) in enumerate(stats):
        cls = "big red" if i == 1 else "big"
        a(f'<text class="{cls}" x="{x}" y="{fy}">{v}</text>')
        a(f'<text class="lab" x="{x}" y="{fy + 16}">{k}</text>')
        x += 150

    spans = "".join(f'<tspan fill-opacity="{INK[i]}" dx="6">{g}</tspan>' for i, g in enumerate(RAMP))
    a(f'<text class="leg" x="{W - PAD_X}" y="{fy + 16}" text-anchor="end">'
      f'<tspan fill-opacity="0.38">LESS</tspan>{spans}<tspan fill-opacity="0.38" dx="8">MORE</tspan></text>')
    a("</g></svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    svg = render(fetch())
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg):,} bytes)")
