"""One figure section with six chart kinds.

This module reads the JSON, checks it, and hands a plan of numbers to a
builder in kit/charts.py. It draws nothing itself, so a new kind is a new
builder and one name in KINDS.

Every figure states its name on the <figure> through aria-labelledby to the
visible title, states the trend in the caption, and carries a real table of
its values under the picture. The SVG is hidden from assistive technology, so
no reader hears a bare image.
"""
from urllib.parse import urlsplit

from .. import charts, inline
from ..text import esc, field, optional_text, text, url
from .accordion import CHEVRON

NAME = 'figure'
TITLE_REQUIRED = True
ORDER = 32
FIELDS = ('<code>label</code>, <code>title</code>, <code>chart</code>:'
          ' <code>kind</code>, <code>unit</code>, <code>value_format</code> and the'
          ' values the kind reads, <code>caption</code>, and optional'
          ' <code>source</code>, <code>note</code> and <code>rail</code>')
SPECIMEN = {
    'summary': 'A chart with direct labels, a one-sentence trend, and its values in a table.',
    'use_when': 'Use it when the shape of the numbers carries the point.',
    'json': {
        'type': 'figure',
        'id': 'figure-specimen',
        'label': 'Example figure',
        'title': 'Partner newsrooms grew in every year of the example set.',
        'chart': {
            'kind': 'bar',
            'unit': 'newsrooms',
            'value_format': 'integer',
            'sort': False,
            'bars': [
                {'label': '2022', 'value': 210},
                {'label': '2023', 'value': 268},
                {'label': '2024', 'value': 305},
                {'label': '2025', 'value': 330},
            ],
        },
        'caption': 'The count rose by 120 newsrooms across the four years. These numbers are invented for the guide.',
        'source': {'label': 'Invented for this specimen', 'url': 'https://centerforcooperativemedia.org/'},
    },
}

KINDS = ('bar', 'dot', 'line', 'slope', 'range', 'stacked')
FORMATS = ('integer', 'decimal', 'percent')
# Length carries the value here, so the scale opens at zero and a negative
# value stops the build.
ZERO_BASED = ('bar', 'stacked')
# These kinds order themselves by value. A line and a slope hold the order the
# author wrote, because that order is time.
SORTABLE = ('bar', 'dot', 'range', 'stacked')
# The first column of the data table.
FIRST_COLUMN = {'line': 'Point'}


def number(item, key, where):
    """One number from the JSON. True is an int in Python, so it is refused
    by name rather than drawn as a bar of length one."""
    if key not in item:
        raise ValueError(f'{where}{key} is required')
    value = item[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f'{where}{key} must be a number, not {type(value).__name__}: {value!r}'
        )
    return float(value)


def entries(chart, key, where):
    """The list of a chart, checked before anything reads it."""
    items = field(chart, key, where)
    if not isinstance(items, list) or not items:
        raise ValueError(f'{where}{key} must be a list with at least one item')
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ValueError(f'{where}{key} item {index} must be an object')
    return items


def spot(where, key, index):
    """Where an error is: the section, the list and the item in it."""
    return f'{where[:-2]} {key} {index}: '


def flag(chart, key, where, default=False):
    value = chart.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f'{where}{key} must be true or false, not {value!r}')
    return value


def rail_attr(section, where):
    """Whether the section stands in the rail. The wide layout reads the mark
    off the section and renders the block at rail width beside the column; the
    reading layout, a narrow window and paper ignore it, so a marked figure is
    never lost, only moved."""
    return ' data-rail="true"' if flag(section, 'rail', where) else ''


def read_bars(chart, where):
    """bar and dot: one value for each category, and a series name when the
    chart compares two or more sets."""
    names, rows, order = [], [], []
    for index, item in enumerate(entries(chart, 'bars', where), 1):
        place = spot(where, 'bar', index)
        name = optional_text(item, 'series', place)
        if name and name not in names:
            names.append(name)
        label = text(item, 'label', place)
        if label not in order:
            order.append(label)
            rows.append({'label': label, 'values': {}})
        rows[order.index(label)]['values'][name] = number(item, 'value', place)
    for row in rows:
        missing = [name for name in names if name not in row['values']]
        if missing:
            raise ValueError(
                f'{where}the category {row["label"]!r} has no value for '
                f'{missing[0]!r}: every category needs one value for each series'
            )
        row['values'] = [row['values'].get(name, 0.0) for name in (names or [''])]
    return names, rows


