#!/usr/bin/env python3
"""Fail when a translated chapter page has other tables than the English page.

Check 25. It runs in the assemble-deploy job of `.github/workflows/build-deploy.yml` on
`site/`, after check 18. It reads the HTML that ships, so it counts the tables that pandoc and
Quarto wrote into each page. A table that JavaScript builds in the browser, such as a
`DT::datatable()` htmlwidget, is not in that HTML, so the check cannot see it.

The site layout is the one `checks/assemble-site.sh` writes: one folder per language, the main
language included, `<site>/<lang>/`. Every folder directly under the site folder is a language
folder. A folder whose name starts with `.` is not.

A chapter page is an `.html` file directly in a language folder that holds the element
`<main id="quarto-document-content">`. Quarto writes that element into every chapter page,
the landing page `index.html` included. These pages are NOT chapter pages:
  - a redirect stub, such as `index.fr.html` or `about.html`, because it has no such element;
  - a page in a subfolder, such as `new_pages/` or `site_libs/`;
  - a file that is not `.html`, such as `search.json`.
A page that exists in one language only is a chapter page when it holds the element, so it is
caught.

Pages pair by language folder and stem: `<site>/<lang>/<stem>.html` against
`<site>/<main>/<stem>.html`. Tables pair by their order within the page. The count rule:
  - a table is a `<table>` element, in the order of its start tag;
  - a row is a `<tr>` element, and it belongs to the innermost open table;
  - a cell is a `<td>` or a `<th>` element, and it belongs to the innermost open table. Each
    cell counts once, whatever its `colspan` or `rowspan`;
  - a table nested in a cell is its own table, in the order of its start tag. Its rows and
    cells do not count for the table around it.
Text inside a `<script>` element is not HTML, so a table in a script is not read.

The check fails (exit 1) on each of these findings:
  empty-site           no language folder other than the main one holds a chapter page
  no-english-page      a translated chapter page has no chapter page of the same stem in the
                       main language
  no-translated-page   a chapter page of the main language has no page of the same stem in a
                       language folder that exists
  table-count          a page pair has a different number of tables. The finding names the
                       first table that differs. The check then compares no table of that pair,
                       because each table after the difference pairs with the wrong table.
  row-count            a table pair has a different number of rows
  cell-count           a table pair has the same number of rows and a different number of cells
A table-count, row-count or cell-count finding names the language, the stem, the table, and
the rows and cells of the English side and of the translated side. A missing-page finding names
the language and the stem, and the rows and cells of each table on the page that exists. An
empty-site finding names the site folder, because it has no language or stem.

The main language is `--main <code>`. The default is the `main:` line of `languages.yml` at
the repository root. The check uses the Python standard library only, so it reads that line
with a regular expression. CI passes the value that the `languages` job read.

`--summary` prints one line per language and a totals line, and no finding. Without it, the
check prints every finding first. `--self-test` runs every fixture under
`checks/fixtures/rendered-tables/`. Each fixture holds a `site/` folder and an `expect.txt` of
`pass` or `fail <finding>`. A fail fixture MUST exit 1 with that finding and no other, and a
pass fixture MUST exit 0. Each finding needs a fail fixture, and one pass fixture is needed.

Exit 0 when every page pair matches and 1 on any finding. Exit 2 on a missing or unusable
input, with one message that names its full path:
  - no site folder;
  - a site folder or a language folder that cannot be read;
  - no main-language folder, whatever the translated folders hold;
  - a page that cannot be read;
  - with no `--main`, no `languages.yml`, or no `main:` line in it.

Usage: python3 checks/check-rendered-tables.py [--main <code>] [--summary] <site dir>
       python3 checks/check-rendered-tables.py --self-test
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / 'fixtures' / 'rendered-tables'
PROG = 'check-rendered-tables'
KINDS = ('empty-site', 'no-english-page', 'no-translated-page',
         'table-count', 'row-count', 'cell-count')
CODE = re.compile(r'[a-z]{2,3}')
MAIN_LINE = re.compile(r'''^main:[ \t]*["']?([^"'\s#]*)["']?[ \t]*(?:#.*)?$''', re.M)


def die(msg):
    print('%s: %s' % (PROG, msg), file=sys.stderr)
    sys.exit(2)


class Page(HTMLParser):
    """The tables of one page as [rows, cells] in start-tag order, and its chapter marker."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.open, self.chapter = [], [], False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.tables.append([0, 0])
            self.open.append(len(self.tables) - 1)
        elif tag == 'tr' and self.open:
            self.tables[self.open[-1]][0] += 1
        elif tag in ('td', 'th') and self.open:
            self.tables[self.open[-1]][1] += 1
        elif tag == 'main' and ('id', 'quarto-document-content') in attrs:
            self.chapter = True

    def handle_endtag(self, tag):
        if tag == 'table' and self.open:
            self.open.pop()


