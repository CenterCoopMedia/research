"""The kit's front door, filled from guide.template.html."""
import copy
import json
import re
from urllib.parse import urljoin

from . import ROOT, endmatter, fonts
from .art import LAYOUTS, MARKS, artwork, mark_specimen
from .page import render_sections
from .registry import REGISTRY
from .text import esc, field, text, url
from .theme import PRESETS, THEME_KEYS, color_scheme, favicon_link, theme_tokens

# Three marks with different stroke counts, drawn by the report's own
# function.
GUIDE_MARKS = (0, 3, 6)
# A count in a sentence is a word up to twenty and digits above it, which is
# the rule the report's own prose follows.
COUNT_WORDS = ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
               'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
               'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
               'nineteen', 'twenty')
# The three lines a type specimen shows: the cover line, a line of prose, and
# the three numerals of the sample's own findings row. One preset changes only
# the faces, so the words hold still and the reader compares the type.
TYPE_EYEBROW = 'Example cover'
TYPE_TITLE = 'A story is only the beginning.'
TYPE_PROSE = ('A reporter asks a question. A resident shares what they know. '
              'An editor connects the account to a wider story.')
TYPE_NUMERALS = ('12', '3', '1')
# The two sections a layout specimen renders. They are JSON, not markup: the
# kit's own renderer builds them, so a specimen cannot show a layout the kit
# does not produce. The prose section carries a note and a pull quote, which are
# the two blocks the rail takes from a run of paragraphs; the figure comes from
# the figure type's own specimen, so it is the block the reader already knows.
LAYOUT_PROSE = {
    'type': 'prose',
    'id': 'prose',
    'label': 'The rail',
    'title': 'A note and a lifted sentence stand beside the column.',
    'paragraphs': [
        'A reporter asks a question. A resident shares what they know. An '
        'editor connects the account to a wider story. Each exchange gives '
        'information a place to go.[^1]',
        {'pullquote': 'Each exchange gives information a place to go.'},
        'The column holds 34em in both layouts, so no line runs past 66 '
        'characters. What changes is where the column sits and what stands '
        'beside it.',
    ],
    'notes': [
        'An invented example. The wide layout puts this note in the rail. '
        'Every narrower window puts it at the foot of the section.',
    ],
}
# What each layout is for, shown beside its specimen.
LAYOUT_NOTES = (
    ('reading', 'The centered column the kit shipped with. A note goes to the '
                'margin beside it where the window is wide enough, and to the '
                'foot of the section where it is not.'),
    ('wide', 'The same column against the left gutter, with the rail beside '
             'it. The figure keeps the full figure width and breaks past the '
             'column on purpose.'),
)
# What each theme color is for, shown beside its swatch on the guide.
PALETTE_ROLES = (
    ('paper', 'Page and card background'),
    ('ink', 'Text, marks, primary button'),
    ('accent', 'Highlights, numerals, focus ring'),
    ('secondary', 'Connection lines and cover caption'),
    ('wash', 'Dividers, code, methods band'),
)


def counted(value):
    """A count as a sentence writes it."""
    return COUNT_WORDS[value] if value < len(COUNT_WORDS) else str(value)


def palette_row(key, role, theme):
    return (
        f'<li><span class="swatch" style="background:var(--{key})"></span>'
        f'<span class="swatch-name">{key} <code>{esc(theme[key])}</code></span>'
        f'<span class="swatch-role">{esc(role)}</span></li>'
    )


def preset_button(name, colors, showing):
    """One theme, as a button a reader can press. The five colors are five
    stripes inside it, so the swatch is the theme rather than a word for it,
    and the name says which theme it is. The button is the kit's own control;
    the one that is showing takes the marker rule an open tab takes."""
    stripes = ''.join(
        f'<span class="preset-stripe" style="background:{colors[key]}"></span>'
        for key in THEME_KEYS
    )
    data = ''.join(f' data-{key}="{colors[key]}"' for key in THEME_KEYS)
    pressed = 'true' if colors == showing else 'false'
    return (
        f'<button type="button" class="control theme-preset" aria-pressed="{pressed}"'
        f'{data} data-scheme="{color_scheme(colors["paper"])}">'
        f'<span class="preset-stripes" aria-hidden="true">{stripes}</span>'
        f'<span class="preset-name">{esc(name)}</span></button>'
    )


def presets(theme):
    """Every theme the kit ships, in the order the brief names them."""
    return '\n'.join(preset_button(name, colors, theme)
                     for name, colors in PRESETS)


