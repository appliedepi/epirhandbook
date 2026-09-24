#!/usr/bin/env bash
# Read-only: report how far the translated chapters have drifted from the English.
# Runs every structural check the 2026-09 fix pass used. Changes nothing. Exit 1 on any drift.
# Usage: checks/check-sync.sh                 (checks 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 14 and 15; about two minutes)
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
if not os.path.exists('languages.yml'):
    # No language list, so this check cannot run. Stop with one line, not a traceback.
    print('   languages.yml is missing; check 9 below reports it')
    sys.exit(1)
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
if not os.path.exists('languages.yml'):
    # No language list, so this check cannot run. Stop with one line, not a traceback.
    print('   languages.yml is missing; check 9 below reports it')
    sys.exit(0)
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
print('   suspect spans by language:', dict(sorted(per.items())), 'total', sum(per.values()), '(baseline 2026-09-17: 357, all judged placeholders or noise. Was 356 from 2026-09-02; the extra one is es/transition_to_r.qmd, where bare R code was wrapped in backticks to stop two dollars pairing as TeX maths)')
PY
echo "== 5. Internal links: every internal link in the 416 declared chapter files"
python3 "$here/check-links.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-links.py" | sed 's/^/   /'; rc=1; }
echo "== 7. Data folder: R chunks that execute and name the repository's data/ folder"
python3 "$here/check-data-reads.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-data-reads.py" | sed 's/^/   /'; rc=1; }
echo "== 9. Layout: the language folders, the project files, the manifest and the aliases"
python3 - <<'LAYOUT' || rc=1
"""Report every way the language folders drift from the layout the repository declares.

`languages.yml` is the language list. `content/<main>/_quarto.yaml` is the reference project
file, and its flattened `book.chapters` list is the stem list. A YAML parser reads both. It
also reads `docker-images.yml` and the front matter of the chapter files.

The loader is `yaml.BaseLoader`. It shares the scanner and the parser of `yaml.safe_load`, and
it makes every scalar a string. `yaml.safe_load` reads an unquoted `no` as False, so the
Norwegian code `no` would not survive it. A file that does not parse gives a DRIFT line.

A duplicate key is a parse failure here. PyYAML keeps the last value of a duplicate key and
says nothing, so a stale second `chapters:` list would hide the first. The regular expressions
this code replaced read the first one and reported it.
"""
import glob, os, sys

try:
    import yaml
except ImportError:
    print('   layout: not measured. Check 9 reads YAML with PyYAML, and python3 cannot import '
          'yaml. Install it with `sudo apt-get install -y python3-yaml`.')
    sys.exit(1)

DRIFT = []

# What parse() returns for text that does not parse. It cannot be None, because an empty
# document parses to None.
FAILED = object()


def drift(where, why):
    DRIFT.append((where, why))


class Loader(yaml.BaseLoader):
    """yaml.BaseLoader that refuses a mapping with a duplicate key."""

    def construct_mapping(self, node, deep=False):
        # Compare the key nodes by tag and text, before construction. A merge key `<<` is
        # skipped, because SafeLoader expands it later. Comparing constructed values would
        # also treat the keys `true` and `1` as one key.
        seen = set()
        for k, _ in node.value:
            if not isinstance(k, yaml.ScalarNode) or k.tag == 'tag:yaml.org,2002:merge':
                continue
            if (k.tag, k.value) in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, 'duplicate key %s' % k.value, k.start_mark)
            seen.add((k.tag, k.value))
        return super().construct_mapping(node, deep)


def parse(text, where, first=1, part='the file'):
    """The YAML document in text, or FAILED after one DRIFT line that names where.

    first is the file line that holds the first line of text, so the message names a line of
    the file.
    """
    try:
        return yaml.load(text, Loader=Loader)
    except yaml.YAMLError as e:
        mark = getattr(e, 'problem_mark', None)
        at = ', line %d' % (mark.line + first) if mark else ''
        why = getattr(e, 'problem', None) or str(e)
        drift(where, '%s does not parse as YAML%s: %s' % (part, at, ' '.join(why.split())))
        return FAILED


def read(path):
    """One YAML file, parsed, or FAILED."""
    return parse(open(path, encoding='utf-8').read(), path)


def stop():
    """Print the summary line and the DRIFT lines so far, and stop.

    Without the language list there is nothing to compare against.
    """
    print('   layout: 0 languages, 0 stems, 0 aliases, drifted: %d' % len(DRIFT))
    for where, why in DRIFT:
        print('   DRIFT %s %s' % (where, why))
    sys.exit(1)


def front_matter(text):
    """The YAML block between the first `---` line and the next `---` line, or ''."""
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---':
        return ''
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return '\n'.join(lines[1:i])
    return ''


def aliases_of(path, text):
    """The items of the front matter's top-level `aliases:` key, in file order, or FAILED.

    Only the front matter is parsed, so a list below it is not an alias. A list under another
    key is not one either. Quarto reads `aliases` as a list of strings, so a scalar gives none.
    """
    doc = parse(front_matter(text), path, 2, 'the front matter')
    if doc is FAILED:
        return FAILED
    found = doc.get('aliases') if isinstance(doc, dict) else None
    return [a for a in found if isinstance(a, str)] if isinstance(found, list) else []


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


