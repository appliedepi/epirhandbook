#!/usr/bin/env python3
"""Fail on markdown that departs from the default form, in every language.

Check 28. It reads every declared chapter of every language, English and `index.qmd`
included. The definition comes from issue 466, second follow-up, contract P6, P11, Q2, B8 and
F1. Five rules apply, and each finding names its rule:

  heading-form          A heading line MUST be 1 to 6 `#`, exactly one space, then the title
                        (P11). A trailing attribute block `{...}` and trailing spaces are
                        allowed. The detail names the fault:
                          tab       a tab after the hashes
                          spaces    two or more spaces after the hashes
                          no-space  another character straight after the hashes
                          no-title  nothing but spaces after the hashes
  heading-blank-before  A heading line MUST NOT follow a non-blank line (Q2), because pandoc
                        then reads it as paragraph text. The exemptions are below.
  bold-command          A bold span MUST NOT start with `git`, whitespace and a git subcommand
                        (P6), because a command belongs in a code span. The whitespace MAY be
                        one line break. The bold opens with `**` or `__`. No letter or digit
                        MAY follow the subcommand. The match is case-sensitive, so **Git** as
                        a product name passes. SUBCOMMANDS lists the subcommands.
  quoted-call           A call MUST NOT stand in quotes in prose outside code spans (P6),
                        because a call belongs in a code span. The match is case-sensitive.
  bold-form             A bold MUST be one of the three B8 forms: `name`, `lead-in` or
                        `sentence`. A `phrase` bold is a finding. A bold with its colon or
                        closing mark directly after it, spaces skipped, is a finding with
                        the detail `mark-outside` (F1 B9): **NOTE**: and **A sentence**.
                        The colon or mark MUST stand inside the bold.

A run applies the rules that `--rules <rule>[,<rule>...]` names. Without `--rules` it applies
DEFAULT_RULES, which is all five rules. The self-test applies all five rules too.

HEADING LINES (P11). A heading line is a line that starts in column 1 with 1 to 6 `#`
characters. Pandoc need not read it as a heading, so `##Title` is a heading line. A run of 7 or
more `#` is not one, and neither is a `#` after leading spaces.

EXEMPTIONS of heading-blank-before. A heading line directly after one of these lines is no
finding. Pandoc ends a block on each of them and reads the next line as a heading:
  - the line that closes an HTML comment which opened at the start of its line, after at most
    3 spaces;
  - the line that closes a fenced code block;
  - the line that closes the YAML front matter;
  - a heading line that pandoc reads as a heading: `#` to `######`, then a space, a tab or the
    line end, and itself no heading-blank-before finding;
  - a `:::` div fence, which opens or closes a div;
  - a pipe-table line, which starts with `|` after at most 3 spaces and ends with `|`.
The first line of a file has no line before it and is no finding.

QUOTED CALLS. A call is a name, an optional `pkg::` or `pkg:::` prefix, then `(`, the arguments
and `)`. A name starts with an ASCII letter or `.` and holds ASCII letters, digits, `.` and `_`.
The arguments hold no line break, and MAY hold two levels of nested parentheses. So `f()`,
`pkg::f()` and `f(x)` are calls. A non-ASCII letter between the parentheses makes it no call,
so "Stage(Aşama)", a button label with its translation, passes. The quotes MUST enclose the
call and nothing else. These are the quote forms, as opening and closing mark:
  - straight double `"` `"` and straight single `'` `'`;
  - curly double `“` `”` and curly single `‘` `’`;
  - guillemets `«` `»`, with one optional space inside each mark, as French writes them;
  - low-high `„` `“` and `„` `”`;
  - corner brackets `「` `」`.
A single quote is also an apostrophe. So for the two single forms, no letter or digit MAY
stand directly before the opening mark or after the closing mark. A call in a code span,
`"`f(x)`"`, is not a finding.

PROSE. The rules bold-command and quoted-call read the prose of a chapter. These parts are not
prose:
  - the YAML front matter;
  - fenced code: ``` or ~~~, up to 3 spaces of indent;
  - indented code: 4 spaces or a tab of indent after a blank line, outside a list;
  - HTML comments;
  - code spans. A code span never pairs across a blank line.
The heading rules skip the same front matter, fenced code and HTML comments.

BOLD FORMS. The rule bold-form reads each chapter through pandoc, exactly as check 27 does, and
classifies each bold with bold_forms() of checks/check-parity.py. The forms and the
sentence-start rule are in the docstring of that script. The name list is
checks/bold-names.txt beside this script. Pandoc JSON carries no source line, so the check
finds each bold in the source by its text. It looks for the first `**` or `__` after the
previous bold whose letters and digits start with those of the bold text. Where that fails, it
tries the first word alone, and then the exact text. A bold it cannot find reports line 0 and
counts as `unlocated` in the totals line.

INPUTS. The declared languages come from `languages.yml` (`main:` and every `- code:` line).
The stems come from the `.qmd` entries of `book.chapters` in `content/<main>/_quarto.yaml`.

OUTPUT. One line per finding, `<lang> <file>:<line> <rule>[ <detail>] | <text>`. The file is
`content/<lang>/<stem>.qmd`, and the text is a JSON string. Then one line per language, and one
totals line. `--summary` prints the language lines and the totals line only.

`--self-test` runs the check on every fixture under `checks/fixtures/markdown-form/`. A fixture
is a small tree with its own `languages.yml`, `content/` and `expect.txt`. The first line of
`expect.txt` is `pass` or `fail`. A fail fixture lists each expected finding as the part of
its line before ` | `. A fail fixture MUST exit 1 with exactly those findings, and a pass
fixture MUST exit 0 with none. The fixtures in REQUIRED MUST exist. The self-test reads every
input of every fixture before it runs any.

Exit 0 on no finding and 1 on a finding. Exit 2 also when pandoc fails on a chapter. Exit 2 on
a missing or unusable input, with one message that names its full path:
  - the tree is not a folder;
  - no `languages.yml`, or one with no `main:` or with a repeated code;
  - no `content/`, no project file, or a project file with no chapter;
  - a missing chapter file;
  - no name list, or one with no name;
  - no checks/check-parity.py;
  - a file that is not UTF-8.

Usage: python3 checks/check-markdown-form.py [--summary] [--pandoc <cmd>] [--rules <rule>[,...]] [<tree>]   (default: the repository root)
       python3 checks/check-markdown-form.py --self-test
"""
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / 'fixtures' / 'markdown-form'
PROG = 'check-markdown-form.py'
RULES = ('heading-form', 'heading-blank-before', 'bold-command', 'quoted-call', 'bold-form')
# The rules a run applies when --rules names none.
DEFAULT_RULES = RULES
# Each rule has a fixture that MUST fail and one that MUST pass. Each exemption of
# heading-blank-before has a pass fixture, and each quote form has a fail fixture. A colon
# and a closing mark outside a bold each have a fail fixture, and inside a bold a pass fixture
# (F1 B9).
REQUIRED = (
    'fail-heading-form', 'pass-heading-form',
    'fail-blank-before-paragraph', 'fail-blank-before-list', 'pass-blank-before-comment',
    'pass-blank-before-fence', 'pass-blank-before-front-matter', 'pass-blank-before-heading',
    'pass-blank-before-div-fence', 'pass-blank-before-pipe-table',
    'fail-bold-command', 'fail-bold-command-line-break', 'pass-bold-command-git-product',
    'pass-bold-command-code-span',
    'fail-quoted-call-straight-double', 'fail-quoted-call-straight-single',
    'fail-quoted-call-curly-double', 'fail-quoted-call-curly-single',
    'fail-quoted-call-guillemets', 'fail-quoted-call-low-high', 'fail-quoted-call-corner',
    'pass-quoted-call-not-a-call', 'pass-quoted-call-code', 'pass-quoted-call-non-ascii-label',
    'fail-bold-form-phrase', 'fail-bold-form-colon-outside', 'fail-bold-form-mark-outside',
    'pass-bold-form', 'pass-bold-form-mark-inside')


