# Канон Моте / The Xiron Canon

[Русский](#ru) · [English](#en)

<a id="ru"></a>

## Русский

**Рекомендуем смотреть [интерактивный график онлайн](https://d-fate.github.io/XironCanon/poets.html).** Все данные и управление доступны прямо в браузере; устанавливать Python или другие программы не нужно.

### График и возможности

Диаграмма показывает **315 поэтов** из ежегодных отборов Поэтического общества Моте — **Xiron Poetry Club (磨铁读诗会)** за **2016–2024 годы**.

| Элемент | Значение |
| --- | --- |
| Ось X | Год рождения из Excel; некоторые даты известны лишь с точностью до десятилетия. |
| Ось Y | Число годовых отборов / антологий с участием автора (`Источники`, от 1 до 9). |
| Площадь | Пропорциональна весу `Топ-№`; круг и крест используют общую шкалу площадей. |
| Форма | Крест — обладатель звания «Поэт года»; круг — остальные авторы. |
| Цвет | Охристая шкала — мужчины, бирюзовая — женщины; больше стихотворений (`Тексты`) — темнее оттенок. |
| Подписи | В общем виде — записи с `Топ-10 = Y`; в выбранной группе — все её участники. |

Полосы Y имеют разную высоту: положение внутри полосы разводит точки и не задаёт дополнительного показателя.

- **Группы:** выбор одной из пяти групп выделяет её участников, делает остальные точки бледными и подбирает масштаб. Разметка хранится в Excel; `0` и пустые значения не образуют выбираемую группу.
- **Навигация:** поиск по имени, сведения при наведении и нажатии, приближение колесом мыши и перемещение перетаскиванием.
- **Оформление:** отдельные регуляторы размера подписей, маркеров, легенды и текста обеих осей; возврат к исходным настройкам.
- **Снимки:** кнопки PNG и SVG сохраняют текущий вид графика с выбранной группой, масштабом и оформлением.

### Стек и структура

**Python 3.10+**: openpyxl читает Excel, NumPy используется в расчётах, Matplotlib строит график. **HTML, CSS и JavaScript** обеспечивают интерактивность в браузере. Все ресурсы встроены в HTML.

| Путь | Назначение |
| --- | --- |
| `1. xiron. v2.0.xlsx` | Данные, лист `Data`. |
| `poets.html` | Готовый интерактивный график. |
| `sources/plot_poets.py`, `sources/app.py` | Запуск, параметры командной строки и сборка. |
| `sources/data.py` | Чтение и проверка данных. |
| `sources/geometry.py`, `sources/layout.py` | Геометрия и размещение точек и подписей. |
| `sources/rendering.py`, `sources/validation.py` | Отрисовка и проверка размещения. |
| `sources/exporting.py`, `sources/web_assets.py` | Экспорт и встроенный интерфейс HTML/CSS/JS. |
| `sources/config.py`, `sources/models.py` | Настройки и структуры данных. |
| `README.md` | Инструкция на русском и английском. |

### Работа с проектом

Для пересборки скачайте репозиторий и выполните из его корня:

```bash
python -m pip install numpy matplotlib openpyxl
python sources/plot_poets.py
```

Скрипт прочитает лист `Data` включённого Excel и перезапишет `poets.html`. Исходная таблица не изменяется. Чтобы использовать другой файл или посмотреть параметры:

```bash
python sources/plot_poets.py "data.xlsx" --sheet Data --out results/poets
python sources/plot_poets.py --help
```

Обязательные заголовки: `Поэт`, `Пол`, `Тексты`, `Год рождения`, `Источники`, `Поэт года`, `Топ-№`, `Топ-10`. Дополнительные: `Группа`, `Строки`. Числовые показатели записываются числами; флаги — `Y/N`, пол — `M` / `М` или `Ж`.

По умолчанию создаётся только HTML. `--csv` добавляет таблицу CSV, `--audit` — отчёт о размещении. `--formats png pdf svg` сохраняет статические изображения, HTML, CSV и отчёт; `--static-only --formats pdf` — PDF и отчёт. Статические изображения показывают общий вид; настроенный в браузере вид сохраняется кнопками снимка.

### Связанное исследование

Материалы к статье **Ивана Алексеева (Ivan Alekseev) «Авангардный канон и практики легитимации современной китайской поэзии: случай Поэтического общества Моте»**, подготовленной для **«Нового литературного обозрения»**. График соответствует рис. 3 рукописи. При использовании материалов указывайте статью и версию репозитория.

---

<a id="en"></a>

## English

**We recommend exploring the [interactive chart online](https://d-fate.github.io/XironCanon/poets.html).** All data and controls are available directly in your browser; no Python installation or additional software is required.

### Chart and features

The chart presents **315 poets** featured in the annual selections of **Xiron Poetry Club (磨铁读诗会; Поэтическое общество Моте)** during **2016–2024**.

| Element | Meaning |
| --- | --- |
| X axis | Birth year recorded in Excel; some dates are known only by decade. |
| Y axis | Number of annual selections / anthologies featuring the author (`Источники`, from 1 to 9). |
| Area | Proportional to the `Топ-№` weight; circles and crosses share the same area scale. |
| Shape | Cross for a “Poet of the Year” recipient; circle for other authors. |
| Color | Ochre for men, teal for women; more poems (`Тексты`) produce a darker shade. |
| Labels | Records with `Топ-10 = Y` in the overview; all members of a selected group. |

Y bands have different heights: positions within a band separate points without encoding an additional variable.

- **Groups:** selecting one of five groups highlights its members, fades other points, and fits the view. Membership is supplied in Excel; `0` and empty values do not form a selectable group.
- **Navigation:** name search, details on hover and click, mouse-wheel zoom, and drag-to-pan.
- **Appearance:** separate size controls for labels, markers, legend text, and both axes; default settings can be restored.
- **Snapshots:** PNG and SVG buttons save the current chart, including the selected group, zoom, and appearance.

### Stack and structure

**Python 3.10+**: openpyxl reads Excel, NumPy supports calculations, and Matplotlib renders the chart. **HTML, CSS, and JavaScript** provide browser interaction. All resources are embedded in the HTML.

| Path | Purpose |
| --- | --- |
| `1. xiron. v2.0.xlsx` | Dataset, `Data` worksheet. |
| `poets.html` | Ready-to-use interactive chart. |
| `sources/plot_poets.py`, `sources/app.py` | Entry point, command-line options, and build workflow. |
| `sources/data.py` | Data loading and validation. |
| `sources/geometry.py`, `sources/layout.py` | Geometry and placement of points and labels. |
| `sources/rendering.py`, `sources/validation.py` | Rendering and layout checks. |
| `sources/exporting.py`, `sources/web_assets.py` | Export and embedded HTML/CSS/JS interface. |
| `sources/config.py`, `sources/models.py` | Settings and data structures. |
| `README.md` | Instructions in Russian and English. |

### Working with the project

To rebuild the chart, download the repository and run from its root:

```bash
python -m pip install numpy matplotlib openpyxl
python sources/plot_poets.py
```

The script reads the included workbook's `Data` sheet and overwrites `poets.html`, leaving the workbook unchanged. To use another file or view available options:

```bash
python sources/plot_poets.py "data.xlsx" --sheet Data --out results/poets
python sources/plot_poets.py --help
```

Required headers: `Поэт`, `Пол`, `Тексты`, `Год рождения`, `Источники`, `Поэт года`, `Топ-№`, `Топ-10`. Optional: `Группа`, `Строки`. Store numeric indicators as numbers; use `Y/N` for flags, `M` / `М` for male and `Ж` for female.

Only HTML is generated by default. `--csv` adds a CSV table, and `--audit` adds a layout report. `--formats png pdf svg` exports static images, HTML, CSV, and a report; `--static-only --formats pdf` exports PDF and a report. Static images show the overview; use the browser's snapshot buttons to save an adjusted view.

### Related research

Companion materials for **Ivan Alekseev's (Иван Алексеев) “Avant-garde Canon and Legitimation Practices in Contemporary Chinese Poetry: A Case of Xiron Poetry Club,”** prepared for **Novoe literaturnoe obozrenie («Новое литературное обозрение»)**. The chart corresponds to Figure 3 in the manuscript. When using these materials, cite the article and the repository version.
