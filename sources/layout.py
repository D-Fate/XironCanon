"""Deterministic marker packing and collision-free label search."""

from __future__ import annotations

import math
import numpy as np
from .config import AREA_PER_UNIT, LABEL_PAD, MARKER_STROKE, ChartStyle
from .geometry import candidates_conflict, overlaps_any, segment_box_hits
from .models import Candidate, Label


def marker_size(row: dict, style: ChartStyle) -> float:
    # MarkerStyle('o') has unit diameter; P occupies 5/9 of its bounding square.
    unit_area = math.pi / 4 if row["Поэт года"] == "N" else 5 / 9
    return AREA_PER_UNIT * style.marker_scale**2 * row["Топ-№"] / unit_area


def pack_band(records, ax, style: ChartStyle, gap=1.6, compact=False):
    """Vertical packing at exact X, with a configurable edge-to-edge gap."""
    placed = []
    order = (
        (lambda r: (r["Топ-10"] == "Y", -marker_size(r, style), r["_row"]))
        if compact
        else (lambda r: (-marker_size(r, style), r["Топ-10"] != "Y", r["_row"]))
    )
    for row in sorted(records, key=order):
        x = ax.transData.transform((row["Год рождения"], 0))[0] * 72 / ax.figure.dpi
        half = math.sqrt(marker_size(row, style)) / 2 + MARKER_STROKE / 2
        neighbors = [p for p in placed if abs(x - p["x"]) < half + p["half"] + gap]
        candidates = [0.0]
        for p in neighbors:
            d = half + p["half"] + gap
            candidates.extend([p["offset"] - d, p["offset"] + d])
        valid = [
            y
            for y in candidates
            if all(
                abs(y - p["offset"]) >= half + p["half"] + gap - 1e-8 for p in neighbors
            )
        ]
        # In the crowded first row, place named markers at the top of their
        # local stack: their callouts can leave the stack without crossing it.
        y = (
            max(valid)
            if compact and row["Топ-10"] == "Y"
            else min(valid, key=lambda v: (abs(v), v > 0))
        )
        placed.append({"row": row, "x": x, "half": half, "offset": y})
    low = min(p["offset"] - p["half"] for p in placed)
    high = max(p["offset"] + p["half"] for p in placed)
    for p in placed:
        p["offset"] -= (low + high) / 2
    return placed, high - low


def make_candidates(
    label: Label, obstacle_boxes, obstacle_coords, frame, style: ChartStyle
) -> list[Candidate]:
    """Reject all point collisions BEFORE trying combinations of labels."""
    options = []
    x, y = label.anchor
    w, h = label.width + 2 * LABEL_PAD, label.height + 2 * LABEL_PAD
    rx = (label.own_box[2] - label.own_box[0]) / 2
    ry = (label.own_box[3] - label.own_box[1]) / 2
    other = obstacle_boxes[np.any(obstacle_coords != label.coord, axis=1)]
    seen = set()
    # Directions and distances are deterministic; no random jitter of data.
    angles = np.radians(np.arange(0, 360, 15))
    for gap in (7, 12, 19, 28, 40, 55, 73, 95, 125, 165):
        for theta in angles:
            cx = x + math.cos(theta) * (w / 2 + rx + gap)
            cy = y + math.sin(theta) * (h / 2 + ry + gap)
            box = np.array([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])
            key = tuple(np.round(box, 2))
            if key in seen:
                continue
            seen.add(key)
            if (
                box[0] < frame[0]
                or box[1] < frame[1]
                or box[2] > frame[2]
                or box[3] > frame[3]
            ):
                continue
            if overlaps_any(box, obstacle_boxes):
                continue
            end = np.clip(label.anchor, box[:2], box[2:])
            direction = end - label.anchor
            length = np.linalg.norm(direction)
            if length < 1e-9:
                continue
            # Connect to the actual circle / cross contour, not its empty corners.
            u = direction / length
            if label.marker == "o":
                edge_distance = label.radius
            else:
                ux, uy = max(abs(u[0]), 1e-12), max(abs(u[1]), 1e-12)
                r = label.radius
                edge_distance = max(
                    min(r / ux, r / (3 * uy)), min(r / (3 * ux), r / uy)
                )
            start = label.anchor + u * (
                edge_distance
                + MARKER_STROKE / 2
                + max(0.8, style.leader_width / 2 + 0.3)
            )
            if np.dot(end - start, direction) <= 0:
                continue
            if np.any(segment_box_hits(start, end, other)):
                continue
            score = float(np.linalg.norm(end - start) + 0.05 * length)
            # Mild preference for above/below over labels extending along a row.
            score += 2.0 * abs(math.cos(theta)) + (0.3 if cy < y else 0)
            options.append(Candidate(box, start, end, score))
    return sorted(options, key=lambda option: option.score)


def solve_layout(candidates, style: ChartStyle, seed=17, restarts=100):
    """Finite reproducible search. Only collision-free solutions are returned."""
    if any(not options for options in candidates):
        return None
    rng = np.random.default_rng(seed)
    difficulty = np.argsort([len(options) for options in candidates], kind="stable")
    priority = np.zeros(len(candidates))
    for attempt in range(restarts):
        if attempt == 0:
            order = difficulty
        else:
            order = np.argsort(
                np.log1p([len(o) for o in candidates])
                - 0.9 * priority
                + rng.normal(0, 0.45, len(candidates))
            )
        placed = {}
        failed = None
        for i in order:
            found = None
            for candidate in candidates[i]:
                if all(
                    not candidates_conflict(candidate, p, style.line_padding)
                    for p in placed.values()
                ):
                    found = candidate
                    break
            if found is None:
                failed = i
                break
            placed[int(i)] = found
        if failed is None:
            return [placed[i] for i in range(len(candidates))]
        priority[failed] += 1
    return None
