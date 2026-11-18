"""Matplotlib artists, compact bands, legends and optional group labels."""

from __future__ import annotations

import math
from collections import defaultdict
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np
from .config import COLOR_RAMPS, FONT, LABEL_PAD, MARKER_STROKE, ChartStyle
from .models import Label, LayoutError, ChartScene, GroupLabelLayout
from .geometry import expanded, candidates_conflict
from .layout import marker_size, pack_band, make_candidates, solve_layout
from .validation import audit


def point_color(row, maximum, grayscale=False, shade=True):
    t = (row["Тексты"] - 1) / max(1, maximum - 1) if shade else 0.5
    if grayscale:
        # Preserve separate lightness ranges in the optional monochrome output.
        ramp = ("#666666", "#282828") if row["Пол"] == "M" else ("#d8d8d8", "#a5a5a5")
    else:
        ramp = COLOR_RAMPS[row["Пол"]]
    position = float(np.clip(t, 0, 1)) * (len(ramp) - 1)
    index = min(int(position), len(ramp) - 2)
    fraction = position - index
    return (
        np.array(to_rgb(ramp[index])) * (1 - fraction)
        + np.array(to_rgb(ramp[index + 1])) * fraction
    )


def point_edge_color(row, grayscale=False):
    return "#425665" if grayscale else COLOR_RAMPS[row["Пол"]][-1]


def draw_legends(fig, rows, grayscale, shade, top, legend_height, bar_height):
    maximum = max(r["Тексты"] for r in rows)
    height = fig.get_size_inches()[1] * 72
    # Keep font sizes and gradient dimensions; tighten the vertical gaps and
    # place the legend beside the title instead of stacking three header blocks.
    legend = fig.add_axes(
        [0.66, (top - legend_height) / height, 0.255, legend_height / height]
    )
    legend.set(xlim=(0, 1), ylim=(0, legend_height))
    legend.axis("off")
    legend.set_gid("gender-legend")
    title = legend.text(
        0,
        legend_height,
        "Пол и число текстов" if shade else "Пол",
        fontsize=10,
        fontweight="bold",
        va="top",
    )
    title.set_gid("legend-heading")
    for i, gender in enumerate(("M", "Ж")):
        y = legend_height - 14 - bar_height / 2 - i * (bar_height + 5)
        identifier = "M" if gender == "M" else "F"
        label = legend.text(
            0, y, "М" if gender == "M" else "Ж", fontsize=10, va="center"
        )
        label.set_gid("legend-gender-" + identifier)
        if shade:
            gradient = np.array(
                [
                    [
                        point_color(
                            {"Пол": gender, "Тексты": v}, maximum, grayscale, shade
                        )
                        for v in np.linspace(1, maximum, 180)
                    ]
                ]
            )
            swatch = legend.imshow(
                gradient,
                extent=(0.12, 0.98, y - bar_height / 2, y + bar_height / 2),
                aspect="auto",
            )
        else:
            swatch = legend.scatter(
                [0.16],
                [y],
                s=45,
                facecolor=[
                    point_color({"Пол": gender, "Тексты": 1}, maximum, grayscale, False)
                ],
                edgecolor=point_edge_color({"Пол": gender}, grayscale),
                linewidth=MARKER_STROKE,
            )
        swatch.set_gid("legend-swatch-" + identifier)
    for v in (
        sorted({1, min(10, maximum), min(20, maximum), maximum}) if shade else []
    ):
        x = 0.12 + 0.86 * (v - 1) / max(1, maximum - 1)
        label = legend.text(x, 0, str(v), fontsize=8.5, ha="center", va="bottom")
        label.set_gid(f"legend-tick-{v}")


