import os, sys
from xml.sax.saxutils import escape as esc

OUT = "assets"

BG = "#0b0418"
PANEL = "#140a2e"
PURPLE = "#b026ff"
PINK = "#ff2bd6"
CYAN = "#00f0ff"
LILAC = "#c77dff"
TEXT = "#e8dcff"
DIM = "#6b5a8e"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "Consolas, 'Cascadia Code', 'Courier New', monospace"

DEFS = f"""
  <linearGradient id="neon" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{PINK}"/>
    <stop offset="0.5" stop-color="{PURPLE}"/>
    <stop offset="1" stop-color="{CYAN}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;2 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="neonStatic" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{PINK}"/>
    <stop offset="0.5" stop-color="{PURPLE}"/>
    <stop offset="1" stop-color="{CYAN}"/>
  </linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
"""

def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">\n'
            f'<title>{esc(title)}</title>\n<defs>{DEFS}</defs>\n{body}\n</svg>\n')

def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)

# ---------------------------------------------------------------- banner
def banner():
    W, H = 1200, 400
    b = []
    b.append(f'''<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M40 0H0V40" fill="none" stroke="{PURPLE}" stroke-opacity="0.10"/>
  </pattern>
  <radialGradient id="gl" cx="0.15" cy="0.3" r="0.6"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0.35"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gr" cx="0.8" cy="0.7" r="0.5"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.18"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>''')
    b.append(f'<g clip-path="url(#frame)">')
    b.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#gl)"/><rect width="{W}" height="{H}" fill="url(#gr)"/>')
    # scanline
    b.append(f'<rect x="0" y="-10" width="{W}" height="3" fill="{CYAN}" opacity="0.07"><animate attributeName="y" values="-10;{H+10}" dur="6s" repeatCount="indefinite"/></rect>')

    # left text block
    b.append(f'<text x="60" y="95" font-family="{MONO}" font-size="18" fill="{CYAN}">&gt; ssh admin@phevyy</text>')
    cur_x = 60 + len("> ssh admin@phevyy") * 10 + 6
    b.append(f'<rect x="{cur_x}" y="80" width="10" height="19" fill="{CYAN}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect>')
    for y, t in ((168, "FIKRET EMRE"), (236, "SINMAZ")):
        b.append(f'<text x="58" y="{y}" font-family="{SANS}" font-size="62" font-weight="800" letter-spacing="2" fill="url(#neon)" filter="url(#glow)">{t}</text>')
    b.append(f'<text x="60" y="284" font-family="{SANS}" font-size="24" fill="{TEXT}">Computer Engineer <tspan fill="{PINK}">|</tspan> Network &amp; Security</text>')
    x = 60
    cols = [PINK, PURPLE, CYAN, PINK, PURPLE, CYAN]
    for i, chip in enumerate(["FortiGate", "Cisco IOS", "OSPF", "VLAN", "ACL", "Python"]):
        w = len(chip) * 8.5 + 24
        c = cols[i]
        b.append(f'<g><rect x="{x}" y="314" width="{w:.0f}" height="30" rx="15" fill="{c}" fill-opacity="0.10" stroke="{c}" stroke-width="1.5">'
                 f'<animate attributeName="fill-opacity" values="0.08;0.28;0.08" dur="3s" begin="{i*0.5}s" repeatCount="indefinite"/></rect>'
                 f'<text x="{x + w/2:.0f}" y="334" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{TEXT}">{chip}</text></g>')
        x += w + 10

    # topology
    links = {
        "e1": "M900 72 V115",
        "e2": "M900 155 V195",
        "e3": "M880 235 L790 272",
        "e4": "M920 235 L1010 272",
        "e5": "M760 308 L708 346",
        "e6": "M780 308 L832 346",
        "e7": "M1020 308 L968 346",
        "e8": "M1040 308 L1092 346",
    }
    b.append('<defs>' + ''.join(f'<path id="{k}" d="{d}"/>' for k, d in links.items()) + '</defs>')
    for k, d in links.items():
        b.append(f'<path d="{d}" stroke="{PURPLE}" stroke-opacity="0.45" stroke-width="2" fill="none"/>')
        b.append(f'<path d="{d}" stroke="{CYAN}" stroke-opacity="0.6" stroke-width="2" fill="none" stroke-dasharray="4 12">'
                 f'<animate attributeName="stroke-dashoffset" values="32;0" dur="1.2s" repeatCount="indefinite"/></path>')

    # packets: (path, color, dur, begin, reverse)
    packets = [
        ("e1", CYAN, 1.6, 0, False), ("e1", PINK, 1.6, 0.8, True),
        ("e2", CYAN, 1.4, 0.3, False), ("e2", PINK, 1.4, 1.0, True),
        ("e3", CYAN, 1.8, 0.6, False), ("e4", CYAN, 1.8, 1.2, False),
        ("e3", PINK, 1.8, 1.5, True), ("e4", PINK, 1.8, 0.2, True),
        ("e5", CYAN, 1.5, 0.9, False), ("e6", CYAN, 1.5, 0.4, False),
        ("e7", CYAN, 1.5, 1.3, False), ("e8", CYAN, 1.5, 0.7, False),
        ("e6", PINK, 1.5, 1.6, True), ("e7", PINK, 1.5, 0.1, True),
    ]
    for p, c, dur, beg, rev in packets:
        kp = ' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if rev else ''
        b.append(f'<circle r="4" fill="{c}" filter="url(#glow)"><animateMotion dur="{dur}s" begin="{beg}s" repeatCount="indefinite"{kp}>'
                 f'<mpath xlink:href="#{p}"/></animateMotion></circle>')

    # cloud
    b.append(f'<path d="M862 72 H938 A15 15 0 0 0 934 44 A21 21 0 0 0 896 34 A17 17 0 0 0 866 46 A13 13 0 0 0 862 72 Z" fill="{PANEL}" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>')
    b.append(f'<text x="900" y="63" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TEXT}">INTERNET</text>')

    def node(cx, cy, w, h, label, color, leds=4, sub=None):
        x, y = cx - w/2, cy - h/2
        s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{PANEL}" stroke="{color}" stroke-width="2" filter="url(#glow)"/>']
        s.append(f'<text x="{x + 12}" y="{cy + 4}" font-family="{MONO}" font-size="12" font-weight="bold" fill="{TEXT}">{label}</text>')
        for i in range(leds):
            lx = x + w - 12 - i * 9
            d = 0.6 + (i * 0.37 + cx * 0.001) % 0.9
            s.append(f'<circle cx="{lx:.0f}" cy="{cy}" r="2.5" fill="{CYAN if i % 2 else PINK}">'
                     f'<animate attributeName="opacity" values="1;0.15;1" dur="{d:.2f}s" repeatCount="indefinite"/></circle>')
        if sub:
            s.append(f'<text x="{cx}" y="{y - 6}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{DIM}">{sub}</text>')
        return "".join(s)

    b.append(node(900, 135, 150, 40, "FORTIGATE", PINK, 3))
    b.append(node(900, 215, 150, 40, "CORE-L3", PURPLE, 4))
    b.append(node(770, 290, 120, 36, "ACC-SW1", CYAN, 3))
    b.append(node(1030, 290, 120, 36, "ACC-SW2", CYAN, 3))
    b.append(f'<text x="985" y="179" font-family="{MONO}" font-size="11" fill="{LILAC}">OSPF AREA 0</text>')
    b.append(f'<text x="985" y="102" font-family="{MONO}" font-size="11" fill="{PINK}">POLICY / NAT / VPN</text>')
    b.append(f'<text x="770" y="262" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{DIM}">VLAN 10 · 20</text>')
    b.append(f'<text x="1030" y="262" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{DIM}">VLAN 30 · 40</text>')
    b.append(f'<text x="680" y="230" font-family="{MONO}" font-size="11" fill="{LILAC}">802.1Q TRUNK</text>')

    for i, px in enumerate((700, 840, 960, 1100)):
        b.append(f'<rect x="{px-18}" y="348" width="36" height="22" rx="3" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.5"/>'
                 f'<rect x="{px-13}" y="352" width="26" height="14" fill="{CYAN}" opacity="0.25"><animate attributeName="opacity" values="0.15;0.5;0.15" dur="{2 + i*0.4}s" repeatCount="indefinite"/></rect>'
                 f'<path d="M{px} 370 V377 M{px-9} 378 H{px+9}" stroke="{CYAN}" stroke-width="1.5"/>')

    # neon frame
    b.append('</g>')
    b.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="url(#neon)" stroke-width="2" opacity="0.9"/>')
    write("banner.svg", svg(W, H, "\n".join(b), "Fikret Emre Sınmaz — Computer Engineer | Network & Security"))

# ---------------------------------------------------------------- terminal
def terminal():
    P = ("FIKRET-EMRE", CYAN)
    K, V, C, T = PINK, LILAC, DIM, TEXT
    lines = [
        ("cmd", [("FIKRET-EMRE> ", CYAN), ("enable", T)]),
        ("cmd", [("FIKRET-EMRE# ", CYAN), ("show running-config", T)]),
        ("out", [("hostname ", K), ("FIKRET-EMRE", V)]),
        ("out", [("!", C)]),
        ("out", [("interface ", K), ("Profile0/0", V)]),
        ("out", [(" description ", K), ("Computer Engineer | Network & Security", T)]),
        ("out", [(" education ", K), ("Necmettin Erbakan University - Computer Eng.", T)]),
        ("out", [(" no shutdown", K)]),
        ("out", [("!", C)]),
        ("out", [("interface ", K), ("Learning0/1", V)]),
        ("out", [(" description ", K), ("FortiGate | Cisco IOS | OSPF | VLAN/DTP/VTP | ACL", T)]),
        ("out", [(" projects ", K), ("SynCore  ParkGuard  SybilShield  phevy_dpi", T)]),
        ("out", [("!", C)]),
        ("out", [("router ospf ", K), ("1", V)]),
        ("out", [(" network ", K), ("curiosity 0.0.0.0 ", T), ("area ", K), ("0", V)]),
        ("out", [("!", C)]),
        ("out", [("access-list ", K), ("100 ", V), ("permit ", CYAN), ("tcp any host ", T), ("knowledge ", V), ("eq 443", T)]),
        ("out", [("access-list ", K), ("100 ", V), ("deny   ", PINK), ("ip  any host ", T), ("giving-up", V)]),
        ("cmd", [("FIKRET-EMRE# ", CYAN)]),
    ]
    W = 900
    top, step, fs, cw = 74, 22, 15, 8.6
    H = top + step * len(lines) + 20
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="url(#neon)" stroke-width="2"/>',
         f'<path d="M15 1 H{W-15} A14 14 0 0 1 {W-1} 15 V38 H1 V15 A14 14 0 0 1 15 1 Z" fill="{PANEL}"/>',
         f'<line x1="1" y1="38" x2="{W-1}" y2="38" stroke="{PURPLE}" stroke-opacity="0.4"/>']
    for i, c in enumerate((PINK, PURPLE, CYAN)):
        b.append(f'<circle cx="{24 + i*20}" cy="20" r="6" fill="{c}"/>')
    b.append(f'<text x="{W/2}" y="24" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{DIM}">admin@phevyy: ~ — ssh 10.0.0.1</text>')

    # pass 1: compute timeline (start, end, [(time,width)...]) per line
    t = 0.6
    plan = []
    for i, (kind, toks) in enumerate(lines):
        text = "".join(s for s, _ in toks)
        w_full = len(text) * cw + 6
        if kind == "cmd":
            pl = len(toks[0][0])
            typed = len(text) - pl
            steps = [(t, pl * cw)] + [(t + 0.3 + k * 0.07, (pl + k) * cw + 6) for k in range(1, typed + 1)]
            t = steps[-1][0] + 0.45
        else:
            steps = [(t, 0), (t + 0.18, w_full)]
            t += 0.12
        plan.append(steps)
    L = t + 6.0
    defs, body = [], []
    for i, (kind, toks) in enumerate(lines):
        y = top + i * step
        text = "".join(s for s, _ in toks)
        st = plan[i]
        if kind == "cmd":
            kt = [0.0] + [a / L for a, _ in st] + [1.0]
            vals = [0.0] + [w for _, w in st] + [st[-1][1]]
            mode = 'calcMode="discrete" '
            # discrete: drop the trailing duplicate keyTime 1
            kt, vals = kt[:-1], vals[:-1]
        else:
            (a, _), (b2, w) = st
            kt = [0, a / L, b2 / L, 1]
            vals = [0, 0, w, w]
            mode = ''
        anim = (f'<animate attributeName="width" {mode}values="{";".join(f"{v:.1f}" for v in vals)}" '
                f'keyTimes="{";".join(f"{k:.4f}" for k in kt)}" dur="{L:.1f}s" repeatCount="indefinite"/>')
        cid = f"c{i}"
        defs.append(f'<clipPath id="{cid}"><rect x="24" y="{y - 17}" width="0" height="{step}">{anim}</rect></clipPath>')
        spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in toks)
        body.append(f'<text x="24" y="{y}" font-family="{MONO}" font-size="{fs}" xml:space="preserve" clip-path="url(#{cid})">{spans}</text>')
        if i == len(lines) - 1:
            cx = 24 + len(text) * cw + 2
            on = st[-1][0] / L
            ks, vs = ["0", f"{on:.4f}"], ["0", "1"]
            tt = st[-1][0] + 0.5; v = 0
            while tt < L - 0.01:
                ks.append(f"{tt / L:.4f}"); vs.append(str(v)); v ^= 1; tt += 0.5
            body.append(f'<rect x="{cx:.1f}" y="{y - 14}" width="9" height="18" fill="{CYAN}" opacity="0">'
                        f'<animate attributeName="opacity" calcMode="discrete" values="{";".join(vs)}" keyTimes="{";".join(ks)}" dur="{L:.1f}s" repeatCount="indefinite"/></rect>')
    b.append('<defs>' + "".join(defs) + '</defs>')
    b += body
    out = svg(W, H, chr(10).join(b), "show running-config — About Fikret Emre")
    write("terminal.svg", out)

