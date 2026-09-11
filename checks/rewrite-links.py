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
pandoc reads no link there. For each file and each target it counts the links it finds in
prose. The count must equal the number of findings for that pair. On any other count the
script reports the pair and writes nothing.

Deterministic. No model, no network, no third-party package.

Usage: python3 checks/rewrite-links.py [--dry-run]
"""
import re, subprocess, sys
from pathlib import Path
from urllib.parse import unquote

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
    return ''.join(out), len(edits)


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