def read_series(chart, where):
    """line: one list of points for each series. Every series holds the same
    x values, so the panels of a small multiple line up."""
    names, rows, steps = [], [], None
    for index, item in enumerate(entries(chart, 'series', where), 1):
        place = spot(where, 'series', index)
        label = text(item, 'label', place)
        points = field(item, 'points', place)
        if not isinstance(points, list) or len(points) < 2:
            raise ValueError(f'{place}points must be a list of two or more points')
        read = []
        for step, point in enumerate(points, 1):
            at = f'{place[:-2]} point {step}: '
            if not isinstance(point, dict):
                raise ValueError(f'{at}a point holds an x and a y')
            read.append((text(point, 'x', at), number(point, 'y', at)))
        if steps is None:
            steps = [x for x, _ in read]
        elif [x for x, _ in read] != steps:
            raise ValueError(
                f'{place}every series needs the same x values: this one reads '
                f'{[x for x, _ in read]} and the first reads {steps}'
            )
        names.append(label)
        rows.append({'label': label, 'points': read})
    return names, rows


def read_lines(chart, where):
    """slope: one line for each category, from a before value to an after."""
    rows = []
    for index, item in enumerate(entries(chart, 'lines', where), 1):
        place = spot(where, 'line', index)
        rows.append({
            'label': text(item, 'label', place),
            'before': number(item, 'before', place),
            'after': number(item, 'after', place),
        })
    return [row['label'] for row in rows], rows


def read_rows(chart, where):
    """range: a low and a high for each category. The two ends are the two
    series, so the count is always two."""
    rows = []
    for index, item in enumerate(entries(chart, 'rows', where), 1):
        place = spot(where, 'row', index)
        low = number(item, 'low', place)
        high = number(item, 'high', place)
        if high < low:
            raise ValueError(f'{place}high is below low: {high} is under {low}')
        rows.append({'label': text(item, 'label', place), 'low': low, 'high': high})
    return [], rows


def read_stacked(chart, where):
    """stacked: one list of segments for each row. Segment order holds across
    every row, so a reader can compare one part from row to row."""
    names, rows = [], []
    for index, item in enumerate(entries(chart, 'rows', where), 1):
        place = spot(where, 'row', index)
        label = text(item, 'label', place)
        segments = field(item, 'segments', place)
        if not isinstance(segments, list) or not segments:
            raise ValueError(f'{place}segments must be a list with at least one segment')
        values = {}
        for step, segment in enumerate(segments, 1):
            at = f'{place[:-2]} segment {step}: '
            if not isinstance(segment, dict):
                raise ValueError(f'{at}a segment holds a label and a value')
            name = text(segment, 'label', at)
            # One row holds one value for each segment. A second segment of
            # the same name would replace the first, and the row would draw a
            # part the author cannot see is missing.
            if name in values:
                raise ValueError(
                    f'{at}the row {label!r} already holds a segment named '
                    f'{name!r}: give the row one segment for each name'
                )
            if name not in names:
                names.append(name)
            values[name] = number(segment, 'value', at)
        rows.append({'label': label, 'values': values})
    for row in rows:
        row['values'] = [row['values'].get(name, 0.0) for name in names]
        row['total'] = sum(row['values'])
    return names, rows


READERS = {
    'bar': read_bars, 'dot': read_bars, 'line': read_series,
    'slope': read_lines, 'range': read_rows, 'stacked': read_stacked,
}


def check_signs(kind, rows, where):
    """A bar and a stacked bar read length as value, so the scale opens at
    zero and a value under zero cannot be drawn."""
    if kind not in ZERO_BASED:
        return
    for index, row in enumerate(rows, 1):
        for value in row['values']:
            if value < 0:
                raise ValueError(
                    f'{spot(where, "row", index)}a {kind} chart opens at zero, so '
                    f'{value:g} cannot be drawn. Use a dot chart for a value under zero.'
                )


def sort_rows(kind, rows, chart, where):
    """Bars order themselves by value, largest first, unless the author states
    that the order of the categories is the point."""
    if kind not in SORTABLE or not flag(chart, 'sort', where, True):
        return rows
    if kind == 'range':
        return sorted(rows, key=lambda row: row['high'], reverse=True)
    if kind == 'stacked':
        return sorted(rows, key=lambda row: sum(row['values']), reverse=True)
    return sorted(rows, key=lambda row: max(row['values']), reverse=True)


