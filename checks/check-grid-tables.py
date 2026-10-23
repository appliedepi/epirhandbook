#!/usr/bin/env python3
"""Report every grid-table line whose borders do not line up, in every declared chapter.

Check 19. In a pandoc grid table every `|` of a content row sits under a `+` of the
separator lines. Where one does not, pandoc drops the whole table. A header row above a
`+===+` line then becomes a level-1 heading, and Quarto numbers it as a chapter. On
2026-10-02 eight chapters shipped like that: English `basics` showed sections up to 12.1.
A link rewrite that changed `dates.html` to `dates.qmd` had shortened three rows by one
character.

The width of a line is its display width, as pandoc measures it: a wide or fullwidth East
Asian character is two columns. `checks/gridtables.py` holds the rule.

The check also reports a cell that starts with `#`, because pandoc reads it as a heading
inside the table, which Quarto numbers too.

It reads the source, so it needs no render and runs in seconds. It reads a table indented by
up to three spaces, as pandoc does, outside fenced code. It does not model row or column
spans: a table with a spanning cell fails, and none of the declared chapters has one.

The file set is `content/<lang>/<stem>.qmd` for every language in `languages.yml` and every
stem in `content/<main>/_quarto.yaml`.

Exit 1 on any misaligned line, 2 when an input is missing.

Usage: python3 checks/check-grid-tables.py [--summary] [--fixture <dir>]
"""
import os
import sys
from pathlib import Path

from langs import read_languages, read_stems
from gridtables import problems, tables

ROOT = Path(__file__).resolve().parent.parent

args = sys.argv[1:]
known = {'--summary': 0, '--fixture': 1}
i = 0
while i < len(args):
    if args[i] not in known:
        sys.exit('unknown argument %s. Usage: %s' % (args[i], __doc__.strip().split('Usage: ')[1]))
    i += 1 + known[args[i]]


def opt(name):
    return args[args.index(name) + 1] if name in args else None


summary = '--summary' in args
fixture = opt('--fixture')


def declared():
    """Every declared chapter file: [(path relative to root, language)]."""
    main, codes = read_languages(ROOT / 'languages.yml')
    stems = read_stems(ROOT / 'content' / main / '_quarto.yaml')
    return [('content/%s/%s.qmd' % (l, s), l) for l in codes for s in stems], codes


if fixture:
    base = Path(fixture)
    files = [(str(p.relative_to(base)), os.path.basename(os.path.dirname(str(p))))
             for p in sorted(base.glob('*/*.qmd'))]
    langs = list(dict.fromkeys(l for _, l in files))
    if not files:
        sys.exit('check-grid-tables.py --fixture %s: the fixture holds no <lang>/<stem>.qmd '
                 'file, so nothing would be measured.' % fixture)
else:
    base = ROOT
    files, langs = declared()

missing = [f for f, _ in files if not (base / f).exists()]
for f in missing:
    print('MISSING %s' % f, file=sys.stderr)
files = [(f, l) for f, l in files if f not in missing]
if not files:
    sys.exit('check-grid-tables.py: no declared chapter file exists under %s/content, so '
             'nothing would be measured.' % base)

rows, counted = [], {}
for f, lang in files:
    lines = (base / f).read_text(encoding='utf-8').split('\n')
    for first, last, indent in tables(lines):
        counted[lang] = counted.get(lang, 0) + 1
        for k, why in problems(lines, first, last, indent):
            rows.append((f, lang, k + 1, why))

if summary:
    for l in langs:
        n = sum(1 for _, x in files if x == l)
        print('lang %s: files %d, grid tables %d, misaligned lines %d'
              % (l, n, counted.get(l, 0), sum(1 for r in rows if r[1] == l)))
    print('misaligned lines %d' % len(rows))
else:
    for f, lang, n, why in rows:
        print('GRID %s:%d %s' % (f, n, why))

sys.exit(1 if rows or missing else 0)