# ---------------------------------------------------------------- project cards
def card(fname, name, tag, desc_lines, techs, accent):
    W, H = 440, 180
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="#2a1650" stroke-width="2"/>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="none" stroke="url(#neonStatic)" stroke-width="2.5" pathLength="100" stroke-dasharray="22 78" filter="url(#glow)">'
         f'<animate attributeName="stroke-dashoffset" values="100;0" dur="5s" repeatCount="indefinite"/></rect>',
         f'<circle cx="34" cy="42" r="7" fill="{accent}" filter="url(#glow)"><animate attributeName="r" values="6;8;6" dur="2s" repeatCount="indefinite"/></circle>',
         f'<text x="52" y="50" font-family="{SANS}" font-size="24" font-weight="800" fill="url(#neon)">{esc(name)}</text>']
    tw = len(tag) * 7 + 18
    b.append(f'<rect x="{W - 24 - tw}" y="28" width="{tw}" height="24" rx="12" fill="{accent}" fill-opacity="0.12" stroke="{accent}"/>'
             f'<text x="{W - 24 - tw/2}" y="44" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{accent}">{esc(tag)}</text>')
    for i, l in enumerate(desc_lines):
        b.append(f'<text x="26" y="{86 + i*21}" font-family="{SANS}" font-size="14.5" fill="{TEXT}">{esc(l)}</text>')
    x = 26
    cols = [PINK, PURPLE, CYAN, LILAC]
    for i, tch in enumerate(techs):
        c = cols[i % 4]
        b.append(f'<circle cx="{x + 5}" cy="155" r="5" fill="{c}"/><text x="{x + 15}" y="160" font-family="{MONO}" font-size="12.5" fill="{TEXT}">{esc(tch)}</text>')
        x += 15 + len(tch) * 7.4 + 18
    write(fname, svg(W, H, "\n".join(b), f"{name} — project"))

