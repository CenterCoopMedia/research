"""A drawing of how a few parts connect, and the same thing said in words.

The marks and the bowed lines come from the cover's own drawing, so a diagram
reads in the hand the rest of the report is drawn in. Nothing here animates
and nothing here is interactive: it is one picture, and an ordered list under
it names every connection for a reader who cannot see it.
"""
import math
import re

from .. import inline
from ..art import mark_shape
from ..text import esc, field, optional_text, text
from .image import caption_html, choice

NAME = 'diagram'
TITLE_REQUIRED = True
ORDER = 64
FIELDS = ('<code>label</code>, <code>title</code>, <code>nodes</code>:'
          ' <code>id</code>, <code>label</code>; <code>edges</code>:'
          ' <code>from</code>, <code>to</code>, optional <code>label</code>;'
          ' <code>layout</code> of <code>row</code>, <code>column</code> or'
          ' <code>ring</code>; optional <code>caption</code>')
LAYOUTS = ('row', 'column', 'ring')
# The frame is the figure column, 1092 units for 1092 pixels, so a label set
# at 16 units is a label set at 16 pixels. The drawing holds that size at
# every width and its own frame scrolls when the column is narrower, because
# a label that scales with the page stops being readable on a phone.
FRAME_W = 1092
# The cover draws a mark 30 to 50 units across in a 720 unit frame. This
# frame is half as big again, so the mark grows with it.
MARK_SCALE = 1.35
# A mark is up to 50 units across and 60 tall, and it is rotated, so the box
# it can turn inside is its own diagonal, scaled. Every layout keeps this
# much room around a node, which is what stops two nodes from touching.
MARK_BOX = 80 * MARK_SCALE
LABEL_SIZE = 16
LABEL_LEADING = 20
# How wide one character of the sans stack is taken to be. An average glyph
# is nearer .55em, but a label of wide glyphs then runs into its neighbour, so
# the bound is the wide end of the stack and a label of narrow glyphs simply
# wraps sooner than it has to.
CHAR_WIDTH = LABEL_SIZE * .72
LABEL_LINES = 2
# How far the first label line sits under the mark it names: half the mark
# box, the label's own ascender, and a gap.
LABEL_DROP = MARK_BOX / 2 + LABEL_SIZE + 8
# A line stops this far short of a node, so it points at the mark instead of
# running under it.
EDGE_GAP = MARK_BOX / 2 + 16
# How much line stays between two nodes that sit as close as a layout puts
# them. The gap comes off both ends, so a layout that puts two nodes closer
# than twice the gap and this span has no line left to draw.
EDGE_SPAN = 40
# The cover bows every line the same way: the control point steps off the
# segment's own perpendicular by 12 percent of its length.
EDGE_BOW = .12
# The ring is an ellipse, not a circle: the frame is wide and a circle in it
# would leave a third of the drawing empty on each side.
RING_RX = 400
RING_RY = 190
RING_CENTER_Y = 274
RING_LABEL_MAX = 240
# How far a node reaches above and below its own centre.
NODE_ABOVE = MARK_BOX / 2
NODE_BELOW = LABEL_DROP + LABEL_LEADING + LABEL_SIZE * .3
MIN_NODES = 2
MAX_NODES = 8
# --j and pathLength carry the cover's draw-in animation. A diagram never
# animates, so the two attributes come off and the drawing stays small.
STROKE_ATTRS = re.compile(r' (?:style|pathLength)="[^"]*"')
SPECIMEN = {
    'summary': 'A few labeled parts, the lines between them, and the same thing in sentences.',
    'use_when': 'Use it when one drawing explains a flow that a sequence of steps would not.',
    'json': {
        'type': 'diagram',
        'id': 'diagram-specimen',
        'label': 'Example diagram',
        'title': 'How one story reaches three newsrooms.',
        'layout': 'ring',
        'nodes': [
            {'id': 'desk', 'label': 'Shared desk'},
            {'id': 'county', 'label': 'County partner'},
            {'id': 'readers', 'label': 'Readers'},
            {'id': 'city', 'label': 'City partner'},
        ],
        'edges': [
            {'from': 'desk', 'to': 'county', 'label': 'sends the draft to'},
            {'from': 'desk', 'to': 'city', 'label': 'sends the draft to'},
            {'from': 'county', 'to': 'readers', 'label': 'publishes for'},
            {'from': 'city', 'to': 'readers', 'label': 'publishes for'},
        ],
        'caption': 'An invented flow. Replace the nodes and the edges with your own.',
    },
}


