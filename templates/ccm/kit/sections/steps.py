"""A numbered sequence on the reading column: the light sibling of the scrolly."""
from .. import inline
from ..text import esc, field, text

NAME = 'steps'
TITLE_REQUIRED = True
ORDER = 14
FIELDS = ('<code>label</code>, <code>title</code>, <code>items</code>: each has'
          ' <code>title</code> and <code>text</code>')
# One step is an instruction, not a sequence, so the type asks for two.
LEAST = 2
SPECIMEN = {
    'summary': 'A numbered sequence, one numeral and one instruction a step.',
    'use_when': 'Use it when the reader has to do the work in order.',
    'json': {
        'type': 'steps',
        'id': 'steps-specimen',
        'label': 'Example steps',
        'title': 'Start a shared reporting project.',
        'items': [
            {
                'title': 'Agree on one question',
                'text': 'An invented example. Write the question every partner answers, and keep it to one sentence.',
            },
            {
                'title': 'Name one editor',
                'text': 'One editor holds the schedule and answers every partner. The role moves between projects.',
            },
            {
                'title': 'Set the publication date',
                'text': 'Every partner publishes on the same day, so the work reaches readers as one story.',
            },
        ],
    },
}


def render_step(item, where, markup):
    """One step. The numeral is drawn by the list counter, so the markup holds
    the words and the stylesheet holds the count."""
    if not isinstance(item, dict):
        raise ValueError(f'{where}a step holds a title and a text')
    return (
        f'<li>\n'
        f'<h3>{esc(text(item, "title", where))}</h3>\n'
        f'<p>{markup(text(item, "text", where), where)}</p>\n'
        f'</li>'
    )


def render(section, heading_html, where, context):
    items = field(section, 'items', where)
    if not isinstance(items, list) or len(items) < LEAST:
        raise ValueError(
            f'{where}a steps section needs {LEAST} steps or more'
        )
    markup = inline.for_section(section, where, term=context.term)
    steps = '\n'.join(
        render_step(item, f'{where[:-2]} step {index}: ', markup)
        for index, item in enumerate(items, 1)
    )
    body = (
        f'<div class="reading">{heading_html}\n'
        f'<ol class="steps-list" role="list">\n{steps}\n</ol>\n'
        f'</div>'
    )
    return body, ''
