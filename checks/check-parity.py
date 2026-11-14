#!/usr/bin/env python3
"""Fail on a per-section difference between each translated chapter and its English chapter.

Check 27. A translated section MUST carry the code spans, link targets, images and bold of its
English section. A difference fails unless a row of `checks/parity-exceptions.tsv` excuses it.
The definition comes from issue 466, second follow-up, contract P1 to P6, Q1, B3 and B8.

LIMIT (P6). The check compares the multiset of items in each section. Equal multisets do not
prove that an item stands in the right sentence. A code span that moves to another sentence of
the same section is not a finding.

SCOPE (P2). Every declared stem except `index`, in every declared language except the main
one. On the handbook that is 50 stems and 7 languages, 350 pairs. `index.qmd` is the landing
page, written for each language, so it is not compared.

PARSER (P1). Each chapter goes through `quarto pandoc -f markdown -t json`. Plain `pandoc` runs
when quarto is not on PATH, and `--pandoc <cmd>` names another command. The source first passes
through plain_fences(), the step of checks/check-links.py, line for line. Pandoc reads ```{r} as
a paragraph, so without that step every `#` comment in an R chunk would be a heading. The walk
then counts four kinds of item:

  code   the text of every Code inline, exactly. Inline R `r ...` is a Code inline too, and its
         text is compared verbatim, the leading `r ` included.
  link   the target of every Link, as pandoc resolves it. A reference link counts by its
         target and never by its label. The href of every <a> in raw HTML counts too.
  image  the target of every Image, and the src of every <img> in raw HTML.
  bold   every Strong, by its B8 form (below). A `name` bold is the item `name:<text>`, compared
         exactly. Every other bold is the one item `bold`, so a section compares their NUMBER.
         A lost or added bold is a finding. A translated lead-in or sentence is not. Italics are
         not compared.

Fenced and indented code blocks (CodeBlock) are never walked. Check 3 holds them identical to
the English. Raw HTML is RawBlock or RawInline of format html, read with html.parser, so the
content of an HTML comment never counts. A footnote counts in the section of its reference.
Headings, list items, table cells, block quotes and divs count where they stand. A Cite counts
by its rendered inlines alone, so its prefix and suffix do not count twice.

BOLD FORMS (B8). checks/check-markdown-form.py, rule `bold-form`, uses the same classifier, so
both checks read bold the same way. The bold text is the flattened text of the Strong, outer
whitespace removed. The block is the Para, the Plain (a tight list item, a table cell), the
LineBlock line or the Header that holds the Strong. A bold STARTS A SENTENCE when the text
before it on its line is empty or ends a sentence. A sentence ends with `.`, `?` or `!` and
whitespace, or with `。`, `？` or `！`. The forms are tested in this order:

  name      the bold text is one entry of checks/bold-names.txt, exactly and case-sensitive.
            **dplyr**, **data.table**, **RStudio**.
  mark-outside  it starts a sentence, and the first character after it, spaces skipped, is
            a colon (`:`, `：`) or a closing mark (`.`, `?`, `!`, `。`, `？`, `！`). F1 B9
            puts that colon or mark inside the bold, so **NOTE**: and **A sentence**. are
            this form, not a lead-in or a sentence.
  lead-in   it starts a sentence, and its text ends in `:` or `：`. **NOTE:**, **注意：**,
            **Remarque :**.
  sentence  it starts a sentence, and its text ends in `.`, `?`, `!`, `。`, `？` or `！`. Or
            nothing but whitespace follows it on its line.
  phrase    anything else, for example **not** in mid-sentence.

Check 28 reports a `mark-outside` or `phrase` bold. Check 27 counts it as a plain bold.

A line is the block, or the part of it between two LineBreaks, because a LineBreak starts a
new rendered line. A Strong inside a Strong belongs to the outer one. Bold in code and in raw
HTML (<b>, <strong>) is not counted.

SECTIONS (P3). Section 0 is the content before the first heading. Section n is the content
after the n-th heading, up to the next heading of any level. A heading inside a div, a block
quote or a list still starts a section. The heading's own inlines belong to the section it
opens. When the English and the translation have different heading counts, the chapter is not
compared, and the run exits 2 and names it. Check 1 holds the heading sequences equal.

FINDINGS. One line per section, kind and item whose count differs:

  <lang> <file> section <n> "<English heading>" <kind> "<item>": English <a>, translation <b>

The item and the heading are JSON strings, so a space or a quote in them stays visible. Where
the section has the same number of top-level blocks in both languages, the line ends with
`[blocks: English 2,5; translation 2]`. That names the block that holds each occurrence. The
heading is block 0. The ordinal is a hint, not a claim of location (P3).

EXCEPTIONS (P4, Q1, B3). `<tree>/checks/parity-exceptions.tsv` MUST exist. Its first line that
is not blank and does not start with `#` MUST be the header: lang, file, section, kind,
english, translation, reason. A row removes one occurrence of `english` from the English side
and one of `translation` from the translated side of that section. An empty side names
nothing. A row MUST match every side it names. Otherwise it is a `stale-exception` finding and
removes nothing. Rows apply in file order. A row is an `invalid-exception` finding, and
removes nothing, in each of these cases:
  - it has not 7 fields;
  - its section is not an integer;
  - its kind is not code, link, image or bold;
  - both sides are empty, or both sides are equal;
  - its reason does not start with an allowed cause, `(a) ` or `(b) `;
  - its cause does not fit its kind: cause (a) needs kind code, and cause (b) kind link (F1 P4a);
  - it names no translated pair in scope.
Cause (a) is a string literal in quotes inside a code span that the code does not use. Cause
(b) is a link to a resource in the reader's language that replaces an English-only resource.
Q1 withdrew cause (c). No cause fits kind image or bold, so a row of either kind is
invalid. `file` is the chapter file name, `cleaning.qmd`.

INPUTS. The declared languages come from `languages.yml` (`main:` and every `- code:` line).
The stems come from the `.qmd` entries of `book.chapters` in `content/<main>/_quarto.yaml`. A
line reader does this, because PyYAML is not standard library. The name list is
checks/bold-names.txt beside this script: one name per line, blank and `#` lines skipped.

OUTPUT. The finding lines, then one line per translated language, then one totals line.
`--summary` prints the language lines and the totals line only.

`--self-test` runs the check on every fixture under `checks/fixtures/parity/`. A fixture is a
small tree with its own `languages.yml`, `content/`, `checks/parity-exceptions.tsv` and
`expect.txt`. The first line of `expect.txt` is `pass` or `fail`. A fail fixture lists each
expected finding line, with the fixture folder written as `<fixture>`. A fail fixture MUST exit
1 with exactly those findings, and a pass fixture MUST exit 0 with none. The fixtures in
REQUIRED MUST exist. The self-test reads every input of every fixture before it runs any.

Exit 0 on no finding and 1 on a finding. Exit 2 also when pandoc fails on a chapter, or when
a pair has different heading counts. Exit 2 on a missing or unusable input, with one message
that names its full path:
  - the tree is not a folder;
  - no `languages.yml`, or one with no `main:`, no translated language or a repeated code;
  - no `content/`, no project file, or a project file with no chapter other than index.qmd;
  - a missing chapter file;
  - no exceptions file, or one with no header;
  - no name list, or one with no name;
  - a file that is not UTF-8.

Usage: python3 checks/check-parity.py [--summary] [--pandoc <cmd>] [<tree>]   (default: the repository root)
       python3 checks/check-parity.py --self-test
"""
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / 'fixtures' / 'parity'
PROG = 'check-parity.py'
KINDS = ('code', 'link', 'image', 'bold')
HEADER = ['lang', 'file', 'section', 'kind', 'english', 'translation', 'reason']
# The one kind that each allowed cause fits (F1 P4a).
CAUSE_KIND = {'a': 'code', 'b': 'link'}
NAMES_FILE = HERE / 'bold-names.txt'
# The fixtures that every kind and every exception outcome need, both ways.
REQUIRED = ('pass-same', 'pass-translated-bold', 'pass-code-block', 'pass-exception',
            'pass-exception-code', 'fail-code-missing', 'fail-code-extra', 'fail-link-missing',
            'fail-raw-html-link', 'fail-image-missing', 'fail-bold-name', 'fail-bold-count',
            'fail-stale-exception', 'fail-invalid-exception', 'fail-invalid-exception-kind')


