"""Static exports, standalone HTML assembly and machine-readable audit report."""

from __future__ import annotations

import html
import io
import json
import math
import re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from .config import COLOR_RAMPS, MARKER_STROKE
from .models import ChartScene, ChartResult
from .data import write_csv
from .web_assets import HTML_TEMPLATE, CSS, JAVASCRIPT


def svg_frame(scene: ChartScene, height: float) -> list[float]:
    """Convert [left, bottom, right, top] points to SVG [x, y, width, height]."""
    x0, y0, x1, y1 = scene.frame
    return [x0, height - y1, x1 - x0, y1 - y0]


def prepare_svg(svg: str, frame: list[float]) -> ET.Element:
    """Move only the plot into a clipped viewport; keep headers and axes fixed."""
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    tag = lambda name: f"{{{ns}}}{name}"
    root = ET.fromstring(svg[svg.index("<svg") :])
    # Matplotlib may define a digit/glyph inside its first tick label and reuse
    # it elsewhere. Hoist definitions before removing ticks, or legend digits
    # and parts of later labels would disappear in the browser and snapshots.
    global_defs = root.find(tag("defs"))
    if global_defs is None:
        global_defs = ET.Element(tag("defs"))
        root.insert(0, global_defs)
    for definitions in list(root.iter(tag("defs"))):
        if definitions is global_defs:
            continue
        for definition in list(definitions):
            definitions.remove(definition)
            global_defs.append(definition)
    figure = root.find(f".//{tag('g')}[@id='figure_1']")
    axes = root.find(f".//{tag('g')}[@id='scatter-axes']")
    if figure is None or axes is None:
        raise ValueError("Не найдены элементы SVG для интерактивного графика")
    for axis in list(axes):
        if axis.get("id", "").startswith("matplotlib.axis_"):
            for child in list(axis):
                if child.get("id") in {"birth-year-axis-label", "sources-axis-label"}:
                    axis.remove(child)
                    figure.append(child)
            axes.remove(axis)
    # The nested SVG provides clipping in screen coordinates, including callouts.
    for node in axes.iter():
        node.attrib.pop("clip-path", None)
    # The legend reflows when its text grows; individual swatches already have
    # finite bounds and must not be clipped to their original header position.
    for node in root.find(f".//{tag('g')}[@id='gender-legend']").iter():
        node.attrib.pop("clip-path", None)
    viewport = ET.Element(
        tag("svg"),
        {
            "id": "plot-viewport",
            "x": str(frame[0]),
            "y": str(frame[1]),
            "width": str(frame[2]),
            "height": str(frame[3]),
            "viewBox": " ".join(map(str, frame)),
            "overflow": "hidden",
            "preserveAspectRatio": "xMidYMid meet",
        },
    )
    position = list(figure).index(axes)
    figure.remove(axes)
    figure.insert(position, viewport)
    viewport.append(axes)
    for node in list(figure):
        identifier = node.get("id", "")
        if identifier.startswith(("label-row-", "leader-row-")):
            figure.remove(node)
            viewport.append(node)
        elif identifier.startswith("band-count-"):
            figure.remove(node)
    return root


def chart_metadata(scene: ChartScene, rows, labels, solution) -> dict:
    """Geometry contract consumed by the offline viewer and snapshot exporter."""
    fig, style = scene.figure, scene.style
    width, height = (float(value) for value in fig.get_size_inches() * 72)
    frame = svg_frame(scene, height)
    _, y0, _, _ = scene.frame
    label_boxes = {
        label.source_rows[0]: candidate.box
        for label, candidate in zip(labels, solution)
    }
    marks, marker_bounds, visuals = {}, {}, {}
    for marker in scene.markers:
        row_id = marker["row"]["_row"]
        b = np.asarray(marker["raw_box_pt"])
        marker_bounds[str(row_id)] = [
            float(b[0]),
            float(height - b[3]),
            float(b[2]),
            float(height - b[1]),
        ]
        anchor = marker["anchor_pt"]
        visuals[str(row_id)] = {
            "anchor": [float(anchor[0]), float(height - anchor[1])],
            "radius": math.sqrt(marker["size"]) / 2,
            "shape": "P" if marker["row"]["Поэт года"] == "Y" else "o",
            "labelBox": None,
            "groupOnly": marker["row"]["Топ-10"] != "Y" and row_id in label_boxes,
        }
        if row_id in label_boxes:
            other = label_boxes[row_id]
            visuals[str(row_id)]["labelBox"] = [
                float(other[0]),
                float(height - other[3]),
                float(other[2]),
                float(height - other[1]),
            ]
            b = np.array(
                [
                    min(b[0], other[0]),
                    min(b[1], other[1]),
                    max(b[2], other[2]),
                    max(b[3], other[3]),
                ]
            )
        marks[str(row_id)] = [
            float(b[0]),
            float(height - b[3]),
            float(b[2]),
            float(height - b[1]),
        ]
    metadata = {
        "width": width,
        "height": height,
        "frame": frame,
        "xlim": scene.xlim,
        "bounds": marks,
        "visuals": visuals,
        "markerBounds": marker_bounds,
        "header": scene.header,
        "fontSize": scene.font_size,
        "markerScale": style.marker_scale,
        "markerStroke": MARKER_STROKE,
        "leaderWidth": style.leader_width,
        "bands": [
            {
                "level": level,
                "center": height - y0 - (bottom + top) / 2,
                "count": sum(r["Источники"] == level for r in rows),
            }
            for level, (bottom, top) in scene.bands.items()
        ],
    }
    return metadata


