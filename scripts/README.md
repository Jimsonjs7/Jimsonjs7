# Profile Art & Automation Scripts Guide

This directory contains utility scripts to generate and maintain your GitHub profile assets (`avi-ascii.svg`, `info-card.svg`, `contrib-heatmap.svg`).

---

## 1. ASCII Text to Animated SVG (`ascii_txt_to_svg.py`)

Converts any ASCII text art file (e.g. `ascii-art.txt`) into a dark-mode terminal animated SVG with sequential line typing reveals and a blinking cursor.

### Quick Start
```bash
# From repository root:
python3 scripts/ascii_txt_to_svg.py
```
*(By default, reads `ascii-art.txt` and outputs `avi-ascii.svg`)*

### Custom File Paths
```bash
python3 scripts/ascii_txt_to_svg.py <input-path.txt> <output-path.svg>

# Example:
python3 scripts/ascii_txt_to_svg.py custom-art.txt my-avatar.svg
```

### Options & Flags
| Flag | Description | Example |
| :--- | :--- | :--- |
| `--terminal-window` | Adds terminal title bar (3 dots + divider line) matching info-card | `python3 scripts/ascii_txt_to_svg.py --terminal-window` |
| `--static` | Disables typing animation (all rows visible immediately, no cursor) | `python3 scripts/ascii_txt_to_svg.py --static` |
| `--natural-scale` | Uses unconstrained dimensions rather than fitting 370x400 | `python3 scripts/ascii_txt_to_svg.py --natural-scale` |
| `--width / --height`| Custom target card dimensions (default: 370x400) | `python3 scripts/ascii_txt_to_svg.py --width 370 --height 400` |
| `--fg <hex>` | Custom text color (default: `#c9d1d9`) | `python3 scripts/ascii_txt_to_svg.py --fg "#58a6ff"` |
| `--bg <hex>` | Custom background color (default: `#0d1117`) | `python3 scripts/ascii_txt_to_svg.py --bg "#161b22"` |
| `--cursor-align` | Cursor position: `terminal` (x=24 left margin), `ascii` (x=pad_x), or `inline` (end of last row) | `python3 scripts/ascii_txt_to_svg.py --cursor-align terminal` |

---

## 2. Terminal Info Card (`make_info_card.py`)

Generates `info-card.svg` — the terminal-style card with macOS window controls showing your role, stack, infrastructure, and links.

### How to Edit:
1. Open `scripts/make_info_card.py` and modify the `ROWS` list (around line 20):
   ```python
   ROWS = [
       ("role", "Freelance Software Developer"),
       ("focus", "Backend engineering, AI/ML LLM pipelines"),
       ("stack", "Python, Java, TypeScript, JavaScript"),
       ("infra", "Docker / Nginx / MinIO / CI/CD / Linux"),
       ("current", "RAG pipelines, agentic AI workflows"),
       ("exploring", "AI-native dev tooling, cybersecurity"),
       ("linkedin", "linkedin.com/in/jimson-shaju-m"),
   ]
   ```
2. Regenerate the card:
   ```bash
   python3 scripts/make_info_card.py
   ```

---

## 3. GitHub Contributions Heatmap

Generates the contribution heatmap `contrib-heatmap.svg` from your GitHub activity.

### How to Run:
```bash
# 1. Fetch contribution data (saves contributions.json)
python3 scripts/fetch_contributions.py

# 2. Render heatmap SVG
python3 scripts/render_heatmap_svg.py contributions.json contrib-heatmap.svg
```
*(Note: A GitHub Actions workflow in `.github/workflows/update-profile-art.yml` also runs this automatically once a day).*

---

## 4. Photo to ASCII Pipeline (Optional)

If you ever want to convert a real photograph directly into an ASCII portrait:

```bash
# Step 1: Remove background and equalize local contrast (requires rembg and opencv)
python3 scripts/prep_photo.py my-photo.jpg source-prepped.png

# Step 2: Convert prepped image to animated ASCII SVG
python3 scripts/make_ascii_svg.py source-prepped.png avi-ascii.svg
```

