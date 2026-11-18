"""Explicit records shared by placement, rendering and export.

Python geometry uses physical points with the origin at the lower left.
Only the HTML exporter converts it to SVG coordinates (origin at the top left).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.text import Text
from .config import ChartStyle


class LayoutError(RuntimeError):
    """The current canvas cannot accommodate a verified collision-free layout."""


@dataclass
class Label:
    text: str
    coord: tuple[float, float]
    source_rows: list[int]
    anchor: np.ndarray
    own_box: np.ndarray
    width: float
    height: float
    artist: Text
    radius: float
    marker: str
    band_frame: np.ndarray


@dataclass
class Candidate:
    """One proposed label box and its leader, in physical points."""

    box: np.ndarray  # [left, bottom, right, top], including text clearance
    start: np.ndarray
    end: np.ndarray
    score: float


@dataclass
class ChartScene:
    """Rendered artists and geometry; no custom attributes on Matplotlib objects."""

    figure: Figure
    axes: Axes
    labels: list[Label]
    obstacle_boxes: np.ndarray
    obstacle_coords: np.ndarray
    frame: np.ndarray
    layout_frame: np.ndarray
    markers: list[dict[str, Any]]
    bands: dict[int, tuple[float, float]]
    xlim: list[float]
    font_size: float
    header: dict[str, Any]
    style: ChartStyle


@dataclass
class GroupLabelLayout:
    """Extra group-only labels, hidden in static output, plus their checks."""

    labels: list[Label] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    leaders: list[Line2D] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)

    def set_visible(self, visible: bool) -> None:
        for label in self.labels:
            label.artist.set_visible(visible)
        for leader in self.leaders:
            leader.set_visible(visible)


@dataclass
class ChartResult:
    """A successful, audited layout ready for all output formats."""

    scene: ChartScene
    candidates: list[Candidate]
    checks: list[dict[str, Any]]
    group_layout: GroupLabelLayout
    marker_collisions: int
