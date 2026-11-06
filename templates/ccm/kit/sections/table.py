"""A real table of values, with a sort control in each column head.

The table is a plain semantic table first. Sort, the sticky head and the
sideways scroll are added on top of it, so the table with no script is already
a working table.
"""
from .. import charts, inline
from ..text import esc, field, optional_text, text
from .figure import source_line

NAME = 'table'
TITLE_REQUIRED = True
ORDER = 34
FIELDS = ('<code>title</code>, <code>caption</code>, <code>columns</code>: each has'
          ' <code>label</code>, <code>type</code> and optional <code>unit</code>,'
          ' <code>rows</code>, <code>sort</code>, and optional <code>note</code>,'
          ' <code>source</code> and <code>rail</code>')
SPECIMEN = {
    'summary': 'A sortable table with right-aligned numerals and a sticky head.',
    'use_when': 'Use it when the reader needs every value, not the shape of them.',
    'json': {
        'type': 'table',
        'id': 'table-specimen',
        'title': 'Grants by program and year',
        'caption': 'Every value here is invented for the guide. Replace them with verified figures.',
        'columns': [
            {'label': 'Program', 'type': 'text'},
            {'label': 'Grants', 'type': 'number'},
            {'label': 'Newsrooms', 'type': 'number'},
        ],
        'rows': [
            ['Local reporting', 12, 34],
            ['Civic technology', 5, 11],
            ['Language access', 8, 19],
        ],
    },
}

TYPES = ('text', 'number')


def read_columns(section, where):
    """The head of the table. A column states what it holds, so a value can be
    checked against it and a numeral can take the column that aligns it."""
    columns = field(section, 'columns', where)
    if not isinstance(columns, list) or not columns:
        raise ValueError(f'{where}columns must be a list with at least one column')
    read = []
    for index, column in enumerate(columns, 1):
        place = f'{where[:-2]} column {index}: '
        if not isinstance(column, dict):
            raise ValueError(f'{place}a column holds a label and a type')
        kind = text(column, 'type', place)
        if kind not in TYPES:
            raise ValueError(f'{place}type must be text or number, not {kind!r}')
        read.append({
            'label': text(column, 'label', place),
            'type': kind,
            'unit': optional_text(column, 'unit', place),
        })
    return read


def read_rows(section, columns, where):
    """Every row, checked against the head. A row of the wrong length, or a
    word in a number column, stops the build and names the row."""
    rows = field(section, 'rows', where)
    if not isinstance(rows, list) or not rows:
        raise ValueError(f'{where}rows must be a list with at least one row')
    for index, row in enumerate(rows, 1):
        place = f'{where[:-2]} row {index}: '
        if not isinstance(row, list):
            raise ValueError(f'{place}a row is a list of values')
        if len(row) != len(columns):
            raise ValueError(
                f'{place}a row holds {len(columns)} values, one for each column, '
                f'and this one holds {len(row)}'
            )
        for step, (value, column) in enumerate(zip(row, columns), 1):
            at = f'{place[:-2]} value {step}: '
            if column['type'] == 'number':
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError(
                        f'{at}the column {column["label"]!r} holds numbers, and '
                        f'{value!r} is not one'
                    )
            elif not isinstance(value, str):
                raise ValueError(
                    f'{at}the column {column["label"]!r} holds text, and {value!r} '
                    f'is not text'
                )
    return rows