def places(layout, count):
    """Where each node sits, and how tall the frame has to be. A place holds
    the mark centre, the first label baseline, how the label is anchored, and
    how wide the label may be before it runs into its neighbour."""
    spots = []
    if layout == 'row':
        cell = FRAME_W / count
        top = MARK_BOX / 2 + 12
        for index in range(count):
            x = cell * (index + .5)
            spots.append({'x': x, 'y': top, 'lx': x, 'ly': top + LABEL_DROP,
                          'anchor': 'middle', 'width': cell - 16, 'center': False})
        return top + NODE_BELOW + 8, spots
    if layout == 'column':
        # The mark box alone holds two marks apart, but an edge between two
        # neighbours gives up EDGE_GAP at each end, so the pitch holds both
        # gaps and a span of line as well.
        pitch = max(MARK_BOX + 20, EDGE_GAP * 2 + EDGE_SPAN)
        mark_x = MARK_BOX / 2 + 16
        label_x = MARK_BOX + 48
        for index in range(count):
            y = pitch / 2 + 8 + index * pitch
            spots.append({'x': mark_x, 'y': y, 'lx': label_x, 'ly': y + 6,
                          'anchor': 'start', 'width': FRAME_W - label_x - 24,
                          'center': True})
        return count * pitch + 16, spots
    points = ring_points(count)
    room = ring_room(points)
    for x, y in points:
        spots.append({'x': x, 'y': y, 'lx': x, 'ly': y + LABEL_DROP,
                      'anchor': 'middle', 'width': room, 'center': False})
    return RING_CENTER_Y + RING_RY + NODE_BELOW + 8, spots


def ring_points(count):
    """The node centres of a ring, starting at the top and going clockwise."""
    points = []
    for index in range(count):
        angle = math.radians(index / count * 360 - 90)
        points.append((
            FRAME_W / 2 + math.cos(angle) * RING_RX,
            RING_CENTER_Y + math.sin(angle) * RING_RY,
        ))
    return points


def ring_room(points):
    """How wide a ring label may be. Two nodes on a ring are near each other
    in one direction and far in the other, so the width is set by the closest
    pair that still shares a band of the drawing, not by the arc between
    neighbours."""
    room = RING_LABEL_MAX
    for first in range(len(points)):
        for second in range(first + 1, len(points)):
            if abs(points[first][1] - points[second][1]) >= NODE_ABOVE + NODE_BELOW:
                continue
            room = min(room, abs(points[first][0] - points[second][0]) - 8)
    return room


def boxes(layout, count, lines=LABEL_LINES):
    """The room one node takes: its mark and its label together. The test
    holds every pair of these apart, so no layout can put two nodes on top of
    each other."""
    spots = places(layout, count)[1]
    out = []
    for spot in spots:
        if spot['anchor'] == 'middle':
            left, right = spot['lx'] - spot['width'] / 2, spot['lx'] + spot['width'] / 2
        else:
            left, right = spot['lx'], spot['lx'] + spot['width']
        first = spot['ly'] - (lines - 1) * LABEL_LEADING / 2 if spot['center'] else spot['ly']
        top = first - LABEL_SIZE
        bottom = first + (lines - 1) * LABEL_LEADING + LABEL_SIZE * .3
        out.append((
            min(spot['x'] - MARK_BOX / 2, left),
            min(spot['y'] - MARK_BOX / 2, top),
            max(spot['x'] + MARK_BOX / 2, right),
            max(spot['y'] + MARK_BOX / 2, bottom),
        ))
    return out


