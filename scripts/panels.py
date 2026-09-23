#!/usr/bin/env python3
"""Render the static profile panels: hero, processes, stack, agents, footer.

Needs Pillow (only to rasterize the name mask). Writes SVGs to the repo root.
"""
import math
import pathlib
import random

from PIL import Image, ImageDraw, ImageFont

from kit import INK, MONO, PAD, RED, W, close_panel, esc, loop_css, meta, open_panel

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME_FONT = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"

BIO = [
    'I told claude, "Make me a 100x dev, make no mistakes."',
    "Now I'm here. Hate the word taste nowadays but I think I have it sometimes.",
]
DOING = [
    "Wiring multi-agent workflows",
    "Building internal tooling that operators rely on",
    "Agentic harness development scoped specifically for health insurance sales pipelines",
]
STACK = [
    ("languages", ["typescript", "javascript", "python", "rust"], ""),
    ("libraries", ["effect"], "# <3"),
    ("frontend", ["react", "next.js", "tailwind", "foldkit"], ""),
    ("mobile", ["flutter"], ""),
    ("cloud", ["gcp", "render", "docker"], ""),
    ("data", ["postgres", "neon", "mysql", "sqlite", "firebase"], ""),
]
AGENTS = ["claude code", "codex", "bb", "pi", "hermes", "opencode", "antigravity"]
LINKEDIN = "in/joshua-cancel-orlando"

GLITCH = "!/\\|_-=+*^?#%$[]{}01"


def flow(x, y, p):
    """Domain-warped waves in cell space; time terms are integer multiples of p so loops close."""
    wx = x + 6 * math.sin(y * 0.33 + p) + 3 * math.sin(x * 0.06 - 2 * p)
    wy = y + 1.6 * math.sin(x * 0.05 - p)
    a = math.sin(wx * 0.15 + wy * 0.34 + p)
    b = math.sin(wx * 0.085 - wy * 0.52 - 2 * p)
    c = math.sin(wx * 0.04 + wy * 0.21 + 3 * p)
    return (a * b + 0.4 * c) * 0.5 + 0.5


def rows(lines, x, y0, lh, length, cls, extra=""):
    return "".join(
        f'<text class="{cls}" x="{x}" y="{y0 + i * lh:.1f}" textLength="{length:.1f}" lengthAdjust="spacing"{extra}>{esc(s)}</text>'
        for i, s in enumerate(lines) if s.strip()
    )


# ---------------------------------------------------------------- hero

def name_mask(text, cols, cw, rh):
    f = ImageFont.truetype(NAME_FONT, 220)
    l, t, r, b = f.getbbox(text)
    im = Image.new("L", (r - l + 20, b - t + 20), 0)
    ImageDraw.Draw(im).text((10 - l, 10 - t), text, font=f, fill=255)
    h = round(im.height * (cols * cw / im.width) / rh)
    small = im.resize((cols, h), Image.LANCZOS)
    m = [[small.getpixel((x, y)) / 255 for x in range(cols)] for y in range(h)]
    return [row for row in m if max(row) > 0.22]


def decode(lines, x, y0, lh, start, cps=90, head=9, seed=7):
    """Type each line in with a glitching head, then hold. Static fallback shows the final text."""
    rnd = random.Random(seed)
    out, css, t = [], [], start
    dt = 3 / cps
    for li, line in enumerate(lines):
        y = y0 + li * lh
        pre = '<tspan class="red">&gt;</tspan> '
        steps = math.ceil(len(line) / 3)
        for k in range(steps):
            done = line[: k * 3]
            noise = "".join(rnd.choice(GLITCH) if ch != " " else " " for ch in line[k * 3: k * 3 + head])
            out.append(f'<text class="bio dz" x="{x}" y="{y}" style="animation-delay:{t + k * dt:.3f}s">'
                       f'{pre}{esc(done)}<tspan opacity="0.45">{esc(noise)}</tspan></text>')
        t += steps * dt
        out.append(f'<text class="bio df" x="{x}" y="{y}" style="animation-delay:{t:.3f}s">{pre}{esc(line)}</text>')
        t += 0.25
    css.append(f"  .dz {{ opacity: 0; animation: dz {dt:.3f}s step-end 1; }}")
    css.append("  @keyframes dz { 0%, 100% { opacity: 1; } }")
    css.append("  .df { animation: df 0.001s step-end 1 both; }")
    css.append("  @keyframes df { 0% { opacity: 0; } 100% { opacity: 1; } }")
    return "".join(out), "\n".join(css), t


