#!/usr/bin/env python3
r"""Check 24. Every translated chapter keeps the R syntax and the register of its language.

The check reads every declared chapter of every language other than the main one, and five
rule groups apply to it. A finding prints as `file:line: rule_id: text`.

(a) argument-names. A call `name(a, b)` written outside code chunks, in prose or in inline
    code, MUST keep the argument names of the English chapter. The pairing is:
      - Calls are read from the lines outside the YAML front matter, fenced code and HTML
        comments, one line at a time. A call is a name (`[A-Za-z_.][A-Za-z0-9_.]*`, with an optional
        `pkg::` prefix) directly followed by `(` and closed by `)` on the same line. The
        arguments are split at the commas outside quotes and brackets.
      - The argument name of `x = value` is `x`. The argument name of a positional argument
        is its whole text.
      - An English call is comparable when every argument is a bare identifier
        (`[A-Za-z_.][A-Za-z0-9_.]*`), optionally `= value`, where the value is one token:
        an identifier, a number or a quoted string. So `mutate(new_column_name = value or
        transformation)` is a placeholder and is not compared. The prose plural `word(s)`
        is not a call. A translated call is compared
        when every argument is one word of letters, digits, `_` and `.`, optionally
        `= value` with a value of one token, in any script. So a placeholder with spaces (`criterio para filas`) or a quoted value
        (`c("siyah", "kırmızı")`) is not compared.
      - A translated call pairs with the comparable calls of the same name and the same
        argument count in the English chapter of the same stem, outside its code chunks.
        It fails when its argument names equal none of them. With no such English call, it
        is not compared.
(b) pipe-in-simple-table. A pipe-table row directly inside two simple-table rules fails. A
    rule is a line of two or more groups of dashes, `----  ----`. The two rules enclose
    the lines between them only when no blank line, heading or fence comes between.
(c) unbalanced-bold. A pipe-table line with an odd number of `**` outside inline code
    fails. A pipe table is a block of non-blank lines that holds a delimiter row
    (`---|---`) under a line with a `|`. Grid tables, as checks/gridtables.py finds them,
    are excluded, because pandoc lets bold text span the lines of a grid cell.
(d) banned patterns. Each regex under `banned:` in `translation/all.yml` and in
    `translation/<code>.yml` applies to one line at a time, case-insensitively unless the
    entry sets `case: sensitive`. The rules of `all.yml` apply to every translated language.
    For `tr`, case-insensitive means the Turkish mapping, because Python's re.I reads ı, i,
    I and İ as one letter. The text and the regex are both folded: I to ı, İ to i, then
    str.lower(). In the regex, a backslash and the character after it stay as written, so
    `\W` stays `\W`. The regex is then compiled without re.I. So `sinir` does not match
    `sınır` or `SINIR`, and `sınır` matches `SINIR`.
    A rule id MUST NOT be in `all.yml` and in a language file. The scope:
      - the prose and the code comments of each chapter. Excluded are the YAML front
        matter, the code of fenced blocks and the chunk options (`#|`), inline code spans
        (also across the lines of a paragraph or of a grid-table cell), URLs, link
        targets, HTML tags with their attributes, HTML comments and `{...}` attribute
        blocks. An HTML tag or comment MAY span several lines. A code comment starts at the
        first `#` outside every string literal (single, double or back quotes, with
        backslash escapes). Each excluded span reads as one NUL character, so a word on
        either side stays a separate word.
      - the language's block of `landing.yml`, keyed by the language code, values only.
      - the language's block of `var UI` in `ael-extras.html`, keyed by the `lang:` tag of
        languages.yml (jp reads `ja`, vn reads `vi`). Each string value, single- or
        double-quoted, is read alone.
(e) all-untranslated-line. A line of a translated chapter fails when all three hold. This
    is the definition of plan amendments S4 and R6, ported from the phase 7 detector.
      1. Scope. The line is outside code, so it is not in one of these:
           - the YAML front matter;
           - a fenced block (``` or ~~~, up to 3 spaces of indent, fence lines included);
           - an indented code block. It starts with 4 spaces or a tab of indent after a
             blank line, outside a list. It continues over the indented or blank lines after it;
           - an HTML comment, when the comment holds all of the line.
         Prose lines, headings and table rows are in scope. A blank line never fails.
      2. Identity. The whitespace-normalised text of the line equals that of a line of the
         English chapter of the same stem. Normalised means that each run of whitespace
         reads as one space and the ends are trimmed. The English lines include code lines.
      3. Threshold. It holds four or more words of letters. A word of letters is a maximal
         run of Unicode letters (`[^\W\d_]+`). The words are counted after these steps, in
         order:
           a. Masked across the whole chapter: HTML comments, inline code spans and display
              math `$$...$$`. A code span MAY cover the lines of one block of non-blank
              lines. Display math MAY cover several lines.
           b. Masked on the line:
                - a link with its text and target: `[text](target)`, `![alt](target)` and
                  `[text][ref]`;
                - an autolink `<http...>` and a bare URL;
                - an HTML tag `<...>` and an attribute block `{...}`;
                - inline math `$...$`. The opening `$` has a non-space on its right. The
                  closing `$` has a non-space on its left and no digit on its right.
           c. Quoted R output counts 0 words. That is a line that starts with `Error in`,
              `Error:` or `Warning` (case-sensitive). Leading spaces and the marks
              `` ` `` `*` `_` `"` `'` `“` `‘` `>` are removed before this test.
           d. Table cells. A line that holds a `|` is split at each `|`. A cell is dropped
              when its text is one of these, after `*`, `_` and quotes are removed and the
              ends trimmed:
                - a file extension `.ext`, or a comma-separated list of them. ext is letters
                  and digits and MAY have a second part, `.csv.gz`;
                - a name in UT_FORMATS (case-insensitive);
                - a name in UT_PACKAGES (case-sensitive).
              The other cells are counted.
    The finding text is the full line, trimmed.

A row of `checks/translation-exceptions.tsv` is the only excuse for a hit of rule (d) or (e).
The row MUST have the same lang, file, full line (trimmed) and rule id. A row that excuses no hit
is itself a finding, `stale-exception`. Rules (a), (b) and (c) have no exception rows.

Choices the brief left open:
  - The language files are read before `all.yml`, so an error in a language file is the
    one reported. `all.yml` is read from the same folder as the language files.
  - A rule id in `all.yml` and in a language file stops the run as an input error (exit 2),
    because it is a fault of the rules files, not of a chapter.
  - `landing.yml` is keyed by the language code (`jp:`), because that is how the file is
    written. Only `ael-extras.html` is keyed by the `lang:` tag.
  - Rows of the exceptions file excuse rules (d) and (e) only. Rules (a), (b) and (c) have
    no exception, because a correct translation never needs one. A line of rule (e) can be
    correct as it is: a reference-list citation, an author list or a proper name.
  - Rule (e) reads the languages of languages.yml and the stems of the main language's
    `_quarto.yaml` with langs.py, as rules (a) to (d) do. The phase 7 detector read the
    folders under content/ and read the stems with a line regex. On this repository both
    give the same languages and the same stems.
  - The Turkish mapping applies to `tr` only, because no other declared language has a
    dotless i. A regex of `case: sensitive` is not folded.
  - For an inline flag group in a `tr` regex, such as `(?i)`, re applies its own case rules.
    No shipped regex has one.
  - The fixtures read the rules from the repository's `translation/` folder, unless a
    fixture holds its own, so the self-test proves the rules that ship.

--self-test asserts two things. Every `bad` and `more_bad` example of a banned entry in
`translation/all.yml` and `translation/<code>.yml` hits its regex, and every `good` and
`more_good` example does not. An example of `all.yml` is tested in every translated
language, so also under the Turkish mapping. It prints one line for each rule.
Each directory under checks/fixtures/translation-rules/ is a small repository root with an
`expect.txt` of `pass`, `fail <rule_id>` or `error <path>`. A fail fixture MUST give at
least one finding, and every finding MUST carry that rule id. An error fixture MUST stop
with an input error whose message names the full path of <path> in the fixture.

Every file is read as UTF-8, and `landing.yml`, `translation/all.yml` and
`translation/<code>.yml` are parsed with yaml.safe_load. A file that cannot be read, decoded or parsed, and an
`ael-extras.html` with no block for the language, stop the run with one message that
names the full path.

Exit 0 when clean, 1 on a finding, 2 on a missing input or a bad argument.

Usage: python3 checks/check-translation-rules.py [--summary] [--lang <code>] [--self-test]
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from langs import Unreadable, parse, read_languages, read_stems  # noqa: E402
from gridtables import FENCE, corners, tables, width  # noqa: E402
import yaml  # noqa: E402  (langs has stopped with a message when PyYAML is absent)

ROOT = HERE.parent
PROG = 'check-translation-rules.py'
TSV_HEADER = ['lang', 'file', 'match_text', 'rule_id', 'reason']
FIXTURES = HERE / 'fixtures' / 'translation-rules'

# --- masking ---------------------------------------------------------------------------

CODE_SPAN = re.compile(r'(`+)(?!`)(.+?)(?<!`)\1(?!`)', re.S)
MASKS = [
    re.compile(r'<!--.*?-->'),
    re.compile(r'<[A-Za-z/!][^>]*>'),
    re.compile(r'\]\([^)]*\)'),
    re.compile(r'https?://\S+'),
    re.compile(r'\{[^{}]*\}'),
]
NUL = '\x00'


def mask_code(text):
    """text with each inline code span read as one NUL per line it covers."""
    return CODE_SPAN.sub(lambda m: re.sub(r'[^\n]+', NUL, m.group(0)), text)


def mask_rest(line):
    for rx in MASKS:
        line = rx.sub(NUL, line)
    return line


def comment_of(line):
    """The comment of one code line, from its first `#` outside quotes, or ''."""
    if re.match(r'\s*#\|', line):
        return ''
    quote, i = None, 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == '\\':
                i += 2          # an escape: the next character cannot close the string
                continue
            if ch == quote:
                quote = None
        elif ch in '"\'`':
            quote = ch
        elif ch == '#':
            return line[i:]
        i += 1
    return ''


def regions(lines):
    """(front, fenced) sets of line indexes: the YAML front matter and fenced code."""
    front = set()
    if lines and lines[0].strip() == '---':
        for k in range(1, len(lines)):
            if lines[k].strip() in ('---', '...'):
                front = set(range(k + 1))
                break
    fenced, fence = set(), None
    for k, line in enumerate(lines):
        if k in front:
            continue
        m = FENCE.match(line)
        if m and len(m.group(1)) <= 3:
            if fence is None:
                fence = m.group(2)
                fenced.add(k)
                continue
            if m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) \
                    and not m.group(3).strip():
                fence = None
                fenced.add(k)
                continue
        if fence is not None:
            fenced.add(k)
    return front, fenced


def bar_indexes(line, want):
    """The character indexes of the `|` at the display columns want, or None."""
    out, col = [], 0
    for i, ch in enumerate(line):
        if col in want and ch == '|':
            out.append(i)
        col += width(ch)
    return out if len(out) == len(want) else None


def chapter_scope(lines):
    """{line index: masked text} for the prose and the code comments of one chapter."""
    front, fenced = regions(lines)
    original = lines
    lines = no_html(lines, front | fenced)
    out = {}
    # Grid tables: mask inline code within each cell, across the lines of one row.
    done = set()
    for first, last, indent in tables(lines):
        want = corners(lines[first][indent:])
        group = []
        for k in range(first, last + 2):
            line = lines[k] if k <= last else '+'
            if line[indent:].startswith('+'):
                cells = {}
                bars = {}
                for g in group:
                    b = bar_indexes(lines[g][indent:], want)
                    if b is None:
                        continue
                    bars[g] = [indent + x for x in b]
                    for j in range(len(b) - 1):
                        cells.setdefault(j, []).append(g)
                masked = {g: list(lines[g]) for g in bars}
                # Right to left, so a masked cell does not move the cells after it.
                for j, rows in sorted(cells.items(), reverse=True):
                    text = '\n'.join(lines[g][bars[g][j] + 1:bars[g][j + 1]] for g in rows)
                    for g, part in zip(rows, mask_code(text).split('\n')):
                        masked[g][bars[g][j] + 1:bars[g][j + 1]] = [part]
                for g in bars:
                    out[g] = mask_rest(''.join(masked[g]))
                    done.add(g)
                group = []
                if k <= last:
                    done.add(k)
            else:
                group.append(k)
    # Paragraphs: mask inline code across the lines of one block of non-blank lines.
    block = []

    def flush():
        if block:
            parts = mask_code('\n'.join(lines[b] for b in block)).split('\n')
            for b, part in zip(block, parts):
                out[b] = mask_rest(part)
            block.clear()

    for k, line in enumerate(lines):
        if k in front or k in done:
            flush()
            continue
        if k in fenced:
            flush()
            if not FENCE.match(original[k]):
                c = comment_of(original[k])
                if c:
                    out[k] = mask_rest(mask_code(c))
            continue
        if not line.strip():
            flush()
            continue
        block.append(k)
    flush()
    return out


# --- inputs -----------------------------------------------------------------------------

def need(path, why):
    if not path.is_file():
        raise Unreadable('no %s. %s' % (path, why))


def read_lines(path):
    """The lines of one UTF-8 file. Raises Unreadable when it cannot be read or decoded."""
    try:
        return path.read_text(encoding='utf-8').split('\n')
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable('%s cannot be read as UTF-8 text: %s' % (path, e)) from None


def load_yaml(path):
    """One YAML file, read with yaml.safe_load. Raises Unreadable when it does not parse."""
    text = '\n'.join(read_lines(path))
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as e:
        mark = getattr(e, 'problem_mark', None)
        at = ', line %d' % (mark.line + 1) if mark else ''
        why = getattr(e, 'problem', None) or str(e)
        raise Unreadable('%s does not parse as YAML%s: %s'
                         % (path, at, ' '.join(str(why).split()))) from None


def read_tsv(path):
    """The exception rows: [(line number, lang, file, match_text, rule_id)]."""
    need(path, 'It holds every excused banned-pattern hit, with its reason.')
    rows = read_lines(path)
    if rows[0].split('\t') != TSV_HEADER:
        raise Unreadable('%s: the first line MUST be the header %s.'
                         % (path, ' '.join(TSV_HEADER)))
    out = []
    for n, row in enumerate(rows[1:], 2):
        if not row.strip():
            continue
        cells = row.split('\t')
        if len(cells) != len(TSV_HEADER) or not all(c.strip() for c in cells):
            raise Unreadable('%s:%d: a row MUST hold a non-empty %s, separated by tabs.'
                             % (path, n, ', '.join(TSV_HEADER)))
        out.append((n, cells[0], cells[1], cells[2].strip(), cells[3]))
    return out


ALL_WHY = 'It holds the banned patterns of every translated language.'


def fold_tr(text):
    """text in lower case by the Turkish mapping: I to ı, İ to i, then str.lower()."""
    return text.replace('I', 'ı').replace('İ', 'i').lower()


def fold_tr_regex(regex):
    """regex with fold_tr applied to every character except a backslash and the one after it."""
    out, i = [], 0
    while i < len(regex):
        if regex[i] == '\\':
            out.append(regex[i:i + 2])
            i += 2
        else:
            out.append(fold_tr(regex[i]))
            i += 1
    return ''.join(out)


class Banned:
    """One banned regex, compiled for one language. search() folds the text as compiled."""

    def __init__(self, regex, sensitive, lang):
        self.fold = lang == 'tr' and not sensitive
        if self.fold:
            self.rx = re.compile(fold_tr_regex(regex))
        else:
            self.rx = re.compile(regex, 0 if sensitive else re.I)

    def search(self, text):
        return self.rx.search(fold_tr(text) if self.fold else text)


def read_rules(path, why='It holds the banned patterns of that language.', lang=None):
    """[(rule id, Banned, examples)] of the banned entries in one rules file.

    The file is translation/<code>.yml or translation/all.yml. Both have the same schema. Each
    regex is compiled for lang, so `tr` gets the Turkish mapping.
    """
    need(path, why)
    doc = load_yaml(path)
    banned = doc.get('banned') if isinstance(doc, dict) else None
    if not isinstance(banned, list):
        raise Unreadable('%s has no banned: list.' % path)
    out = []
    for n, e in enumerate(banned, 1):
        if not isinstance(e, dict) or not e.get('id') or not e.get('regex'):
            raise Unreadable('%s: banned item %d has no id or no regex.' % (path, n))
        try:
            rx = Banned(e['regex'], e.get('case') == 'sensitive', lang)
        except re.error as err:
            raise Unreadable('%s: the regex of %s does not compile: %s'
                             % (path, e['id'], err)) from None
        examples = {}
        for key in ('bad', 'good', 'more_bad', 'more_good'):
            v = e.get(key, [])
            examples[key] = [v] if isinstance(v, str) else list(v or [])
        out.append((e['id'], rx, examples))
    return out


def landing_block(path, code):
    """[(line index, text)] of the values in the `<code>:` block of landing.yml.

    The file MUST parse with yaml.safe_load and hold a mapping under the code. The values are
    then read line by line, so that each finding carries its line number.
    """
    doc = load_yaml(path)
    if not isinstance(doc, dict) or not isinstance(doc.get(code), dict):
        raise Unreadable('%s has no %s: block.' % (path, code))
    lines = read_lines(path)
    start = next((k for k, l in enumerate(lines) if l.rstrip() == code + ':'), None)
    if start is None:
        raise Unreadable('%s has no %s: block.' % (path, code))
    out = []
    for k in range(start + 1, len(lines)):
        line = lines[k]
        if line and not line[0].isspace() and not line.startswith('#'):
            break
        m = re.match(r'\s*(?:-\s+)?[\w-]+:\s*(.*)$', line)
        value = m.group(1) if m else line.strip()
        if value.startswith('#'):
            continue
        value = re.sub(r'^"(.*)"\s*$', r'\1', value)
        if value:
            out.append((k, mask_rest(mask_code(value.replace('\\"', '"')))))
    return out


JS_STRING = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"")


def ui_block(path, tag):
    """[(line index, text)] of the quoted strings in the `tag: {` block of `var UI`.

    Every string value counts, single- or double-quoted, with backslash escapes.
    """
    lines = read_lines(path)
    start = next((k for k, l in enumerate(lines) if re.match(r'\s*var UI = \{', l)), None)
    if start is None:
        raise Unreadable('%s has no `var UI = { ... };` object.' % path)
    first = next((k for k in range(start, len(lines))
                  if re.match(r'\s*%s: \{' % re.escape(tag), lines[k])), None)
    if first is None:
        raise Unreadable('%s: the UI object has no %s block.' % (path, tag))
    out = []
    for k in range(first, len(lines)):
        body = re.sub(r'^\s*%s: \{' % re.escape(tag), '', lines[k]) if k == first else lines[k]
        for m in JS_STRING.finditer(body):
            s = m.group(1) if m.group(1) is not None else m.group(2)
            out.append((k, mask_rest(mask_code(re.sub(r'\\(.)', r'\1', s)))))
        if re.search(r"\}\s*,?\s*$", lines[k]):
            break
    return out


# --- rule (a) ---------------------------------------------------------------------------

CALL = re.compile(r'(?<![\w.$@:])((?:[A-Za-z_.][A-Za-z0-9_.]*::)?[A-Za-z_.][A-Za-z0-9_.]*)\(')
TOKEN = r'(?:[A-Za-z_.][A-Za-z0-9_.]*|-?\d[\d.]*|"[^"]*"|\'[^\']*\')'
EN_ARG = re.compile(r'^([A-Za-z_.][A-Za-z0-9_.]*)\s*(?:=(?!=)\s*' + TOKEN + r')?$', re.S)
TR_TOKEN = r'(?:(?:[^\W\d]|[._])[\w.]*|-?\d[\d.]*|"[^"]*"|\'[^\']*\'|“[^”]*”)'
TR_ARG = re.compile(r'^((?:[^\W\d]|[._])[\w.]*)\s*(?:=(?!=)\s*' + TR_TOKEN + r')?$', re.S)


def split_args(line, start):
    """The arguments of the call whose `(` is at start, and the end index, or None."""
    depth, quote, args, cur = 0, None, [], []
    for i in range(start + 1, len(line)):
        ch = line[i]
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in '"\'`':
            quote = ch
        elif ch in '([{':
            depth += 1
        elif ch in ')]}':
            if depth == 0:
                if ch != ')':
                    return None
                args.append(''.join(cur).strip())
                return args, i
            depth -= 1
        elif ch == ',' and depth == 0:
            args.append(''.join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    return None


def calls(lines, keep):
    """[(line index, name, call text, [argument])] of the calls on the lines in keep."""
    out = []
    for k in sorted(keep):
        line = lines[k]
        for m in CALL.finditer(line):
            got = split_args(line, m.end() - 1)
            if got is None or got[0] == ['']:
                continue
            args, end = got
            out.append((k, m.group(1), line[m.start():end + 1], args))
    return out


def arg_names(args, rx):
    names = []
    for a in args:
        m = rx.match(a)
        if not m:
            return None
        names.append(m.group(1))
    return tuple(names)


def outside_code(lines):
    front, fenced = regions(lines)
    return [k for k in range(len(lines)) if k not in front and k not in fenced]


def no_html_comments(lines):
    """lines with the text of every HTML comment, also across lines, read as NUL."""
    text = re.sub(r'<!--.*?-->', lambda m: re.sub(r'[^\n]+', NUL, m.group(0)),
                  '\n'.join(lines), flags=re.S)
    return text.split('\n')


# An HTML tag, which MAY span lines but not a blank line. Its name starts with a letter.
HTML_TAG = re.compile(r'<[A-Za-z/!](?:[^<>\n]|\n(?![ \t]*\n))*>')


def no_html(lines, skip):
    """lines with every HTML comment and tag, also across lines, read as NUL.

    The lines in skip (front matter and fenced code) read as blank lines here, so a `<` in
    code never opens a tag. The caller reads those lines from the original text.
    """
    text = '\n'.join('' if k in skip else l for k, l in enumerate(lines))
    text = re.sub(r'<!--.*?-->', lambda m: re.sub(r'[^\n]+', NUL, m.group(0)), text, flags=re.S)
    text = HTML_TAG.sub(lambda m: re.sub(r'[^\n]+', NUL, m.group(0)), text)
    return text.split('\n')


def rule_a(lines, en_lines):
    english = {}
    en_lines, lines = no_html_comments(en_lines), no_html_comments(lines)
    for _, name, _, args in calls(en_lines, outside_code(en_lines)):
        names = arg_names(args, EN_ARG)
        if names and names != ('s',):
            english.setdefault((name, len(names)), set()).add(names)
    out = []
    for k, name, text, args in calls(lines, outside_code(lines)):
        names = arg_names(args, TR_ARG)
        want = english.get((name, len(names))) if names else None
        if want and names not in want:
            alts = '; '.join('%s(%s)' % (name, ', '.join(w)) for w in sorted(want))
            out.append((k, 'argument-names', '%s (English: %s)' % (text, alts)))
    return out


# --- rules (b) and (c) ------------------------------------------------------------------

SIMPLE_RULE = re.compile(r'^\s*-{3,}(?:\s+-{3,})+\s*$')
DELIMITER = re.compile(r'^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*$')


def has_pipe(line):
    return '|' in mask_code(line).replace('\\|', '')


def rule_b(lines):
    front, fenced = regions(lines)
    out = []
    k = 0
    while k < len(lines):
        if k in front or k in fenced or not SIMPLE_RULE.match(lines[k]):
            k += 1
            continue
        j = k + 1
        while j < len(lines) and j not in fenced and lines[j].strip() \
                and not lines[j].lstrip().startswith('#') and not SIMPLE_RULE.match(lines[j]):
            j += 1
        if j < len(lines) and j not in fenced and SIMPLE_RULE.match(lines[j]):
            for i in range(k + 1, j):
                if has_pipe(lines[i]):
                    out.append((i, 'pipe-in-simple-table', lines[i].strip()))
            k = j + 1
        else:
            k += 1
    return out


def rule_c(lines):
    front, fenced = regions(lines)
    grid = set()
    for first, last, _ in tables(lines):
        grid.update(range(first, last + 1))
    out = []
    k = 0
    while k < len(lines):
        if k in front or k in fenced or k in grid or not lines[k].strip():
            k += 1
            continue
        j = k
        while j < len(lines) and lines[j].strip() and j not in fenced and j not in grid:
            j += 1
        block = range(k, j)
        heads = [i for i in block if i > k and DELIMITER.match(lines[i]) and '|' in lines[i]
                 and has_pipe(lines[i - 1])]
        if heads:
            i = heads[0] - 1
            while i < j and has_pipe(lines[i]):
                text = mask_code(lines[i]).replace('\\*', '')
                if len(re.findall(r'\*\*', text)) % 2:
                    out.append((i, 'unbalanced-bold', lines[i].strip()))
                i += 1
        k = j
    return out


# --- rule (d) ---------------------------------------------------------------------------

def rule_d(scope, rules):
    out = []
    for k, text in scope:
        text = text.rstrip()
        for rid, rx, _ in rules:
            if rx.search(text):
                out.append((k, rid))
    return out


# --- rule (e) ---------------------------------------------------------------------------
# The definition of /tmp/p7-466/untranslated.py (phase 7), with every R6 exclusion on.

UNTRANSLATED = 'all-untranslated-line'
UT_FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
UT_LIST_ITEM = re.compile(r'^\s*([-*+]|\d+[.)])\s+')
UT_COMMENT = re.compile(r'<!--.*?-->', re.S)
UT_DISPLAY_MATH = re.compile(r'\$\$.*?\$\$', re.S)
UT_LINKS = [
    re.compile(r'!?\[[^\]\n]*\]\([^)\n]*\)'),
    re.compile(r'\[[^\]\n]*\]\[[^\]\n]*\]'),
    re.compile(r'<https?://[^>\s]*>'),
    re.compile(r'https?://\S+'),
]
UT_OTHER = [
    re.compile(r'<[A-Za-z/!][^>]*>'),
    re.compile(r'\{[^{}]*\}'),
]
UT_INLINE_MATH = re.compile(r'\$(?=\S)[^$\n]*?(?<=\S)\$(?!\d)')
UT_R_OUTPUT = re.compile(r'^[\s`*_"\'“‘>]*(Error in\b|Error:|Warning)')
UT_EXTENSION = re.compile(
    r'^\.[A-Za-z0-9]+(\.[A-Za-z0-9]+)?(\s*,\s*\.[A-Za-z0-9]+(\.[A-Za-z0-9]+)?)*$')
UT_FORMATS = {f.lower() for f in (
    'SAS', 'XPORT', 'SPSS', 'SPSS Portable', 'Stata', 'Excel', 'Epiinfo', 'Minitab', 'Systat',
    'XBASE', 'EViews', 'JSON', 'Matlab', 'YAML', 'CSV', 'CSVY', 'TSV', 'PSV', 'RDS', 'RData',
    'DBF', 'ODS', 'Feather', 'Parquet', 'Weka', 'ARFF', 'HTML', 'XML', 'fst')}
# The R packages that the rio import table names.
UT_PACKAGES = {'base', 'utils', 'haven', 'foreign', 'readxl', 'openxlsx', 'data.table', 'csvy',
               'hexView', 'feather', 'fst', 'jsonlite', 'rmatio', 'readODS', 'xml2', 'yaml',
               'clipr', 'rio', 'arrow'}
UT_WORD = re.compile(r'[^\W\d_]+')


def ut_code_lines(lines):
    """Indexes of the front matter, fenced code, indented code and HTML comments."""
    skip = set()
    start = 0
    if lines and lines[0].strip() == '---':
        for k in range(1, len(lines)):
            if lines[k].strip() in ('---', '...'):
                skip.update(range(k + 1))
                start = k + 1
                break
    fence = None
    in_list = in_indented = False
    prev_blank = True
    for k in range(start, len(lines)):
        line = lines[k]
        m = UT_FENCE.match(line)
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
        if UT_LIST_ITEM.match(line):
            in_list = True
        elif not indented:
            in_list = False
        prev_blank = False
    # A line wholly inside an HTML comment is not prose.
    text = '\n'.join('' if k in skip else l for k, l in enumerate(lines))
    text = UT_COMMENT.sub(lambda m: re.sub(r'[^\n]', NUL, m.group(0)), text)
    for k, line in enumerate(text.split('\n')):
        if line and not line.replace(NUL, '').strip():
            skip.add(k)
    return skip


def ut_blank(m):
    return re.sub(r'[^\n]', ' ', m.group(0))


def ut_masked_lines(lines, skip):
    """Each line with the chapter-wide masks of step 3a applied."""
    text = '\n'.join('' if k in skip else l for k, l in enumerate(lines))
    text = UT_COMMENT.sub(ut_blank, text)
    blocks = re.split(r'(\n[ \t]*\n)', text)
    text = ''.join(CODE_SPAN.sub(ut_blank, b) for b in blocks)
    return UT_DISPLAY_MATH.sub(ut_blank, text).split('\n')


def ut_mask_line(line):
    """Step 3b."""
    for rx in UT_LINKS + UT_OTHER:
        line = rx.sub(' ', line)
    return UT_INLINE_MATH.sub(' ', line)


def ut_dropped(cell):
    t = re.sub(r'[*_"\'“”‘’]', '', cell).strip()
    return bool(t) and (UT_EXTENSION.match(t) is not None or t.lower() in UT_FORMATS
                        or t in UT_PACKAGES)


def ut_words(raw, masked):
    """The words of letters of one line, by steps 3b to 3d."""
    if UT_R_OUTPUT.match(raw):
        return 0
    line = ut_mask_line(masked)
    if '|' in line:
        line = ' '.join(c for c in line.split('|') if not ut_dropped(c))
    return len(UT_WORD.findall(line))


def ut_norm(line):
    return ' '.join(line.split())


def english_lines(en_lines):
    """The whitespace-normalised non-blank lines of one English chapter, code included."""
    return {ut_norm(l) for l in en_lines if l.strip()}


def rule_e(lines, english):
    """[(line index, rule id, trimmed line)] of the lines that pass steps 1 to 3."""
    skip = ut_code_lines(lines)
    masked = ut_masked_lines(lines, skip)
    out = []
    for k, line in enumerate(lines):
        if k in skip or not line.strip() or ut_norm(line) not in english:
            continue
        if ut_words(line, masked[k]) >= 4:
            out.append((k, UNTRANSLATED, line.strip()))
    return out


# --- the run ----------------------------------------------------------------------------

def add_common(rules, rules_dir):
    """rules with the banned entries of rules_dir/all.yml added to every language.

    The language files are read first, so an error in one of them is the one reported.
    Raises Unreadable when a rule id is in all.yml and in a language file.
    """
    path = rules_dir / 'all.yml'
    common = {l: read_rules(path, ALL_WHY, l) for l in rules}
    for l, own in rules.items():
        both = sorted({rid for rid, _, _ in common[l]} & {rid for rid, _, _ in own})
        if both:
            raise Unreadable('%s and %s both define the rule id %s. A rule id MUST be in one '
                             'file only.' % (path, rules_dir / ('%s.yml' % l), ', '.join(both)))
    return {l: common[l] + own for l, own in rules.items()}


def run(root, only=None, rules_dir=None):
    """(findings, per-language counts). A finding is (lang, file, line, rule_id, text)."""
    rules_dir = rules_dir or root / 'translation'
    fixed = [
        (root / 'languages.yml', 'That file declares which languages ship.'),
        (root / 'landing.yml', 'It holds the landing-page strings, one block per language.'),
        (root / 'ael-extras.html', 'It holds the interface strings, one block per language.'),
        (root / 'checks' / 'translation-exceptions.tsv',
         'It holds every excused banned-pattern hit, with its reason.'),
    ]
    missing = [(p, why) for p, why in fixed if not p.is_file()]
    if missing:
        raise Unreadable(' '.join('no %s. %s' % m for m in missing))
    main, codes = read_languages(root / 'languages.yml')
    doc = parse(root / 'languages.yml')
    tag = {e.get('code'): e.get('lang') or e.get('code')
           for e in doc.get('languages', []) if isinstance(e, dict)}
    stems = read_stems(root / 'content' / main / '_quarto.yaml')
    targets = [c for c in codes if c != main]
    if only is not None:
        if only not in targets:
            raise Unreadable('%s declares no translated language %s.'
                             % (root / 'languages.yml', only))
        targets = [only]
    if not targets:
        raise Unreadable('%s declares no language other than %s, so nothing would be '
                         'measured.' % (root / 'languages.yml', main))
    exceptions = read_tsv(root / 'checks' / 'translation-exceptions.tsv')
    files = [root / 'content' / l / ('%s.qmd' % s) for l in [main] + targets for s in stems]
    absent = [f for f in files if not f.is_file()]
    if absent:
        raise Unreadable(' '.join('no %s.' % f for f in absent)
                         + ' Every declared chapter is read.')
    rules = {l: read_rules(rules_dir / ('%s.yml' % l), lang=l) for l in targets}
    rules = add_common(rules, rules_dir)

    lines_of = read_lines

    english = {s: lines_of(root / 'content' / main / ('%s.qmd' % s)) for s in stems}
    english_set = {s: english_lines(english[s]) for s in stems}
    landing, ael = lines_of(root / 'landing.yml'), lines_of(root / 'ael-extras.html')
    raw, counts = [], {}
    for l in targets:
        hits = []
        for s in stems:
            rel = 'content/%s/%s.qmd' % (l, s)
            lines = lines_of(root / rel)
            for k, rid, text in (rule_a(lines, english[s]) + rule_b(lines) + rule_c(lines)
                                 + rule_e(lines, english_set[s])):
                hits.append((l, rel, k + 1, rid, text))
            scope = sorted(chapter_scope(lines).items())
            for k, rid in rule_d(scope, rules[l]):
                hits.append((l, rel, k + 1, rid, lines[k].strip()))
        for rel, scope, src in (
                ('landing.yml', landing_block(root / 'landing.yml', l), landing),
                ('ael-extras.html', ui_block(root / 'ael-extras.html', tag[l]), ael)):
            for k, rid in sorted(set(rule_d(scope, rules[l]))):
                hits.append((l, rel, k + 1, rid, src[k].strip()))
        raw.extend(hits)
    # The rule ids that an exception row can excuse: rules (d) and (e).
    excusable = {rid for l in targets for rid, _, _ in rules[l]} | {UNTRANSLATED}
    used, findings = set(), []
    for h in raw:
        l, rel, _, rid, text = h
        row = next((e for e in exceptions if rid in excusable
                    and (e[1], e[2], e[3], e[4]) == (l, rel, text, rid)), None)
        if row:
            used.add(row[0])
        else:
            findings.append(h)
    for n, l, rel, text, rid in exceptions:
        if (only is None or l == only) and n not in used:
            findings.append((l, 'checks/translation-exceptions.tsv', n, 'stale-exception',
                             '%s %s %s %s' % (l, rel, rid, text)))
    for l in targets:
        mine = [f for f in findings if f[0] == l]
        counts[l] = (len(stems), len(mine),
                     len({f[1] for f in mine if f[1].startswith('content/')}),
                     sum(1 for e in exceptions if e[1] == l and e[0] in used))
    return findings, counts


# --- self-test --------------------------------------------------------------------------

def self_test():
    bad = []
    main, codes = read_languages(ROOT / 'languages.yml')
    examples = 0
    targets = [l for l in codes if l != main]
    files = [(ROOT / 'translation' / 'all.yml', targets)] + [
        (ROOT / 'translation' / ('%s.yml' % l), [l]) for l in targets]
    for path, langs in files:
        name = 'translation/%s' % path.name
        # One compiled rule list per language: all.yml applies to every translated language.
        compiled = [read_rules(path, ALL_WHY, l) if path.name == 'all.yml'
                    else read_rules(path, lang=l) for l in langs]
        for j, (rid, _, ex) in enumerate(compiled[0]):
            n, wrong = 0, len(bad)
            for key in ('bad', 'more_bad', 'good', 'more_good'):
                for text in ex[key]:
                    n += 1
                    masked = mask_rest(mask_code(text)).rstrip()
                    off = [l for l, c in zip(langs, compiled)
                           if bool(c[j][1].search(masked)) != key.endswith('bad')]
                    if off:
                        bad.append('%s %s: the %s example %r %s in %s'
                                   % (name, rid, key, text,
                                      'gives no hit' if key.endswith('bad') else 'gives a hit',
                                      ', '.join(off)))
            examples += n
            print('rule %s %s: examples %d, wrong %d' % (name, rid, n, len(bad) - wrong))
    print('rule examples %d, wrong %d' % (examples, len(bad)))
    dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    if not dirs:
        sys.exit('%s: no fixture directory under %s, so nothing would be tested.'
                 % (PROG, FIXTURES))
    for d in dirs:
        expect_path = d / 'expect.txt'
        if not expect_path.is_file():
            bad.append('%s: no expect.txt' % d.name)
            continue
        expect = expect_path.read_text(encoding='utf-8').split()
        own = d / 'translation'
        try:
            findings, _ = run(d, rules_dir=own if own.is_dir() else ROOT / 'translation')
        except Unreadable as e:
            # An input error. main() prints e.why as its one message and exits 2.
            ok = len(expect) == 2 and expect[0] == 'error' and str(d / expect[1]) in e.why
            print('%s %s: expect %s, got the input error: %s'
                  % ('ok' if ok else 'FAIL', d.name, ' '.join(expect), e.why))
            if not ok:
                bad.append('%s: %s' % (d.name, e.why))
            continue
        if expect[:1] == ['error']:
            print('FAIL %s: expect %s, the run read every input' % (d.name, ' '.join(expect)))
            bad.append('%s: no input error' % d.name)
            continue
        got = sorted({f[3] for f in findings})
        if expect == ['pass']:
            ok = not findings
        elif len(expect) == 2 and expect[0] == 'fail':
            ok = bool(findings) and got == [expect[1]]
        else:
            bad.append('%s: expect.txt is neither `pass` nor `fail <rule_id>`' % d.name)
            continue
        print('%s %s: expect %s, got %s' % ('ok' if ok else 'FAIL', d.name, ' '.join(expect),
                                            ' '.join(got) or 'no finding'))
        if not ok:
            bad.append('%s: expect %s, got %s' % (d.name, ' '.join(expect), ' '.join(got)))
    for b in bad:
        print('   %s' % b)
    print('fixtures %d, failed %d' % (len(dirs), len(bad)))
    return 1 if bad else 0


def main():
    args = sys.argv[1:]
    usage = 'usage: checks/%s [--summary] [--lang <code>] [--self-test]' % PROG
    only, summary, test, i = None, False, False, 0
    while i < len(args):
        if args[i] == '--summary':
            summary = True
        elif args[i] == '--self-test':
            test = True
        elif args[i] == '--lang' and i + 1 < len(args):
            only = args[i + 1]
            i += 1
        else:
            print('%s: unknown argument %s. %s' % (PROG, args[i], usage), file=sys.stderr)
            return 2
        i += 1
    try:
        if test:
            return self_test()
        findings, counts = run(ROOT, only)
    except Unreadable as e:
        print('%s: %s' % (PROG, e.why), file=sys.stderr)
        return 2
    if summary:
        for l, (n, f, c, x) in counts.items():
            print('lang %s: chapters %d, findings %d in %d chapter(s), excused %d'
                  % (l, n, f, c, x))
        print('translation rules: languages %d, findings %d' % (len(counts), len(findings)))
    else:
        for _, rel, n, rid, text in findings:
            print('%s:%d: %s: %s' % (rel, n, rid, text))
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
