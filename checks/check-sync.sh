#!/usr/bin/env bash
# Read-only: report how far the translated chapters have drifted from the English.
# Runs every structural check the 2026-09 fix pass used. Changes nothing. Exit 1 on any drift.
# Usage: checks/check-sync.sh                 (checks 1, 2, 3, 4, 5 and 7; about half a minute)
#        checks/check-sync.sh --base <sha>    (also checks 6 and 8, over the files changed since <sha>)
#        checks/check-sync.sh --render        (also checks 6 and 8, over the whole tree, ~20 min)
# Checks 6 and 8 are the render gate and the chunk parse gate. Both need a base commit. Without
# --base and without --render they do not run, and the result line says
# "IN SYNC (checks 6 and 8 not run)".
# Exit 0 on IN SYNC, 1 on DRIFT, 2 when --base names something that is not a commit.
# Every check writes its full output to /tmp/check-sync/, and the lines below come from those files.
# Full description of each check, expected output and remedies: checks/README.md
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
cd "$here/.."
rc=0
log=/tmp/check-sync; rm -rf "$log"; mkdir -p "$log"
base=''
while [ $# -gt 0 ]; do
  case "$1" in
    --render) base=$(git rev-list --max-parents=0 HEAD | tail -1) ;;
    --base)
      shift
      base="${1:-}"
      if [ -z "$base" ]; then echo "--base needs a commit" >&2; exit 2; fi
      ;;
    *) echo "unknown argument $1. Usage: checks/check-sync.sh [--base <sha> | --render]" >&2; exit 2 ;;
  esac
  shift
done
if [ -n "$base" ] && ! git cat-file -e "$base^{commit}" 2>/dev/null; then
  echo "checks/check-sync.sh: '$base' is not a commit in this repository." >&2
  echo "== result: CANNOT RUN, checks 6 and 8 need a base commit that exists"
  exit 2
fi
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
python3 "$here/sync-anchors.py" --dry-run > "$log/anchors.txt" 2>&1 || rc=1
grep -E '^dead|^headings' "$log/anchors.txt" | sed 's/^/   /'
grep -q '^headings changed 0,' "$log/anchors.txt" || rc=1
grep -q '^dead English-id links before: 0$' "$log/anchors.txt" || rc=1
grep -q '^dead English-id links after: 0$' "$log/anchors.txt" || rc=1
echo "== 3. Chunks: aligned chunks whose code differs from the English (sync-chunks.py --dry-run)"
python3 "$here/sync-chunks.py" --dry-run > "$log/chunks.txt" 2>&1 || rc=1
grep -E '^files|^SKIPPED' "$log/chunks.txt" | sed 's/^/   /'
grep -q '^files [0-9]*, changed 0,' "$log/chunks.txt" || rc=1
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
print('   suspect spans by language:', dict(sorted(per.items())), 'total', sum(per.values()), '(baseline 2026-09-02, after the inline and mirror passes and the return of the GIS chapter: 356, all judged placeholders or noise)')
PY
echo "== 5. Internal links: every internal link in the 400 declared chapter files"
python3 "$here/check-links.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-links.py" | sed 's/^/   /'; rc=1; }
echo "== 7. Data folder: R chunks that execute and name the repository's data/ folder"
python3 "$here/check-data-reads.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-data-reads.py" | sed 's/^/   /'; rc=1; }
if [ -n "$base" ]; then
  echo "== 6. Render gate on every translated chapter changed since $base (quarto render --no-execute)"
  "$here/render-gate.sh" "$base" HEAD > "$log/render.txt" 2>&1 || rc=1
  grep -E '^(rendered:|skipped inline-r)|FAIL' "$log/render.txt" | sed 's/^/   /'
  grep -E '^FAIL-LOG' "$log/render.txt" | sed 's/^/   /'
  echo "   full output: $log/render.txt, per file: /tmp/render-gate/SUMMARY.tsv"
  echo "== 8. Chunk parse gate on every translated chapter changed since $base"
  python3 "$here/chunk-parse-gate.py" "$base" HEAD > "$log/parse.txt" 2>&1 || rc=1
  grep -E '^files |^chapters/|after-fail' "$log/parse.txt" | sed 's/^/   /'
  echo "   full output: $log/parse.txt"
else
  echo "== 6. Render gate: NOT RUN. It needs a base commit."
  echo "== 8. Chunk parse gate: NOT RUN. It needs a base commit."
  echo "== NOTE: checks 6 and 8 did not run. Run checks/check-sync.sh --base <sha> for the files"
  echo "         changed since <sha>, or checks/check-sync.sh --render for the whole tree."
fi
if [ -n "$base" ]; then note=''; else note=' (checks 6 and 8 not run)'; fi
echo "== result: $([ $rc -eq 0 ] && echo "IN SYNC$note" || echo 'DRIFT, see above')"
exit $rc