def die(message):
    print('%s: %s' % (PROG, message), file=sys.stderr)
    sys.exit(2)


def parity_module():
    """checks/check-parity.py as a module: the reader of the declared chapters, the pandoc
    call and the bold classifier."""
    path = HERE / 'check-parity.py'
    if not path.is_file():
        die('no %s. Check 28 classifies bold with the code of check 27.' % path)
    spec = importlib.util.spec_from_file_location('check_parity', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.PROG = PROG
    return mod


P = parity_module()

# ---------------------------------------------------------------- heading-form, blank-before

FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
CANDIDATE = re.compile(r'^(#{1,6})(?!#)(.*)$')
PANDOC_HEADING = re.compile(r'^#{1,6}(?:[ \t]|$)')
DIV_FENCE = re.compile(r'^ {0,3}:{3,}')
PIPE_ROW = re.compile(r'^ {0,3}\|.*\|\s*$')
CODE_SPAN_LINE = re.compile(r'(`+)(?:(?!\1).)+?\1')


def headings(text):
    """[(line number, rule, detail, line)] of the two heading rules for one chapter."""
    found = []
    lines = text.split('\n')
    start = 0
    # YAML front matter: a `---` first line, up to the next `---` or `...` line.
    if lines and lines[0].rstrip() == '---':
        for j in range(1, len(lines)):
            if lines[j].rstrip() in ('---', '...'):
                start = j + 1
                break
    fence, comment, block_comment = None, False, False
    # Whether pandoc reads a heading on the next line: after a blank line, or after a line on
    # which pandoc ends its block. The line after the front matter, or line 1, is such a line.
    prev_ok = True
    for n in range(start, len(lines)):
        l = lines[n]
        if not comment:
            m = FENCE.match(l)
            if fence is None and m and len(m.group(1)) <= 3:
                fence = m.group(2)
                prev_ok = False
                continue
            if fence is not None:
                if m and len(m.group(1)) <= 3 and m.group(2)[0] == fence[0] \
                        and len(m.group(2)) >= len(fence) and not m.group(3).strip():
                    fence = None
                    prev_ok = True
                else:
                    prev_ok = False
                continue
        starts_in_comment = comment
        before_ok = prev_ok
        block_closed = False
        # Follow the comment state along the line, outside backtick code spans.
        rest = CODE_SPAN_LINE.sub('', l)
        pos = 0
        while True:
            if comment:
                k = rest.find('-->', pos)
                if k < 0:
                    break
                comment, pos = False, k + 3
                block_closed = block_comment
            else:
                k = rest.find('<!--', pos)
                if k < 0:
                    break
                # An HTML block: the comment opens the line, after at most 3 spaces.
                block_comment = pos == 0 and rest[:k].strip(' ') == '' and k <= 3
                comment, pos = True, k + 4
        c = None if starts_in_comment else CANDIDATE.match(l)
        prev_ok = (not l.strip() or (block_closed and not comment)
                   or (not starts_in_comment and not comment
                       and (DIV_FENCE.match(l) is not None or PIPE_ROW.match(l) is not None))
                   or (c is not None and before_ok and PANDOC_HEADING.match(l) is not None))
        if not c:
            continue
        if not before_ok:
            found.append((n + 1, 'heading-blank-before', '', l))
        after = c.group(2)
        if after.startswith(' ') and after[1:2] not in (' ', '\t', '') and after.strip():
            continue
        if not after.strip():
            kind = 'no-title'
        elif after[0] not in ' \t':
            kind = 'no-space'
        elif '\t' in after[:len(after) - len(after.lstrip(' \t'))]:
            kind = 'tab'
        else:
            kind = 'spaces'
        found.append((n + 1, 'heading-form', kind, l))
    return found


# ---------------------------------------------------------------- prose: bold-command, quoted-call

FENCE_PROSE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
LIST_ITEM = re.compile(r'^\s*([-*+]|\d+[.)])\s+')
CODE_SPAN = re.compile(r'(`+)(?!`)(.+?)(?<!`)\1(?!`)', re.S)
COMMENT = re.compile(r'<!--.*?-->', re.S)


def code_lines(lines):
    """Indexes of the front matter, fenced code and indented code (as check 26 reads them)."""
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
        m = FENCE_PROSE.match(line)
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


def blank_out(m):
    return re.sub(r'[^\n]', ' ', m.group(0))


def prose(text):
    """The text with every part that is not prose replaced by spaces. Line breaks and
    offsets stay, so an offset in the result is an offset in the source."""
    lines = text.split('\n')
    skip = code_lines(lines)
    text = '\n'.join(' ' * len(l) if k in skip else l for k, l in enumerate(lines))
    text = COMMENT.sub(blank_out, text)
    # Code spans per block of non-blank lines, so a span never pairs across a blank line.
    blocks = re.split(r'(\n[ \t]*\n)', text)
    return ''.join(CODE_SPAN.sub(blank_out, b) for b in blocks)


SUBCOMMANDS = ('add|am|bisect|blame|branch|checkout|cherry-pick|clean|clone|commit|config|diff|'
               'fetch|grep|init|log|merge|mv|pull|push|rebase|reflog|remote|reset|restore|revert|'
               'rm|show|stash|status|switch|tag')
BOLD_COMMAND = re.compile(r'(?:(?<![*\\])\*\*|(?<![\w\\])__)git(?:[ \t]+|[ \t]*\n[ \t]*)'
                          r'(?:%s)(?![A-Za-z0-9])' % SUBCOMMANDS)
CALL = (r'(?:[A-Za-z][A-Za-z0-9._]*:::?)?[A-Za-z.][A-Za-z0-9._]*'
        r'\((?:[^()\n]|\((?:[^()\n]|\([^()\n]*\))*\))*\)')
# (opening mark, closing mark, spaces allowed inside the marks, guard). With the guard, no
# letter or digit MAY touch the marks. The single quotes are also apostrophes, so they need
# it. Japanese writes a letter straight after the corner bracket, so the other forms MUST NOT
# have it.
QUOTES = (('"', '"', '', False), ("'", "'", '', True), ('“', '”', '', False),
          ('‘', '’', '', True), ('«', '»', '[ \u00a0\u202f]?', False),
          ('„', '[“”]', '', False), ('「', '」', '', False))
QUOTED_CALL = re.compile('|'.join(
    '%s%s%s%s%s%s%s' % (r'(?<![^\W_])' if guard else '', re.escape(o), sp, CALL, sp,
                        c if c.startswith('[') else re.escape(c),
                        r'(?![^\W_])' if guard else '')
    for o, c, sp, guard in QUOTES))


def non_ascii_letter(call):
    """Whether the parentheses of a matched call hold a non-ASCII letter. Such a call is a
    label with its translation, such as "Stage(Aşama)", and not code."""
    return any(ch.isalpha() and not ch.isascii() for ch in call[call.index('('):])


def prose_rules(text):
    """[(line number, rule, detail, matched text)] of bold-command and quoted-call."""
    p = prose(text)
    found = []
    for rule, rx in (('bold-command', BOLD_COMMAND), ('quoted-call', QUOTED_CALL)):
        for m in rx.finditer(p):
            if rule == 'quoted-call' and non_ascii_letter(m.group(0)):
                continue
            found.append((p.count('\n', 0, m.start()) + 1, rule, '', m.group(0)))
    return found


# ---------------------------------------------------------------- bold-form

OPEN = re.compile(r'(?<![*\\])\*{2,3}(?=[^\s*])|(?<![\w\\])_{2,3}(?=[^\s_])')
# Source markup that the bold text does not show: an HTML tag, a link or image target.
MARKUP = re.compile(r'<(?!https?:|mailto:)/?[A-Za-z][^>\n]*>|\]\([^)\n]*\)|\]\[[^\]\n]*\]'
                    r'|\{[^}\n]*\}')


def norm(s):
    return ''.join(ch for ch in s if ch.isalnum())


def locate(src, texts):
    """The 1-based source line of each bold text, in order; 0 where none is found."""
    lines = src.split('\n')
    infence, fence = [False] * len(lines), None
    for i, l in enumerate(lines):
        m = P.FENCE.match(l)
        code = m is None or len(m.group(1)) > 3
        if fence is None and not code:
            fence = m.group(2)
            infence[i] = True
        elif fence is not None:
            infence[i] = True
            if not code and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) \
                    and not m.group(3).strip():
                fence = None
    opens = []
    for m in OPEN.finditer(src):
        ln = src.count('\n', 0, m.start())
        if not infence[ln]:
            opens.append((m.end(), ln + 1))
    keys = [norm(MARKUP.sub('', src[p:p + 600])) for p, _ in opens]
    out, cur = [], 0
    for t in texts:
        hit = 0
        # The first 40 letters and digits, then the first word alone: a bold that a grid
        # table cell splits over two source lines holds cell borders in its source. A bold of
        # punctuation alone (**%<>%**) has no letter or digit, so its exact text is compared.
        tests = [lambda j, w=norm(t)[:40]: w and keys[j].startswith(w),
                 lambda j, w=norm((t.split() or [''])[0]): w and keys[j].startswith(w),
                 lambda j: not norm(t) and src[opens[j][0]:opens[j][0] + len(t) + 8]
                 .replace('`', '').replace('\\', '').startswith(t)]
        for test in tests:
            for rng in (range(cur, len(opens)), range(0, len(opens))):
                for j in rng:
                    if test(j):
                        hit = j + 1
                        break
                if hit:
                    break
            if hit:
                break
        if hit:
            out.append(opens[hit - 1][1])
            cur = hit
        else:
            out.append(0)
    return out