def chapters(folder):
    """{stem: [[rows, cells], ...]} for every chapter page directly in one language folder."""
    out = {}
    # glob() returns nothing on a folder it cannot list, so list the folder first.
    try:
        next(folder.iterdir(), None)
    except OSError as e:
        die('%s cannot be read: %s' % (folder, e.strerror))
    for page in sorted(folder.glob('*.html')):
        if not page.is_file():
            continue
        try:
            text = page.read_text(encoding='utf-8', errors='replace')
        except OSError as e:
            die('%s cannot be read: %s' % (page, e.strerror))
        p = Page()
        p.feed(text)
        p.close()
        if p.chapter:
            out[page.stem] = p.tables
    return out


def default_main():
    """The `main:` code of languages.yml at the repository root."""
    path = ROOT / 'languages.yml'
    try:
        text = path.read_text(encoding='utf-8')
    except OSError:
        die('no %s, and no --main. That file names the main language.' % path)
    m = MAIN_LINE.search(text)
    if not m or not CODE.fullmatch(m.group(1)):
        die('%s has no `main:` line with a language code, and no --main was given.' % path)
    return m.group(1)


def shape(t):
    return '%d rows and %d cells' % (t[0], t[1]) if t else 'no such table'


def listing(path, tables):
    """One page that exists, with the rows and cells of each of its tables."""
    each = '; '.join('table %d: %s' % (i + 1, shape(t)) for i, t in enumerate(tables))
    return '%s, tables %d%s' % (path, len(tables), ' (%s)' % each if each else '')


def compare(lang, stem, eng, tr):
    """The findings of one page pair. eng and tr are the table lists."""
    where = 'language %s, stem %s' % (lang, stem)
    if len(eng) != len(tr):
        first = next(i for i in range(max(len(eng), len(tr)))
                     if i >= len(eng) or i >= len(tr) or eng[i] != tr[i])
        e = eng[first] if first < len(eng) else None
        t = tr[first] if first < len(tr) else None
        return [('table-count', '%s: English has %d tables, translation %d. Table %d is the '
                 'first that differs: English %s, translation %s'
                 % (where, len(eng), len(tr), first + 1, shape(e), shape(t)))]
    out = []
    for i, (e, t) in enumerate(zip(eng, tr)):
        if e[0] != t[0]:
            kind = 'row-count'
        elif e[1] != t[1]:
            kind = 'cell-count'
        else:
            continue
        out.append((kind, '%s, table %d of %d: English %s, translation %s'
                    % (where, i + 1, len(eng), shape(e), shape(t))))
    return out


