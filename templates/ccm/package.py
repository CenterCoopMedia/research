#!/usr/bin/env python3
"""Rebuild the demonstration exports, the joined assets and the source ZIP."""
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from kit import assets  # noqa: E402

FILES = ('README.md', 'DESIGN.md', 'build.py', 'package.py', 'report.json',
         'report.css', 'report.js', 'index.html', 'starter.html',
         'guide.template.html', 'guide.html', 'favicon.svg')
# The kit, the stylesheet partials, the script partials and the font files ship
# whole: build.py reads all four, so a download without them cannot build, and a
# download without fonts/ cannot embed the preset a report names.
FOLDERS = ('kit', 'styles', 'scripts', 'fonts')
# The showcase pages. Each is built from its own JSON file after the sample, so
# an edit to a token or to a section module cannot leave a stale example page
# beside the kit. EXAMPLES is the folder; the names are the JSON files in it.
EXAMPLES = ROOT / 'examples'
EXAMPLE_NAMES = ('report', 'paper', 'story', 'brief', 'explainer', 'waterfall')
# What each shipped folder has to hold. A folder that is gone, or that holds no
# file of its own kind, makes the join of the partials an empty string, so the
# check runs before package.py writes anything.
FOLDER_SUFFIX = {'kit': '.py', 'styles': '.css', 'scripts': '.js',
                 'fonts': '.woff2'}
# Every source file and every folder beside build.py is either shipped or
# named here on purpose, so adding one and forgetting the list stops the build
# instead of shipping a download that cannot be worked from.
KEPT_BACK = {
    'og-image.png': 'every published report needs its own social image',
    'examples': (
        'the showcase pages are what the kit makes, not a part of it: they '
        'carry invented content, they are built from their own JSON files '
        'after the sample, and the folder holds seven PNG social images and '
        'two placeholder PDFs the ZIP has no way to carry, because it writes '
        'every entry as text'
    ),
}
SOURCES = ('.py', '.html', '.css', '.js', '.json', '.md', '.svg', '.png',
           '.woff2', '.txt')
# A font file is bytes. Every other shipped file is read as text and written
# back as UTF-8, so a checkout with Windows line endings makes the same archive;
# a woff2 read that way would be corrupted, so it is copied byte for byte.
BINARY = ('.woff2',)
# Python writes these beside the modules it imports. They are machine files,
# not source, so they never ship.
SKIP = '__pycache__'


def check_missing():
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    missing += [name for name in FOLDERS if not (ROOT / name).is_dir()]
    if missing:
        raise SystemExit(f'package.py cannot ship files that are not there: {", ".join(missing)}')


def check_folders():
    """Every shipped folder, before the first write. write_assets() joins the
    partials it finds, so a missing styles/ or scripts/ folder would write an
    empty report.css or report.js and rebuild both exports without them."""
    for name in FOLDERS:
        folder = ROOT / name
        suffix = FOLDER_SUFFIX[name]
        if not folder.is_dir():
            raise SystemExit(
                f'package.py cannot build without the {name}/ folder beside it, '
                f'and it is not there. Nothing was written.'
            )
        if not any(path.suffix == suffix for path in folder.rglob('*') if path.is_file()):
            raise SystemExit(
                f'package.py found no {suffix} file in the {name}/ folder, so '
                f'the build would write an empty file. Nothing was written.'
            )


def check_unlisted():
    """Every file and every folder beside build.py is accounted for. A folder
    counts as well as a file, because a new folder of sources that nothing
    lists would go missing from the ZIP without a word."""
    unlisted = sorted(
        path.name for path in ROOT.iterdir()
        if (path.is_file() and path.suffix in SOURCES) or (path.is_dir() and path.name != SKIP)
        if path.name not in FILES and path.name not in FOLDERS
        and path.name not in KEPT_BACK
    )
    if unlisted:
        raise SystemExit(
            f'package.py does not know about {", ".join(unlisted)}. '
            'Add each name to FILES or FOLDERS to ship it, or to KEPT_BACK '
            'with the reason.'
        )


def write_assets():
    """report.css and report.js are the join of the partials. They are written
    here and committed, because the hosted export links them and the ZIP ships
    them; a test holds the committed pair against a fresh join."""
    (ROOT / 'report.css').write_text(assets.stylesheet(), encoding='utf-8', newline='\n')
    (ROOT / 'report.js').write_text(assets.script(), encoding='utf-8', newline='\n')


def build_examples():
    """The showcase, rebuilt from its own sources after the sample. The files
    the pages offer for download come first, because a page that names one has
    to have it beside it; the drawings the story points at come next, because
    the page embeds nothing and reads them off the disk beside it; the index
    comes last, because it refuses to build a link to a page that is not
    there.

    The ZIP leaves the folder out on purpose, so a reader who unpacks the
    download and runs this file has no examples to build. That is the normal
    case for them, not an error, so the run says what it skipped and carries
    on to the archive.

    The social images are not built here. They need a browser, and the kit
    builds with the standard library alone, so examples/social.py is run by
    hand and its PNGs are committed.
    """
    if not EXAMPLES.is_dir():
        print('No examples/ folder beside package.py, so the showcase pages '
              'were not built. The ZIP does not carry them.')
        return
    subprocess.run([sys.executable, str(EXAMPLES / 'downloads.py')], check=True)
    subprocess.run([sys.executable, str(EXAMPLES / 'pictures.py')], check=True)
    for name in EXAMPLE_NAMES:
        subprocess.run([sys.executable, str(ROOT / 'build.py'),
                        str(EXAMPLES / f'{name}.json'), '--output',
                        str(EXAMPLES / f'{name}.html')], check=True)
    subprocess.run([sys.executable, str(EXAMPLES / 'index.py')], check=True)


def shipped():
    """Every path the ZIP carries, in one fixed order."""
    for name in FILES:
        yield name
    for folder in FOLDERS:
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and SKIP not in path.parts:
                yield path.relative_to(ROOT).as_posix()


def main():
    # The folders it has to have come first, so a renamed styles/ is reported
    # as the missing folder it is rather than as an unlisted one.
    check_folders()
    check_unlisted()
    write_assets()
    subprocess.run([sys.executable, str(ROOT / 'build.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'build.py'), '--output',
                    str(ROOT / 'starter.html'), '--assets-url',
                    'https://jamditis.com/ccm-report-template'], check=True)
    # The guide is generated too, from the same theme and the same drawing, so
    # the kit's front door can never show a palette the kit no longer makes.
    subprocess.run([sys.executable, str(ROOT / 'build.py'), '--guide',
                    '--output', str(ROOT / 'guide.html')], check=True)
    build_examples()
    check_missing()
    with zipfile.ZipFile(ROOT / 'template.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in shipped():
            entry = zipfile.ZipInfo('CCM-report-template/' + name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            path = ROOT / name
            if path.suffix in BINARY:
                archive.writestr(entry, path.read_bytes())
            else:
                # Text is read as text and written back as UTF-8, so a checkout
                # with Windows line endings makes the same archive.
                archive.writestr(entry, path.read_text(encoding='utf-8').encode('utf-8'))
    print('Built template.zip')


if __name__ == '__main__':
    main()