def bold_form(path, pandoc):
    """([(line number, 'bold-form', detail, text)] of the phrase and mark-outside bolds, bolds,
    unlocated, None) for one chapter, or (None, 0, 0, why). The detail of a mark-outside bold
    is `mark-outside`, and that of a phrase bold is empty."""
    doc, src, why = P.pandoc_json(path, pandoc)
    if why:
        return None, 0, 0, why
    bolds = P.bold_forms(doc['blocks'])
    where = locate(src, [t for _, t in bolds])
    found = [(n, 'bold-form', '' if f == 'phrase' else f, t)
             for (f, t), n in zip(bolds, where) if f in ('phrase', 'mark-outside')]
    return found, len(bolds), sum(1 for n in where if n == 0), None


# ---------------------------------------------------------------- the run

def load(root):
    """Every input of one tree: (codes, [(code, stem, path)]). The check and the self-test both
    call it, so the self-test validates exactly what a run reads. Stops with exit 2 and one
    message on the first missing or unusable input."""
    if not os.path.isdir(root):
        die('%s is not a folder. It is the repository tree to check.' % os.path.abspath(root))
    main_lang, codes, stems = P.read_declared(root)
    files = []
    for c in codes:
        for s in stems:
            p = os.path.join(root, 'content', c, s + '.qmd')
            if not os.path.isfile(p):
                die('no %s. %s declares that chapter.'
                    % (os.path.abspath(p), os.path.abspath(
                        os.path.join(root, 'content', main_lang, '_quarto.yaml'))))
            P.read_text(p)
            files.append((c, s, p))
    P.load_names()
    return codes, files