def stop(message):
    print('%s: %s' % (PROG, message), file=sys.stderr)
    sys.exit(2)


def read_text(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        stop('no %s.' % os.path.abspath(path))
    except (OSError, UnicodeDecodeError) as e:
        stop('%s cannot be read as UTF-8: %s' % (os.path.abspath(path), e))


def read_declared(root):
    """(main, codes, stems) from <root>/languages.yml and <root>/content/<main>/_quarto.yaml."""
    ly = os.path.join(root, 'languages.yml')
    text = read_text(ly)
    m = re.search(r'''^main:\s*["']?([a-z]{2,3})["']?\s*(?:#.*)?$''', text, re.M)
    if not m:
        stop('%s declares no main: language.' % os.path.abspath(ly))
    main = m.group(1)
    codes = re.findall(r'''^\s*-\s*code:\s*["']?([a-z]{2,3})["']?\s*(?:#.*)?$''', text, re.M)
    if not codes or main not in codes or len(set(codes)) != len(codes):
        stop('%s: codes %s, main %s. The codes MUST be distinct and include main.'
             % (os.path.abspath(ly), codes, main))
    content = os.path.join(root, 'content')
    if not os.path.isdir(content):
        stop('no %s. That folder holds the chapters of every language.' % os.path.abspath(content))
    qy = os.path.join(content, main, '_quarto.yaml')
    lines = read_text(qy).split('\n')
    stems, i = [], 0
    while i < len(lines) and not re.match(r'^book:\s*$', lines[i]):
        i += 1
    i += 1
    key = None
    while i < len(lines):
        l = lines[i]
        if l.strip() and not l.startswith(' '):
            break
        km = re.match(r'^( +)chapters:\s*$', l)
        if key is None and km:
            key = len(km.group(1))
        elif key is not None:
            ind = len(l) - len(l.lstrip(' '))
            body = l.strip()
            if body and not body.startswith('#'):
                if ind < key or (ind == key and not body.startswith('-')):
                    break
                stems += [s for s in re.findall(r'''(?:^|[\s:"'])([\w./-]+)\.qmd''', body)]
        i += 1
    if not stems:
        stop('%s declares no chapter in book.chapters.' % os.path.abspath(qy))
    return main, codes, stems


FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')


def plain_fences(text):
    """checks/check-links.py plain_fences(): ```{r, eval=F} becomes ```{.r}, line for line."""
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


class RawLinks(HTMLParser):
    """The href of every <a> and the src of every <img> in one piece of raw HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href') is not None:
            self.found.append(('link', a['href']))
        elif tag == 'img' and a.get('src') is not None:
            self.found.append(('image', a['src']))

    handle_startendtag = handle_starttag


def raw_items(text):
    p = RawLinks()
    p.feed(text)
    p.close()
    return p.found


def items(node, out):
    """Append (kind, item) for every code, link and image item under one pandoc JSON node."""
    if isinstance(node, list):
        for x in node:
            items(x, out)
        return
    if not isinstance(node, dict) or 't' not in node:
        return
    t, c = node['t'], node.get('c')
    if t == 'Code':
        out.append(('code', c[1]))
    elif t in ('Link', 'Image'):
        out.append(('link' if t == 'Link' else 'image', c[2][0]))
        items(c[1], out)
    elif t in ('RawInline', 'RawBlock'):
        if c[0] in ('html', 'html4', 'html5'):
            out.extend(raw_items(c[1]))
    elif t == 'CodeBlock':
        return
    elif t == 'Cite':
        items(c[1], out)
    elif c is not None:
        items(c, out)


def has_header(node):
    if isinstance(node, list):
        return any(has_header(x) for x in node)
    if isinstance(node, dict):
        if node.get('t') == 'Header':
            return True
        return has_header(node.get('c'))
    return False


def count_headers(node):
    if isinstance(node, list):
        return sum(count_headers(x) for x in node)
    if isinstance(node, dict):
        return (node.get('t') == 'Header') + count_headers(node.get('c'))
    return 0


class Limitation(Exception):
    pass


def children(block):
    """The block lists inside a container that holds a heading."""
    t, c = block['t'], block.get('c')
    if t == 'Div':
        return [c[1]]
    if t == 'BlockQuote':
        return [c]
    if t == 'BulletList':
        return c
    if t == 'OrderedList':
        return c[1]
    raise Limitation('a %s holds a heading' % t)


def units(blocks):
    for b in blocks:
        if b.get('t') == 'Header':
            yield 'H', b
        elif has_header(b):
            for bl in children(b):
                yield from units(bl)
        else:
            yield 'B', b


def stringify(node):
    if isinstance(node, list):
        return ''.join(stringify(x) for x in node)
    if not isinstance(node, dict):
        return ''
    t, c = node.get('t'), node.get('c')
    if t == 'Str':
        return c
    if t in ('Space', 'SoftBreak', 'LineBreak'):
        return ' '
    if t in ('Code', 'Math'):
        return c[1]
    if t in ('Link', 'Image', 'Span'):
        return stringify(c[1])
    if t == 'Quoted':
        return '"%s"' % stringify(c[1])
    if t in ('RawInline', 'Note'):
        return ''
    if t == 'Cite':
        return stringify(c[1])
    return stringify(c)


BOLD_FORMS = ('name', 'lead-in', 'sentence', 'mark-outside', 'phrase')
NAMES = frozenset()
SENT_PUNCT = '.?!。？！'
LEAD_END = ':：'
# Text before a bold span that ends a sentence: ASCII . ? ! then whitespace, or a CJK
# sentence mark with or without whitespace.
PRE_END = re.compile(r'(?:[.?!]\s+|[。？！]\s*)$')
INLINE_TYPES = {'Str', 'Space', 'SoftBreak', 'LineBreak', 'Code', 'Math', 'Strong', 'Emph',
                'Underline', 'Strikeout', 'Superscript', 'Subscript', 'SmallCaps', 'Quoted',
                'Cite', 'Link', 'Image', 'Span', 'RawInline', 'Note'}


def load_names(path=None):
    """Set NAMES from the name list (B8): every line that is not blank and does not start with
    `#`, outer whitespace removed. Exits 2 when the file is missing or holds no name."""
    global NAMES
    path = str(path or NAMES_FILE)
    names = {l.strip() for l in read_text(path).split('\n')
             if l.strip() and not l.strip().startswith('#')}
    if not names:
        stop('%s holds no name. It is the B8 name list, and the bold forms need it.'
             % os.path.abspath(path))
    NAMES = frozenset(names)


def classify(text, start, end):
    """The B8 form of the bold span text[start:end] of one block: name, lead-in, sentence,
    mark-outside or phrase. text is the block text as flatten() builds it."""
    b = text[start:end].strip()
    if b in NAMES:
        return 'name'
    # A LineBreak ends a rendered line, so the line a bold belongs to is what it sees.
    before, after = text[:start].rsplit('\n', 1)[-1], text[end:].split('\n', 1)[0]
    starts = not before.strip() or PRE_END.search(before) is not None
    # B9: a lead-in holds its colon and a sentence its closing mark inside the bold. A tuple,
    # so an empty string (nothing after the bold) is not a member.
    if b and starts and after.lstrip()[:1] in tuple(LEAD_END + SENT_PUNCT):
        return 'mark-outside'
    if b and starts and b[-1] in LEAD_END:
        return 'lead-in'
    if b and starts and (b[-1] in SENT_PUNCT or not after.strip()):
        return 'sentence'
    return 'phrase'


def flatten(inlines):
    """(text, [(start, end)] of every outermost Strong, [footnote block lists]) for one block.

    Str as it is, a space for Space and SoftBreak, a newline for LineBreak, the text of Code
    and Math, the inlines of a Link, Image, Span and Cite, a Quoted inside its quote marks, and
    nothing for RawInline and Note.
    """
    buf, spans, notes = [], [], []
    size = [0]

    def put(s):
        buf.append(s)
        size[0] += len(s)

    def walk(xs, inside):
        for x in xs:
            if not isinstance(x, dict):
                continue
            t, c = x.get('t'), x.get('c')
            if t == 'Str':
                put(c)
            elif t in ('Space', 'SoftBreak'):
                put(' ')
            elif t == 'LineBreak':
                put('\n')
            elif t in ('Code', 'Math'):
                put(c[1])
            elif t == 'Strong':
                s = size[0]
                walk(c, True)
                if not inside:
                    spans.append((s, size[0]))
            elif t in ('Link', 'Image', 'Span', 'Cite'):
                walk(c[1], inside)
            elif t == 'Quoted':
                mark = '"' if c[0].get('t') == 'DoubleQuote' else "'"
                put(mark)
                walk(c[1], inside)
                put(mark)
            elif t == 'Note':
                notes.append(c)
            elif t == 'RawInline':
                pass
            elif isinstance(c, list):
                walk(c, inside)

    walk(inlines, False)
    return ''.join(buf), spans, notes


def bold_forms(node, out=None):
    """[(form, text)] for every pandoc Strong under one node, in document order (B8).

    A block is a Para, a Plain, one line of a LineBlock, or a Header. A bare inline list that
    no such block holds (a definition-list term, a table caption) is a block too. A footnote
    is a set of blocks of its own, listed after the block that references it. CodeBlock and
    RawBlock are never walked.
    """
    if out is None:
        out = []
    if isinstance(node, list):
        if node and all(isinstance(x, dict) and x.get('t') in INLINE_TYPES for x in node):
            _bold_block(node, out)
        else:
            for x in node:
                bold_forms(x, out)
        return out
    if not isinstance(node, dict) or 't' not in node:
        return out
    t, c = node['t'], node.get('c')
    if t in ('CodeBlock', 'RawBlock'):
        return out
    if t in ('Para', 'Plain'):
        _bold_block(c, out)
    elif t == 'Header':
        _bold_block(c[2], out)
    elif t == 'LineBlock':
        for line in c:
            _bold_block(line, out)
    elif c is not None:
        bold_forms(c, out)
    return out


def _bold_block(inlines, out):
    text, spans, notes = flatten(inlines)
    for s, e in spans:
        out.append((classify(text, s, e), text[s:e].strip()))
    for n in notes:
        bold_forms(n, out)


def bold_item(form, text):
    """The parity item of one bold span (B8): `name:<text>` for a `name` bold, so names are
    compared exactly; `bold` for every other form, so those are compared by number."""
    return 'name:' + text if form == 'name' else 'bold'


def sections(doc):
    """[(heading text, [ [(kind, item)] per block, block 0 the heading ])] for one document.

    Section 0 has an empty heading block. Raises Limitation when a container that children()
    does not open holds a heading.
    """
    out = [['', [[]]]]
    for kind, b in units(doc['blocks']):
        if kind == 'H':
            head = []
            items(b['c'][2], head)
            head += [('bold', bold_item(f, x)) for f, x in bold_forms(b)]
            out.append([' '.join(stringify(b['c'][2]).split()), [head]])
        else:
            found = []
            items(b, found)
            found += [('bold', bold_item(f, x)) for f, x in bold_forms(b)]
            out[-1][1].append(found)
    if len(out) - 1 != count_headers(doc['blocks']):
        raise Limitation('the walk found %d headings, the tree holds %d'
                         % (len(out) - 1, count_headers(doc['blocks'])))
    return out


def pandoc_json(path, pandoc):
    """(the pandoc JSON document of one chapter, the source after plain_fences(), None), or
    (None, None, why)."""
    try:
        with open(path, encoding='utf-8') as f:
            src = plain_fences(f.read())
    except (OSError, UnicodeDecodeError) as e:
        return None, None, 'cannot be read: %s' % e
    try:
        r = subprocess.run(pandoc + ['-f', 'markdown', '-t', 'json'],
                           input=src, capture_output=True, text=True)
    except OSError as e:
        return None, None, 'pandoc %s cannot run: %s' % (' '.join(pandoc), e)
    if r.returncode != 0:
        return None, None, 'pandoc failed: %s' % (r.stderr.strip().split('\n') or [''])[0]
    return json.loads(r.stdout), src, None


def parse(path, pandoc):
    """(sections, None) for one chapter, or (None, why)."""
    doc, _, why = pandoc_json(path, pandoc)
    if why:
        return None, why
    try:
        return sections(doc), None
    except Limitation as e:
        return None, 'the check cannot split it into sections: %s' % e


def read_exceptions(path):
    """[(path, line number, fields)] for the exceptions file. Exits 2 on a missing header."""
    rows, header = [], False
    for n, line in enumerate(read_text(path).split('\n'), 1):
        if not line.strip() or line.startswith('#'):
            continue
        fields = line.split('\t')
        if not header:
            if fields != HEADER:
                stop('%s line %d: the header MUST be %s, tab-separated.'
                     % (os.path.abspath(path), n, ' '.join(HEADER)))
            header = True
            continue
        rows.append((os.path.abspath(path), n, fields))
    if not header:
        stop('%s holds no header line. The header MUST be %s, tab-separated.'
             % (os.path.abspath(path), ' '.join(HEADER)))
    return rows


def invalid(fields):
    """Why one exception row is invalid, or None."""
    if len(fields) != 7:
        return 'it has %d fields, not 7' % len(fields)
    _, _, section, kind, en, tr, reason = fields
    if not re.fullmatch(r'[0-9]+', section):
        return 'section %r is not an integer' % section
    if kind not in KINDS:
        return 'kind %r is not code, link, image or bold' % kind
    if not en and not tr:
        return 'both sides are empty'
    if en == tr:
        return 'english and translation are equal'
    m = re.match(r'\((a|b)\) ', reason)
    if not m:
        return 'the reason does not start with the cause (a) or (b)'
    # F1 P4a: cause (a) is a string literal in a code span, cause (b) a localized link.
    need = CAUSE_KIND[m.group(1)]
    if kind != need:
        return 'cause (%s) needs kind %s, not %s' % (m.group(1), need, kind)
    return None


def q(s):
    return json.dumps(s, ensure_ascii=False)


def compare(lang, stem, en, tr, rows, findings, stats):
    """Append the findings of one pair. rows: the exception rows of this pair."""
    file = stem + '.qmd'
    hint_ok = [len(e[1]) == len(t[1]) for e, t in zip(en, tr)]
    count = {}
    where = {}
    for side, secs in (('en', en), ('tr', tr)):
        for s, (_, blocks) in enumerate(secs):
            for b, found in enumerate(blocks):
                for kind, item in found:
                    count.setdefault((side, s, kind), Counter())[item] += 1
                    where.setdefault((side, s, kind, item), []).append(b)
    for src, n, fields in rows:
        _, _, section, kind, e, t, _ = fields
        s = int(section)
        head = en[s][0] if s < len(en) else ''
        ce = count.setdefault(('en', s, kind), Counter())
        ct = count.setdefault(('tr', s, kind), Counter())
        ok_e = not e or (s < len(en) and ce[e] > 0)
        ok_t = not t or (s < len(tr) and ct[t] > 0)
        if ok_e and ok_t:
            if e:
                ce[e] -= 1
            if t:
                ct[t] -= 1
            stats['applied'] += 1
            continue
        why = ('section %d does not exist' % s if s >= len(en) else
               'english found %s, translation found %s'
               % ('n/a' if not e else ('yes' if ok_e else 'no'),
                  'n/a' if not t else ('yes' if ok_t else 'no')))
        findings.append((lang, stem, s, len(KINDS), 'stale-exception', '',
                         '%s %s section %d %s stale-exception %s english %s translation %s: '
                         'row %d of %s, %s' % (lang, file, s, q(head), kind, q(e), q(t), n, src,
                                               why), 0))
    for s in range(len(en)):
        for k, kind in enumerate(KINDS):
            ce = count.get(('en', s, kind), Counter())
            ct = count.get(('tr', s, kind), Counter())
            for item in sorted(set(ce) | set(ct)):
                a, b = ce[item], ct[item]
                if a == b:
                    continue
                line = '%s %s section %d %s %s %s: English %d, translation %d' % (
                    lang, file, s, q(en[s][0]), kind, q(item), a, b)
                if hint_ok[s]:
                    line += ' [blocks: English %s; translation %s]' % (
                        ','.join(map(str, where.get(('en', s, kind, item), []))) or '-',
                        ','.join(map(str, where.get(('tr', s, kind, item), []))) or '-')
                tag = '%s %s' % (kind, 'missing' if b < a else 'extra')
                findings.append((lang, stem, s, k, item, tag, line, abs(a - b)))
                stats['sections'].add((lang, stem, s))


def load(root):
    """Every input of one tree: (main, langs, stems, exception rows). The check and the
    self-test both call it, so the self-test validates exactly what a run reads. Stops with
    exit 2 and one message on the first missing or unusable input."""
    if not os.path.isdir(root):
        stop('%s is not a folder. It is the repository tree to check.' % os.path.abspath(root))
    main_lang, codes, stems = read_declared(root)
    langs = [c for c in codes if c != main_lang]
    if not langs:
        stop('%s declares no language other than %s, so nothing would be compared.'
             % (os.path.abspath(os.path.join(root, 'languages.yml')), main_lang))
    stems = [s for s in stems if s != 'index']
    if not stems:
        stop('%s declares no chapter other than index.qmd, so nothing would be compared.'
             % os.path.abspath(os.path.join(root, 'content', main_lang, '_quarto.yaml')))
    for l in [main_lang] + langs:
        for s in stems:
            p = os.path.join(root, 'content', l, s + '.qmd')
            if not os.path.isfile(p):
                stop('no %s. %s declares that chapter.'
                     % (os.path.abspath(p), os.path.abspath(
                         os.path.join(root, 'content', main_lang, '_quarto.yaml'))))
            read_text(p)
    rows = read_exceptions(os.path.join(root, 'checks', 'parity-exceptions.tsv'))
    load_names()
    return main_lang, langs, stems, rows


def default_pandoc():
    return ['quarto', 'pandoc'] if shutil.which('quarto') else ['pandoc']


def check(root, summary, pandoc):
    """Print the findings and the totals of one tree. Returns the exit status."""
    main_lang, langs, stems, rows = load(root)
    path = lambda l, s: os.path.join(root, 'content', l, s + '.qmd')
    pairs = [(l, s) for l in langs for s in stems]
    files = [(main_lang, s) for s in stems] + pairs
    with ThreadPoolExecutor(8) as ex:
        parsed = dict(zip(files, ex.map(lambda f: parse(path(*f), pandoc), files)))
    errors, findings = [], []
    stats = {'applied': 0, 'sections': set()}
    by_pair = {}
    for src, n, fields in rows:
        why = invalid(fields)
        if why is None and (fields[0] not in langs or fields[1][:-4] not in stems
                            or not fields[1].endswith('.qmd')):
            why = 'no translated pair %s %s in scope' % (fields[0], fields[1])
        if why is not None:
            lang = fields[0] if fields[0] in langs else ''
            stem = fields[1][:-4] if len(fields) > 1 and fields[1][:-4] in stems else ''
            findings.append((lang, stem, -1, len(KINDS) + 1, 'invalid-exception', '',
                             '%s: row %d of %s is an invalid-exception: %s'
                             % (PROG, n, src, why), 0))
            continue
        by_pair.setdefault((fields[0], fields[1][:-4]), []).append((src, n, fields))
    compared = Counter()
    for l, s in pairs:
        en, err_en = parsed[(main_lang, s)]
        tr, err_tr = parsed[(l, s)]
        if err_en or err_tr:
            errors.append('%s: %s %s' % (PROG, os.path.abspath(path(*(
                (main_lang, s) if err_en else (l, s)))), err_en or err_tr))
            continue
        if len(en) != len(tr):
            errors.append('%s: %s has %d headings and %s has %d. The sections do not '
                          'correspond, so the chapter is not compared.'
                          % (PROG, os.path.abspath(path(l, s)), len(tr) - 1,
                             os.path.abspath(path(main_lang, s)), len(en) - 1))
            continue
        compared[l] += 1
        compare(l, s, en, tr, by_pair.get((l, s), []), findings, stats)
    order = {c: i for i, c in enumerate(langs)}
    order[''] = len(langs)
    sorder = {s: i for i, s in enumerate(stems)}
    sorder[''] = len(stems)
    findings.sort(key=lambda f: (order[f[0]], sorder[f[1]], f[2], f[3], f[4]))
    tally = Counter()
    per_lang = Counter()
    items_total = 0
    for f in findings:
        if not summary:
            print(f[-2])
        tally[f[-3] or f[4]] += 1
        per_lang[f[0]] += 1
        items_total += f[-1]
    for l in langs:
        print('parity %s: pairs %d, compared %d, findings %d'
              % (l, len(stems), compared[l], per_lang[l]))
    tags = []
    for k in KINDS:
        tags += ['%s missing' % k, '%s extra' % k]
    tags += ['stale-exception', 'invalid-exception']
    print('parity: pairs %d (%d languages x %d stems), compared %d, pandoc %s, findings %d (%s), '
          'items %d, sections with a finding %d, exception rows %d (applied %d)'
          % (len(pairs), len(langs), len(stems), sum(compared.values()), ' '.join(pandoc),
             len(findings), ', '.join('%s %d' % (t, tally[t]) for t in tags), items_total,
             len(stats['sections']), len(rows), stats['applied']))
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        return 2
    return 1 if findings else 0


def self_test(pandoc):
    dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir()) if FIXTURES.is_dir() else []
    if not dirs:
        stop('no fixture folder under %s, so nothing would be tested.' % FIXTURES)
    for n in REQUIRED:
        if not (FIXTURES / n).is_dir():
            stop('no %s. That fixture is one of the REQUIRED fixtures.' % (FIXTURES / n))
    # A missing or unusable fixture input stops the self-test before any fixture runs.
    expects = {}
    for d in dirs:
        p = d / 'expect.txt'
        if not p.is_file():
            stop('no %s. Each fixture needs one, so that its result can be compared.' % p)
        expect = [x.rstrip() for x in read_text(str(p)).split('\n') if x.strip()]
        kind = expect[0] if expect else ''
        if kind not in ('pass', 'fail') or not d.name.startswith(kind + '-') \
                or (kind == 'pass') != (len(expect) == 1):
            stop('%s MUST hold `pass` alone, or `fail` and its findings, as the folder name '
                 'says.' % p)
        load(str(d))
        expects[d] = expect
    bad, lines = [], []
    for d in dirs:
        expect = expects[d]
        kind = expect[0]
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--pandoc',
                              shlex.join(pandoc), str(d)],
                             capture_output=True, text=True, timeout=120)
        # A child that exits 2 or crashes met an input that load() did not check, so the
        # fixture is unusable, and its result is not a pass or a fail.
        if run.returncode == 2 or 'Traceback' in run.stderr:
            stop('%s: the check exited %d on this fixture: %s'
                 % (d, run.returncode, ' '.join(run.stderr.split())))
        got = [x.replace(str(d), '<fixture>') for x in run.stdout.split('\n')
               if x.strip() and not x.startswith('parity')]
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
    summary, pandoc, rest, self = False, None, [], False
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
        elif a.startswith('-'):
            stop('unknown argument %s. Usage: %s' % (a, usage))
        else:
            rest.append(a)
        i += 1
    if len(rest) > 1 or (self and (rest or summary)):
        stop('expected at most one tree, and no tree with --self-test. Usage: %s' % usage)
    pandoc = pandoc or default_pandoc()
    if self:
        return self_test(pandoc)
    return check(os.path.abspath(rest[0]) if rest else str(ROOT), summary, pandoc)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
