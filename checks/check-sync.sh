#!/usr/bin/env bash
# Read-only: report how far the translated chapters have drifted from the English.
# Runs every structural check the 2026-09 fix pass used. Changes nothing. Exit 1 on any drift.
# Usage: checks/check-sync.sh                 (checks 1, 2, 3, 4, 5, 7 and 9; about a minute)
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
y = open('languages.yml', encoding='utf-8').read()
main = re.search(r'^main:\s*([A-Za-z0-9_]+)', y, re.M).group(1)
langs = [l for l in re.findall(r'^\s*-\s*code:\s*([A-Za-z0-9_]+)', y, re.M) if l != main]
ref = 'content/%s/_quarto.yaml' % main
if not os.path.exists(ref):
    # No stem list, so this check cannot run. Stop with one line, not a traceback.
    print('   %s is missing; check 9 below reports it' % ref)
    sys.exit(1)
decl = re.findall(r'^\s*-\s*([A-Za-z0-9_]+)\.qmd',
                  open(ref, encoding='utf-8').read(), re.M)
# The landing page is written per language, so it is not held to the English structure.
decl = [s for s in decl if s != 'index']
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
    en = open('content/%s/%s.qmd' % (main, st), encoding='utf-8').read()
    for l in langs:
        p = 'content/%s/%s.qmd' % (l, st); n += 1
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
import re, os, sys, collections
def strip(t): return re.sub(r'^\s*`{3,}\s*\{r.*?^\s*`{3,}\s*$', '', t, flags=re.S | re.M)
SPAN = re.compile(r'(?<!`)`([^`\n]+)`(?!`)')
y = open('languages.yml', encoding='utf-8').read()
main = re.search(r'^main:\s*([A-Za-z0-9_]+)', y, re.M).group(1)
langs = [l for l in re.findall(r'^\s*-\s*code:\s*([A-Za-z0-9_]+)', y, re.M) if l != main]
ref = 'content/%s/_quarto.yaml' % main
if not os.path.exists(ref):
    # No stem list, so this check cannot run. Stop with one line, not a traceback.
    print('   %s is missing; check 9 below reports it' % ref)
    sys.exit(0)
decl = re.findall(r'^\s*-\s*([A-Za-z0-9_]+)\.qmd',
                  open(ref, encoding='utf-8').read(), re.M)
# The landing page is written per language, so its spans are not measured against the English.
decl = [s for s in decl if s != 'index']
per = collections.Counter()
# The declared set, language by language and stem by stem. A file outside it is not measured
# here; check 9 below reports every file the layout does not declare.
for lang in langs:
    for st in decl:
        tr = 'content/%s/%s.qmd' % (lang, st)
        en = 'content/%s/%s.qmd' % (main, st)
        if not os.path.exists(en): print('   %s is missing; check 9 below reports it' % en); continue
        if not os.path.exists(tr): print('   %s is missing; check 9 below reports it' % tr); continue
        te = open(en, encoding='utf-8').read(); tt = open(tr, encoding='utf-8').read()
        es = set(SPAN.findall(strip(te)))
        for span in SPAN.findall(strip(tt)):
            s2 = span.strip()
            if not (s2 in es or s2 in te or s2.strip('r ').strip() in te): per[lang] += 1
print('   suspect spans by language:', dict(sorted(per.items())), 'total', sum(per.values()), '(baseline 2026-09-02, after the inline and mirror passes and the return of the GIS chapter: 356, all judged placeholders or noise)')
PY
echo "== 5. Internal links: every internal link in the 400 declared chapter files"
python3 "$here/check-links.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-links.py" | sed 's/^/   /'; rc=1; }
echo "== 7. Data folder: R chunks that execute and name the repository's data/ folder"
python3 "$here/check-data-reads.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-data-reads.py" | sed 's/^/   /'; rc=1; }
echo "== 9. Layout: the language folders, the project files, the manifest and the aliases"
python3 - <<'LAYOUT' || rc=1
"""Report every way the language folders drift from the layout the repository declares.

`languages.yml` is the language list. `content/<main>/_quarto.yaml` is the reference project
file, and its flattened chapter list is the stem list. Regular expressions read both, because
the translation-sync runner carries no yaml module.
"""
import glob, os, re, sys

DRIFT = []


def drift(where, why):
    DRIFT.append((where, why))


def front_matter(text):
    """The YAML block between the first `---` line and the next `---` line, or ''."""
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---':
        return ''
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return '\n'.join(lines[1:i])
    return ''


