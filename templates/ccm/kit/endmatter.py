"""The blocks that come after the last section: the authors, the credits, what
to read next, the series links, the form and the corrections.

The cover byline is here as well, because the byline states the authors and
the authors are end matter. page.py calls byline() for the cover and render()
for the blocks, so the shape of `authors` changes in this file alone.

Every block reads a top-level field. The download list reads one too, so it
lives here, but the methods band places it: methods.py calls
render_downloads() and puts the list under its citations.
"""
import re
from urllib.parse import urlsplit

from . import inline
from .text import check_text, esc, field, optional_text, text, url

# A form field name, and the name of the spam trap that must stay free.
FIELD_NAME = re.compile(r'[a-z][a-z0-9_-]*')
TRAP = 'website'
# The names the form element keeps for itself. A field with one of these names
# hides the property of the same name behind the input, so `form.action` in a
# script gives the input and not the address. The script reads the two it needs
# with getAttribute(), and a field that takes one of these names stops the
# build, because the shadow reaches every other script on the page as well.
RESERVED = (
    'action', 'method', 'submit', 'reset', 'elements', 'length', 'name',
    'target', 'enctype', 'encoding', 'acceptCharset', 'autocomplete',
    'noValidate',
)
# The autocomplete token each common field name takes. A name outside this
# table has no token the kit can guess, so the author states one. The field for
# a person's name is `full-name`, because `name` is one of the names the form
# element keeps for itself.
AUTOCOMPLETE = {
    'email': 'email',
    'full-name': 'name',
    'organization': 'organization',
}
# One email address, which is what a report form asks for when the author
# lists no fields of their own.
DEFAULT_FIELDS = ({'name': 'email', 'label': 'Email address'},)


def markup(value, where):
    """End-matter text. A link works. A note reference and a glossary term do
    not, because a block after the last section belongs to no section and has
    no notes to point at."""
    return inline.render(value, where)


def block(name, label, body, label_id='', screen_only=False):
    """One end-matter block: a hairline, a small label, and the content.

    The hairline goes edge to edge and the content takes a role width, so one
    wrapper holds both. That wrapper carries the body type size as well, and
    the measure is stated in em: a width on the small label itself would come
    out of the label's own size and would be a third short.
    """
    ident = f' id="{label_id}"' if label_id else ''
    kind = f'{name} screen-only' if screen_only else name
    return (
        f'<section class="endmatter endmatter-{kind}">\n'
        f'<div class="endmatter-inner">\n'
        f'<h2 class="endmatter-label"{ident}>{esc(label)}</h2>\n'
        f'{body}\n'
        f'</div>\n'
        f'</section>'
    )


def listing(data, key, where, low, high):
    """A top-level list field, checked for a list and for its bounds."""
    items = field(data, key, where)
    if not isinstance(items, list):
        raise ValueError(
            f'{where}{key} must be a list, not {type(items).__name__}: {items!r}'
        )
    if not low <= len(items) <= high:
        raise ValueError(
            f'{where}{key} holds {low} to {high} items, and this one holds '
            f'{len(items)}'
        )
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ValueError(
                f'{where}{key} item {index} must be an object, not '
                f'{type(item).__name__}: {item!r}'
            )
    return items


def authors(data, where=''):
    """Every author as an object, or None when `authors` is the string form
    the kit shipped with."""
    value = field(data, 'authors', where)
    if isinstance(value, str):
        return None
    if not isinstance(value, list):
        raise ValueError(
            f'{where}authors must be a string, not {type(value).__name__}: {value!r}'
        )
    if not value:
        raise ValueError(
            f'{where}authors cannot be an empty list: write one object for each '
            f'author, or one string for the whole byline'
        )
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(
                f'{where}authors must be a string, not list of '
                f'{type(item).__name__}: a list of authors holds one object with '
                f'a name for each author'
            )
    return value


def names(data, where=''):
    """The names the byline states, joined with commas and "and"."""
    people = authors(data, where)
    if people is None:
        return text(data, 'authors', where)
    written = [
        text(person, 'name', f'{where}authors author {index}: ')
        for index, person in enumerate(people, 1)
    ]
    if len(written) == 1:
        return written[0]
    return f'{", ".join(written[:-1])} and {written[-1]}'


def byline(data):
    """The cover byline: who wrote the report, and when it was published."""
    return (
        '<p class="byline">'
        f'<span>{esc(names(data))}</span>'
        f'<span class="byline-date">{esc(text(data, "date"))}</span>'
        '</p>'
    )


