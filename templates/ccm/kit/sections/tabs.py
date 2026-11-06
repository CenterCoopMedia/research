"""Two to five parallel views of one subject, one shown at a time.

The markup ships with every panel open and the tab list hidden. 50-tabs.js
shows the list, hides the panels it is not on, and hides the heading each panel
opens with, because the tab label states the same thing. A reader with no
script keeps the stacked panels and their headings, so nothing is behind a
control that cannot work.
"""
from .. import inline
from ..text import esc, field, paragraphs, text

NAME = 'tabs'
# The separator between the id of the section and the name of the id this
# module builds from it. page.py refuses a section id that holds it, so a tab
# id and a panel id can never take the name of a section.
SPLIT = '--'
TITLE_REQUIRED = True
ORDER = 50
FIELDS = ('<code>label</code>, <code>title</code>, <code>panels</code>: each has'
          ' <code>label</code> and <code>paragraphs</code>')
LOW, HIGH = 2, 5
SPECIMEN = {
    'summary': 'Two to five panels of prose under a row of text tabs.',
    'use_when': 'Use it when a reader compares parallel views instead of reading them in order.',
    'json': {
        'type': 'tabs',
        'id': 'tabs-specimen',
        'label': 'Example views',
        'title': 'One question, three answers.',
        'panels': [
            {
                'label': 'Reporters',
                'paragraphs': [
                    'An invented view for the template. State what this group gains and what it gives up.',
                    'Keep each panel about the same length, so no view reads as the important one.',
                ],
            },
            {
                'label': 'Editors',
                'paragraphs': [
                    'An invented view for the template. Replace it with the second position and its evidence.',
                ],
            },
            {
                'label': 'Readers',
                'paragraphs': [
                    'An invented view for the template. Replace it with the third position and its evidence.',
                ],
            },
        ],
    },
}


def render_tab(sid, index, label, selected):
    """One control in the tab list. The selected tab is the group's one stop in
    the page tab order; the arrow keys reach the rest."""
    return (
        f'<button type="button" role="tab" class="tab" id="{sid}{SPLIT}tab-{index}"'
        f' aria-controls="{sid}{SPLIT}panel-{index}"'
        f' aria-selected="{"true" if selected else "false"}"'
        f' tabindex="{0 if selected else -1}">{esc(label)}</button>'
    )


def render_panel(sid, index, label, body):
    """One panel. It is in the tab order itself, because a panel of prose holds
    nothing else a keyboard can reach."""
    return (
        f'<div class="tab-panel" role="tabpanel" id="{sid}{SPLIT}panel-{index}"'
        f' aria-labelledby="{sid}{SPLIT}tab-{index}" tabindex="0">\n'
        f'<h3 class="tab-heading">{esc(label)}</h3>\n{body}\n</div>'
    )


def render(section, heading_html, where, context):
    """The tab list, then every panel, both keyed to the section id and the
    reserved separator, so two tabs sections on one page never share an id and
    no author's section id can take the name of one."""
    panels = field(section, 'panels', where)
    if not isinstance(panels, list) or not LOW <= len(panels) <= HIGH:
        raise ValueError(
            f'{where}panels must be a list of {LOW} to {HIGH} panels, not '
            f'{len(panels) if isinstance(panels, list) else type(panels).__name__}'
        )
    sid = section['id']
    markup = inline.for_section(section, where, term=context.term)
    tabs, bodies = [], []
    for index, panel in enumerate(panels, 1):
        spot = f'{where[:-2]} panel {index}: '
        if not isinstance(panel, dict):
            raise ValueError(f'{spot}a panel holds a label and paragraphs')
        label = text(panel, 'label', spot)
        body = paragraphs(field(panel, 'paragraphs', spot), spot,
                          lambda value, at=spot: markup(value, at))
        tabs.append(render_tab(sid, index, label, index == 1))
        bodies.append(render_panel(sid, index, label, body))
    body = (
        f'<div class="section-heading">{heading_html}\n</div>\n'
        f'<div class="tabs reading">\n'
        f'<div class="tablist" role="tablist" aria-label="{esc(text(section, "title", where))}">\n'
        + '\n'.join(tabs)
        + '\n</div>\n'
        + '\n'.join(bodies)
        + '\n</div>'
    )
    return body, ''
