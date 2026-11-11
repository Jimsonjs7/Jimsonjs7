#!/usr/bin/env python3
"""
ascii_txt_to_svg.py - Convert an ASCII art text file into a terminal-animated SVG.

Usage:
    python scripts/ascii_txt_to_svg.py [input.txt] [output.svg] [options]

Examples:
    # Default: aligns with terminal card (370x400) and writes avi-ascii.svg
    python scripts/ascii_txt_to_svg.py

    # Include macOS terminal window header (3 dots + divider line)
    python scripts/ascii_txt_to_svg.py --terminal-window

    # Render static (no typing reveal animation)
    python scripts/ascii_txt_to_svg.py --static
"""

import argparse
import sys
from pathlib import Path

# Styling defaults matching GitHub dark mode terminal look
DEFAULT_FG = "#c9d1d9"
DEFAULT_BG = "#0d1117"
DEFAULT_BORDER = "#30363d"
FONT_FAMILY = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
ROW_REVEAL_DUR = 0.028  # Seconds delay between row reveals


def escape_xml(s: str) -> str:
    """Escape XML special characters."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def convert_ascii_to_svg(
    lines: list[str],
    static: bool = False,
    fg: str = DEFAULT_FG,
    bg: str = DEFAULT_BG,
    border: str = DEFAULT_BORDER,
    target_width: int = 370,
    target_height: int = 400,
    terminal_window: bool = False,
    natural_scale: bool = False,
    cursor_align: str = "terminal",
) -> str:
    """Build an animated SVG string from a list of ASCII art text lines."""
    raw_rows = [line.rstrip("\r\n") for line in lines]

    # Find content bounds (strip surrounding blank lines)
    non_empty = [i for i, r in enumerate(raw_rows) if r.strip()]
    if non_empty:
        rows = raw_rows[non_empty[0] : non_empty[-1] + 1]
    else:
        rows = raw_rows or [""]

    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) if rows else 1
    n_cols = max(n_cols, 20)

    if natural_scale:
        # Standard unconstrained scale
        font_size = 7.0
        line_height = 7.0
        char_aspect = 0.52
        char_w = font_size * char_aspect
        width = n_cols * char_w + 20
        height = n_rows * line_height + 20
        start_y = 14.0
        pad_x = 10.0
    else:
        # Fit into target card dimensions to align with info-card.svg
        width = target_width
        height = target_height
        char_aspect = 0.52

        if terminal_window:
            # Header has 3 dots + border line at y=32 + line space
            top_bar_h = 32.0
            line_space = 18.0
            start_y = top_bar_h + line_space
            avail_h = height - start_y - 12.0
        else:
            # Card with line space between top border and first line
            start_y = 20.0
            avail_h = height - start_y - 14.0

        # Reserve a dedicated row below ASCII art for the terminal cursor
        n_slots = (n_rows + 1) if not static and cursor_align != "inline" else n_rows
        line_height = avail_h / max(n_slots, 1)
        font_size = line_height
        char_w = font_size * char_aspect
        text_w = n_cols * char_w
        pad_x = max((width - text_w) / 2.0, 8.0)

    total_anim = n_rows * ROW_REVEAL_DUR

    css = f"""
    .ascii-line {{
      font-family: {FONT_FAMILY};
      font-size: {font_size:.2f}px;
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
        f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" rx="8" fill="{bg}" stroke="{border}" stroke-width="1"/>',
    ]

    if terminal_window and not natural_scale:
        parts.append('  <circle cx="20" cy="18" r="5" fill="#ff5f56"/>')
        parts.append('  <circle cx="38" cy="18" r="5" fill="#ffbd2e"/>')
        parts.append('  <circle cx="56" cy="18" r="5" fill="#27c93f"/>')
        parts.append(
            f'  <line x1="0" y1="32" x2="{width:.0f}" y2="32" stroke="{border}" stroke-width="1"/>'
        )

    for i, row in enumerate(rows):
        y = start_y + (i + 1) * line_height
        delay = i * ROW_REVEAL_DUR
        style = "" if static else f' style="animation-delay:{delay:.3f}s"'
        parts.append(
            f'  <text x="{pad_x:.1f}" y="{y:.1f}" class="ascii-line"{style}>{escape_xml(row)}</text>'
        )

    if not static:
        if cursor_align == "inline":
            last_row_len = len(rows[-1]) if rows else 0
            cy = start_y + n_rows * line_height
            cx = pad_x + last_row_len * char_w
            cw = char_w
        elif cursor_align == "ascii":
            cy = start_y + (n_rows + 1) * line_height
            cx = pad_x
            cw = max(char_w, 3.0)
        else:  # "terminal" (default: aligns with terminal left margin / info-card.svg)
            cy = start_y + (n_rows + 1) * line_height
            cx = 24.0 if terminal_window else pad_x
            cw = max(char_w * 1.5, 4.0)

        parts.append(
            f'  <rect class="cursor" x="{cx:.1f}" y="{cy - font_size + 1:.1f}" width="{cw:.1f}" height="{font_size:.1f}"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Convert an ASCII text art file into a terminal-animated SVG portrait aligned with info-card.svg."
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
        "--terminal-window",
        action="store_true",
        help="Add terminal window title bar (red/yellow/green dots + divider line)",
    )
    parser.add_argument(
        "--natural-scale",
        action="store_true",
        help="Use unconstrained scale rather than fitting into 370x400 card",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=370,
        help="Target card width (default: 370)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=400,
        help="Target card height (default: 400, matching info-card.svg)",
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
    parser.add_argument(
        "--cursor-align",
        choices=["terminal", "ascii", "inline"],
        default="terminal",
        help="Cursor placement: 'terminal' (left margin x=24), 'ascii' (left edge of ASCII text), or 'inline' (end of last text row)",
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
        target_width=args.width,
        target_height=args.height,
        terminal_window=args.terminal_window,
        natural_scale=args.natural_scale,
        cursor_align=args.cursor_align,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(
        f"[ascii_txt_to_svg] Successfully converted '{args.input}' -> '{args.output}'"
    )
    print(
        f"                   Dimensions: {args.width}x{args.height}, Window Style: {'Terminal Window' if args.terminal_window else 'Aligned Card'}"
    )


if __name__ == "__main__":
    main()
