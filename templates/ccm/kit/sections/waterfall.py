"""A scroll-driven unit chart with a local data editor."""
import copy
import json
import math
import re
from pathlib import Path

from ..text import esc, field, optional_text, text

NAME = 'waterfall'
TITLE_REQUIRED = True
ORDER = 21
FIELDS = '<code>label</code>, <code>title</code>, <code>dataset</code> (title, unit, totalSquares, status, source, caveat, groups)'
SPECIMEN = {'summary': 'Equal squares fall into place as the reader scrolls, from small groups to the whole '
            'population.',
 'use_when': 'Use it for non-overlapping groups with a known total. Readers can edit the data and '
             'export their own chart.',
 'json': {'type': 'waterfall',
          'id': 'waterfall-specimen',
          'label': 'A matter of scale',
          'title': 'See the whole audience.',
          'dataset': {'version': 1,
                      'title': 'Program reach, in perspective',
                      'unit': 'people',
                      'totalSquares': 2500,
                      'status': 'Fictional example · not a measured population',
                      'source': 'Entirely invented figures for demonstrating the storytelling '
                                'template. These are not results from a real program, '
                                'organization, or community.',
                      'caveat': 'The four example groups are mutually exclusive and total 50,000 '
                                'people. Replace all figures and narration with your own validated '
                                'data before publication. “Not yet reached” should only be used '
                                'when the full target population is known.',
                      'summaryHeadline': 'The audience you know\nis not the whole audience.',
                      'groups': [{'id': 'regular',
                                  'label': 'Regular participants',
                                  'shortLabel': 'Regular',
                                  'value': 420,
                                  'color': '#ec3864',
                                  'headline': 'The people\nyou know best.',
                                  'description': 'The regulars: {value} {unit}. They are highly '
                                                 'visible, but occupy only {tiles} squares in this '
                                                 'fictional population.'},
                                 {'id': 'occasional',
                                  'label': 'Occasional participants',
                                  'shortLabel': 'Occasional',
                                  'value': 1680,
                                  'color': '#e7bb27',
                                  'headline': 'A wider\ncircle.',
                                  'description': 'Add the occasional participants. The picture '
                                                 'grows, but the people actively involved are '
                                                 'still a small group.'},
                                 {'id': 'aware',
                                  'label': 'Reached, not participating',
                                  'shortLabel': 'Reached',
                                  'value': 7900,
                                  'color': '#00b982',
                                  'headline': 'Awareness\nis not engagement.',
                                  'description': 'These people have been reached by the fictional '
                                                 'program but do not participate. A different '
                                                 'relationship, and a bigger band.'},
                                 {'id': 'unreached',
                                  'label': 'Not yet reached',
                                  'shortLabel': 'Not reached',
                                  'value': 40000,
                                  'color': '#3e4740',
                                  'headline': 'Beyond\nthe usual circle.',
                                  'description': 'The largest group: people the fictional program '
                                                 'has not yet reached. This is what a '
                                                 'participant-only view would leave out.'}]}}}


def dataset(value, where):
    """Keep the build and the browser within the same numeric and text limits."""
    if not isinstance(value, dict):
        raise ValueError(f'{where}dataset must be an object')
    data = copy.deepcopy(value)
    for key in ('title', 'unit', 'status', 'source', 'caveat'):
        value = text(data, key, where)
        if key in ('title', 'unit') and not value.strip():
            raise ValueError(f'{where}{key} must not be blank')
    data['summaryHeadline'] = optional_text(data, 'summaryHeadline', where)
    if isinstance(data.get('totalSquares'), bool) or data.get('totalSquares') not in (1000, 2500, 5000):
        raise ValueError(f'{where}totalSquares must be 1000, 2500 or 5000')
    groups = data.get('groups')
    if not isinstance(groups, list) or not 2 <= len(groups) <= 8:
        raise ValueError(f'{where}groups must hold two to eight groups')
    for i, group in enumerate(groups):
        if not isinstance(group, dict):
            raise ValueError(f'{where}each group must be an object')
        if not text(group, 'label', where).strip():
            raise ValueError(f'{where}group label must not be blank')
        amount = group.get('value')
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not 0 <= amount <= 9007199254740991 or not math.isfinite(amount):
            raise ValueError(f'{where}group values must be finite non-negative safe numbers')
        if not isinstance(group.get('color'), str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', group['color']):
            raise ValueError(f'{where}group colors need six hexadecimal digits')
        group['id'] = f'group-{i}'
        for key in ('shortLabel', 'headline', 'description'):
            value = optional_text(group, key, where)
            default = ('{value} {unit}, or {share} of the total. Each square has the same weight.'
                       if key == 'description' else group['label'])
            if key == 'description':
                group[key] = default if group.get(key) is None else value
            else:
                group[key] = value if value.strip() else default
    total = sum(group['value'] for group in groups)
    if not 0 < total <= 9007199254740991:
        raise ValueError(f'{where}the total must be positive and within the safe numeric range')
    return data


def render(section, heading_html, where, context):
    data = dataset(field(section, 'dataset', where), where)
    rows = ''.join(f'<tr><td>{esc(g["label"])}</td><td>{g["value"]:,} {esc(data["unit"])}</td></tr>' for g in data['groups'])
    fallback = (f'<div class="waterfall-fallback"><p>{esc(data["status"])}</p>'
                f'<table><caption>{esc(data["title"])}</caption><thead><tr><th>Group</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table>'
                f'<p>{esc(data["source"])}</p><p>{esc(data["caveat"])}</p></div>')
    source = (Path(__file__).parent.parent / 'waterfall.html').read_text(encoding='utf-8')
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    # The inert template scopes all IDs and styles when the browser attaches it.
    return (f'<div class="section-heading">{heading_html}</div>'
            f'<div class="waterfall-host">{fallback}<template>{source}'
            f'<script type="application/json" id="scale-data">{payload}</script>'
            '</template></div>'), ''
