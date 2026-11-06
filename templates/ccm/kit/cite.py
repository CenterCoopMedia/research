"""The report's own citation, in three forms.

Every field comes from the report the reader has open, so a citation can never
name a title, a date or an address the page does not carry. The share dialog
shows the three strings on screen and the print stylesheet puts the plain one
under the colophon.

`authors` is a string or a list of objects with a `name`, the two shapes
endmatter.py accepts, and this module reads both without asking it.
"""
import re

from .text import check_text, field, text

# BibTeX reads these eight characters as syntax, so a field that holds one is
# escaped before it goes in an entry. Nothing is dropped: a title that names a
# folder or a draft keeps every character the report writes.
LATEX_ESCAPES = {
    # The backslash is first, because its escape writes two braces of its own.
    '\\': r'\textbackslash{}',
    '{': r'\{',
    '}': r'\}',
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
}
LATEX = re.compile('[' + re.escape(''.join(LATEX_ESCAPES)) + ']')
YEAR = re.compile(r'\b(\d{4})\b')
WORD = re.compile(r'[a-z0-9]+')


def author_names(data, where=''):
    """Every author's name, in the order the report states them. A string is
    one name. A list holds one object with a `name` for each author."""
    value = field(data, 'authors', where)
    if isinstance(value, str):
        return [check_text(value, 'authors', where)]
    if not isinstance(value, list) or not value:
        raise ValueError(
            f'{where}authors is a name, or a list of authors with a name each'
        )
    names = []
    for index, author in enumerate(value, 1):
        spot = f'{where}author {index}: '
        if not isinstance(author, dict):
            raise ValueError(f'{spot}an author is an object with a name')
        names.append(text(author, 'name', spot))
    return names


def joined(names):
    """Names as a reader says them: commas between, "and" before the last."""
    if len(names) == 1:
        return names[0]
    return f'{", ".join(names[:-1])} and {names[-1]}'


def stop(value):
    """A full stop, unless the sentence already ends in one. A title that ends
    in a question mark keeps it and takes no second mark."""
    return value if value.endswith(('.', '?', '!')) else f'{value}.'


def parts(data, where=''):
    """The six fields every form is built from. `names` is the list, because
    BibTeX joins authors its own way, and `byline` is the reader's join."""
    names = author_names(data, where)
    return {
        'names': names,
        'byline': joined(names),
        'title': text(data, 'title', where),
        'organization': text(data, 'organization', where),
        'date': text(data, 'date', where),
        'series': text(data, 'series', where),
        'url': text(data, 'url', where),
    }


def plain(item):
    """One line a reader can paste into a document or a message."""
    return (
        f'{stop(item["byline"])} {stop(item["title"])} {stop(item["series"])} '
        f'{item["organization"]}, {item["date"]}. {item["url"]}'
    )


def apa(item):
    """APA 7, in the shape a report takes: author, date, title, publisher, URL.

    The names stay as the report writes them. The kit cannot tell which part of
    a name is the family name, and an inverted name that guesses wrong is worse
    than a name printed the way its owner writes it.
    """
    return (
        f'{stop(item["byline"])} ({item["date"]}). {stop(item["title"])} '
        f'{stop(item["organization"])} {item["url"]}'
    )


def field_text(value):
    """One BibTeX field value. One pass reads each character once and writes
    its escape, so the braces the backslash escape adds are not escaped
    again."""
    return LATEX.sub(lambda found: LATEX_ESCAPES[found.group()], value)


def key(item):
    """The citation key: the last word of the first name, the year, and the
    first word of the title, which is how a reader types it from memory."""
    first = item['names'][0].split()
    groups = [WORD.findall(first[-1].lower()) if first else []]
    groups.append(WORD.findall(item['title'].lower()))
    pieces = [group[0] for group in groups if group]
    found = YEAR.search(item['date'])
    if found and pieces:
        pieces.insert(1, found.group(1))
    return ''.join(pieces) or 'report'


def bibtex(item):
    """A `techreport` entry. A report with no four-digit year in its date gets
    no year field rather than a guessed one."""
    found = YEAR.search(item['date'])
    month = YEAR.sub('', item['date']).strip(' ,.') if found else item['date']
    rows = [
        ('author', ' and '.join(item['names'])),
        ('title', item['title']),
        ('institution', item['organization']),
        ('series', item['series']),
    ]
    if found:
        rows.append(('year', found.group(1)))
    if month:
        rows.append(('month', month))
    rows.append(('url', item['url']))
    body = ',\n'.join(f'  {name} = {{{field_text(value)}}}' for name, value in rows)
    return f'@techreport{{{key(item)},\n{body}\n}}'


def citations(data, where=''):
    """The three forms, keyed by the name each one goes under in the dialog."""
    item = parts(data, where)
    return {'plain': plain(item), 'apa': apa(item), 'bibtex': bibtex(item)}