def plan_of(kind, chart, sid, where, names, rows, percent):
    """One chart, ready to draw."""
    low, high = charts.domain(kind, rows, percent)
    return {
        'kind': kind,
        'sid': sid,
        'value_format': chart.get('value_format', 'integer'),
        'series': names,
        'rows': rows,
        'row_count': len(rows),
        # A stacked row holds a name over a value inside its own segment, so
        # its rows are one step taller than a row with a label beside it.
        'per_row': max(2, len(names)) if kind == 'bar' else (3 if kind == 'stacked' else 2),
        'percent': percent,
        'patterned': len(names) > 1 and kind in ZERO_BASED,
        'defs': charts.patterns(sid) if len(names) > 1 and kind in ZERO_BASED else '',
        'low': low,
        'high': high,
        'start_label': optional_text(chart, 'start_label', where) or 'Before',
        'end_label': optional_text(chart, 'end_label', where) or 'After',
    }


def one_series(kind, plan, index):
    """One panel of a small multiple. It keeps the scale of the whole figure,
    so a panel cannot grow a series that the panel beside it shrinks.

    Every panel draws in the first series color. A panel holds one series and
    its own heading names that series, so a color has nothing left to tell the
    reader apart; the four-color set is for series that share one chart.
    """
    panel = dict(plan)
    # The panel heading names the series, so the marks inside it do not.
    panel['series'] = ['']
    panel['per_row'] = 2
    # Each panel writes its own definitions, so two panels of one figure never
    # share the id of a pattern or of a drawing window.
    panel['sid'] = f'{plan["sid"]}-{index + 1}'
    panel['defs'] = charts.patterns(panel['sid']) if plan['patterned'] else ''
    if kind in ('bar', 'dot', 'stacked'):
        panel['rows'] = [
            {**row, 'values': [row['values'][index]]} for row in plan['rows']
        ]
        panel['row_count'] = len(panel['rows'])
    else:
        panel['rows'] = [{**plan['rows'][index], 'label': ''}]
        panel['row_count'] = 1
    return panel


def draw(kind, plan, multiples):
    """The picture: one chart, or one small chart for each series on the one
    scale the whole figure shares."""
    if not multiples:
        return charts.BUILDERS[kind](plan)
    panels = []
    for index, name in enumerate(plan['series']):
        panel = charts.BUILDERS[kind](one_series(kind, plan, index))
        panels.append(
            f'<div class="chart-panel"><h3 class="chart-panel-name">{esc(name)}</h3>'
            f'{panel}</div>'
        )
    return f'<div class="chart-multiples">{"".join(panels)}</div>'


def table_head(kind, names, plan):
    """The column names of the data table. A percent stack draws the share, so
    it states both: the value the author gave and the share the mark holds."""
    if kind == 'slope':
        return [plan['start_label'], plan['end_label']]
    if kind == 'range':
        return ['Low', 'High']
    if kind == 'stacked':
        if plan['percent']:
            return [part for name in names
                    for part in (name, f'{name} share')] + ['Total']
        return list(names) + ['Total']
    return [name or 'Value' for name in (names or [''])]


def table_body(kind, plan):
    """Every value the picture draws, in reading order."""
    value_format = plan['value_format']

    def cell(value):
        return charts.fmt(value, value_format)

    if kind == 'line':
        steps = plan['rows'][0]['points']
        return [
            (x, [cell(row['points'][index][1]) for row in plan['rows']])
            for index, (x, _) in enumerate(steps)
        ]
    if kind == 'slope':
        return [(row['label'], [cell(row['before']), cell(row['after'])])
                for row in plan['rows']]
    if kind == 'range':
        return [(row['label'], [cell(row['low']), cell(row['high'])])
                for row in plan['rows']]
    if kind == 'stacked':
        out = []
        for row in plan['rows']:
            total = row['total'] or 1
            values = []
            for value in row['values']:
                values.append(cell(value))
                if plan['percent']:
                    values.append(cell(value / total * 100.0))
            out.append((row['label'], values + [cell(row['total'])]))
        return out
    return [(row['label'], [cell(value) for value in row['values']])
            for row in plan['rows']]


