#!/usr/bin/env python3
"""Report every internal link in the declared chapters that pandoc leaves dead.

The file set is `content/<lang>/<stem>.qmd` for every language in `languages.yml` and every
stem in `content/en/_quarto.yaml`: 400 files. Pandoc renders each file to one standalone HTML
page, and Python's `html.parser` reads that page once. The ids are the ones a browser sees:
`id` on any element, and `name` on an `<a>` element. The links are the `href` of every `<a>`
element.

Pandoc does the hard part. It resolves a heading, a div, a span, a metadata title, raw HTML, an
HTML comment and a character reference into one document. So the checker never re-implements
pandoc's identifier rule, and it never reads markdown itself.

A link is dead when its `.qmd` target does not exist, or when the target page does not define
the `#fragment` it asks for. Fragments resolve against the same page when the target is a bare
`#fragment`. External links and targets that are not `.qmd` are ignored.

Two more link forms fail. Write a link to a section of the same page as `#id`, never as
`file.qmd#id`. The checker counts the long form as `same-page`. A link never crosses languages.
A file's language is the folder that holds it, and a link target's language is the language of
its resolved path. So `../en/basics.qmd` written in a French chapter is a `language-mismatch`.

One form pandoc cannot report is the unterminated link, `[text](#target` with no closing
parenthesis. Pandoc reads no link there, so the page carries no `<a>` element and the target is
never checked. The checker reads the raw source for that form and counts it as
`unterminated-link`. A blank line ends the search, because an inline link cannot cross one. So a
link whose destination sits on the next line still passes, which CommonMark allows. The checker
skips a fenced code block, an HTML comment and a code span.

Deterministic. No model, no network, no third-party package. Exit 1 on a link that is dead,
same-page in long form, across languages, or unterminated.

Usage: python3 checks/check-links.py [--summary] [--fixture <dir>] [--pandoc <cmd>]
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
    `index` is the first of them. Every language declares the same stems in the same order:
    check 9 of `checks/check-sync.sh` reports a language that does not.
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


def blank_comments(text):
    """The text with every HTML comment blanked, one space per character, newlines kept.

    Pandoc reads no link inside an HTML comment. Blanking keeps every line number.
    """
    return re.sub(r'<!--.*?-->', lambda m: ''.join(c if c == '\n' else ' ' for c in m.group(0)),
                  text, flags=re.S)


def blank_code_spans(line):
    """The line with every backtick code span blanked, one space per character.

    A span opens on a run of backticks and closes on a run of the same length, as CommonMark
    says. An unclosed run is left alone. Pandoc reads no link inside a code span.
    """
    out, i, n = list(line), 0, len(line)
    while i < n:
        if line[i] != '`':
            i += 1
            continue
        j = i
        while j < n and line[j] == '`':
            j += 1
        run, k, end = j - i, j, None
        while k < n:
            if line[k] != '`':
                k += 1
                continue
            m = k
            while m < n and line[m] == '`':
                m += 1
            if m - k == run:
                end = m
                break
            k = m
        if end is None:
            i = j
            continue
        for x in range(i, end):
            out[x] = ' '
        i = end
    return ''.join(out)


def unterminated_links(text):
    """Every `](` in prose whose link target does not close before the next blank line.

    Returns [(line number, the source line)]. An inline link cannot cross a blank line, so the
    blank line bounds the search. The scan counts nested parentheses, so a URL that holds a
    balanced pair passes, and a destination written on the next line passes too. The scan skips
    a fenced code block, an HTML comment and a code span.
    """
    raws = text.split('\n')
    found, fence, block = [], None, []

    def flush():
        if not block:
            return
        joined = '\n'.join(l for _, l in block)
        at = []
        for n, l in block:
            at.extend([n] * (len(l) + 1))
        for hit in re.finditer(r'\]\(', joined):
            if hit.start() and joined[hit.start() - 1] == '\\':
                continue
            depth, j, closed = 1, hit.end(), False
            while j < len(joined):
                c = joined[j]
                if c == '\\':
                    j += 2
                    continue
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        closed = True
                        break
                j += 1
            if not closed:
                n = at[hit.start()]
                found.append((n, raws[n - 1].rstrip()))
        block.clear()

    for n, l in enumerate(blank_comments(text).split('\n'), 1):
        m = FENCE.match(l)
        code = m is None or len(m.group(1)) > 3
        if fence is None:
            if not code:
                flush()
                fence = m.group(2)
                continue
        else:
            if not code and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) \
                    and not m.group(3).strip():
                fence = None
            continue
        if not l.strip():
            flush()
            continue
        block.append((n, blank_code_spans(l)))
    flush()
    return sorted(found)


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
    files = [(str(p.relative_to(base)), language(p)) for p in sorted(base.glob('*/*.qmd'))]
    langs = sorted({l for _, l in files})
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

dead, samepage, mismatch, unterminated = [], [], [], []
for f, lang in files:
    for n, line in unterminated_links((base / f).read_text(encoding='utf-8')):
        unterminated.append((f, lang, n, line))
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
        if q == f and frag:
            samepage.append((f, lang, t))
        if language(q) != lang:
            mismatch.append((f, lang, t))
        if frag and frag not in parsed[q][0]:
            dead.append((f, lang, t, 'no id %s in %s' % (frag, q)))

if not summary:
    out, src = [], {}

    def at(f, t):
        lines = src.setdefault(f, (base / f).read_text(encoding='utf-8').split('\n'))
        return first_line(lines, t)

    for f, lang, t, why in dead:
        n, many = at(f, t)
        out.append((f, n, t, 'DEAD %s:%d%s %s (%s)' % (f, n, '?' if many else '', t, why)))
    for f, lang, t in samepage:
        n, many = at(f, t)
        out.append((f, n, t, 'SAME-PAGE %s:%d%s %s' % (f, n, '?' if many else '', t)))
    for f, lang, t in mismatch:
        n, many = at(f, t)
        out.append((f, n, t, 'LANGUAGE-MISMATCH %s:%d%s %s' % (f, n, '?' if many else '', t)))
    for f, lang, n, line in unterminated:
        out.append((f, n, line, 'UNTERMINATED-LINK %s:%d %s' % (f, n, line.strip())))
    for _, _, _, line in sorted(out):
        print(line)

else:
    print('files scanned: %d' % scanned)
    print('pandoc: %s, version %s' % (' '.join(pandoc), pandoc_version()))
    for l in langs:
        n = sum(1 for _, x in files if x == l)
        if not n:
            continue
        print('lang %s: files %d, dead %d, same-page %d, language-mismatch %d'
              % (l, n, sum(1 for r in dead if r[1] == l), sum(1 for r in samepage if r[1] == l),
                 sum(1 for r in mismatch if r[1] == l)))
    if extra:
        print('targets parsed outside the declared set: %d' % len(extra))
    print('same-page %d' % len(samepage))
    print('language-mismatch %d' % len(mismatch))
    print('unterminated-links %d' % len(unterminated))
    print('dead %d' % len(dead))

sys.exit(1 if dead or samepage or mismatch or unterminated or missing else 0)
