"""A pinned drawing with a column of cards. Each card names one state."""
from .. import inline
from ..art import LAYOUTS, artwork, resolve_highlight
from ..text import esc, field, optional_text, text

NAME = 'scrolly'
TITLE_REQUIRED = True
ORDER = 20
FIELDS = ('<code>label</code>, <code>title</code>, optional <code>center_label</code>,'
          ' <code>steps</code>')
SPECIMEN = {
    'summary': 'A drawing that holds its place while short cards change it.',
    'use_when': 'Use it when one picture carries the whole argument and each step changes it.',
    'json': {
        'type': 'scrolly',
        'id': 'scrolly-specimen',
        'label': 'Follow the connections',
        'title': 'From one newsroom to a shared network.',
        'steps': [
            {
                'title': 'Start with the people doing the work.',
                'text': 'Each mark stands for one imagined newsroom. At first, the marks sit apart.',
                'caption': '12 imagined newsrooms, working independently',
                'layout': 'scatter',
                'highlight': 0,
            },
            {
                'title': 'Keep the community at the center.',
                'text': 'The shared work matters when people can find and use it.',
                'caption': 'Shared work returns to a common public purpose',
                'layout': 'orbit',
                'highlight': 0,
            },
        ],
    },
}


def render_step(step, index, total, where, markup):
    """One card + data attributes for a single scrolly step."""
    layout = text(step, 'layout', where)
    if layout not in LAYOUTS:
        raise ValueError(
            f'{where}layout must be one of {", ".join(LAYOUTS)}: {layout!r}'
        )
    highlight = ' '.join(str(i) for i in resolve_highlight(field(step, 'highlight', where), where))
    caption = esc(text(step, 'caption', where))
    # The card states its place in words. A padded numeral is a habit, not a
    # sort order: this list can never pass nine.
    eyebrow = f'<span class="eyebrow">{index} of {total}</span>'
    return (
        f'<article class="step" data-layout="{layout}" data-highlight="{highlight}" data-caption="{caption}">\n'
        f'<div class="step-card">{eyebrow}<h3>{esc(text(step, "title", where))}</h3>\n'
        f'<p>{markup(text(step, "text", where), where)}</p>\n'
        f'<p class="static-caption">{caption}</p>\n'
        f'</div>\n'
        f'</article>'
    )


def render(section, heading_html, where, context):
    """The card carries the reading text. The caption repeats it for sighted
    readers only, so it is hidden from assistive technology."""
    place = where[:-2]
    sid = section['id']
    steps_data = field(section, 'steps', where)
    if not isinstance(steps_data, list) or not steps_data:
        raise ValueError(f'{where}steps must be a list holding at least one step')
    total = len(steps_data)
    markup = inline.for_section(section, where, term=context.term)
    steps_html = '\n'.join(
        render_step(step, i + 1, total, f'{place} step {i + 1}: ', markup)
        for i, step in enumerate(steps_data)
    )
    art = artwork(sid, context.theme, optional_text(section, 'center_label', where) or 'Community')
    first_caption = esc(text(steps_data[0], 'caption', f'{place} step 1: '))
    body = (
        f'<div class="section-heading">{heading_html}\n'
        f'</div>\n'
        f'<div class="scrolly">\n'
        f'<figure class="stage">\n'
        f'{art}\n'
        f'<figcaption aria-hidden="true">{first_caption}</figcaption>\n'
        f'<div class="stage-progress" aria-hidden="true"><i></i></div>\n'
        f'</figure>\n'
        f'<div class="print-figure" aria-hidden="true"></div>\n'
        f'<div class="steps">\n'
        f'{steps_html}\n'
        f'</div>\n'
        f'</div>'
    )
    return body, ''
