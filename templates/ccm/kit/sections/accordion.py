"""A list of summaries a reader opens one at a time, or all at once.

Native <details>, so it opens with no script and prints with no script. When
`exclusive` is true every item carries the section id as its `name` and the
browser closes the open one for the reader.
"""
from .. import inline
from ..text import field, paragraphs, text

NAME = 'accordion'
TITLE_REQUIRED = True
ORDER = 52
FIELDS = ('<code>label</code>, <code>title</code>, <code>items</code>: each has'
          ' <code>summary</code> and <code>paragraphs</code>; optional'
          ' <code>exclusive</code>')
# The chevron the summary carries. It is drawn, not typed, so no screen reader
# reads a punctuation mark in place of the state.
CHEVRON = (
    '<svg class="accordion-chevron" viewBox="0 0 12 12" width="12" height="12"'
    ' aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.25"'
    ' stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M3 4.5 6 7.5 9 4.5"/></svg>'
)
SPECIMEN = {
    'summary': 'Summaries a reader opens for the detail under each one.',
    'use_when': 'Use it when most readers skip the detail and a few readers need all of it.',
    'json': {
        'type': 'accordion',
        'id': 'accordion-specimen',
        'label': 'Example questions',
        'title': 'The questions readers ask most.',
        'exclusive': True,
        'items': [
            {
                'summary': 'How were the newsrooms selected?',
                'paragraphs': [
                    'An invented answer for the template. State the sampling frame and who it leaves out.',
                ],
            },
            {
                'summary': 'What does the count measure?',
                'paragraphs': [
                    'An invented answer for the template. State the unit, the period, and the source.',
                    'Keep the summary above useful on its own, because many readers never open it.',
                ],
            },
        ],
    },
}


def render_item(item, sid, spot, markup, exclusive):
    """One <details>. The shared name is what makes the group exclusive, so it
    is written only when the section asks for it."""
    if not isinstance(item, dict):
        raise ValueError(f'{spot}an item holds a summary and paragraphs')
    name = f' name="{sid}"' if exclusive else ''
    summary = markup(text(item, 'summary', spot), spot)
    body = paragraphs(field(item, 'paragraphs', spot), spot,
                      lambda value, at=spot: markup(value, at))
    return (
        f'<details class="accordion-item"{name}>\n'
        f'<summary><span class="accordion-label">{summary}</span>{CHEVRON}</summary>\n'
        f'<div class="accordion-panel">\n{body}\n</div>\n'
        f'</details>'
    )


def render(section, heading_html, where, context):
    """Every item, in the order the report writes them."""
    items = field(section, 'items', where)
    if not isinstance(items, list) or not items:
        raise ValueError(f'{where}items must be a list of at least one item')
    exclusive = section.get('exclusive', False)
    if not isinstance(exclusive, bool):
        raise ValueError(
            f'{where}exclusive must be true or false, not '
            f'{type(exclusive).__name__}: {exclusive!r}'
        )
    sid = section['id']
    markup = inline.for_section(section, where, term=context.term)
    rows = '\n'.join(
        render_item(item, sid, f'{where[:-2]} item {index}: ', markup, exclusive)
        for index, item in enumerate(items, 1)
    )
    body = (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<div class="accordion reading">\n{rows}\n</div>'
    )
    return body, ''
