"""Independent checks of the actual rendered text and leader geometry."""

from __future__ import annotations

import numpy as np
from .config import ChartStyle
from .geometry import (
    expanded,
    overlaps_any,
    overlap,
    segment_box_hits,
    segment_distance,
)
from .models import LayoutError, ChartScene


def audit(
    fig,
    labels,
    solution,
    obstacle_boxes,
    obstacle_coords,
    frame,
    dpi,
    style: ChartStyle,
):
    """Re-render and verify ACTUAL text bounds, independently of placement."""
    fig.set_dpi(dpi)
    fig.canvas.draw()
    scale = fig.dpi / 72
    boxes = [
        expanded(
            label.artist.get_window_extent(fig.canvas.get_renderer()).extents / scale,
            1.5,
        )
        for label in labels
    ]
    errors = []
    counts = {
        "label_label": 0,
        "label_marker": 0,
        "leader_label": 0,
        "leader_marker": 0,
        "leader_leader": 0,
        "outside_axes": 0,
    }
    for i, (label, box, candidate) in enumerate(zip(labels, boxes, solution)):
        if (
            box[0] < frame[0]
            or box[1] < frame[1]
            or box[2] > frame[2]
            or box[3] > frame[3]
        ):
            counts["outside_axes"] += 1
            errors.append(f"За рамкой: {label.text}")
        if overlaps_any(box, obstacle_boxes):
            counts["label_marker"] += 1
            errors.append(f"Подпись/маркер: {label.text}")
        other = obstacle_boxes[np.any(obstacle_coords != label.coord, axis=1)]
        if np.any(segment_box_hits(candidate.start, candidate.end, other)):
            counts["leader_marker"] += 1
        for j in range(i):
            if overlap(box, boxes[j]):
                counts["label_label"] += 1
                errors.append(f"Подписи: {label.text} / {labels[j].text}")
            if (
                segment_distance(
                    candidate.start, candidate.end, solution[j].start, solution[j].end
                )
                <= 2 * style.line_padding
            ):
                counts["leader_leader"] += 1
        for j, other_box in enumerate(boxes):
            if (
                i != j
                and segment_box_hits(
                    candidate.start,
                    candidate.end,
                    [expanded(other_box, style.line_padding)],
                )[0]
            ):
                counts["leader_label"] += 1
    if any(counts.values()):
        raise LayoutError(f"Проверка при {dpi} dpi не пройдена: {counts}; {errors[:5]}")
    return {"dpi": dpi, **counts}


def validate_placement(scene: ChartScene, candidates) -> int:
    """Check marker separation and that every label stays in its source band."""
    raw_boxes = [np.array(marker["raw_box_pt"]) for marker in scene.markers]
    marker_hits = sum(
        overlap(box, other)
        for index, box in enumerate(raw_boxes)
        for other in raw_boxes[:index]
    )
    if marker_hits:
        raise LayoutError(f"Пересечения маркеров: {marker_hits}")
    for label, candidate in zip(scene.labels, candidates):
        band = label.band_frame
        box = candidate.box
        if not (
            band[0] <= box[0]
            and band[1] <= box[1]
            and band[2] >= box[2]
            and band[3] >= box[3]
        ):
            raise LayoutError("Подпись вышла из своей полосы")
    return marker_hits
