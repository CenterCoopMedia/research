"""A chapter opener: the part number, the part title, and a short deck."""
from .. import inline
from ..text import field, optional_text

NAME = 'part'
TITLE_REQUIRED = True
ORDER = 65
FIELDS = '<code>number</code>, <code>title</code>, optional <code>deck</code>'
SPECIMEN = {
    'summary': 'A part number and a part title, with space above and below.',
    'use_when': 'Use it when a report is long enough to read as chapters.',
    'json': {
        'type': 'part',
        'id': 'part-specimen',
        'number': 2,
        'title': 'What the partners found',
        'deck': 'An invented deck. Say in one sentence what this part of the report covers.',
    },
}


def number(section, where):
    """The part number. It counts 1, 2, 3 and never pads with a zero: a
    padded number sorts a list that can pass nine, and a report has no such
    list. A number the author writes as text would print its own quotes."""
    value = field(section, 'number', where)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f'{where}number must be a whole number, such as 2: {value!r}'
        )
    if value < 1:
        raise ValueError(f'{where}number must be 1 or more: {value}')
    return str(value)


def render(section, heading_html, where, context):
    """The numeral is the one thing on this page besides the cover title that
    is allowed to be large. The deck sits on the reading column under it, so
    the opener is a pause and not a page of its own."""
    markup = inline.for_section(section, where, term=context.term)
    deck = optional_text(section, 'deck', where)
    deck_html = f'<p class="part-deck">{markup(deck)}</p>\n' if deck else ''
    body = (
        f'<div class="part">\n'
        f'<p class="part-number"><span class="part-kicker">Part </span>'
        f'{number(section, where)}</p>\n'
        f'{heading_html}\n'
        f'{deck_html}'
        f'</div>'
    )
    return body, ''
