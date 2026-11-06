"""One picture on the page, with its caption and its credit.

This module also holds the checks the other media types share: the source
address, the alt text, a boolean field, a named choice, and the placeholder
picture a specimen draws for itself.
"""
from urllib.parse import quote, urlsplit

from .. import inline
from ..text import esc, optional_text, text

NAME = 'image'
TITLE_REQUIRED = False
ORDER = 61
FIELDS = ('<code>src</code>, <code>alt</code>, optional <code>caption</code>,'
          ' <code>credit</code>, <code>decorative</code>, <code>lightbox</code>,'
          ' and <code>width</code> of <code>reading</code>, <code>figure</code>'
          ' or <code>bleed</code>')
WIDTHS = ('reading', 'figure', 'bleed')
# The kit ships text files only, so a specimen has no picture file to point
# at and draws one instead. A data: URI cannot read a CSS variable, so the
# placeholder is drawn in the kit's own default palette. Every specimen
# caption says that the picture stands in for the author's own.
PLACEHOLDER_GROUND = '#e7e4d9'
PLACEHOLDER_INK = '#292925'
PLACEHOLDER_ACCENT = '#a33e36'
PLACEHOLDER_W = 560
PLACEHOLDER_H = 315
PLACEHOLDER_STROKES = 13


def data_uri(svg):
    """One SVG as a data: URI an <img> can read. The characters left
    unencoded cannot end the attribute the URI sits in."""
    return 'data:image/svg+xml,' + quote(svg, safe=":/=,")


def placeholder(seed, accent=False):
    """A picture that stands in for the author's own: bowed ink strokes on a
    tinted ground, in the hand the cover draws in. `seed` moves the strokes,
    so two placeholders beside each other are not the same drawing. Every
    number is an integer, because the URI rides inside the specimen's JSON
    and a reader has to be able to look past it."""
    strokes = []
    for step in range(PLACEHOLDER_STROKES):
        x = 46 + step * 39
        top = 96 + (step * 17 + seed * 11) % 54
        bottom = 246 - (step * 23 + seed * 13) % 62
        strokes.append(f'M{x} {top}Q{x - 13} {(top + bottom) // 2} {x + 8} {bottom}')
    return data_uri(
        # The width and the height are what gives the file a size of its own.
        # Without them a browser reads any SVG as 300 pixels wide, and the
        # lightbox would open the picture smaller than the page shows it.
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{PLACEHOLDER_W}" height="{PLACEHOLDER_H}"'
        f' viewBox="0 0 {PLACEHOLDER_W} {PLACEHOLDER_H}">'
        f'<rect width="{PLACEHOLDER_W}" height="{PLACEHOLDER_H}"'
        f' fill="{PLACEHOLDER_GROUND}"/>'
        f'<path fill="none" stroke-linecap="round" stroke-width="2"'
        f' stroke="{PLACEHOLDER_ACCENT if accent else PLACEHOLDER_INK}"'
        f' d="{"".join(strokes)}"/></svg>'
    )


def source(item, key, where):
    """Where a picture comes from. A real report points this at its own file,
    so a relative path is the common case; a specimen draws its own picture
    into a data: URI. A path that climbs out of the report folder with ".."
    breaks as soon as the page moves, and a path with a backslash in it is a
    file name from another operating system, so both stop the build."""
    value = text(item, key, where)
    if value.startswith('data:image/svg+xml'):
        return esc(value)
    parts = urlsplit(value)
    if parts.scheme in ('http', 'https') and parts.netloc:
        return esc(value)
    if parts.scheme or parts.netloc:
        raise ValueError(
            f'{where}{key} must be an absolute HTTP(S) URL, a data:image/svg+xml '
            f'URI, or a relative path: {value}'
        )
    # A Windows path is not a web address. It also hides the ".." check
    # below, which only knows the forward slash, so it is caught first.
    if '\\' in value:
        raise ValueError(
            f'{where}{key} is a path with a backslash in it: a page reads a '
            f'path with forward slashes only: {value!r}'
        )
    if not value or '..' in value.split('/'):
        raise ValueError(
            f'{where}{key} must be a path with no "..": {value!r}'
        )
    return esc(value)


