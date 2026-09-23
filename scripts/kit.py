"""Shared look for the profile panels: black glass, dot grid, mono ink, one red."""

W = 869
PAD = 44
BG = "#05070b"
INK = "#eef2f8"
RED = "#ff3547"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def open_panel(h, label, defs="", style=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label)}" xml:space="preserve">
<title>{esc(label)}</title>
<defs>
  <pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="0.6" fill="#9fb4d8" opacity="0.10"/>
  </pattern>
  <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="2.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="panel"><rect width="{W}" height="{h}" rx="14"/></clipPath>
{defs}
</defs>
<style>
  text {{ font-family: {MONO}; fill: {INK}; white-space: pre; }}
  .meta {{ font-size: 10px; opacity: 0.55; letter-spacing: 3px; }}
  .lab {{ font-size: 9px; opacity: 0.38; letter-spacing: 2.2px; }}
  .red {{ fill: {RED}; }}
  .glow {{ filter: url(#glow); }}
  .cur {{ animation: blink 1.1s steps(1, end) infinite; }}
  @keyframes blink {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: 0.15; }} }}
{style}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<g clip-path="url(#panel)">
<rect width="{W}" height="{h}" fill="{BG}"/><rect width="{W}" height="{h}" fill="url(#dots)"/>
"""


def close_panel():
    return "</g></svg>\n"


def meta(left, right="", y=38):
    out = f'<text class="meta" x="{PAD}" y="{y}">{esc(left)}</text>'
    if right:
        out += f'<text class="meta" x="{W - PAD}" y="{y}" text-anchor="end">{esc(right)}</text>'
    return out


def loop_css(cls, n, period):
    """Flipbook: n frames with classes {cls}0..{cls}{n-1}, each shown for period/n.

    Frame 0 is the static fallback (no animation / reduced motion)."""
    step = 100 / n
    css = [
        f"  .{cls} {{ opacity: 0; animation: {cls} {period}s step-end infinite; }}",
        f"  .{cls}0 {{ opacity: 1; }}",
        f"  @keyframes {cls} {{ 0% {{ opacity: 1; }} {step:.4f}% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}",
    ]
    for i in range(n):
        css.append(f"  .{cls}{i} {{ animation-delay: {i * period / n - period:.4f}s; }}")
    return "\n".join(css)
