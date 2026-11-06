"""A chronology: a column of dates and, beside each one, what happened."""
from .. import inline
from ..text import esc, field, text

NAME = 'timeline'
TITLE_REQUIRED = True
ORDER = 60
FIELDS = ('<code>label</code>, <code>title</code>, <code>events</code>: each has'
          ' <code>date</code>, <code>title</code>, <code>text</code>')
SPECIMEN = {
    'summary': 'Dated events in one column, with the date beside each one.',
    'use_when': 'Use it when the order of the events is the argument.',
    'json': {
        'type': 'timeline',
        'id': 'timeline-specimen',
        'label': 'Example chronology',
        'title': 'How the work moved.',
        'events': [
            {
                'date': 'March 2024',
                'title': 'The partners agree on one question',
                'text': 'An invented event. Replace it with a dated step of your own work.',
            },
            {
                'date': 'September 2024',
                'title': 'The first shared story runs',
                'text': 'State what happened and why the date matters. Keep each event to one or two sentences.',
            },
            {
                'date': 'Spring 2025',
                'title': 'The group reports on the result',
                'text': 'A date is text, so "Spring 2025" and "12 May 2025" both hold their own form.',
            },
        ],
    },
}


def render_event(event, where, markup):
    """One dated event. The date is text and prints as the author wrote it:
    a chronology that spans "1998" and "12 May 2025" cannot take one date
    format without losing the shape the author chose."""
    return (
        f'<li>\n'
        f'<span class="timeline-date">{esc(text(event, "date", where))}</span>\n'
        f'<div class="timeline-event">\n'
        f'<h3>{esc(text(event, "title", where))}</h3>\n'
        f'<p>{markup(text(event, "text", where), where)}</p>\n'
        f'</div>\n'
        f'</li>'
    )


def render(section, heading_html, where, context):
    """The events keep the order the author wrote them in. A chronology the
    build re-sorts is a chronology the author cannot control, and a date here
    is free text that no sort can read."""
    events = field(section, 'events', where)
    if not isinstance(events, list) or len(events) < 2:
        raise ValueError(
            f'{where}a timeline needs two events or more: one event is a '
            f'paragraph with a date in it'
        )
    markup = inline.for_section(section, where, term=context.term)
    items = '\n'.join(
        render_event(event, f'{where[:-2]} event {i + 1}: ', markup)
        for i, event in enumerate(events)
    )
    body = (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<ol class="timeline" role="list">\n{items}\n</ol>'
    )
    return body, ''
