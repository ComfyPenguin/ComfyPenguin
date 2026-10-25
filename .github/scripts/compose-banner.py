"""Compose the banner and the lowlighter/metrics renders into one SVG.

usage: compose-banner.py <banner.svg> <metrics-dir>

Each SVG is embedded as a data: image, so its CSS stays isolated and the result
still renders inside a GitHub README <img> (no external resources).
"""
import base64
import re
import sys
from pathlib import Path

banner, out = Path(sys.argv[1]), Path(sys.argv[2])
W, MARGIN, GAP, COLS = 1600, 24, 32, 2
BG = "#060e24"  # same as the metrics panels, so they blend into the page
# placed one by one into the shortest column
ITEMS = ["metrics-profile.svg", "metrics-calendar.svg", "metrics-languages.svg", "metrics-repos.svg"]


def size(data):
    head = data[:600].decode("utf-8")
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head) or re.search(
        r'<svg[^>]*?\swidth="([\d.]+)"[^>]*?\sheight="([\d.]+)"', head
    )
    return float(m.group(1)), float(m.group(2))


def image(data, x, y, w, h):
    b64 = base64.b64encode(data).decode("ascii")
    return f'<image href="data:image/svg+xml;base64,{b64}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/>'


bdata = banner.read_bytes()
bw, bh = size(bdata)
parts = [image(bdata, 0, 0, W, W * bh / bw)]
top = W * bh / bw + GAP

cw = (W - 2 * MARGIN - GAP * (COLS - 1)) / COLS
ys = [top] * COLS
for name in ITEMS:
    path = out / name
    if not path.exists():
        print(f"skip {name}: not found", file=sys.stderr)
        continue
    data = path.read_bytes()
    w, h = size(data)
    c = ys.index(min(ys))
    sh = h * cw / w
    parts.append(image(data, MARGIN + c * (cw + GAP), ys[c], cw, sh))
    ys[c] += sh + GAP

height = max(ys) - GAP + MARGIN
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height:.0f}" width="100%" role="img" '
    f'aria-label="Andy Pérez, full-stack developer, with GitHub metrics">'
    f"<title>Andy Pérez · Full-stack developer</title>"
    f'<rect width="{W}" height="{height:.0f}" fill="{BG}"/>' + "".join(parts) + "</svg>\n"
)
(out / "profile-banner.svg").write_text(svg, encoding="utf-8")
print(f"profile-banner.svg: {len(svg) // 1024} KB, {W}x{height:.0f}")