def check_author(person, where):
    """Every field one author supplies, read and checked. The block renders
    only when an author says more than a name, so the check comes before that
    decision: a broken bio stops the build even when nothing shows it."""
    text(person, 'name', where)
    optional_text(person, 'role', where)
    optional_text(person, 'bio', where)
    if person.get('url') is not None:
        url(person['url'], 'url', where)


def render_author(person, where):
    """One author: the name, then the role, the bio and the link the author
    supplies. The link states the host it points at, the way a citation does,
    so the reader sees where it goes before following it."""
    rows = [f'<h3 class="author-name">{esc(text(person, "name", where))}</h3>']
    role = optional_text(person, 'role', where)
    if role:
        rows.append(f'<p class="author-role">{esc(role)}</p>')
    bio = optional_text(person, 'bio', where)
    if bio:
        rows.append(f'<p class="author-bio">{markup(bio, where)}</p>')
    if person.get('url') is not None:
        href = url(person['url'], 'url', where)
        host = esc(urlsplit(person['url']).netloc)
        rows.append(f'<p class="author-link"><a href="{href}" rel="noopener">{host}</a></p>')
    return '<div class="author">\n' + '\n'.join(rows) + '\n</div>'


def render_authors(data, where=''):
    """The block renders only when an author carries a bio or a link. A row of
    bare names repeats the byline and tells the reader nothing new."""
    if 'authors' not in data:
        return ''
    people = authors(data, where)
    if people is None:
        return ''
    for index, person in enumerate(people, 1):
        check_author(person, f'{where}authors author {index}: ')
    if not any(person.get('bio') or person.get('url') for person in people):
        return ''
    label = 'About the author' if len(people) == 1 else 'About the authors'
    rows = '\n'.join(
        render_author(person, f'{where}authors author {index}: ')
        for index, person in enumerate(people, 1)
    )
    return block('authors', label, f'<div class="authors">\n{rows}\n</div>')


def render_contributors(data, where=''):
    """The credits: the role, then the name, in the order the author writes
    them. The role is the term of the list, because a reader looks for the
    work before the person who did it."""
    if 'contributors' not in data:
        return ''
    people = listing(data, 'contributors', where, 1, 40)
    rows = []
    for index, person in enumerate(people, 1):
        spot = f'{where}contributors item {index}: '
        rows.append(
            f'<div><dt>{esc(text(person, "role", spot))}</dt>'
            f'<dd>{esc(text(person, "name", spot))}</dd></div>'
        )
    body = '<dl class="contributors">\n' + '\n'.join(rows) + '\n</dl>'
    return block('contributors', 'Credits', body)


def render_related(data, where=''):
    """Read next: two or three reports the reader may want after this one,
    each with the title as the link and one line to judge it by."""
    if 'related' not in data:
        return ''
    items = listing(data, 'related', where, 1, 3)
    rows = []
    for index, item in enumerate(items, 1):
        spot = f'{where}related item {index}: '
        href = url(field(item, 'url', spot), 'url', spot)
        rows.append(
            f'<li><a href="{href}" rel="noopener">{esc(text(item, "title", spot))}</a>\n'
            f'<p>{markup(text(item, "description", spot), spot)}</p></li>'
        )
    body = (
        f'<ul class="read-next" data-count="{len(items)}">\n'
        + '\n'.join(rows)
        + '\n</ul>'
    )
    return block('related', 'Read next', body)


def render_series_link(item, direction, where):
    """One end of the series: the direction word, then the real title, so the
    reader decides before the click."""
    href = url(field(item, 'url', where), 'url', where)
    return (
        f'<a class="series-link series-{direction}" href="{href}" rel="noopener">'
        f'<span class="series-direction">{direction.capitalize()}</span>'
        f'<span class="series-title">{esc(text(item, "title", where))}</span></a>'
    )


def render_series_links(data, where=''):
    """The report before this one and the report after it."""
    if 'series_links' not in data:
        return ''
    links = field(data, 'series_links', where)
    if not isinstance(links, dict):
        raise ValueError(
            f'{where}series_links must be an object with a previous link, a next '
            f'link, or both, not {type(links).__name__}: {links!r}'
        )
    rows = []
    for direction in ('previous', 'next'):
        item = links.get(direction)
        if item is None:
            continue
        spot = f'{where}series_links {direction}: '
        if not isinstance(item, dict):
            raise ValueError(f'{spot}a series link holds a title and a URL')
        rows.append(render_series_link(item, direction, spot))
    if not rows:
        raise ValueError(
            f'{where}series_links needs a previous link, a next link, or both'
        )
    body = (
        '<nav class="series-links" aria-labelledby="series-links--label">\n'
        + '\n'.join(rows)
        + '\n</nav>'
    )
    return block('series-links', 'More in this series', body, 'series-links--label')