def wrap(label, width, where):
    """A node label, in at most two lines. SVG text does not wrap itself, so
    a label that cannot fit the room its layout leaves stops the build and
    names the room it has. One word longer than the room is the case no wrap
    can answer, so it is reported on its own."""
    limit = max(1, int(width / CHAR_WIDTH))
    lines, current = [], ''
    for word in label.split():
        if len(word) > limit:
            raise ValueError(
                f'{where}the word {word!r} is {len(word)} characters and this '
                f'node holds {limit} in {width:.0f} units: shorten the word, '
                f'use the column layout, or draw fewer nodes'
            )
        nxt = f'{current} {word}'.strip()
        if len(nxt) <= limit:
            current = nxt
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if len(lines) > LABEL_LINES:
        raise ValueError(
            f'{where}label is {len(label)} characters and this layout holds '
            f'{limit} on each of {LABEL_LINES} lines: shorten the label, use '
            f'the column layout, or draw fewer nodes'
        )
    return lines


def read_nodes(section, where):
    """Every node, in input order, with its label already split into lines."""
    items = field(section, 'nodes', where)
    if not isinstance(items, list) or not MIN_NODES <= len(items) <= MAX_NODES:
        raise ValueError(
            f'{where}a diagram needs {MIN_NODES} to {MAX_NODES} nodes: one node '
            f'draws no connection, and more than {MAX_NODES} is a picture a '
            f'reader cannot hold. Draw two diagrams instead'
        )
    nodes, seen = [], set()
    for index, item in enumerate(items, 1):
        spot = f'{where[:-2]} node {index}: '
        if not isinstance(item, dict):
            raise ValueError(f'{spot}a node holds an id and a label')
        node_id = text(item, 'id', spot)
        if node_id in seen:
            raise ValueError(f'{spot}the node id {node_id!r} is used twice')
        seen.add(node_id)
        nodes.append({'id': node_id, 'label': text(item, 'label', spot), 'where': spot})
    return nodes


def read_edges(section, nodes, where):
    """Every edge, checked against the nodes. An edge to a node that is not
    drawn points at nothing, so it stops the build and names the id."""
    items = field(section, 'edges', where)
    if not isinstance(items, list) or not items:
        raise ValueError(f'{where}a diagram needs at least one edge')
    known = {node['id'] for node in nodes}
    edges, touched = [], set()
    for index, item in enumerate(items, 1):
        spot = f'{where[:-2]} edge {index}: '
        if not isinstance(item, dict):
            raise ValueError(f'{spot}an edge holds from and to')
        pair = []
        for key in ('from', 'to'):
            value = text(item, key, spot)
            if value not in known:
                raise ValueError(
                    f'{spot}{key} is {value!r}, which is not a node of this '
                    f'diagram: the nodes are {", ".join(sorted(known))}'
                )
            pair.append(value)
            touched.add(value)
        if pair[0] == pair[1]:
            raise ValueError(f'{spot}from and to are both {pair[0]!r}')
        edges.append({
            'from': pair[0], 'to': pair[1],
            'label': optional_text(item, 'label', spot),
        })
    missing = [node['id'] for node in nodes if node['id'] not in touched]
    if missing:
        raise ValueError(
            f'{where}every node needs at least one edge, so the list under the '
            f'drawing names it: {", ".join(missing)} has none'
        )
    return edges


