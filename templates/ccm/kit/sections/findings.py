"""A grid of statistics. One numeral, one heading and one sentence each."""
import re

from .. import charts, inline
from ..text import esc, field, optional_text, text

NAME = 'findings'
TITLE_REQUIRED = True
ORDER = 30
FIELDS = ('<code>label</code>, <code>title</code>, <code>items</code>: each has'
          ' <code>value</code>, <code>title</code>, <code>text</code>, and optional'
          ' <code>unit</code>, <code>note</code> and <code>trend</code>')
SPECIMEN = {
    'summary': 'A row of statistics, each with a numeral, a heading and a sentence.',
    'use_when': 'Use it when three or four numbers carry the result.',
    'json': {
        'type': 'findings',
        'id': 'findings-specimen',
        'label': 'Example findings',
        'title': 'Give the evidence space.',
        'items': [
            {
                'value': '12',
                'title': 'Participating newsrooms',
                'text': 'An illustrative count. Replace this with a verified result and its source.',
                'unit': 'newsrooms',
                'note': 'Illustrative count for 2024 to 2026.',
                'trend': [4, 6, 9, 11, 12],
            },
            {
                'value': '3',
                'title': 'Shared reporting groups',
                'text': 'Explain what this number measures and the period it covers.',
                'unit': 'groups',
            },
        ],
    },
}

# A value the numeral can count up to: any text before the digits, the digits
# themselves with their grouping, and any text after them. "330+" counts to
# 330 and keeps the plus; "Most" does not move.
NUMERAL = re.compile(r'^([^\d]*)(\d[\d,]*(?:\.\d+)?)(.*)$')
# A sparkline needs a shape, and two points make a straight line.
TREND_LOW, TREND_HIGH = 3, 24


def counting(value):
    """The attributes the counting numeral reads. A value with no number in it
    carries none of them, so the script leaves it alone."""
    match = NUMERAL.fullmatch(value)
    if match is None:
        return ''
    before, digits, after = match.groups()
    return (f' data-count="{esc(digits)}"'
            f' data-before="{esc(before)}" data-after="{esc(after)}"')


def read_trend(item, where):
    """The numbers behind one sparkline. Every one is a number, and there are
    enough of them to have a shape."""
    points = item.get('trend')
    if points is None:
        return []
    if not isinstance(points, list):
        raise ValueError(f'{where}trend must be a list of numbers')
    for value in points:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(
                f'{where}trend must be a list of numbers, and {value!r} is not one'
            )
    if not TREND_LOW <= len(points) <= TREND_HIGH:
        raise ValueError(
            f'{where}trend needs {TREND_LOW} to {TREND_HIGH} points, and this one '
            f'has {len(points)}'
        )
    return [float(value) for value in points]


def endpoint(value):
    """One end of the trend sentence, at the precision the value carries. A
    whole number stays whole; anything else keeps up to two decimals with no
    trailing zero, so a trend of 0.4 to 0.8 does not read from 0 to 1."""
    if float(value).is_integer():
        return f'{int(value):,}'
    return f'{round(value, 2):,.2f}'.rstrip('0').rstrip('.')


def render_trend(points):
    """One path, one dot at the end, and one sentence. No axis and no frame:
    the numeral beside it is the value, and the line is only its shape."""
    if not points:
        return ''
    low, high = min(points), max(points)
    place = charts.scale(low, high)
    steps = len(points) - 1
    plot = ' '.join(
        f'{charts.pct(index / steps * 100)},{charts.pct(100 - place(value))}'
        for index, value in enumerate(points)
    )
    end = charts.pct(100 - place(points[-1]))
    first, last = endpoint(points[0]), endpoint(points[-1])
    return (
        f'<span class="finding-trend">'
        f'<svg class="sparkline" viewBox="0 0 100 100" preserveAspectRatio="none"'
        f' aria-hidden="true" focusable="false">'
        f'<polyline points="{plot}" pathLength="1" vector-effect="non-scaling-stroke"/>'
        f'</svg>'
        f'<span class="sparkline-dot" style="--y:{end}%"></span>'
        f'<span class="hidden-text">From {esc(first)} to {esc(last)} over '
        f'{len(points)} points.</span></span>'
    )


def render_finding(item, where, markup):
    """One statistic. unit sits under the numeral and note under the text;
    both are optional and neither leaves an empty element behind."""
    unit = optional_text(item, 'unit', where)
    note = optional_text(item, 'note', where)
    shown = text(item, 'value', where)
    value = f'<span class="finding-value">{esc(shown)}</span>'
    value += render_trend(read_trend(item, where))
    if unit:
        value += f'<span class="finding-unit">{esc(unit)}</span>'
    return (
        f'<article{counting(shown)}>{value}<h3>{esc(text(item, "title", where))}</h3>\n'
        f'<p>{markup(text(item, "text", where), where)}</p>\n'
        + (f'<p class="finding-note">{markup(note, where)}</p>\n' if note else '')
        + f'</article>'
    )


def render(section, heading_html, where, context):
    """The grid takes its column count from the item count, so a row of two
    reads as a pair rather than as a three-up with a hole in it."""
    items = field(section, 'items', where)
    if not items:
        raise ValueError(f'{where}a findings section needs at least one item')
    markup = inline.for_section(section, where, term=context.term)
    findings_html = '\n'.join(
        render_finding(item, f'{where[:-2]} item {i + 1}: ', markup)
        for i, item in enumerate(items)
    )
    body = (
        f'<div class="section-heading">{heading_html}\n'
        f'</div>\n'
        f'<div class="findings" data-count="{len(items)}">\n'
        f'{findings_html}\n'
        f'</div>'
    )
    return body, ''
