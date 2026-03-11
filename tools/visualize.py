#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
import struct
import zlib
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Tuple


def _read_history(path: Path) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    with path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "epoch": float(row["epoch"]),
                    "l2_error": float(row["l2_error"]),
                    "pde_residual": float(row["pde_residual"]),
                    "bc_ic_error": float(row["bc_ic_error"]),
                }
            )
    return rows


def _read_summary(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _rolling_mean(values: List[float], window: int = 5) -> List[float]:
    if window <= 1:
        return values[:]
    out = []
    for i in range(len(values)):
        s = max(0, i - window + 1)
        out.append(mean(values[s : i + 1]))
    return out


def _scale(v: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if abs(in_max - in_min) < 1e-12:
        return (out_min + out_max) / 2
    ratio = (v - in_min) / (in_max - in_min)
    return out_min + ratio * (out_max - out_min)


class PngCanvas:
    def __init__(self, w: int, h: int, bg: Tuple[int, int, int] = (255, 255, 255)) -> None:
        self.w, self.h = w, h
        self.p = [list(bg) for _ in range(w * h)]

    def _set(self, x: int, y: int, c: Tuple[int, int, int]) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y * self.w + x] = [c[0], c[1], c[2]]

    def line(self, x1: float, y1: float, x2: float, y2: float, c: Tuple[int, int, int], t: int = 1) -> None:
        x1i, y1i, x2i, y2i = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
        dx = abs(x2i - x1i)
        sx = 1 if x1i < x2i else -1
        dy = -abs(y2i - y1i)
        sy = 1 if y1i < y2i else -1
        err = dx + dy
        x, y = x1i, y1i
        while True:
            for ox in range(-(t // 2), t // 2 + 1):
                for oy in range(-(t // 2), t // 2 + 1):
                    self._set(x + ox, y + oy, c)
            if x == x2i and y == y2i:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def rect(self, x: float, y: float, w: float, h: float, c: Tuple[int, int, int]) -> None:
        xi, yi, wi, hi = int(round(x)), int(round(y)), int(round(w)), int(round(h))
        for yy in range(yi, yi + hi):
            for xx in range(xi, xi + wi):
                self._set(xx, yy, c)

    def to_png(self, path: Path) -> None:
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            row = self.p[y * self.w : (y + 1) * self.w]
            for r, g, b in row:
                raw.extend([r, g, b])

        def chunk(tag: bytes, data: bytes) -> bytes:
            return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        sig = b"\x89PNG\r\n\x1a\n"
        ihdr = chunk(b"IHDR", struct.pack("!IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
        idat = chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        iend = chunk(b"IEND", b"")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(sig + ihdr + idat + iend)


def _variant_name(run_name: str) -> str:
    return re.sub(r"_seed\d+$", "", run_name)


def plot_loss(history_csv: Path, out_svg: Path, out_png: Path) -> None:
    rows = _read_history(history_csv)
    if not rows:
        raise ValueError(f"No rows in {history_csv}")

    w, h = 1200, 720
    ml, mr, mt, mb = 110, 40, 50, 80
    cw, ch = w - ml - mr, h - mt - mb

    xs = [r["epoch"] for r in rows]
    l2 = [r["l2_error"] for r in rows]
    pde = [r["pde_residual"] for r in rows]
    bc = [r["bc_ic_error"] for r in rows]
    pde_s = _rolling_mean(pde, 5)
    bc_s = _rolling_mean(bc, 5)

    ymin, ymax = min(l2 + pde + bc), max(l2 + pde + bc)
    xmin, xmax = min(xs), max(xs)

    def pts(vals: List[float]) -> List[Tuple[float, float]]:
        return [(_scale(x, xmin, xmax, ml, ml + cw), _scale(y, ymin, ymax, mt + ch, mt)) for x, y in zip(xs, vals)]

    l2p, pdep, bcp = pts(l2), pts(pde_s), pts(bc_s)

    # SVG
    grid = [f'<line x1="{ml}" y1="{mt + ch*i/5:.2f}" x2="{ml+cw}" y2="{mt + ch*i/5:.2f}" stroke="#e6e6e6" />' for i in range(6)]
    def poly(points: List[Tuple[float, float]], color: str, sw: int = 3) -> str:
        return f'<polyline fill="none" stroke="{color}" stroke-width="{sw}" points="' + " ".join(f"{x:.2f},{y:.2f}" for x,y in points) + '" />'
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">',
        '<rect width="100%" height="100%" fill="white"/>',
        *grid,
        f'<line x1="{ml}" y1="{mt+ch}" x2="{ml+cw}" y2="{mt+ch}" stroke="#333"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#333"/>',
        poly(l2p, "#1f77b4", 4),
        poly(pdep, "#d62728", 3),
        poly(bcp, "#2ca02c", 3),
        f'<text x="{w/2}" y="34" text-anchor="middle" font-size="34">Training Curves (smoothed PDE/BCIC)</text>',
        f'<text x="{w/2}" y="{h-18}" text-anchor="middle" font-size="26">Epoch</text>',
        f'<text x="34" y="{h/2}" transform="rotate(-90,34,{h/2})" text-anchor="middle" font-size="26">Error</text>',
        '<text x="860" y="120" font-size="28" fill="#1f77b4">L2</text>',
        '<text x="860" y="160" font-size="28" fill="#d62728">PDE residual (MA5)</text>',
        '<text x="860" y="200" font-size="28" fill="#2ca02c">BC/IC error (MA5)</text>',
        '</svg>'
    ]
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text("\n".join(svg), encoding="utf-8")

    # PNG
    cv = PngCanvas(w, h)
    for i in range(6):
        y = mt + ch * i / 5
        cv.line(ml, y, ml + cw, y, (230, 230, 230), 1)
    cv.line(ml, mt + ch, ml + cw, mt + ch, (50, 50, 50), 2)
    cv.line(ml, mt, ml, mt + ch, (50, 50, 50), 2)
    for arr, col, th in [(l2p, (31, 119, 180), 3), (pdep, (214, 39, 40), 2), (bcp, (44, 160, 44), 2)]:
        for a, b in zip(arr[:-1], arr[1:]):
            cv.line(a[0], a[1], b[0], b[1], col, th)
    cv.to_png(out_png)


def plot_ablation(summary_csv: Path, out_svg: Path, out_png: Path) -> None:
    rows = _read_summary(summary_csv)
    if not rows:
        raise ValueError(f"No rows in {summary_csv}")

    grouped: Dict[str, List[float]] = {}
    for r in rows:
        name = _variant_name(r["run"])
        grouped.setdefault(name, []).append(float(r["l2_error"]))

    items = []
    for k, vals in grouped.items():
        m = mean(vals)
        sd = stdev(vals) if len(vals) > 1 else 0.0
        items.append((k, m, sd, len(vals)))
    items.sort(key=lambda x: x[1])

    w, h = 1280, 760
    ml, mr, mt, mb = 120, 40, 60, 190
    cw, ch = w - ml - mr, h - mt - mb
    ymax = max((m + sd) for _, m, sd, _ in items) * 1.2

    # SVG
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">', '<rect width="100%" height="100%" fill="white"/>']
    for i in range(6):
        y = mt + ch * i / 5
        svg.append(f'<line x1="{ml}" y1="{y:.2f}" x2="{ml+cw}" y2="{y:.2f}" stroke="#e6e6e6" />')
    svg += [f'<line x1="{ml}" y1="{mt+ch}" x2="{ml+cw}" y2="{mt+ch}" stroke="#333"/>', f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#333"/>']
    bw = cw / max(len(items), 1) * 0.62
    gap = cw / max(len(items), 1) * 0.38
    x = ml + gap/2
    palette = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc949"]
    for i, (name, m, sd, n) in enumerate(items):
        top = _scale(m, 0, ymax, mt + ch, mt)
        bh = mt + ch - top
        c = palette[i % len(palette)]
        svg.append(f'<rect x="{x:.2f}" y="{top:.2f}" width="{bw:.2f}" height="{bh:.2f}" fill="{c}"/>')
        if sd > 0:
            y1 = _scale(m - sd, 0, ymax, mt + ch, mt)
            y2 = _scale(m + sd, 0, ymax, mt + ch, mt)
            cx = x + bw/2
            svg += [f'<line x1="{cx:.2f}" y1="{y1:.2f}" x2="{cx:.2f}" y2="{y2:.2f}" stroke="#111" stroke-width="2"/>',
                    f'<line x1="{cx-8:.2f}" y1="{y1:.2f}" x2="{cx+8:.2f}" y2="{y1:.2f}" stroke="#111" stroke-width="2"/>',
                    f'<line x1="{cx-8:.2f}" y1="{y2:.2f}" x2="{cx+8:.2f}" y2="{y2:.2f}" stroke="#111" stroke-width="2"/>']
        svg.append(f'<text x="{x+bw/2:.2f}" y="{top-8:.2f}" text-anchor="middle" font-size="19">{m:.4f} (n={n})</text>')
        svg.append(f'<text x="{x+bw/2:.2f}" y="{h-24}" transform="rotate(20,{x+bw/2:.2f},{h-24})" text-anchor="start" font-size="18">{name}</text>')
        x += bw + gap
    svg += [f'<text x="{w/2}" y="40" text-anchor="middle" font-size="36">Ablation Comparison (L2 mean ± std)</text>',
            f'<text x="{w/2}" y="{h-8}" text-anchor="middle" font-size="26">Variants</text>',
            f'<text x="32" y="{h/2}" transform="rotate(-90,32,{h/2})" text-anchor="middle" font-size="26">L2 Error</text>',
            '</svg>']
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text("\n".join(svg), encoding="utf-8")

    # PNG
    cv = PngCanvas(w, h)
    for i in range(6):
        y = mt + ch * i / 5
        cv.line(ml, y, ml + cw, y, (230, 230, 230), 1)
    cv.line(ml, mt + ch, ml + cw, mt + ch, (50, 50, 50), 2)
    cv.line(ml, mt, ml, mt + ch, (50, 50, 50), 2)
    x = ml + gap / 2
    pal = [(78, 121, 167), (242, 142, 43), (225, 87, 89), (118, 183, 178), (89, 161, 79), (237, 201, 72)]
    for i, (_, m, sd, _) in enumerate(items):
        top = _scale(m, 0, ymax, mt + ch, mt)
        bh = mt + ch - top
        cv.rect(x, top, bw, bh, pal[i % len(pal)])
        if sd > 0:
            y1 = _scale(m - sd, 0, ymax, mt + ch, mt)
            y2 = _scale(m + sd, 0, ymax, mt + ch, mt)
            cx = x + bw / 2
            cv.line(cx, y1, cx, y2, (20, 20, 20), 2)
            cv.line(cx - 8, y1, cx + 8, y1, (20, 20, 20), 2)
            cv.line(cx - 8, y2, cx + 8, y2, (20, 20, 20), 2)
        x += bw + gap
    cv.to_png(out_png)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate experiment visualizations (PNG first, then SVG).")
    parser.add_argument("--run-dir", default="runs", help="runs root")
    parser.add_argument("--summary-csv", default="results/raw/summary.csv")
    parser.add_argument("--out-dir", default="results/figures")
    parser.add_argument("--run-name", default="", help="optional run name for loss curve")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_dir = Path(args.run_dir)
    if args.run_name:
        history_csv = run_dir / args.run_name / "history.csv"
    else:
        candidates = sorted(run_dir.glob("*/history.csv"))
        if not candidates:
            raise FileNotFoundError("No history.csv found under runs")
        history_csv = candidates[-1]

    # 先输出 PNG，再输出 SVG
    loss_png = out_dir / "loss_curves.png"
    ablation_png = out_dir / "ablation_l2.png"
    loss_svg = out_dir / "loss_curves.svg"
    ablation_svg = out_dir / "ablation_l2.svg"

    plot_loss(history_csv, out_svg=loss_svg, out_png=loss_png)
    plot_ablation(Path(args.summary_csv), out_svg=ablation_svg, out_png=ablation_png)

    print(f"[viz] loss curve png: {loss_png}")
    print(f"[viz] loss curve svg: {loss_svg}")
    print(f"[viz] ablation png: {ablation_png}")
    print(f"[viz] ablation svg: {ablation_svg}")


if __name__ == "__main__":
    main()