def neutralize_colors(fig):
    """Make every artist grayscale, including legend swatches and typography."""
    from matplotlib.collections import Collection
    from matplotlib.patches import Patch
    from matplotlib.text import Text

    def gray(color):
        r, g, b, a = to_rgba(color)
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return (y, y, y, a)

    for artist in fig.findobj():
        if isinstance(artist, Text):
            artist.set_color(gray(artist.get_color()))
        elif isinstance(artist, Line2D):
            artist.set_color(gray(artist.get_color()))
        elif isinstance(artist, Collection):
            artist.set_facecolor([gray(c) for c in artist.get_facecolor()])
            artist.set_edgecolor([gray(c) for c in artist.get_edgecolor()])
        elif isinstance(artist, Patch):
            artist.set_facecolor(gray(artist.get_facecolor()))
            artist.set_edgecolor(gray(artist.get_edgecolor()))


def configure_axes(ax, xmin: float, xmax: float) -> None:
    """Set exact birth-year X and reserve a category-band Y axis."""
    ax.set(
        xlim=(xmin, xmax), ylim=(0, 1), xlabel="Год рождения", ylabel="Число источников"
    )
    ax.set_xticks(np.arange(math.ceil(xmin / 10) * 10, xmax + 1, 10))
    ax.set_xticks(np.arange(math.ceil(xmin / 5) * 5, xmax + 1, 5), minor=True)
    ax.xaxis.labelpad = 13
    ax.yaxis.labelpad = 20
    ax.xaxis.label.set_size(11)
    ax.yaxis.label.set_size(11)
    ax.xaxis.label.set_gid("birth-year-axis-label")
    ax.yaxis.label.set_gid("sources-axis-label")
    ax.tick_params(axis="x", length=0, pad=9, labelcolor="#465664")
    ax.tick_params(axis="y", length=0, pad=15, labelsize=12)
    ax.tick_params(which="minor", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_header(
    fig,
    rows,
    grayscale,
    shade,
    width_pt,
    height_pt,
    header_top,
    legend_height,
    bar_height,
) -> dict:
    """Place the title and compact gender legend; return their HTML anchor positions."""
    fig.text(
        0.068,
        0.963,
        "Поэты по году рождения и числу источников",
        fontsize=21,
        fontweight="bold",
        color="#223747",
        va="top",
    )
    subtitle = fig.text(
        0.068,
        (header_top - 32) / height_pt,
        f"{len(rows)} строк данных.",
        fontsize=10.5,
        color="#52616e",
        va="top",
    )
    subtitle.set_gid("chart-subtitle")
    draw_legends(fig, rows, grayscale, shade, header_top, legend_height, bar_height)
    header = {
        "captionX": 0.068 * width_pt,
        "captionY": height_pt - header_top + 42.5,
        "legendX": 0.66 * width_pt,
        "legendTop": height_pt - header_top,
        "legendHeight": legend_height,
        "legendFontSize": 10,
        "axisFontSize": 11,
        "shading": shade,
    }
    return header


def pack_source_bands(rows, ax, frame, fontsize, first_row_gap, style: ChartStyle):
    """Pack exact-X markers and allocate height, excluding band 1 from surplus space.

    Returns packed markers, band boundaries, the final axes frame and its height.
    With only band 1, the axes themselves shrink to the compact band height.
    """
    available_height = frame[3] - frame[1]
    levels = sorted({int(r["Источники"]) for r in rows})
    packed, heights = {}, {}
    for level in levels:
        rs = [r for r in rows if r["Источники"] == level]
        packed[level], span = pack_band(
            rs, ax, style, first_row_gap if level == 1 else 1.6, compact=level == 1
        )
        number_labels = sum(r["Топ-10"] == "Y" for r in rs)
        heights[level] = (
            max(36, span + 12, 2 * fontsize + 12)
            if level == 1
            else max(47, span + 2 * fontsize + 12, 40 + 1.6 * number_labels)
        )
    if sum(heights.values()) > available_height:
        raise LayoutError(
            f"Полосам нужно {sum(heights.values()):.0f} pt; доступно {available_height:.0f} pt"
        )
    # Do not spread surplus whitespace into the compact first band.
    flexible = [level for level in levels if level != 1]
    spare = (available_height - sum(heights.values())) / max(1, len(flexible))
    if not flexible:
        available_height = heights[1]
        ax.set_position(
            [
                0.068,
                0.14,
                0.847,
                available_height / (ax.figure.get_size_inches()[1] * 72),
            ]
        )
        ax.figure.canvas.draw()
        frame = np.array(ax.get_window_extent().extents) / (ax.figure.dpi / 72)
    ax.set_ylim(0, available_height)
    bands, cursor = {}, 0.0
    for level in levels:
        height = heights[level] + (spare if level != 1 else 0)
        bands[level] = (cursor, cursor + height)
        cursor += height
    centers = [(a + b) / 2 for a, b in bands.values()]
    ax.set_yticks(centers, [str(s) for s in levels])
    return packed, bands, frame, available_height


def draw_reference_regions(fig, ax, regions, bands, available_height) -> None:
    """Render optional annotations from the reference, not statistical clusters."""
    levels = list(bands)
    if regions:
        # These remain optional image annotations, never asserted to be data clusters.
        def band_boundary(v):
            if v <= min(levels) - 0.5:
                return 0
            if v >= max(levels) + 0.5:
                return available_height
            keys = [min(levels) - 0.5] + [s + 0.5 for s in levels]
            vals = [0] + [bands[s][1] for s in levels]
            return float(np.interp(v, keys, vals))

        for region in regions:
            x0, x1, y0, y1 = region["bounds"]
            a, b = band_boundary(y0), band_boundary(y1)
            patch = Rectangle(
                (x0, a),
                x1 - x0,
                b - a,
                fill=False,
                edgecolor="#999999",
                lw=0.8,
                linestyle=region["style"],
                zorder=2,
            )
            patch.set_gid("reference-region-" + str(region["name"]))
            ax.add_patch(patch)
    if regions:
        fig.text(
            0.068,
            0.027,
            "Рамки перенесены с образца приблизительно; их границы и названия не заданы в Excel.",
            fontsize=8.5,
            color="#6b6b6b",
        )
        fig.legend(
            [
                Line2D([], [], linestyle=r["style"], color="#888888", lw=0.9)
                for r in regions
            ],
            [f"Область {r['name']}" for r in regions],
            frameon=False,
            ncol=len(regions),
            loc="lower left",
            bbox_to_anchor=(0.065, 0.004),
            fontsize=8.5,
            handlelength=3,
        )


def make_label_artist(fig, row: dict, fontsize: float):
    """Create one named SVG text group and measure its unpadded pixel bounds."""
    artist = fig.text(
        0,
        0,
        row["Поэт"],
        fontsize=fontsize,
        va="bottom",
        ha="left",
        color="#223440",
        zorder=6,
        parse_math=False,
    )
    artist.set_gid(f'label-row-{row["_row"]}')
    bounds = artist.get_window_extent(fig.canvas.get_renderer())
    return artist, bounds


def create_figure(
    rows,
    regions,
    figsize,
    fontsize,
    dpi,
    grayscale=False,
    shade=True,
    first_row_gap=0.4,
    *,
    style: ChartStyle,
):
    plt.rcParams.update(
        {
            "font.family": FONT,
            "font.size": 10,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "path",
            "axes.unicode_minus": False,
            "image.composite_image": False,
        }
    )
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor="white")
    width_pt, height_pt = np.asarray(figsize) * 72
    header_top = 0.963 * height_pt
    bar_height = 0.079 * 0.17 * height_pt
    legend_height = 14 + 2 * bar_height + 5 + 14
    plot_top = header_top - legend_height - 22
    ax = fig.add_axes([0.068, 0.14, 0.847, plot_top / height_pt - 0.14])
    ax.set_gid("scatter-axes")
    years = [r["Год рождения"] for r in rows]
    xmin, xmax = min(years) - 4, max(years) + 4
    configure_axes(ax, xmin, xmax)
    header = draw_header(
        fig,
        rows,
        grayscale,
        shade,
        width_pt,
        height_pt,
        header_top,
        legend_height,
        bar_height,
    )
    fig.canvas.draw()
    pixels_per_point = dpi / 72
    frame = np.array(ax.get_window_extent().extents) / pixels_per_point
    try:
        packed, bands, frame, available_height = pack_source_bands(
            rows,
            ax,
            frame,
            fontsize,
            first_row_gap,
            style,
        )
    except LayoutError:
        plt.close(fig)
        raise
    levels = list(bands)
    maximum = max(r["Тексты"] for r in rows)
    count_heading = fig.text(
        0.947,
        (frame[3] + 12) / height_pt,
        "Записей",
        fontsize=9,
        ha="center",
        color="#66737e",
    )
    count_heading.set_gid("record-count-heading")
    markers, boxes, coords, labels = [], [], [], []
    for index, level in enumerate(levels):
        bottom, top = bands[level]
        center = (bottom + top) / 2
        ax.axhspan(
            bottom, top, facecolor="#f4f7f9" if index % 2 == 0 else "#ffffff", zorder=0
        )
        ax.axhline(bottom, color="#dce3e8", linewidth=0.65, zorder=1)
        count_label = fig.text(
            0.947,
            (frame[1] + center) / (figsize[1] * 72),
            str(len(packed[level])),
            fontsize=11,
            ha="center",
            va="center",
            color="#4e6474",
        )
        count_label.set_gid(f"band-count-{level}")
        for p in packed[level]:
            row = p["row"]
            y = center + p["offset"]
            display = (float(row["Год рождения"]), float(y))
            shape = "P" if row["Поэт года"] == "Y" else "o"
            artist = ax.scatter(
                *display,
                s=marker_size(row, style),
                marker=shape,
                facecolors=[point_color(row, maximum, grayscale, shade)],
                edgecolors=point_edge_color(row, grayscale),
                linewidths=MARKER_STROKE,
                zorder=4,
            )
            artist.set_gid(f'poet-row-{row["_row"]}')
            anchor = ax.transData.transform(display) / pixels_per_point
            radius = math.sqrt(marker_size(row, style)) / 2
            raw_box = expanded(np.tile(anchor, 2), radius + MARKER_STROKE / 2)
            box = expanded(raw_box, style.point_padding)
            boxes.append(box)
            coords.append(display)
            markers.append(
                {
                    "row": row,
                    "display": display,
                    "anchor_pt": anchor.tolist(),
                    "raw_box_pt": raw_box.tolist(),
                    "band": level,
                    "offset_pt": float(p["offset"]),
                    "size": marker_size(row, style),
                }
            )
            if row["Топ-10"] != "Y":
                continue
            text, bb = make_label_artist(fig, row, fontsize)
            label = Label(
                row["Поэт"],
                display,
                [row["_row"]],
                anchor,
                box,
                bb.width / pixels_per_point,
                bb.height / pixels_per_point,
                text,
                radius,
                shape,
                np.array(
                    [
                        frame[0] + 3,
                        frame[1] + bottom + 2,
                        frame[2] - 3,
                        frame[1] + top - 2,
                    ]
                ),
            )
            labels.append(label)
    ax.axhline(available_height, color="#dce3e8", linewidth=0.65, zorder=1)
    ax.grid(axis="x", which="major", color="#e2e8ed", linewidth=0.6)
    ax.grid(axis="x", which="minor", color="#edf1f4", linewidth=0.4)
    ax.set_axisbelow(True)
    draw_reference_regions(fig, ax, regions, bands, available_height)
    return ChartScene(
        figure=fig,
        axes=ax,
        labels=labels,
        obstacle_boxes=np.array(boxes),
        obstacle_coords=np.array(coords),
        frame=frame,
        layout_frame=expanded(frame, -1),
        markers=markers,
        bands=bands,
        xlim=[xmin, xmax],
        font_size=fontsize,
        header=header,
        style=style,
    )