def aliases_of(text):
    """The items of the front matter's top-level `aliases:` key, in file order.

    A list item under another key is not an alias. A list below the front matter is not one
    either. The first line that is not an indented list item ends the key.
    """
    found, inside = [], False
    for line in front_matter(text).split('\n'):
        if re.match(r'^aliases:\s*$', line):
            inside = True
            continue
        if not inside:
            continue
        m = re.match(r'^\s+-\s+(\S+)\s*$', line)
        if m:
            found.append(m.group(1).strip('"\''))
        else:
            inside = False
    return found


def wanted(stem, code, main):
    """The aliases one chapter file must carry.

    An alias keeps the chapter's old `/new_pages/` URL alive, so it spells the stem the way
    that page spelled it. Only `transition_to_r` differs from its own stem: the old page was
    `transition_to_R`. The English chapter shipped under both spellings and carries both.
    """
    old = 'transition_to_R' if stem == 'transition_to_r' else stem
    if code != main:
        return ['/new_pages/%s.%s.html' % (old, code)]
    if stem == 'transition_to_r':
        return ['/new_pages/transition_to_R.html', '/new_pages/transition_to_r.html']
    return ['/new_pages/%s.html' % old]


def project(path):
    """One project file: (stems in order, part count, lang, book title)."""
    t = open(path, encoding='utf-8').read()
    m = re.search(r'^  chapters:\s*$', t, re.M)
    body = t[m.end():] if m else ''
    stems = re.findall(r'^\s*-\s*([A-Za-z0-9_]+)\.qmd\s*$', body, re.M)
    parts = len(re.findall(r'^\s*-\s*part:', body, re.M))
    lang = re.search(r'^lang:\s*(\S+)', t, re.M)
    b = re.search(r'^book:\s*$', t, re.M)
    title = re.search(r'^  title:\s*(.*)$', t[b.end():], re.M) if b else None
    return (stems, parts,
            lang.group(1) if lang else '',
            title.group(1).strip().strip('"\'') if title else '')


if not os.path.exists('languages.yml'):
    # The language list is the one declaration of which languages ship. Without it there is
    # nothing to compare against, so report the file and stop with one line, not a traceback.
    print('   layout: 0 languages, 0 stems, 0 aliases, drifted: 1')
    print('   DRIFT languages.yml the language list is missing')
    sys.exit(1)

y = open('languages.yml', encoding='utf-8').read()
main = re.search(r'^main:\s*([A-Za-z0-9_]+)', y, re.M).group(1)
codes, titles, cur = [], {}, None
for line in y.split('\n'):
    if re.match(r'^\s*#', line):
        continue
    m = re.match(r'^\s*-\s*code:\s*([A-Za-z0-9_]+)', line)
    if m:
        cur = m.group(1)
        codes.append(cur)
        continue
    m = re.match(r'^\s+title:\s*(.*)$', line)
    if m and cur:
        titles[cur] = m.group(1).strip().strip('"\'')

ref_file = 'content/%s/_quarto.yaml' % main
if os.path.exists(ref_file):
    ref_stems, ref_parts, _, _ = project(ref_file)
else:
    # Drift 1 below reports the missing file. Every check that needs the reference is
    # skipped, and the rest of check 9 still runs.
    ref_stems, ref_parts = None, None

# 1. A declared language with no project file.
for c in codes:
    if not os.path.exists('content/%s/_quarto.yaml' % c):
        drift('content/%s/_quarto.yaml' % c,
              'languages.yml declares %s and this file is missing' % c)

# 2. A folder of chapters for a language languages.yml does not declare.
for d in sorted(glob.glob('content/*/')):
    code = d.rstrip('/').split('/')[1]
    if code not in codes and glob.glob(d + '*.qmd'):
        drift(d.rstrip('/'), 'languages.yml declares no code %s' % code)

# 3 and 4. Each project file against the reference and against languages.yml.
for c in codes:
    f = 'content/%s/_quarto.yaml' % c
    if not os.path.exists(f):
        continue
    stems, parts, lang, title = project(f)
    if ref_stems is not None and stems != ref_stems:
        drift(f, 'chapter list differs from content/%s/_quarto.yaml' % main)
    if ref_parts is not None and parts != ref_parts:
        drift(f, 'part count %d, content/%s/_quarto.yaml has %d' % (parts, main, ref_parts))
    if lang != c:
        drift(f, 'lang %s, folder %s' % (lang or '(none)', c))
    if title != titles.get(c, ''):
        drift(f, 'book.title %s, languages.yml says %s'
              % (title or '(none)', titles.get(c, '(none)')))