def scan(path, pandoc, rules):
    text = P.read_text(path)
    found, bolds, unlocated, why = bold_form(path, pandoc)
    if why:
        return None, 0, 0, why
    found = [f for f in headings(text) + prose_rules(text) + found if f[1] in rules]
    found.sort(key=lambda f: (f[0], RULES.index(f[1])))
    return found, bolds, unlocated, None


def check(root, summary, pandoc, rules):
    """Print the findings and the totals of one tree. Returns the exit status."""
    codes, files = load(root)
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda f: scan(f[2], pandoc, rules), files))
    errors = []
    total = {r: 0 for r in RULES}
    per = {c: {'files': 0, 'findings': 0} for c in codes}
    bolds = unlocated = 0
    for (code, stem, path), (found, nb, nu, why) in zip(files, results):
        if why:
            errors.append('%s: %s %s' % (PROG, os.path.abspath(path), why))
            continue
        per[code]['files'] += 1
        bolds += nb
        unlocated += nu
        for n, rule, detail, text in found:
            total[rule] += 1
            per[code]['findings'] += 1
            if not summary:
                print('%s content/%s/%s.qmd:%d %s%s | %s'
                      % (code, code, stem, n, rule, ' ' + detail if detail else '',
                         json.dumps(text, ensure_ascii=False)))
    for c in codes:
        print('markdown form %s: files %d, findings %d' % (c, per[c]['files'], per[c]['findings']))
    off = [r for r in RULES if r not in rules]
    print('markdown form: languages %d, files %d, pandoc %s, findings %d (%s%s), bolds read %d, '
          'unlocated %d'
          % (len(codes), len(files), ' '.join(pandoc), sum(total.values()),
             ', '.join('%s %d' % (r, total[r]) for r in RULES if r in rules),
             '; not run: ' + ', '.join(off) if off else '', bolds, unlocated))
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        return 2
    return 1 if sum(total.values()) else 0