def project(doc):
    """One parsed project file: (stems in order, part count, lang, book title).

    The stems are the `.qmd` entries of `book.chapters`, in file order. A part is a mapping
    with a `part:` key, and its own `chapters:` list gives its stems in its place. A part may
    name a `.qmd` file instead of a title. Quarto renders that file as the part page, so it is
    a stem too, and it comes before the part's chapters.
    """
    doc = doc if isinstance(doc, dict) else {}
    book = doc.get('book') if isinstance(doc.get('book'), dict) else {}
    stems, parts = [], 0

    def walk(items):
        nonlocal parts
        for x in items if isinstance(items, list) else []:
            if isinstance(x, str) and x.endswith('.qmd'):
                stems.append(x[:-len('.qmd')])
            elif isinstance(x, dict):
                if 'part' in x:
                    parts += 1
                    if isinstance(x['part'], str) and x['part'].endswith('.qmd'):
                        stems.append(x['part'][:-len('.qmd')])
                walk(x.get('chapters'))

    walk(book.get('chapters'))
    lang, title = doc.get('lang'), book.get('title')
    return (stems, parts,
            lang if isinstance(lang, str) else '',
            title if isinstance(title, str) else '')


# Each project file is parsed once. A file that does not parse gives its DRIFT line once, and
# None here, so every comparison that needs the file is skipped.
PROJECTS = {}


def project_of(path):
    if path not in PROJECTS:
        doc = read(path)
        PROJECTS[path] = None if doc is FAILED else project(doc)
    return PROJECTS[path]


def first_line(item):
    """The first key and value of one manifest item, in the form `- stem: index`."""
    if isinstance(item, dict) and item:
        k, v = next(iter(item.items()))
        return ('- %s: %s' % (k, v if isinstance(v, str) else '')).rstrip()
    return ('- %s' % (item if isinstance(item, str) else '')).rstrip()


if not os.path.exists('languages.yml'):
    # The language list is the one declaration of which languages ship. Without it there is
    # nothing to compare against, so report the file and stop with one line, not a traceback.
    drift('languages.yml', 'the language list is missing')
    stop()

langs = read('languages.yml')
if langs is FAILED:
    stop()
langs = langs if isinstance(langs, dict) else {}
main = langs.get('main')
if not isinstance(main, str) or not main:
    drift('languages.yml', 'declares no main: language, and that language names the reference '
          'project file')
    stop()

codes, titles, tags = [], {}, {}
entries = langs.get('languages')
for e in entries if isinstance(entries, list) else []:
    code = e.get('code') if isinstance(e, dict) else None
    if not isinstance(code, str) or not code:
        continue
    codes.append(code)
    # The BCP-47 tag this language declares. It is not the folder code for two of the
    # eight: content/jp/ is Japanese, tag ja, and content/vn/ is Vietnamese, tag vi.
    if isinstance(e.get('lang'), str):
        tags[code] = e['lang']
    if isinstance(e.get('title'), str):
        titles[code] = e['title']

ref_file = 'content/%s/_quarto.yaml' % main
ref = project_of(ref_file) if os.path.exists(ref_file) else None
if ref is not None:
    ref_stems, ref_parts = ref[0], ref[1]
else:
    # Drift 1 below reports a missing file, and parse() reports a file that does not parse.
    # Every check that needs the reference is skipped, and the rest of check 9 still runs.
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
    if not os.path.exists(f) or project_of(f) is None:
        continue
    stems, parts, lang, title = project_of(f)
    if ref_stems is not None and stems != ref_stems:
        drift(f, 'chapter list differs from content/%s/_quarto.yaml' % main)
    if ref_parts is not None and parts != ref_parts:
        drift(f, 'part count %d, content/%s/_quarto.yaml has %d' % (parts, main, ref_parts))
    if lang != tags.get(c, ''):
        drift(f, 'lang %s, languages.yml declares the tag %s'
              % (lang or '(none)', tags.get(c) or '(none)'))
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
# A key counts only when it holds text, so an empty stem: names no chapter.
manifest = FAILED
if not os.path.exists('docker-images.yml'):
    drift('docker-images.yml', 'the chapter image manifest is missing')
elif ref_stems is not None:
    manifest = read('docker-images.yml')
if manifest is not FAILED:
    items = manifest.get('chapters') if isinstance(manifest, dict) else None
    rows = []
    for n, item in enumerate(items if isinstance(items, list) else [], 1):
        keys = ({k: v for k, v in item.items() if isinstance(v, str) and v}
                if isinstance(item, dict) else {})
        for k in ('stem', 'image'):
            if k not in keys:
                drift('docker-images.yml',
                      'chapters: item %d, %s, carries no %s: key' % (n, first_line(item), k))
        if 'stem' in keys:
            rows.append(keys['stem'])
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
        found = aliases_of(f, open(f, encoding='utf-8').read())
        if found is FAILED:
            continue
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
echo "== 10. Unparsed links: markdown that looks like a link but that pandoc never parsed"
python3 "$here/check-unparsed-links.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-unparsed-links.py" | sed 's/^/   /'; rc=1; }
echo "== 11. Image names: every images/ file a chapter names, commented lines included"
python3 "$here/check-image-names.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-image-names.py" | sed 's/^/   /'; rc=1; }
echo "== 15. Landing page: every hero string resolves and is distinct, every language is wired"
python3 "$here/check-landing-strings.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-landing-strings.py" | sed 's/^/   /'; rc=1; }
echo "== 14. Image versions in prose: every 2.<n> the docs name is one the repository uses"
python3 "$here/check-image-version-refs.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-image-version-refs.py" | sed 's/^/   /'; rc=1; }
echo "== 12. Clean failure: every check names a missing input instead of crashing on it"
python3 "$here/check-clean-failure.py" --summary | sed 's/^/   /' \
  || { python3 "$here/check-clean-failure.py" | sed 's/^/   /'; rc=1; }
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
