"""The drawings a figure section makes: one builder for each chart kind.

Every chart is one SVG of marks and one layer of HTML labels. The SVG holds a
viewBox of 100 by 100 and takes preserveAspectRatio="none", so an x value is a
percent of the plot width and a y value is a percent of the plot height. The
labels stay in HTML, so they hold the token type size at every screen width.
A scaled SVG would shrink its own text to four pixels on a phone.

Every stroke carries vector-effect="non-scaling-stroke", so the stretch that
this scaling applies to the geometry never changes a line thickness.

figure.py validates the JSON and hands each builder a plan of numbers. A
builder returns the chart markup and the rows of the data table, so the
picture and the table can never state different values.
"""
import math

from .text import esc

# The marks the reader can tell apart without color: four series and no more.
SERIES_CAP = 4
# A label needs about this much of the plot height to clear the label above it.
LABEL_GAP = 14.0
# A value label sits outside its bar until the bar is this long, then it moves
# inside the bar end, where there is still room for it.
INSIDE_AT = 72.0
# A stacked segment holds its value at this width and its series name at this
# one. A narrower segment gives its value to the data table instead.
VALUE_AT = 14.0
NAME_AT = 22.0
# How much of its own slot one mark of a group fills. The rest is the gap that
# separates the marks of one row.
GROUP_FILL = .82
# How much of a row's height the dots of one group spread across. Two series
# that hold the same value draw two dots at one point without this step.
GROUP_SPAN = .5
# The pattern tile: one unit across and two down. The plot stretches sideways,
# so the tile is not square once it is drawn; every tile is a stripe or a grid,
# and neither shape stops a reader from telling the four apart under a stretch.
# The tile is small enough that even a thin bar carries three or four lines.
TILE_W = 1
TILE_H = 2


def pct(value):
    """One coordinate, rounded, so a snapshot of a chart is stable."""
    return f'{value:.2f}'


def fmt(value, value_format):
    """One value, as the reader reads it. Every figure states one format, so
    two marks of one chart never round to different places."""
    if value_format == 'percent':
        if float(value).is_integer():
            return f'{value:,.0f}%'
        return f'{value:,.1f}%'
    if value_format == 'decimal':
        return f'{value:,.1f}'
    return f'{round(value):,}'


def scale(low, high):
    """A value to a percent of the plot. A flat series would divide by zero,
    so it sits on the middle line instead."""
    span = high - low
    if span <= 0:
        return lambda value: 50.0
    return lambda value: (value - low) / span * 100.0


def bounds(values):
    """The scale a chart with no zero baseline takes. It opens one step below
    the smallest value and closes one step above the largest, so a mark never
    sits on the frame."""
    low, high = min(values), max(values)
    if low == high:
        return (low - 1, high + 1) if low else (0.0, 1.0)
    step = (high - low) / 8
    return low - step, high + step


def domain(kind, rows, percent=False):
    """The scale of one figure, read from every value it holds. Small
    multiples take this one scale, so a panel cannot grow a series that a
    panel beside it shrinks. Length carries the value in a bar and a stacked
    bar, so those two open at zero."""
    if kind == 'bar':
        return 0.0, max([value for row in rows for value in row['values']] + [1.0])
    if kind == 'stacked':
        if percent:
            return 0.0, 100.0
        return 0.0, max([sum(row['values']) for row in rows] + [1.0])
    if kind == 'dot':
        return bounds([value for row in rows for value in row['values']])
    if kind == 'line':
        return bounds([point[1] for row in rows for point in row['points']])
    if kind == 'slope':
        return bounds([value for row in rows for value in (row['before'], row['after'])])
    return bounds([value for row in rows for value in (row['low'], row['high'])])


def ticks(low, high, count=4):
    """At most four gridlines, on values a reader recognizes. A chart that
    labels every mark needs none of these; a line chart needs a few."""
    span = high - low
    if span <= 0:
        return []
    rough = span / count
    power = 10 ** len(str(int(abs(rough)))) if abs(rough) >= 1 else 1
    for size in (1, 2, 2.5, 5, 10):
        step = size * power / 10 if abs(rough) >= 1 else size / 10
        if step >= rough:
            break
    # floor, not int: int truncates toward zero, so a domain that opens
    # below zero would put its first gridline on the wrong side of it.
    first = (math.floor(low / step) + 1) * step
    out, value = [], first
    while value < high and len(out) < count:
        out.append(round(value, 6))
        value += step
    return out


