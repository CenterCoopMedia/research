"""The two to five points a reader keeps after one pass."""
from .. import inline
from ..text import check_text, field

NAME = 'takeaways'
TITLE_REQUIRED = True
ORDER = 8
FIELDS = ('<code>label</code>, <code>title</code>, <code>items</code>'
          ' (list of text, 2 to 5)')
# Under two points is a sentence, and over five is the report again, so the
# block stops being the thing a reader can hold in one look.
LEAST, MOST = 2, 5
SPECIMEN = {
    'summary': 'A short list of the points a reader keeps, on a tinted block.',
    'use_when': 'Use it at the top, when a reader who stops here needs the result.',
    'json': {
        'type': 'takeaways',
        'id': 'takeaways-specimen',
        'label': 'Example takeaways',
        'title': 'Keep these three points.',
        'items': [
            'Shared reporting reaches readers that one newsroom cannot reach alone.',
            'A collaboration needs one editor who holds the schedule.',
            'An invented example. Replace each line with a point your report proves.',
        ],
    },
}


def render(section, heading_html, where, context):
    items = field(section, 'items', where)
    if not isinstance(items, list):
        raise ValueError(f'{where}items must be a list of {LEAST} to {MOST} sentences')
    if not LEAST <= len(items) <= MOST:
        raise ValueError(
            f'{where}takeaways holds {LEAST} to {MOST} items, and this section '
            f'holds {len(items)}'
        )
    markup = inline.for_section(section, where, term=context.term)
    rows = []
    for index, item in enumerate(items, 1):
        spot = f'{where[:-2]} item {index}: '
        rows.append(f'<li>{markup(check_text(item, "item", spot), spot)}</li>')
    body = (
        f'<div class="reading">{heading_html}\n'
        f'<ul class="takeaways">\n' + '\n'.join(rows) + f'\n</ul>\n'
        f'</div>'
    )
    return body, ''