def form_endpoint(value, where):
    """Where the form posts. It is an absolute HTTPS URL and it never opens a
    mail client: a mail client cannot validate a field, cannot confirm a send,
    and puts the reader's address on a public page."""
    check_text(value, 'endpoint', where)
    parts = urlsplit(value)
    if parts.scheme == 'mailto':
        raise ValueError(
            f'{where}endpoint must not open a mail client: post to a form '
            f'endpoint over HTTPS instead: {value}'
        )
    if parts.scheme != 'https' or not parts.netloc:
        raise ValueError(f'{where}endpoint must be an absolute HTTPS URL: {value}')
    return esc(value)


def form_field(item, index, taken, where):
    """One field of the form, checked and rendered, with the flag that says
    whether the reader must fill it. Every field carries a label, an
    autocomplete token and its own error paragraph."""
    spot = f'{where}form field {index}: '
    if not isinstance(item, dict):
        raise ValueError(f'{spot}a field holds a name and a label')
    name = text(item, 'name', spot)
    if name == TRAP:
        raise ValueError(f'{spot}the name {TRAP!r} belongs to the spam trap')
    if name in RESERVED:
        raise ValueError(
            f'{spot}the name {name!r} belongs to the form element itself, and a '
            f'field with that name hides it from every script on the page: '
            f'choose another name'
        )
    if not FIELD_NAME.fullmatch(name):
        raise ValueError(
            f'{spot}name must be lowercase and hold letters, digits, hyphens and '
            f'underscores: {name!r}'
        )
    if name in taken:
        raise ValueError(f'{spot}the name {name!r} is used twice')
    taken.add(name)
    label = text(item, 'label', spot)
    if not label.strip():
        raise ValueError(
            f'{spot}label cannot be blank: the field {name!r} needs a name the '
            f'reader can read'
        )
    required = item.get('required', True)
    if not isinstance(required, bool):
        raise ValueError(f'{spot}required must be true or false: {required!r}')
    complete = item.get('autocomplete')
    if complete is None:
        complete = AUTOCOMPLETE.get(name)
    else:
        check_text(complete, 'autocomplete', spot)
    if not complete:
        raise ValueError(
            f'{spot}autocomplete is required for the field {name!r}: state the '
            f'token the browser fills it from'
        )
    ident = f'form--{name}'
    kind = 'email' if complete == 'email' else 'text'
    attrs = (
        f' id="{ident}" name="{esc(name)}" type="{kind}"'
        f' autocomplete="{esc(complete)}" aria-describedby="{ident}-error"'
    )
    if required:
        attrs += ' required'
        attrs += f' data-required-error="enter your {esc(label.lower())}."'
    if kind == 'email':
        attrs += (
            ' data-format-error="enter an email address in the correct format,'
            ' like name@example.com."'
        )
    # The word "Error" opens the message and the script writes only the text
    # after it, so the summary lists the same message with no repeated word in
    # front of every line. The message starts in lower case because a colon
    # opens it here; the summary lifts its first letter in the stylesheet.
    markup = (
        f'<div class="form-field">\n'
        f'<label for="{ident}">{esc(label)}</label>\n'
        f'<p class="field-error" id="{ident}-error" hidden>'
        f'<span class="error-word">Error:</span> <span class="error-text"></span></p>\n'
        f'<input class="form-input"{attrs}>\n'
        f'</div>'
    )
    return markup, required


