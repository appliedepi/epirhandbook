#!/usr/bin/env python3
"""Report every internal link in the declared chapters that pandoc leaves dead.

The file set is every chapter declared in `_quarto.yml` (`index.qmd` and `chapters/<stem>.qmd`)
in English and in every language under `babelquarto.languages`: 400 files. Pandoc renders each
file to one standalone HTML page, and Python's `html.parser` reads that page once. The ids are
the ones a browser sees: `id` on any element, and `name` on an `<a>` element. The links are the
`href` of every `<a>` element.

Pandoc does the hard part. It resolves a heading, a div, a span, a metadata title, raw HTML, an
HTML comment and a character reference into one document. So the checker never re-implements
pandoc's identifier rule, and it never reads markdown itself.

A link is dead when its `.qmd` target does not exist, or when the target page does not define
the `#fragment` it asks for. Fragments resolve against the same page when the target is a bare
`#fragment`. External links and targets that are not `.qmd` are ignored. A translation that
links to the English `.qmd` file is live, and is counted as `language-mismatch`.

Deterministic. No model, no network, no third-party package. Exit 1 when any link is dead.

Usage: python3 modernization/check-links.py [--summary] [--fixture <dir>] [--pandoc <cmd>]
"""
import os, re, shutil, shlex, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
POOL = 8
FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
SCHEME = re.compile(r'^(?:[A-Za-z][A-Za-z0-9+.\-]*:|//)')

args = sys.argv[1:]
summary = '--summary' in args
known = {'--summary': 0, '--fixture': 1, '--pandoc': 1}
i = 0
while i < len(args):
    if args[i] not in known:
        sys.exit('unknown argument %s. Usage: %s' % (args[i], __doc__.strip().split('Usage: ')[1]))
    i += 1 + known[args[i]]


def opt(name):
    return args[args.index(name) + 1] if name in args else None


fixture = opt('--fixture')
pandoc = shlex.split(opt('--pandoc')) if opt('--pandoc') else None
if pandoc is None:
    pandoc = ['quarto', 'pandoc'] if shutil.which('quarto') else ['pandoc']


def pandoc_version():
    out = subprocess.run(pandoc + ['--version'], capture_output=True, text=True).stdout
    m = re.search(r'([0-9]+(?:\.[0-9]+)+)', out)
    return m.group(1) if m else 'unknown'


def declared():
    """Every declared chapter file: [(path relative to root, language)]."""
    y = (ROOT / '_quarto.yml').read_text(encoding='utf-8')
    stems = ['index'] + ['chapters/' + s for s in re.findall(r'^\s*-\s*chapters/([A-Za-z0-9_]+)\.qmd', y, re.M)]
    langs = re.search(r'languages:\s*\[([^\]]*)\]', y).group(1)
    langs = [x.strip().strip("'\"") for x in langs.split(',') if x.strip()]
    out = [(s + '.qmd', 'en') for s in stems]
    out += [(s + '.' + l + '.qmd', l) for s in stems for l in langs]
    return sorted(out), langs


def language(path, langs):
    m = re.search(r'\.([a-z]{2})\.qmd$', path)
    return m.group(1) if m and m.group(1) in langs else 'en'


