"""The page frame: the head, the header, the cover, the sections and the
colophon. Everything a report has that is not one section type."""
import math
import re
from urllib.parse import urlsplit

from . import assets, cite, endmatter, fonts, inline, notes
from .art import artwork, seed_from
from .registry import REGISTRY
from .text import check_text, esc, field, heading, optional_text, text, url
from .theme import favicon_link, theme_tokens


# The subset of BCP 47 a report needs, in lowercase: a language of two or three
# letters, then an optional script of four letters, then an optional region of
# two letters or three digits, then any number of variants of five to eight
# letters and digits or of a digit and three more; or a private use tag, "x"
# and one or more subtags of one to eight letters and digits. Extensions and
# grandfathered tags are not in the subset, because a report has no use for
# them and a loose pattern lets an incomplete tag such as "en-a" through.
LANGUAGE = re.compile(
    r'[a-z]{2,3}(-[a-z]{4})?(-([a-z]{2}|[0-9]{3}))?'
    r'(-([a-z0-9]{5,8}|[0-9][a-z0-9]{3}))*'
    r'|x(-[a-z0-9]{1,8})+'
)
# The two page layouts. `reading` is the centered column the kit shipped with;
# `wide` puts the same measure against the left gutter and opens a rail beside
# it. A report that names neither reads the centered one.
PAGE_LAYOUTS = ('reading', 'wide')
# Words a minute, for the reading time on the cover. 200 is the middle of the
# measured range for an adult reading prose of this kind on a screen.
WORDS_A_MINUTE = 200
# These fields name a structure or an address, not prose, so the reading time
# does not count them.
NOT_PROSE = frozenset({'id', 'type', 'layout', 'highlight', 'kind', 'url', 'endpoint'})


def language(data):
    """The report's language, written on <html>. English is the default,
    because the kit is written in it and most reports that use it are too."""
    value = data.get('lang')
    if value is None:
        return 'en'
    check_text(value, 'lang', '')
    if not LANGUAGE.fullmatch(value):
        raise ValueError(
            f'lang must be a BCP 47 tag in the lowercase subset the kit reads, '
            f'such as "en", "es-419" or "zh-hant-tw": {value!r}'
        )
    return value


def page_layout(data):
    """The layout one report asks for, checked. The name goes on <body>, and
    the stylesheet reads it from there, so a report changes layout by one line
    of JSON and no change to a section."""
    value = data.get('layout')
    if value is None:
        return PAGE_LAYOUTS[0]
    check_text(value, 'layout', '')
    if value not in PAGE_LAYOUTS:
        raise ValueError(
            f'layout must be one of {", ".join(PAGE_LAYOUTS)}, not {value!r}'
        )
    return value


def count_words(value):
    """The words in one field, one item or one whole section. It walks whatever
    a section type holds, so a new type is counted without naming its fields."""
    if isinstance(value, str):
        return len(value.split())
    if isinstance(value, list):
        return sum(count_words(item) for item in value)
    if isinstance(value, dict):
        return sum(count_words(item) for key, item in value.items()
                   if key not in NOT_PROSE)
    return 0


def reading_minutes(data):
    """How long the sections take to read, rounded up. The cover states it
    beside the date, so a reader can judge the piece before starting it."""
    words = sum(count_words(section) for section in data['sections'])
    return max(1, math.ceil(words / WORDS_A_MINUTE))


def first_reading_id(data):
    """Where "Begin reading" lands: the first section that renders a heading.
    A quote carries no title, so a report that opens with one would otherwise
    drop the reader into a sentence with nothing above it."""
    for section in data['sections']:
        module = REGISTRY.get(section.get('type'))
        if module is not None and module.TITLE_REQUIRED:
            return section['id']
    return data['sections'][0]['id']