def spread(positions, gap=LABEL_GAP):
    """Label placement down one edge. Two labels that would overlap move apart
    in the reading order of the values, so a line and its name stay together
    and no name lands on top of another."""
    order = sorted(range(len(positions)), key=lambda i: positions[i])
    out = list(positions)
    last = None
    for index in order:
        if last is not None and out[index] - last < gap:
            out[index] = last + gap
        last = out[index]
    if order and out[order[-1]] > 100:
        drop = out[order[-1]] - 100
        for index in order:
            out[index] = max(0.0, out[index] - drop)
    return out


def patterns(sid):
    """The four print fills, written into this figure's own SVG with ids that
    carry the section id. Two figures on one page never share an id, so no
    page-level block of definitions is needed.

    Each tile is a stripe or a grid at its own density, so the four hold apart
    in grayscale and for a reader who cannot separate the hues.
    """
    tiles = (
        f'<rect width="{TILE_W}" height=".5" fill="var(--ink)"/>',
        f'<rect width=".16" height="{TILE_H}" fill="var(--ink)"/>',
        f'<rect width="{TILE_W}" height=".4" fill="var(--ink)"/>'
        f'<rect width=".16" height="{TILE_H}" fill="var(--ink)"/>',
        f'<rect width=".3" height=".5" fill="var(--ink)"/>'
        f'<rect x=".5" y="1" width=".3" height=".5" fill="var(--ink)"/>',
    )
    out = []
    for index, tile in enumerate(tiles, 1):
        out.append(
            f'<pattern id="{sid}--pattern-{index}" patternUnits="userSpaceOnUse"'
            f' width="{TILE_W}" height="{TILE_H}">'
            f'<rect width="{TILE_W}" height="{TILE_H}" fill="var(--paper)"/>'
            f'{tile}</pattern>'
        )
    return f'<defs>{"".join(out)}</defs>'


def reveal(sid):
    """The window a line is drawn through. A dash offset cannot draw a line
    that also carries a non-scaling stroke, because the dash is then measured
    in screen units and the path length is not. A rectangle that grows from
    the left draws the same gesture with a transform, which is one of the four
    properties this page animates."""
    return (
        f'<defs><clipPath id="{sid}--reveal">'
        f'<rect class="chart-reveal" x="0" y="-10" width="100" height="120"/>'
        f'</clipPath></defs>'
    )


def paint(index, sid, patterned):
    """One series, painted. Screen takes the series color. Print takes the
    pattern through the same custom property, so one rule in the stylesheet
    swaps every fill on the page and no rule names a figure's own id."""
    number = index + 1
    fill = f'fill="var(--series-{number})"'
    if not patterned:
        return fill
    return f'{fill} style="--pattern:url(#{sid}--pattern-{number})"'


def svg(body):
    """The mark layer. It is hidden from assistive technology: the figure
    carries the name, the caption carries the trend, and the data table under
    the figure carries every value."""
    return (
        f'<svg class="chart-marks" viewBox="0 0 100 100" preserveAspectRatio="none"'
        f' aria-hidden="true" focusable="false">{body}</svg>'
    )


def label(classes, style, content):
    return f'<span class="{classes}" style="{style}">{content}</span>'


def categories(rows):
    """The column of category names beside a set of rows."""
    names = ''.join(f'<span class="chart-cat">{esc(row["label"])}</span>' for row in rows)
    return f'<div class="chart-cats">{names}</div>'


def frame(plan, cats, plot):
    """The shell every row chart shares: a name column, a plot, and the counts
    the stylesheet needs to give each row its height."""
    style = f'--rows:{plan["row_count"]};--per-row:{plan["per_row"]}'
    # A chart that swaps its fills for patterns on paper says so, because a
    # value printed in paper over a pattern cannot be read.
    marked = ' patterned' if plan['patterned'] else ''
    return (
        f'<div class="chart chart-{plan["kind"]}{marked}" style="{style}">'
        f'{cats}<div class="chart-plot">{plot}</div></div>'
    )


def row_band(index, count, share, part=0, parts=1):
    """Where one mark sits inside its row, as a percent of the whole plot.
    `share` is how much of the row's height the marks take. A row of two or
    more marks keeps a gap between them, so a group reads as a group."""
    height = share / count * 100.0
    top = (index + (1 - share) / 2) / count * 100.0
    slot = height / parts
    return top + part * slot, slot if parts == 1 else slot * GROUP_FILL


