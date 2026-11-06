"""The type presets: which faces a report sets in, and the tokens they become.

A report names one preset in its `fonts` block. The preset resolves to a set of
`@font-face` rules and to the font tokens the stylesheet reads. The default
export embeds each face as a base64 data URI, so a page opened from a disk with
no network sets in the face the author chose. Hosted-asset mode links the same
files from the host instead.

The files under fonts/ are latin subsets from Google Fonts, one variable file to
a family, each with its OFL licence text beside it. A character outside the
latin subset falls back to the next family in the stack, so a report in a
language the subset does not cover still reads.
"""
import base64
import re

from . import ROOT
from .text import check_text, field, url

FONTS = ROOT / 'fonts'
# The system stacks. They are the `system` preset, and they are the tail of
# every other preset: a glyph the embedded subset does not carry is drawn by
# the first family after it that does.
SERIF = ("'Iowan Old Style','Palatino Linotype','Book Antiqua',Palatino,"
         "Charter,Georgia,'Times New Roman',serif")
SANS = ("ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,"
        "'Helvetica Neue',Arial,sans-serif")
# One entry for each face file a preset can ask for. `weight` and `stretch` are
# the descriptors that match the file Google Fonts served, so the browser picks
# the instance the token asks for instead of synthesizing one.
FACES = {
    'Figtree': {'file': 'figtree.woff2', 'weight': '300 900',
                'stack': SANS, 'licence': 'figtree-OFL.txt'},
    'Nunito Sans': {'file': 'nunito-sans.woff2', 'weight': '200 1000',
                    'stretch': '100%', 'stack': SANS,
                    'licence': 'nunito-sans-OFL.txt'},
    'Fraunces': {'file': 'fraunces.woff2', 'weight': '100 900',
                 'stack': SERIF, 'licence': 'fraunces-OFL.txt'},
    'Recursive': {'file': 'recursive.woff2', 'weight': '300 1000',
                  'stack': SANS, 'licence': 'recursive-OFL.txt'},
    'Bricolage Grotesque': {'file': 'bricolage-grotesque.woff2',
                            'weight': '200 800', 'stretch': '100%',
                            'stack': SANS,
                            'licence': 'bricolage-grotesque-OFL.txt'},
}
# The presets, in the order the guide shows them. Each one names the family of
# the body, the display and the label, the weight the display takes, and the
# variable-axis settings the body and the display set. Every preset carries a
# display weight of 800 or more, which is what makes the cover and the large
# numerals read as display rather than as heavy body copy.
#
# `note` is the sentence the guide prints beside the specimen. `faces` is
# derived, not written: it is every family the three roles name.
PRESETS = (
    ('system', {
        'body': None, 'display': None, 'label': None,
        'body_stack': SERIF, 'display_stack': SERIF, 'label_stack': SANS,
        'w_display': '800', 'vs_body': 'normal', 'vs_display': 'normal',
        'note': ('The reader\'s own faces, and no file to download. The '
                 'display weight is 800, which the stack draws where the '
                 'face has it.'),
    }),
    ('field', {
        'body': 'Figtree', 'display': 'Bricolage Grotesque', 'label': 'Figtree',
        'w_display': '800', 'vs_body': 'normal', 'vs_display': 'normal',
        'note': ('Figtree gets out of the way of the drawing; Bricolage '
                 'Grotesque at 800 carries the cover and the numerals.'),
    }),
    ('quill', {
        'body': 'Nunito Sans', 'display': 'Fraunces', 'label': 'Nunito Sans',
        'w_display': '900', 'vs_body': 'normal',
        'vs_display': '"SOFT" 100,"WONK" 1',
        'note': ('Fraunces at 900, soft and wonky, echoes the hand-drawn '
                 'marks; Nunito Sans keeps the body warm.'),
    }),
    ('ink', {
        'body': 'Recursive', 'display': 'Recursive', 'label': 'Recursive',
        'w_display': '1000', 'vs_body': '"CASL" 0,"MONO" 0',
        'vs_display': '"CASL" 1,"MONO" 0',
        'note': ('One variable file for the whole page: casual at 1000 for '
                 'display, linear at 400 for the body.'),
    }),
)
NAMES = tuple(name for name, _ in PRESETS)
BY_NAME = dict(PRESETS)
DEFAULT = 'system'
# The figures every numeral takes: one width to a digit, and no old-style
# descenders under a heading.
NUMERALS = 'lining-nums tabular-nums'
# A family name reaches a font-family token and a @font-face rule, so it holds
# letters, digits and single spaces and nothing that could end either one.
NAME_SHAPE = re.compile(r'[A-Za-z0-9]+( [A-Za-z0-9]+)*')