def glossary_terms(data):
    """Every term the report defines, with the ids of its entry and its
    popover, read from every glossary section before the first section renders,
    so a term in the first section can point at a definition the last section
    holds.

    The check here is a light one: the section carries a list of terms, and
    each term carries two text fields. The glossary module owns the rest, and
    it owns the ids as well, so the mention and the entry write one name.
    """
    module = REGISTRY.get('glossary')
    terms, defined_in, ids = {}, {}, {}
    for position, section in enumerate(data['sections'], 1):
        if not isinstance(section, dict) or section.get('type') != 'glossary':
            continue
        sid = section.get('id', f'section {position}')
        where = f'section "{sid}": '
        items = field(section, 'terms', where)
        if not isinstance(items, list):
            raise ValueError(f'{where}terms must be a list of terms')
        names = []
        for index, item in enumerate(items, 1):
            spot = f'section "{sid}" term {index}: '
            if not isinstance(item, dict):
                raise ValueError(f'{spot}a term holds a term and a definition')
            name = text(item, 'term', spot)
            definition = text(item, 'definition', spot)
            if name in terms:
                raise ValueError(
                    f'{spot}the term {name!r} is defined twice: section '
                    f'"{defined_in[name]}" defines it and section "{sid}" '
                    f'defines it again'
                )
            terms[name] = definition
            defined_in[name] = sid
            names.append(name)
        if module is not None:
            ids.update(module.anchors(sid, names))
    return terms, ids


def downloads_for(data, where=''):
    """The download list, and the rule that places it. Every methods band
    renders the list, so two bands would print the files twice and no band
    would print them nowhere. The count runs once, before the first section
    renders, and the band takes the list from here."""
    items = endmatter.download_list(data, where)
    if items is None:
        return None
    bands = sum(
        1 for section in data.get('sections') or []
        if isinstance(section, dict) and section.get('type') == 'methods'
    )
    if bands != 1:
        raise ValueError(
            f'{where}downloads render inside the methods band, so a report with '
            f'downloads holds exactly one methods section, and this one holds '
            f'{bands}'
        )
    return items


class Context:
    """What every section renders with: the whole report, the theme, the
    glossary and the downloads. page.py builds one of these for each report,
    before the first section renders, and hands the same object to every
    section module. A module that needs a report-wide value reads it here
    rather than through a new argument of its own."""

    def __init__(self, data, theme):
        self.data = data
        self.theme = theme
        self.terms, self.anchors = glossary_terms(data)
        self.downloads = downloads_for(data)

    def term(self, name, where=''):
        """The control that shows one glossary term with its definition. The
        inline parser calls this for each {term} it reads, with the name alone,
        so `where` names the field only when the caller states it."""
        if name not in self.terms:
            raise ValueError(
                f'{where}no glossary section defines the term {name!r}'
            )
        module = REGISTRY.get('glossary')
        if module is None:
            raise ValueError(
                f'{where}the kit has no glossary section type yet, so the term '
                f'{name!r} cannot show its definition'
            )
        return module.term_control(name, self.terms[name], where,
                                   self.anchors[name])


def render_sections(data, theme):
    """Validate and build every <section>, plus the contents-nav links.
    Returns (list of <section> HTML strings, list of nav <a> HTML strings)."""
    context = Context(data, theme)
    # notes.py holds each note against the references the renderer emitted, so
    # the record starts empty for every report the process builds.
    inline.forget()
    sections, nav, ids = [], [], {"main", "top"}
    for position, section in enumerate(data['sections'], 1):
        sid = text(section, 'id', f'section {position}: ')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', sid):
            raise ValueError(
                f'section {position}: id must be a lowercase slug that starts with a '
                f'letter and holds letters, digits and hyphens: {sid!r}'
            )
        # The kit builds the id of a tab and a panel from the id of the
        # section they are in. Two hyphens in a row is the separator it uses
        # for them, so an author's id can never take the name of a generated
        # one.
        if '--' in sid:
            raise ValueError(
                f'section {position}: id cannot hold two hyphens in a row, because '
                f'the kit uses "--" in the ids it generates: {sid!r}'
            )
        if sid in ids:
            raise ValueError(
                f'section {position}: id is already taken, and "main" and "top" are '
                f'reserved: {sid!r}'
            )
        ids.add(sid)
        where = f'section "{sid}": '
        kind = text(section, 'type', where)
        module = REGISTRY.get(kind)
        if module is None:
            raise ValueError(f'{where}unknown section type: {kind!r}')
        label = optional_text(section, 'label', where)
        # A type that renders no heading gets no heading to throw away.
        heading_html = ''
        if module.TITLE_REQUIRED:
            title_text = text(section, 'title', where)
            if not title_text.strip():
                raise ValueError(
                    f'{where}title cannot be empty: a {kind} section renders a heading '
                    f'and a contents link'
                )
            nav.append(f'<a href="#{sid}">{esc(title_text)}</a>')
            heading_html = heading(label, title_text, sid,
                                   heading_id=f'{sid}{inline.SPLIT}title')
        body, attrs = module.render(section, heading_html, where, context)
        # notes.py renders the sidenotes and the footnotes of every section
        # type, so one family owns them and no section module writes them.
        sections.append(
            f'<section id="{sid}" class="section section-{kind}"{attrs}>\n{body}\n'
            f'{notes.render(section, sid, where, context)}</section>'
        )
    if not sections:
        raise ValueError('A report needs at least one section')
    return sections, nav


