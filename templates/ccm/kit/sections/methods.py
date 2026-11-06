"""The methods band: how the work was done, and what it cites."""
from urllib.parse import urlsplit

from .. import endmatter, inline
from ..text import esc, field, optional_text, paragraphs, text, url

NAME = 'methods'
TITLE_REQUIRED = True
ORDER = 90
FIELDS = ('<code>title</code>, <code>paragraphs</code>, optional <code>brief</code>,'
          ' <code>sources</code>: each has <code>label</code>, <code>url</code>')
SPECIMEN = {
    'summary': 'A tinted band that carries the method note and the citation list.',
    'use_when': 'Use it at the end, when the reader needs the method and the sources.',
    'json': {
        'type': 'methods',
        'id': 'methods-specimen',
        'title': 'Methods and sources',
        'brief': 'Replace this lead with two plain sentences on what you counted and '
                 'how you counted it. The note under it carries the detail.',
        'paragraphs': [
            'Replace this note with the study period, the sample, the method, the limits, the funding, and the disclosures.',
        ],
        'sources': [
            {'label': 'Center for Cooperative Media', 'url': 'https://centerforcooperativemedia.org/'},
            {'label': 'Montclair State University', 'url': 'https://www.montclair.edu/'},
        ],
    },
}
# The lead answers "can I trust this?" for a reader who will not read the whole
# note, so it stays short enough to read in one pass.
BRIEF_WORDS = 80


def render_source(source, where):
    """A citation row: the label is the link, the host says where it points."""
    href = url(field(source, 'url', where), 'url', where)
    host = esc(urlsplit(source['url']).netloc)
    return (
        f'<li><a href="{href}">{esc(text(source, "label", where))}</a>'
        f'<span class="source-host">{host}</span></li>'
    )


def render_brief(section, where, markup):
    """"How we did this": the plain-language lead at the top of the band, above
    the note that carries the detail."""
    value = optional_text(section, 'brief', where)
    if not value:
        return ''
    words = len(value.split())
    if words > BRIEF_WORDS:
        raise ValueError(
            f'{where}brief must be under {BRIEF_WORDS} words, and this one holds '
            f'{words}'
        )
    return (
        f'<div class="methods-brief">\n'
        f'<h3>How we did this</h3>\n'
        f'<p>{markup(value, where)}</p>\n'
        f'</div>\n'
    )


def render(section, heading_html, where, context):
    """Two columns on the band: the note on the reading measure, the citations
    and the downloads beside it. One column of prose in the middle of a
    full-bleed tint leaves the band empty on both sides."""
    markup = inline.for_section(section, where, term=context.term)
    sources = section.get('sources', [])
    citations = ''
    if sources:
        items = '\n'.join(
            render_source(source, f'{where[:-2]} source {i + 1}: ')
            for i, source in enumerate(sources)
        )
        citations = f'<ol>\n{items}\n</ol>\n'
    # The downloads read a top-level field, so endmatter.py holds them, and the
    # band places them: a file list belongs beside the citations it backs. The
    # list comes from the context, which counted the bands once, so the files
    # cannot print twice.
    downloads = ''
    if context.downloads is not None:
        downloads = endmatter.downloads_markup(context.downloads)
    aside = ''
    if citations or downloads:
        aside = f'<div class="methods-aside">\n{citations}{downloads}</div>\n'
    rows = len(sources) + len(context.downloads or [])
    body = (
        f'<div class="methods" data-aside="{rows}">\n'
        f'<div class="reading">{heading_html}\n'
        f'{render_brief(section, where, markup)}'
        f'{paragraphs(field(section, "paragraphs", where), where, markup)}\n'
        f'</div>\n'
        f'{aside}'
        f'</div>'
    )
    # The section states its citation count for the author and for a stylesheet
    # that keys on it. The grid keys on data-aside, which counts the downloads
    # in the same column.
    return body, f' data-sources="{len(sources)}"'
