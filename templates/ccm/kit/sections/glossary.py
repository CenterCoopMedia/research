"""The glossary, and the definition control every {term} in the report renders.

The list is the record: one entry a term, alphabetized, anchored. The control
is a button beside the word that opens the same definition where the reader is
reading. One popover holds each definition, in the glossary section, and every
mention of that term points at it, so a term used ten times adds ten buttons
and no extra text.
"""
import re

from .. import inline
from ..text import esc, field, text

NAME = 'glossary'
TITLE_REQUIRED = True
ORDER = 16
FIELDS = ('<code>title</code>, <code>terms</code>: each has <code>term</code>'
          ' and <code>definition</code>')
# A definition longer than this needs its own scrollbar in the popover, and a
# reader who has to scroll a popover is better served by the entry itself.
WORDS = 40
LINK_LABEL = 'Open the glossary entry'
# A note reference in a definition. The definition is rendered twice, in the
# entry and in the popover, so a reference in one would write the reference id
# twice as well.
REFERENCE = re.compile(r'\[\^\d+\]')
SPECIMEN = {
    'summary': 'An alphabetized list of terms, with an anchor on every term.',
    'use_when': 'Use it when the report needs words a general reader does not hold.',
    'json': {
        'type': 'glossary',
        'id': 'glossary-specimen',
        'title': 'Terms used in this report',
        'terms': [
            {
                'term': 'shared beat',
                'definition': 'One reporter who covers a subject for several newsrooms at once. The newsrooms share the cost and publish the same reporting.',
            },
            {
                'term': 'collaborative reporting',
                'definition': 'Two or more newsrooms that report one story together. A {shared beat} is one form of it.',
            },
        ],
    },
}


def order(names):
    """The terms of one section in the order the page shows them: A to Z, with
    the order the author wrote them breaking a tie."""
    return sorted(names, key=lambda name: name.casefold())


def anchors(sid, names):
    """The id of each term and the id of its popover, keyed by the term. The
    ids count the sorted terms rather than spelling them, so a term in any
    writing system takes an anchor, two terms that differ only in an accent
    take two, and the reserved separator keeps both off the name of a section.
    """
    return {
        name: (f'{sid}{inline.SPLIT}term-{index}',
               f'{sid}{inline.SPLIT}definition-{index}')
        for index, name in enumerate(order(names), 1)
    }


def check_definition(name, definition, where=''):
    count = len(definition.split())
    if count > WORDS:
        raise ValueError(
            f'{where}the definition of {name!r} runs {count} words, and a '
            f'definition holds {WORDS} or fewer: put the longer text in a section'
        )
    if REFERENCE.search(definition):
        raise ValueError(
            f'{where}the definition of {name!r} holds a note reference, and a '
            f'definition is rendered twice, in the entry and in the popover: '
            f'put the note on the text that uses the term'
        )
    return definition


def term_control(name, definition, where, ids):
    """What a {term} becomes in any text field. The button carries no
    aria-expanded of its own: a button with popovertarget reports the state of
    its popover to assistive technology already, and a written attribute would
    go stale the first time the reader opened it.

    The link beside it is the whole control with scripts off, so a reader who
    never sees the popover still reaches the definition.
    """
    check_definition(name, definition, where)
    term_id, definition_id = ids
    label = esc(name)
    return (
        f'<span class="definition">'
        f'<button type="button" class="definition-term" '
        f'popovertarget="{definition_id}">{label}</button>'
        f'<a class="definition-link" href="#{term_id}">{label}</a>'
        f'</span>'
    )


def entry(name, definition_html, term_id):
    """One row of the list. The term takes tabindex="-1" so a jump to it moves
    the reader's focus as well as the page, and lands under the sticky header
    through the scroll padding the page already carries."""
    return (
        f'<div class="glossary-entry">\n'
        f'<dt id="{term_id}" tabindex="-1">{esc(name)}</dt>\n'
        f'<dd>{definition_html}</dd>\n'
        f'</div>'
    )


def popover(name, definition_html, ids):
    """The definition where the reader is reading. It holds the term, the
    definition and a link to the entry, and nothing that needs a scrollbar."""
    term_id, definition_id = ids
    return (
        f'<div id="{definition_id}" class="definition-popover" popover>\n'
        f'<p class="definition-name">{esc(name)}</p>\n'
        f'<p class="definition-text">{definition_html}</p>\n'
        f'<a class="definition-more" href="#{term_id}">{LINK_LABEL}</a>\n'
        f'</div>'
    )


def read_terms(section, where):
    """Every term of one section, checked in the order the author wrote them,
    so an error names the line the author is looking at."""
    items = field(section, 'terms', where)
    if not isinstance(items, list) or not items:
        raise ValueError(f'{where}terms must be a list with at least one term')
    read = []
    for index, item in enumerate(items, 1):
        spot = f'{where[:-2]} term {index}: '
        if not isinstance(item, dict):
            raise ValueError(f'{spot}a term holds a term and a definition')
        name = text(item, 'term', spot)
        definition = check_definition(name, text(item, 'definition', spot), spot)
        read.append((name, definition, spot))
    return read


def render(section, heading_html, where, context):
    """The list is sorted here rather than in the JSON, so an author adds a
    term at the end of the file and the page still reads A to Z. The ids come
    off the context, which read every glossary section before the first section
    rendered, so a mention in the first section and the entry in the last one
    write one name."""
    markup = inline.for_section(section, where, term=context.term)
    entries, popovers = [], []
    for name, definition, spot in sorted(read_terms(section, where),
                                         key=lambda read: read[0].casefold()):
        ids = context.anchors[name]
        definition_html = markup(definition, spot)
        entries.append(entry(name, definition_html, ids[0]))
        popovers.append(popover(name, definition_html, ids))
    body = (
        f'<div class="reading">{heading_html}\n'
        f'<dl class="glossary">\n' + '\n'.join(entries) + '\n</dl>\n'
        f'</div>\n'
        f'<div class="definitions screen-only">\n' + '\n'.join(popovers) + '\n</div>'
    )
    return body, ''