def check(site, main):
    """(findings, summary lines) for one site folder. Each finding is (kind, text)."""
    site = site.resolve()
    try:
        entries = list(site.iterdir())
    except OSError as e:
        die('%s cannot be read: %s' % (site, e.strerror))
    langs = sorted(d for d in entries if d.is_dir() and not d.name.startswith('.')
                   and d.name != main)
    translated = {d.name: chapters(d) for d in langs}
    pages = sum(len(v) for v in translated.values())
    tables = sum(len(t) for v in translated.values() for t in v.values())
    ref_dir = site / main
    if not ref_dir.is_dir():
        die('%s is not a directory. It holds the pages of the main language, %s.'
            % (ref_dir, main))
    ref = chapters(ref_dir)
    findings, lines = [], []
    lines.append('%s (main): pages %d, tables %d'
                 % (main, len(ref), sum(len(v) for v in ref.values())))
    # With no translated chapter page, no page pair exists, so nothing is compared. The
    # empty-site finding belongs to no language, so each language line has 0 findings.
    compared = ref if pages else {}
    if not pages:
        findings.append(('empty-site', '%s: no language folder other than %s holds a chapter '
                         'page, so no table was compared' % (site, main)))
    for lang, own in translated.items():
        before = len(findings)
        for stem in sorted(set(own) - set(compared)):
            findings.append(('no-english-page', 'language %s, stem %s: English %s/%s.html is '
                             'not a chapter page. Translation %s'
                             % (lang, stem, main, stem,
                                listing('%s/%s.html' % (lang, stem), own[stem]))))
        for stem in sorted(set(compared) - set(own)):
            findings.append(('no-translated-page', 'language %s, stem %s: English %s. '
                             'Translation %s/%s.html is not a chapter page'
                             % (lang, stem, listing('%s/%s.html' % (main, stem), ref[stem]),
                                lang, stem)))
        for stem in sorted(set(own) & set(compared)):
            findings.extend(compare(lang, stem, ref[stem], own[stem]))
        lines.append('%s: pages %d, tables %d, findings %d'
                     % (lang, len(own), sum(len(v) for v in own.values()), len(findings) - before))
    lines.append('rendered tables: translated languages %d, pages %d, tables %d, findings %d'
                 % (len(translated), pages, tables, len(findings)))
    return findings, lines


def self_test():
    dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    if not dirs:
        die('no fixture directory under %s, so nothing would be tested.' % FIXTURES)
    bad, seen = [], set()
    for d in dirs:
        try:
            expect = (d / 'expect.txt').read_text(encoding='utf-8').split()
        except OSError:
            bad.append('%s: no expect.txt' % d.name)
            print('FAIL %s: no expect.txt' % d.name)
            continue
        if expect == ['pass']:
            want_rc, want = 0, set()
        elif len(expect) == 2 and expect[0] == 'fail' and expect[1] in KINDS:
            want_rc, want = 1, {expect[1]}
        else:
            bad.append('%s: expect.txt is neither `pass` nor `fail <finding>`' % d.name)
            print('FAIL %s: expect.txt is neither `pass` nor `fail <finding>`' % d.name)
            continue
        seen.add(' '.join(expect))
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                              '--main', 'en', str(d / 'site')],
                             capture_output=True, text=True, timeout=60)
        got = {line.split(':', 1)[0] for line in run.stdout.splitlines()
               if line.split(':', 1)[0] in KINDS}
        ok = run.returncode == want_rc and got == want
        print('%s %s: expect %s, exit %d, got %s'
              % ('ok' if ok else 'FAIL', d.name, ' '.join(expect), run.returncode,
                 ' '.join(sorted(got)) or 'no finding'))
        if not ok:
            bad.append('%s: expect %s, exit %d, got %s%s'
                       % (d.name, ' '.join(expect), run.returncode,
                          ' '.join(sorted(got)) or 'no finding',
                          '; stderr: ' + run.stderr.strip() if run.stderr.strip() else ''))
    for need in ['pass'] + ['fail %s' % k for k in KINDS]:
        if need not in seen:
            bad.append('no fixture expects `%s`' % need)
    for b in bad:
        print('   %s' % b)
    print('self-test: fixtures %d, wrong %d' % (len(dirs), len(bad)))
    return 1 if bad else 0


def main(argv):
    usage = __doc__.strip().split('Usage: ')[1]
    if argv == ['--self-test']:
        return self_test()
    summary, main, rest = False, None, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--summary':
            summary = True
        elif a == '--main' and i + 1 < len(argv):
            main = argv[i + 1]
            i += 1
        elif a.startswith('-'):
            die('unknown argument %s. Usage: %s' % (a, usage))
        else:
            rest.append(a)
        i += 1
    if len(rest) != 1:
        die('expected one site folder. Usage: %s' % usage)
    site = Path(rest[0]).absolute()
    if not site.is_dir():
        die('%s is not a directory. It is the assembled site.' % site)
    if main is None:
        main = default_main()
    elif not CODE.fullmatch(main):
        die('--main %r is not a language code of 2 or 3 lowercase letters.' % main)
    findings, lines = check(site, main)
    if not summary:
        for kind, text in findings:
            print('%s: %s' % (kind, text))
    for line in lines:
        print(line)
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