# ---------------------------------------------------------------- roadmap
def roadmap():
    W, H = 900, 210
    nodes = [
        ("SWITCHING", "VLAN · DTP · VTP · STP", "LAB", CYAN),
        ("ROUTING", "OSPF · Inter-VLAN", "LAB", CYAN),
        ("SECURITY", "ACL · NAT", "LAB", CYAN),
        ("FORTIGATE", "Policy · VPN · SD-WAN", "NOW", PINK),
        ("NSE 4", "FCP FortiGate Admin", "NEXT", PURPLE),
    ]
    xs = [90 + i * 180 for i in range(5)]
    y = 70
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{BG}" stroke="#2a1650" stroke-width="2"/>',
         f'<path id="track" d="M{xs[0]} {y} H{xs[-1]}" stroke="{PURPLE}" stroke-opacity="0.35" stroke-width="4" fill="none"/>',
         f'<path d="M{xs[0]} {y} H{xs[-1]}" stroke="url(#neonStatic)" stroke-width="4" fill="none" stroke-dasharray="{xs[-1]-xs[0]}" stroke-dashoffset="{xs[-1]-xs[0]}">'
         f'<animate attributeName="stroke-dashoffset" values="{xs[-1]-xs[0]};0;0" keyTimes="0;0.7;1" dur="5s" repeatCount="indefinite"/></path>',
         f'<circle r="6" fill="#fff" filter="url(#softglow)"><animateMotion dur="5s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.7;1" calcMode="linear"><mpath xlink:href="#track"/></animateMotion></circle>']
    for (title, sub, status, c), x in zip(nodes, xs):
        if status == "NOW":
            for d in (0, 1):
                b.append(f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{c}" stroke-width="2">'
                         f'<animate attributeName="r" values="14;34" dur="2s" begin="{d}s" repeatCount="indefinite"/>'
                         f'<animate attributeName="opacity" values="1;0" dur="2s" begin="{d}s" repeatCount="indefinite"/></circle>')
        b.append(f'<circle cx="{x}" cy="{y}" r="14" fill="{PANEL}" stroke="{c}" stroke-width="3" filter="url(#glow)"/>'
                 f'<circle cx="{x}" cy="{y}" r="5" fill="{c}"/>')
        b.append(f'<text x="{x}" y="{y + 50}" text-anchor="middle" font-family="{SANS}" font-size="16" font-weight="800" fill="{TEXT}">{title}</text>')
        b.append(f'<text x="{x}" y="{y + 72}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{LILAC}">{esc(sub)}</text>')
        sw = len(status) * 8 + 22
        b.append(f'<rect x="{x - sw/2}" y="{y + 86}" width="{sw}" height="22" rx="11" fill="{c}" fill-opacity="0.15" stroke="{c}"/>'
                 f'<text x="{x}" y="{y + 101}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="bold" fill="{c}">{status}</text>')
    write("roadmap.svg", svg(W, H, "\n".join(b), "Network learning path"))


