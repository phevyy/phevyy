"""Builds 1280x640 social preview images (repo Settings -> Social preview).

Usage:  python scripts/social_previews.py <out_dir>
Writes <name>.svg files; render them to PNG with a headless browser, e.g.
  chrome --headless=new --window-size=1280,640 --screenshot=out.png file:///.../name.svg
"""
import os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_assets as g
from generate_assets import BG, PANEL, PURPLE, PINK, CYAN, LILAC, TEXT, DIM, SANS, MONO, svg, write
from xml.sax.saxutils import escape as esc

W, H = 1280, 640


def frame(name, tagline, chips, art, name_size=88):
    b = [f'''<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{PURPLE}" stroke-opacity="0.10"/></pattern>
  <radialGradient id="gl" cx="0.1" cy="0.2" r="0.7"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0.35"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gr" cx="0.78" cy="0.55" r="0.45"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.16"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
</defs>''',
         f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#gl)"/><rect width="{W}" height="{H}" fill="url(#gr)"/>',
         f'<rect x="12" y="12" width="{W-24}" height="{H-24}" rx="22" fill="none" stroke="url(#neonStatic)" stroke-width="3"/>',
         f'<text x="80" y="130" font-family="{MONO}" font-size="24" fill="{CYAN}">github.com/phevyy/</text>',
         f'<text x="76" y="240" font-family="{SANS}" font-size="{name_size}" font-weight="800" fill="url(#neonStatic)" filter="url(#glow)">{esc(name)}</text>']
    for i, l in enumerate(tagline):
        b.append(f'<text x="80" y="{315 + i*42}" font-family="{SANS}" font-size="30" fill="{TEXT}">{esc(l)}</text>')
    x = 80
    cols = [PINK, PURPLE, CYAN, LILAC]
    for i, c in enumerate(chips):
        w = len(c) * 12 + 36
        col = cols[i % 4]
        b.append(f'<rect x="{x}" y="440" width="{w}" height="44" rx="22" fill="{col}" fill-opacity="0.14" stroke="{col}" stroke-width="2"/>'
                 f'<text x="{x + w/2}" y="469" text-anchor="middle" font-family="{MONO}" font-size="20" fill="{TEXT}">{esc(c)}</text>')
        x += w + 14
    b.append(f'<text x="80" y="570" font-family="{MONO}" font-size="20" fill="{DIM}">Fikret Emre Sınmaz · Network &amp; Security</text>')
    b.append(art)
    return "\n".join(b)


def art_syncore():
    rnd = random.Random(7)
    a = [f'<rect x="790" y="150" width="300" height="320" rx="26" fill="{PANEL}" stroke="{PURPLE}" stroke-width="4" filter="url(#glow)"/>',
         f'<circle cx="940" cy="290" r="78" fill="none" stroke="{PINK}" stroke-width="6" filter="url(#glow)"/>',
         f'<circle cx="940" cy="290" r="54" fill="none" stroke="{PURPLE}" stroke-width="3" stroke-dasharray="10 8"/>']
    for k in range(8):
        a.append(f'<line x1="940" y1="290" x2="940" y2="222" stroke="{PINK}" stroke-width="4" transform="rotate({k*45} 940 290)" stroke-opacity="0.5"/>')
    a.append(f'<circle cx="940" cy="290" r="20" fill="{PINK}" filter="url(#glow)"/>')
    a.append(f'<text x="940" y="420" text-anchor="middle" font-family="{MONO}" font-size="20" fill="{LILAC}">VAULT · LOCKED</text>')
    # phone with QR
    a.append(f'<rect x="1040" y="250" width="150" height="270" rx="22" fill="{BG}" stroke="{CYAN}" stroke-width="4" filter="url(#glow)"/>')
    qx, qy, cs = 1065, 300, 10
    for i in range(10):
        for j in range(10):
            corner = (i < 3 and j < 3) or (i > 6 and j < 3) or (i < 3 and j > 6)
            if corner or rnd.random() < 0.45:
                a.append(f'<rect x="{qx + i*cs}" y="{qy + j*cs}" width="{cs-1}" height="{cs-1}" fill="{CYAN}"/>')
    a.append(f'<text x="1115" y="440" text-anchor="middle" font-family="{MONO}" font-size="16" fill="{CYAN}">2FA · SCAN</text>')
    a.append(f'<line x1="1050" y1="350" x2="1180" y2="350" stroke="{PINK}" stroke-width="3" filter="url(#glow)"/>')
    return "\n".join(a)