def curve(start, end):
    """One bowed line between two node centres, stopped short of both marks,
    with the point the edge label sits on. The bow is the cover's own."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    span = math.hypot(dx, dy) or 1
    ux, uy = dx / span, dy / span
    # A row of eight nodes puts two marks closer together than twice the gap,
    # and the full gap off both ends turns the line inside out. A third of the
    # span at each end is the most a short line can give up and still be a
    # line that points from one mark to the other.
    gap = min(EDGE_GAP, span / 3)
    x1, y1 = start[0] + ux * gap, start[1] + uy * gap
    x2, y2 = end[0] - ux * gap, end[1] - uy * gap
    cx = x1 + (x2 - x1) / 2 + (y2 - y1) * EDGE_BOW
    cy = y1 + (y2 - y1) / 2 - (x2 - x1) * EDGE_BOW
    return (
        f'M{x1:.1f} {y1:.1f}Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}',
        (x1 + 2 * cx + x2) / 4,
        (y1 + 2 * cy + y2) / 4,
    )


def node_svg(node, spot, index, theme):
    """One node: a mark from the cover's own set, and its label in sans."""
    shape = mark_shape(index)
    mark = (
        f'<g class="mark" stroke-width="{shape["weight"]:.2f}"'
        f' transform="translate({spot["x"]:.1f} {spot["y"]:.1f})'
        f' rotate({shape["angle"]:.1f}) scale({MARK_SCALE})">'
        f'{STROKE_ATTRS.sub("", shape["strokes"])}</g>'
    )
    lines = wrap(node['label'], spot['width'], node['where'])
    first = spot['ly'] - (len(lines) - 1) * LABEL_LEADING / 2 if spot['center'] else spot['ly']
    spans = ''.join(
        f'<tspan x="{spot["lx"]:.1f}" y="{first + row * LABEL_LEADING:.1f}">{esc(line)}</tspan>'
        for row, line in enumerate(lines)
    )
    label = (
        f'<text class="diagram-label" text-anchor="{spot["anchor"]}"'
        f' font-size="{LABEL_SIZE}" fill="{theme["ink"]}">{spans}</text>'
    )
    return mark, label


def edge_svg(edge, points, theme):
    """One line, and the words the author put on it. The label carries a
    halo of paper, so it stays readable where it crosses its own line."""
    path, mid_x, mid_y = curve(points[edge['from']], points[edge['to']])
    line = f'<path d="{path}"/>'
    if not edge['label']:
        return line, ''
    label = (
        f'<text class="diagram-edge-label" x="{mid_x:.1f}" y="{mid_y:.1f}"'
        f' text-anchor="middle" font-size="{LABEL_SIZE - 3}"'
        f' paint-order="stroke" stroke="{theme["paper"]}" stroke-width="4"'
        f' fill="{theme["ink"]}">{esc(edge["label"])}</text>'
    )
    return line, label


def drawing(nodes, edges, layout, theme):
    """The whole picture. It is hidden from assistive technology, because a
    screen reader gets nothing from a bare SVG; the list under it carries the
    same information in sentences."""
    height, spots = places(layout, len(nodes))
    points = {node['id']: (spots[i]['x'], spots[i]['y']) for i, node in enumerate(nodes)}
    marks, labels = [], []
    for index, node in enumerate(nodes):
        mark, label = node_svg(node, spots[index], index, theme)
        marks.append(mark)
        labels.append(label)
    lines, edge_labels = [], []
    for edge in edges:
        line, label = edge_svg(edge, points, theme)
        lines.append(line)
        edge_labels.append(label)
    return (
        f'<svg class="diagram-art" viewBox="0 0 {FRAME_W} {height:.0f}"'
        f' aria-hidden="true" fill="none">'
        f'<g class="diagram-lines" stroke="{theme["secondary"]}"'
        f' stroke-width="1.1" opacity=".85">{"".join(lines)}</g>'
        f'<g class="diagram-marks" stroke="{theme["ink"]}" stroke-linecap="round">'
        f'{"".join(marks)}</g>'
        f'{"".join(labels)}{"".join(edge_labels)}'
        f'</svg>'
    )


def render(section, heading_html, where, context):
    """The picture and the words. Both come from the same nodes and edges, so
    the two can never say different things."""
    markup = inline.for_section(section, where, term=context.term)
    layout = choice(section, 'layout', LAYOUTS, where)
    nodes = read_nodes(section, where)
    edges = read_edges(section, nodes, where)
    names = {node['id']: node['label'] for node in nodes}
    items = '\n'.join(
        f'<li>{esc(names[edge["from"]])} {esc(edge["label"] or "connects to")} '
        f'{esc(names[edge["to"]])}.</li>'
        for edge in edges
    )
    body = (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<figure class="diagram">\n'
        f'<div class="diagram-frame scroll-edge">'
        f'{drawing(nodes, edges, layout, context.theme)}</div>\n'
        f'<ol class="diagram-edges">\n{items}\n</ol>\n'
        f'{caption_html(section, where, markup)}\n'
        f'</figure>'
    )
    return body, ''