def type_specimen(name, spec):
    """One preset: the name, what it is for, the line of JSON that selects it,
    and the three places type carries a report. The preset's tokens ride on the
    style attribute of the block that shows them, so the four specimens set in
    four presets on one page."""
    snippet = json.dumps({'fonts': {'preset': name}}, indent=2)
    numerals = ''.join(f'<span class="finding-value">{value}</span>'
                       for value in TYPE_NUMERALS)
    return (
        f'<article class="type-block" id="type-{name}">\n'
        f'<h3><code>{name}</code></h3>\n'
        f'<p class="use-when">{esc(spec["note"])}</p>\n'
        f'<pre>{esc(snippet)}</pre>\n'
        f'<div class="type-render" style="{esc(fonts.tokens(spec))}">\n'
        f'<span class="eyebrow">{esc(TYPE_EYEBROW)}</span>\n'
        f'<p class="type-title">{esc(TYPE_TITLE)}</p>\n'
        f'<p>{esc(TYPE_PROSE)}</p>\n'
        f'<p class="type-numerals">{numerals}</p>\n'
        f'</div>\n'
        f'</article>'
    )


def type_specimens():
    """Every preset the kit ships, in the order kit/fonts.py names them, so a
    new preset is one entry there and no edit here."""
    return '\n'.join(type_specimen(name, spec) for name, spec in fonts.PRESETS)


def layout_sections(layout, theme):
    """The two sections of one layout specimen, built by the report's own
    renderer. Each id carries the layout's name, because both specimens stand on
    one page and an id belongs to one element."""
    sections = [copy.deepcopy(LAYOUT_PROSE),
                copy.deepcopy(REGISTRY['figure'].SPECIMEN['json'])]
    for section in sections:
        section['id'] = f'{layout}-{section["id"].split("-")[0]}'
    return '\n'.join(render_sections({'sections': sections}, theme)[0])


def layout_specimen(layout, note, theme):
    """One layout: the name, what it is for, the line of JSON that selects it,
    and the two sections rendered inside a page of their own. The name goes on
    the wrapper rather than on <body>, so both layouts show on one page."""
    snippet = json.dumps({'layout': layout}, indent=2)
    return (
        f'<article class="layout-block" id="layout-{layout}">\n'
        f'<h3><code>{layout}</code></h3>\n'
        f'<p class="use-when">{esc(note)}</p>\n'
        f'<pre>{esc(snippet)}</pre>\n'
        f'<div class="layout-render" data-layout="{layout}">\n'
        f'{layout_sections(layout, theme)}\n'
        f'</div>\n'
        f'</article>'
    )


def layout_specimens(theme):
    """Both layouts, in the order kit/page.py names them."""
    return '\n'.join(layout_specimen(layout, note, theme)
                     for layout, note in LAYOUT_NOTES)


def section_table():
    """The row for each section type, from the modules themselves, so a type
    that ships is a type the guide names."""
    return '\n'.join(
        f'<tr><td>{module.NAME}</td><td>{module.FIELDS}</td></tr>'
        for module in REGISTRY.values()
    )


def specimen_block(name, source, rendered):
    """One specimen, shown three ways: what it does, the JSON it is built from,
    and what that JSON makes. A section type and an end-matter block are shown
    with the same markup, so the guide reads as one list. The anchor is on the
    block, not on its heading, so a link from the index lands above the name
    rather than beside it."""
    written = esc(json.dumps(source['json'], indent=2, ensure_ascii=False))
    return (
        f'<article class="specimen-block" id="specimen-{name}">\n'
        f'<h3><code>{name}</code></h3>\n'
        f'<p>{esc(source["summary"])}</p>\n'
        f'<p class="use-when">{esc(source["use_when"])}</p>\n'
        f'<pre>{written}</pre>\n'
        f'<div class="specimen-render">\n{rendered}\n</div>\n'
        f'</article>'
    )


def static_scrolly_specimen(html):
    """The scrolly specimen, shown as the states it holds rather than as the
    live pinned mechanic that shows them one at a time. The mechanic needs
    real scroll room to read, four screens of it for two steps, which is a
    long stretch of blank paper among the guide's 26 specimens; the sample
    report and every real report keep it, because there the room is earned by
    the argument around it.

    report.js already builds one static copy of the stage per step for print,
    into the section's own `.print-figure`, with the same clone-and-lay-out
    function the live stage uses. The guide reuses that path rather than
    building a second one: it shows the print copies on screen instead of
    only on paper, and hides the pinned stage and the step column that would
    otherwise sit behind them. `.print-figure` renders `aria-hidden` because
    paper carries no assistive technology; on the guide it is the only copy
    of the drawing a reader sees, so that guide-only copy keeps its captions
    in the accessibility tree."""
    html = html.replace(
        '<div class="print-figure" aria-hidden="true"></div>',
        '<div class="print-figure"></div>',
    )
    note = (
        '<p class="specimen-note">The live version pins the drawing while '
        'the reader scrolls past each step: see it in the '
        '<a href="index.html#connections">sample report</a>.</p>\n'
    )
    return html.replace('</section>', f'{note}</section>')


