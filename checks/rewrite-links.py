#!/usr/bin/env python3
"""Rewrite every dead internal link that check-links.py reports.

The mapping table `checks/link-map.tsv` names the target of every dead link. Its
columns are `old_id`, `stem`, `anchor` and `note`. `old_id` is the link target exactly as
check-links.py reports it. `stem` is the chapter that holds the content today. `anchor` is
an in-page id that every language version of that chapter defines, or an empty field.

A rewritten link points at a file, never at a bare fragment. Every declared file sits in
`content/<lang>/`, so a link target is `<stem>.qmd` in the same folder, `index.qmd` included.
The `anchor` field, where the table gives one, follows as `#anchor`.

Pandoc percent-encodes a link target, so the reported `old_id` and the source text can
differ. The script looks for both forms.

The script rewrites prose only. It skips a fenced code block and an HTML comment, because
pandoc reads no link there.

A link inside a grid-table row changes the length of that row. The row's borders would then
miss the `+` of the separators, and pandoc would drop the table: that is how English `basics`
lost its tables on 2026-09-08. So the script re-pads the cell it edits to the width of its
column, measured as pandoc measures it (`checks/gridtables.py`). When the new text does not
fit the column, the script names the row and writes nothing. For each file and each target it counts the links it finds in
prose. The count must equal the number of findings for that pair. On any other count the
script reports the pair and writes nothing.

Deterministic. No model, no network, no third-party package.

Usage: python3 checks/rewrite-links.py [--dry-run]
"""
import re, subprocess, sys
from pathlib import Path
from urllib.parse import unquote

from gridtables import corners, tables, width

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
COMMENT = re.compile(r'<!--.*?-->', re.S)
DEAD = re.compile(r'^DEAD (\S+):(\d+)\??\s+(\S+)\s+\(')
USAGE = 'Usage: python3 checks/rewrite-links.py [--dry-run]'

args = sys.argv[1:]
for a in args:
    if a != '--dry-run':
        sys.exit('unknown argument %s. %s' % (a, USAGE))
dry = '--dry-run' in args


def table():
    """The mapping table: {old_id: (stem, anchor)}."""
    rows = (HERE / 'link-map.tsv').read_text(encoding='utf-8').rstrip('\n').split('\n')
    if rows[0].split('\t') != ['old_id', 'stem', 'anchor', 'note']:
        sys.exit('link-map.tsv needs the header old_id, stem, anchor, note')
    out = {}
    for r in rows[1:]:
        c = r.split('\t')
        out[c[0]] = (c[1], c[2])
    return out


def findings():
    """Run check-links.py and count its findings: {(file, target): occurrences}."""
    r = subprocess.run([sys.executable, str(HERE / 'check-links.py')],
                       capture_output=True, text=True)
    if r.returncode not in (0, 1):
        sys.exit('check-links.py failed: %s' % r.stderr.strip())
    out = {}
    for l in r.stdout.split('\n'):
        m = DEAD.match(l)
        if m:
            k = (m.group(1), m.group(3))
            out[k] = out.get(k, 0) + 1
    return out


def code(text):
    """Every character range pandoc does not read as prose.

    CommonMark bounds a fence line, and this function follows the same rule as
    check-links.py. An indent of four spaces or more is code, so such a line opens no
    fence and closes none. A closing fence carries the opening character, and it is as
    long as the opener or longer. An HTML comment holds no link either, so its range
    joins the list.
    """
    spans, pos, fence = [], 0, None
    for line in text.split('\n'):
        start, pos = pos, pos + len(line) + 1
        m = FENCE.match(line)
        shut = m is None or len(m.group(1)) > 3
        if fence is None:
            if not shut:
                fence = m.group(2)
                spans.append((start, pos))
            continue
        spans.append((start, pos))
        if not shut and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) \
                and not m.group(3).strip():
            fence = None
    spans += [(m.start(), m.end()) for m in COMMENT.finditer(text)]
    return spans


def prose(text):
    """One flag per character: True where pandoc reads prose."""
    ok = [True] * len(text)
    for a, b in code(text):
        for i in range(a, min(b, len(text))):
            ok[i] = False
    return ok


def link(stem, anchor):
    """The new link target, relative to the file that holds the link.

    Every declared file sits in `content/<lang>/`, and every chapter of one language sits in
    that one folder. So the target is `<stem>.qmd`, with no folder part and no language part.
    """
    return '%s.qmd' % stem + ('#' + anchor if anchor else '')


