#!/usr/bin/env python3
"""Report markdown that LOOKS like a link but that pandoc did not turn into one.

check-links.py asks pandoc which links it found, then checks their targets. Anything that
never parses as a link is invisible to it by construction, and its own header says so for one
form. Five defects have come out of that blind spot, all found by reading:

  [text][label]                 a reference link whose [label]: definition does not exist
  [text(url)]                   the bracket and the paren transposed
  text](url)                    the opening bracket missing
  [text (url)                   the closing bracket missing
  [text](url) after a bare $    two unescaped dollars pair as TeX math and swallow the link

Every one renders as literal bracket text on the published page.

THE RULE, one line: a link that parsed leaves no brackets behind. Render the chapter, then
look for a residual `](` or `][`. Four things are removed first, because each produces that
signature without being a defect:

  fenced code blocks   ```{r} ... ```      R code is full of x[[1]][2]
  HTML comments        <!-- ... -->        pandoc passes them through unparsed
  inline R             `r "https://..."`   Quarto evaluates these, pandoc does not
  rendered code        <code>, <pre>       inline spans that survived as code

A link with its closing bracket missing leaves neither signature, so a second rule finds it.
The check removes every HTML tag from the rendered chapter and decodes the character
references. That leaves the text a reader sees. A finding is an opening `[` that is not
closed before a `(` that opens a target:

  a URL        http://, https:// or mailto:
  a page       a relative path that ends in .qmd or .html, with or without a #fragment
  a section    `#` and then a letter, a digit or `_`
  an image     a path that ends in .png, .jpg, .jpeg, .gif, .svg, .webp, .bmp, .tif or .tiff

The text between the `[` and the `(` holds no bracket and at most 200 characters, and it MAY
cross a line break. `[sic]`, `x[1]` and a `[ ]` checkbox close their bracket, so none of them
is a finding. A transposed link `[text(url)]` matches both rules, so it gives two findings.

OUTPUT. One line per finding, with three fields separated by tabs. The first rule prints the
file, the signature and the rendered HTML around it. The second rule prints `<file>:<line>`,
`missing ]` and the text from the `[` to the target. The line is the source line of the `(`.
The k-th finding with target t is the k-th `(t` in the source with no `]` before it. Fenced
code and HTML comments do not count. Line 0 means that the source holds no such `(t`.

A chapter that the check cannot read is an input error, never a clean chapter. The check stops
at the first one with exit 2 and one message that names the full path of the chapter:
  - the chapter is not UTF-8;
  - pandoc exits other than 0 on the chapter. The message holds the error that pandoc wrote.
    A YAML metadata block at the start of a chapter that does not parse does this.
A missing pandoc, an unknown argument, and `--fixture` or `--pandoc` with no value also stop
the check with exit 2 and one message.

`--self-test` runs the check on every fixture under `checks/fixtures/unparsed-links/`. A
fixture is a small tree with `content/<lang>/<file>.qmd` and `expect.txt`. The first line of
`expect.txt` is `pass`, `fail` or `error`. A fail fixture then lists each expected finding as
its first two fields. An error fixture lists the text that its message MUST hold, with
`{fixture}` for the full path of the fixture. A fail fixture MUST exit 1 with exactly those
findings, and a pass fixture MUST exit 0. An error fixture MUST exit 2 with one message line
and no traceback. The fixtures in REQUIRED MUST exist.

Usage: python3 checks/check-unparsed-links.py [--summary] [--fixture <dir>] [--pandoc <cmd>]
       python3 checks/check-unparsed-links.py --self-test [--pandoc <cmd>]
Exit 0 when every chapter is clean, 1 when any chapter holds an unparsed link, 2 when no
chapter is found or on an input error. The self-test exits 0 when every fixture has its
expected result, 1 when one does not, and 2 on a missing or unusable fixture.
"""
from html import unescape
import pathlib
import re
import shutil
import subprocess
import sys

FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
COMMENT = re.compile(r'<!--.*?-->', re.S)
INLINE_R = re.compile(r'`r\s[^`]*`')
HTML_CODE = re.compile(r'<code.*?</code>|<pre.*?</pre>', re.S)
# Two signatures, because they catch different failures.
#   ]( or ][   the link text closed and the target began, but nothing parsed
#   [ ... ]    a bracketed span whose content looks like a link TARGET. This is the
#              transposed form [text(url)], which contains neither of the above:
#              the brackets and parens nest the wrong way round.
SIGNATURE = re.compile(
    r'\]\(|\]\[|'
    r'\[[^\]]{0,120}?(?:\.qmd|\.html|https?://|\(#)[^\]]{0,120}?\]'
)
# The second rule: an opening [ that is not closed before a ( that opens a target. It reads
# the rendered text with every tag removed, because a parsed link leaves no bracket there.
TAG = re.compile(r'<[^>]*>')
IMAGE_EXT = r'(?:png|jpe?g|gif|svg|webp|bmp|tiff?)'
TARGET = (r'(?:https?://[^\s()]*'
          r'|mailto:[^\s()]*'
          r'|#[\w][^\s()]*'
          r'|[^\s()\[\]]+?\.(?:qmd|html)(?:#[^\s()]*)?(?=[\s)"]|$)'
          r'|[^\s()\[\]]+?\.' + IMAGE_EXT + r'(?=[\s)"]|$))')
