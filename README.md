# img2ascii

Convert PNG/JPG images to ASCII art and back to PNG.

Three commands:

- **`image2ascii`** — image → ASCII text
- **`ascii2png`** — ASCII text → PNG image (monospace glyphs or gray blocks)
- **`image2blocks`** — image → gray-block PNG directly (no ASCII step)

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

After installation, three CLI commands are available:

```bash
.venv/bin/image2ascii --help
.venv/bin/ascii2png --help
.venv/bin/image2blocks --help
```

## image2ascii

```bash
image2ascii input.png [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-w`, `--width` | 120 | Output width in characters |
| `-H`, `--height` | auto | Output height (overrides aspect calc) |
| `-o`, `--output` | stdout | Write to file instead of printing |
| `--charset` | default | Character set: `default`, `detailed`, `ramp`, `fine`, `binary`, `blocks` |
| `--invert` | off | Invert tonal mapping |
| `--char-aspect` | 0.55 | Terminal character height/width ratio |

### Charsets

| Name | Characters | Use for |
|------|-----------|---------|
| `default` | `@%#*+=-:. ` | General use |
| `detailed` | `@#%+=:-$ ` | Higher contrast |
| `ramp` | `%@#*+o:. ` | Smooth grayscale |
| `fine` | `@#W$%&*+=;:~-,. ` | Smoothest shading (14 steps) |
| `binary` | `# ` | High contrast / blocky |
| `blocks` | `▓ ▒ ░ ` | Unicode block elements |

### Examples

```bash
# Default output to terminal
image2ascii photo.png

# High detail to file
image2ascii photo.png -w 200 --charset fine -o art.txt

# For blocks PNG round trip (see below)
image2ascii photo.png -w 160 --char-aspect 1.0 -o art.txt
```

## ascii2png

```bash
ascii2png art.txt [options]
```

### Text mode

Renders each character as a monospace glyph on a solid background.

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | blocks | `text` or `blocks` |
| `-o`, `--output` | `<input>.png` | Output PNG path |
| `--font-size` | 16 | Glyph height in pixels |
| `--fg` | `#ffffff` | Character color |
| `--bg` | `#000000` | Background color |
| `--font` | auto | Path to monospace TTF/OTF font |
| `--line-spacing` | 1.0 | Vertical spacing multiplier |
| `--pad` | 10 | Outer padding in pixels |

```bash
ascii2png art.txt --mode text -o text.png --fg "#00ff66"
```

### Blocks mode (default)

Fills each cell with a gray rectangle mapped from the character's brightness. Produces a pixelated grayscale version of the original image.

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | blocks | `text` or `blocks` |
| `--charset` | default | Charset the art was made with (must match) |
| `--cell-size` | 8 | Cell size in pixels |
| `--cell-aspect` | 1.0 | Cell height/width ratio (1.0 = square) |
| `--invert` | off | Flip gray mapping |
| `--pad` | 10 | Outer padding in pixels |

```bash
# Default (blocks mode)
ascii2png art.txt -o blocks.png

# Larger cells
ascii2png art.txt --cell-size 16 -o large.png
```

## image2blocks

Renders an image directly into a PNG of gray rectangles — no ASCII text step. This preserves the original proportions exactly and avoids the quality loss of the text round trip.

```bash
image2blocks photo.png [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-w`, `--width` | 160 | Grid width in cells (raise for detail) |
| `-o`, `--output` | `<input>_blocks.png` | Output PNG path |
| `--cell-size` | 8 | Cell size in pixels |
| `--cell-aspect` | 1.0 | Cell height/width ratio (1.0 = square) |
| `--invert` | off | Invert gray mapping |
| `--pad` | 10 | Outer padding in pixels |

### Examples

```bash
# Default (160 cells wide, 8px square cells)
image2blocks photo.png

# High detail, larger cells
image2blocks photo.png -w 300 --cell-size 12

# Inverted (light background)
image2blocks photo.png --invert
```

## Round trips

### Terminal viewing

```bash
image2ascii photo.png -w 120 -o art.txt
cat art.txt
```

### Blocks PNG via ASCII (two-step)

```bash
# Step 1: create art at true aspect ratio (no terminal squashing)
image2ascii photo.png -w 160 --char-aspect 1.0 -o art.txt

# Step 2: render with square cells
ascii2png art.txt --mode blocks -o output.png
```

> **Important:** Use `--char-aspect 1.0` when creating art for blocks PNG output. The default 0.55 compensates for terminal glyph proportions and will cause horizontal stretching in blocks mode.

### Blocks PNG directly (one-step, best quality)

```bash
image2blocks photo.png -w 160 -o output.png
```

This skips the ASCII step entirely, preserving exact proportions and full grayscale detail.

## Test outputs

The `tests/` directory contains sample outputs from `tests/original.png`:

| File | Description |
|------|-------------|
| `t1_default.txt` | Default charset, 80w |
| `t2_fine.txt` | Fine charset, 160w |
| `t3_blocks.txt` | Blocks charset, 100w |
| `t4_invert.txt` | Inverted, 80w |
| `t5_roundtrip.txt` | Terminal-friendly, 120w |
| `t6_height60.txt` | Explicit height 60 |
| `t7_text.png` | Text mode render |
| `t8_blocks.png` | Blocks mode, square cells |
| `t9_blocks_small.png` | Blocks, cell-size 4 |
| `t10_blocks_large.png` | Blocks, cell-size 16 |
| `t11_blocks_invert.png` | Blocks, inverted |
| `t12_blocks_fine.png` | Blocks with fine charset |

## Project structure

```
img2ascii/
├── pyproject.toml
├── README.md
├── src/
│   └── img2ascii/
│       ├── __init__.py
│       ├── charsets.py
│       ├── image2ascii.py
│       ├── ascii2png.py
│       └── image2blocks.py
└── tests/
    ├── original.png
    └── ... (sample outputs)
```