def hero():
    C, R, F, PERIOD = 150, 22, 12, 3.6
    cw, rh = (W - 2 * PAD) / C, 9.8
    fs = cw / 0.6
    name = name_mask("DEMONSHINOBI", 128, cw, rh)
    nh, nw = len(name), len(name[0])
    nx, ny = (C - nw) // 2, (R - nh) // 2
    cx, cy = (nx + nw / 2) * cw, (ny + nh / 2) * rh
    top = 60
    H = 372

    frames = []
    for t in range(F):
        p = 2 * math.pi * t / F
        ring = (t / (F * 0.7)) * 480 if t < F * 0.7 else None
        field, glyphs, halo = [], [], []
        for y in range(R):
            fr, gr, hr = [], [], []
            for x in range(C):
                v = flow(x, y, p)
                c = name[y - ny][x - nx] if 0 <= y - ny < nh and 0 <= x - nx < nw else 0
                f = g = h = " "
                if c > 0.22:
                    g = "#%@"[min(2, int((c * 0.7 + v * 0.3) * 3))] if c > 0.55 else ":=+"[min(2, int(c * 4) - 1)]
                else:
                    d = math.hypot((x + .5) * cw - cx, ((y + .5) * rh - cy) * 1.7)
                    dx = max(0, nx - x, x - (nx + nw - 1)) / 5
                    dy = max(0, ny - y, y - (ny + nh - 1)) / 1.3
                    clear = min(1, max(0, math.hypot(dx, dy) - 0.5))
                    edge = min(1, x / 12, (C - 1 - x) / 12, (y + 1) / 3, (R - y) / 3)
                    k = (v * clear * edge - 0.3) / 0.7
                    if ring is not None and abs(d - ring) < 4.5 and clear > 0:
                        h = "+" if d < 220 else ":" if d < 360 else "."
                    elif k > 0:
                        f = " .,-~~=*"[min(7, int(k * 8))]
                fr.append(f)
                gr.append(g)
                hr.append(h)
            field.append("".join(fr))
            glyphs.append("".join(gr))
            halo.append("".join(hr))
        frames.append((field, glyphs, halo))

    y0 = top + rh * 0.8
    L = W - 2 * PAD
    body = []
    for i, (field, glyphs, halo) in enumerate(frames):
        body.append(f'<g class="lq lq{i}">')
        body.append(rows(field, PAD, y0, rh, L, "fd"))
        body.append(rows(glyphs, PAD, y0, rh, L, "nm"))
        body.append(rows(halo, PAD, y0, rh, L, "hl"))
        body.append("</g>")

    bio, bio_css, done = decode(BIO, PAD, top + R * rh + 42, 22, start=0.6)
    last = PAD + (len(BIO[-1]) + 2) * 7.8 + 4
    bio += (f'<g class="df" style="animation-delay:{done:.2f}s"><rect class="cur" x="{last:.1f}" '
            f'y="{top + R * rh + 42 + 22 - 11}" width="8" height="13" fill="{RED}"/></g>')

    style = f"""  .fd {{ font-size: {fs:.2f}px; opacity: 0.34; }}
  .nm {{ font-size: {fs:.2f}px; fill: url(#nameg); }}
  .hl {{ font-size: {fs:.2f}px; fill: {RED}; opacity: 0.75; }}
  .bio {{ font-size: 13px; opacity: 0.92; }}
{loop_css("lq", F, PERIOD)}
{bio_css}"""
    defs = f"""  <linearGradient id="nameg" gradientUnits="userSpaceOnUse" x1="{PAD + nx * cw:.0f}" y1="0" x2="{PAD + (nx + nw) * cw:.0f}" y2="0">
    <stop offset="0" stop-color="{INK}" stop-opacity="0.62"/>
    <stop offset="1" stop-color="{INK}" stop-opacity="1"/>
  </linearGradient>"""
    label = "demonshinobi. " + " ".join(BIO)
    svg = open_panel(H, label, defs, style)
    svg += meta("// DEMONSHINOBI", "AGENTIC DEV // FOUNDER BRAIN")
    svg += "".join(body) + bio + close_panel()
    return svg


# ---------------------------------------------------------------- processes

