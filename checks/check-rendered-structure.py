#!/usr/bin/env python3
"""Fail when a section of a translated chapter page has other elements than the English section.

Check 29. It runs in the assemble-deploy job of `.github/workflows/build-deploy.yml` on `site/`,
right after check 25. It reads the HTML that ships. A list that pandoc reads as paragraph text,
or a stray indent that pandoc reads as a code block, changes a count here.

The site layout, the chapter pages and the page pairs are those of check 25,
`checks/check-rendered-tables.py`. Every folder directly under the site folder is a language
folder, unless its name starts with `.`. A chapter page is an `.html` file directly in a
language folder that holds `<main id="quarto-document-content">`. Pages pair by language
folder and stem: `<site>/<lang>/<stem>.html` against `<site>/<main>/<stem>.html`. The check
does not read `index.html`, the landing page. Each language writes its own landing page, so its
structure MAY differ from the English (contract P2 of issue 466). Check 25 still reads it.

The check counts only the elements inside `<main id="quarto-document-content">`. It skips each
`<nav>` inside that element, which holds the breadcrumbs and the page navigation. The header,
the sidebar, the margin table of contents and the footer are outside it. A difference in the
navigation is therefore not a finding. Text inside `<script>` and `<style>` is not HTML, so
nothing in it counts.

Section 0 is the content before the first heading. Section n starts at the n-th heading, `<h1>`
to `<h6>`, and runs to the next heading of any level. The heading belongs to its own section.

The check counts these kinds in each section:
  h1 to h6      a heading of that level
  a             an `<a>` with an `href` attribute, outside `<pre>`
  img           an `<img>`
  code-inline   a `<code>` outside `<pre>`
  code-block    a `<code>` inside `<pre>`
  table         a `<table>`
  li            an `<li>`
Quarto writes an `<a href="#cb1-1">` on each line of a code block. A code block with one more
line would then read as one more link, so an `<a>` inside `<pre>` does not count. Italics are
not compared.

The check first compares the heading levels of the two pages, in order. Where they differ, the
same ordinal names different sections on the two pages. The check then aligns the two level
sequences with `difflib.SequenceMatcher`. It reports each level whose count differs in each run
of headings that does not align, and it compares no other kind on that page. Where two headings
of the same level stand next to each other, the finding MAY name either of them.

The check fails (exit 1) on each of these findings:
  missing-language     a language that is declared has no folder in the site
  empty-site           no language folder other than the main one holds a chapter page
  no-english-page      a translated chapter page has no chapter page of the same stem in the
                       main language
  no-translated-page   a chapter page of the main language has no page of the same stem in a
                       language folder that exists
  <kind>               a section pair has a different count of that kind
A kind finding names the language, the stem, the section ordinal and its English heading, and
the count on each side. A missing-page finding names the language, the stem and the sections of
the page that exists. An empty-site finding names the site folder. A missing-language finding
names the language and the folder that does not exist.

The main language is `--main <code>`. The default is the `main:` line of `languages.yml` at
the repository root. The check uses the Python standard library only, so it reads that line
with a regular expression. CI passes the value that the `languages` job read.

The declared languages are `--languages <code,code,...>`. The default is every `code:` line of
`languages.yml` at the repository root, read with a regular expression. CI passes no
`--languages`, so the check reads that file. The self-test passes the codes in the
`languages.txt` of a fixture, or the folder names of its site when it has no such file.

`--summary` prints one line per language and a totals line, and no finding. Without it, the
check prints every finding first. `--self-test` runs every fixture under
`checks/fixtures/rendered-structure/`. Each fixture holds a `site/` folder and an `expect.txt`,
and MAY hold a `languages.txt`.
The first line of `expect.txt` is `pass` or `fail`. A fail fixture lists each expected finding
line after it, with `{site}` for the full path of its site folder. A fail fixture MUST exit 1
with exactly those findings, and a pass fixture MUST exit 0 with no finding. Each finding needs
a fail fixture, and one pass fixture is needed.

Exit 0 when every section pair matches and 1 on any finding. Exit 2 on a missing or unusable
input, with one message that names its full path:
  - no site folder;
  - a site folder or a language folder that cannot be read;
  - no main-language folder, whatever the translated folders hold;
  - a page that cannot be read;
  - with no `--main`, no `languages.yml`, or no `main:` line in it;
  - with no `--languages`, no `code:` line in `languages.yml`, or a code that is not 2 or 3
    lowercase letters.

Usage: python3 checks/check-rendered-structure.py [--main <code>] [--languages <codes>] [--summary] <site dir>
       python3 checks/check-rendered-structure.py --self-test
"""
import difflib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / 'fixtures' / 'rendered-structure'
PROG = 'check-rendered-structure'
HEADS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
KINDS = HEADS + ('a', 'img', 'code-inline', 'code-block', 'table', 'li')
LANDING = 'index.html'
FINDINGS = ('missing-language', 'empty-site', 'no-english-page', 'no-translated-page') + KINDS
CODE = re.compile(r'[a-z]{2,3}')
MAIN_LINE = re.compile(r'''^main:[ \t]*["']?([^"'\s#]*)["']?[ \t]*(?:#.*)?$''', re.M)
CODE_LINE = re.compile(r'''^[ \t]*(?:-[ \t]+)?code:[ \t]*["']?([^"'\s#]*)["']?[ \t]*(?:#.*)?$''', re.M)


