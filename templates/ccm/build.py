#!/usr/bin/env python3
"""Build a self-contained report from JSON with Python's standard library."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
# The kit sits beside this file, so a reader can unpack the ZIP and run the
# build from the folder it makes. The path goes on sys.path first, because a
# tool that loads this file by its path does not put the folder there.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kit.guide import render_guide  # noqa: E402
from kit.page import render  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('content', nargs='?', type=Path, default=ROOT / 'report.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'index.html')
    parser.add_argument('--assets-url', help='Load CSS and JS from this absolute HTTP(S) base URL')
    parser.add_argument('--guide', action='store_true',
                        help='Build the kit guide from guide.template.html instead of a report')
    args = parser.parse_args()
    try:
        content = args.content.read_text(encoding="utf-8")
    except OSError as exc:
        parser.exit(1, f'Cannot read the content file {args.content}: {exc.strerror}\n')
    except UnicodeDecodeError as exc:
        parser.exit(1, f'{args.content} is not valid UTF-8: {exc}\n')
    try:
        data = json.loads(content)
        result = render_guide(data) if args.guide else render(data, args.assets_url)
    except (KeyError, ValueError, TypeError) as exc:
        parser.exit(1, f'Invalid report: {exc}\n')
    except OSError as exc:
        # The partials, guide.template.html and favicon.svg are read while the
        # page is built, so a missing one lands here rather than above.
        parser.exit(1, f'Cannot read a file the build needs: {exc}\n')
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8", newline="\n")
    except OSError as exc:
        parser.exit(1, f'Cannot write {args.output}: {exc.strerror}\n')
    print(f'Built {args.output}')


if __name__ == '__main__':
    main()