def processes():
    H = 44 + 30 + len(DOING) * 30 + 26
    sig_w = 10
    body = []
    css = []
    y = 88
    body.append(f'<text class="lab" x="{PAD}" y="{y - 22}">PID</text>')
    body.append(f'<text class="lab" x="{PAD + 52}" y="{y - 22}">COMMAND</text>')
    sx = W - PAD - 100
    body.append(f'<text class="lab" x="{sx}" y="{y - 22}">SIGNAL</text>')
    body.append(f'<text class="lab" x="{W - PAD}" y="{y - 22}" text-anchor="end">STAT</text>')
    for i, cmd in enumerate(DOING):
        yy = y + i * 30
        body.append(f'<text class="pid" x="{PAD}" y="{yy}">{i + 1:03d}</text>')
        body.append(f'<text class="cmd" x="{PAD + 52}" y="{yy}">{esc(cmd)}</text>')
        n, period = sig_w, 2.2 + i * 0.7
        cls = f"s{i}"
        for k in range(n):
            wave = "".join(
                " .:-=+*#"[int((0.5 + 0.5 * math.sin(2 * math.pi * (j + k) / n * (1 + i % 2))
                                * math.sin(2 * math.pi * (j - 2 * k) / n + i)) * 7.99)]
                for j in range(sig_w))
            body.append(f'<text class="sig {cls} {cls}{k}" x="{sx}" y="{yy}" textLength="{sig_w * 7:.0f}" '
                        f'lengthAdjust="spacing">{esc(wave)}</text>')
        css.append(loop_css(cls, n, period))
        body.append(f'<text class="red glow st" x="{W - PAD}" y="{yy}" text-anchor="end">R+</text>')
    style = """  .pid { font-size: 11px; opacity: 0.4; letter-spacing: 1px; }
  .cmd { font-size: 12px; opacity: 0.92; }
  .sig { font-size: 12px; opacity: 0.55; }
  .st { font-size: 12px; letter-spacing: 1px; }
""" + "\n".join(css)
    svg = open_panel(H, "What I'm usually doing: " + "; ".join(DOING), style=style)
    svg += meta("// PS AUX", f"{len(DOING)} RUNNING")
    return svg + "".join(body) + close_panel()


# ---------------------------------------------------------------- stack

def stack():
    lh, fs = 23, 13
    y0 = 78
    H = y0 + (len(STACK) + 1) * lh + 22
    cw = 7.8
    body = []

    def ln(i):
        return f'<text class="gut" x="{PAD}" y="{y0 + i * lh}">{i + 1:02d}</text>'

    x0 = PAD + 34
    body.append(ln(0) + f'<text class="red" x="{x0}" y="{y0}" font-size="{fs}">[stack]</text>')
    keyw = max(len(k) for k, _, _ in STACK)
    for i, (key, vals, comment) in enumerate(STACK, start=1):
        y = y0 + i * lh
        parts = [f'<tspan class="k">{key.ljust(keyw)}</tspan>', '<tspan class="p"> = [ </tspan>']
        for j, v in enumerate(vals):
            if j:
                parts.append('<tspan class="p">, </tspan>')
            parts.append(f'<tspan class="s">"{esc(v)}"</tspan>')
        parts.append('<tspan class="p"> ]</tspan>')
        if comment:
            parts.append(f'<tspan class="red">  {esc(comment)}</tspan>')
        body.append(ln(i) + f'<text x="{x0}" y="{y}" font-size="{fs}">{"".join(parts)}</text>')
    last = len(STACK) + 1
    body.append(ln(last) + f'<rect class="cur" x="{x0}" y="{y0 + last * lh - 11}" width="8" height="14" fill="{RED}"/>')

    # liquid margin, echoing the hero
    C, R, F = 34, 13, 8
    fx, cwf, rhf = W - PAD - 34 * 6.2, 6.2, 11.5
    frames = []
    for t in range(F):
        p = 2 * math.pi * t / F
        lines = []
        for y in range(R):
            s = ""
            for x in range(C):
                k = (flow(x * 1.6, y * 1.2, p) * min(1, x / 7, (C - 1 - x) / 4, (y + 1) / 2.5, (R - y) / 2.5) - 0.38) / 0.62
                s += " .,-~~=*"[min(7, int(k * 8))] if k > 0 else " "
            lines.append(s)
        frames.append(f'<g class="lm lm{t}">' + rows(lines, f"{fx:.1f}", 70, rhf, C * cwf, "lf") + "</g>")
    style = f"""  .gut {{ font-size: 11px; opacity: 0.24; }}
  .k {{ opacity: 0.62; }}
  .p {{ opacity: 0.34; }}
  .s {{ opacity: 1; }}
  .lf {{ font-size: {cwf / 0.6:.2f}px; opacity: 0.3; }}
{loop_css("lm", F, 3.2)}"""
    label = "Stack: " + "; ".join(f"{k}: {', '.join(v)}" for k, v, _ in STACK)
    svg = open_panel(H, label, style=style)
    svg += meta("// STACK.TOML", "")
    return svg + "".join(frames) + "".join(body) + close_panel()