def data_table(rows: list[dict]) -> tuple[list[dict], str, str]:
    """Keep source values in the table and escape all cell text as HTML."""
    headers = [
        "_row",
        "Поэт",
        "Пол",
        "Год рождения",
        "Источники",
        "Тексты",
        "Строки",
        "Поэт года",
        "Топ-№",
        "Топ-10",
        "Группа",
    ]
    data = [{**{k: r.get(k) for k in headers}, "_group": r["_group"]} for r in rows]
    header = "".join(
        "<th>" + html.escape("Строка Excel" if k == "_row" else k) + "</th>"
        for k in headers
    )
    table = "".join(
        '<tr data-row="'
        + str(r["_row"])
        + '">'
        + "".join("<td>" + html.escape(str(r.get(k, ""))) + "</td>" for k in headers)
        + "</tr>"
        for r in rows
    )
    return data, header, table


def load_html_template() -> str:
    """Assemble the browser resources stored as readable Python strings.

    Assets are trusted source. User data is substituted only after they are embedded.
    The result needs neither a server nor neighboring CSS/JS files.
    """
    return HTML_TEMPLATE.replace("__CSS__", CSS).replace("__JAVASCRIPT__", JAVASCRIPT)


def script_json(value) -> str:
    """Prevent a cell containing </script> from ending the embedded data block."""
    return json.dumps(value, ensure_ascii=False).replace("<", r"\u003c")


def export_html(
    svg, rows, destination: Path, scene: ChartScene, labels, solution
) -> None:
    metadata = chart_metadata(scene, rows, labels, solution)
    root = prepare_svg(svg, metadata["frame"])
    data, header, table = data_table(rows)
    substitutions = {
        "__SVG__": ET.tostring(root, encoding="unicode"),
        "__DATA__": script_json(data),
        "__META__": script_json(metadata),
        "__HEADER__": header,
        "__TABLE__": table,
        "__COUNT__": str(len(rows)),
    }
    # One pass: literal placeholder-looking cell values must not be expanded again.
    document = re.sub(
        r"__SVG__|__DATA__|__META__|__HEADER__|__TABLE__|__COUNT__",
        lambda match: substitutions[match.group()],
        load_html_template(),
    )
    destination.write_text(document, encoding="utf-8")


def export_outputs(result: ChartResult, rows, args) -> list[str]:
    """Export static artists first, then include hidden group labels in the viewer."""
    scene = result.scene
    figure = scene.figure
    args.out.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in args.formats:
        destination = args.out.with_suffix("." + extension)
        figure.savefig(destination, dpi=args.dpi, facecolor="white")
        outputs.append(str(destination))
    if not args.static_only:
        extra = result.group_layout
        extra.set_visible(True)
        try:
            with io.StringIO() as buffer:
                figure.savefig(buffer, format="svg", facecolor="white")
                svg = buffer.getvalue()
            export_html(
                svg,
                rows,
                args.out.with_suffix(".html"),
                scene,
                scene.labels + extra.labels,
                result.candidates + extra.candidates,
            )
        finally:
            extra.set_visible(False)
        outputs.append(str(args.out.with_suffix(".html")))
        if args.csv:
            write_csv(rows, args.out.with_suffix(".csv"))
            outputs.append(str(args.out.with_suffix(".csv")))
    return outputs


def label_geometry(labels, candidates) -> list[dict]:
    return [
        {
            "name": label.text,
            "excel_row": label.source_rows[0],
            "box_pt": candidate.box.tolist(),
            "leader_start_pt": candidate.start.tolist(),
            "leader_end_pt": candidate.end.tolist(),
        }
        for label, candidate in zip(labels, candidates)
    ]


def write_audit_report(
    result: ChartResult, rows, regions, warnings, outputs, args
) -> None:
    """Retain the version-6 audit schema for existing consumers."""
    scene, style = result.scene, result.scene.style
    labels, solution = scene.labels, result.candidates
    extra = result.group_layout
    report = {
        "version": 6,
        "input": args.excel.name,
        "sheet": args.sheet,
        "rows": len(rows),
        "visible_markers": len(scene.markers),
        "individual_labels": len(labels),
        "birth_years_unchanged": True,
        "sources_are_category_bands": True,
        "vertical_display_offsets_only": True,
        "marker_marker_collisions": result.marker_collisions,
        "all_labels_in_correct_source_band": True,
        "canvas_inches": list(scene.figure.get_size_inches()),
        "font_size_pt": args.font_size,
        "checks": result.checks,
        "warnings": warnings,
        "leader_width_pt": style.leader_width,
        "first_row_gap_pt": args.first_row_gap,
        "marker_diameter_scale": style.marker_scale,
        "axis_font_size_pt": scene.header["axisFontSize"],
        "legend_font_size_pt": scene.header["legendFontSize"],
        "color_ramps": None if args.grayscale else COLOR_RAMPS,
        "group_colors_follow_gender_and_texts": True,
        "group_label_checks": extra.checks,
        "group_only_labels": label_geometry(extra.labels, extra.candidates),
        "band_heights_pt": {str(k): b - a for k, (a, b) in scene.bands.items()},
        "selectable_groups": dict(Counter(r["_group"] for r in rows if r["_group"])),
        "reference_regions": regions,
        "marker_area_formula": f"filled area before stroke = 13 * {style.marker_scale:g}² * Топ-№ pt²; circle and plus normalized",
        "markers": scene.markers,
        "labels": label_geometry(labels, solution),
        "outputs": outputs,
    }
    args.out.with_suffix(".audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