def render_meta(title, desc, canonical, social):
    """<meta>/OG/Twitter tags for <head>."""
    meta_tags = [
        f'<meta name="description" content="{desc}">',
        f'<link rel="canonical" href="{canonical}">',
    ]
    for key, value in (
        ('og:title', title),
        ('og:description', desc),
        ('og:type', 'article'),
        ('og:url', canonical),
        ('og:image', social),
        ('og:image:width', '1200'),
        ('og:image:height', '630'),
    ):
        meta_tags.append(f'<meta property="{key}" content="{value}">')
    for key, value in (
        ('twitter:card', 'summary_large_image'),
        ('twitter:title', title),
        ('twitter:description', desc),
        ('twitter:image', social),
    ):
        meta_tags.append(f'<meta name="{key}" content="{value}">')
    return '\n'.join(meta_tags)


def render_styles_and_scripts(root_vars, assets_url, font_block=''):
    """Either inline the joined stylesheet and script, or point at a hosted
    copy of them. The join is the same one package.py writes to report.css and
    report.js, so the two exports can never carry different code.

    The font block goes after the stylesheet, because it declares the same font
    tokens the stylesheet declares and the preset the report named is the one
    the page has to read in. It is an empty string for the system preset, which
    embeds nothing."""
    styles = f'<style>:root{{{root_vars}}}{assets.stylesheet()}</style>{font_block}'
    scripts = f'<script>{assets.script()}</script>'
    if not assets_url:
        return styles, scripts
    parts = urlsplit(assets_url)
    if parts.query or parts.fragment:
        raise ValueError('The asset base URL must not have a query or fragment')
    base = assets_url.rstrip('/')
    styles = (
        f'<style>:root{{{root_vars}}}</style>'
        f'<link rel="stylesheet" href="{url(base + "/report.css")}">'
        f'{font_block}'
    )
    scripts = f'<script defer src="{url(base + "/report.js")}"></script>'
    return styles, scripts


# The header carries no more than this many links of its own. Three plain links
# beside the contents control still fit on a 390px header; a fourth would push
# the control off the edge.
HEADER_LINKS = 3


# A header link is a page beside this one, so it may be a relative path. The
# pattern is a plain relative file path with an optional fragment: no scheme,
# no host, and nothing that could carry a colon into an href. A page in a
# subfolder links up with "../", which the examples index needs.
HEADER_HREF = re.compile(r'^[A-Za-z0-9_\-./]+(?:#[A-Za-z0-9_\-]+)?$')


def header_href(value, where):
    """The address of one header link. The guide and the examples index sit
    beside the report on the same host, and the ZIP export sits in a folder with
    no host at all, so a relative path is the useful form here. An absolute
    HTTP(S) URL still passes, for a report that is published on its own."""
    check_text(value, 'url', where)
    if value.lower().startswith(('http://', 'https://')):
        return url(value, 'url', where)
    if value.startswith('//') or not HEADER_HREF.fullmatch(value):
        raise ValueError(
            f'{where}url must be an absolute HTTP(S) URL or a plain relative '
            f'path beside this page, such as guide.html: {value}'
        )
    return esc(value)


