"""Readable browser resources embedded in Python.

The generated HTML is self-contained. Edit these strings to change its markup,
styles or behavior; no separate web files or JavaScript build tools are needed.
User data is inserted only after these trusted resources are assembled.
"""

HTML_TEMPLATE = r"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Поэты: группы и источники</title>
    <style>
      __CSS__
    </style>
  </head>
  <body>
    <header>
      <strong>Поэты</strong>
      <label>
        Группа
        <select id="group" aria-label="Группа">
          <option value="">Все записи</option>
        </select>
      </label>
      <input id="search" type="search" placeholder="Найти имя…" aria-label="Поиск по имени" />
      <button id="minus" aria-label="Уменьшить">−</button>
      <button id="plus" aria-label="Увеличить">+</button>
      <button id="fit">Показать группу</button>
      <button id="reset">Сбросить</button>
      <button id="save-png">Снимок PNG</button>
      <button id="save-svg">Снимок SVG</button>
      <span id="summary" aria-live="polite">__COUNT__ записей</span>
      <span id="export-status" role="status"></span>
      <div class="size-controls">
        <label for="label-size">
          Подписи
          <input
            id="label-size"
            type="range"
            min="6"
            max="28"
            step="any"
            aria-label="Размер подписей"
          />
          <output id="label-size-value" for="label-size"></output>
        </label>
        <label for="marker-size">
          Маркеры
          <input
            id="marker-size"
            type="range"
            min="50"
            max="200"
            step="5"
            value="100"
            aria-label="Размер маркеров"
          />
          <output id="marker-size-value" for="marker-size">100%</output>
        </label>
        <label for="legend-size">
          Легенда
          <input
            id="legend-size"
            type="range"
            min="6"
            max="28"
            step="0.5"
            value="10"
            aria-label="Размер текста легенды"
          />
          <output id="legend-size-value" for="legend-size">10 pt</output>
        </label>
        <label for="axis-size">
          Оси X/Y
          <input
            id="axis-size"
            type="range"
            min="6"
            max="28"
            step="0.5"
            value="11"
            aria-label="Размер названий и делений осей X и Y"
          />
          <output id="axis-size-value" for="axis-size">11 pt</output>
        </label>
        <button id="reset-sizes">Размеры по умолчанию</button>
      </div>
    </header>
    <p class="note">
      Выбор группы выделяет её цветом и подбирает масштаб. Колесо мыши и кнопки +/− меняют масштаб;
      перетаскивание перемещает график. Снимок сохраняет текущий вид, включая выделение и масштаб.
      Наведите указатель или нажмите на точку для точных значений.
    </p>
    <div id="chart">__SVG__</div>
    <div id="tooltip" hidden></div>
    <div id="detail" aria-live="polite">Выберите маркер, чтобы закрепить сведения о записи.</div>
    <details>
      <summary>Исходные данные (__COUNT__ записей; таблица учитывает фильтр)</summary>
      <div class="table-scroll">
        <table>
          <thead><tr>__HEADER__</tr></thead>
          <tbody>__TABLE__</tbody>
        </table>
      </div>
    </details>
    <script id="chart-data" type="application/json">
      __DATA__
    </script>
    <script id="chart-metadata" type="application/json">
      __META__
    </script>
    <script>
      __JAVASCRIPT__;
    </script>
  </body>
</html>
"""


CSS = r"""* {
  box-sizing: border-box;
}
body {
  margin: 0;
  font:
    15px system-ui,
    sans-serif;
  color: #223440;
  background: #fff;
}
header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #fff;
  border-bottom: 1px solid #dce3e8;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
label {
  display: flex;
  gap: 7px;
  align-items: center;
}
input,
select,
button {
  font: inherit;
  padding: 8px 11px;
  border: 1px solid #bac8d1;
  border-radius: 6px;
  background: #fff;
}
input {
  width: 205px;
}
button {
  background: #edf3f7;
  cursor: pointer;
}
button:hover {
  background: #deebf3;
}
button:disabled {
  opacity: 0.5;
  cursor: wait;
}
.size-controls {
  display: flex;
  flex-basis: 100%;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px 24px;
  font-size: 14px;
}
.size-controls input[type="range"] {
  width: 145px;
  padding: 0;
  accent-color: #326789;
}
.size-controls output {
  min-width: 50px;
  font-variant-numeric: tabular-nums;
}
.size-controls button {
  padding: 5px 10px;
  font-size: 13px;
}
#summary,
#export-status {
  font-size: 13px;
  color: #576a78;
}
#chart {
  padding: 8px;
}
#chart > svg {
  display: block;
  width: 100%;
  height: auto;
}
#plot-viewport {
  cursor: grab;
  touch-action: none;
}
#plot-viewport.dragging {
  cursor: grabbing;
}
[id^="poet-row-"] {
  cursor: pointer;
}
[id^="poet-row-"]:focus {
  outline: none;
  filter: drop-shadow(0 0 3px #101010);
}
#tooltip {
  position: fixed;
  z-index: 20;
  background: #fff;
  border: 1px solid #8da2b1;
  border-radius: 7px;
  box-shadow: 0 3px 18px #0002;
  padding: 12px;
  max-width: 340px;
  font-size: 13px;
  pointer-events: none;
  white-space: pre-line;
}
#detail {
  margin: 0 20px 16px;
  padding: 12px 16px;
  background: #f3f7fa;
  border-radius: 6px;
  white-space: pre-line;
  min-height: 46px;
}
details {
  margin: 16px 20px 32px;
}
summary {
  cursor: pointer;
  font-weight: 600;
  padding: 8px 0;
}
.table-scroll {
  overflow: auto;
  max-height: 600px;
}
table {
  border-collapse: collapse;
  font-size: 13px;
  width: 100%;
}
th,
td {
  text-align: left;
  padding: 7px 10px;
  border-bottom: 1px solid #e1e7eb;
  white-space: nowrap;
}
th {
  position: sticky;
  top: 0;
  background: #edf3f7;
}
tr.selected {
  background: #fff1bd;
}
p.note {
  margin: 12px 20px;
  font-size: 13px;
  color: #526574;
}
"""


JAVASCRIPT = r"""/** Offline SVG viewer. All lengths use SVG points, with Y increasing downward.
 * Source data and audited geometry come from the two application/json blocks.
 * State stays private to this viewer; the exported HTML needs no external assets.
 */
