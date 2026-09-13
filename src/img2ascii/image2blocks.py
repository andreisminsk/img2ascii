#!/usr/bin/env python3
"""Render an image directly into a PNG of gray rectangles (gray gradation).

Unlike the ASCII round trip, this does NOT pass through a lossy text grid, so
the output always matches the source image's proportions and detail.

Usage:
    image2blocks photo.png
    image2blocks photo.png -w 160 --cell-size 8 -o photo.png
    image2blocks photo.png --cell-aspect 1.0   # square cells
"""

import argparse
import sys
import os

from PIL import Image


def render(image, width=160, cell_size=8, cell_aspect=1.0,
           invert=False, pad=10):
    """Map an image to a 1px-per-cell grayscale grid, then upscale to blocks."""
    orig_w, orig_h = image.size
    if width <= 0:
        width = orig_w
    height = max(1, int(round(orig_h / orig_w * width)))

    small = image.convert("L").resize((width, height), Image.LANCZOS)
    if invert:
        small = Image.eval(small, lambda v: 255 - v)

    cw = max(1, int(cell_size))
    ch = max(1, int(round(cell_size * cell_aspect)))
    big = small.resize((width * cw, height * ch), Image.NEAREST).convert("RGB")

    if pad:
        out = Image.new("RGB", (big.width + 2 * pad, big.height + 2 * pad),
                        (255, 255, 255))
        out.paste(big, (pad, pad))
        return out
    return big


def main():
    p = argparse.ArgumentParser(
        description="Render an image directly into a gray-rectangle PNG.")
    p.add_argument("input", help="Path to the source image (.png or .jpg).")
    p.add_argument("-o", "--output", default=None,
                   help="Output PNG path (default: <input>_blocks.png).")
    p.add_argument("-w", "--width", type=int, default=160,
                   help="Grid width in cells (default: 160). Raise for detail.")
    p.add_argument("--cell-size", type=int, default=8,
                   help="Cell size in px (default: 8).")
    p.add_argument("--cell-aspect", type=float, default=1.0,
                   help="Cell height/width ratio; 1.0 = square (default).")
    p.add_argument("--invert", action="store_true",
                   help="Invert the gray mapping (dark bg -> light bg).")
    p.add_argument("--pad", type=int, default=10,
                   help="Outer padding in px (default: 10).")
    args = p.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"File not found: {args.input}")
    ext = os.path.splitext(args.input)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg"):
        sys.exit(f"Unsupported format: {ext} (use .png or .jpg).")

    img = render(Image.open(args.input), args.width, args.cell_size,
                 args.cell_aspect, args.invert, args.pad)
    out = args.output or os.path.splitext(args.input)[0] + "_blocks.png"
    img.save(out)
    print(f"Saved {out}  ({img.width}x{img.height}px)")


if __name__ == "__main__":
    main()