def apply_layout(fig, labels, solution, style: ChartStyle):
    width_pt, height_pt = fig.get_size_inches() * 72
    lines = []
    for label, candidate in zip(labels, solution):
        label.artist.set_position(
            (
                (candidate.box[0] + LABEL_PAD) / width_pt,
                (candidate.box[1] + LABEL_PAD) / height_pt,
            )
        )
        # A straight leader with a small gap to both marker and text.
        start, end = candidate.start / [width_pt, height_pt], candidate.end / [
            width_pt,
            height_pt,
        ]
        line = Line2D(
            [start[0], end[0]],
            [start[1], end[1]],
            transform=fig.transFigure,
            lw=style.leader_width,
            color="#506473",
            solid_capstyle="round",
            zorder=3,
        )
        line.set_gid(f"leader-row-{label.source_rows[0]}")
        fig.add_artist(line)
        lines.append(line)
    return lines


def prepare_group_labels(scene: ChartScene, solution, dpi, seed) -> GroupLabelLayout:
    """Add the missing group names, with a checked layout for each selection.

    Existing names stay in place. Faded background marks may be overlapped,
    but selected marks, labels and leaders cannot overlap at default sizes.
    Extra artists are hidden for static exports and enabled only in HTML.
    """
    fig, labels, style = scene.figure, scene.labels, scene.style
    existing = {
        label.source_rows[0]: (label, candidate)
        for label, candidate in zip(labels, solution)
    }
    by_group = defaultdict(list)
    for marker in scene.markers:
        if marker["row"]["_group"]:
            by_group[marker["row"]["_group"]].append(marker)
    extra_labels, extra_solution, extra_lines, checks = [], [], [], []
    for group, markers in sorted(by_group.items()):
        boxes = np.array(
            [expanded(m["raw_box_pt"], style.point_padding) for m in markers]
        )
        coords = np.array([m["display"] for m in markers])
        fixed = [
            existing[m["row"]["_row"]] for m in markers if m["row"]["_row"] in existing
        ]
        missing = []
        for marker, box in zip(markers, boxes):
            row = marker["row"]
            if row["_row"] in existing:
                continue
            artist, bb = make_label_artist(fig, row, scene.font_size)
            bottom, top = scene.bands[marker["band"]]
            x0, y0, x1, _ = scene.frame
            label = Label(
                row["Поэт"],
                marker["display"],
                [row["_row"]],
                np.array(marker["anchor_pt"]),
                box,
                bb.width * 72 / fig.dpi,
                bb.height * 72 / fig.dpi,
                artist,
                math.sqrt(marker["size"]) / 2,
                "P" if row["Поэт года"] == "Y" else "o",
                np.array([x0 + 3, y0 + bottom + 2, x1 - 3, y0 + top - 2]),
            )
            missing.append(label)
        options = [
            [
                candidate
                for candidate in make_candidates(
                    label, boxes, coords, label.band_frame, style
                )
                if all(
                    not candidates_conflict(candidate, other, style.line_padding)
                    for _, other in fixed
                )
            ]
            for label in missing
        ]
        placed = solve_layout(options, style, seed)
        if placed is None:
            raise LayoutError(f"Не удалось разместить все подписи группы {group}")
        lines = apply_layout(fig, missing, placed, style)
        group_labels = [label for label, _ in fixed] + missing
        group_solution = [candidate for _, candidate in fixed] + placed
        group_checks = [
            audit(
                fig,
                group_labels,
                group_solution,
                boxes,
                coords,
                scene.layout_frame,
                resolution,
                style,
            )
            for resolution in sorted(set((72, dpi)))
        ]
        checks.append(
            {
                "group": group,
                "labels": len(group_labels),
                "additional_labels": len(missing),
                "checks": group_checks,
            }
        )
        for artist in [*[label.artist for label in missing], *lines]:
            artist.set_visible(False)
        extra_labels.extend(missing)
        extra_solution.extend(placed)
        extra_lines.extend(lines)
    return GroupLabelLayout(extra_labels, extra_solution, extra_lines, checks)
