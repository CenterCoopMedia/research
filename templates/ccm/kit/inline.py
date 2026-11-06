"""One inline markup for every text field.

`[text](https://example.org)` is a link. `[^1]` is a reference to note 1 of
the same section. `{term}` is a glossary term. Every other character is
escaped the way esc() escapes it, so an author reaches the markup through
these three forms and through nothing else.

A reference to a note the section does not carry, and a term the glossary does
not hold, both stop the build and name the field.

Every id this module writes is `{sid}--{name}`, where `sid` is the id of the
section. page.py refuses a section id that holds two hyphens in a row, so a
generated id can never take the name of a section.
"""
import re

from .text import check_text, esc, url

# One pattern, so the three forms are read in one pass and none of them can
# hide inside another. A URL may hold one pair of parentheses, because many
# real addresses do, and a URL the parser cannot use stops the build rather
# than printing itself as text.
PATTERN = re.compile(
    r'\[([^\[\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)|\[\^(\d+)\]|\{([^{}]+)\}'
)
# The separator between the id of a section and the name of an id built from
# it. tabs.py uses the same two characters for the same reason.
SPLIT = '--'
# What each section rendered, keyed by the section id: each note number the
# renderer emitted a reference for, and how many references it emitted. It is
# the record notes.py holds a note against, so a note is measured by the
# references the page carries rather than by every string in the section. A
# `[^1]` in a title, and a `[^1]` a link consumed, render no reference and
# reach no note.
RENDERED = {}


def rendered(sid):
    """The record of one section: the note numbers its text rendered a
    reference for."""
    return RENDERED.get(sid, {})


def forget():
    """Drop every record. page.py calls it before the first section of a
    report, so one build never reads what an earlier build wrote."""
    RENDERED.clear()


def link(label, href, where):
    """A text link. The URL is absolute HTTP(S), the way every other URL in
    the kit is, and the link states rel="noopener"."""
    return f'<a href="{url(href, "link", where)}" rel="noopener">{esc(label)}</a>'


def reference(number, sid, notes, where, count=1):
    """A note reference. The number is the note's place in the section's own
    notes, so a section can be moved without renumbering the page. `count` is
    the place of this reference among the references to that note in the same
    section: the first keeps the plain id, and each one after it adds its own
    number, so a note cited twice writes two ids and one note to point at."""
    if not 1 <= number <= len(notes):
        raise ValueError(
            f'{where}[^{number}] has no note {number}: the section carries '
            f'{len(notes)}'
        )
    note = f'{sid}{SPLIT}note-{number}'
    ref = f'{sid}{SPLIT}ref-{number}'
    if count > 1:
        ref = f'{ref}-{count}'
    return (
        f'<sup><a href="#{note}" id="{ref}" '
        f'aria-describedby="{note}">{number}</a></sup>'
    )


def glossary(name, term, where):
    """A glossary term. The caller supplies the function that renders it, so
    the parser holds no glossary of its own. `where` goes to that function as
    well, so a term the glossary does not hold names its section and its
    field."""
    if term is None:
        raise ValueError(
            f'{where}{{{name}}} is a glossary term, and this field was rendered '
            f'with no glossary to read'
        )
    rendered_term = term(name, where)
    if rendered_term is None:
        raise ValueError(f'{where}{{{name}}} is not in the glossary')
    return rendered_term


def render(value, where='', sid='', notes=(), term=None, seen=None):
    """One text field, escaped, with the three inline forms rendered. `seen`
    counts the references to each note, so the count runs over every field of
    one section rather than over one field alone."""
    check_text(value, 'text', where)
    if seen is None:
        seen = {}
    parts = []
    last = 0
    for match in PATTERN.finditer(value):
        parts.append(esc(value[last:match.start()]))
        label, href, number, name = match.groups()
        if href is not None:
            parts.append(link(label, href, where))
        elif number is not None:
            index = int(number)
            seen[index] = seen.get(index, 0) + 1
            parts.append(reference(index, sid, notes, where, seen[index]))
        else:
            parts.append(glossary(name, term, where))
        last = match.end()
    parts.append(esc(value[last:]))
    return ''.join(parts)


def plain(value, where=''):
    """One text field with the markup reduced to what a reader sees: a link
    becomes its text, a term becomes the term, and a note reference goes. The
    text is not escaped, because it is read against text an author wrote and
    not written into the page. A pull quote is held against this, so an author
    lifts the sentence a reader sees rather than the source that makes it."""
    check_text(value, 'text', where)
    parts = []
    last = 0
    for match in PATTERN.finditer(value):
        parts.append(value[last:match.start()])
        label, href, number, name = match.groups()
        if href is not None:
            parts.append(label)
        elif number is None:
            parts.append(name)
        last = match.end()
    parts.append(value[last:])
    return ''.join(parts)


def for_section(section, where, term=None):
    """The renderer one section's text fields use. It carries the section's id
    and its notes, so a reference names a note of its own section."""
    sid = section.get('id', '')
    notes = section.get('notes')
    if notes is None:
        notes = []
    if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
        raise ValueError(f'{where}notes must be a list of strings')

    # One count for the whole section, because the id has to be unique on the
    # page and a note can be cited from more than one field of its section.
    # The same count is the section's record: notes.py reads its keys, so it
    # holds each note against the references this renderer emitted.
    seen = {}
    RENDERED[sid] = seen

    def markup(value, spot=None):
        return render(value, where if spot is None else spot, sid, notes, term, seen)

    markup.rendered = seen
    return markup