# ---------------------------------------------------------------- agents

def agents():
    H = 300
    cx, cy = W / 2, 168
    rx, ry = 292, 92
    n = len(AGENTS)
    period = 8.4
    slot = period / n
    body, css = [], []
    css.append("  @keyframes zap { 0% { fill: #ff3547; opacity: 1; } 6% { fill: #eef2f8; opacity: 0.22; } 100% { opacity: 0.22; } }")
    css.append("  @keyframes lit { 0% { opacity: 1; } 12% { opacity: 0.55; } 100% { opacity: 0.55; } }")
    css.append(f"  .dt {{ font-size: 11px; opacity: 0.22; animation: zap {period}s linear infinite; }}")
    css.append(f"  .ag {{ font-size: 11px; letter-spacing: 2px; opacity: 0.55; animation: lit {period}s linear infinite; }}")
    for i, a in enumerate(AGENTS):
        ang = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        ex, ey = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
        dist = math.hypot(ex - cx, (ey - cy) * 2.2)
        steps = max(6, int(dist / 12))
        for j in range(2, steps - 1):
            f = j / steps
            px, py = cx + (ex - cx) * f, cy + (ey - cy) * f
            delay = i * slot + j * 0.045 - period
            body.append(f'<text class="dt" x="{px:.1f}" y="{py + 4:.1f}" text-anchor="middle" '
                        f'style="animation-delay:{delay:.3f}s">·</text>')
        anchor = "middle" if abs(math.cos(ang)) < 0.25 else ("start" if math.cos(ang) > 0 else "end")
        lx = ex + (10 if anchor == "start" else -10 if anchor == "end" else 0)
        ly = ey + (4 if anchor != "middle" else (-6 if math.sin(ang) < 0 else 16))
        delay = i * slot + steps * 0.045 - period
        body.append(f'<text class="ag" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
                    f'style="animation-delay:{delay:.3f}s">[ {esc(a.upper())} ]</text>')
    core = []
    frames = ["*", "#", "@", "#"]
    for k, g in enumerate(frames):
        core.append(f'<g class="cr cr{k}"><text class="core" x="{cx}" y="{cy + 5}" text-anchor="middle">'
                    f'<tspan fill-opacity="0.35">[ </tspan><tspan class="red">{g}</tspan>'
                    f'<tspan fill-opacity="0.35"> ]</tspan></text></g>')
    css.append("  .core { font-size: 15px; }")
    css.append(loop_css("cr", len(frames), 1.6))
    svg = open_panel(H, "Agentic tooling: " + ", ".join(AGENTS), style="\n".join(css))
    svg += meta("// AGENTS", f"{n} NODES")
    return svg + "".join(body) + "".join(core) + close_panel()


# ---------------------------------------------------------------- footer

def footer():
    H = 56
    y = 33
    tag = " demonshinobi "
    tw = len(tag) * 7.2 + 6
    style = "  .sb { font-size: 11.5px; letter-spacing: 1px; }\n  .dim { opacity: 0.45; }"
    svg = open_panel(H, f"LinkedIn: {LINKEDIN}", style=style)
    svg += f'<rect x="{PAD - 8}" y="{y - 15}" width="{tw:.0f}" height="21" fill="{RED}"/>'
    svg += f'<text class="sb" x="{PAD - 5}" y="{y}" fill="#05070b" style="fill:#05070b">{tag}</text>'
    svg += f'<text class="sb dim" x="{PAD + tw + 6:.0f}" y="{y}">0:readme*  1:activity  2:ps  3:stack  4:agents</text>'
    svg += (f'<text class="sb" x="{W - PAD}" y="{y}" text-anchor="end">'
            f'<tspan class="dim">linkedin </tspan>{LINKEDIN}<tspan class="red"> -&gt;</tspan></text>')
    return svg + close_panel()


if __name__ == "__main__":
    for name, fn in [("hero", hero), ("ps", processes), ("stack", stack), ("agents", agents), ("footer", footer)]:
        svg = fn()
        (ROOT / f"{name}.svg").write_text(svg)
        print(f"{name}.svg {len(svg):,} bytes")