# ---------------------------------------------------------------- certifications
FORTINET = ("M0 9.785h6.788v4.454H0zm8.666-6.33h6.668v4.453H8.666zm0 12.637h6.668v4.454H8.666zm8.522-6.307H24v4.454h-6.812zM2.792 3.455"
            "C1.372 3.814.265 5.404 0 7.425v.506h6.788V3.454zM0 16.091v.554c.24 1.926 1.276 3.466 2.624 3.9h4.188v-4.454zm24-8.184v-.506"
            "c-.265-1.998-1.372-3.587-2.792-3.972h-4.02v4.454H24zM21.376 20.57c1.324-.458 2.36-1.974 2.624-3.9v-.554h-6.812v4.454Z")

def certs():
    items = [
        (["Introduction to Next", "Generation Firewall"], ["Fortinet Training Institute", "Course v1.0"], "NOV 2026", False),
        (["FortiGate 7.6", "Operator"], ["Fortinet Training Institute", "Self-Paced"], "NOV 2026", False),
        (["FortiGate 101", "Fast Track"], ["Deploying Security Strategies", "for the Modern Network", "Ingram Micro · 4h ISC2 CPE"], "NOV 2026", False),
        (["NSE 4", "FortiGate Admin"], ["FCP - FortiGate Administrator", "Fortinet Certified", "Professional"], "UP NEXT", True),
    ]
    cw, ch, gap, m = 232, 240, 12, 18
    W, H = m * 2 + cw * 4 + gap * 3, ch + 30
    b = []
    for i, (title, sub, date, nxt) in enumerate(items):
        x, y = m + i * (cw + gap), 15
        accent = PINK if nxt else CYAN
        b.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="14" fill="{BG}" stroke="#2a1650" stroke-width="2"/>')
        if nxt:
            b.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="14" fill="none" stroke="{PINK}" stroke-width="2" stroke-dasharray="8 8">'
                     f'<animate attributeName="stroke-dashoffset" values="32;0" dur="1.5s" repeatCount="indefinite"/></rect>')
        else:
            b.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="14" fill="none" stroke="url(#neonStatic)" stroke-width="2.5" pathLength="100" stroke-dasharray="20 80" filter="url(#glow)">'
                     f'<animate attributeName="stroke-dashoffset" values="100;0" dur="5s" begin="{i*0.8}s" repeatCount="indefinite"/></rect>')
        b.append(f'<g transform="translate({x + 18} {y + 18}) scale(1.15)" filter="url(#glow)"><path d="{FORTINET}" fill="{accent}"/></g>')
        b.append(f'<text x="{x + 54}" y="{y + 30}" font-family="{MONO}" font-size="10.5" fill="{DIM}">FORTINET</text>')
        b.append(f'<text x="{x + 54}" y="{y + 44}" font-family="{MONO}" font-size="10.5" fill="{DIM}">TRAINING INSTITUTE</text>')
        for k, t in enumerate(title):
            b.append(f'<text x="{x + 18}" y="{y + 84 + k*22}" font-family="{SANS}" font-size="18" font-weight="800" fill="url(#neon)">{esc(t)}</text>')
        for k, t in enumerate(sub):
            b.append(f'<text x="{x + 18}" y="{y + 134 + k*17}" font-family="{MONO}" font-size="11.5" fill="{LILAC}">{esc(t)}</text>')
        b.append(f'<text x="{x + 18}" y="{y + 197}" font-family="{MONO}" font-size="11" fill="{DIM}">{date}</text>')
        label = "◎ NEXT GOAL" if nxt else "✓ COMPLETED"
        lw = len(label) * 7.2 + 20
        b.append(f'<rect x="{x + cw - 18 - lw}" y="{y + 182}" width="{lw:.0f}" height="24" rx="12" fill="{accent}" fill-opacity="0.12" stroke="{accent}">'
                 f'<animate attributeName="fill-opacity" values="0.08;0.3;0.08" dur="2.5s" begin="{i*0.4}s" repeatCount="indefinite"/></rect>'
                 f'<text x="{x + cw - 18 - lw/2:.0f}" y="{y + 198}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="bold" fill="{accent}">{label}</text>')
    write("certs.svg", svg(W, H, "\n".join(b), "Fortinet training: Introduction to NGFW, FortiGate 7.6 Operator, FortiGate 101 Fast Track. Next: NSE 4"))