def read_header_links(data):
    """The links the header shows beside the contents control, from the report's
    own JSON. A report that names none keeps the header it had.

    The kit cannot guess where a guide or an index sits: a hosted sample links
    them one way and a page inside examples/ links them another. So the report
    states them, and the build checks every url before it ships one."""
    if 'header_links' not in data or data['header_links'] is None:
        return []
    items = data['header_links']
    if not isinstance(items, list) or not items:
        raise ValueError(
            'header_links must be a list of one to '
            f'{HEADER_LINKS} objects, each with a label and a url'
        )
    if len(items) > HEADER_LINKS:
        raise ValueError(
            f'header_links holds {len(items)} links, and the header carries '
            f'{HEADER_LINKS} or fewer: the rest belong in the footer'
        )
    read = []
    for index, item in enumerate(items, 1):
        where = f'header_links item {index}: '
        if not isinstance(item, dict):
            raise ValueError(f'{where}a header link holds a label and a url')
        read.append((text(item, 'label', where),
                     header_href(field(item, 'url', where), where)))
    return read


def brand_markup(organization, href='#top'):
    """The mark and the organization at the left of every header. The examples
    index reads it too, so the showcase carries one brand and not two."""
    return (
        f'<a class="brand" href="{esc(href)}">'
        '<span class="brand-mark" aria-hidden="true">ccm</span>'
        f'<span class="brand-name">{esc(organization)}</span>'
        '</a>'
    )


def links_markup(links):
    """The report's own links, as plain links in the label face. A button here
    would say the same thing louder than the report's own title."""
    return ''.join(
        f'<a class="header-link" href="{href}">{esc(label)}</a>'
        for label, href in links
    )


def panel_links_markup(links):
    """The same links inside the contents panel. Below 560px the header has room
    for the brand and its two controls and nothing else, so the panel carries
    them there. One copy is hidden at every width, so a reader never meets the
    same link twice and Tab never stops on it twice."""
    return ''.join(
        f'<a class="panel-link" href="{href}">{esc(label)}</a>'
        for label, href in links
    )


def render_header(organization, nav_links, links=()):
    brand = brand_markup(organization)
    # The icon carries the control at narrow widths, where the label is hidden
    # and report.js keeps aria-label in step with the state.
    motion_icon = (
        '<svg class="motion-icon" viewBox="0 0 12 12" width="12" height="12"'
        ' aria-hidden="true" fill="currentColor">'
        '<rect class="icon-pause" x="2" y="1" width="3" height="10"/>'
        '<rect class="icon-pause" x="7" y="1" width="3" height="10"/>'
        '<path class="icon-play" d="M3 1 10.5 6 3 11Z"/>'
        '</svg>'
    )
    motion_button = (
        '<button type="button" class="control motion-button" hidden'
        ' aria-pressed="false" aria-label="Pause motion">'
        f'{motion_icon}<span class="motion-label">Pause motion</span></button>'
    )
    # The state is drawn, not typed: a "+" in a pseudo-element is read aloud as
    # the word "plus" after the label the summary carries.
    contents_icon = (
        '<svg class="contents-icon" viewBox="0 0 12 12" width="12" height="12"'
        ' aria-hidden="true" fill="currentColor">'
        '<rect y="5" width="12" height="1"/>'
        '<rect class="icon-cross" x="5" width="1" height="12"/>'
        '</svg>'
    )
    contents_widget = (
        '<details class="contents">\n'
        f'<summary><span>Contents</span>{contents_icon}</summary>\n'
        f'<nav aria-label="Report contents">{nav_links}'
        f'{panel_links_markup(links)}</nav>\n'
        '</details>'
    )
    # The links come before the controls, so Tab reaches the guide and the
    # examples on the way to the contents panel.
    site_links = links_markup(links)
    header_actions = (
        f'<div class="header-actions screen-only">{site_links}'
        f'{motion_button}{contents_widget}</div>'
    )
    # The title of the section the reader is in. report.js fills it. The
    # contents panel states the same thing with aria-current, so this copy is
    # for the eye alone and a screen reader is not told twice on every scroll.
    section_slot = '<span class="header-section screen-only" aria-hidden="true"></span>'
    progress = (
        '<div class="reading-progress screen-only" role="progressbar"'
        ' aria-label="Reading progress" aria-valuemin="0" aria-valuemax="100"'
        ' aria-valuenow="0"></div>'
    )
    # The class says the header carries a contents panel. Below 560px the panel
    # is where the report's own links go, and the guide and the examples index,
    # which have no panel, keep theirs in the header at every width.
    return (
        f'<header class="site-header with-contents">{brand}{section_slot}{header_actions}\n'
        f'{progress}\n'
        '</header>'
    )


