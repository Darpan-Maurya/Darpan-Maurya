#!/usr/bin/env python3
"""
Apply a lightweight typing reveal to avi-ascii.svg.

The portrait is made from tens of thousands of small text nodes, so animating
every character would bloat the file. Instead, this wraps the existing text in
a mask and reveals one scanline at a time from left to right.
"""
import os
import re
import sys


def find_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [script_dir, os.getcwd(), os.path.abspath(os.path.join(script_dir, ".."))]
    for candidate in candidates:
        if (
            os.path.isdir(candidate)
            and os.path.isdir(os.path.join(candidate, "scripts"))
            and os.path.isfile(os.path.join(candidate, "README.md"))
        ):
            return os.path.abspath(candidate)
    return os.path.abspath(os.path.join(script_dir, ".."))


ROOT = find_project_root()
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "avi-ascii.svg")
ROW_DURATION = float(os.environ.get("ASCII_ROW_DURATION", "0.16"))
ROW_DELAY = float(os.environ.get("ASCII_ROW_DELAY", "0.026"))


def svg_attr(svg_open, name, fallback):
    match = re.search(rf'{name}="([0-9.]+)"', svg_open)
    return float(match.group(1)) if match else fallback


def build_mask(width, height, rows):
    if len(rows) > 1:
        line_step = min(b - a for a, b in zip(rows, rows[1:]) if b > a)
    else:
        line_step = 5.0
    line_h = line_step + 1.4

    parts = [
        "<!-- typing-reveal:start -->",
        '<defs><mask id="typing-mask" maskUnits="userSpaceOnUse">',
        f'<rect x="0" y="0" width="{width:g}" height="{height:g}" fill="black"/>',
    ]
    for idx, y in enumerate(rows):
        top = max(0, y - line_step)
        begin = idx * ROW_DELAY
        parts.append(
            f'<rect x="0" y="{top:.2f}" width="0" height="{line_h:.2f}" fill="white">'
            f'<animate attributeName="width" from="0" to="{width:g}" begin="{begin:.3f}s" '
            f'dur="{ROW_DURATION:.3f}s" fill="freeze" calcMode="spline" '
            f'keySplines="0.2 0.8 0.2 1"/></rect>'
        )
    parts.append("</mask></defs>")
    parts.append("<!-- typing-reveal:end -->")
    return "".join(parts)


def apply_typing_reveal(svg):
    if 'id="typing-mask"' in svg:
        print(f"{OUT} already has a typing reveal.")
        return svg

    open_match = re.match(r"(<svg[^>]*>)", svg)
    if not open_match:
        raise ValueError("Could not find opening <svg> tag.")

    svg_open = open_match.group(1)
    width = svg_attr(svg_open, "width", 840)
    height = svg_attr(svg_open, "height", 870)
    rows = sorted({float(y) for y in re.findall(r'<text\b[^>]*\by="([0-9.]+)"', svg)})
    if not rows:
        raise ValueError("Could not find text rows to animate.")

    bg_match = re.search(r"(<rect\b[^>]*/>)", svg)
    if not bg_match:
        raise ValueError("Could not find the background rect.")

    text_start = bg_match.end()
    svg_end = svg.rfind("</svg>")
    if svg_end == -1:
        raise ValueError("Could not find closing </svg> tag.")

    prefix = svg[:text_start]
    body = svg[text_start:svg_end]
    suffix = svg[svg_end:]
    mask = build_mask(width, height, rows)
    wrapped_body = f'{mask}<g mask="url(#typing-mask)">{body}</g>'
    return prefix + wrapped_body + suffix


if __name__ == "__main__":
    with open(OUT) as f:
        source = f.read()
    animated = apply_typing_reveal(source)
    with open(OUT, "w") as f:
        f.write(animated)
    print(f"typing reveal ready in {OUT}")