def art_parkguard():
    a = []
    for i in range(5):
        x = 760 + i * 92
        a.append(f'<path d="M{x} 150 V330" stroke="{TEXT}" stroke-opacity="0.5" stroke-width="3"/>')
    a.append(f'<path d="M1220 150 V330" stroke="{TEXT}" stroke-opacity="0.5" stroke-width="3"/>')
    a.append(f'<rect x="1036" y="150" width="92" height="180" fill="{PINK}" fill-opacity="0.08"/>')
    a.append(f'<text x="1082" y="322" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="bold" fill="{PINK}">DISABLED</text>')
    for i in (0, 2, 3):
        x = 760 + i * 92 + 14
        a.append(f'<rect x="{x}" y="185" width="64" height="110" rx="14" fill="{PANEL}" stroke="{PURPLE}" stroke-width="3"/>'
                 f'<rect x="{x+8}" y="205" width="48" height="26" rx="6" fill="{PURPLE}" fill-opacity="0.4"/>')
    # offending car in disabled spot
    a.append(f'<rect x="1050" y="175" width="64" height="110" rx="14" fill="{PANEL}" stroke="{PINK}" stroke-width="3"/>'
             f'<rect x="1058" y="195" width="48" height="26" rx="6" fill="{PINK}" fill-opacity="0.4"/>')
    a.append(f'<rect x="1040" y="165" width="84" height="130" fill="none" stroke="{CYAN}" stroke-width="3" stroke-dasharray="10 6" filter="url(#glow)"/>')
    a.append(f'<rect x="1040" y="137" width="178" height="28" fill="{CYAN}"/><text x="1048" y="157" font-family="{MONO}" font-size="16" font-weight="bold" fill="{BG}">UNAUTHORIZED 0.94</text>')
    # robot with scan cone
    a.append(f'<path d="M900 470 L1050 300 L1130 330 Z" fill="{CYAN}" fill-opacity="0.12"/>')
    a.append(f'<circle cx="900" cy="470" r="34" fill="{PANEL}" stroke="{CYAN}" stroke-width="4" filter="url(#glow)"/>'
             f'<circle cx="900" cy="470" r="10" fill="{CYAN}"/>')
    a.append(f'<path d="M780 520 H1200" stroke="{PURPLE}" stroke-width="3" stroke-dasharray="14 12"/>')
    a.append(f'<text x="990" y="555" text-anchor="middle" font-family="{MONO}" font-size="18" fill="{LILAC}">PATROL ROUTE · YOLO11</text>')
    return "\n".join(a)