def group_y(index, count, part, parts):
    """Where one dot of a group sits down its own row. A row of one dot puts
    it on the row rule. A row of two or more steps them apart, so two series
    that hold the same value stay two marks the reader can count."""
    middle = (index + .5) / count * 100.0
    if parts < 2:
        return middle
    step = GROUP_SPAN / parts / count * 100.0
    return middle + (part - (parts - 1) / 2) * step


def series_names(plan):
    """The names a chart states, or one empty name when the chart has one
    unnamed series."""
    return plan['series'] or ['']


# --- bar and dot ------------------------------------------------------------

def bar(plan):
    """Length from a zero baseline carries the value, so every bar starts at
    the same edge and the value sits at the bar end."""
    names = series_names(plan)
    place = scale(plan['low'], plan['high'])
    marks, labels = [], []
    for index, row in enumerate(plan['rows']):
        parts = []
        for part, value in enumerate(row['values']):
            top, height = row_band(index, plan['row_count'], .62, part, len(names))
            width = place(value)
            parts.append(
                f'<rect class="chart-mark" x="0" y="{pct(top)}" width="{pct(width)}"'
                f' height="{pct(height)}" '
                f'{paint(part, plan["sid"], plan["patterned"])}/>'
            )
            text = fmt(value, plan['value_format'])
            if index == 0 and names[part]:
                text = f'{esc(names[part])} {text}'
            else:
                text = esc(text)
            inside = ' inside' if width >= INSIDE_AT else ''
            labels.append(label(
                f'chart-value{inside}',
                f'--x:{pct(width)}%;--y:{pct(top + height / 2)}%',
                text,
            ))
        marks.append(
            f'<g class="chart-grow" style="--row:{index}">{"".join(parts)}</g>'
        )
    body = plan['defs'] + ''.join(marks)
    return frame(plan, categories(plan['rows']), svg(body) + ''.join(labels))


def dot(plan):
    """The same scale as a bar with a lighter mark. The row rule is the only
    ink under the dot, so a long list of categories reads as a list.

    The dots of one row step down that row by series, and each label sits
    beside its own dot, so a row where two series hold the same value still
    shows two marks and two labels.
    """
    names = series_names(plan)
    place = scale(plan['low'], plan['high'])
    rules, dots, labels = [], [], []
    for index, row in enumerate(plan['rows']):
        middle, _ = row_band(index, plan['row_count'], 0)
        rules.append(
            f'<line class="chart-rule" x1="0" y1="{pct(middle)}" x2="100"'
            f' y2="{pct(middle)}" vector-effect="non-scaling-stroke"/>'
        )
        for part, value in enumerate(row['values']):
            spot = place(value)
            seat = group_y(index, plan['row_count'], part, len(names))
            style = f'--x:{pct(spot)}%;--y:{pct(seat)}%'
            dots.append(
                f'<span class="chart-point series-{part + 1}"'
                f' style="{style}"></span>'
            )
            text = fmt(value, plan['value_format'])
            if index == 0 and names[part]:
                text = f'{esc(names[part])} {text}'
            else:
                text = esc(text)
            flip = ' flip' if spot >= INSIDE_AT else ''
            labels.append(label(f'chart-value beside{flip}', style, text))
    body = plan['defs'] + ''.join(rules)
    plot = svg(body) + ''.join(dots) + ''.join(labels)
    return frame(plan, categories(plan['rows']), plot)


# --- line -------------------------------------------------------------------

