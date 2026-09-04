#!/usr/bin/env bash
# Read-only: report how far the translated chapters have drifted from the English.
# Runs every structural check the 2026-09 fix pass used. Changes nothing. Exit 1 on any drift.
# Usage: modernization/check-sync.sh            (structure, anchors, chunks, inline spans)
#        modernization/check-sync.sh --render   (also the render gate on every translated chapter, ~20 min)
# Full description of each check, expected output and remedies: modernization/SYNC-CHECKS.md
set -uo pipefail
cd "$(dirname "$0")/.."
rc=0
echo "== 1. Structure: every declared chapter in every language, same chunk count, same heading sequence"
python3 - <<'PY' || rc=1
import re, os, sys
decl = re.findall(r'^\s*-\s*chapters/([A-Za-z0-9_]+)\.qmd', open('_quarto.yml').read(), re.M)
langs = re.search(r"languages:\s*\[([^\]]*)\]", open('_quarto.yml').read()).group(1)
langs = [x.strip().strip("'\"") for x in langs.split(',') if x.strip()]
F = re.compile(r'^\s*`{3,}\s*\{r[ ,}]', re.M)
def prose(t):
    out, fence = [], None
    for l in t.split('\n'):
        m = re.match(r'^\s*(`{3,})', l)
        if fence is None and m: fence = m.group(1); continue
        if fence is not None and re.match(r'^\s*' + fence + r'\s*$', l): fence = None; continue
        if fence is None: out.append(l)
    return '\n'.join(out)
def heads(t): return [len(m.group(1)) for m in re.finditer(r'^(#{1,6})\s', prose(t), re.M)]
bad = []; n = 0
for st in decl:
    en = open('chapters/%s.qmd' % st, encoding='utf-8').read()
    for l in langs:
        p = 'chapters/%s.%s.qmd' % (st, l); n += 1
        if not os.path.exists(p): bad.append((p, 'missing')); continue
        t = open(p, encoding='utf-8').read()
        if len(F.findall(t)) != len(F.findall(en)): bad.append((p, 'chunks %d vs %d' % (len(F.findall(t)), len(F.findall(en)))))
        elif heads(t) != heads(en): bad.append((p, 'headings %d vs %d or levels differ' % (len(heads(t)), len(heads(en)))))
print('   %d chapters x %d languages = %d pairs; drifted: %d' % (len(decl), len(langs), n, len(bad)))
for p, why in bad: print('   DRIFT', p, why)
sys.exit(1 if bad else 0)
PY
echo "== 2. Anchors: headings whose anchor id differs from the English, and dead English-style links"
python3 modernization/sync-anchors.py --dry-run | grep -E '^dead|^headings' | sed 's/^/   /'
python3 modernization/sync-anchors.py --dry-run | grep -q '^headings changed 0,' || rc=1
echo "== 3. Chunks: aligned chunks whose code differs from the English (sync-chunks.py --dry-run)"
python3 modernization/sync-chunks.py --dry-run | grep -E '^files|^SKIPPED' | sed 's/^/   /'
python3 modernization/sync-chunks.py --dry-run | grep -q '^files [0-9]*, changed 0,' || rc=1
echo "== 4. Inline code spans in translated prose that occur nowhere in the English chapter (informational)"
python3 - <<'PY'
import re, glob, os, collections
def strip(t): return re.sub(r'^\s*`{3,}\s*\{r.*?^\s*`{3,}\s*$', '', t, flags=re.S | re.M)
SPAN = re.compile(r'(?<!`)`([^`\n]+)`(?!`)')
per = collections.Counter()
for tr in sorted(glob.glob('chapters/*.[a-z][a-z].qmd')):
    en = re.sub(r'\.[a-z]{2}\.qmd$', '.qmd', tr)
    if not os.path.exists(en) or tr.endswith('.de.qmd'): continue
    te = open(en, encoding='utf-8').read(); tt = open(tr, encoding='utf-8').read()
    es = set(SPAN.findall(strip(te)))
    for s in SPAN.findall(strip(tt)):
        s2 = s.strip()
        if not (s2 in es or s2 in te or s2.strip('r ').strip() in te): per[tr[-6:-4]] += 1
print('   suspect spans by language:', dict(sorted(per.items())), 'total', sum(per.values()), '(baseline 2026-09-02, after the inline and mirror passes: 355, all judged placeholders or noise)')
PY
if [ "${1:-}" = "--render" ]; then
  echo "== 5. Render gate on every translated chapter (quarto render --no-execute)"
  base=$(git rev-list --max-parents=0 HEAD | tail -1)
  modernization/render-gate.sh "$base" HEAD | tail -3 | sed 's/^/   /' || rc=1
fi
echo "== result: $([ $rc -eq 0 ] && echo 'IN SYNC' || echo 'DRIFT, see above')"
exit $rc
