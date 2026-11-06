"""The drawing. One set of repeatable ink marks, four layouts, and the frame
report.js lays them out in."""
import hashlib
import math

from .text import esc

# One source of truth for the drawing. build.py writes MARKS marks and states
# the count on the SVG as data-marks; report.js reads that count and places
# every mark from it, so the two files can never drift apart.
MARKS = 12
FRAME_W = 720
FRAME_H = 540
CENTER_X = FRAME_W / 2
CENTER_Y = FRAME_H / 2
FALLBACK_RADIUS = 210
RING_RADIUS = 72
# report.js lays out any count of marks in this frame. The size comes from the
# viewBox and the ring from its own radius; the two values with no home in the
# markup ride on data attributes, so no number is written down twice.
FRAME_INSET = 60
MARK_WIDTH = 40
# The intro draws each stroke of a mark with one dash. pathLength makes every
# stroke that long whatever its own arc length is, so the dash always equals
# the stroke and no mark is left drawn short.
STROKE_DASH = 48
# The label sits inside the ring, in frame units, so it scales with the drawing
# instead of with the page. 22 units survives the phone and the printed sheet.
ART_LABEL = 22
LABEL_LIMIT = 14
LAYOUTS = ('scatter', 'groups', 'network', 'orbit')


def seed_from(*candidates):
    """The seed of one report's drawing, from the first field it supplies.

    A report states its own `url`, and no two reports share one, so the url is
    the first choice and the title is the fallback. The digest is blake2s and
    not Python's hash(), because hash() of a string is salted per process: the
    same report would draw a different cover on every build.

    A report with neither field takes seed 0, which is the drawing the kit
    shipped with, so the guide specimens and any caller that names no report
    keep the marks they had.
    """
    for value in candidates:
        if isinstance(value, str) and value.strip():
            digest = hashlib.blake2s(value.strip().encode('utf-8'), digest_size=4)
            return int.from_bytes(digest.digest(), 'big')
    return 0


def seeded(index, salt, seed=0):
    """A repeatable 0-to-1 value for one mark and one property of one report.
    Twelve marks that are siblings instead of clones start here, and the
    report's own seed makes one report's twelve marks differ from another's.
    seed 0 is the mark set the kit shipped with."""
    value = (index * 73856093) ^ (salt * 19349663) ^ (seed * 83492791)
    value = (value * 2654435761) & 0xFFFFFFFF
    value ^= value >> 16
    value = (value * 2246822519) & 0xFFFFFFFF
    return (value & 0xFFFFFF) / 0xFFFFFF


def mark_shape(index, seed=0):
    """One ink mark. Stroke count, size, weight and per-stroke jitter all come
    from the index, so the mark is the same on every build and different from
    its neighbors. A mark is 30 to 50 units wide in a 720 unit frame, about a
    fifteenth of it, and stroke, pitch and size hold one ratio, so the mark
    reads the same at 24px as it does at 240px."""
    count = 5 + int(seeded(index, 1, seed) * 7)
    pitch = min(50.0, max(30.0, (count - 1) * (5.5 + seeded(index, 2, seed) * 1.2))) / (count - 1)
    width = pitch * (count - 1)
    height = 36 + seeded(index, 3, seed) * 24
    strokes = []
    for j in range(count):
        x = j * pitch - width / 2
        top = -height / 2 * (.88 + seeded(index, 20 + j, seed) * .24)
        bottom = height / 2 * (.88 + seeded(index, 60 + j, seed) * .24)
        bow = x - pitch * (.9 + seeded(index, 100 + j, seed) * .5)
        end = x + pitch * (.1 + seeded(index, 140 + j, seed) * .3)
        # --j is the stroke's place in its mark. One rule in report.css turns
        # it and --i into the intro delay, so a mark of any stroke count
        # staggers without a rule per stroke.
        strokes.append(
            f'<path style="--j:{j}" pathLength="{STROKE_DASH}"'
            f' d="M{x:.2f} {top:.2f}Q{bow:.2f} 0 {end:.2f} {bottom:.2f}"/>'
        )
    return {
        'strokes': ''.join(strokes),
        'count': count,
        'weight': 1.35 + seeded(index, 4, seed) ** 2 * .85,
        'angle': seeded(index, 5, seed) * 360,
        'delay': int(seeded(index, 6, seed) * 120),
    }


def bow(index, seed):
    """How far one ruled line of the paper bends, in frame units. Under a whole
    unit, so the sheet stays ruled and only the hand that ruled it changes."""
    return seeded(index, 11, seed) * 2.4