MISSING_BRACKET = re.compile(r'\[([^\[\]]{0,200}?)\((' + TARGET + r')', re.I)

HERE = pathlib.Path(__file__).resolve().parent
FIXTURES = HERE / 'fixtures' / 'unparsed-links'
# Each target form of the second rule has a fixture that MUST fail, and so has each form of
# the first rule. Literal brackets in prose and a correct link each have one that MUST pass.
REQUIRED = (
    'fail-missing-bracket-http', 'fail-missing-bracket-https', 'fail-missing-bracket-mailto',
    'fail-missing-bracket-qmd', 'fail-missing-bracket-html', 'fail-missing-bracket-fragment',
    'fail-missing-bracket-image', 'fail-missing-bracket-line-break',
    'fail-reference-undefined', 'fail-transposed', 'fail-opening-bracket', 'fail-math',
    'pass-sic', 'pass-index', 'pass-checkbox', 'pass-link',
    # An input error MUST stop the check, and a chapter with valid metadata MUST pass.
    'error-pandoc-failure', 'error-not-utf8', 'pass-metadata',
)
USAGE = ('Usage: check-unparsed-links.py [--summary] [--fixture <dir>] [--pandoc <cmd>], '
         'or check-unparsed-links.py --self-test [--pandoc <cmd>]')


def stop(message):
    print(f"check-unparsed-links.py: {message}", file=sys.stderr)
    sys.exit(2)


# Every argument is a known flag, or a known option and its value. The first value wins.
args = sys.argv[1:]
flags, values = set(), {}
i = 0
while i < len(args):
    a = args[i]
    if a in ('--summary', '--self-test'):
        flags.add(a)
    elif a in ('--fixture', '--pandoc'):
        if i + 1 == len(args) or args[i + 1].startswith('--'):
            stop(f"{a} needs a value. {USAGE}")
        values.setdefault(a, args[i + 1])
        i += 1
    else:
        stop(f"unknown argument {a}. {USAGE}")
    i += 1

summary = '--summary' in flags
root = pathlib.Path(values.get('--fixture') or '.')
pandoc = (values.get('--pandoc') or '').split() or (['quarto', 'pandoc'] if shutil.which('quarto') else ['pandoc'])
if shutil.which(pandoc[0]) is None:
    stop(f"no pandoc: `{pandoc[0]}` is not a command that can run. The check renders each "
         "chapter with it. Install Quarto or pandoc, or name one with --pandoc <cmd>.")


def strip_fences(text, split=str.splitlines):
    """The text with every fenced line empty. The render splits with str.splitlines. The line
    map of the second rule splits on newlines alone, so its line numbers are the editor's."""
    out, fence = [], None
    for line in split(text):
        m = FENCE.match(line)
        if fence is None and m:
            fence = m.group(2)
            out.append('')
            continue
        if fence is not None:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence):
                fence = None
            out.append('')
            continue
        out.append(line)
    return '\n'.join(out)


def blank_comments(text):
    """The text with every HTML comment blanked and its newlines kept, so line numbers hold."""
    return COMMENT.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text)


def source_line(lines, target, k):
    """The line number of the k-th `(target` in the source that does not follow `]`, or 0."""
    seen = 0
    for n, line in enumerate(lines, 1):
        plain = re.sub(r'\\(.)', r'\1', line)
        for m in re.finditer(re.escape('(' + target), plain):
            if m.start() > 0 and plain[m.start() - 1] == ']':
                continue
            if seen == k:
                return n
            seen += 1
    return 0