# ---------------------------------------------------------------- mini cards (more network projects)
def mini_card(fname, name, tag, desc_lines, techs, accent):
    W, H = 440, 130
    b = [f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{BG}" stroke="#2a1650" stroke-width="2"/>',
         f'<rect x="1" y="1" width="4" height="{H-2}" rx="2" fill="{accent}" filter="url(#glow)">'
         f'<animate attributeName="opacity" values="0.5;1;0.5" dur="2.4s" repeatCount="indefinite"/></rect>',
         f'<text x="22" y="34" font-family="{MONO}" font-size="17" font-weight="bold" fill="{TEXT}"><tspan fill="{accent}">~/</tspan>{esc(name)}</text>']
    tw = len(tag) * 7 + 18
    b.append(f'<rect x="{W - 18 - tw}" y="16" width="{tw}" height="22" rx="11" fill="{accent}" fill-opacity="0.12" stroke="{accent}"/>'
             f'<text x="{W - 18 - tw/2}" y="31" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{accent}">{esc(tag)}</text>')
    for i, l in enumerate(desc_lines):
        b.append(f'<text x="22" y="{62 + i*19}" font-family="{SANS}" font-size="13.5" fill="{TEXT}">{esc(l)}</text>')
    x = 22
    cols = [PINK, PURPLE, CYAN, LILAC]
    for i, tch in enumerate(techs):
        c = cols[i % 4]
        b.append(f'<circle cx="{x + 4}" cy="109" r="4" fill="{c}"/><text x="{x + 13}" y="113" font-family="{MONO}" font-size="11.5" fill="{DIM}">{esc(tch)}</text>')
        x += 13 + len(tch) * 6.9 + 16
    write(fname, svg(W, H, "\n".join(b), f"{name} — project"))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        OUT = sys.argv[1]
    banner()
    terminal()
    certs()
    card("card-syncore.svg", "SynCore", "SECURITY",
         ["Offline-first password vault for Windows with", "QR-based 2FA — the Android app is the", "authenticator that unlocks the vault."],
         ["Python", "PyQt6", "Flutter"], PINK)
    card("card-parkguard.svg", "ParkGuard", "AI / VISION",
         ["Autonomous robot that patrols a parking lot,", "spots cars in disabled spaces and checks", "their plates with YOLO11."],
         ["Python", "PyTorch", "YOLO11", "Pygame"], CYAN)
    card("card-sybilshield.svg", "SybilShield", "NETWORK SEC",
         ["Simulates Sybil attacks on wireless sensor", "networks and detects fake identities with", "RSSI-based clustering."],
         ["Python", "WSN", "Clustering"], PURPLE)
    card("card-phevy-dpi.svg", "phevy_dpi", "NETWORKING",
         ["ISP-agnostic DPI bypass for Discord on", "Windows — not a VPN, no added ping.", ""],
         ["Windows", "DPI", "Networking"], PINK)
    roadmap()
    mini_card("mini-private-vpn.svg", "Private-VPN", "VPN",
              ["OpenVPN client manager with auto-reconnect", "and AES-256-GCM authenticated encryption."],
              ["Python", "OpenVPN", "AES-GCM"], PINK)
    mini_card("mini-tcp-udp.svg", "TCP-UDP", "SOCKETS",
              ["TCP & UDP client/server sockets with", "CRC32 checksum integrity verification."],
              ["Python", "TCP/UDP", "CRC32"], CYAN)
    mini_card("mini-ftp-esp32.svg", "FTP-ServerwEsp32", "WIRELESS",
              ["ESP32 as a SoftAP + FTP server, serving", "files from an SD card — no router needed."],
              ["C++", "ESP32", "FTP", "SoftAP"], PURPLE)
    mini_card("mini-iamu.svg", "Ambient-Monitoring-Unit", "IoT",
              ["ESP32 sensor hub with a web dashboard,", "REST API and relay control over WiFi."],
              ["C++", "ESP32", "REST", "DHT22"], PINK)
    print("ok")