def line(plan):
    """One path for each series, drawn left to right, with the name and the
    last value at the line end. A legend would send the eye back and forth."""
    low, high = plan['low'], plan['high']
    place = scale(low, high)
    steps = len(plan['rows'][0]['points'])
    across = [index / (steps - 1) * 100.0 if steps > 1 else 50.0 for index in range(steps)]
    grid, scale_labels = [], []
    for value in ticks(low, high, 4):
        spot = 100 - place(value)
        grid.append(
            f'<line class="chart-grid" x1="0" y1="{pct(spot)}" x2="100" y2="{pct(spot)}"'
            f' vector-effect="non-scaling-stroke"/>'
        )
        scale_labels.append(label(
            'chart-tick', f'--y:{pct(spot)}%', esc(fmt(value, plan['value_format']))
        ))
    scale_labels = ''.join(scale_labels)
    paths = []
    ends, dots = [], []
    raw = [100 - place(row['points'][-1][1]) for row in plan['rows']]
    for index, (row, spot) in enumerate(zip(plan['rows'], spread(raw))):
        points = ' '.join(
            f'{pct(across[step])},{pct(100 - place(value))}'
            for step, (_, value) in enumerate(row['points'])
        )
        paths.append(
            f'<polyline class="chart-path series-{index + 1}"'
            f' style="--row:{index}" points="{points}"'
            f' clip-path="url(#{plan["sid"]}--reveal)"'
            f' vector-effect="non-scaling-stroke"/>'
        )
        last = 100 - place(row['points'][-1][1])
        dots.append(
            f'<span class="chart-point series-{index + 1}"'
            f' style="--x:100%;--y:{pct(last)}%"></span>'
        )
        name = f'<span class="chart-name">{esc(row["label"])}</span>' if row['label'] else ''
        ends.append(label(
            f'chart-end series-{index + 1}',
            f'--y:{pct(spot)}%',
            f'{name}<span class="chart-figure">'
            f'{esc(fmt(row["points"][-1][1], plan["value_format"]))}</span>',
        ))
    marks = reveal(plan['sid']) + ''.join(grid) + ''.join(paths)
    steps_shown = axis_steps(steps)
    axis = '<div class="chart-axis">' + ''.join(
        label(
            'chart-x' + edge_class(step, steps),
            f'--x:{pct(across[step])}%',
            esc(plan['rows'][0]['points'][step][0]),
        )
        for step in steps_shown
    ) + '</div>'
    plot = svg(marks) + ''.join(dots)
    return (
        f'<div class="chart chart-line">'
        f'<div class="chart-scale">{scale_labels}</div>'
        f'<div class="chart-plot">{plot}</div>'
        f'<div class="chart-ends">{"".join(ends)}</div>'
        f'{axis}</div>'
    )


def axis_steps(count, most=5):
    """At most five labels under a line, the first and the last always.

    The threshold is one more than the cap, not the cap. Thinning six points to
    five picks 0, 1, 2, 4 and 5, so a January to June line loses April and shows
    five labels where six would have fitted. One more point than the cap is
    still readable, so all of them are kept and the thinning starts above that.
    """
    if count <= most + 1:
        return list(range(count))
    gap = (count - 1) / (most - 1)
    return sorted({round(index * gap) for index in range(most)})


def edge_class(step, count):
    if step == 0:
        return ' first'
    if step == count - 1:
        return ' last'
    return ''


# --- slope ------------------------------------------------------------------

def slope(plan):
    """Two moments, one line for each category. A crossing is the point of the
    form, so both ends carry the name and the value."""
    place = scale(plan['low'], plan['high'])
    lines = []
    starts = spread([100 - place(row['before']) for row in plan['rows']])
    finishes = spread([100 - place(row['after']) for row in plan['rows']])
    left, right = [], []
    for index, row in enumerate(plan['rows']):
        first, last = 100 - place(row['before']), 100 - place(row['after'])
        lines.append(
            f'<polyline class="chart-path series-{index + 1}"'
            f' style="--row:{index}" points="0,{pct(first)} 100,{pct(last)}"'
            f' clip-path="url(#{plan["sid"]}--reveal)"'
            f' vector-effect="non-scaling-stroke"/>'
        )
        for side, spot, value in (
            (left, starts[index], row['before']), (right, finishes[index], row['after'])
        ):
            side.append(label(
                f'chart-end series-{index + 1}',
                f'--y:{pct(spot)}%',
                f'<span class="chart-name">{esc(row["label"])}</span>'
                f'<span class="chart-figure">{esc(fmt(value, plan["value_format"]))}</span>',
            ))
    axis = (
        f'<div class="chart-axis">'
        f'<span class="chart-x first" style="--x:0%">{esc(plan["start_label"])}</span>'
        f'<span class="chart-x last" style="--x:100%">{esc(plan["end_label"])}</span>'
        f'</div>'
    )
    marks = reveal(plan['sid']) + ''.join(lines)
    return (
        f'<div class="chart chart-slope">'
        f'<div class="chart-ends chart-ends-start">{"".join(left)}</div>'
        f'<div class="chart-plot">{svg(marks)}</div>'
        f'<div class="chart-ends">{"".join(right)}</div>'
        f'{axis}</div>'
    )


# --- range ------------------------------------------------------------------

