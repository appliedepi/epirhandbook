"""Find the grid tables in a chapter and measure their rows the way pandoc does.

A pandoc grid table is a block of lines that start in column 0: separator lines that start
with `+` and content rows that start with `|`. Pandoc reads a column boundary only where a
`|` of a content row sits exactly under a `+` of the separator lines. A row whose borders do
not line up makes pandoc drop the whole table. A header row above a `+===+` line then becomes
a setext level-1 heading, which Quarto numbers as a chapter.

Pandoc measures a line by display width, not by characters. A wide or fullwidth East Asian
character takes two columns, a combining mark takes none, and every other character takes
one. `width()` follows the same rule.

Pandoc does not parse cell text to find the boundaries. It slices each content row at the
display columns of the `+` of the separator line above it, and a row is aligned when it holds
a `|` at every one of those columns. A `|` anywhere else is cell text.

Used by check-grid-tables.py (check 19) and rewrite-links.py.
"""
import re
import unicodedata

FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
# A table starts at a separator, indented by up to three spaces as pandoc allows, whose first
# segment is dashes, equals signs or an alignment colon.
START = re.compile(r'^( {0,3})\+[-=:]')
# A separator line holds nothing but + and the rule characters.
SEPARATOR = re.compile(r'^\+(?:[-=:]+\+)+\s*$')


def width(text):
    """The display width of text, as pandoc measures it."""
    n = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        n += 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1
    return n


def char_at(row, column):
    """The character of a row that starts at a display column, or None."""
    col = 0
    for ch in row:
        w = width(ch)
        if w == 0:
            continue            # a combining mark belongs to the character before it
        if col == column:
            return ch
        col += w
        if col > column:
            return None
    return None


def corners(separator):
    """The display columns of the + of a separator line."""
    return [i for i, ch in enumerate(separator) if ch == '+']


def tables(lines):
    """Yield (first, last, indent) of each grid table outside code: line indexes, both
    inclusive, and the indent its lines share.

    A table starts at a separator, indented by up to three spaces, that does not follow a
    table line. Fenced code is skipped with the CommonMark rule check-links.py uses: an
    indent of four spaces or more opens and closes no fence.
    """
    fence, i = None, 0
    while i < len(lines):
        line = lines[i]
        m = FENCE.match(line)
        if m and len(m.group(1)) <= 3:
            if fence is None:
                fence = m.group(2)
            elif m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) \
                    and not m.group(3).strip():
                fence = None
            i += 1
            continue
        start = START.match(line) if fence is None else None
        if start and (i == 0 or not lines[i - 1].lstrip(' ').startswith(('+', '|'))):
            pad = start.group(1)
            j = i
            while j + 1 < len(lines) and lines[j + 1].startswith(pad) and \
                    lines[j + 1][len(pad):].startswith(('+', '|')):
                j += 1
            yield i, j, len(pad)
            i = j + 1
            continue
        i += 1


def problems(lines, first, last, indent=0):
    """The misaligned lines of one table, as (line index, reason).

    The check does not model row or column spans. A table with a spanning cell fails it,
    and needs to be written without the span. None of the declared chapters has one.
    """
    want = corners(lines[first][indent:])
    out = []
    for k in range(first, last + 1):
        line = lines[k][indent:].rstrip()
        if '\t' in line:
            out.append((k, 'a tab, which pandoc expands to a tab stop; use spaces'))
            continue
        if line.startswith('+'):
            if not SEPARATOR.match(line):
                out.append((k, 'a separator line with a character other than + - = :'))
            elif corners(line) != want:
                out.append((k, 'a separator whose + do not match the first separator'))
            continue
        missing = [c for c in want if char_at(line, c) != '|']
        if missing:
            out.append((k, 'a row with no | at column %s, where the separators put a +'
                        % ', '.join(map(str, missing))))
            continue
        for a, b in zip(want, want[1:]):
            cell = cell_text(line, a, b)
            if re.match(r'\s*#{1,6}\s', cell):
                out.append((k, 'a cell that starts with #, which pandoc reads as a heading'))
                break
    return out


def cell_text(row, start, end):
    """The text of a row between display columns start and end, exclusive of both."""
    col, out = 0, []
    for ch in row:
        if start < col < end:
            out.append(ch)
        col += width(ch)
    return ''.join(out)