def cover_seed(data):
    """The seed of this report's cover drawing. The url comes first, because no
    two reports share one; the title is the fallback for a report that states
    no url yet. Two reports in one theme now open on two drawings."""
    return seed_from(data.get('url'), data.get('title'))


def render_hero(data, theme, title, desc, download):
    """Three horizontal bands: masthead, headline beside the art, footnotes."""
    hero_art = (
        '<figure class="hero-art">\n'
        f'{artwork("hero", theme, seed=cover_seed(data))}\n'
        f'<figcaption>{esc(text(data, "hero_caption"))}</figcaption>\n'
        '</figure>'
    )
    # endmatter.py owns the byline, so the reading time sits beside it rather
    # than inside it, and the group puts the two on one line at the right.
    reading_time = (
        f'<span class="reading-time">{reading_minutes(data)} minute read</span>'
    )
    hero_top = (
        '<div class="hero-top">'
        f'<span class="eyebrow">{esc(text(data, "series"))}</span>'
        f'<div class="byline-group">{endmatter.byline(data)}{reading_time}</div>'
        '</div>'
    )
    primary_link = (
        f'<a class="button primary" href="#{first_reading_id(data)}">Begin reading '
        '<span aria-hidden="true">↓</span></a>'
    )
    hero_actions = f'<div class="hero-actions screen-only">{primary_link}{download}</div>'
    hero_copy = (
        '<div class="hero-copy">'
        f'<h1>{title}</h1>\n'
        f'<p class="standfirst">{desc}</p>\n'
        f'{hero_actions}\n'
        '</div>'
    )
    hero_main = f'<div class="hero-main">\n{hero_art}\n{hero_copy}\n</div>'
    # A lone footnote's own class tells the CSS which gutter it belongs at:
    # a tagline stays at the left it already renders at, a cue moves to the
    # right one it names.
    footnote_classes = {'tagline': 'tagline', 'scroll_cue': 'scroll-cue'}
    footnotes = ''.join(
        f'<span class="{footnote_classes[key]}">{esc(optional_text(data, key))}</span>'
        for key in ('tagline', 'scroll_cue') if key in data and data[key] is not None
    )
    hero_bottom = f'<div class="hero-bottom screen-only">{footnotes}</div>' if footnotes else ''
    return (
        '<section class="hero" id="top">\n'
        f'{hero_top}\n'
        f'{hero_main}\n'
        f'{hero_bottom}\n'
        '</section>'
    )


def render_footer(data, canonical, forms):
    """A colophon: who published it and when on the left, where it lives and
    what the reader can do with it on the right. Paper keeps the plain citation
    under it, because a printed page has no clipboard."""
    colophon = (
        f'<span class="colophon-org">{esc(text(data, "organization"))}</span>'
        f'<span>{esc(text(data, "series"))}</span>'
        f'<span>{esc(text(data, "date"))}</span>'
    )
    # Every control is hidden until its script shows it, so a reader with no
    # script is never offered a button that cannot do anything.
    controls = (
        '<button type="button" class="control copy-link-button screen-only" hidden>Copy link</button>'
        '<button type="button" class="control cite-button screen-only" hidden>Cite</button>'
        '<button type="button" class="control print-button screen-only" hidden>Print / save PDF</button>'
    )
    links = (
        f'<a class="footer-url" href="{canonical}">{canonical}</a>'
        '<a class="back-to-top screen-only" href="#top">Back to top ↑</a>'
        f'<div class="footer-controls">{controls}</div>'
    )
    return (
        '<footer class="site-footer">'
        f'<div class="colophon">{colophon}</div>'
        f'<div class="colophon-links">{links}</div>'
        f'<p class="print-citation">{esc(forms["plain"])}</p>'
        '</footer>'
    )


def render_cite_form(name, label, action, body, code=False):
    """One citation in the dialog, with the button that copies it. The button
    states which form it copies, because three buttons named "Copy" tell a
    screen reader nothing about which one it landed on."""
    tag = 'pre class="cite-code"' if code else 'p class="cite-text"'
    close = 'pre' if code else 'p'
    return (
        f'<div class="cite-form">\n'
        f'<h3>{esc(label)}</h3>\n'
        f'<{tag} id="cite-{name}">{esc(body)}</{close}>\n'
        f'<button type="button" class="control cite-copy" data-cite="cite-{name}"'
        f' hidden>{esc(action)}</button>\n'
        f'</div>'
    )


