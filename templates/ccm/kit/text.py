"""The author's text boundary. Every field the JSON supplies comes through
one of these functions, so no value reaches the markup unchecked."""
import html
from urllib.parse import urlsplit


def esc(value):
    """The last gate before the markup. Every field is named and checked by
    text() or optional_text() before it arrives here, so a value of any other
    type is a bug in this file rather than in the author's JSON."""
    if not isinstance(value, str):
        raise TypeError(f'text must be a string, not {type(value).__name__}: {value!r}')
    return html.escape(value, quote=True)


def field(item, key, where=''):
    """A required field, named where it is missing. `where` says which section
    and which step, so an error points at a line in the JSON."""
    if key not in item:
        raise ValueError(f'{where}{key} is required')
    return item[key]


def text(item, key, where=''):
    """A required plain-text field. A list or a dict here would render as its
    Python repr on the page, so it stops the build instead."""
    return check_text(field(item, key, where), key, where)


def optional_text(item, key, where=''):
    """An optional plain-text field. Present means a string and nothing else,
    so an author cannot reach the markup through it."""
    value = item.get(key)
    if value is None:
        return ''
    return check_text(value, key, where)


def check_text(value, key, where):
    if not isinstance(value, str):
        raise ValueError(
            f'{where}{key} must be a string, not {type(value).__name__}: {value!r}'
        )
    return value


def url(value, key='url', where=''):
    check_text(value, key, where)
    parts = urlsplit(value)
    if parts.scheme not in ('https', 'http') or not parts.netloc:
        raise ValueError(f'{where}{key} must be an absolute HTTP(S) URL: {value}')
    return esc(value)


def paragraphs(items, where='', markup=esc):
    """A run of paragraphs. `markup` is the renderer the section uses, which
    is the inline parser for a section and esc() for anything with no section
    of its own to read notes from."""
    if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
        raise ValueError(f'{where}paragraphs must be a list of strings')
    return '\n'.join(f'<p>{markup(p)}</p>' for p in items)


def heading(label, title, section_id, heading_id=''):
    """The small eyebrow + <h2> pair every section body opens with. The title
    is a link to its own section, so a reader can take the address of the part
    they are reading. The link wraps the title rather than sitting beside it:
    a permalink beside it would add its own name to the heading's, and every
    heading would be announced with four words that are not the heading.
    Sections without a label get no empty span and no stray line box.

    `heading_id` names the heading itself. A figure and a table point
    aria-labelledby at it, so the name they announce is the title the reader
    already sees. page.py gives every heading the same id, so no section
    module writes one of its own.
    """
    eyebrow = f'<span class="eyebrow">{esc(label)}</span>' if label else ''
    ident = f' id="{heading_id}"' if heading_id else ''
    return (
        f'{eyebrow}<h2{ident}>'
        f'<a class="heading-anchor" href="#{section_id}">{esc(title)}</a></h2>'
    )