def render_form(data, where=''):
    """The form ships only when `form.endpoint` is set. What renders is a plain
    form that posts on its own: 50-form.js adds the inline errors and the error
    summary to a form that already works without it.

    `inline` says which of the two sends runs. Without it the script checks the
    fields and then lets the native post go, so the endpoint answers with its
    own page. With it the script posts with fetch and keeps the reader here,
    which an endpoint answers only when it sends CORS headers.
    """
    if 'form' not in data:
        return ''
    form = field(data, 'form', where)
    if not isinstance(form, dict):
        raise ValueError(
            f'{where}form must be an object with an endpoint, a heading and a '
            f'reason, not {type(form).__name__}: {form!r}'
        )
    if form.get('endpoint') is None:
        return ''
    spot = f'{where}form: '
    action = form_endpoint(form['endpoint'], spot)
    heading = text(form, 'heading', spot)
    reason = text(form, 'reason', spot)
    send = optional_text(form, 'button', spot) or 'Subscribe'
    inline_send = form.get('inline', False)
    if not isinstance(inline_send, bool):
        raise ValueError(f'{spot}inline must be true or false: {inline_send!r}')
    fields = form.get('fields')
    if fields is None:
        fields = list(DEFAULT_FIELDS)
    if not isinstance(fields, list) or not fields:
        raise ValueError(f'{spot}fields must be a list with one object for each field')
    taken = set()
    rows, wanted = [], 0
    for index, item in enumerate(fields, 1):
        markup_row, required = form_field(item, index, taken, where)
        rows.append(markup_row)
        wanted += required
    if not wanted:
        raise ValueError(
            f'{spot}at least one field must be required: a form where every '
            f'field is optional sends an empty reply and tells the reader it '
            f'has their answer'
        )
    rows = '\n'.join(rows)
    mode = ' data-inline="true"' if inline_send else ''
    body = (
        f'<form class="signup" method="post" action="{action}"{mode}'
        f' data-success="Thank you. We have your {{field}}: {{value}}."'
        f' data-success-empty="Thank you. We have your reply.">\n'
        f'<div class="form-summary" tabindex="-1" hidden>\n'
        f'<p class="form-summary-title">Error: the form is not ready to send.</p>\n'
        f'<ul></ul>\n'
        f'</div>\n'
        f'<p class="form-send-error" role="alert" hidden>Error: the form did not '
        f'send. Check your connection and try again.</p>\n'
        f'{rows}\n'
        f'<div class="form-trap" aria-hidden="true">\n'
        f'<label for="form--{TRAP}">Leave this field empty</label>\n'
        f'<input id="form--{TRAP}" name="{TRAP}" type="text" tabindex="-1" autocomplete="off">\n'
        f'</div>\n'
        f'<div class="form-actions">\n'
        f'<button class="button primary" type="submit" data-sending="Sending">{esc(send)}</button>\n'
        f'<p class="form-reason">{markup(reason, spot)}</p>\n'
        f'</div>\n'
        f'</form>\n'
        f'<p class="form-status" role="status" tabindex="-1" hidden></p>'
    )
    # A form is interactive, and paper takes no input, so the block is one of
    # the parts the print rule drops.
    return block('form', heading, body, screen_only=True)


def render_corrections(data, where=''):
    """The corrections log: what changed after publication, and when. It is
    plain text in the order the author writes it, because a log that is styled
    to be read quickly is a log that is styled to be missed."""
    if 'corrections' not in data:
        return ''
    items = listing(data, 'corrections', where, 1, 40)
    rows = []
    for index, item in enumerate(items, 1):
        spot = f'{where}corrections item {index}: '
        rows.append(
            f'<li><span class="correction-date">{esc(text(item, "date", spot))}</span>\n'
            f'<p class="correction-text">{markup(text(item, "text", spot), spot)}</p></li>'
        )
    body = '<ul class="corrections">\n' + '\n'.join(rows) + '\n</ul>'
    return block('corrections', 'Corrections', body)


def download_list(data, where=''):
    """The download list, read and checked. page.py reads it once for the whole
    report, because the list renders inside the methods band and the report
    holds one of those."""
    if 'downloads' not in data:
        return None
    return listing(data, 'downloads', where, 1, 12)


def render_downloads(data, where=''):
    """The download list of one report, as markup."""
    items = download_list(data, where)
    if items is None:
        return ''
    return downloads_markup(items, where)


def downloads_markup(items, where=''):
    """The files the report offers. The format and the size sit inside the
    link, so a reader hears them in the link's own name and knows what the
    click starts. methods.py places this list under its citations."""
    rows = []
    for index, item in enumerate(items, 1):
        spot = f'{where}downloads item {index}: '
        href = url(field(item, 'url', spot), 'url', spot)
        meta = f'{text(item, "format", spot)}, {text(item, "size", spot)}'
        rows.append(
            f'<li><a href="{href}">'
            f'<span class="download-label">{esc(text(item, "label", spot))}</span>'
            f'<span class="download-meta">{esc(meta)}</span></a></li>'
        )
    return (
        '<div class="downloads">\n'
        '<h3>Downloads</h3>\n'
        '<ul>\n' + '\n'.join(rows) + '\n</ul>\n'
        '</div>'
    )


# The fixed order of section 5 of the brief. The footer follows them, and
# page.py renders that.
BLOCKS = (
    render_authors,
    render_contributors,
    render_related,
    render_series_links,
    render_form,
    render_corrections,
)


