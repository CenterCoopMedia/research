"""One lifted sentence on the reading column, with its attribution."""
from .. import inline
from ..text import text

NAME = 'quote'
TITLE_REQUIRED = False
ORDER = 40
FIELDS = '<code>text</code>, <code>attribution</code>'
SPECIMEN = {
    'summary': 'One sentence at display size, opened by a short accent rule.',
    'use_when': 'Use it when one voice states the point better than the report can.',
    'json': {
        'type': 'quote',
        'id': 'quote-specimen',
        'text': 'A useful report lets the reader see the evidence, follow the reasoning, and ask a better question.',
        'attribution': 'Template editorial principle',
    },
}


def render(section, heading_html, where, context):
    """<footer> inside a blockquote maps to a second contentinfo landmark,
    because a blockquote is not sectioning content. The attribution is a
    paragraph with a <cite> in it instead."""
    markup = inline.for_section(section, where, term=context.term)
    body = (
        f'<blockquote>\n'
        f'<p>{markup(text(section, "text", where))}</p>\n'
        f'<p class="quote-attribution">'
        f'<cite>{markup(text(section, "attribution", where))}</cite></p>\n'
        f'</blockquote>'
    )
    return body, ''
