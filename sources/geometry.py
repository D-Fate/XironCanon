"""Collision primitives for boxes and straight leader segments, in points."""

from __future__ import annotations

import numpy as np
from .models import Candidate


def overlap(a, b) -> bool:
    return bool(a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1])


def overlaps_any(box, boxes) -> bool:
    if len(boxes) == 0:
        return False
    return bool(
        np.any(
            (box[0] <= boxes[:, 2])
            & (box[2] >= boxes[:, 0])
            & (box[1] <= boxes[:, 3])
            & (box[3] >= boxes[:, 1])
        )
    )


def expanded(box, amount):
    return np.asarray(box) + np.array([-amount, -amount, amount, amount])


def segment_box_hits(a, b, boxes) -> np.ndarray:
    """Closed segment vs closed AABBs, using the slab intersection algorithm."""
    boxes = np.asarray(boxes, dtype=float).reshape(-1, 4)
    lo = np.zeros(len(boxes))
    hi = np.ones(len(boxes))
    live = np.ones(len(boxes), dtype=bool)
    for axis in (0, 1):
        d = b[axis] - a[axis]
        if abs(d) < 1e-12:
            live &= (a[axis] >= boxes[:, axis]) & (a[axis] <= boxes[:, axis + 2])
        else:
            t0 = (boxes[:, axis] - a[axis]) / d
            t1 = (boxes[:, axis + 2] - a[axis]) / d
            lo = np.maximum(lo, np.minimum(t0, t1))
            hi = np.minimum(hi, np.maximum(t0, t1))
    return live & (lo <= hi + 1e-10)


def point_segment_distance(p, a, b):
    v = b - a
    t = np.clip(np.dot(p - a, v) / max(np.dot(v, v), 1e-18), 0, 1)
    return float(np.linalg.norm(p - (a + t * v)))


def cross2(a, b):
    return float(a[0] * b[1] - a[1] * b[0])


def segment_distance(a, b, c, d):
    """Includes proper crossings, collinearity and near touches."""
    u, v = b - a, d - c
    det = cross2(u, v)
    if abs(det) > 1e-12:
        t, s = cross2(c - a, v) / det, cross2(c - a, u) / det
        if -1e-10 <= t <= 1 + 1e-10 and -1e-10 <= s <= 1 + 1e-10:
            return 0.0
    return min(
        point_segment_distance(a, c, d),
        point_segment_distance(b, c, d),
        point_segment_distance(c, a, b),
        point_segment_distance(d, a, b),
    )


def candidates_conflict(a: Candidate, b: Candidate, clearance: float) -> bool:
    return (
        overlap(a.box, b.box)
        or bool(segment_box_hits(a.start, a.end, [expanded(b.box, clearance)])[0])
        or bool(segment_box_hits(b.start, b.end, [expanded(a.box, clearance)])[0])
        or segment_distance(a.start, a.end, b.start, b.end) <= 2 * clearance
    )
