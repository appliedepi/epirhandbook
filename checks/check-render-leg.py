#!/usr/bin/env python3
"""Fail a render leg whose log carries an R warning or error, or whose pages leak render output.

Check 17. It runs in each render leg of `.github/workflows/build-deploy.yml`, after the render.

The book's images load an R profile that writes one line to stderr for each R warning that
reaches knitr, and one line for each error that an `error=TRUE` chunk captures:

    EHB-WARNING<TAB><input file><TAB><chunk label><TAB><message>
    EHB-ERROR<TAB><input file><TAB><chunk label><TAB><message>

The log colours these lines, so the check removes ANSI escape codes before it reads a line.

ALLOWED names seven chunks that raise a warning or an error that the check accepts, by file,
chunk label and kind. PREFIXES gives the accepted message starts for some of these chunks. The
check fails on each of these:

1. An `EHB-WARNING` or `EHB-ERROR` line that ALLOWED does not name.
2. A log with no line for one of the chunks in ALLOWED. Each one always raises its warning or
   error, so a log without it shows that the R profile did not run in that chunk's image. Then
   no warning in that image was logged either. writing_functions, missing_data and ggplot_tips
   render in three different images.
3. A line for a chunk in PREFIXES whose message starts with none of the prefixes of that chunk.
4. A log with no line for one of the prefixes in PREFIXES.
5. An element with the class `cell-output-stderr` in a page. Quarto puts the messages and the
   warnings that a chunk prints into that element. The page of an ALLOWED warning chunk MAY
   carry one such element for each allowed message, when its text is that message. A chunk in
   PREFIXES gets no such allowance, so its page MUST NOT show its warnings. A page in
   NOTES MAY carry any number of elements whose text is only lines that NOTES gives for it.
6. A render-machine path in a page, from LEAKS.
7. A level-1 heading with an id on a page. Quarto writes the chapter title as an h1 with no id,
   so an h1 with one is text that pandoc read as a heading: most often the header row of a
   grid table that pandoc could not parse. Quarto numbers it as a chapter.
8. An h2 whose number does not start with the page's chapter number. A stray chapter heading
   above it renumbers it, so English `basics`, chapter 3, showed a section 12.1.

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
    # Remove when UpSetR > 1.4.1 or ggupset > 0.4.1 stop warning. See PREFIXES.
    ('combination_analysis.qmd', 'combination_header', 'WARNING'),
    ('combination_analysis.qmd', 'combination_upsetr', 'WARNING'),
    # The page shows on purpose that fisher.test() fails on this 8 x 2 table. See PREFIXES.
    ('tables_descriptive.qmd', 'fisher-exact-fails', 'ERROR'),
)

# The message starts that an ALLOWED chunk MUST show in the log, and the only ones it MAY show
# there. The page MUST NOT show a warning from here. A chunk that is not a key here MAY show
# any message. The two combination_analysis entries are the ggplot2 deprecation warnings that
# ggupset 0.4.1 and UpSetR 1.4.1 raised in epirhandbook-data-viz:2.9 on 2026-10-05. combination_ggupset raises none, because ggplot2
# gives each deprecation warning once per session and combination_header raises it first.
# Remove when UpSetR > 1.4.1 or ggupset > 0.4.1 stop warning.
PREFIXES = {
    ('combination_analysis.qmd', 'combination_header', 'WARNING'): (
        'Using `size` aesthetic for lines was deprecated in ggplot2 3.4.0.',
    ),
    ('combination_analysis.qmd', 'combination_upsetr', 'WARNING'): (
        '`aes_string()` was deprecated in ggplot2 3.0.0.',
        'The `size` argument of `element_line()` is deprecated as of ggplot2 3.4.0.',
    ),
    # fisher.test() stops with this error on the age_cat x outcome table, even with
    # workspace = 2e8. The page shows the error on purpose, and the prose explains it.
    # Another error in this chunk fails.
    ('tables_descriptive.qmd', 'fisher-exact-fails', 'ERROR'): (
        'FEXACT error 7',
    ),
}

# Messages that a page MAY show, by page stem. ggtree 4.2.0 gheatmap() adds its own y and fill
# scales. So the gheatmap() chunks of phylogenetic_trees print "Scale for y is already present"
# and the same message for fill. Remove this allowance when ggtree stops adding those scales.
NOTES = {
    'phylogenetic_trees': (
        'Scale for y is already present.',
        'Adding another scale for y, which will replace the existing scale.',
        'Scale for fill is already present.',
        'Adding another scale for fill, which will replace the existing scale.',
    ),
}

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
    """Return the failures in the log, the ALLOWED entries and the PREFIXES it carries, and
    the allowed warning messages by page stem."""
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
        where = '%s [%s] (%s line %d)' % (source, label, log, number)
        if entry in PREFIXES:
            prefix = next((p for p in PREFIXES[entry] if squash(message).startswith(p)), None)
            if prefix is None:
                failures.append('R %s in %s, with a message that PREFIXES does not give: %s'
                                % (kind.lower(), where, message.strip()))
                continue
            seen.add(entry + (prefix,))
        if entry in ALLOWED:
            seen.add(entry)
            # A PREFIXES warning is allowed in the log only. Its page MUST NOT show it.
            if kind == 'WARNING' and entry not in PREFIXES:
                messages.setdefault(Path(source).stem, set()).add(squash(message))
            continue
        failures.append('R %s in %s: %s' % (kind.lower(), where, message.strip()))
    return failures, seen, messages


class Headings(HTMLParser):
    """The ids of the h1 elements, the chapter number, and the data-number of each h2.

    The chapter number is the one inside the page title, the h1 with the class title. The
    breadcrumb carries a .chapter-number too, and comes first in the page.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1_ids, self.h2_numbers, self.chapter = [], [], None
        self.in_title, self.in_number, self.number = False, False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get('class') or '').split()
        if tag == 'h1' and a.get('id'):
            self.h1_ids.append(a['id'])
        if tag == 'h1' and 'title' in classes:
            self.in_title = True
        if tag == 'h2' and a.get('data-number'):
            self.h2_numbers.append(a['data-number'])
        if tag == 'span' and 'chapter-number' in classes and self.in_title \
                and self.chapter is None:
            self.in_number, self.number = True, []

    def handle_endtag(self, tag):
        if tag == 'span' and self.in_number:
            self.in_number = False
            self.chapter = ''.join(self.number).strip() or None
        if tag == 'h1':
            self.in_title = False

    def handle_data(self, data):
        if self.in_number:
            self.number.append(data)