def flag(item, key, where):
    """An optional true or false field. A string "true" is not a boolean and
    would read as true forever, so it stops the build."""
    value = item.get(key, False)
    if not isinstance(value, bool):
        raise ValueError(f'{where}{key} must be true or false: {value!r}')
    return value


def choice(item, key, allowed, where):
    """An optional field that takes one of a few names. The first name is the
    default."""
    value = item.get(key)
    if value is None:
        return allowed[0]
    if value not in allowed:
        raise ValueError(
            f'{where}{key} must be one of {", ".join(allowed)}: {value!r}'
        )
    return value


def alt_text(item, where):
    """What a reader hears in place of the picture. Alt text is never
    optional: a picture with none is a picture some readers never receive."""
    value = text(item, 'alt', where)
    decorative = flag(item, 'decorative', where)
    if not value.strip() and not decorative:
        raise ValueError(
            f'{where}alt cannot be empty: describe the picture, or set '
            f'decorative to true when it carries no information'
        )
    if value.strip() and decorative:
        raise ValueError(
            f'{where}a decorative picture needs no alt text: clear alt, or set '
            f'decorative to false'
        )
    return esc(value)


def picture(item, where, classes=''):
    """The <img> itself. Lazy and async, because a report is a long page and
    a picture halfway down it must not hold the first screen back."""
    name = f' class="{classes}"' if classes else ''
    src = source(item, 'src', where)
    alt = alt_text(item, where)
    return f'<img{name} src="{src}" alt="{alt}" loading="lazy" decoding="async">'


def caption_html(item, where, markup):
    """The caption, then the credit. Both are quiet, and the credit is last,
    because the reader wants the picture explained before they are told who
    made it. Neither one leaves an empty element behind."""
    caption = optional_text(item, 'caption', where)
    credit = optional_text(item, 'credit', where)
    if not caption and not credit:
        return ''
    parts = markup(caption) if caption else ''
    if credit:
        parts += f'<span class="media-credit">{markup(credit)}</span>'
    return f'<figcaption class="media-caption">{parts}</figcaption>'


SPECIMEN = {
    'summary': 'One picture on the reading column, the figure column or the full page.',
    'use_when': 'Use it when a picture carries evidence a sentence cannot.',
    'json': {
        'type': 'image',
        'id': 'image-specimen',
        'src': placeholder(1),
        'alt': 'A field of bowed ink strokes of different heights on a tinted ground.',
        'caption': 'This picture is a placeholder. Point src at your own file.',
        'credit': 'Drawn by the template',
        'width': 'figure',
        'lightbox': True,
    },
}


def lightbox_html(item, sid, where):
    """The full size view. It is a <dialog>, so the browser gives the modal
    its focus trap, its backdrop and its Escape key. Scripts off it never
    opens, and the picture beside it is a link to the file instead."""
    return (
        f'<dialog class="lightbox screen-only" id="{sid}--lightbox"'
        f' aria-label="The picture at full size">\n'
        f'<button type="button" class="control lightbox-close">Close</button>\n'
        f'{picture(item, where, "lightbox-image")}\n'
        f'</dialog>'
    )


def render(section, heading_html, where, context):
    """The picture, its caption and, when the author asks for it, the full
    size view. A picture that opens has to have a name to open under, so a
    decorative picture cannot carry a lightbox."""
    markup = inline.for_section(section, where, term=context.term)
    sid = text(section, 'id', where)
    width = choice(section, 'width', WIDTHS, where)
    lightbox = flag(section, 'lightbox', where)
    if lightbox and flag(section, 'decorative', where):
        raise ValueError(
            f'{where}a decorative picture has nothing to open: set lightbox to '
            f'false, or describe the picture in alt'
        )
    src = source(section, 'src', where)
    body = picture(section, where)
    # Scripts off, the picture is a link to its own file. A data: URI is the
    # picture itself and has no file to open, so it gets no link; the script
    # gives that one a button of its own.
    if lightbox and not src.startswith('data:'):
        body = f'<a class="lightbox-open" href="{src}">{body}</a>'
    figure_class = f'media-figure media-on-{width}'
    if lightbox:
        figure_class += ' has-lightbox'
    return (
        f'<figure class="{figure_class}">\n'
        f'{body}\n'
        f'{caption_html(section, where, markup)}\n'
        + (f'{lightbox_html(section, sid, where)}\n' if lightbox else '')
        + f'</figure>'
    ), ''