# 5. Every language folder holds a file for every declared stem, and the landing page.
if ref_stems is not None:
    for c in codes:
        for s in list(dict.fromkeys(ref_stems + ['index'])):
            p = 'content/%s/%s.qmd' % (c, s)
            if not os.path.exists(p):
                drift(p, 'the layout declares %s.qmd in every language folder' % s)

# 6. The manifest holds exactly one row per declared stem, and no row for anything else.
# Every row carries both keys: stem: names the chapter, image: names the image CI renders it in.
if not os.path.exists('docker-images.yml'):
    drift('docker-images.yml', 'the chapter image manifest is missing')
elif ref_stems is not None:
    manifest = open('docker-images.yml', encoding='utf-8').read()
    rows = re.findall(r'^\s*-\s*stem:\s*([A-Za-z0-9_]+)', manifest, re.M)
    # One entry per list item under chapters:, as [the item's first line, its keys]. The row
    # regex above sees a stem: key and nothing else, so a row that carries no stem: at all is
    # invisible to it. Read the keys of every item instead.
    cm = re.search(r'^chapters:\s*$', manifest, re.M)
    items = []
    for line in (manifest[cm.end():] if cm else '').split('\n'):
        if not line.strip() or re.match(r'^\s*#', line):
            continue
        if re.match(r'^\S', line):
            break  # a new top-level key ends the chapters: list
        if re.match(r'^\s*-\s', line):
            items.append([line.strip(), []])
        k = re.match(r'^\s*(?:-\s*)?([A-Za-z0-9_]+)\s*:', line)
        if k and items:
            items[-1][1].append(k.group(1))
    for n, (first, keys) in enumerate(items, 1):
        for k in ('stem', 'image'):
            if k not in keys:
                drift('docker-images.yml',
                      'chapters: item %d, %s, carries no %s: key' % (n, first, k))
    for s in ref_stems:
        hits = rows.count(s)
        if hits != 1:
            drift('docker-images.yml',
                  'no row for the declared stem %s' % s if hits == 0
                  else '%d rows for the declared stem %s' % (hits, s))
    for s in sorted(set(rows)):
        if s not in ref_stems:
            drift('docker-images.yml', 'row %s is not a declared stem' % s)

# 7. Every .qmd file in a language folder is a declared chapter. Each one carries in its
# front matter the aliases that keep its old /new_pages/ URLs alive. The comparison is
# case-sensitive, because a URL path is case-sensitive.
aliases = 0
for c in codes:
    for f in sorted(glob.glob('content/%s/*.qmd' % c)):
        stem = os.path.basename(f)[:-len('.qmd')]
        if ref_stems is not None and stem != 'index' and stem not in ref_stems:
            drift(f, 'content/%s/_quarto.yaml declares no chapter %s.qmd' % (main, stem))
            continue
        found = aliases_of(open(f, encoding='utf-8').read())
        aliases += len(found)
        if stem == 'index':
            continue
        want = wanted(stem, c, main)
        if sorted(found) != sorted(want):
            drift(f, 'aliases %s, expected %s' % (found or '(none)', want))

print('   layout: %d languages, %d stems, %d aliases, drifted: %d'
      % (len(codes), len(ref_stems or []), aliases, len(DRIFT)))
for where, why in DRIFT:
    print('   DRIFT %s %s' % (where, why))
sys.exit(1 if DRIFT else 0)
LAYOUT
if [ -n "$base" ]; then
  echo "== 6. Render gate on every translated chapter changed since $base (quarto render --no-execute)"
  "$here/render-gate.sh" "$base" HEAD > "$log/render.txt" 2>&1 || rc=1
  grep -E '^(rendered:|skipped inline-r)|FAIL' "$log/render.txt" | grep -v '^FAIL-LOG' | sed 's/^/   /'
  grep -E '^FAIL-LOG' "$log/render.txt" | sed 's/^/   /'
  echo "   full output: $log/render.txt, per file: /tmp/render-gate/SUMMARY.tsv"
  echo "== 8. Chunk parse gate on every translated chapter changed since $base"
  python3 "$here/chunk-parse-gate.py" "$base" HEAD > "$log/parse.txt" 2>&1 || rc=1
  grep -E '^files |^content/|after-fail' "$log/parse.txt" | sed 's/^/   /'
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
