"""The five theme colors, the tokens they become, and the icon they paint."""
import re
from urllib.parse import quote

from . import ROOT
from .text import field, url

THEME_KEYS = ('paper', 'ink', 'accent', 'secondary', 'wash')
# The themes the kit ships with. The guide shows all four as swatches a reader
# can try on the page before copying one into their own JSON file. Every mixed
# pair of each of them holds 4.5:1 for text on its own paper.
PRESETS = (
    ('warm', {'paper': '#f6f3eb', 'ink': '#292925', 'accent': '#a33e36',
              'secondary': '#466958', 'wash': '#e7e4d9'}),
    ('cool', {'paper': '#f1f4f3', 'ink': '#1b2828', 'accent': '#315d73',
              'secondary': '#51694b', 'wash': '#dce5e2'}),
    ('night', {'paper': '#1f2023', 'ink': '#ece9e1', 'accent': '#d98b7c',
               'secondary': '#8fb3a0', 'wash': '#2a2b2f'}),
    ('clay', {'paper': '#f7f4ef', 'ink': '#292831', 'accent': '#9b5324',
              'secondary': '#3f5f8a', 'wash': '#ebe6dd'}),
)
# favicon.svg is the kit's only icon and its drawing. It is authored in the
# default palette; a build paints the report's own theme into it, so one file
# serves any theme. The default export carries the painted icon in a data URI,
# so the page opens from disk. ICON_SAFE is left unencoded to keep the URI
# readable; none of those characters can end the attribute or the data.
ICON_SAFE = ":/;=,"
ICON_PAPER = '#f6f3eb'
ICON_INK = '#292925'
ICON_ACCENT = '#a33e36'
# The accent alone holds 2.29:1 on the ink tile, so the dark scheme lifts it
# with paper. The mix is the stylesheet's own: accent 60 percent in oklab.
ICON_DARK_STROKE = '#c9877c'
ICON_DARK_MIX = 60
# The rule that lifts the icon on a page whose own paper is light. A dark paper
# already holds a dark tile, so the block is dropped rather than painted, which
# would put a light tile on a dark page.
ICON_DARK_RULE = re.compile(
    r'@media\(prefers-color-scheme:dark\)\{(?:[^{}]*\{[^{}]*\})*\}\n?'
)
# Below this relative luminance the paper is a dark paper, so the page asks the
# browser for dark scrollbars and dark form chrome. 0.18 is the middle gray of
# the sRGB range: every paper in the kit's own themes sits far from it, and a
# paper that sits on it reads either way.
DARK_PAPER = .18


def relative_luminance(color):
    """The WCAG relative luminance of one opaque hex color, 0 for black and 1
    for white. It is what tells the build whether the paper is a dark paper."""
    channels = []
    value = color.lstrip('#')
    for i in (0, 2, 4):
        part = int(value[i:i + 2], 16) / 255
        channels.append(part / 12.92 if part <= .04045
                        else ((part + .055) / 1.055) ** 2.4)
    red, green, blue = channels
    return .2126 * red + .7152 * green + .0722 * blue


def color_scheme(paper):
    """What the page tells the browser its own colors are. A reader whose
    system is set to dark gets scrollbars and form chrome painted for the
    report's paper rather than for a theme the page does not have, and a report
    on a dark paper gets dark chrome even when the system is light."""
    return 'dark' if relative_luminance(paper) < DARK_PAPER else 'light'


