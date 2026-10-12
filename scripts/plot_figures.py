#!/usr/bin/env python3
"""Render retained observer-gap results with Matplotlib (optional dependency).

Run: python scripts/plot_figures.py [--font-file path/to/LinLibertine_R.otf]
Use an installed Linux Libertine O face or TeX's kpsewhich font lookup; an
explicit font file is portable when neither lookup is available. Font files
are not redistributed. This script runs no experiment and changes no raw data.
Native output is figures/observer-gap.pdf (337.5 x 128 PDF points); a sibling
paper/figures receives the identical PDF when that directory exists.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import shutil
import subprocess
import tempfile

import matplotlib as mpl
mpl.use("Agg")
from matplotlib import font_manager as fm
from matplotlib import pyplot as plt
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT_CACHE = tempfile.TemporaryDirectory(prefix="figure-fonts-", ignore_cleanup_errors=True)


def register_font(path: Path) -> Path:
    """Give the PDF Type-42 backend TrueType outlines, retaining the same face.

    TeX's Libertine OTF has CFF outlines. Convert those outlines to quadratic
    curves within one font unit in a temporary file, not a shipped font asset.
    Direct CFF embedding as CIDFontType2 can leave invisible PDF text.
    """
    font = TTFont(path)
    if "CFF " in font:
        glyph_set = font.getGlyphSet()
        glyphs = {}
        for name in font.getGlyphOrder():
            pen = TTGlyphPen(None)
            glyph_set[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
            glyphs[name] = pen.glyph()
        del font["CFF "]
        font.sfntVersion = "\x00\x01\x00\x00"
        builder = FontBuilder(font=font, isTTF=True)
        builder.isTTF = True
        builder.setupGlyf(glyphs)
        builder.setupMaxp()
        converted = Path(FONT_CACHE.name) / (path.stem + ".ttf")
        font.save(converted)
        path = converted
    fm.fontManager.addfont(str(path))
    return path


def configure_font(path: Path | None) -> str:
    if path is None:
        try:
            path = Path(fm.findfont("Linux Libertine O", fallback_to_default=False))
        except ValueError:
            lookup = shutil.which("kpsewhich")
            found = subprocess.check_output([lookup, "LinLibertine_R.otf"], text=True).strip() if lookup else ""
            if not found:
                raise SystemExit("Install Linux Libertine O or supply --font-file LinLibertine_R.otf")
            path = Path(found)
    if not path.is_file():
        raise FileNotFoundError(path)
    regular = register_font(path)
    for name in ("LinLibertine_RI.otf", "LinLibertine_RB.otf"):
        companion = path.with_name(name)
        if companion.is_file():
            register_font(companion)
    family = fm.FontProperties(fname=str(regular)).get_name()
    mpl.rcParams.update({
        "font.family": family, "font.size": 8, "mathtext.fontset": "custom",
        "mathtext.rm": family, "mathtext.it": f"{family}:italic",
        "mathtext.bf": f"{family}:bold", "mathtext.fallback": "cm",
        "pdf.fonttype": 42, "pdf.use14corefonts": False, "text.usetex": False,
        "axes.unicode_minus": False, "axes.linewidth": .5,
        "path.simplify": False,
    })
    return family


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-file", type=Path)
    parser.add_argument("--data", type=Path, default=ROOT / "results/presentation/observer-gap.csv")
    args = parser.parse_args()
    family = configure_font(args.font_file)
    with args.data.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    bits = [int(row["input_bits"]) for row in rows]
    coarse = [int(row["coarse_bytes"]) for row in rows]
    refined = [int(row["refined_bytes"]) for row in rows]
    if bits != list(range(4)) or coarse != [12] * 4 or refined != [8 * 2**b + 4 for b in bits]:
        raise ValueError("Observer-gap table does not match the declared four confirmed instances")
    fig = plt.figure(figsize=(337.5 / 72, 128 / 72))
    ax = fig.add_axes([32 / 337.5, 26 / 128, 301 / 337.5, 98 / 128])
    ax.plot(bits, coarse, color="black", marker="o", ms=4.4, lw=.6, label="coarse signature")
    ax.plot(bits, refined, color="black", marker="s", ms=4.4, lw=.6, ls="--", label="origin-refined")
    ax.set(xlim=(-.3, 3.3), ylim=(0, 74), xlabel=r"entry bits $b$", ylabel="PFC1 bytes")
    ax.set_xticks(bits)
    ax.set_yticks([0, 12, 20, 36, 68])
    ax.tick_params(length=2, width=.5, pad=2)
    ax.grid(color=".80", lw=.35)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", bbox_to_anchor=(.03, .97), fontsize=8, borderpad=.3)
    output = ROOT / "figures/observer-gap.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, metadata={"Creator": None, "Producer": None, "CreationDate": None, "ModDate": None})
    plt.close(fig)
    paper = ROOT.parent / "paper/figures"
    if paper.is_dir():
        shutil.copyfile(output, paper / output.name)
    print(f"observer-gap: {len(rows)} retained rows, two series; embedded {family}; {output.name}")


if __name__ == "__main__":
    main()
