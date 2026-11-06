"""Join the stylesheet and the script from their partials.

styles/ and scripts/ hold one file for each part of the page. The join reads
them in sorted name order, so a component adds a file and edits no list. The
number in front of a name puts the file in its band. The component band is
order free, because each component partial holds only its own selectors; the
numbers inside it keep the join in the order the one stylesheet shipped in
before the split.
"""
import re

from . import ROOT

STYLES = ROOT / 'styles'
SCRIPTS = ROOT / 'scripts'
# One IIFE holds every script partial, so the partials share one scope and no
# name reaches the page.
SCRIPT_HEAD = (
    "/* Scroll selects a visual state. It never captures wheel or touch input.\n"
    "   The drawing's mark count and every seeded angle come from the markup that\n"
    "   build.py wrote, so nothing here repeats a number that lives in build.py. */\n"
    "(() => {\n"
)
SCRIPT_TAIL = '})();\n'
# The default export writes both assets into the page, so a partial that holds
# the closing tag of its own element would end that element early. The HTML
# parser ends a raw text element on "</style" or "</script" in any letter case,
# and on whitespace or "/" in front of the ">", so the check reads all of those
# forms rather than the one lowercase string.
CLOSERS = {'.css': re.compile(r'</style(?=[\s/>])', re.IGNORECASE),
           '.js': re.compile(r'</script(?=[\s/>])', re.IGNORECASE)}
# A newline holds the partials apart. Without it a partial that ends in a "//"
# comment with no last newline reads the first line of the next partial as part
# of the comment.
SEPARATOR = '\n'


def partials(folder, suffix):
    """Every partial in one folder, in sorted name order."""
    return sorted(folder.glob(f'*{suffix}'), key=lambda path: path.name)


def read(path):
    text = path.read_text(encoding='utf-8')
    found = CLOSERS[path.suffix].search(text)
    if found:
        raise ValueError(
            f'{path.name} holds the string {found.group(0)}, which ends the '
            f'element the default export embeds it in'
        )
    return text


def stylesheet():
    """report.css: every styles/*.css partial, in name order."""
    return SEPARATOR.join(read(path) for path in partials(STYLES, '.css'))


def script():
    """report.js: every scripts/*.js partial, in name order, in one IIFE."""
    body = SEPARATOR.join(read(path) for path in partials(SCRIPTS, '.js'))
    return SCRIPT_HEAD + body + SEPARATOR + SCRIPT_TAIL