def self_test():
    """Run the check on every fixture, and compare each result with its expect.txt."""
    if summary or '--fixture' in values:
        stop("--self-test takes no --summary and no --fixture. "
             "Usage: check-unparsed-links.py --self-test [--pandoc <cmd>]")
    dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    if not dirs:
        stop(f"no fixture folder under {FIXTURES}, so nothing would be tested.")
    for name in REQUIRED:
        if not (FIXTURES / name).is_dir():
            stop(f"no {FIXTURES / name}. That fixture is one of the REQUIRED fixtures.")
    # A missing or unusable fixture input stops the self-test before any fixture runs.
    expects = {}
    for d in dirs:
        p = d / 'expect.txt'
        if not p.is_file():
            stop(f"no {p}. Each fixture needs one, so that its result can be compared.")
        expect = [x.strip() for x in p.read_text(encoding='utf-8').split('\n') if x.strip()]
        kind = expect[0] if expect else ''
        if kind not in ('pass', 'fail', 'error') or not d.name.startswith(kind + '-') \
                or (kind == 'pass') != (len(expect) == 1):
            stop(f"{p} MUST hold `pass` alone, or `fail` and its findings, or `error` and the "
                 "text of its message, as the folder name says.")
        if not list(d.glob('content/*/*.qmd')):
            stop(f"no chapter under {d}/content/<lang>/. The fixture would report a clean tree.")
        expects[d] = expect
    bad, lines = [], []
    for d in dirs:
        expect = expects[d]
        run = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()),
                              '--fixture', str(d), '--pandoc', ' '.join(pandoc)],
                             capture_output=True, text=True, timeout=120)
        if expect[0] == 'error':
            # An input error MUST stop the check with one message line, and no traceback.
            message = run.stderr.strip()
            want = [x.replace('{fixture}', str(d.resolve())) for x in expect[1:]]
            ok = (run.returncode == 2 and 'Traceback' not in run.stderr
                  and len(message.split('\n')) == 1 and all(x in message for x in want))
            lines.append(f"{'ok' if ok else 'FAIL'} {d.name}: expect error, exit 2; "
                         f"exit {run.returncode}, message lines {len(message.splitlines())}")
            if not ok:
                bad.append(f"{d.name}: want exit 2 with one line that holds [{'; '.join(want)}], "
                           f"got exit {run.returncode} with [{message}]")
            continue
        # A child that exits 2 or crashes met an input this function did not check, so the
        # result of that fixture is neither a pass nor a fail.
        if run.returncode == 2 or 'Traceback' in run.stderr:
            stop(f"{d}: the check exited {run.returncode} on this fixture: "
                 f"{' '.join(run.stderr.split())}")
        got = ['\t'.join(x.split('\t')[:2]) for x in run.stdout.split('\n') if x.count('\t') == 2]
        want_rc = 0 if expect[0] == 'pass' else 1
        ok = run.returncode == want_rc and sorted(got) == sorted(expect[1:])
        lines.append(f"{'ok' if ok else 'FAIL'} {d.name}: expect {expect[0]}, findings "
                     f"{len(expect) - 1}; exit {run.returncode}, findings {len(got)}")
        if not ok:
            bad.append(f"{d.name}: want exit {want_rc} with [{'; '.join(expect[1:])}], "
                       f"got exit {run.returncode} with [{'; '.join(got)}]")
    for line in lines:
        print(line)
    for b in bad:
        print(f"   {b}")
    print(f"self-test: fixtures {len(dirs)}, wrong {len(bad)}")
    return 1 if bad else 0


if '--self-test' in flags:
    sys.exit(self_test())

chapters = sorted(root.glob('content/*/*.qmd'))
if not chapters:
    print(f"check-unparsed-links.py: no chapter found under {root.resolve()}/content/<lang>/. "
          "An empty file set would otherwise report a clean tree.", file=sys.stderr)
    sys.exit(2)

findings, missing = [], 0
for chapter in chapters:
    try:
        text = chapter.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        stop(f"{chapter.resolve()} is not UTF-8, so the chapter was not checked: {e.reason} "
             f"at byte {e.start}.")
    source = INLINE_R.sub('RCODE', COMMENT.sub('', strip_fences(text)))
    run = subprocess.run(pandoc + ['-f', 'markdown', '-t', 'html'],
                         input=source, capture_output=True, text=True)
    # A chapter that pandoc fails on has no rendered text to read, so it is not clean.
    if run.returncode != 0:
        stop(f"pandoc exited {run.returncode} on {chapter.resolve()}, so the chapter was not "
             f"checked: {' '.join(run.stderr.split())}")
    html = run.stdout
    rendered = HTML_CODE.sub('', html)
    shown = str(chapter.relative_to(root))
    for match in SIGNATURE.finditer(rendered):
        context = rendered[max(0, match.start() - 45):match.start() + 40].replace('\n', ' ').strip()
        findings.append((shown, match.group(0), context))
    visible = unescape(TAG.sub('', rendered))
    lines = blank_comments(strip_fences(text, lambda t: t.split('\n'))).split('\n')
    seen = {}
    for match in MISSING_BRACKET.finditer(visible):
        target = match.group(2)
        k = seen.get(target, 0)
        seen[target] = k + 1
        findings.append((f"{shown}:{source_line(lines, target, k)}", 'missing ]',
                         ' '.join(match.group(0).split())))
        missing += 1

print(f"files scanned: {len(chapters)}")
print(f"pandoc: {' '.join(pandoc)}")
print(f"links with a missing ]: {missing}")
print(f"unparsed links: {len(findings)}")
if findings and not summary:
    for shown, signature, context in findings:
        print(f"{shown}\t{signature}\t{context}")
sys.exit(1 if findings else 0)
