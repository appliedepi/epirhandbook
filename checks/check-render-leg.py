#!/usr/bin/env python3
"""Fail a render leg whose log carries an R warning or error, or whose pages leak render output.

Check 17. It runs in each render leg of `.github/workflows/build-deploy.yml`, after the render.

The book's images load an R profile that writes one line to stderr for each R warning that
reaches knitr, and one line for each error that an `error=TRUE` chunk captures:

    EHB-WARNING<TAB><input file><TAB><chunk label><TAB><message>
    EHB-ERROR<TAB><input file><TAB><chunk label><TAB><message>

The log colours these lines, so the check removes ANSI escape codes before it reads a line.

ALLOWED names four chunks that show a warning or an error on purpose, by file, chunk label and
kind. The check fails on each of these:

1. An `EHB-WARNING` or `EHB-ERROR` line that ALLOWED does not name.
2. A log with no line for one of the chunks in ALLOWED. Each one always raises its warning or
   error, so a log without it shows that the R profile did not run in that chunk's image. Then
   no warning in that image was logged either. writing_functions, missing_data and ggplot_tips
   render in three different images.
3. An element with the class `cell-output-stderr` in a page. Quarto puts the messages and the
   warnings that a chunk prints into that element. The page of an ALLOWED warning chunk MAY
   carry one such element for each allowed message, when its text is that message.
4. A render-machine path in a page, from LEAKS.

Exit 0 when nothing fails, 1 when something fails, and 2 when an input is missing or empty.

Usage: python3 checks/check-render-leg.py <html_outputs> <log>
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# The chunks that show a warning or an error on purpose: (file, chunk label, kind). Each
# language carries the same label, because check 3 copies the fence line from the English.
ALLOWED = (
    ('writing_functions.qmd', 'error-missing-argument', 'ERROR'),
    ('writing_functions.qmd', 'error-stop', 'ERROR'),
    ('missing_data.qmd', 'warning-coercion-demo', 'WARNING'),
    ('ggplot_tips.qmd', 'warning-na-translate-demo', 'WARNING'),
)

# Paths of the render machine. /tmp/Rtmp is the R session temporary folder, /home/runner is
# the GitHub runner home, and /book/ is where build_all_chapters.sh mounts the repository.
# /book/ also occurs inside URLs, such as https://git-scm.com/book/. So it counts only when no
# host or path character comes before it. The other two never occurred inside a URL in the
# English render of 2026-10-01, so they match as plain strings.
LEAKS = (
    ('/tmp/Rtmp', re.compile(re.escape('/tmp/Rtmp'))),
    ('/home/runner', re.compile(re.escape('/home/runner'))),
    ('/book/', re.compile(r'(?<![A-Za-z0-9._~%-])/book/')),
)

# A CSI sequence such as ESC[31m, or any other two-byte ESC sequence.
ANSI = re.compile(r'\x1b(?:\[[0-?]*[ -/]*[@-~]|[@-Z\\-_])')
EHB = re.compile(r'EHB-(WARNING|ERROR)')
FIELDS = re.compile(r'EHB-(WARNING|ERROR)\t([^\t]*)\t([^\t]*)\t(.*)')


def die(msg):
    print('check-render-leg: %s' % msg, file=sys.stderr)
    sys.exit(2)


def squash(text):
    return ' '.join(text.split())


class StderrCells(HTMLParser):
    """Collect the text of each element whose class list holds cell-output-stderr."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells, self.open, self.depth, self.parts = [], None, 0, []

    def handle_starttag(self, tag, attrs):
        if self.open:
            self.depth += tag == self.open
            return
        for name, value in attrs:
            if name == 'class' and value and 'cell-output-stderr' in value.split():
                self.open, self.depth, self.parts = tag, 1, []

    def handle_endtag(self, tag):
        if self.open and tag == self.open:
            self.depth -= 1
            if self.depth == 0:
                self.cells.append(squash(''.join(self.parts)))
                self.open = None

    def handle_data(self, data):
        if self.open:
            self.parts.append(data)


def read_log(log):
    """Return the failures in the log, the ALLOWED entries it carries, and the allowed
    warning messages by page stem."""
    failures, seen, messages = [], set(), {}
    text = log.read_text(encoding='utf-8', errors='replace')
    for number, raw in enumerate(text.splitlines(), 1):
        line = ANSI.sub('', raw)
        if not EHB.search(line):
            continue
        m = FIELDS.search(line)
        if not m:
            failures.append('%s line %d: an EHB line that does not have four fields: %s'
                            % (log, number, line.strip()))
            continue
        kind, source, label, message = m.groups()
        entry = (Path(source).name, label, kind)
        if entry in ALLOWED:
            seen.add(entry)
            if kind == 'WARNING':
                messages.setdefault(Path(source).stem, set()).add(squash(message))
            continue
        where = '%s [%s] (%s line %d)' % (source, label, log, number)
        failures.append('R %s in %s: %s' % (kind.lower(), where, message.strip()))
    return failures, seen, messages


def allowed_cell(cell, allowed):
    """The allowed message that this stderr text shows, or None."""
    for message in allowed:
        if re.fullmatch(r'Warning(?: in .+?)?: ' + re.escape(message), cell):
            return message
    return None


def read_pages(pages, root, messages):
    """Return the failures in the rendered pages."""
    failures = []
    for page in pages:
        text = page.read_text(encoding='utf-8', errors='replace')
        shown = page.relative_to(root)
        parser = StderrCells()
        parser.feed(text)
        parser.close()
        left = set(messages.get(page.stem, ()))
        bad = 0
        for cell in parser.cells:
            message = allowed_cell(cell, left)
            if message is None:
                bad += 1
            else:
                left.discard(message)
        if bad:
            failures.append('%s: %d cell-output-stderr element(s), output a chunk sent to stderr'
                            % (shown, bad))
        for name, pattern in LEAKS:
            n = len(pattern.findall(text))
            if n:
                failures.append('%s: the render path %s appears %d time(s)' % (shown, name, n))
    return failures


def main(argv):
    if len(argv) != 2:
        die('expected 2 arguments. Usage: %s' % __doc__.strip().split('Usage: ')[1])
    root, log = Path(argv[0]), Path(argv[1])
    if not root.is_dir():
        die('%s is not a directory. It is the output folder of the render.' % root)
    if not log.is_file():
        die('%s is missing. It is the log of the render, which carries the EHB lines.' % log)
    if log.stat().st_size == 0:
        die('%s is empty. A render always writes to its log, so the tee did not run.' % log)
    pages = sorted(root.rglob('*.html'))
    if not pages:
        die('%s holds no .html file, so the render wrote no page.' % root)

    failures, seen, messages = read_log(log)
    for entry in ALLOWED:
        if entry not in seen:
            failures.append('%s: no EHB-%s line for %s [%s]. That chunk always raises it, so '
                            'the R profile that logs warnings did not run in its image.'
                            % (log, entry[2], entry[0], entry[1]))
    failures += read_pages(pages, root, messages)

    for f in failures:
        print(f)
    print('render leg: %d page(s), %d failure(s)' % (len(pages), len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