def heading_failures(text, shown):
    """Rules 5 and 6 for one page."""
    parser = Headings()
    parser.feed(text)
    parser.close()
    out = []
    if parser.h1_ids:
        out.append('%s: %d level-1 heading(s) inside the page (%s). Pandoc read text as a '
                   'chapter heading, most often the header row of a grid table it could not '
                   'parse. Run checks/check-grid-tables.py.'
                   % (shown, len(parser.h1_ids), ', '.join(parser.h1_ids[:3])))
    if parser.chapter:
        wrong = [n for n in parser.h2_numbers if n.split('.')[0] != parser.chapter]
        if wrong:
            out.append('%s: chapter %s has section number(s) %s. A stray chapter heading '
                       'renumbered them.' % (shown, parser.chapter, ', '.join(wrong[:3])))
    return out


def allowed_cell(cell, allowed):
    """The allowed message that this stderr text shows, or None."""
    for message in allowed:
        if re.fullmatch(r'Warning(?: in .+?)?: ' + re.escape(message), cell):
            return message
    return None


def note_cell(cell, lines):
    """True when this stderr text is one or more of the lines, in any order, and nothing else."""
    if not lines:
        return False
    one = '(?:%s)' % '|'.join(re.escape(squash(line)) for line in lines)
    return re.fullmatch('%s(?: %s)*' % (one, one), cell) is not None


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
        notes = NOTES.get(page.stem, ())
        bad = []
        for cell in parser.cells:
            if note_cell(cell, notes):
                continue
            message = allowed_cell(cell, left)
            if message is None:
                bad.append(cell)
            else:
                left.discard(message)
        if bad:
            # Name each cell, so the reader sees which output to remove.
            cells = ''.join('\n    %s' % (c[:120] + '...' if len(c) > 120 else c) for c in bad)
            failures.append('%s: %d cell-output-stderr element(s), output a chunk sent to stderr%s'
                            % (shown, len(bad), cells))
        for name, pattern in LEAKS:
            n = len(pattern.findall(text))
            if n:
                failures.append('%s: the render path %s appears %d time(s)' % (shown, name, n))
        failures += heading_failures(text, shown)
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
    for entry, prefixes in PREFIXES.items():
        for prefix in prefixes:
            if entry + (prefix,) not in seen:
                failures.append('%s: no EHB-%s line for %s [%s] that starts "%s". That chunk '
                                'always raises it, so the warning changed or the R profile did '
                                'not run.' % (log, entry[2], entry[0], entry[1], prefix))
    failures += read_pages(pages, root, messages)

    for f in failures:
        print(f)
    print('render leg: %d page(s), %d failure(s)' % (len(pages), len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