def range_plot(plan):
    """The gap between two values, read down a list. Both ends carry a value,
    because the reader came for the distance between them."""
    place = scale(plan['low'], plan['high'])
    bars, dots, labels = [], [], []
    for index, row in enumerate(plan['rows']):
        middle, _ = row_band(index, plan['row_count'], 0)
        top, height = row_band(index, plan['row_count'], .12)
        start, finish = place(row['low']), place(row['high'])
        bars.append(
            f'<g class="chart-grow" style="--row:{index}">'
            f'<rect class="chart-mark chart-span" x="{pct(start)}" y="{pct(top)}"'
            f' width="{pct(finish - start)}" height="{pct(height)}"/></g>'
        )
        # The low value sits left of its dot and the high value right of its
        # own, always. The plot keeps a margin on both sides for them, so a
        # row of any length places both labels the same way.
        for part, (spot, value) in enumerate(((start, row['low']), (finish, row['high']))):
            style = f'--x:{pct(spot)}%;--y:{pct(middle)}%'
            dots.append(f'<span class="chart-point series-{part + 1}" style="{style}"></span>')
            side = 'flip' if part == 0 else 'beside'
            labels.append(label(
                f'chart-value {side}', style, esc(fmt(value, plan['value_format']))
            ))
    body = plan['defs'] + ''.join(bars)
    plot = svg(body) + ''.join(dots) + ''.join(labels)
    return frame(plan, categories(plan['rows']), plot)


# --- stacked ----------------------------------------------------------------

def stacked(plan):
    """A total split into parts. With percent the row is normalized to 100, so
    every row reads on one scale and only the share is compared."""
    names = series_names(plan)
    # The row keeps the total of every segment it started with, so one panel
    # of a small multiple still states a share of the whole row.
    totals = [row['total'] for row in plan['rows']]
    high = plan['high']
    widest = widest_row(plan['rows'], totals, plan['percent'], high)
    marks, labels = [], []
    for index, row in enumerate(plan['rows']):
        total = totals[index] or 1
        top, height = row_band(index, plan['row_count'], .62)
        run, parts = 0.0, []
        for part, value in enumerate(row['values']):
            share = value / total * 100.0 if plan['percent'] else value / high * 100.0
            parts.append(
                f'<rect class="chart-mark" x="{pct(run)}" y="{pct(top)}" width="{pct(share)}"'
                f' height="{pct(height)}" '
                f'{paint(part, plan["sid"], plan["patterned"])}/>'
            )
            labels.append(segment_label(plan, names, part, index, widest, share, run, top, height, value))
            run += share
        marks.append(f'<g class="chart-grow" style="--row:{index}">{"".join(parts)}</g>')
    body = plan['defs'] + ''.join(marks)
    plot = svg(body) + ''.join(text for text in labels if text)
    return frame(plan, categories(plan['rows']), plot)


def widest_row(rows, totals, percent, high):
    """The row where each series is widest. A series is named once, there,
    because that is the one place its own segment can hold the name."""
    best = {}
    for index, row in enumerate(rows):
        total = totals[index] or 1
        for part, value in enumerate(row['values']):
            share = value / total * 100.0 if percent else value / high * 100.0
            if share > best.get(part, (-1, 0))[1]:
                best[part] = (index, share)
    return {part: spot[0] for part, spot in best.items()}


def segment_label(plan, names, part, index, widest, share, run, top, height, value):
    """A segment states its value when it can hold it, and its series name in
    the one row where it is widest. A narrower segment leaves both to the data
    table, which holds every value.

    With percent the width of the segment is the share, so the label states
    the share. A row of 30 and 10 draws two marks of 75 and 25, and printing
    30 on the first of them would name a number the picture does not draw.
    """
    if share < VALUE_AT:
        return ''
    text = esc(fmt(share if plan['percent'] else value, plan['value_format']))
    if names[part] and widest.get(part) == index and share >= NAME_AT:
        text = f'<span class="chart-name">{esc(names[part])}</span>{text}'
    # The label is capped at the width of the segment it names, so a name too
    # long for its own segment stops at the segment edge instead of running
    # over the segment beside it.
    return label(
        'chart-value inside centered',
        f'--x:{pct(run + share / 2)}%;--y:{pct(top + height / 2)}%'
        f';--w:{pct(share)}%',
        text,
    )


BUILDERS = {
    'bar': bar,
    'dot': dot,
    'line': line,
    'slope': slope,
    'range': range_plot,
    'stacked': stacked,
}
