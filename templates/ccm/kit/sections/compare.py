"""Two pictures of the same thing, before and after."""
from .. import inline
from ..text import esc, field, text
from .image import caption_html, picture, placeholder

NAME = 'compare'
TITLE_REQUIRED = True
ORDER = 62
FIELDS = ('<code>label</code>, <code>title</code>, <code>before</code> and'
          ' <code>after</code>: each has <code>src</code>, <code>alt</code>,'
          ' <code>label</code>; optional <code>caption</code>')
SPECIMEN = {
    'summary': 'Two pictures side by side, with a divider a reader can move.',
    'use_when': 'Use it when one picture changes and the change is the point.',
    'json': {
        'type': 'compare',
        'id': 'compare-specimen',
        'label': 'Example comparison',
        'title': 'Show the change, do not describe it.',
        'before': {
            'src': placeholder(2),
            'alt': 'A field of bowed ink strokes on a tinted ground.',
            'label': 'Before',
        },
        'after': {
            'src': placeholder(2, accent=True),
            'alt': 'The same field of strokes, drawn in the accent color.',
            'label': 'After',
        },
        'caption': 'Both pictures are placeholders. Point src at your own two files, cropped to one size.',
    },
}


def render_side(section, key, where):
    """One of the two pictures, with its own label above it. A label under
    both pictures makes the reader work out which one it names."""
    item = field(section, key, where)
    if not isinstance(item, dict):
        raise ValueError(f'{where}{key} holds src, alt and label')
    spot = f'{where[:-2]} {key}: '
    return (
        f'<figure class="compare-side compare-{key}">\n'
        f'<figcaption class="compare-label">{esc(text(item, "label", spot))}</figcaption>\n'
        f'{picture(item, spot)}\n'
        f'</figure>'
    )


def render(section, heading_html, where, context):
    """Side by side is the base state, and it is what prints and what a
    reader with no scripting sees. The script lays one picture over the other
    and hands the reader the range input that moves the divider."""
    markup = inline.for_section(section, where, term=context.term)
    sid = text(section, 'id', where)
    control = (
        f'<div class="compare-control screen-only" hidden>\n'
        f'<label for="{sid}--compare">Move the divider</label>\n'
        f'<input type="range" id="{sid}--compare" min="0" max="100" step="2"'
        f' value="50" aria-valuetext="50 percent">\n'
        f'</div>'
    )
    body = (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<figure class="compare">\n'
        f'<div class="compare-pair">\n'
        f'{render_side(section, "before", where)}\n'
        f'{render_side(section, "after", where)}\n'
        f'</div>\n'
        f'{control}\n'
        f'{caption_html(section, where, markup)}\n'
        f'</figure>'
    )
    return body, ''
