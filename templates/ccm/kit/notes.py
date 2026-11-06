"""The notes of one section: the sidenote and the footnote.

page.py calls render() after the body of every section, inside the section, so
one module renders the notes of every section type and no section module holds
note markup of its own.

One note is written twice. Wide enough, and with scripts, the sidenote in the
margin is the one the reader sees and the footnote is hidden; every other
width, print, and scripts off show the footnote at the end of the section and
hide the sidenote. Both copies are hidden the way that also takes them out of
the accessibility tree and the tab order, so a reader hears one note and a
link inside a note is reachable in the copy that is on the page. The id that
the reference points at travels with the copy that is shown: the markup gives
it to the footnote, and scripts/50-notes.js hands it to the sidenote while the
sidenote is the one on the page.
"""
from . import inline
from .text import esc

TITLE = 'Notes'
BACK_LABEL = 'Back to the text'


def check_notes(section, where, sid):
    """Every note of the section, held against the references the body
    rendered. The record comes from the renderer, so a `[^1]` that reached the
    page counts and a `[^1]` in a title, or one that a link consumed, does
    not: neither of those two writes a reference for the note to point back
    at."""
    notes = section.get('notes')
    if notes is None:
        return []
    if not isinstance(notes, list) or any(not isinstance(n, str) for n in notes):
        raise ValueError(f'{where}notes must be a list of strings')
    points_at = inline.rendered(sid)
    for number in range(1, len(notes) + 1):
        if number not in points_at:
            raise ValueError(
                f'{where}note {number} has no [^{number}] reference on the '
                f'page, so nothing reaches it: a title and a link are not '
                f'inline markup, and a [^{number}] in one renders no reference'
            )
    return notes


def sidenote(number, note_html, sid):
    """The margin copy. It takes tabindex="-1" so the reference lands the
    reader's focus on it while it is the copy the id belongs to."""
    return (
        f'<p class="sidenote" tabindex="-1" '
        f'data-ref="{sid}{inline.SPLIT}ref-{number}">'
        f'<span class="sidenote-number">{number}</span>{note_html}</p>'
    )


def footnote(number, note_html, sid):
    """The end-of-section copy. The back link is a link to the reference, which
    is itself a link, so the browser moves the reader's focus with the page and
    the reader carries on from the word they left."""
    return (
        f'<li id="{sid}{inline.SPLIT}note-{number}" tabindex="-1">{note_html} '
        f'<a class="note-back screen-only" '
        f'href="#{sid}{inline.SPLIT}ref-{number}">{esc(BACK_LABEL)}</a></li>'
    )


def render(section, sid, where, context):
    """Every note of one section, as one string. `section` is the section, `sid`
    is its id, which numbers each note, `where` names the section in an error,
    and `context` carries the report's glossary, so a `{term}` inside a note
    renders the same definition control the body renders."""
    notes = check_notes(section, where, sid)
    if not notes:
        return ''
    sidenotes, footnotes = [], []
    for number, note in enumerate(notes, 1):
        # The note is rendered without the section's own notes: a reference
        # inside a note would write a second element with the id the body
        # already carries. The glossary travels, because a definition control
        # writes no id of the body's.
        note_html = inline.render(
            note, f'{where[:-2]} note {number}: ', term=context.term
        )
        sidenotes.append(sidenote(number, note_html, sid))
        footnotes.append(footnote(number, note_html, sid))
    return (
        f'<aside class="sidenotes screen-only">\n' + '\n'.join(sidenotes) + '\n</aside>\n'
        f'<div class="footnotes">\n'
        f'<h3 class="footnotes-title">{esc(TITLE)}</h3>\n'
        f'<ol class="footnote-list">\n' + '\n'.join(footnotes) + '\n</ol>\n'
        f'</div>\n'
    )
