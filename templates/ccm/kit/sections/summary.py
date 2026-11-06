"""The "in brief" block: what the report holds, in under 100 words."""
from .. import inline
from ..text import text

NAME = 'summary'
TITLE_REQUIRED = True
ORDER = 6
FIELDS = '<code>title</code>, <code>text</code> (under 100 words)'
# A reader decides to continue inside the first screen, so the block is capped
# at the length that fits one.
WORDS = 100
SPECIMEN = {
    'summary': 'A compressed abstract with its own landmark, for the top of a report.',
    'use_when': 'Use it when a reader decides in one screen whether to read on.',
    'json': {
        'type': 'summary',
        'id': 'summary-specimen',
        'title': 'In brief',
        'text': (
            'An invented example. This block states what the report holds, so a '
            'reader can decide to continue. Write it last, after the report is '
            'finished. Do not repeat the standfirst: the standfirst offers the '
            'report and this block states its content.'
        ),
    },
}


def render(section, heading_html, where, context):
    """The block names the whole section through aria-labelledby, so a reader
    who moves by landmark hears "in brief" and can jump to it. The name sits on
    the heading block rather than on the <h2>, because page.py writes the
    heading and the label above it as one string.

    The name is built with the reserved separator, so it can never take the id
    of a section: `brief--label` names the heading of the section `brief`, and
    an author who wants a section called `brief--label` is refused the id."""
    body_text = text(section, 'text', where)
    count = len(body_text.split())
    if count > WORDS:
        raise ValueError(
            f'{where}text runs {count} words, and a summary holds {WORDS} or fewer'
        )
    markup = inline.for_section(section, where, term=context.term)
    name = f'{section.get("id", "")}{inline.SPLIT}label'
    body = (
        f'<div class="reading summary">\n'
        f'<div class="summary-heading" id="{name}">{heading_html}</div>\n'
        f'<p>{markup(body_text)}</p>\n'
        f'</div>'
    )
    return body, f' aria-labelledby="{name}"'