def rewrite(path, wanted, tbl):
    """The new text of one file, and the number of links it rewrites."""
    text = (ROOT / path).read_text(encoding='utf-8')
    ok = prose(text)
    edits = []
    for target, n in sorted(wanted.items()):
        stem, anchor = tbl[target]
        new = '](%s)' % link(stem, anchor)
        found = []
        for form in dict.fromkeys([unquote(target), target]):
            old = '](%s)' % form
            i = text.find(old)
            while i >= 0:
                if ok[i]:
                    found.append((i, i + len(old), new))
                i = text.find(old, i + 1)
        if len(found) != n:
            sys.exit('%s %s: %d links in prose, %d findings' % (path, target, len(found), n))
        edits += found
    edits.sort()
    out, at = [], 0
    for a, b, new in edits:
        out.append(text[at:a])
        out.append(new)
        at = b
    out.append(text[at:])
    return repad(path, text, ''.join(out), edits), len(edits)


def repad(path, old, new, edits):
    """The new text with every edited grid-table row padded back to its borders.

    An edit keeps the line count, so a row keeps its line number. The old row is aligned, so
    its cells sit between the + columns of the table. Each edit is applied inside its cell,
    and the cell is padded to the width of its column again. A cell whose text no longer
    fits, or an edit that crosses a border, stops the run.
    """
    old_lines, new_lines = old.split('\n'), new.split('\n')
    if len(old_lines) != len(new_lines):
        sys.exit('%s: a link rewrite changed the line count' % path)
    starts, pos = [], 0
    for line in old_lines:
        starts.append(pos)
        pos += len(line) + 1
    by_line = {}
    for a, b, text in edits:
        k = old.count('\n', 0, a)
        by_line.setdefault(k, []).append((a - starts[k], b - starts[k], text))
    for first, last, indent in tables(old_lines):
        want = corners(old_lines[first][indent:])
        for k in range(first, last + 1):
            row = old_lines[k][indent:]
            if k in by_line and row.startswith('|'):
                shifted = [(a - indent, b - indent, t) for a, b, t in by_line[k]]
                new_lines[k] = old_lines[k][:indent] + pad_row(path, k, row, want, shifted)
    return '\n'.join(new_lines)


def pad_row(path, k, row, want, line_edits):
    """One edited grid-table row: each edit applied inside its cell, each cell padded."""
    # The character index of each border: the | at each + column of the table.
    bounds, col = [], 0
    for i, ch in enumerate(row):
        if col in want and ch == '|':
            bounds.append(i)
        col += width(ch)
    if len(bounds) != len(want):
        sys.exit('%s:%d: this grid-table row is not aligned to its separators, so the script '
                 'cannot tell its cells apart. Run checks/check-grid-tables.py.' % (path, k + 1))
    out = '|'
    for c in range(len(bounds) - 1):
        lo, hi = bounds[c] + 1, bounds[c + 1]
        cell, shift = row[lo:hi], 0
        for a, b, text in sorted(line_edits):
            if lo <= a and b <= hi:
                cell = cell[:a - lo + shift] + text + cell[b - lo + shift:]
                shift += len(text) - (b - a)
            elif a < hi and b > lo:
                sys.exit('%s:%d: a rewritten link crosses a border of this grid-table row. '
                         'Rewrite it by hand.' % (path, k + 1))
        room = want[c + 1] - want[c] - 1
        text = cell.rstrip()
        if width(text) > room:
            sys.exit('%s:%d: the rewritten link makes cell %d of this grid-table row wider '
                     'than its column. Widen the column by hand, then run the script again.'
                     % (path, k + 1, c + 1))
        out += text + ' ' * (room - width(text)) + '|'
    return out + row[bounds[-1] + 1:]


tbl = table()
found = findings()
absent = sorted({t for _, t in found if t not in tbl})
if absent:
    sys.exit('link-map.tsv has no row for: %s' % ', '.join(absent))

per = {}
for (f, t), n in found.items():
    per.setdefault(f, {})[t] = n

fresh, total = {}, 0
for f in sorted(per):
    fresh[f], n = rewrite(f, per[f], tbl)
    total += n

if not dry:
    for f, text in fresh.items():
        (ROOT / f).write_text(text, encoding='utf-8', newline='')

print('files %d, links rewritten %d%s' % (len(fresh), total, ' (dry run)' if dry else ''))