def preset(data, where=''):
    """The preset one report asks for, checked. A report with no `fonts` block
    gets the system stacks, which is what the kit shipped before the presets
    and what a report that names no faces still reads in."""
    block = data.get('fonts')
    if block is None:
        return DEFAULT, BY_NAME[DEFAULT]
    if not isinstance(block, dict):
        raise ValueError(
            f'{where}fonts must be an object that names a preset, such as '
            f'{{"preset": "field"}}'
        )
    name = check_text(field(block, 'preset', f'{where}fonts.'), 'preset',
                      f'{where}fonts.')
    extra = sorted(key for key in block if key != 'preset')
    if extra:
        raise ValueError(
            f'{where}fonts reads one field, preset, and this block also holds '
            f'{", ".join(extra)}'
        )
    if name not in BY_NAME:
        raise ValueError(
            f'{where}fonts.preset must be one of {", ".join(NAMES)}, not '
            f'{name!r}'
        )
    return name, BY_NAME[name]


def stack(spec, role):
    """The font-family value for one role: the embedded family first, then the
    system families that draw whatever the subset does not carry."""
    family = spec[role]
    if family is None:
        return spec[f'{role}_stack']
    if not NAME_SHAPE.fullmatch(family):
        raise ValueError(
            f'{family!r} is not a family name the kit can write into a '
            f'font-family token'
        )
    return f"'{family}',{FACES[family]['stack']}"


def families(spec):
    """Every family the preset embeds, once each, in the order the roles name
    them. The system preset names none, so it embeds nothing."""
    wanted = []
    for role in ('body', 'display', 'label'):
        family = spec[role]
        if family is not None and family not in wanted:
            wanted.append(family)
    return wanted


def tokens(spec):
    """The font tokens of one preset, as one `:root` declaration list. The
    stylesheet aliases --font-serif and --font-sans onto these, so a rule that
    named a family before the presets names one of these now."""
    return ';'.join((
        f'--font-body:{stack(spec, "body")}',
        f'--font-display:{stack(spec, "display")}',
        f'--font-label:{stack(spec, "label")}',
        f'--w-display:{spec["w_display"]}',
        f'--vs-body:{spec["vs_body"]}',
        f'--vs-display:{spec["vs_display"]}',
        f'--num-display:{NUMERALS}',
    ))


def face_file(family):
    """One woff2 file from fonts/, as bytes. A preset that names a family the
    folder has no file for cannot embed it, so the build stops and names the
    file rather than shipping a page that asks the reader's browser for a face
    it never had."""
    path = FONTS / FACES[family]['file']
    if not path.is_file():
        raise ValueError(
            f'{path} is missing, so the font preset cannot embed '
            f'{family}. The kit ships the file in fonts/.'
        )
    return path.read_bytes()


def face_rule(family, source):
    """One @font-face rule. `source` is the value of src, which is a data URI
    in the default export and a hosted address in the hosted one."""
    face = FACES[family]
    stretch = f'font-stretch:{face["stretch"]};' if 'stretch' in face else ''
    return (
        f"@font-face{{font-family:'{family}';"
        f'src:{source} format("woff2");'
        f'font-weight:{face["weight"]};'
        f'{stretch}'
        'font-style:normal;font-display:swap}'
    )


def embedded(family):
    """The face as a data URI, so the page carries the file and asks for
    nothing."""
    data = base64.b64encode(face_file(family)).decode('ascii')
    return f'url("data:font/woff2;base64,{data}")'


def hosted(family, assets_url):
    """The face as an address under the asset base, which is where package.py
    ships fonts/."""
    address = assets_url.rstrip('/') + '/fonts/' + FACES[family]['file']
    return f'url("{url(address)}")'


def faces(spec, assets_url=None):
    """Every @font-face rule the preset needs, as one string."""
    return ''.join(
        face_rule(family, hosted(family, assets_url) if assets_url
                  else embedded(family))
        for family in families(spec)
    )


def style_block(spec, assets_url=None):
    """The one element that carries the preset into the page: the faces and the
    tokens that name them. It sits after the stylesheet, so the tokens it sets
    replace the system stacks the stylesheet declares. The system preset writes
    nothing, so a report that names no faces carries no font bytes and makes no
    request."""
    if not families(spec):
        return ''
    return f'<style>{faces(spec, assets_url)}:root{{{tokens(spec)}}}</style>'


def linked_block(base=''):
    """Every family the kit ships, linked from fonts/ beside the page. The
    guide uses it: it shows all four presets on one page, so embedding four
    presets' files would carry the same bytes the folder already holds beside
    it. A report never uses this, because a report is one file a reader can
    move on its own."""
    rules = ''.join(
        face_rule(family, f'url("{base}fonts/{FACES[family]["file"]}")')
        for family in FACES
    )
    return f'<style>{rules}</style>'
