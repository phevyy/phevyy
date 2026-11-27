"""Builds neon stats / languages / streak cards from the GitHub GraphQL API.

Usage:  GITHUB_TOKEN=... python scripts/build_stats.py <username> <out_dir>
Runs daily in .github/workflows/yilan.yml; output is pushed to the `output` branch.
"""
import json, os, sys, urllib.request
from datetime import date, datetime, timedelta, timezone
from xml.sax.saxutils import escape as esc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_assets as g
from generate_assets import BG, PANEL, PURPLE, PINK, CYAN, LILAC, TEXT, DIM, SANS, MONO, svg, write

API = "https://api.github.com/graphql"
IGNORED_LANGS = {"CMake", "Makefile", "Batchfile", "Procfile", "Dockerfile"}


def gql(query, variables, token):
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]


MAIN_Q = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE]) { totalCount }
    contributionsCollection { totalCommitContributions restrictedContributionsCount contributionYears }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}"""

YEAR_Q = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch(login, token):
    u = gql(MAIN_Q, {"login": login}, token)["user"]
    days = {}
    for y in sorted(u["contributionsCollection"]["contributionYears"]):
        v = {"login": login, "from": f"{y}-01-01T00:00:00Z", "to": f"{y}-12-31T23:59:59Z"}
        cal = gql(YEAR_Q, v, token)["user"]["contributionsCollection"]["contributionCalendar"]
        for w in cal["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return u, days


def streaks(days):
    today = datetime.now(timezone.utc).date()
    ds = sorted(d for d in days if date.fromisoformat(d) <= today)
    longest, cur, run, run_start = (0, None, None), 0, 0, None
    best = (0, None, None)
    for d in ds:
        if days[d] > 0:
            if run == 0:
                run_start = d
            run += 1
            if run > best[0]:
                best = (run, run_start, d)
        else:
            run = 0
    # current streak: today may still be empty
    cur, start, end = 0, None, None
    day = today if days.get(today.isoformat(), 0) > 0 else today - timedelta(days=1)
    end = day.isoformat()
    while days.get(day.isoformat(), 0) > 0:
        cur += 1
        start = day.isoformat()
        day -= timedelta(days=1)
    return best, (cur, start, end if cur else None)


def fmt(d):
    return date.fromisoformat(d).strftime("%b %d, %Y") if d else "—"


def short(d):
    return date.fromisoformat(d).strftime("%b %d") if d else "—"


# ------------------------------------------------------------------ cards
def stats_card(u, total_contrib):
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    rows = [
        ("Total Stars", stars, PINK),
        ("Commits (this year)", u["contributionsCollection"]["totalCommitContributions"]
         + u["contributionsCollection"]["restrictedContributionsCount"], CYAN),
        ("Pull Requests", u["pullRequests"]["totalCount"], PURPLE),
        ("Issues", u["issues"]["totalCount"], LILAC),
        ("Public Repos", u["repositories"]["totalCount"], PINK),
        ("Contributed To", u["repositoriesContributedTo"]["totalCount"], CYAN),
    ]
    W, H = 495, 220
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="{PURPLE}" stroke-opacity="0.6" stroke-width="2"/>',
         f'<text x="24" y="38" font-family="{MONO}" font-size="15" fill="{CYAN}">phevyy# <tspan fill="{TEXT}">show interface stats</tspan></text>']
    for i, (label, val, c) in enumerate(rows):
        y = 74 + i * 24
        b.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{0.2 + i*0.15:.2f}s" dur="0.4s" fill="freeze"/>'
                 f'<rect x="24" y="{y - 10}" width="8" height="8" rx="2" fill="{c}" filter="url(#glow)"/>'
                 f'<text x="42" y="{y}" font-family="{SANS}" font-size="14" fill="{TEXT}">{esc(label)}</text>'
                 f'<text x="300" y="{y}" text-anchor="end" font-family="{MONO}" font-size="14" font-weight="bold" fill="{c}">{val}</text></g>')
    # ring: all-time contributions
    cx, cy, r = 400, 125, 52
    circ = 2 * 3.14159 * r
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{PANEL}" stroke-width="10"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#neonStatic)" stroke-width="10" stroke-linecap="round" '
             f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" transform="rotate(-90 {cx} {cy})" filter="url(#glow)">'
             f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="0" dur="1.6s" fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1" keyTimes="0;1"/></circle>')
    b.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="{SANS}" font-size="26" font-weight="800" fill="url(#neon)">{total_contrib}</text>')
    b.append(f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{DIM}">CONTRIBUTIONS</text>')
    write("stats.svg", svg(W, H, "\n".join(b), "GitHub stats for phevyy"))


def langs_card(u):
    totals = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            if e["node"]["name"] in IGNORED_LANGS:
                continue
            totals[e["node"]["name"]] = totals.get(e["node"]["name"], 0) + e["size"]
    top = sorted(totals.items(), key=lambda x: -x[1])[:6]
    s = sum(v for _, v in top) or 1
    cols = [PINK, PURPLE, CYAN, LILAC, "#ff7ae9", "#7df9ff"]
    W, H = 495, 220
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="{PURPLE}" stroke-opacity="0.6" stroke-width="2"/>',
         f'<text x="24" y="38" font-family="{MONO}" font-size="15" fill="{CYAN}">phevyy# <tspan fill="{TEXT}">show languages</tspan></text>',
         f'<clipPath id="bar"><rect x="24" y="58" width="{W-48}" height="12" rx="6"/></clipPath>',
         f'<rect x="24" y="58" width="{W-48}" height="12" rx="6" fill="{PANEL}"/>']
    x, bw = 24, W - 48
    segs = []
    for i, (name, v) in enumerate(top):
        w = bw * v / s
        segs.append(f'<rect x="{x:.1f}" y="58" width="0" height="12" fill="{cols[i]}">'
                    f'<animate attributeName="width" from="0" to="{w:.1f}" begin="{i*0.15:.2f}s" dur="0.6s" fill="freeze"/></rect>')
        x += w
    b.append(f'<g clip-path="url(#bar)">{"".join(segs)}</g>')
    for i, (name, v) in enumerate(top):
        col, row = i % 2, i // 2
        lx, ly = 24 + col * 230, 104 + row * 36
        b.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{0.3 + i*0.12:.2f}s" dur="0.4s" fill="freeze"/>'
                 f'<circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="{cols[i]}" filter="url(#glow)"/>'
                 f'<text x="{lx + 20}" y="{ly}" font-family="{SANS}" font-size="14" fill="{TEXT}">{esc(name)}</text>'
                 f'<text x="{lx + 200}" y="{ly}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{cols[i]}">{100*v/s:.1f}%</text></g>')
    write("langs.svg", svg(W, H, "\n".join(b), "Top languages"))


def streak_card(days, best, cur):
    today = datetime.now(timezone.utc).date()
    first = min((d for d, c in days.items() if c > 0), default=None)
    total = sum(days.values())
    W, H = 1000, 240
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="{PURPLE}" stroke-opacity="0.6" stroke-width="2"/>']
    cols = [(167, "TOTAL CONTRIBUTIONS", str(total), f"{fmt(first)} – Present", CYAN),
            (500, "CURRENT STREAK", f"{cur[0]}", f"{short(cur[1])} – {short(cur[2])}" if cur[0] else "start one today!", PINK),
            (833, "LONGEST STREAK", f"{best[0]}", f"{short(best[1])} – {short(best[2])}" if best[0] else "—", PURPLE)]
    for x, label, val, sub, c in cols:
        if label == "CURRENT STREAK":
            for d in (0, 1.2):
                b.append(f'<circle cx="{x}" cy="68" r="40" fill="none" stroke="{c}" stroke-width="2">'
                         f'<animate attributeName="r" values="40;58" dur="2.4s" begin="{d}s" repeatCount="indefinite"/>'
                         f'<animate attributeName="opacity" values="0.8;0" dur="2.4s" begin="{d}s" repeatCount="indefinite"/></circle>')
            b.append(f'<circle cx="{x}" cy="68" r="40" fill="{PANEL}" stroke="{c}" stroke-width="4" filter="url(#glow)"/>')
            b.append(f'<text x="{x}" y="80" text-anchor="middle" font-family="{SANS}" font-size="34" font-weight="800" fill="{TEXT}">{val}</text>')
            b.append(f'<text x="{x}" y="132" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="bold" fill="{c}">{label}</text>')
            b.append(f'<text x="{x}" y="152" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{DIM}">{esc(sub)}</text>')
        else:
            b.append(f'<text x="{x}" y="82" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="800" fill="url(#neon)">{val}</text>')
            b.append(f'<text x="{x}" y="112" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="bold" fill="{c}">{label}</text>')
            b.append(f'<text x="{x}" y="132" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{DIM}">{esc(sub)}</text>')
    b.append(f'<line x1="333" y1="30" x2="333" y2="150" stroke="{PURPLE}" stroke-opacity="0.3"/><line x1="667" y1="30" x2="667" y2="150" stroke="{PURPLE}" stroke-opacity="0.3"/>')

    # traffic graph: weekly contributions over the last 52 weeks
    weeks = []
    for k in range(52, 0, -1):
        end = today - timedelta(days=7 * (k - 1))
        weeks.append(sum(days.get((end - timedelta(days=i)).isoformat(), 0) for i in range(7)))
    gx0, gx1, gy0, gy1 = 30, W - 30, 176, 226
    mx = max(weeks) or 1
    pts = [(gx0 + (gx1 - gx0) * i / (len(weeks) - 1), gy1 - (gy1 - gy0) * v / mx) for i, v in enumerate(weeks)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{gx0},{gy1} {line} {gx1},{gy1}"
    b.append(f'<linearGradient id="fillg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PINK}" stop-opacity="0.35"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>')
    b.append(f'<text x="{gx0}" y="{gy0 - 8}" font-family="{MONO}" font-size="10" fill="{DIM}">TRAFFIC · weekly contributions · last 52 weeks</text>')
    b.append(f'<polygon points="{area}" fill="url(#fillg)"/>')
    b.append(f'<polyline points="{line}" fill="none" stroke="url(#neonStatic)" stroke-width="2" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" filter="url(#glow)">'
             f'<animate attributeName="stroke-dashoffset" from="100" to="0" dur="2s" fill="freeze"/></polyline>')
    lx, ly = pts[-1]
    b.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{CYAN}" filter="url(#glow)"><animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite"/></circle>')
    write("streak.svg", svg(W, H, "\n".join(b), "Contribution streak"))


def game_card(days):
    """FIREWALL DEFENSE: a defender ship sweeps the contribution grid and blocks every packet."""
    import random
    today = datetime.now(timezone.utc).date()
    # grid: 53 columns (weeks, Sunday-first) x 7 rows, ending this week
    start = today - timedelta(days=(today.weekday() + 1) % 7) - timedelta(weeks=52)
    cs, gap, gx, gy = 14, 3, 50, 70
    W, H = 1000, 330
    ship_y = 285
    cells, targets = [], []
    nz = sorted(v for v in days.values() if v > 0)
    q = [nz[int(len(nz) * f)] if nz else 1 for f in (0.25, 0.5, 0.75)]
    lvl_col = [LILAC, PURPLE, PINK, CYAN]
    for c in range(53):
        for r in range(7):
            d = start + timedelta(days=c * 7 + r)
            if d > today:
                continue
            x, y = gx + c * (cs + gap), gy + r * (cs + gap)
            n = days.get(d.isoformat(), 0)
            if n > 0:
                lvl = sum(n > t for t in q)
                targets.append((x + cs / 2, y + cs / 2, x, y, lvl_col[lvl], n))
            else:
                cells.append((x, y))
    N = len(targets)
    step = min(0.6, max(0.22, 28 / max(N, 1)))
    move = step * 0.6
    T0 = 1.0
    end_play = T0 + N * step
    L = end_play + 3.5

    def kt(t):
        return f"{min(max(t / L, 0), 1):.5f}"

    D = f'dur="{L:.2f}s" repeatCount="indefinite"'
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="{PURPLE}" stroke-opacity="0.6" stroke-width="2"/>',
         f'<text x="24" y="34" font-family="{MONO}" font-size="15" font-weight="bold" fill="url(#neon)">FIREWALL DEFENSE</text>',
         f'<text x="190" y="34" font-family="{MONO}" font-size="12" fill="{DIM}">// every contribution is a packet. inspect them all.</text>']
    rnd = random.Random(42)
    for _ in range(40):
        sx, sy = rnd.randint(10, W - 10), rnd.randint(50, H - 10)
        b.append(f'<circle cx="{sx}" cy="{sy}" r="{rnd.choice((0.8, 1.2))}" fill="{TEXT}" opacity="0.3">'
                 f'<animate attributeName="opacity" values="0.1;0.5;0.1" dur="{rnd.uniform(2, 5):.1f}s" repeatCount="indefinite"/></circle>')
    last = None
    for c in range(53):
        m = (start + timedelta(days=c * 7)).strftime("%b")
        if m != last and c < 51:
            b.append(f'<text x="{gx + c * (cs + gap)}" y="{gy - 8}" font-family="{MONO}" font-size="10" fill="{DIM}">{m.upper()}</text>')
            last = m
    for x, y in cells:
        b.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="3" fill="{PANEL}" stroke="{PURPLE}" stroke-opacity="0.15"/>')

    ship_x, ship_t = [W / 2], [0.0]
    score, score_steps = 0, []
    for i, (cx, cy, x, y, col, n) in enumerate(targets):
        t_arrive = T0 + i * step + move
        t_hit = t_arrive + step * 0.25
        ship_t += [T0 + i * step, t_arrive]
        ship_x += [ship_x[-1], cx]
        # empty slot stays behind the packet
        b.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="3" fill="{PANEL}" stroke="{PURPLE}" stroke-opacity="0.15"/>')
        b.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="3" fill="{col}" filter="url(#glow)">'
                 f'<animate attributeName="opacity" calcMode="discrete" values="1;0;1" keyTimes="0;{kt(t_hit)};{kt(L - 0.05)}" {D}/></rect>')
        b.append(f'<line x1="{cx}" y1="{ship_y - 16}" x2="{cx}" y2="{cy}" stroke="{CYAN}" stroke-width="3" opacity="0" filter="url(#glow)">'
                 f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{kt(t_arrive)};{kt(t_hit)}" {D}/></line>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="2" fill="none" stroke="{col}" stroke-width="2" opacity="0">'
                 f'<animate attributeName="r" values="2;2;18;18" keyTimes="0;{kt(t_hit)};{kt(t_hit + 0.4)};1" {D}/>'
                 f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{kt(t_hit - 0.01)};{kt(t_hit)};{kt(t_hit + 0.4)};1" {D}/></circle>')
        score += n
        score_steps.append((t_hit, score))
    ship_t += [end_play + 0.6, L]
    ship_x += [W / 2, W / 2]
    kts = [kt(t) for t in ship_t]
    kts[0], kts[-1] = "0", "1"
    ship_vals = ";".join(f"{x:.1f} 0" for x in ship_x)

    b.append(f'<g><animateTransform attributeName="transform" type="translate" values="{ship_vals}" keyTimes="{";".join(kts)}" {D}/>'
             f'<path d="M0 {ship_y - 16} L16 {ship_y - 4} L12 {ship_y + 12} L0 {ship_y + 6} L-12 {ship_y + 12} L-16 {ship_y - 4} Z" fill="{PANEL}" stroke="{PINK}" stroke-width="2.5" filter="url(#glow)"/>'
             f'<rect x="-6" y="{ship_y - 4}" width="12" height="6" rx="1" fill="{CYAN}"/>'
             f'<path d="M-5 {ship_y + 12} L0 {ship_y + 24} L5 {ship_y + 12} Z" fill="{CYAN}" opacity="0.8">'
             f'<animate attributeName="opacity" values="0.3;1;0.3" dur="0.3s" repeatCount="indefinite"/></path></g>')
    b.append(f'<line x1="30" y1="{ship_y + 30}" x2="{W - 30}" y2="{ship_y + 30}" stroke="{PURPLE}" stroke-opacity="0.35" stroke-dasharray="6 6"/>')

    # HUD score: one text per value, each visible only in its own time window
    b.append(f'<text x="{W - 250}" y="34" font-family="{MONO}" font-size="12" fill="{DIM}">PACKETS INSPECTED</text>')
    windows = [(0.0, 0)] + score_steps
    for k, (t, val) in enumerate(windows):
        t_next = windows[k + 1][0] if k + 1 < len(windows) else L
        if k == 0:
            vals, kts2 = "1;0;1", f"0;{kt(t_next)};{kt(L - 0.05)}"
        elif t_next >= L:
            vals, kts2 = "0;1;0", f"0;{kt(t)};{kt(L - 0.05)}"
        else:
            vals, kts2 = "0;1;0", f"0;{kt(t)};{kt(t_next)}"
        b.append(f'<text x="{W - 24}" y="35" text-anchor="end" font-family="{MONO}" font-size="18" font-weight="bold" fill="{CYAN}" opacity="{1 if k == 0 else 0}">'
                 f'{val:05d}<animate attributeName="opacity" calcMode="discrete" values="{vals}" keyTimes="{kts2}" {D}/></text>')
    b.append(f'<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{kt(end_play + 0.3)};{kt(L - 0.2)}" {D}/>'
             f'<rect x="{W/2 - 190}" y="{gy + 30}" width="380" height="54" rx="10" fill="{BG}" stroke="url(#neonStatic)" stroke-width="2" filter="url(#glow)"/>'
             f'<text x="{W/2}" y="{gy + 64}" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="bold" fill="url(#neon)">ALL THREATS BLOCKED ✓</text></g>')
    write("game.svg", svg(W, H, "\n".join(b), "Firewall Defense — contribution game"))


def main():
    login, out = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("GITHUB_TOKEN is not set")
    g.OUT = out
    u, days = fetch(login, token)
    best, cur = streaks(days)
    stats_card(u, sum(days.values()))
    langs_card(u)
    streak_card(days, best, cur)
    game_card(days)
    print(f"ok: {sum(days.values())} contributions, current streak {cur[0]}, longest {best[0]}")


if __name__ == "__main__":
    main()