def art_sybil():
    rnd = random.Random(3)
    honest = [(rnd.randint(760, 1200), rnd.randint(150, 520)) for _ in range(16)]
    honest = [(x, y) for x, y in honest if not (1000 < x < 1140 and 260 < y < 420)]
    sybil_c = (1070, 340)
    sybil = [(sybil_c[0] + rnd.randint(-45, 45), sybil_c[1] + rnd.randint(-45, 45)) for _ in range(6)]
    a = []
    for i, p in enumerate(honest):
        for q in honest[i+1:]:
            if (p[0]-q[0])**2 + (p[1]-q[1])**2 < 140**2:
                a.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="{CYAN}" stroke-opacity="0.3" stroke-width="2"/>')
    for p in sybil:
        for q in honest:
            if (p[0]-q[0])**2 + (p[1]-q[1])**2 < 170**2:
                a.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="{PINK}" stroke-opacity="0.25" stroke-width="2"/>')
    for r in (40, 70, 100):
        a.append(f'<circle cx="{sybil_c[0]}" cy="{sybil_c[1]}" r="{r}" fill="none" stroke="{PINK}" stroke-opacity="{0.6 - r/250:.2f}" stroke-width="2"/>')
    a.append(f'<circle cx="{sybil_c[0]}" cy="{sybil_c[1]}" r="80" fill="{PINK}" fill-opacity="0.06" stroke="{PINK}" stroke-width="3" stroke-dasharray="10 8" filter="url(#glow)"/>')
    for x, y in honest:
        a.append(f'<circle cx="{x}" cy="{y}" r="11" fill="{PANEL}" stroke="{CYAN}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="4" fill="{CYAN}"/>')
    for x, y in sybil:
        a.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{PINK}" filter="url(#glow)"/>')
    a.append(f'<rect x="1000" y="438" width="160" height="30" fill="{PINK}"/><text x="1080" y="459" text-anchor="middle" font-family="{MONO}" font-size="16" font-weight="bold" fill="{BG}">SYBIL CLUSTER</text>')
    a.append(f'<text x="770" y="580" font-family="{MONO}" font-size="18" fill="{LILAC}">RSSI CLUSTERING · WSN</text>')
    return "\n".join(a)


def art_dpi():
    a = [f'<rect x="960" y="130" width="40" height="370" rx="8" fill="{PANEL}" stroke="{PINK}" stroke-width="4" filter="url(#glow)"/>',
         f'<text x="980" y="115" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="bold" fill="{PINK}">DPI</text>']
    for k in range(5):
        a.append(f'<line x1="966" y1="{160 + k*70}" x2="994" y2="{160 + k*70}" stroke="{PINK}" stroke-width="3" stroke-opacity="0.6"/>')
    rows = [200, 280, 360, 440]
    for i, y in enumerate(rows):
        # whole packets before the wall
        for j in range(2):
            x = 760 + j * 90
            a.append(f'<rect x="{x}" y="{y - 18}" width="70" height="36" rx="8" fill="{PURPLE}" fill-opacity="0.3" stroke="{PURPLE}" stroke-width="2"/>')
        # fragmented packets after the wall
        for j in range(3):
            x = 1030 + j * 60 + (i % 2) * 12
            a.append(f'<rect x="{x}" y="{y - 14}" width="34" height="28" rx="6" fill="{CYAN}" fill-opacity="0.3" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>')
        a.append(f'<path d="M740 {y} H1220" stroke="{TEXT}" stroke-opacity="0.12" stroke-width="2"/>')
    a.append(f'<text x="760" y="560" font-family="{MONO}" font-size="18" fill="{LILAC}">not a VPN · no added ping</text>')
    a.append(f'<text x="1060" y="560" font-family="{MONO}" font-size="18" fill="{CYAN}">→ DISCORD ✓</text>')
    return "\n".join(a)


if __name__ == "__main__":
    g.OUT = sys.argv[1] if len(sys.argv) > 1 else "social-previews"
    items = [
        ("syncore", "SynCore", ["Offline-first password vault", "with QR-based 2FA"], ["Python", "PyQt6", "Flutter"], art_syncore()),
        ("parkguard", "ParkGuard", ["Autonomous parking-lot patrol", "with YOLO11 plate checks"], ["Python", "PyTorch", "YOLO11"], art_parkguard()),
        ("sybilshield", "SybilShield", ["Sybil attack detection for", "wireless sensor networks"], ["Python", "WSN", "RSSI"], art_sybil()),
        ("phevy_dpi", "phevy_dpi", ["ISP-agnostic DPI bypass", "for Discord on Windows"], ["Windows", "DPI", "Networking"], art_dpi()),
    ]
    for fname, name, tag, chips, art in items:
        write(f"{fname}.svg", svg(W, H, frame(name, tag, chips, art, 80 if len(name) > 10 else 88), f"{name} social preview"))
    print("ok")
