#!/usr/bin/env python3
"""Report every R chunk that executes and names the repository's `data/` folder.

The handbook loads its data with `appliedepidata::get_data()`. Two chapters are different. The
directories chapter and the importing chapter teach file paths, so a reader runs them against
the repository's own `data/` folder. Those two may read `data/`. Nothing may write into it.

The file set is `content/<lang>/<stem>.qmd` for every language in `languages.yml` and every
stem in `content/en/_quarto.yaml`: 400 files.

A chunk executes when its fence options do not set `eval=F` or `eval=FALSE`. The checker strips
the `#` comment from each line of such a chunk, then matches three lexical forms:

- `here("data"`, `here::here("data"`, `file.path("data"`, `fs::path("data"` or `path("data"`
- a string that starts `data/`
- a string that starts `../data/`

A match prints `DATA-READ file:line`. In the directories chapter and the importing chapter it
prints nothing, unless the same line also calls a function that writes. Then it prints
`DATA-WRITE file:line`.

The check is lexical. It reads the source line, and it does not follow a path through a
variable. A chunk that builds the path on one line and reads it on another passes.

Deterministic. No model, no network, no third-party package. Exit 1 on any flagged line.

Usage: python3 checks/check-data-reads.py [--summary] [--fixture <dir>]
"""
import os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The two chapters that teach file paths. Their subject is the repository's own `data/` folder,
# so their chunks name it on purpose and a reader needs that folder to run them. Every other
# chapter loads its data with `appliedepidata::get_data()`, so a `data/` path there is a defect.
PATH_CHAPTERS = ('directories', 'importing')

FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
R_CHUNK = re.compile(r'^\{r[ ,}]')
NO_EVAL = re.compile(r'eval\s*=\s*F(ALSE)?')
DATA = re.compile(r'''(here|here::here|file\.path|fs::path|path)\s*\(\s*["']data["']'''
                  r'''|["']data/|["']\.\./data/''')
WRITE = re.compile(r'\b(export|write[A-Za-z_.]*|save|saveRDS|st_write|file\.copy|file\.create'
                   r'|dir\.create|dir_create|file_create|download\.file|unzip)\s*\(')

args = sys.argv[1:]
summary = '--summary' in args
known = {'--summary': 0, '--fixture': 1}
i = 0
while i < len(args):
    if args[i] not in known:
        sys.exit('unknown argument %s. Usage: %s' % (args[i], __doc__.strip().split('Usage: ')[1]))
    i += 1 + known[args[i]]


def opt(name):
    return args[args.index(name) + 1] if name in args else None


fixture = opt('--fixture')


def languages():
    """The codes `languages.yml` declares, in file order, and the main language.

    The order is the declared one. `main:` names the reference language, and it is a code in
    that list, not a position in it.
    """
    y = (ROOT / 'languages.yml').read_text(encoding='utf-8')
    main = re.search(r'^main:\s*([A-Za-z0-9_]+)', y, re.M).group(1)
    codes = re.findall(r'^\s*-\s*code:\s*([A-Za-z0-9_]+)', y, re.M)
    return codes, main


def declared():
    """Every declared chapter file: [(path relative to root, language)].

    `languages.yml` names the languages. `content/<main>/_quarto.yaml` names the stems, and
    `index` is the first of them.
    """
    langs, main = languages()
    ref = ROOT / 'content' / main / '_quarto.yaml'
    if not ref.exists():
        # Without the reference project file there is no stem list, so this check cannot run.
        # Stop with one line, not a traceback. Check 9 of check-sync.sh reports the file.
        sys.exit('%s: missing. Check 9 of checks/check-sync.sh reports it.' % ref)
    y = ref.read_text(encoding='utf-8')
    stems = re.findall(r'^\s*-\s*([A-Za-z0-9_]+)\.qmd', y, re.M)
    return sorted(('content/%s/%s.qmd' % (l, s), l) for l in langs for s in stems), langs


def language(path):
    """The language of a chapter file: the folder that holds it.

    Every declared file is `content/<lang>/<stem>.qmd`, so the language is the second path
    segment. A fixture drops the `content/` prefix and keeps the language folder.
    """
    return os.path.basename(os.path.dirname(str(path)))


def stem(path):
    """The chapter name, with the extension removed."""
    return os.path.basename(str(path))[:-len('.qmd')]


def executing_chunks(text):
    """Every R chunk that executes: [(line number of its first body line, body lines)].

    CommonMark bounds a fence line, and this function follows it. An indent of four spaces or
    more is code, so such a line opens no fence and closes none. A closing fence carries the
    opening character, and it is as long as the opener or longer.
    """
    out, fence, opts, start, body = [], None, '', 0, []
    for i, l in enumerate(text.split('\n')):
        m = FENCE.match(l)
        code = m is None or len(m.group(1)) > 3
        if fence is None:
            if not code:
                fence, opts, start, body = m.group(2), m.group(3).strip(), i + 2, []
        elif not code and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) \
                and not m.group(3).strip():
            if R_CHUNK.match(opts) and not NO_EVAL.search(opts):
                out.append((start, body))
            fence = None
        else:
            body.append(l)
    return out


def code_part(line):
    """The code before a `#` comment, ignoring a `#` inside a string."""
    out, q = [], None
    for ch in line:
        if q:
            out.append(ch)
            if ch == q: q = None
        elif ch in '"\'':
            q = ch; out.append(ch)
        elif ch == '#':
            break
        else:
            out.append(ch)
    return ''.join(out)


def scan(path, chapter):
    """Every flagged line of one file: [(line number, 'DATA-READ' or 'DATA-WRITE')]."""
    hits = []
    for start, body in executing_chunks(Path(path).read_text(encoding='utf-8')):
        for k, l in enumerate(body):
            c = code_part(l)
            if not DATA.search(c):
                continue
            if chapter in PATH_CHAPTERS:
                if WRITE.search(c):
                    hits.append((start + k, 'DATA-WRITE'))
            else:
                hits.append((start + k, 'DATA-READ'))
    return hits


base = Path(fixture) if fixture else ROOT
if fixture:
    files = [(str(p.relative_to(base)), language(p)) for p in sorted(base.glob('*/*.qmd'))]
    langs = sorted({l for _, l in files})
else:
    files, langs = declared()

missing = [f for f, _ in files if not (base / f).exists()]
for f in missing:
    print('MISSING %s' % f, file=sys.stderr)
files = [(f, l) for f, l in files if f not in missing]

rows = []
for f, lang in files:
    for n, kind in scan(base / f, stem(f)):
        rows.append((f, lang, n, kind))

if summary:
    print('files scanned %d' % len(files))
    for l in langs:
        n = sum(1 for _, x in files if x == l)
        if n:
            print('lang %s: files %d, data-reads %d' % (l, n, sum(1 for r in rows if r[1] == l)))
    print('data-reads %d' % len(rows))
else:
    for f, lang, n, kind in sorted(rows):
        print('%s %s:%d' % (kind, f, n))

sys.exit(1 if rows or missing else 0)