def head_cell(column, index, sortable):
    """One column head. The sort control is a button inside the head cell, so
    the cell keeps its scope and the reader keeps a real control to press."""
    # A space stands between the name and the unit, so the two are two words
    # wherever the head is read as one line.
    unit = (f' <span class="column-unit">{esc(column["unit"])}</span>'
            if column['unit'] else '')
    numeric = ' class="numeric"' if column['type'] == 'number' else ''
    # The name and its unit are one block, so the sort mark sits beside the
    # pair rather than in the line between them. The name has a span of its
    # own, because the sorter states the name of the column it sorted and the
    # unit is not part of that name.
    inside = (f'<span class="column-head">'
              f'<span class="column-name">{esc(column["label"])}</span>'
              f'{unit}</span>')
    if not sortable:
        # aria-sort states the order of a column a reader can order. A column
        # with no control states nothing.
        return f'<th scope="col"{numeric}>{inside}</th>'
    # The button name is the sort action plus the column label. The unit stays
    # in the header cell so table navigation still hears the measurement.
    header_unit = (f'<span class="hidden-text">{esc(column["unit"])}</span>'
                   if column['unit'] else '')
    inside = (
        f'<button type="button" class="column-sort" data-column="{index}"'
        f' data-type="{column["type"]}"'
        f' aria-label="Sort by {esc(column["label"])}">{inside}'
        f'<span class="sort-mark" aria-hidden="true"></span></button>'
        f'{header_unit}'
    )
    return f'<th scope="col"{numeric} aria-sort="none">{inside}</th>'


def sort_key(value):
    """The number the sort reads, written in full. The `g` format keeps six
    significant digits, so 1234567 and 1234568 would both read 1.23457e+06
    and the sort would call them one value."""
    if isinstance(value, int):
        return str(value)
    return repr(float(value))


def body_cell(value, column, where, markup):
    """One value. A number carries its own value in an attribute, so a sort
    reads the number and not the text that formats it."""
    if column['type'] != 'number':
        return f'<td>{markup(value, where)}</td>'
    whole = float(value).is_integer()
    shown = charts.fmt(value, 'integer' if whole else 'decimal')
    return f'<td class="numeric" data-value="{sort_key(value)}">{esc(shown)}</td>'


def rail_attr(section, where):
    """Whether the table stands in the rail. It is the same mark a figure
    reads: the wide layout renders the block at rail width beside the column,
    and every other width and paper ignore it."""
    value = section.get('rail', False)
    if not isinstance(value, bool):
        raise ValueError(f'{where}rail must be true or false, not {value!r}')
    return ' data-rail="true"' if value else ''


def render(section, heading_html, where, context):
    """The table, its caption, and the sentence a screen reader hears after a
    sort. The first column is the row head when it holds text, so every value
    in a row is announced with the name of its row."""
    markup = inline.for_section(section, where, term=context.term)
    sid = section['id']
    columns = read_columns(section, where)
    rows = read_rows(section, columns, where)
    sortable = section.get('sort', True)
    if not isinstance(sortable, bool):
        raise ValueError(f'{where}sort must be true or false, not {sortable!r}')
    head = ''.join(head_cell(column, index, sortable)
                   for index, column in enumerate(columns))
    body = []
    for index, row in enumerate(rows, 1):
        place = f'{where[:-2]} row {index}: '
        cells = []
        for step, (value, column) in enumerate(zip(row, columns)):
            if step == 0 and column['type'] == 'text':
                cells.append(f'<th scope="row">{markup(value, place)}</th>')
            else:
                cells.append(body_cell(value, column, place, markup))
        body.append(f'<tr>{"".join(cells)}</tr>')
    note = optional_text(section, 'note', where)
    status = ('<p class="table-status hidden-text" role="status"></p>\n'
              if sortable else '')
    return (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<div class="table-wrap scroll-edge" tabindex="0" role="region"'
        f' aria-labelledby="{sid}--title">\n'
        f'<table class="data-table">\n'
        f'<caption>{markup(text(section, "caption", where))}</caption>\n'
        f'<thead><tr>{head}</tr></thead>\n'
        f'<tbody>\n' + '\n'.join(body) + '\n</tbody>\n'
        f'</table>\n</div>\n'
        f'{status}{source_line(section, where, markup)}'
        + (f'<p class="figure-note">{markup(note, where)}</p>\n' if note else '')
    ), rail_attr(section, where)
