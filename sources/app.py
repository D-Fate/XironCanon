"""Command-line interface and the read → lay out → check → export workflow."""

from __future__ import annotations
import argparse
import math
import sys
import json
from pathlib import Path
from .config import ChartStyle, REFERENCE_REGIONS
from .models import LayoutError, ChartResult, GroupLabelLayout
from .data import read_data
from .layout import make_candidates, solve_layout
from .rendering import (
    create_figure,
    apply_layout,
    prepare_group_labels,
    neutralize_colors,
    plt,
)
from .validation import audit, validate_placement
from .exporting import export_outputs, write_audit_report

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLI_DESCRIPTION = """Poets chart: checked callouts, group focus and offline snapshots.

Run: python sources/plot_poets.py
Custom data: python sources/plot_poets.py "data.xlsx" --out poets

X is the exact birth year; Y is a category band for the source count.
Open the resulting HTML to select groups, adjust sizes and save snapshots.
By default only HTML is written; collision checks always run before export.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    default_style = ChartStyle()
    parser = argparse.ArgumentParser(
        description=CLI_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "excel",
        nargs="?",
        type=Path,
        default=PROJECT_ROOT / "1. xiron. v2.0.xlsx",
        help="Excel-файл (по умолчанию приложенный файл в корне проекта)",
    )
    parser.add_argument("--sheet", default="Data")
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "poets")
    parser.add_argument("--width", type=float, default=18)
    parser.add_argument("--height", type=float, default=12.5)
    parser.add_argument(
        "--font-size",
        type=float,
        default=14,
        help="Размер подписей имён, pt (по умолчанию 14)",
    )
    parser.add_argument("--dpi", type=int, default=220)
    parser.add_argument(
        "--marker-scale",
        type=float,
        default=default_style.marker_scale,
        help="Масштаб диаметра маркеров относительно исходной версии (по умолчанию %(default)s)",
    )
    parser.add_argument(
        "--leader-width",
        type=float,
        default=default_style.leader_width,
        help="Толщина линий от точек к подписям, pt (по умолчанию %(default)s)",
    )
    parser.add_argument(
        "--first-row-gap",
        type=float,
        default=0.4,
        help="Зазор между маркерами в полосе Источники=1, pt (по умолчанию 0.4)",
    )
    parser.add_argument("--max-scale", type=float, default=1.8)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--grayscale", action="store_true")
    parser.add_argument("--no-shading", action="store_true")
    parser.add_argument(
        "--reference-regions",
        action="store_true",
        help="Добавить приблизительные рамки с образца",
    )
    parser.add_argument(
        "--regions", type=Path, help="JSON с вручную заданными областями"
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        choices=("png", "pdf", "svg"),
        default=(),
        help="Дополнительные статические форматы; включает также CSV и отчёт проверки",
    )
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Создать только статические форматы и отчёт, без HTML и CSV",
    )
    parser.add_argument(
        "--csv", action="store_true", help="Дополнительно сохранить CSV"
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Дополнительно сохранить отчёт проверки JSON",
    )
    args = parser.parse_args(argv)
    # Explicit requests for the old static-export modes retain their full output set.
    # An ordinary launch now writes only the standalone HTML requested by the project.
    if args.static_only and not args.formats:
        args.formats = ("png", "pdf", "svg")
    args.csv = args.csv or bool(args.formats)
    args.audit = args.audit or bool(args.formats)
    return args


def validate_arguments(args: argparse.Namespace) -> None:
    """Reject invalid dimensions before opening data or creating artists."""
    dimensions = (
        args.width,
        args.height,
        args.font_size,
        args.dpi,
        args.max_scale,
        args.leader_width,
        args.first_row_gap,
        args.marker_scale,
    )
    if not all(math.isfinite(value) for value in dimensions):
        raise ValueError("Параметры размеров должны быть конечными числами")
    if (
        min(
            args.width,
            args.height,
            args.font_size,
            args.dpi,
            args.leader_width,
            args.marker_scale,
        )
        <= 0
        or args.max_scale < 1
    ):
        raise ValueError("Размеры и dpi должны быть положительными, max-scale >= 1")
    if args.first_row_gap <= 0:
        raise ValueError("first-row-gap должен быть положительным")


def read_regions(args: argparse.Namespace) -> list[dict]:
    """Load optional, manually supplied annotations; never infer data clusters."""
    regions = REFERENCE_REGIONS if args.reference_regions else []
    if args.regions:
        regions = json.loads(args.regions.read_text(encoding="utf-8"))
    for region in regions:
        bounds = region["bounds"]
        if (
            len(bounds) != 4
            or not all(math.isfinite(value) for value in bounds)
            or bounds[0] >= bounds[1]
            or bounds[2] >= bounds[3]
        ):
            raise ValueError(f"Некорректная область: {region}")
    return regions


def canvas_scales(maximum: float) -> list[float]:
    """The same finite retry schedule as the original single-file version."""
    return sorted(
        {1.0, *(scale for scale in (1.12, 1.3, 1.55, 1.8) if scale <= maximum), maximum}
    )


def build_chart(
    rows: list[dict], regions: list[dict], args: argparse.Namespace
) -> ChartResult:
    """Try larger canvases until both general and group layouts pass all checks."""
    style = ChartStyle(marker_scale=args.marker_scale, leader_width=args.leader_width)
    for scale in canvas_scales(args.max_scale):
        figsize = (args.width * scale, args.height * scale)
        try:
            scene = create_figure(
                rows,
                regions,
                figsize,
                args.font_size,
                args.dpi,
                args.grayscale,
                not args.no_shading,
                args.first_row_gap,
                style=style,
            )
        except LayoutError as error:
            print(error, flush=True)
            continue

        options = [
            make_candidates(
                label,
                scene.obstacle_boxes,
                scene.obstacle_coords,
                label.band_frame,
                style,
            )
            for label in scene.labels
        ]
        print(
            f"Холст {figsize[0]:g} × {figsize[1]:g}; маркеров {len(rows)}; "
            f"подписей {len(scene.labels)}; поиск...",
            flush=True,
        )
        candidates = solve_layout(options, style, args.seed)
        if candidates is None:
            plt.close(scene.figure)
            continue

        apply_layout(scene.figure, scene.labels, candidates, style)
        try:
            checks = [
                audit(
                    scene.figure,
                    scene.labels,
                    candidates,
                    scene.obstacle_boxes,
                    scene.obstacle_coords,
                    scene.layout_frame,
                    dpi,
                    style,
                )
                for dpi in sorted({72, args.dpi})
            ]
            marker_collisions = validate_placement(scene, candidates)
            group_layout = (
                GroupLabelLayout()
                if args.static_only
                else prepare_group_labels(scene, candidates, args.dpi, args.seed)
            )
            if args.grayscale:
                neutralize_colors(scene.figure)
        except LayoutError as error:
            print(error, file=sys.stderr)
            plt.close(scene.figure)
            continue

        return ChartResult(scene, candidates, checks, group_layout, marker_collisions)

    raise LayoutError(
        "Не найдена расстановка без пересечений. Увеличьте --width/--height/--max-scale."
    )


def main(argv=None) -> int:
    """Build all requested outputs; repeated calls do not share mutable settings."""
    args = parse_args(argv)
    validate_arguments(args)
    rows, warnings = read_data(args.excel, args.sheet)
    regions = read_regions(args)
    for warning in warnings:
        print("Внимание:", warning, file=sys.stderr)

    result = build_chart(rows, regions, args)
    try:
        assert len(result.scene.labels) == sum(row["Топ-10"] == "Y" for row in rows)
        assert len(result.scene.markers) == len(rows)
        outputs = export_outputs(result, rows, args)
        if args.audit:
            write_audit_report(result, rows, regions, warnings, outputs, args)
    finally:
        plt.close(result.scene.figure)

    print(
        f"Готово: {len(rows)} отдельных маркеров, {len(result.scene.labels)} "
        "индивидуальных подписей; все пересечения = 0.",
        flush=True,
    )
    return 0


def run_cli() -> int:
    """Translate expected input/layout failures into the existing CLI exit code."""
    try:
        return main()
    except (ValueError, LayoutError, FileNotFoundError, KeyError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
