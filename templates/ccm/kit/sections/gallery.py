"""A filmstrip of pictures the reader steps through at their own pace."""
from .. import inline
from ..text import field
from .image import caption_html, picture, placeholder

NAME = 'gallery'
TITLE_REQUIRED = True
ORDER = 63
FIELDS = ('<code>label</code>, <code>title</code>, <code>items</code>: each has'
          ' <code>src</code>, <code>alt</code>, <code>caption</code>')
MIN_ITEMS = 2
MAX_ITEMS = 12
SPECIMEN = {
    'summary': 'Pictures in one strip, with a caption on each and buttons that step through them.',
    'use_when': 'Use it when a report holds more pictures than the column can carry.',
    'json': {
        'type': 'gallery',
        'id': 'gallery-specimen',
        'label': 'Example gallery',
        'title': 'Let the reader set the pace.',
        'items': [
            {
                'src': placeholder(3),
                'alt': 'A field of bowed ink strokes, the tallest on the left.',
                'caption': 'This picture is a placeholder. Give every picture its own caption.',
            },
            {
                'src': placeholder(7),
                'alt': 'A field of bowed ink strokes at even heights.',
                'caption': 'A caption says what the reader is looking at, not what the set is about.',
            },
            {
                'src': placeholder(11, accent=True),
                'alt': 'A field of bowed ink strokes in the accent color.',
                'caption': 'Nothing here moves on its own. The reader steps through the strip.',
            },
        ],
    },
}


def render_item(item, where, markup):
    """One picture and its own caption. A set with one caption for all of it
    tells the reader nothing about the picture in front of them."""
    if not isinstance(item, dict):
        raise ValueError(f'{where}an item holds src, alt and caption')
    if not item.get('caption'):
        raise ValueError(f'{where}caption is required: every picture needs its own')
    return (
        f'<li class="gallery-item">\n'
        f'<figure>\n{picture(item, where)}\n'
        f'{caption_html(item, where, markup)}\n</figure>\n</li>'
    )


def render(section, heading_html, where, context):
    """The strip scrolls by hand with no scripting, so the buttons and the
    count start hidden and the script shows them. Nothing moves on its own:
    a picture changes when the reader asks for it."""
    markup = inline.for_section(section, where, term=context.term)
    items = field(section, 'items', where)
    if not isinstance(items, list) or not MIN_ITEMS <= len(items) <= MAX_ITEMS:
        raise ValueError(
            f'{where}a gallery holds {MIN_ITEMS} to {MAX_ITEMS} pictures: '
            f'one picture is an image section, and more than {MAX_ITEMS} is a '
            f'strip the reader gives up on'
        )
    total = len(items)
    strip = '\n'.join(
        render_item(item, f'{where[:-2]} item {i + 1}: ', markup)
        for i, item in enumerate(items)
    )
    bar = (
        f'<div class="gallery-bar screen-only" hidden>\n'
        f'<button type="button" class="control gallery-step" data-step="-1">'
        f'Show previous picture</button>\n'
        f'<p class="gallery-count" role="status">1 of {total}</p>\n'
        f'<button type="button" class="control gallery-step" data-step="1">'
        f'Show next picture</button>\n'
        f'</div>'
    )
    body = (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<div class="gallery" data-total="{total}">\n'
        f'<ol class="gallery-strip" role="list">\n{strip}\n</ol>\n'
        f'{bar}\n'
        f'</div>'
    )
    return body, ''