(() => {
  "use strict";

  // Data, DOM references and viewer state.

  const rows = JSON.parse(document.getElementById("chart-data").textContent);
  const metadata = JSON.parse(document.getElementById("chart-metadata").textContent);
  const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
  const getElement = (id) => document.getElementById(id);
  const tooltip = getElement("tooltip");
  const detail = getElement("detail");
  const searchInput = getElement("search");
  const groupSelect = getElement("group");
  const chart = document.querySelector("#chart>svg");
  const viewport = getElement("plot-viewport");
  const plotFrame = {
    x: metadata.frame[0],
    y: metadata.frame[1],
    w: metadata.frame[2],
    h: metadata.frame[3],
  };
  let camera = {
    ...plotFrame,
  };
  let dragState = null;
  let suppressClick = false;
  let autoFitEnabled = true;
  const labelSizeInput = getElement("label-size");
  const markerSizeInput = getElement("marker-size");
  const legendSizeInput = getElement("legend-size");
  const axisSizeInput = getElement("axis-size");
  labelSizeInput.min = Math.min(6, metadata.fontSize);
  labelSizeInput.max = Math.max(28, metadata.fontSize * 2);
  labelSizeInput.value = metadata.fontSize;
  legendSizeInput.value = metadata.header.legendFontSize;
  axisSizeInput.value = metadata.header.axisFontSize;
  let sizes = {
    fontSize: metadata.fontSize,
    markerScale: 1,
    legendFontSize: metadata.header.legendFontSize,
    axisFontSize: metadata.header.axisFontSize,
  };
  const liveBounds = new Map(Object.entries(metadata.bounds));
  const groups = [...new Set(rows.map((r) => r._group).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b, "ru", {
      numeric: true,
    }),
  );
  groups.forEach((g) => {
    const option = document.createElement("option");
    option.value = g;
    option.textContent = `${g} (${rows.filter((r) => r._group === g).length})`;
    groupSelect.append(option);
  });
  groupSelect.disabled = !groups.length;
  const rowElements = new Map(
    rows.map((r) => {
      const marker = getElement("poet-row-" + r._row);
      const label = getElement("label-row-" + r._row);
      const leader = getElement("leader-row-" + r._row);
      const paint = [...marker.querySelectorAll("use,path")].filter((el) => !el.closest("defs"));
      const strokes = leader ? [...leader.querySelectorAll("path")] : [];
      const pointColor =
        paint.find((el) => el.style.fill && el.style.fill !== "none")?.style.fill || "#506473";
      return [
        r._row,
        {
          marker,
          label,
          leader,
          paint,
          strokes,
          pointColor,
          base: paint.map((el) => el.getAttribute("style")),
          lineBase: strokes.map((el) => el.getAttribute("style")),
          markerTransform: marker.getAttribute("transform"),
          labelTransform: label?.getAttribute("transform"),
          linePaths: strokes.map((el) => el.getAttribute("d")),
          table: document.querySelector(`tr[data-row="${r._row}"]`),
        },
      ];
    }),
  );
  function createSvgElement(tag, attributes = {}, parent = null) {
    const el = document.createElementNS(SVG_NAMESPACE, tag);
    for (const [k, v] of Object.entries(attributes)) {
      el.setAttribute(k, String(v));
    }
    if (parent) {
      parent.append(el);
    }
    return el;
  }
  function appendSvgText(parent, x, y, value, attributes = {}) {
    const el = createSvgElement(
      "text",
      {
        x,
        y,
        fill: "#465664",
        "font-size": 10,
        "font-family": "DejaVu Sans, Arial, sans-serif",
        ...attributes,
      },
      parent,
    );
    el.textContent = value;
    return el;
  }
  // Fresh grid lines go behind the points, after the background bands.
  const gridLayer = createSvgElement("g", {
    id: "interactive-grid",
    "pointer-events": "none",
  });
  const plotAxes = getElement("scatter-axes");
  const firstMarker = plotAxes.querySelector('[id^="poet-row-"]');
  if (firstMarker) {
    plotAxes.insertBefore(gridLayer, firstMarker);
  } else {
    plotAxes.append(gridLayer);
  }
  const axisOverlay = createSvgElement(
    "g",
    {
      id: "interactive-axes",
      "pointer-events": "none",
    },
    chart,
  );
  const stateCaption = appendSvgText(
    chart,
    metadata.header.captionX,
    metadata.header.captionY,
    "",
    {
      id: "state-caption",
      "font-size": 10.5,
    },
  );
  getElement("chart-subtitle").style.display = "none";
  const groupLegend = createSvgElement(
    "g",
    {
      id: "active-group-legend",
    },
    chart,
  );
  // Capture outlined glyph bounds once, while the general legend is visible.
  // Scale only the text; reflow the rows without resizing gradient bars/swatches.
  function captureSvgPart(el) {
    const bounds = el.getBBox();
    const transform = el.getAttribute("transform");
    const matrix = el.transform.baseVal.consolidate()?.matrix || new DOMMatrix();
    const corners = [
      [bounds.x, bounds.y],
      [bounds.x + bounds.width, bounds.y],
      [bounds.x, bounds.y + bounds.height],
      [bounds.x + bounds.width, bounds.y + bounds.height],
    ].map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
    const x = Math.min(...corners.map((p) => p.x));
    const y = Math.min(...corners.map((p) => p.y));
    return {
      el,
      box: {
        x,
        y,
        w: Math.max(...corners.map((p) => p.x)) - x,
        h: Math.max(...corners.map((p) => p.y)) - y,
      },
      transform,
    };
  }
  const legendParts = {
    heading: captureSvgPart(getElement("legend-heading")),
    rows: ["M", "F"].map((g) => ({
      label: captureSvgPart(getElement("legend-gender-" + g)),
      swatch: captureSvgPart(getElement("legend-swatch-" + g)),
    })),
    ticks: [...getElement("gender-legend").querySelectorAll('[id^="legend-tick-"]')].map(
      captureSvgPart,
    ),
  };
  let legendHeadingPosition = {
    x: legendParts.heading.box.x,
    y: legendParts.heading.box.y,
  };
  const axisParts = {
    x: captureSvgPart(getElement("birth-year-axis-label")),
    y: captureSvgPart(getElement("sources-axis-label")),
    count: captureSvgPart(getElement("record-count-heading")),
  };
  // Legend and axis text reflow; gradient swatches keep their original dimensions.
  function placeSvgPart(part, x, y, scale = 1) {
    part.el.setAttribute(
      "transform",
      `translate(${x} ${y}) scale(${scale}) translate(${-part.box.x} ${-part.box.y}) ${part.transform || ""}`,
    );
  }
  function drawGroupLegend() {
    groupLegend.replaceChildren();
    legendParts.heading.el.style.display = groupSelect.value ? "none" : "";
    if (!groupSelect.value) {
      return 0;
    }
    const title = appendSvgText(
      groupLegend,
      0,
      0,
      `Группа ${groupSelect.value} · ${metadata.header.shading ? "число текстов" : "пол"}`,
      {
        "font-size": sizes.legendFontSize,
        "font-weight": "bold",
      },
    );
    const bounds = title.getBBox();
    title.setAttribute("x", legendHeadingPosition.x - bounds.x);
    title.setAttribute("y", legendHeadingPosition.y - bounds.y);
    return bounds.height;
  }
  function applyLegendSize() {
    sizes.legendFontSize = Number(legendSizeInput.value);
    getElement("legend-size-value").textContent = `${Number(sizes.legendFontSize.toFixed(1))} pt`;
    legendSizeInput.setAttribute("aria-valuetext", getElement("legend-size-value").textContent);
    const scale = sizes.legendFontSize / metadata.header.legendFontSize;
    const groupHeadingHeight = drawGroupLegend();
    if (scale === 1 && !groupSelect.value) {
      for (const part of [
        legendParts.heading,
        ...legendParts.rows.flatMap((r) => [r.label, r.swatch]),
        ...legendParts.ticks,
      ]) {
        restoreTransform(part.el, part.transform);
      }
      legendHeadingPosition = {
        x: legendParts.heading.box.x,
        y: legendParts.heading.box.y,
      };
    } else {
      const heading = legendParts.heading;
      const rowHeights = legendParts.rows.map((r) =>
        Math.max(r.label.box.h * scale, r.swatch.box.h),
      );
      const headingHeight = Math.max(heading.box.h * scale, groupHeadingHeight);
      const tickHeight = Math.max(0, ...legendParts.ticks.map((p) => p.box.h * scale));
      const height =
        headingHeight +
        5 +
        rowHeights.reduce((a, b) => a + b, 0) +
        5 +
        (tickHeight ? 6 + tickHeight : 0);
      // Use the free space above the legend when its labels grow, keeping the
      // graph and the current camera completely unchanged.
      let y = Math.max(
        8,
        Math.min(
          metadata.header.legendTop,
          metadata.header.legendTop + metadata.header.legendHeight - height,
        ),
      );
      legendHeadingPosition = {
        x: heading.box.x,
        y,
      };
      placeSvgPart(heading, heading.box.x, y, scale);
      y += headingHeight + 5;
      legendParts.rows.forEach((r, i) => {
        const center = y + rowHeights[i] / 2;
        placeSvgPart(r.label, r.label.box.x, center - (r.label.box.h * scale) / 2, scale);
        placeSvgPart(r.swatch, r.swatch.box.x, center - r.swatch.box.h / 2);
        y += rowHeights[i] + (i === 0 ? 5 : 0);
      });
      for (const p of legendParts.ticks) {
        placeSvgPart(p, p.box.x + (p.box.w * (1 - scale)) / 2, y + 6, scale);
      }
    }
    drawGroupLegend();
  }
  function applyAxisSize() {
    sizes.axisFontSize = Number(axisSizeInput.value);
    getElement("axis-size-value").textContent = `${Number(sizes.axisFontSize.toFixed(1))} pt`;
    axisSizeInput.setAttribute("aria-valuetext", getElement("axis-size-value").textContent);
    const scale = sizes.axisFontSize / metadata.header.axisFontSize;
    if (scale === 1) {
      for (const part of Object.values(axisParts)) {
        restoreTransform(part.el, part.transform);
      }
    } else {
      const x = axisParts.x;
      const y = axisParts.y;
      const count = axisParts.count;
      placeSvgPart(
        x,
        plotFrame.x + plotFrame.w / 2 - (x.box.w * scale) / 2,
        plotFrame.y + plotFrame.h + 18 + 10 * scale,
        scale,
      );
      const digits = Math.max(...metadata.bands.map((b) => String(b.level).length));
      const tickWidth = digits * 12 * scale * 0.7;
      placeSvgPart(
        y,
        Math.max(8, plotFrame.x - 15 - tickWidth - 14 - y.box.w * scale),
        plotFrame.y + plotFrame.h / 2 - (y.box.h * scale) / 2,
        scale,
      );
      placeSvgPart(
        count,
        metadata.width * 0.947 - (count.box.w * scale) / 2,
        plotFrame.y - 8 - count.box.h * scale,
        scale,
      );
    }
    drawAxes();
  }
  // Camera transforms and regenerated ticks. Only the plot viewport moves.
  function yearAt(x) {
    return (
      metadata.xlim[0] + ((x - plotFrame.x) / plotFrame.w) * (metadata.xlim[1] - metadata.xlim[0])
    );
  }
  function xForYear(year) {
    return (
      plotFrame.x +
      ((year - metadata.xlim[0]) / (metadata.xlim[1] - metadata.xlim[0])) * plotFrame.w
    );
  }
  function screenX(x) {
    return plotFrame.x + ((x - camera.x) * plotFrame.w) / camera.w;
  }
  function screenY(y) {
    return plotFrame.y + ((y - camera.y) * plotFrame.h) / camera.h;
  }
  function drawAxes() {
    axisOverlay.replaceChildren();
    gridLayer.replaceChildren();
    const axisScale = sizes.axisFontSize / metadata.header.axisFontSize;
    const left = yearAt(camera.x);
    const right = yearAt(camera.x + camera.w);
    const target = (right - left) / 9;
    const power = 10 ** Math.floor(Math.log10(Math.max(1, target)));
    const step = [1, 2, 5, 10].map((v) => v * power).find((v) => v >= target) || 10 * power;
    for (let year = Math.ceil(left / step) * step; year <= right + 1e-7; year += step) {
      const source = xForYear(year);
      const x = screenX(source);
      createSvgElement(
        "line",
        {
          x1: source,
          x2: source,
          y1: camera.y,
          y2: camera.y + camera.h,
          stroke: "#dfe6eb",
          "stroke-width": (0.6 * camera.w) / plotFrame.w,
        },
        gridLayer,
      );
      appendSvgText(
        axisOverlay,
        x,
        plotFrame.y + plotFrame.h + 8 + 10 * axisScale,
        Math.round(year),
        {
          "text-anchor": "middle",
          "font-size": 10 * axisScale,
          "data-axis": "x",
        },
      );
    }
    for (const band of metadata.bands) {
      const y = screenY(band.center);
      if (y < plotFrame.y + 5 || y > plotFrame.y + plotFrame.h - 5) {
        continue;
      }
      appendSvgText(axisOverlay, plotFrame.x - 15, y + 4 * axisScale, band.level, {
        "text-anchor": "end",
        "font-size": 12 * axisScale,
        "data-axis": "y",
      });
      const n = rows.filter(
        (r) => r["Источники"] === band.level && r._group === groupSelect.value,
      ).length;
      appendSvgText(
        axisOverlay,
        metadata.width * 0.947,
        y + 4 * axisScale,
        groupSelect.value ? `${n} / ${band.count}` : band.count,
        {
          "text-anchor": "middle",
          "font-size": 10 * axisScale,
          "data-axis": "count",
        },
      );
    }
  }
  function setCamera(next) {
    camera = next;
    viewport.setAttribute("viewBox", `${camera.x} ${camera.y} ${camera.w} ${camera.h}`);
    drawAxes();
  }
  function selectedRows() {
    return groupSelect.value ? rows.filter((r) => r._group === groupSelect.value) : rows;
  }
  function fitSelection() {
    autoFitEnabled = true;
    if (!groupSelect.value && sizes.fontSize === metadata.fontSize && sizes.markerScale === 1) {
      setCamera({
        ...plotFrame,
      });
      return;
    }
    const boxes = selectedRows().map((r) => liveBounds.get(String(r._row)));
    if (!groupSelect.value) {
      boxes.push([plotFrame.x, plotFrame.y, plotFrame.x + plotFrame.w, plotFrame.y + plotFrame.h]);
    }
    const x0 = Math.min(...boxes.map((b) => b[0]));
    const y0 = Math.min(...boxes.map((b) => b[1]));
    const x1 = Math.max(...boxes.map((b) => b[2]));
    const y1 = Math.max(...boxes.map((b) => b[3]));
    const pad = groupSelect.value ? 40 : 0;
    const ratio = Math.max((x1 - x0 + pad) / plotFrame.w, (y1 - y0 + pad) / plotFrame.h, 0.2);
    setCamera({
      x: (x0 + x1 - plotFrame.w * ratio) / 2,
      y: (y0 + y1 - plotFrame.h * ratio) / 2,
      w: plotFrame.w * ratio,
      h: plotFrame.h * ratio,
    });
  }
  function zoomAt(factor, px = plotFrame.x + plotFrame.w / 2, py = plotFrame.y + plotFrame.h / 2) {
    autoFitEnabled = false;
    const w = Math.max(plotFrame.w * 0.08, Math.min(plotFrame.w * 3, camera.w * factor));
    const ratio = w / camera.w;
    const ax = camera.x + ((px - plotFrame.x) * camera.w) / plotFrame.w;
    const ay = camera.y + ((py - plotFrame.y) * camera.h) / plotFrame.h;
    setCamera({
      x: ax - (ax - camera.x) * ratio,
      y: ay - (ay - camera.y) * ratio,
      w,
      h: camera.h * ratio,
    });
  }
  // Marker/label resizing. All calculations start from the audited base geometry.
  function restoreStyle(el, value) {
    if (value === null) {
      el.removeAttribute("style");
    } else {
      el.setAttribute("style", value);
    }
  }
  function restoreTransform(el, value) {
    if (value === null || value === undefined) {
      el.removeAttribute("transform");
    } else {
      el.setAttribute("transform", value);
    }
  }
  function markerEdge(radius, shape, ux, uy) {
    if (shape === "o") {
      return radius;
    }
    const x = Math.max(Math.abs(ux), 1e-12);
    const y = Math.max(Math.abs(uy), 1e-12);
    return Math.max(Math.min(radius / x, radius / (3 * y)), Math.min(radius / (3 * x), radius / y));
  }

  /** Recompute a padded label box and contour-to-box leader in SVG points.
   * Labels move outward as they grow; point centers and birth years stay fixed.
   */
  function scaledLabelGeometry(visual, labelScale, markerScale) {
    const [anchorX, anchorY] = visual.anchor;
    const radius = (visual.radius + metadata.markerStroke / 2) * markerScale;
    const originalBox = visual.labelBox;
    const originalCenterX = (originalBox[0] + originalBox[2]) / 2;
    const originalCenterY = (originalBox[1] + originalBox[3]) / 2;
    const halfWidth = (originalBox[2] - originalBox[0]) / 2;
    const halfHeight = (originalBox[3] - originalBox[1]) / 2;
    const distance = Math.hypot(originalCenterX - anchorX, originalCenterY - anchorY);
    const unitX = (originalCenterX - anchorX) / distance;
    const unitY = (originalCenterY - anchorY) / distance;
    const labelEdgeDistance = Math.min(
      halfWidth / Math.max(Math.abs(unitX), 1e-12),
      halfHeight / Math.max(Math.abs(unitY), 1e-12),
    );
    const outwardShift =
      (labelScale - 1) * labelEdgeDistance +
      (markerScale - 1) *
        (markerEdge(visual.radius, visual.shape, unitX, unitY) + metadata.markerStroke / 2);
    let centerX = originalCenterX + unitX * outwardShift;
    let centerY = originalCenterY + unitY * outwardShift;
    let box = [
      centerX - halfWidth * labelScale,
      centerY - halfHeight * labelScale,
      centerX + halfWidth * labelScale,
      centerY + halfHeight * labelScale,
    ];
    const nearest = () => [
      Math.max(box[0], Math.min(anchorX, box[2])),
      Math.max(box[1], Math.min(anchorY, box[3])),
    ];
    let leaderEnd = nearest();
    let leaderDistance = Math.hypot(leaderEnd[0] - anchorX, leaderEnd[1] - anchorY);
    const gap = Math.max(0.8, metadata.leaderWidth / 2 + 0.3);
    if (leaderDistance <= radius + gap + 1) {
      const safe = Math.max(
        distance + outwardShift,
        radius + Math.hypot(halfWidth * labelScale, halfHeight * labelScale) + gap + 2,
      );
      centerX = anchorX + unitX * safe;
      centerY = anchorY + unitY * safe;
      box = [
        centerX - halfWidth * labelScale,
        centerY - halfHeight * labelScale,
        centerX + halfWidth * labelScale,
        centerY + halfHeight * labelScale,
      ];
      leaderEnd = nearest();
      leaderDistance = Math.hypot(leaderEnd[0] - anchorX, leaderEnd[1] - anchorY);
    }
    const leaderUnitX = (leaderEnd[0] - anchorX) / leaderDistance;
    const leaderUnitY = (leaderEnd[1] - anchorY) / leaderDistance;
    const markerEdgeDistance =
      markerEdge(visual.radius * markerScale, visual.shape, leaderUnitX, leaderUnitY) +
      (metadata.markerStroke * markerScale) / 2 +
      gap;
    return {
      box,
      transform: `translate(${centerX} ${centerY}) scale(${labelScale}) translate(${-originalCenterX} ${-originalCenterY})`,
      leaderPath: `M ${anchorX + leaderUnitX * markerEdgeDistance} ${anchorY + leaderUnitY * markerEdgeDistance} L ${leaderEnd[0]} ${leaderEnd[1]}`,
    };
  }
  function resizeRow(row, labelScale, markerScale) {
    const key = String(row._row);
    const elements = rowElements.get(row._row);
    const visual = metadata.visuals[key];
    const [anchorX, anchorY] = visual.anchor;
    const activeLabel = !visual.groupOnly || row._group === groupSelect.value;
    if (visual.groupOnly) {
      for (const el of [elements.label, elements.leader]) {
        if (el) {
          el.style.display = activeLabel ? "" : "none";
        }
      }
    }
    if (markerScale === 1) {
      restoreTransform(elements.marker, elements.markerTransform);
    } else {
      elements.marker.setAttribute(
        "transform",
        `translate(${anchorX} ${anchorY}) scale(${markerScale}) translate(${-anchorX} ${-anchorY}) ${elements.markerTransform || ""}`,
      );
    }
    if (labelScale === 1 && markerScale === 1) {
      if (elements.label) {
        restoreTransform(elements.label, elements.labelTransform);
      }
      elements.strokes.forEach((p, i) => p.setAttribute("d", elements.linePaths[i]));
      liveBounds.set(key, activeLabel ? metadata.bounds[key] : metadata.markerBounds[key]);
      return;
    }
    const radius = (visual.radius + metadata.markerStroke / 2) * markerScale;
    let bounds = [anchorX - radius, anchorY - radius, anchorX + radius, anchorY + radius];
    if (elements.label && visual.labelBox && activeLabel) {
      const geometry = scaledLabelGeometry(visual, labelScale, markerScale);
      const box = geometry.box;
      elements.label.setAttribute(
        "transform",
        `${geometry.transform} ${elements.labelTransform || ""}`,
      );
      elements.strokes.forEach((path) => path.setAttribute("d", geometry.leaderPath));
      bounds = [
        Math.min(bounds[0], box[0]),
        Math.min(bounds[1], box[1]),
        Math.max(bounds[2], box[2]),
        Math.max(bounds[3], box[3]),
      ];
    }
    liveBounds.set(key, bounds);
  }
  function applySizes(refit = true) {
    sizes = {
      fontSize: Number(labelSizeInput.value),
      markerScale: Number(markerSizeInput.value) / 100,
      legendFontSize: Number(legendSizeInput.value),
      axisFontSize: Number(axisSizeInput.value),
    };
    applyLegendSize();
    applyAxisSize();
    const labelScale = sizes.fontSize / metadata.fontSize;
    const markerScale = sizes.markerScale;
    getElement("label-size-value").textContent = `${Number(sizes.fontSize.toFixed(1))} pt`;
    getElement("marker-size-value").textContent = `${Math.round(markerScale * 100)}%`;
    labelSizeInput.setAttribute("aria-valuetext", getElement("label-size-value").textContent);
    markerSizeInput.setAttribute("aria-valuetext", getElement("marker-size-value").textContent);
    for (const row of rows) {
      resizeRow(row, labelScale, markerScale);
    }
    tooltip.hidden = true;
    if (refit && autoFitEnabled) {
      fitSelection();
    }
  }
  function resetSizes(refit = true) {
    labelSizeInput.value = metadata.fontSize;
    markerSizeInput.value = 100;
    legendSizeInput.value = metadata.header.legendFontSize;
    axisSizeInput.value = metadata.header.axisFontSize;
    applySizes(refit);
  }
  // Selection changes opacity and table visibility without changing point colors.
  function applyFilters() {
    const group = groupSelect.value;
    const query = searchInput.value.toLocaleLowerCase("ru").trim();
    let count = 0;
    for (const row of rows) {
      const e = rowElements.get(row._row);
      const member = !group || row._group === group;
      const match = member && String(row["Поэт"]).toLocaleLowerCase("ru").includes(query);
      count += Number(match);
      for (const el of [e.marker, e.label, e.leader]) {
        if (el) {
          el.style.opacity = match ? "1" : ".12";
        }
      }
      // A selection keeps the same gender/text-count encoding as the overview.
      // Dimming the background identifies the group without erasing its data.
      e.paint.forEach((el, i) => restoreStyle(el, e.base[i]));
      e.strokes.forEach((el, i) => {
        restoreStyle(el, e.lineBase[i]);
        if (group && member) {
          el.style.stroke = e.pointColor;
        }
      });
      e.table.hidden = !match;
    }
    const groupCount = selectedRows().length;
    getElement("summary").textContent = group
      ? `Группа ${group}: ${groupCount} из ${rows.length}${query ? `; найдено ${count}` : ""}`
      : query
        ? `Найдено ${count} из ${rows.length}`
        : `${rows.length} записей`;
    stateCaption.textContent =
      getElement("summary").textContent + (query ? ` · Поиск: ${searchInput.value.trim()}` : "");
    applyLegendSize();
    getElement("fit").textContent = group ? "Показать группу" : "Весь график";
    tooltip.hidden = true;
    drawAxes();
  }
  function describeRow(row) {
    return [
      `${row["Поэт"]}`,
      `Год рождения: ${row["Год рождения"]} · Источники: ${row["Источники"]}`,
      `Группа: ${row["Группа"] ?? "—"} · Пол: ${row["Пол"] === "M" ? "М" : row["Пол"]}`,
      `Тексты: ${row["Тексты"]} · Строки: ${row["Строки"] ?? "—"}`,
      `Топ-№: ${row["Топ-№"]} · Поэт года: ${row["Поэт года"] === "Y" ? "да" : "нет"} · Топ-10: ${row["Топ-10"] === "Y" ? "да" : "нет"}`,
      `Строка Excel: ${row._row}`,
    ].join("\n");
  }
  function moveTooltip(x, y) {
    tooltip.style.left =
      Math.max(5, Math.min(x + 14, window.innerWidth - tooltip.offsetWidth - 8)) + "px";
    tooltip.style.top =
      Math.max(5, Math.min(y + 14, window.innerHeight - tooltip.offsetHeight - 8)) + "px";
  }
  function pointerPosition(event) {
    return new DOMPoint(event.clientX, event.clientY).matrixTransform(
      chart.getScreenCTM().inverse(),
    );
  }
  function finishDrag(event) {
    if (event.type === "pointerup" && !suppressClick && dragState?.target) {
      dragState.target.dispatchEvent(new MouseEvent("click"));
    }
    dragState = null;
    viewport.classList.remove("dragging");
    setTimeout(() => {
      suppressClick = false;
    }, 0);
  }
  // Snapshot clones include the current camera, filters and all four size settings.
  function createSvgSnapshot() {
    const clone = chart.cloneNode(true);
    clone.setAttribute("xmlns", SVG_NAMESPACE);
    clone.setAttribute("width", metadata.width);
    clone.setAttribute("height", metadata.height);
    clone.removeAttribute("style");
    clone.querySelectorAll("[tabindex]").forEach((el) => {
      el.removeAttribute("tabindex");
      el.removeAttribute("role");
    });
    const state = createSvgElement("metadata");
    state.textContent = JSON.stringify({
      group: groupSelect.value || null,
      search: searchInput.value,
      camera,
      sizes,
      created: new Date().toISOString(),
    });
    clone.prepend(state);
    return new Blob([new XMLSerializer().serializeToString(clone)], {
      type: "image/svg+xml;charset=utf-8",
    });
  }
  function snapshotFilename(ext) {
    const group = groupSelect.value ? "group-" + groupSelect.value : "all";
    return `poets-${group.replace(/[^\p{L}\p{N}_-]/gu, "_")}-${new Date().toISOString().replace(/[:.]/g, "-")}.${ext}`;
  }
  function downloadBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  }
  async function saveSnapshot(format) {
    const buttons = [getElement("save-png"), getElement("save-svg")];
    buttons.forEach((b) => (b.disabled = true));
    getElement("export-status").textContent = "Создаётся снимок…";
    let imageUrl;
    try {
      const blob = createSvgSnapshot();
      if (format === "svg") {
        downloadBlob(blob, snapshotFilename("svg"));
      } else {
        imageUrl = URL.createObjectURL(blob);
        const img = new Image();
        await new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = () =>
            reject(new Error("Браузер не смог прочитать SVG. Попробуйте снимок SVG."));
          img.src = imageUrl;
        });
        const scale = Math.min(2, 8192 / Math.max(metadata.width, metadata.height));
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(metadata.width * scale);
        canvas.height = Math.round(metadata.height * scale);
        const context = canvas.getContext("2d");
        if (!context) {
          throw new Error("Не удалось создать изображение");
        }
        context.fillStyle = "white";
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, 0, 0, canvas.width, canvas.height);
        const png = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
        if (!png) {
          throw new Error("Не удалось создать PNG");
        }
        downloadBlob(png, snapshotFilename("png"));
      }
      getElement("export-status").textContent = `Снимок ${format.toUpperCase()} готов`;
    } catch (error) {
      getElement("export-status").textContent = error.message;
    } finally {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
      buttons.forEach((b) => (b.disabled = false));
    }
  }
  // Event registration is grouped here; initialize() binds each handler once.
  function bindSizeControls() {
    labelSizeInput.addEventListener("input", () => applySizes());
    markerSizeInput.addEventListener("input", () => applySizes());
    legendSizeInput.addEventListener("input", applyLegendSize);
    axisSizeInput.addEventListener("input", applyAxisSize);
    getElement("reset-sizes").onclick = () => resetSizes();
  }
  function bindMarkerEvents() {
    for (const row of rows) {
      const e = rowElements.get(row._row);
      const el = e.marker;
      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "button");
      el.setAttribute("aria-label", describeRow(row));
      const title = createSvgElement("title");
      title.textContent = describeRow(row);
      el.prepend(title);
      el.addEventListener("pointerenter", (event) => {
        if (dragState) {
          return;
        }
        tooltip.textContent = describeRow(row);
        tooltip.hidden = false;
        moveTooltip(event.clientX, event.clientY);
      });
      el.addEventListener("pointermove", (event) => {
        if (!dragState) {
          moveTooltip(event.clientX, event.clientY);
        }
      });
      el.addEventListener("pointerleave", () => (tooltip.hidden = true));
      function select() {
        detail.textContent = describeRow(row);
        document.querySelectorAll("tr.selected").forEach((t) => t.classList.remove("selected"));
        e.table.classList.add("selected");
      }
      el.addEventListener("click", () => {
        if (!suppressClick) {
          select();
        }
      });
      el.addEventListener("focus", select);
      el.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          select();
        }
      });
    }
  }
  function bindViewportEvents() {
    viewport.addEventListener(
      "wheel",
      (event) => {
        event.preventDefault();
        const p = pointerPosition(event);
        zoomAt(event.deltaY > 0 ? 1.14 : 1 / 1.14, p.x, p.y);
        tooltip.hidden = true;
      },
      {
        passive: false,
      },
    );
    viewport.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) {
        return;
      }
      const p = pointerPosition(event);
      dragState = {
        id: event.pointerId,
        x: p.x,
        y: p.y,
        camera: {
          ...camera,
        },
        target: event.target.closest('[id^="poet-row-"]'),
      };
      suppressClick = false;
      viewport.setPointerCapture(event.pointerId);
      viewport.classList.add("dragging");
      tooltip.hidden = true;
    });
    viewport.addEventListener("pointermove", (event) => {
      if (!dragState || event.pointerId !== dragState.id) {
        return;
      }
      const p = pointerPosition(event);
      const dx = p.x - dragState.x;
      const dy = p.y - dragState.y;
      if (Math.hypot(dx, dy) > 2) {
        suppressClick = true;
        autoFitEnabled = false;
      }
      setCamera({
        ...dragState.camera,
        x: dragState.camera.x - (dx * dragState.camera.w) / plotFrame.w,
        y: dragState.camera.y - (dy * dragState.camera.h) / plotFrame.h,
      });
    });
    viewport.addEventListener("pointerup", finishDrag);
    viewport.addEventListener("pointercancel", finishDrag);
  }
  function bindToolbar() {
    searchInput.addEventListener("input", applyFilters);
    groupSelect.addEventListener("change", () => {
      searchInput.value = "";
      applySizes(false);
      applyFilters();
      fitSelection();
    });
    getElement("plus").onclick = () => zoomAt(1 / 1.25);
    getElement("minus").onclick = () => zoomAt(1.25);
    getElement("fit").onclick = fitSelection;
    getElement("reset").onclick = () => {
      groupSelect.value = "";
      searchInput.value = "";
      resetSizes(false);
      applyFilters();
      fitSelection();
      detail.textContent = "Выберите маркер, чтобы закрепить сведения о записи.";
      document.querySelectorAll("tr.selected").forEach((t) => t.classList.remove("selected"));
    };
    getElement("save-png").onclick = () => saveSnapshot("png");
    getElement("save-svg").onclick = () => saveSnapshot("svg");
  }
  function initialize() {
    bindSizeControls();
    bindMarkerEvents();
    bindViewportEvents();
    bindToolbar();
    applySizes(false);
    applyFilters();
    setCamera({
      ...plotFrame,
    });
  }
  initialize();
})();
"""