def data_table(kind, names, plan, sid):
    """The figure's values, as a real table behind a disclosure. It is the
    reader's path to every number, and the keyboard path as well, because a
    focus stop inside a hidden SVG would have no name to announce."""
    head = ''.join(f'<th scope="col" class="numeric">{esc(name)}</th>'
                   for name in table_head(kind, names, plan))
    first = FIRST_COLUMN.get(kind, 'Category')
    body = ''.join(
        f'<tr><th scope="row">{esc(label)}</th>'
        + ''.join(f'<td class="numeric">{esc(value)}</td>' for value in values)
        + '</tr>'
        for label, values in table_body(kind, plan)
    )
    # The wrapper scrolls sideways on a narrow screen, so it is a focus stop
    # with a name: a reader with a keyboard alone has to reach the scroll.
    return (
        f'<details class="figure-data">\n'
        f'<summary>Show the data{CHEVRON}</summary>\n'
        f'<div class="table-wrap scroll-edge" tabindex="0" role="region"'
        f' aria-labelledby="{sid}--title"><table class="data-table">'
        f'<thead><tr><th scope="col">{first}</th>{head}</tr></thead>'
        f'<tbody>{body}</tbody></table></div>\n'
        f'</details>'
    )


def source_line(section, where, markup):
    """Where the numbers came from, with the host under the label, so a reader
    sees where a citation points before they follow it."""
    source = section.get('source')
    if source is None:
        return ''
    if not isinstance(source, dict):
        raise ValueError(f'{where}source holds a label and a url')
    href = url(field(source, 'url', where), 'url', where)
    host = esc(urlsplit(source['url']).netloc)
    return (
        f'<p class="figure-source"><a href="{href}">'
        f'{esc(text(source, "label", where))}</a>'
        f'<span class="source-host">{host}</span></p>\n'
    )


def render(section, heading_html, where, context):
    """Read the chart, check it, draw it, and state its values twice: once as
    marks and once as a table."""
    markup = inline.for_section(section, where, term=context.term)
    sid = section['id']
    chart = field(section, 'chart', where)
    if not isinstance(chart, dict):
        raise ValueError(f'{where}chart must be an object with a kind')
    kind = text(chart, 'kind', where)
    if kind not in KINDS:
        raise ValueError(
            f'{where}kind must be one of {", ".join(KINDS)}, not {kind!r}'
        )
    value_format = chart.get('value_format', 'integer')
    if value_format not in FORMATS:
        raise ValueError(
            f'{where}value_format must be one of {", ".join(FORMATS)}, not '
            f'{value_format!r}'
        )
    names, rows = READERS[kind](chart, where)
    multiples = flag(chart, 'multiples', where)
    # The cap is on the marks that share one chart, where the reader tells
    # four apart and no more. Small multiples give each series a chart and a
    # heading of its own, so the cap does not reach them: the error names the
    # fix, and the fix has to build.
    if len(names) > charts.SERIES_CAP and not multiples:
        raise ValueError(
            f'{where}a figure carries at most {charts.SERIES_CAP} series and this '
            f'one carries {len(names)}. Set "multiples": true to draw one small '
            f'chart for each series on one scale.'
        )
    percent = flag(chart, 'percent', where) and kind == 'stacked'
    check_signs(kind, rows, where)
    rows = sort_rows(kind, rows, chart, where)
    if multiples and not names:
        raise ValueError(
            f'{where}multiples draws one chart for each series, and this figure '
            f'names no series'
        )
    plan = plan_of(kind, chart, sid, where, names, rows, percent)
    unit = optional_text(chart, 'unit', where)
    unit_html = f'<p class="figure-unit">Measured in {esc(unit)}.</p>\n' if unit else ''
    note = optional_text(section, 'note', where)
    # The marks and the labels around them are one picture. Hiding the SVG
    # alone left the labels in the accessibility tree as a stream of words
    # with no shape, so the whole picture is hidden and the caption and the
    # data table are what a screen reader reads.
    body = (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<figure class="figure" aria-labelledby="{sid}--title">\n'
        f'{unit_html}<div class="chart-view" aria-hidden="true">'
        f'{draw(kind, plan, multiples)}</div>\n'
        f'<figcaption>\n'
        f'<p class="figure-caption">{markup(text(section, "caption", where))}</p>\n'
        f'{source_line(section, where, markup)}'
        + (f'<p class="figure-note">{markup(note, where)}</p>\n' if note else '')
        + f'</figcaption>\n</figure>\n'
        f'{data_table(kind, names, plan, sid)}'
    )
    return body, rail_attr(section, where)