def mix_oklab(top, bottom, share):
    """color-mix(in oklab, top share%, bottom) for two opaque hex colors.
    report.css mixes every derived color this way; the icon is a file rather
    than a stylesheet, so its one derived color is mixed here instead."""
    def channels(value):
        value = value.lstrip('#')
        return [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def to_linear(c):
        return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4

    def to_srgb(c):
        c = 12.92 * c if c <= .0031308 else 1.055 * (c ** (1 / 2.4)) - .055
        return min(255, max(0, round(c * 255)))

    def to_oklab(rgb):
        r, g, b = rgb
        long_ = (.4122214708 * r + .5363325363 * g + .0514459929 * b) ** (1 / 3)
        medium = (.2119034982 * r + .6806995451 * g + .1073969566 * b) ** (1 / 3)
        short = (.0883024619 * r + .2817188376 * g + .6299787005 * b) ** (1 / 3)
        return (
            .2104542553 * long_ + .7936177850 * medium - .0040720468 * short,
            1.9779984951 * long_ - 2.4285922050 * medium + .4505937099 * short,
            .0259040371 * long_ + .7827717662 * medium - .8086757660 * short,
        )

    def to_rgb(lab):
        lightness, green_red, blue_yellow = lab
        long_ = (lightness + .3963377774 * green_red + .2158037573 * blue_yellow) ** 3
        medium = (lightness - .1055613458 * green_red - .0638541728 * blue_yellow) ** 3
        short = (lightness - .0894841775 * green_red - 1.2914855480 * blue_yellow) ** 3
        return (
            4.0767416621 * long_ - 3.3077115913 * medium + .2309699292 * short,
            -1.2684380046 * long_ + 2.6097574011 * medium - .3413193965 * short,
            -.0041960863 * long_ - .7034186147 * medium + 1.7076147010 * short,
        )

    weight = share / 100
    first = to_oklab([to_linear(c) for c in channels(top)])
    second = to_oklab([to_linear(c) for c in channels(bottom)])
    mixed = [a * weight + b * (1 - weight) for a, b in zip(first, second)]
    return '#%02x%02x%02x' % tuple(to_srgb(c) for c in to_rgb(mixed))


def theme_tokens(data):
    """The five colors, checked, and the :root block that carries them into
    the stylesheet. The report and the guide both start here."""
    theme = field(data, 'theme')
    tokens = []
    for key in THEME_KEYS:
        value = field(theme, key, 'theme.')
        if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            raise ValueError(f'theme.{key} must be a six-digit hex color: {value!r}')
        tokens.append(f'--{key}:{value}')
    # The scheme rides with the colors it is read from, so one block states the
    # paper and what the browser should paint around it.
    tokens.append(f'color-scheme:{color_scheme(theme["paper"])}')
    return theme, ';'.join(tokens)


def theme_icon(theme):
    """favicon.svg painted in the report's own colors. A build with no
    favicon.svg beside it would silently ship a page with no icon, so it stops
    instead, and so does a build whose icon no longer carries the colors this
    function knows how to swap."""
    icon = ROOT / 'favicon.svg'
    if not icon.is_file():
        raise ValueError(f'favicon.svg is missing from {ROOT}; the icon has no source')
    source = icon.read_text(encoding='utf-8')
    swaps = {
        ICON_PAPER: theme['paper'],
        ICON_INK: theme['ink'],
        ICON_ACCENT: theme['accent'],
        ICON_DARK_STROKE: mix_oklab(theme['accent'], theme['paper'], ICON_DARK_MIX),
    }
    if not ICON_DARK_RULE.search(source):
        raise ValueError(
            'favicon.svg no longer carries its prefers-color-scheme rule, so '
            'build.py cannot tell a dark page not to paint a light tile'
        )
    for default in swaps:
        if default not in source:
            raise ValueError(
                f'favicon.svg no longer carries {default}, so build.py cannot paint '
                f'the theme into it'
            )
    # The tile is already the theme's paper. On a dark paper the dark-scheme
    # rule would paint the theme's ink over it, which is the light color, so
    # the rule goes and the icon keeps the one tile the page is drawn on.
    if color_scheme(theme['paper']) == 'dark':
        source = ICON_DARK_RULE.sub('', source)
    # One pass, so a theme color that matches another default is not swapped twice.
    return re.sub(
        r'#[0-9a-fA-F]{6}',
        lambda match: swaps.get(match.group(0).lower(), match.group(0)),
        source,
    )


def favicon_link(assets_url, theme):
    """The one icon, from the one file. The hosted export links the copy that
    ships beside report.css, but only while the theme is the one that file is
    drawn in: a shared icon cannot be five palettes, so a themed report carries
    its own in the page."""
    painted = theme_icon(theme)
    if assets_url and painted == (ROOT / 'favicon.svg').read_text(encoding='utf-8'):
        return (
            '<link rel="icon" type="image/svg+xml" '
            f'href="{url(assets_url.rstrip("/") + "/favicon.svg")}">'
        )
    data = quote(painted, safe=ICON_SAFE)
    return f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{data}">'