def render(data, where=''):
    """Every end-matter block, in the fixed order, as one string. A block that
    reads a field the report does not carry renders nothing and leaves no
    empty element behind."""
    return '\n'.join(filter(None, (one(data, where) for one in BLOCKS)))


SOURCES = (
    {
        'name': 'authors',
        'summary': 'A row for each author with the role, the bio and a link.',
        'use_when': 'Use it when the reader needs to know who did the work.',
        'json': {
            'authors': [
                {
                    'name': 'Robin Vega',
                    'role': 'Lead researcher',
                    'bio': 'An invented author for this specimen. Replace the name, '
                           'the role and the bio with your own.',
                    'url': 'https://example.org/people/robin-vega',
                },
                {
                    'name': 'Sam Okafor',
                    'role': 'Data reporter',
                    'bio': 'A second invented author. The cover byline joins the '
                           'two names.',
                },
            ],
        },
        'render': render_authors,
    },
    {
        'name': 'contributors',
        'summary': 'A credits list that states the role before the name.',
        'use_when': 'Use it when more hands did the work than the byline shows.',
        'json': {
            'contributors': [
                {'role': 'Editing', 'name': 'Dana Whitfield'},
                {'role': 'Illustration', 'name': 'Ola Brandt'},
                {'role': 'Fact checking', 'name': 'Priya Raman'},
            ],
        },
        'render': render_contributors,
    },
    {
        'name': 'related',
        'summary': 'A "Read next" row of one to three reports with a line each.',
        'use_when': 'Use it when the site holds other reports on the same subject.',
        'json': {
            'related': [
                {
                    'title': 'What the network counted in 2025',
                    'url': 'https://example.org/reports/2025',
                    'description': 'An invented earlier report. Say what the reader gets from it.',
                },
                {
                    'title': 'How the partners share a story',
                    'url': 'https://example.org/reports/sharing',
                    'description': 'A second invented report, to show the row with two items.',
                },
            ],
        },
        'render': render_related,
    },
    {
        'name': 'series_links',
        'summary': 'The report before this one and the report after it, by title.',
        'use_when': 'Use it when the report is one part of a numbered series.',
        'json': {
            'series_links': {
                'previous': {
                    'title': 'Part one: what the partners asked for',
                    'url': 'https://example.org/reports/part-one',
                },
                'next': {
                    'title': 'Part three: what the network does next',
                    'url': 'https://example.org/reports/part-three',
                },
            },
        },
        'render': render_series_links,
    },
    {
        'name': 'form',
        'summary': 'A one-column form that posts to your endpoint and states what the reader gets.',
        'use_when': 'Use it when a real list is behind it and you can name what it sends.',
        'json': {
            'form': {
                'endpoint': 'https://example.org/subscribe',
                'heading': 'Get the next report',
                'reason': 'One email a month with the next report and what it found. '
                          'This specimen sends inline, and the endpoint is a '
                          'placeholder: a real deployment needs an endpoint that '
                          'answers with CORS headers, so a send from this page '
                          'fails.',
                'button': 'Subscribe',
                'inline': True,
            },
        },
        'render': render_form,
    },
    {
        'name': 'corrections',
        'summary': 'A dated log of what changed after publication.',
        'use_when': 'Use it as soon as you change a published number or a name.',
        'json': {
            'corrections': [
                {
                    'date': '4 March 2026',
                    'text': 'An invented entry. Corrected the partner count in the '
                            'findings from 320 to 330.',
                },
                {
                    'date': '19 March 2026',
                    'text': 'A second invented entry. Named the county the sample '
                            'was drawn from.',
                },
            ],
        },
        'render': render_corrections,
    },
    {
        'name': 'downloads',
        'summary': 'A file list inside the methods band that states the format and the size.',
        'use_when': 'Use it when the reader can check your work against the data.',
        'json': {
            'downloads': [
                {
                    'label': 'Survey responses',
                    'url': 'https://example.org/data/responses-2026-03.csv',
                    'format': 'CSV',
                    'size': '412 KB',
                },
                {
                    'label': 'Method note',
                    'url': 'https://example.org/data/method-note-2026-03.pdf',
                    'format': 'PDF',
                    'size': '1.2 MB',
                },
            ],
        },
        'render': render_downloads,
    },
)

# One specimen for each block, in the order the guide shows them. The guide
# reads `html`, because an end-matter block reads top-level fields and has no
# section for render_sections() to build.
SPECIMENS = [
    {
        'name': source['name'],
        'summary': source['summary'],
        'use_when': source['use_when'],
        'json': source['json'],
        'html': source['render'](source['json']),
    }
    for source in SOURCES
]