def render_cite(forms):
    """The cite dialog and the toast both share controls use. Both ship in the
    markup and both stay out of sight until a script opens them: a <dialog>
    with no open attribute and a popover are hidden by the browser itself."""
    dialog = (
        '<dialog class="cite-dialog screen-only" aria-labelledby="cite-title">\n'
        '<div class="cite-head">'
        '<h2 id="cite-title" tabindex="-1" autofocus>Cite this report</h2>'
        '<button type="button" class="control cite-close">Close</button>'
        '</div>\n'
        + render_cite_form('plain', 'Plain text', 'Copy the plain text',
                           forms['plain']) + '\n'
        + render_cite_form('apa', 'APA', 'Copy the APA citation',
                           forms['apa']) + '\n'
        + render_cite_form('bibtex', 'BibTeX', 'Copy the BibTeX entry',
                           forms['bibtex'], code=True) + '\n'
        '</dialog>'
    )
    toast = '<div class="toast screen-only" popover="manual" role="status" hidden></div>'
    return f'{dialog}\n{toast}'


def render(data, assets_url=None):
    theme, root_vars = theme_tokens(data)
    # The preset and the layout are read before the first section renders, so a
    # report that names either one wrong stops the build rather than shipping a
    # page in the wrong faces.
    _, preset = fonts.preset(data)
    layout = page_layout(data)

    sections, nav = render_sections(data, theme)

    title = esc(text(data, 'title'))
    desc = esc(text(data, 'subtitle'))
    canonical = url(field(data, 'url'), 'url')
    social = url(field(data, 'image_url'), 'image_url')
    meta = render_meta(title, desc, canonical, social)

    styles, scripts = render_styles_and_scripts(
        root_vars, assets_url, fonts.style_block(preset, assets_url))

    notice_parts = []
    if 'notice' in data and data['notice'] is not None:
        notice_parts.append(f'<span>{esc(optional_text(data, "notice"))}</span>')
    if 'template_url' in data and data['template_url'] is not None:
        notice_parts.append(
            f'<a href="{url(data["template_url"], "template_url")}">Use this template</a>'
        )
    notice = f'<aside class="notice">{"".join(notice_parts)}</aside>' if notice_parts else ''

    download = ''
    if 'pdf_url' in data and data['pdf_url'] is not None:
        download = (
            f'<a class="button" href="{url(data["pdf_url"], "pdf_url")}">Read the paper '
            '<span aria-hidden="true">↗</span></a>'
        )

    head_html = (
        '<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{title} | {esc(text(data, "organization"))}</title>\n'
        f'{meta}\n'
        f'<meta name="theme-color" content="{esc(theme["paper"])}">\n'
        f'{favicon_link(assets_url, theme)}\n'
        f'{styles}\n'
        '</head>'
    )

    skip_link = '<a class="skip-link screen-only" href="#main">Skip to report</a>'
    header_html = render_header(text(data, 'organization'), ''.join(nav),
                                read_header_links(data))
    hero_html = render_hero(data, theme, title, desc, download)

    main_children = [hero_html]
    if notice:
        main_children.append(notice)
    main_children.append('\n'.join(sections))
    blocks = endmatter.render(data)
    if blocks:
        main_children.append(blocks)
    # tabindex="-1" is what makes the skip link move focus rather than only
    # scroll: <main> is not focusable on its own, so focus would stay on the
    # body and the next Tab would start again from the top of the page.
    main_html = '<main id="main" tabindex="-1">\n' + '\n'.join(main_children) + '\n</main>'

    forms = cite.citations(data)
    footer_html = render_footer(data, canonical, forms)
    cite_html = render_cite(forms)

    return (
        '<!doctype html>\n'
        f'<html lang="{language(data)}">\n'
        f'{head_html}\n'
        f'<body data-layout="{layout}">'
        f'{skip_link}{header_html}\n'
        f'{main_html}\n'
        f'{footer_html}\n'
        f'{cite_html}\n'
        f'{scripts}'
        '</body>'
        '</html>'
    )