FINDING = re.compile(r'^(\S+ \S+:\d+ .+?) \| ')


def self_test(pandoc):
    dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    if not dirs:
        die('no fixture folder under %s, so nothing would be tested.' % FIXTURES)
    for n in REQUIRED:
        if not (FIXTURES / n).is_dir():
            die('no %s. That fixture is one of the REQUIRED fixtures.' % (FIXTURES / n))
    # A missing or unusable fixture input stops the self-test before any fixture runs.
    expects = {}
    for d in dirs:
        p = d / 'expect.txt'
        if not p.is_file():
            die('no %s. Each fixture needs one, so that its result can be compared.' % p)
        expect = [x.strip() for x in P.read_text(str(p)).split('\n') if x.strip()]
        kind = expect[0] if expect else ''
        if kind not in ('pass', 'fail') or not d.name.startswith(kind + '-') \
                or (kind == 'pass') != (len(expect) == 1):
            die('%s MUST hold `pass` alone, or `fail` and its findings, as the folder name '
                'says.' % p)
        load(str(d))
        expects[d] = expect
    bad, lines = [], []
    for d in dirs:
        expect = expects[d]
        kind = expect[0]
        # Every rule runs on a fixture, whatever DEFAULT_RULES holds.
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--pandoc',
                              shlex.join(pandoc), '--rules', ','.join(RULES), str(d)],
                             capture_output=True, text=True, timeout=120)
        # A child that exits 2 or crashes met an input that load() did not check, so the
        # fixture is unusable, and its result is not a pass or a fail.
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
            bad.append('%s: want exit %d with [%s], got exit %d with [%s]'
                       % (d.name, want_rc, '; '.join(expect[1:]), run.returncode,
                          '; '.join(got)))
    for line in lines:
        print(line)
    for b in bad:
        print('   %s' % b)
    print('self-test: fixtures %d, wrong %d' % (len(dirs), len(bad)))
    return 1 if bad else 0


def main(argv):
    usage = __doc__.strip().split('Usage: ')[1]
    summary, pandoc, rest, self, rules = False, None, [], False, DEFAULT_RULES
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--summary':
            summary = True
        elif a == '--self-test':
            self = True
        elif a == '--pandoc' and i + 1 < len(argv):
            pandoc = shlex.split(argv[i + 1])
            i += 1
        elif a == '--rules' and i + 1 < len(argv):
            rules = tuple(r.strip() for r in argv[i + 1].split(',') if r.strip())
            if not rules or any(r not in RULES for r in rules):
                die('--rules %r: each rule MUST be one of %s.' % (argv[i + 1], ', '.join(RULES)))
            i += 1
        elif a.startswith('-'):
            die('unknown argument %s. Usage: %s' % (a, usage))
        else:
            rest.append(a)
        i += 1
    if len(rest) > 1 or (self and (rest or summary)):
        die('expected at most one tree, and no tree with --self-test. Usage: %s' % usage)
    pandoc = pandoc or P.default_pandoc()
    if self:
        return self_test(pandoc)
    return check(os.path.abspath(rest[0]) if rest else str(ROOT), summary, pandoc, rules)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
