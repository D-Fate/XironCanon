"""Shared units, palettes and immutable per-chart appearance settings."""

from dataclasses import dataclass

COLUMNS = (
    "Поэт",
    "Пол",
    "Тексты",
    "Год рождения",
    "Источники",
    "Поэт года",
    "Топ-№",
    "Топ-10",
)
AREA_PER_UNIT = 13.0  # actual filled area (before stroke), pt² per Топ-№
MARKER_STROKE = 0.60
LABEL_PAD = 2.8  # reserved clearance around the actual rendered text
FONT = "DejaVu Sans"
COLOR_RAMPS = {
    "M": ("#ead28a", "#b58d2c", "#625013"),
    "Ж": ("#9ed8ca", "#399d8f", "#07584e"),
}

# Approximate, manually configurable regions copied from the reference image.
# These are visual annotations, NOT inferred/statistically calculated clusters.
REFERENCE_REGIONS = [
    {"name": "1", "bounds": [1936, 1959.7, 0.55, 5.45], "style": ":"},
    {"name": "2", "bounds": [1960, 1988.9, 0.55, 5.45], "style": "--"},
    {"name": "3", "bounds": [1989.3, 2011.8, 0.55, 5.45], "style": "-."},
    {"name": "4", "bounds": [1951.1, 1987.2, 5.55, 9.45], "style": "-"},
]


@dataclass(frozen=True)
class ChartStyle:
    """Lengths are physical points; marker_scale scales diameter, not area."""

    marker_scale: float = 1.3
    leader_width: float = 1.5

    @property
    def point_padding(self) -> float:
        return max(0.65, self.leader_width / 2 + 0.2)

    @property
    def line_padding(self) -> float:
        return self.leader_width / 2 + 0.3