def specimen_names():
    """Every specimen on the page, in the order the page shows them."""
    return [module.NAME for module in REGISTRY.values()] + [
        source['name'] for source in endmatter.SPECIMENS
    ]


def specimen_index():
    """A jump list, so a reader looking for one component does not scroll past
    every other one to reach it."""
    rows = '\n'.join(
        f'<li><a href="#specimen-{name}"><code>{name}</code></a></li>'
        for name in specimen_names()
    )
    return f'<ul class="specimen-index">\n{rows}\n</ul>'


def specimen_sections(theme):
    """Every section specimen, rendered in one pass as one report and keyed by
    the name of its type.

    The set renders together so that it shares one context, which means the
    glossary any one specimen reads is the glossary of the whole page. A
    specimen rendered on its own carries no glossary, so no specimen but the
    glossary's own could hold a `{term}`, and the guide could not show a
    reader the form they write one in."""
    modules = list(REGISTRY.values())
    sections = render_sections(
        {'sections': [module.SPECIMEN['json'] for module in modules]}, theme)[0]
    return dict(zip((module.NAME for module in modules), sections))


def specimens(theme):
    """Every section type, then every end-matter block. An end-matter block
    reads top-level fields rather than a section, so endmatter.py renders it and
    hands the guide the markup in the specimen's `html`."""
    rendered = dict(specimen_sections(theme))
    rendered['scrolly'] = static_scrolly_specimen(rendered['scrolly'])
    blocks = [specimen_block(module.NAME, module.SPECIMEN, rendered[module.NAME])
              for module in REGISTRY.values()]
    blocks += [specimen_block(source['name'], source, source['html'])
               for source in endmatter.SPECIMENS]
    return '\n'.join(blocks)


def render_guide(data):
    """Everything a visitor sees that the generator can make is made here, by
    the same theme, the same artwork and the same marks the report uses, so the
    guide cannot show a palette or a drawing the kit no longer produces."""
    theme, root_vars = theme_tokens(data)
    # The guide sets in the preset the kit's own sample names, and it links
    # every family the kit ships so the four type specimens each show their own
    # faces. It links rather than embeds because fonts/ sits beside this page
    # and beside it in the download, so embedding four presets would carry the
    # same bytes twice.
    preset = fonts.preset(data)[1]
    canonical = data.get('template_url') or urljoin(text(data, 'url'), 'guide.html')
    # The guide ships inside the ZIP and the ZIP does not carry the examples, so
    # the header link to them is the hosted address, the way the "In the wild"
    # links are.
    examples = urljoin(text(data, 'url'), 'examples/')
    values = {
        'theme_block': f'<style>:root{{{root_vars}}}</style>',
        'font_block': (f'{fonts.linked_block()}'
                       f'<style>:root{{{fonts.tokens(preset)}}}</style>'),
        'type_specimens': type_specimens(),
        'layout_specimens': layout_specimens(theme),
        'theme_color': esc(theme['paper']),
        'icon': favicon_link(None, theme),
        'hero_art': artwork('hero', theme),
        'hero_caption': esc(text(data, 'hero_caption')),
        'mark_specimens': '\n'.join(mark_specimen(i, theme) for i in GUIDE_MARKS),
        'palette': '\n'.join(palette_row(key, role, theme) for key, role in PALETTE_ROLES),
        'presets': presets(theme),
        'organization': esc(text(data, 'organization')),
        'date': esc(text(data, 'date')),
        'guide_url': url(canonical, 'template_url'),
        'examples_url': url(examples, 'url'),
        'image_url': url(field(data, 'image_url'), 'image_url'),
        'mark_count': str(MARKS),
        # The heading names how many types the kit ships, so a new module in
        # kit/sections changes the number with no edit to the template.
        'section_count': counted(len(REGISTRY)).capitalize(),
        'section_table': section_table(),
        'specimen_index': specimen_index(),
        'specimen_count': str(len(specimen_names())),
        'section_type_count': str(len(REGISTRY)),
        'endmatter_count': counted(len(endmatter.SPECIMENS)),
        'specimens': specimens(theme),
        'layouts': ', '.join(f'<code>{name}</code>' for name in LAYOUTS[:-1])
                   + f', or <code>{LAYOUTS[-1]}</code>',
    }
    template = (ROOT / 'guide.template.html').read_text(encoding='utf-8')
    wanted = set(re.findall(r'\{\{(\w+)\}\}', template))
    missing = wanted - set(values)
    unused = set(values) - wanted
    if missing or unused:
        raise ValueError(
            f'guide.template.html and render_guide disagree. '
            f'The template asks for {sorted(missing)} and does not use {sorted(unused)}'
        )
    return re.sub(r'\{\{(\w+)\}\}', lambda match: values[match.group(1)], template)
