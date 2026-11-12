#!/usr/bin/env python3
"""Fail on a raw-HTML placeholder such as `<name>` in the prose of any language.

Check 26. A browser reads `<name>` as an unknown HTML element and shows nothing, so the
reader loses the word. Write the placeholder in a code span, `` `<name>` ``, or escape it as
`\\<name>`. The check reads every language, English included. Check 24 skips English, so
this check is separate from it. The definition comes from issue 466.

A finding is `<` followed by a word and `>`. The word starts with a letter or `_` and holds
letters, digits, `_`, `.` and `-`. The letters MAY be non-ASCII, so `<имя>` is a finding.
A `<` with a backslash before it is escaped and is not a finding.

These contexts are not prose, so the check skips them:
  - the YAML front matter;
  - fenced code (``` or ~~~, up to 3 spaces of indent), the chunk options included;
  - indented code: a line with 4 spaces or a tab of indent after a blank line, outside a
    list. The indented or blank lines that follow it are code too. In a list, such a line
    continues the list item and is prose;
  - inline code spans, also across the lines of one block of non-blank lines. A span never
    pairs across a blank line;
  - HTML comments, also across lines;
  - a real HTML element, compared case-insensitively. The list is HTML_ELEMENTS below:
    a abbr b br center code del details div em font h1 h2 h3 h4 h5 h6 hr i iframe img ins
    kbd li mark ol p pre s small span strong sub summary sup table tbody td th thead tr u ul.

The languages are the `code:` entries of the `languages:` list in `languages.yml`, in file
order. The chapters of one language are the `.qmd` entries of `content/<code>/_quarto.yaml`.
The check uses the Python standard library only, so it reads both files with line regular
expressions, as check 25 reads `main:`. These line readers need the block style that both
files use: one `- code:` line per language, and one `.qmd` name per chapter line.

Output: one line per finding, `<code> <file>:<line> <names> | <line text>`. Then one line per
language with its count of scanned files and of findings, and the file names. Then one totals
line. `--summary` prints the language lines without the file names, and no finding.

`--self-test` runs the check on every fixture under `checks/fixtures/raw-html/`. A fixture is
a small tree with its own `languages.yml` and `content/`, and an `expect.txt`. The first line
of `expect.txt` is `pass` or `fail`. A fail fixture lists each expected finding on its own
line, as `<code> <file>:<line> <names>`. A fail fixture MUST exit 1 with exactly those
findings, and a pass fixture MUST exit 0 with no finding. The fixtures in REQUIRED MUST exist.
Before it runs any fixture, the self-test validates every input of every fixture, with the
same code as a run. These are the inputs of one fixture `<f>`:
  - `<f>/expect.txt`;
  - `<f>/languages.yml`;
  - the folder `<f>/content/`;
  - `<f>/content/<code>/_quarto.yaml`, for each code of `<f>/languages.yml`;
  - `<f>/content/<code>/<chapter>`, for each chapter of that `_quarto.yaml`.
A missing or unusable input stops the self-test with exit 2. So does a fixture on which the
check exits 2 or crashes, because that fixture has an input that this list misses.

Exit 0 on no finding and 1 on any finding. Exit 2 on a missing or unusable input, with one
message that names its full path:
  - the tree is not a folder;
  - no `languages.yml`, or one that declares no language, a code that is not 2 or 3
    lowercase letters, a code twice, or a list entry with no `code:` line;
  - no `content/` folder;
  - no `content/<code>/_quarto.yaml` for a declared code, or one that declares no chapter;
  - a declared chapter file that does not exist;
  - a file that cannot be read as UTF-8;
  - with `--self-test`: no fixture folder, a missing REQUIRED fixture, a missing or
    malformed `expect.txt`, any input above of any fixture, or the backstop above.

Usage: python3 checks/check-raw-html.py [--summary] [<tree>]   (default: the repository root)
       python3 checks/check-raw-html.py --self-test
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / 'fixtures' / 'raw-html'
PROG = 'check-raw-html.py'
# The fixtures that R4 names. Each excluded context has a pass fixture, and each place a
# placeholder can hide in has a fail fixture.
REQUIRED = ('fail-prose', 'fail-table-cell', 'fail-heading', 'fail-non-ascii',
            'pass-fenced-code', 'pass-indented-code', 'pass-code-span', 'pass-html-comment',
            'pass-html-tag')

HTML_ELEMENTS = set(
    "a abbr b br center code del details div em font h1 h2 h3 h4 h5 h6 hr i iframe img ins "
    "kbd li mark ol p pre s small span strong sub summary sup table tbody td th thead tr u ul"
    .split())
NAME = re.compile(r'(?<!\\)<([^\W\d]|_)([\w.\-]*)>')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
LIST_ITEM = re.compile(r'^\s*([-*+]|\d+[.)])\s+')
CODE_SPAN = re.compile(r'(`+)(?!`)(.+?)(?<!`)\1(?!`)', re.S)
COMMENT = re.compile(r'<!--.*?-->', re.S)
CHAPTER = re.compile(r'^\s*-?\s*(?:part:\s*)?["\']?([\w.\-]+\.qmd)["\']?\s*(?:#.*)?$')
TOP_KEY = re.compile(r'^[^\s#-][^:]*:')
ENTRY = re.compile(r'^(\s*)-(\s|$)')
CODE_KEY = re.compile(r'''^\s*(?:-\s+)?code:\s*["']?([^"'\s#]*)["']?\s*(?:#.*)?$''')
FINDING = re.compile(r'^(\S+ \S+:\d+ .+?) \| ')


def die(msg):
    print('%s: %s' % (PROG, msg), file=sys.stderr)
    sys.exit(2)


def read(path):
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        die('no %s.' % path)
    except (OSError, UnicodeDecodeError) as e:
        die('%s cannot be read as UTF-8: %s' % (path, e))


def languages(path):
    """The codes of the `languages:` list in one languages.yml, in file order."""
    if not path.is_file():
        die('no %s. That file declares the languages to check.' % path)
    codes, entries, indent, inside = [], 0, None, False
    for line in read(path).split('\n'):
        if TOP_KEY.match(line):
            inside = line.split(':', 1)[0].strip() == 'languages'
            continue
        if not inside:
            continue
        m = ENTRY.match(line)
        if m and (indent is None or len(m.group(1)) == indent):
            indent = len(m.group(1))
            entries += 1
        m = CODE_KEY.match(line)
        if m:
            code = m.group(1)
            if not re.fullmatch(r'[a-z]{2,3}', code):
                die('%s has the code %r. A code is 2 or 3 lowercase letters.' % (path, code))
            if code in codes:
                die('%s declares the code %s twice.' % (path, code))
            codes.append(code)
    if not codes:
        die('%s declares no language in a block-style `languages:` list, so nothing would '
            'be checked.' % path)
    if entries != len(codes):
        die('%s: the `languages:` list has entries %d and `code:` lines %d. Each entry needs '
            'one `code:` line.' % (path, entries, len(codes)))
    return codes


def chapters(quarto):
    """The `.qmd` names of one project file, in file order."""
    if not quarto.is_file():
        die('no %s. That project file lists the chapters of its language.' % quarto)
    out = []
    for line in read(quarto).split('\n'):
        m = CHAPTER.match(line)
        if m and m.group(1) not in out:
            out.append(m.group(1))
    if not out:
        die('%s declares no .qmd chapter, so nothing would be checked.' % quarto)
    return out


def blank_out(m):
    return re.sub(r'[^\n]', ' ', m.group(0))


def code_lines(lines):
    """Indexes of the front matter, fenced code and indented code."""
    skip = set()
    start = 0
    if lines and lines[0].strip() == '---':
        for k in range(1, len(lines)):
            if lines[k].strip() in ('---', '...'):
                skip.update(range(k + 1))
                start = k + 1
                break
    fence = None
    in_list = False
    in_indented = False
    prev_blank = True
    for k in range(start, len(lines)):
        line = lines[k]
        m = FENCE.match(line)
        if fence is not None:
            skip.add(k)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not m.group(2).strip():
                fence = None
                prev_blank = False
            continue
        if m:
            fence = m.group(1)
            skip.add(k)
            in_indented = False
            continue
        blank = not line.strip()
        indented = line.startswith('    ') or line.startswith('\t')
        if in_indented:
            if blank or indented:
                skip.add(k)
                prev_blank = blank
                continue
            in_indented = False
        if blank:
            prev_blank = True
            continue
        if indented and prev_blank and not in_list:
            in_indented = True
            skip.add(k)
            prev_blank = False
            continue
        if LIST_ITEM.match(line):
            in_list = True
        elif not indented:
            in_list = False
        prev_blank = False
    return skip


def findings(text):
    """(line number, names, line text) for each line of one chapter with a placeholder."""
    lines = text.split('\n')
    skip = code_lines(lines)
    text = '\n'.join('' if k in skip else line for k, line in enumerate(lines))
    text = COMMENT.sub(blank_out, text)
    # Code spans per block of non-blank lines, so a span never pairs across a blank line.
    blocks = re.split(r'(\n[ \t]*\n)', text)
    text = ''.join(CODE_SPAN.sub(blank_out, b) for b in blocks)
    out = []
    for k, line in enumerate(text.split('\n')):
        names = [m.group(0) for m in NAME.finditer(line)
                 if (m.group(1) + m.group(2)).lower() not in HTML_ELEMENTS]
        if names:
            out.append((k + 1, ' '.join(names), lines[k].strip()))
    return out


def load(root):
    """Every input the check reads in one tree: (codes, {code: [(file, text), ...]}).

    It stops with exit 2 and one message on the first missing or unusable input. The check
    and the self-test both call it, so the self-test validates exactly what a run reads.
    """
    if not root.is_dir():
        die('%s is not a folder. It is the repository tree to check.' % root)
    codes = languages(root / 'languages.yml')
    content = root / 'content'
    if not content.is_dir():
        die('no %s. That folder holds the chapters of every language.' % content)
    texts = {}
    for code in codes:
        quarto = content / code / '_quarto.yaml'
        texts[code] = []
        for f in chapters(quarto):
            path = content / code / f
            if not path.is_file():
                die('no %s. %s declares that chapter.' % (path, quarto))
            texts[code].append((f, read(path)))
    return codes, texts


def check(root, summary):
    """Print the findings and the summary of one tree. Returns the exit status."""
    codes, texts = load(root)
    scanned = {code: [f for f, _ in texts[code]] for code in codes}
    per, total, names = {}, 0, 0
    for code in codes:
        per[code] = 0
        for f, text in texts[code]:
            for n, found, line in findings(text):
                if not summary:
                    print('%s %s:%d %s | %s' % (code, f, n, found, line))
                per[code] += 1
                names += len(found.split())
        total += per[code]
    for code in codes:
        files = scanned[code]
        print('scanned %s: files %d, lines with a placeholder %d%s'
              % (code, len(files), per[code], '' if summary else ': ' + ' '.join(files)))
    print('raw html: languages %d, files %d, total %d lines, %d placeholders'
          % (len(codes), sum(len(v) for v in scanned.values()), total, names))
    return 1 if total else 0


def self_test():
    dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    if not dirs:
        die('no fixture folder under %s, so nothing would be tested.' % FIXTURES)
    # A missing or unusable fixture input stops the self-test before any fixture runs.
    for n in REQUIRED:
        if not (FIXTURES / n).is_dir():
            die('no %s. That fixture is one of the REQUIRED fixtures.' % (FIXTURES / n))
    expects = {}
    for d in dirs:
        path = d / 'expect.txt'
        if not path.is_file():
            die('no %s. Each fixture needs one, so that its result can be compared.' % path)
        expect = [x.strip() for x in read(path).split('\n') if x.strip()]
        kind = expect[0] if expect else ''
        if kind not in ('pass', 'fail') or not d.name.startswith(kind + '-') \
                or (kind == 'pass') != (len(expect) == 1):
            die('%s MUST hold `pass` alone, or `fail` and its findings, as the folder name '
                'says.' % path)
        load(d)
        expects[d] = expect
    # The lines print after the last fixture, so that a backstop stop prints one line only.
    bad, lines = [], []
    for d in dirs:
        expect = expects[d]
        kind = expect[0]
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(d)],
                             capture_output=True, text=True, timeout=60)
        # The backstop: a child that exits 2 or crashes met an input that load() did not
        # check, so the fixture is unusable, and its result is not a pass or a fail.
        if run.returncode == 2 or 'Traceback' in run.stderr:
            die('%s: the check exited %d on this fixture: %s'
                % (d, run.returncode, ' '.join(run.stderr.split())))
        got = [m.group(1) for m in map(FINDING.match, run.stdout.split('\n')) if m]
        want_rc = 0 if kind == 'pass' else 1
        ok = run.returncode == want_rc and sorted(got) == sorted(expect[1:])
        lines.append('%s %s: expect %s, findings %d; exit %d, findings %d'
                     % ('ok' if ok else 'FAIL', d.name, kind, len(expect) - 1,
                        run.returncode, len(got)))
        if not ok:
            bad.append('%s: want exit %d with [%s], got exit %d with [%s]%s'
                       % (d.name, want_rc, '; '.join(expect[1:]), run.returncode,
                          '; '.join(got),
                          '; stderr: ' + run.stderr.strip() if run.stderr.strip() else ''))
    for line in lines:
        print(line)
    for b in bad:
        print('   %s' % b)
    print('self-test: fixtures %d, wrong %d' % (len(dirs), len(bad)))
    return 1 if bad else 0


def main(argv):
    usage = __doc__.strip().split('Usage: ')[1]
    if argv == ['--self-test']:
        return self_test()
    summary = '--summary' in argv
    rest = [a for a in argv if a != '--summary']
    for a in rest:
        if a.startswith('-'):
            die('unknown argument %s. Usage: %s' % (a, usage))
    if len(rest) > 1:
        die('expected at most one tree. Usage: %s' % usage)
    return check(Path(rest[0]).absolute() if rest else ROOT, summary)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
