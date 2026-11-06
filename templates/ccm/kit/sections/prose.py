"""A run of paragraphs on the reading column, and the five blocks a run of
paragraphs can hold: a subhead, a list, a callout, a caveat and a pull quote.

A block is an object where a paragraph would be, so the order of the argument
stays one list and an author never opens a second field to break a page.
"""
from .. import inline
from ..text import check_text, esc, field, text

NAME = 'prose'
TITLE_REQUIRED = True
# The place of the type in the guide's table and in its specimens. Ties break
# on the name, so two families can pick the same number without a merge.
ORDER = 10
FIELDS = ('<code>label</code>, <code>title</code>, <code>paragraphs</code>'
          ' (list of text, or a block object)')
CAVEAT_TITLE = 'Caveat'
SHAPE = 'paragraphs must be a list of strings, or of block objects'
# Each block key, with the keys it allows beside it. Anything else in the
# object is a typing mistake and stops the build with its own name in the
# message.
BLOCKS = {
    'subhead': (),
    'list': ('ordered',),
    'callout': (),
    'caveat': (),
    'pullquote': (),
}
SPECIMEN = {
    'summary': 'A heading and a run of paragraphs, with five blocks a run can hold.',
    'use_when': 'Use it when the reader needs the argument in sentences.',
    'json': {
        'type': 'prose',
        'id': 'prose-specimen',
        'label': 'The question',
        'title': 'A story is only the beginning.',
        'paragraphs': [
            'A reporter asks a question. A resident shares what they know. An editor connects the account to a wider story. Each exchange gives information a place to go.[^1] When two newsrooms answer one question together, the work becomes {collaborative reporting}.',
            {'pullquote': 'Each exchange gives information a place to go.'},
            {'subhead': 'What a block does'},
            'A paragraph can also be a block. Every block keeps the reading column, and none of them adds a card, an icon or a color.',
            {
                'list': [
                    'A subhead opens one part of the argument.',
                    'A list holds items a reader scans.',
                    'A pull quote lifts one sentence the reader has already read.',
                ],
                'ordered': False,
            },
            {
                'callout': {
                    'title': 'One fact, set aside',
                    'text': 'An invented example. A callout holds a fact that matters and would break the sentence beside it.',
                },
            },
            {
                'caveat': {
                    'text': 'An invented example. The sample is too small to carry a claim about the whole state.',
                },
            },
        ],
        'notes': [
            'An invented example. A note holds the source or the limit that would break the sentence.',
        ],
    },
}


def unknown_key(item, name, spot):
    """The first key the block does not read, named in the error, so an author
    who wrote "orderd" is told the word rather than the block."""
    allowed = {name, *BLOCKS[name]}
    for key in item:
        if key not in allowed:
            raise ValueError(
                f'{spot}a {name} block does not read the key {key!r}'
            )


def block_name(item, spot):
    names = [key for key in item if key in BLOCKS]
    if len(names) != 1:
        raise ValueError(
            f'{spot}a block holds one of {", ".join(sorted(BLOCKS))}, and this '
            f'one holds {len(names)}: {sorted(item)}'
        )
    unknown_key(item, names[0], spot)
    return names[0]


def render_list(item, spot, markup):
    rows = item['list']
    if not isinstance(rows, list) or not rows:
        raise ValueError(f'{spot}list must be a list with at least one item')
    ordered = item.get('ordered', False)
    if not isinstance(ordered, bool):
        raise ValueError(f'{spot}ordered must be true or false')
    tag = 'ol' if ordered else 'ul'
    items = '\n'.join(
        f'<li>{markup(check_text(row, "list", spot), spot)}</li>' for row in rows
    )
    return f'<{tag} class="prose-list">\n{items}\n</{tag}>'


def render_aside(item, name, spot, markup):
    """A callout and a caveat are one block with two rules. The caveat states
    its own name by default, because a limit a reader has to notice cannot rely
    on a border to say what it is."""
    source = item[name]
    if not isinstance(source, dict):
        raise ValueError(f'{spot}a {name} holds a text and an optional title')
    title = source.get('title')
    if title is None and name == 'caveat':
        title = CAVEAT_TITLE
    heading = ''
    if title is not None:
        heading = f'<p class="callout-title">{esc(check_text(title, "title", spot))}</p>\n'
    body = markup(text(source, 'text', spot), spot)
    kind = ' caveat' if name == 'caveat' else ''
    return f'<aside class="callout{kind}">\n{heading}<p>{body}</p>\n</aside>'


def render_pullquote(item, spot, lifted):
    """A pull quote is a lift, so the build reads it back against the section's
    own paragraphs. The author writes the sentence a reader sees, and the
    paragraphs are reduced to what a reader sees as well: a link is its text, a
    term is the term, and a note reference is gone. A sentence with a link in
    it can then be lifted, and it prints as a sentence rather than as markup.

    It carries aria-hidden because the sentence is already in the text above
    it, and a reader who listens would hear it twice."""
    quote = check_text(item['pullquote'], 'pullquote', spot)
    if not any(quote in paragraph for paragraph in lifted):
        raise ValueError(
            f'{spot}the pull quote is not in this section: a pull quote lifts a '
            f'sentence that a paragraph of the same section already holds, as '
            f'the reader sees it and not as the markup writes it'
        )
    return f'<p class="pullquote" aria-hidden="true">{esc(quote)}</p>'


def render_block(item, spot, markup, lifted):
    name = block_name(item, spot)
    if name == 'subhead':
        return f'<h3>{markup(check_text(item["subhead"], "subhead", spot), spot)}</h3>'
    if name == 'list':
        return render_list(item, spot, markup)
    if name == 'pullquote':
        return render_pullquote(item, spot, lifted)
    return render_aside(item, name, spot, markup)


def render_paragraphs(items, where, markup):
    if not isinstance(items, list) or not items:
        raise ValueError(f'{where}{SHAPE}')
    lifted = [inline.plain(item, where) for item in items if isinstance(item, str)]
    rows = []
    for index, item in enumerate(items, 1):
        spot = f'{where[:-2]} paragraph {index}: '
        if isinstance(item, dict):
            rows.append(render_block(item, spot, markup, lifted))
        elif isinstance(item, str):
            rows.append(f'<p>{markup(item, spot)}</p>')
        else:
            raise ValueError(f'{spot}{SHAPE}, and this one is a {type(item).__name__}')
    return '\n'.join(rows)


def render(section, heading_html, where, context):
    markup = inline.for_section(section, where, term=context.term)
    body = (
        f'<div class="reading">{heading_html}\n'
        f'{render_paragraphs(field(section, "paragraphs", where), where, markup)}\n'
        f'</div>'
    )
    return body, ''
