"""Combine per-sheet chart PNGs (see generate_all_charts.py) into overview
grid montages, each chart labeled with its sheet name.

Usage:
    python make_overview.py

Reads all PNGs from charts/, excludes the combined/master sheets (Everything
already includes those trainings individually), and writes three montages
into overview/:
  - overview_all.png          every remaining chart, alphabetical
  - overview_epos_trainings.png     sheets whose name starts with "EPOS"
  - overview_other_trainings.png    all other (non-EPOS) trainings
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).parent
CHARTS_DIR = PROJECT_DIR / "charts"
OVERVIEW_DIR = PROJECT_DIR / "overview"

EXCLUDED_SHEETS = {"AllParticpants", "ORFEUS_allParticipants", "WP5Participants"}

THUMB_SIZE = 480  # each chart is scaled to THUMB_SIZE x THUMB_SIZE
LABEL_HEIGHT = 56
PADDING = 16
BACKGROUND = "white"


def load_font(size):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


LABEL_FONT = load_font(22)


def make_montage(names, output_path, columns=None):
    if not names:
        print(f"Skipping {output_path.name}: no charts to include")
        return

    cols = columns or math.ceil(math.sqrt(len(names)))
    rows = math.ceil(len(names) / cols)

    cell_w = THUMB_SIZE + PADDING
    cell_h = THUMB_SIZE + LABEL_HEIGHT + PADDING
    canvas = Image.new("RGB", (cols * cell_w + PADDING, rows * cell_h + PADDING), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    for i, name in enumerate(names):
        row, col = divmod(i, cols)
        x = PADDING + col * cell_w
        y = PADDING + row * cell_h

        img = Image.open(CHARTS_DIR / f"{name}.png").convert("RGB")
        img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
        canvas.paste(img, (x, y))

        text_bbox = draw.textbbox((0, 0), name, font=LABEL_FONT)
        text_w = text_bbox[2] - text_bbox[0]
        text_x = x + max((THUMB_SIZE - text_w) // 2, 0)
        text_y = y + THUMB_SIZE + (LABEL_HEIGHT - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((text_x, text_y), name, fill="black", font=LABEL_FONT)

    OVERVIEW_DIR.mkdir(exist_ok=True)
    canvas.save(output_path)
    print(f"{output_path.name}: {len(names)} charts, {cols}x{rows} grid -> {output_path}")


def main():
    available = {p.stem for p in CHARTS_DIR.glob("*.png")}
    names = sorted(available - EXCLUDED_SHEETS)

    epos_names = [n for n in names if n.startswith("EPOS")]
    other_names = [n for n in names if not n.startswith("EPOS")]

    make_montage(names, OVERVIEW_DIR / "overview_all.png")
    make_montage(epos_names, OVERVIEW_DIR / "overview_epos_trainings.png")
    make_montage(other_names, OVERVIEW_DIR / "overview_other_trainings.png")


if __name__ == "__main__":
    main()