class PageParser(HTMLParser):
    """Every id and every link target of one rendered HTML page.

    An `id` attribute names a fragment target on any element. A `name` attribute names one on
    an `<a>` element, which is the legacy anchor. An empty value names nothing. A repeated
    attribute takes the first value, which is what an HTML parser does.

    The parser does four things a regular expression cannot:

    - It lowercases the element name and the attribute name.
    - It decodes a character reference in an attribute value.
    - It treats the body of `script` and `style` as text.
    - It sends a comment to a handler this class does not implement.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = {}
        for k, v in attrs:
            a.setdefault(k, v)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'a':
            if a.get('name'):
                self.ids.add(a['name'])
            if a.get('href'):
                self.links.append(a['href'])

    handle_startendtag = handle_starttag


def plain_fences(text):
    """Rewrite every executable chunk header, ```{r, eval=F} to ```{.r}, line for line.

    Pandoc's markdown reader does not accept a bare word in a fence attribute. It reads
    ```{r} as a paragraph, and the whole chunk as prose. Quarto never asks it to: knitr rewrites
    the header first. Without this step every `#` comment in an R chunk becomes a heading with
    an id, and every link inside a chunk becomes a link. Raw blocks such as ```{=html} are
    valid pandoc syntax and are left alone.

    CommonMark bounds a fence line, and this function follows it. An indent of four spaces or
    more is code, so such a line opens no fence and closes none. A closing fence carries the
    opening character, and it is as long as the opener or longer.
    """
    out, fence = [], None
    for l in text.split('\n'):
        m = FENCE.match(l)
        code = m is None or len(m.group(1)) > 3
        if fence is None and not code:
            fence = m.group(2)
            w = re.match(r'^\{([A-Za-z][A-Za-z0-9_]*)(?:[ ,][^}]*)?\}$', m.group(3).strip())
            if w:
                l = m.group(1) + m.group(2) + '{.' + w.group(1) + '}'
        elif fence is not None and not code and m.group(2)[0] == fence[0] \
                and len(m.group(2)) >= len(fence) and not m.group(3).strip():
            fence = None
        out.append(l)
    return '\n'.join(out)


def parse(path):
    """Return (ids, link targets) for one file, from the page pandoc renders."""
    src = plain_fences(Path(path).read_text(encoding='utf-8'))
    r = subprocess.run(pandoc + ['-s', '-f', 'markdown', '-t', 'html',
                                 '--metadata', 'pagetitle=check'],
                       input=src, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('pandoc failed on %s: %s' % (path, r.stderr.strip()))
    p = PageParser()
    p.feed(r.stdout)
    p.close()
    return p.ids, p.links


def first_line(lines, target):
    """The first source line holding the target, and whether it occurs on more than one."""
    want = {target, unquote(target)}
    hits = [i + 1 for i, l in enumerate(lines) if any(w in l for w in want)]
    return (hits[0] if hits else 0), len(hits) > 1


base = Path(fixture) if fixture else ROOT
if fixture:
    files = [(p.name, 'en') for p in sorted(Path(fixture).glob('*.qmd'))]
    langs = []
else:
    files, langs = declared()

missing = [f for f, _ in files if not (base / f).exists()]
for f in missing:
    print('MISSING %s' % f, file=sys.stderr)
files = [(f, l) for f, l in files if f not in missing]

with ThreadPoolExecutor(POOL) as ex:
    parsed = dict(zip([f for f, _ in files], ex.map(lambda f: parse(base / f), [f for f, _ in files])))
scanned = len(parsed)

# Targets outside the declared set still need their ids, so parse those too. They are not scanned.
extra = set()
for f, _ in files:
    for t in parsed[f][1]:
        if SCHEME.match(t) or t.startswith('#'):
            continue
        p = t.split('#', 1)[0]
        if p.lower().endswith('.qmd'):
            q = os.path.normpath(os.path.join(os.path.dirname(f), p))
            if q not in parsed and (base / q).exists():
                extra.add(q)
with ThreadPoolExecutor(POOL) as ex:
    parsed.update(zip(sorted(extra), ex.map(lambda f: parse(base / f), sorted(extra))))

dead, mismatch = [], []
for f, lang in files:
    for t in parsed[f][1]:
        if not t or SCHEME.match(t):
            continue
        path, _, frag = t.partition('#')
        frag = unquote(frag)
        if not path:
            if frag and frag not in parsed[f][0]:
                dead.append((f, lang, t, 'no id %s on this page' % frag))
            continue
        if not path.lower().endswith('.qmd'):
            continue
        q = os.path.normpath(os.path.join(os.path.dirname(f), path))
        if not (base / q).exists():
            dead.append((f, lang, t, 'no such file'))
            continue
        if language(q, langs) != lang:
            mismatch.append((f, lang, t))
        if frag and frag not in parsed[q][0]:
            dead.append((f, lang, t, 'no id %s in %s' % (frag, q)))

if not summary:
    out, src = [], {}
    for f, lang, t, why in dead:
        lines = src.setdefault(f, (base / f).read_text(encoding='utf-8').split('\n'))
        n, many = first_line(lines, t)
        out.append((f, n, t, 'DEAD %s:%d%s %s (%s)' % (f, n, '?' if many else '', t, why)))
    for _, _, _, line in sorted(out):
        print(line)

else:
    print('files scanned: %d' % scanned)
    print('pandoc: %s, version %s' % (' '.join(pandoc), pandoc_version()))
    for l in ['en'] + sorted(langs):
        print('lang %s: files %d, dead %d, language-mismatch %d'
              % (l, sum(1 for _, x in files if x == l), sum(1 for r in dead if r[1] == l),
                 sum(1 for r in mismatch if r[1] == l)))
    if extra:
        print('targets parsed outside the declared set: %d' % len(extra))
    print('language-mismatch %d' % len(mismatch))
    print('dead %d' % len(dead))

sys.exit(1 if dead or missing else 0)
