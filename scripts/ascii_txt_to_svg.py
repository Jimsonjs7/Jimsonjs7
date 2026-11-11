#!/usr/bin/env python3
"""
ascii_txt_to_svg.py - Convert an ASCII art text file into a terminal-animated SVG.

Usage:
    python scripts/ascii_txt_to_svg.py [input.txt] [output.svg] [options]

Examples:
    # Default: reads ascii-art.txt -> writes avi-ascii.svg
    python scripts/ascii_txt_to_svg.py

    # Custom input & output files
    python scripts/ascii_txt_to_svg.py my-art.txt output.svg

    # Generate static SVG (no typing reveal animation)
    python scripts/ascii_txt_to_svg.py ascii-art.txt avi-ascii.svg --static

    # Auto-trim excess blank lines at top and bottom
    python scripts/ascii_txt_to_svg.py ascii-art.txt avi-ascii.svg --trim
"""

import argparse
import sys
from pathlib import Path

# Styling defaults matching GitHub dark mode terminal look
DEFAULT_FG = "#c9d1d9"
DEFAULT_BG = "#0d1117"
FONT_FAMILY = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
FONT_SIZE = 7
LINE_HEIGHT = 7.0
CHAR_ASPECT = 0.52  # Width-to-height ratio for monospace characters
CHAR_WIDTH = FONT_SIZE * CHAR_ASPECT
ROW_REVEAL_DUR = 0.028  # Seconds delay between row reveals


def escape_xml(s: str) -> str:
    """Escape XML special characters."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def convert_ascii_to_svg(
    lines: list[str],
    static: bool = False,
    fg: str = DEFAULT_FG,
    bg: str = DEFAULT_BG,
    trim: bool = False,
) -> str:
    """Build an animated SVG string from a list of ASCII art text lines."""
    # Strip newline terminators
    rows = [line.rstrip("\r\n") for line in lines]

    # Optionally trim leading & trailing completely empty lines, keeping 2 lines of breathing space
    if trim:
        non_empty = [i for i, r in enumerate(rows) if r.strip()]
        if non_empty:
            start = max(0, non_empty[0] - 2)
            end = min(len(rows), non_empty[-1] + 3)
            rows = rows[start:end]

    if not rows:
        rows = [""]

    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) if rows else 1
    # Minimum columns to avoid zero-width box
    n_cols = max(n_cols, 20)

    width = n_cols * CHAR_WIDTH + 20
    height = n_rows * LINE_HEIGHT + 20
    total_anim = n_rows * ROW_REVEAL_DUR

    css = f"""
    .ascii-line {{
      font-family: {FONT_FAMILY};
      font-size: {FONT_SIZE}px;
      white-space: pre;
      fill: {fg};
    }}
    """
    if not static:
        css += f"""
    .ascii-line {{
      opacity: 0;
      animation: reveal 0.35s ease-out forwards;
    }}
    @keyframes reveal {{
      to {{ opacity: 1; }}
    }}
    .cursor {{
      fill: {fg};
      animation: blink 0.9s steps(1) infinite;
      animation-delay: {total_anim:.2f}s;
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    """

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}">',
        f'<style>{css}</style>',
        f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="{bg}" rx="6"/>',
    ]

    for i, row in enumerate(rows):
        y = 14 + i * LINE_HEIGHT
        delay = i * ROW_REVEAL_DUR
        style = "" if static else f' style="animation-delay:{delay:.3f}s"'
        parts.append(
            f'<text x="10" y="{y:.1f}" class="ascii-line"{style}>{escape_xml(row)}</text>'
        )

    if not static:
        last_row_len = len(rows[-1]) if rows else 0
        cy = 14 + (n_rows - 1) * LINE_HEIGHT
        cx = 10 + last_row_len * CHAR_WIDTH
        parts.append(
            f'<rect class="cursor" x="{cx:.1f}" y="{cy - FONT_SIZE + 1:.1f}" width="{CHAR_WIDTH:.1f}" height="{FONT_SIZE:.1f}"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Convert an ASCII text art file into a terminal-animated SVG portrait."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="ascii-art.txt",
        help="Input ASCII text file (default: ascii-art.txt)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="avi-ascii.svg",
        help="Output SVG file (default: avi-ascii.svg)",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Render a static SVG without typing animation",
    )
    parser.add_argument(
        "--trim",
        action="store_true",
        help="Auto-trim excess blank lines at top and bottom",
    )
    parser.add_argument(
        "--fg",
        default=DEFAULT_FG,
        help=f"Foreground text color (default: {DEFAULT_FG})",
    )
    parser.add_argument(
        "--bg",
        default=DEFAULT_BG,
        help=f"Background rectangle color (default: {DEFAULT_BG})",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    svg_content = convert_ascii_to_svg(
        lines,
        static=args.static,
        fg=args.fg,
        bg=args.bg,
        trim=args.trim,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(
        f"[ascii_txt_to_svg] Successfully converted '{args.input}' -> '{args.output}'"
    )
    print(
        f"                   Rows: {len(lines)}, Mode: {'static' if args.static else 'animated'}"
    )


if __name__ == "__main__":
    main()

