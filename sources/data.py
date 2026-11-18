"""Read and validate the source workbook without modifying it."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path
import openpyxl
from .config import COLUMNS


def group_key(value) -> str:
    """Canonical selector value. Zero/blank means no selectable group."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    try:
        number = float(text.replace(",", "."))
    except ValueError:
        return text
    if not math.isfinite(number):
        raise ValueError(f"Некорректная группа: {value!r}")
    if number == 0:
        return ""
    return str(int(number)) if number.is_integer() else text


def validate_row(row: dict, row_number: int) -> None:
    """Normalize supported categories and fail with the original Excel row number."""
    if row["Поэт"] is None or not str(row["Поэт"]).strip():
        raise ValueError(f"Строка {row_number}: отсутствует имя")
    # The supplied file contains a numeric cell with value 43 here.
    # Preserve it literally without guessing a name or its meaning.
    row["Поэт"] = str(row["Поэт"]).strip()
    for key in ("Тексты", "Год рождения", "Источники", "Топ-№"):
        value = row[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Строка {row_number}, {key}: не число {value!r}")
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Строка {row_number}, {key}: нужно положительное число")
        if key != "Топ-№" and int(value) != value:
            raise ValueError(f"Строка {row_number}, {key}: нужно целое число")
    for key in ("Поэт года", "Топ-10"):
        row[key] = str(row[key]).strip().upper()
        if row[key] not in {"Y", "N"}:
            raise ValueError(f"Строка {row_number}, {key}: допустимы только Y/N")
    row["Пол"] = str(row["Пол"]).strip().upper().replace("М", "M")
    if row["Пол"] not in {"M", "Ж"}:
        raise ValueError(f"Строка {row_number}: неизвестное значение Пол")


def read_data(filename: Path, sheet: str) -> tuple[list[dict], list[str]]:
    """Read only; never modify the supplied workbook or silently drop rows."""
    wb = openpyxl.load_workbook(filename, read_only=True, data_only=True)
    try:
        if sheet not in wb.sheetnames:
            raise ValueError(f"Нет листа {sheet!r}. Листы: {wb.sheetnames}")
        iterator = wb[sheet].iter_rows(values_only=True)
        header = [str(v).strip() if v is not None else "" for v in next(iterator)]
        missing = set(COLUMNS) - set(header)
        if missing:
            raise ValueError(f"Отсутствуют столбцы: {sorted(missing)}")
        if any(header.count(c) != 1 for c in COLUMNS) or header.count("Группа") > 1:
            raise ValueError("Имена обязательных столбцов должны быть уникальны")
        rows = []
        for row_number, values in enumerate(iterator, 2):
            if all(v is None for v in values):
                continue
            r = dict(zip(header, values))
            r["_row"] = row_number
            r.setdefault("Группа", 0)
            r["_group"] = group_key(r["Группа"])
            validate_row(r, row_number)
            rows.append(r)
    finally:
        wb.close()
    if not rows:
        raise ValueError("Нет строк данных")
    exact = Counter(tuple(r[k] for k in header if k) for r in rows)
    duplicates = sum(count - 1 for count in exact.values())
    warnings = []
    if "Группа" not in header:
        warnings.append("Нет столбца «Группа»: выделение групп недоступно.")
    if duplicates:
        warnings.append(f"Полных повторных строк: {duplicates}. Все строки сохранены.")
    return rows, warnings


def write_csv(rows: list[dict], destination: Path) -> None:
    """Export original fields and the Excel row number, with a BOM for Excel."""
    keys = [key for key in rows[0] if key and not key.startswith("_")]
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["Строка Excel", *keys])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {"Строка Excel": row["_row"], **{key: row[key] for key in keys}}
            )