def artwork(name, theme, center_label="Community", seed=0):
    """Original repeatable ink marks; no reference artwork or fonts are copied.
    Paint lands on the SVG as presentation attributes and each mark carries a
    starting transform, so the drawing reads even if the stylesheet or the
    script never arrives."""
    if len(center_label) > LABEL_LIMIT:
        raise ValueError(
            f'center_label must be {LABEL_LIMIT} characters or fewer to fit the ring: {center_label}'
        )
    marks = []
    for i in range(MARKS):
        shape = mark_shape(i, seed)
        angle = math.radians(i / MARKS * 360 - 90)
        x = CENTER_X + math.cos(angle) * FALLBACK_RADIUS
        y = CENTER_Y + math.sin(angle) * FALLBACK_RADIUS
        marks.append(
            f'<g class="mark" data-index="{i}" data-angle="{shape["angle"]:.1f}"'
            f' style="--i:{i};--md:{shape["delay"]}ms"'
            f' stroke-width="{shape["weight"]:.2f}"'
            f' transform="translate({x:.1f} {y:.1f}) rotate({shape["angle"]:.1f})"'
            f'>{shape["strokes"]}</g>'
        )
    # The ruling bows by a hand's width and the width comes from the report's
    # own seed, so no two reports carry the same sheet of paper under the marks.
    # The pitch stays at 30 units: a ruled sheet is regular, and only the hand
    # that ruled it changes.
    vertical_grid = ''.join(
        f'<path d="M{x} 25 Q{x - 2 - bow(i, seed):.1f} 270 {x + 1 + bow(i, 7 + seed):.1f} 515"/>'
        for i, x in enumerate(range(30, 710, 30))
    )
    horizontal_grid = ''.join(
        f'<path d="M20 {y} Q360 {y + 2 + bow(i, 13 + seed):.1f} 700 {y - 1 - bow(i, 19 + seed):.1f}"/>'
        for i, y in enumerate(range(30, 530, 30))
    )
    # The ruling dissolves under a radial mask instead of stopping at a rectangle.
    defs = (
        f'<defs><radialGradient id="{name}--fade">'
        f'<stop offset=".55" stop-color="#fff"/><stop offset="1" stop-color="#000"/>'
        f'</radialGradient>'
        f'<mask id="{name}--mask" maskUnits="userSpaceOnUse"'
        f' x="0" y="0" width="{FRAME_W}" height="{FRAME_H}">'
        f'<rect width="{FRAME_W}" height="{FRAME_H}" fill="url(#{name}--fade)"/>'
        f'</mask></defs>'
    )
    return (
        f'<svg class="ink-art" viewBox="0 0 {FRAME_W} {FRAME_H}" aria-hidden="true"'
        f' data-art="{name}" data-marks="{MARKS}" data-inset="{FRAME_INSET}"'
        f' data-mark="{MARK_WIDTH}" fill="none"'
        f' style="--stroke-len:{STROKE_DASH}">'
        f'{defs}'
        f'<g class="paper-grid" mask="url(#{name}--mask)" fill="none"'
        f' stroke="{theme["ink"]}" stroke-width=".5" opacity=".16">'
        f'{vertical_grid}{horizontal_grid}</g>'
        f'<g class="connections" fill="none" stroke="{theme["secondary"]}"'
        f' stroke-width="1.1" opacity=".85"></g>'
        f'<g class="marks" fill="none" stroke="{theme["ink"]}" stroke-linecap="round">'
        f'{"".join(marks)}</g>'
        f'<circle class="center-ring" cx="{CENTER_X:.0f}" cy="{CENTER_Y:.0f}"'
        f' r="{RING_RADIUS}" fill="none" stroke="{theme["accent"]}"'
        f' stroke-width=".8" opacity="0"/>'
        f'<text class="center-label" x="{CENTER_X:.0f}" y="{CENTER_Y:.0f}"'
        f' font-size="{ART_LABEL}" dominant-baseline="central" text-anchor="middle"'
        f' fill="{theme["ink"]}" opacity="0">{esc(center_label)}</text>'
        f'</svg>'
    )


def resolve_highlight(value, where=''):
    """highlight is a count of leading marks, or a list of mark indices."""
    if isinstance(value, bool):
        raise ValueError(f'{where}highlight must be an integer count or a list of mark indices: {value!r}')
    if isinstance(value, int):
        if not 0 <= value <= MARKS:
            raise ValueError(f'{where}highlight count must be an integer from 0 to {MARKS}: {value}')
        return list(range(value))
    if isinstance(value, list):
        indices = []
        for item in value:
            if isinstance(item, bool) or not isinstance(item, int):
                raise ValueError(f'{where}highlight list must hold integers: {item!r}')
            if not 0 <= item < MARKS:
                raise ValueError(f'{where}highlight index must be from 0 to {MARKS - 1}: {item}')
            if item in indices:
                raise ValueError(f'{where}highlight index is listed twice: {item}')
            indices.append(item)
        return indices
    raise ValueError(f'{where}highlight must be an integer count or a list of mark indices: {value!r}')


def mark_specimen(index, theme, seed=0):
    """One mark on its own, at the size the guide shows it."""
    shape = mark_shape(index, seed)
    return (
        f'<figure><svg class="mark-art" viewBox="-36 -36 72 72" width="80" height="80"'
        f' aria-hidden="true" fill="none">'
        f'<g class="marks" fill="none" stroke="{theme["ink"]}" stroke-linecap="round">'
        f'<g class="mark" stroke-width="{shape["weight"]:.2f}">{shape["strokes"]}</g>'
        f'</g></svg><figcaption>{shape["count"]} strokes</figcaption></figure>'
    )
