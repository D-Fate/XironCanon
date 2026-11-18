#!/usr/bin/env python3
"""Построение интерактивного графика поэтов. Python 3.10+.

Установка зависимостей:
    python -m pip install numpy matplotlib openpyxl

Запуск из корня проекта:
    python sources/plot_poets.py

По умолчанию Excel читается из корня проекта, результат — poets.html рядом с ним.
Это работает и при запуске из другой рабочей директории. Готовый HTML открывается
без Python, сервера и интернета. Полная справка: python sources/plot_poets.py --help

Другой Excel, лист или имя результата:
    python sources/plot_poets.py "данные.xlsx" --sheet Data --out другой_график

Дополнительные экспорты по запросу:
    python sources/plot_poets.py --csv --audit
    python sources/plot_poets.py --formats png pdf svg
    python sources/plot_poets.py --static-only

Обычный запуск создаёт только HTML. --formats сохраняет прежний расширенный
экспорт выбранных статических форматов, HTML, CSV и отчёта проверки.
--static-only создаёт статические файлы и отчёт без HTML и CSV.
Проверки пересечений выполняются всегда, независимо от сохранения отчёта.

Структура sources:
    app.py         — параметры и последовательность построения;
    config.py      — оформление и палитры;
    models.py      — структуры данных;
    data.py        — Excel, проверка значений и CSV;
    geometry.py    — пересечения и расстояния;
    layout.py      — упаковка точек и размещение подписей;
    rendering.py   — отрисовка, легенда и подписи групп;
    validation.py  — проверки геометрии;
    exporting.py   — HTML и дополнительные форматы;
    web_assets.py  — встроенные HTML, CSS и JavaScript.
"""

from pathlib import Path
import sys

# Keep a normal launch from adding __pycache__ directories to the source tree.
sys.dont_write_bytecode = True
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sources.app import main, run_cli

if __name__ == "__main__":
    raise SystemExit(run_cli())