def die(msg):
    print('%s: %s' % (PROG, msg), file=sys.stderr)
    sys.exit(2)


class Page(HTMLParser):
    """The sections of one page: the count of each kind, and the level and text of each heading."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chapter = False
        self.main = 0      # open <main> elements, from <main id="quarto-document-content"> on
        self.nav = 0       # open <nav> elements inside it
        self.pre = 0       # open <pre> elements inside it
        self.sections = [dict.fromkeys(KINDS, 0)]
        self.levels, self.titles, self.heading = [], [], None

    def handle_starttag(self, tag, attrs):
        if tag == 'main':
            if self.main:
                self.main += 1
            elif ('id', 'quarto-document-content') in attrs:
                self.chapter, self.main = True, 1
            return
        if not self.main:
            return
        if tag == 'nav':
            self.nav += 1
            return
        if self.nav:
            return
        if tag == 'pre':
            self.pre += 1
            return
        if tag in HEADS:
            self.sections.append(dict.fromkeys(KINDS, 0))
            self.sections[-1][tag] = 1
            self.levels.append(tag)
            self.titles.append('')
            self.heading = tag
        elif tag == 'a':
            if not self.pre and any(k == 'href' for k, _ in attrs):
                self.sections[-1]['a'] += 1
        elif tag == 'code':
            self.sections[-1]['code-block' if self.pre else 'code-inline'] += 1
        elif tag in ('img', 'table', 'li'):
            self.sections[-1][tag] += 1

    def handle_endtag(self, tag):
        if not self.main:
            return
        if tag == 'main':
            self.main -= 1
        elif tag == 'nav' and self.nav:
            self.nav -= 1
        elif self.nav:
            return
        elif tag == 'pre' and self.pre:
            self.pre -= 1
        elif tag == self.heading:
            self.heading = None

    def handle_data(self, data):
        if self.heading and self.main and not self.nav:
            self.titles[-1] += data


def chapters(folder):
    """{stem: Page} for every chapter page directly in one language folder, index.html aside."""
    out = {}
    # glob() returns nothing on a folder it cannot list, so list the folder first.
    try:
        next(folder.iterdir(), None)
    except OSError as e:
        die('%s cannot be read: %s' % (folder, e.strerror))
    for page in sorted(folder.glob('*.html')):
        if not page.is_file() or page.name == LANDING:
            continue
        try:
            text = page.read_text(encoding='utf-8', errors='replace')
        except OSError as e:
            die('%s cannot be read: %s' % (page, e.strerror))
        p = Page()
        p.feed(text)
        p.close()
        if p.chapter:
            out[page.stem] = p
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


def default_languages():
    """The `code:` values of languages.yml at the repository root, in file order."""
    path = ROOT / 'languages.yml'
    try:
        text = path.read_text(encoding='utf-8')
    except OSError:
        die('no %s, and no --languages. That file declares the languages.' % path)
    codes = CODE_LINE.findall(text)
    if not codes or not all(CODE.fullmatch(c) for c in codes):
        die('%s has no `code:` line, or a code that is not 2 or 3 lowercase letters, and no '
            '--languages was given.' % path)
    return codes


def section(page, n):
    """Section n of a page, with its heading text."""
    if n == 0:
        return 'section 0, before the first heading'
    return 'section %d %s' % (n, json.dumps(' '.join(page.titles[n - 1].split()),
                                             ensure_ascii=False))


def compare(lang, stem, eng, tr):
    """The findings of one page pair, each as (kind, text)."""
    where = 'language %s, stem %s' % (lang, stem)
    out = []
    if eng.levels != tr.levels:
        match = difflib.SequenceMatcher(None, eng.levels, tr.levels, autojunk=False)
        for op, i1, i2, j1, j2 in match.get_opcodes():
            if op == 'equal':
                continue
            # A run that only the translation holds lands in English section i1.
            n = i1 + 1 if i2 > i1 else i1
            for level in HEADS:
                e = eng.levels[i1:i2].count(level)
                t = tr.levels[j1:j2].count(level)
                if e != t:
                    out.append((level, '%s, %s: English %d, translation %d. The heading levels '
                                'differ, so no other kind on this page is compared'
                                % (where, section(eng, n), e, t)))
        return out
    for n, (e, t) in enumerate(zip(eng.sections, tr.sections)):
        for kind in KINDS:
            if e[kind] != t[kind]:
                out.append((kind, '%s, %s: English %d, translation %d'
                            % (where, section(eng, n), e[kind], t[kind])))
    return out


def check(site, main, declared):
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
    sections = sum(len(p.sections) for v in translated.values() for p in v.values())
    ref_dir = site / main
    if not ref_dir.is_dir():
        die('%s is not a directory. It holds the pages of the main language, %s.'
            % (ref_dir, main))
    ref = chapters(ref_dir)
    totals = dict.fromkeys(KINDS, 0)
    for p in ref.values():
        for s in p.sections:
            for kind in KINDS:
                totals[kind] += s[kind]
    findings, lines = [], []
    lines.append('main language %s: pages %d, sections %d; %s'
                 % (main, len(ref), sum(len(p.sections) for p in ref.values()),
                    ', '.join('%s %d' % (k, totals[k]) for k in KINDS)))
    # A declared language with no folder has no page to compare, so it is not clean.
    for lang in declared:
        if lang != main and not (site / lang).is_dir():
            findings.append(('missing-language', 'language %s: %s is not a directory, so no '
                             'page of this declared language was compared' % (lang, site / lang)))
            lines.append('language %s: no folder, findings 1' % lang)
    # With no translated chapter page, no page pair exists, so nothing is compared. The
    # empty-site finding belongs to no language, so each language line has 0 findings.
    compared = ref if pages else {}
    if not pages:
        findings.append(('empty-site', '%s: no language folder other than %s holds a chapter '
                         'page, so no section was compared' % (site, main)))
    for lang, own in translated.items():
        before = len(findings)
        for stem in sorted(set(own) - set(compared)):
            findings.append(('no-english-page', 'language %s, stem %s: English %s/%s.html is '
                             'not a chapter page. Translation %s/%s.html, sections %d'
                             % (lang, stem, main, stem, lang, stem, len(own[stem].sections))))
        for stem in sorted(set(compared) - set(own)):
            findings.append(('no-translated-page', 'language %s, stem %s: English %s/%s.html, '
                             'sections %d. Translation %s/%s.html is not a chapter page'
                             % (lang, stem, main, stem, len(ref[stem].sections), lang, stem)))
        for stem in sorted(set(own) & set(compared)):
            findings.extend(compare(lang, stem, ref[stem], own[stem]))
        lines.append('language %s: pages %d, sections %d, findings %d'
                     % (lang, len(own), sum(len(p.sections) for p in own.values()),
                        len(findings) - before))
    lines.append('rendered structure: translated languages %d, pages %d, sections %d, '
                 'findings %d' % (len(translated), pages, sections, len(findings)))
    return findings, lines


def fixture_languages(d):
    """The declared codes of one fixture: its languages.txt, or else its site folders."""
    path = d / 'languages.txt'
    if path.is_file():
        return path.read_text(encoding='utf-8').strip()
    site = d / 'site'
    names = [p.name for p in site.iterdir() if p.is_dir()] if site.is_dir() else []
    return ','.join(sorted(n for n in names if not n.startswith('.')))


def self_test():
    dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    if not dirs:
        die('no fixture directory under %s, so nothing would be tested.' % FIXTURES)
    bad, seen, passes = [], set(), 0
    for d in dirs:
        try:
            expect = [x.strip() for x in
                      (d / 'expect.txt').read_text(encoding='utf-8').splitlines() if x.strip()]
        except OSError:
            bad.append('%s: no expect.txt' % d.name)
            print('FAIL %s: no expect.txt' % d.name)
            continue
        site = (d / 'site').resolve()
        want = sorted(x.replace('{site}', str(site)) for x in expect[1:])
        kinds = {x.split(':', 1)[0] for x in want}
        if expect == ['pass']:
            want_rc = 0
            passes += 1
        elif expect[:1] == ['fail'] and want and kinds <= set(FINDINGS):
            want_rc = 1
            seen |= kinds
        else:
            bad.append('%s: expect.txt is neither `pass` nor `fail` and its findings' % d.name)
            print('FAIL %s: expect.txt is neither `pass` nor `fail` and its findings' % d.name)
            continue
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                              '--main', 'en', '--languages', fixture_languages(d), str(site)],
                             capture_output=True, text=True, timeout=60)
        got = sorted(line for line in run.stdout.splitlines()
                     if line.split(':', 1)[0] in FINDINGS)
        ok = run.returncode == want_rc and got == want
        print('%s %s: expect %s, exit %d, findings %d'
              % ('ok' if ok else 'FAIL', d.name, expect[0], run.returncode, len(got)))
        if not ok:
            bad.append('%s: expect %s with %d findings, exit %d%s'
                       % (d.name, expect[0], len(want), run.returncode,
                          '; stderr: ' + run.stderr.strip() if run.stderr.strip() else ''))
            for line in want:
                if line not in got:
                    bad.append('%s: missing finding: %s' % (d.name, line))
            for line in got:
                if line not in want:
                    bad.append('%s: unexpected finding: %s' % (d.name, line))
    if not passes:
        bad.append('no fixture expects `pass`')
    for kind in FINDINGS:
        if kind not in seen:
            bad.append('no fixture expects a `%s` finding' % kind)
    for b in bad:
        print('   %s' % b)
    print('self-test: fixtures %d, wrong %d' % (len(dirs), len(bad)))
    return 1 if bad else 0


def main(argv):
    usage = __doc__.strip().split('Usage: ')[1]
    if argv == ['--self-test']:
        return self_test()
    summary, main, languages, rest = False, None, None, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--summary':
            summary = True
        elif a == '--main' and i + 1 < len(argv):
            main = argv[i + 1]
            i += 1
        elif a == '--languages' and i + 1 < len(argv):
            languages = argv[i + 1]
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
    if languages is None:
        declared = default_languages()
    else:
        declared = [c for c in re.split(r'[,\s]+', languages) if c]
        if not declared or not all(CODE.fullmatch(c) for c in declared):
            die('--languages %r is not a list of language codes of 2 or 3 lowercase letters.'
                % languages)
    findings, lines = check(site, main, declared)
    if not summary:
        for kind, text in findings:
            print('%s: %s' % (kind, text))
    for line in lines:
        print(line)
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
