#!/usr/bin/env python3
"""Parse every R chunk of the English chapters with R, and refuse code that muffles warnings.

The file set is every `content/en/*.qmd`. A chunk is a ```{r ...} fence. One R process parses
every chunk with `parse()`. Translations carry the same code byte for byte, check 3 says so, so
the English chapters are enough.

Two rules fail the check.

1. A chunk that does not parse. A chunk is exempt only when `checks/parse-exceptions.tsv` names
   it, by stem and by the first non-empty line of the chunk, with a reason. An exception that
   names no failing chunk is stale, and that fails too.
2. A call to `suppressWarnings()` in a chunk that runs. Also a call to `options()` with a
   `warn` argument that is not a non-negative number literal, such as `0`, `1` or `1L`. So
   `options(warn = -1)`, `options(warn = 0 - 1)` and `options(warn = x)` all fail. An
   `options()` call with no `warn` argument is not judged. A chunk with `eval=F` or
   `eval=FALSE` in its header, or `#| eval: false` in its body, does not run. R finds the
   calls by a walk of the parsed expressions, not by a text search.

The render profile in the book's image logs every warning that reaches knitr. A warning muffled
inside chunk code never reaches knitr, so the log cannot show it.

The check needs `Rscript` on PATH. Without it the check stops with exit 2 and one line that says
so. It never skips.

Exit 0 when every chunk passes, 1 when one fails a rule, and 2 when the check cannot run.

Usage: python3 checks/check-english-parse.py [--summary]
"""
import csv, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCEPTIONS = ROOT / 'checks' / 'parse-exceptions.tsv'
FENCE_OPEN = re.compile(r'^\s*(`{3,})\s*\{r([ ,}].*)$')
NO_EVAL_HEADER = re.compile(r'\beval\s*=\s*(?:F|FALSE)\b')
NO_EVAL_BODY = re.compile(r'^\s*#\|\s*eval:\s*false\s*$')

args = sys.argv[1:]
for a in args:
    if a != '--summary':
        sys.exit('unknown argument %s. Usage: %s' % (a, __doc__.strip().split('Usage: ')[1]))
summary = '--summary' in args


def die(msg):
    print('check-english-parse: %s' % msg, file=sys.stderr)
    sys.exit(2)


# The R code. It reads a list of chunk files and prints one line for each failure:
# `<file>\tPARSE\t<message>` or `<file>\tMUFFLE\t<line in chunk>\t<call>`.
R_CODE = r'''
# TRUE only for a non-negative number literal: 0, 1, 2, 1L. A call such as -1 or 0 - 1, a
# name, and an empty argument are all FALSE.
safe_warn <- function(x) is.numeric(x) && length(x) == 1 && !is.na(x) && x >= 0
fname <- function(head) {
  if (is.name(head)) return(as.character(head))
  if (is.call(head) && is.name(head[[1]]) && as.character(head[[1]]) %in% c("::", ":::")) return(as.character(head[[3]]))
  ""
}
walk <- function(e, hits) {
  if (is.call(e)) {
    f <- fname(e[[1]])
    if (f == "suppressWarnings") hits <- c(hits, "suppressWarnings()")
    if (f == "options" && length(e) > 1) {
      a <- as.list(e)[-1]
      n <- names(a)
      if (!is.null(n)) for (i in which(n == "warn")) if ((is.name(a[[i]]) && !nzchar(as.character(a[[i]]))) || !safe_warn(a[[i]])) hits <- c(hits, "options(warn = <not a non-negative number literal>)")
    }
  }
  if (is.call(e) || is.pairlist(e) || is.expression(e)) {
    l <- as.list(e)
    # An empty argument, as in x[, 1], is the empty symbol. It cannot be passed on.
    for (i in seq_along(l)) if (!(is.name(l[[i]]) && !nzchar(as.character(l[[i]])))) hits <- walk(l[[i]], hits)
  }
  hits
}
fs <- readLines(commandArgs(TRUE)[1])
evals <- readLines(commandArgs(TRUE)[2]) == "1"
for (k in seq_along(fs)) {
  f <- fs[k]
  ex <- tryCatch(parse(file = f, keep.source = TRUE), error = function(err) err)
  if (inherits(ex, "error")) {
    cat(f, "\tPARSE\t", gsub("[\r\n]+", " ", conditionMessage(ex)), "\n", sep = "")
    next
  }
  if (!evals[k]) next
  refs <- attr(ex, "srcref")
  for (j in seq_along(ex)) {
    for (h in walk(ex[[j]], character(0))) cat(f, "\tMUFFLE\t", refs[[j]][1], "\t", h, "\n", sep = "")
  }
}
cat("R_VERSION\t", R.version$major, ".", R.version$minor, "\n", sep = "")
'''


def chunks(text):
    """Every R chunk: (header line number, header, body lines)."""
    out, cur, fence = [], None, None
    for n, line in enumerate(text.split('\n'), 1):
        if cur is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence, cur = m.group(1), (n, m.group(2), [])
        elif re.match(r'^\s*' + fence + r'\s*$', line):
            out.append(cur)
            cur = None
        else:
            cur[2].append(line)
    return out


def first_line(body):
    for l in body:
        if l.strip():
            return l.strip()
    return ''


def read_exceptions():
    """{(stem, first non-empty line): row number} from parse-exceptions.tsv."""
    if not EXCEPTIONS.exists():
        die('%s is missing. It lists the chunks that are pseudo-code on purpose.'
            % EXCEPTIONS.relative_to(ROOT))
    out = {}
    with open(EXCEPTIONS, encoding='utf-8', newline='') as fh:
        rows = list(csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONE))
    if not rows or [c.strip() for c in rows[0]] != ['stem', 'first_line', 'reason']:
        die('%s must start with the header line: stem, first_line, reason, tab-separated.'
            % EXCEPTIONS.relative_to(ROOT))
    for i, r in enumerate(rows[1:], 2):
        if not any(c.strip() for c in r):
            continue
        if len(r) != 3 or not all(c.strip() for c in r):
            die('%s line %d needs three non-empty fields: stem, first_line, reason.'
                % (EXCEPTIONS.relative_to(ROOT), i))
        out[(r[0].strip(), r[1].strip())] = i
    return out


# The inputs come first, so a missing file is named even where R is also missing.
files = sorted((ROOT / 'content' / 'en').glob('*.qmd'))
if not files:
    die('content/en/ holds no .qmd file, so there is nothing to parse.')
exceptions = read_exceptions()

rscript = shutil.which('Rscript')
if rscript is None:
    die('Rscript is not on PATH, so no chunk was parsed. Check 16 needs R. '
        'Run it where R is installed, for example in the book\'s image.')

tmp = tempfile.mkdtemp(prefix='english-parse-')
try:
    index = []  # (file, header line, stem, first line, evaluated, chunk path)
    for f in files:
        rel = str(f.relative_to(ROOT))
        for k, (n, header, body) in enumerate(chunks(f.read_text(encoding='utf-8'))):
            p = os.path.join(tmp, '%s__%d.R' % (f.stem, k))
            Path(p).write_text('\n'.join(body) + '\n', encoding='utf-8')
            runs = not NO_EVAL_HEADER.search(header) and not any(NO_EVAL_BODY.match(l) for l in body)
            index.append((rel, n, f.stem, first_line(body), runs, p))
    listing = os.path.join(tmp, 'files.txt')
    Path(listing).write_text('\n'.join(r[5] for r in index) + '\n', encoding='utf-8')
    evals = os.path.join(tmp, 'evals.txt')
    Path(evals).write_text('\n'.join('1' if r[4] else '0' for r in index) + '\n', encoding='utf-8')
    res = subprocess.run([rscript, '-e', R_CODE, listing, evals], capture_output=True, text=True)
    if res.returncode != 0:
        die('Rscript exited %d while parsing the chunks:\n%s' % (res.returncode, res.stderr.rstrip()))
finally:
    subprocess.run(['rm', '-rf', tmp])

by_path = {r[5]: r for r in index}
parse_fail, excepted, muffle, used, r_version = [], [], [], set(), None
for line in res.stdout.split('\n'):
    parts = line.split('\t')
    if parts[0] == 'R_VERSION':
        r_version = parts[1]
        continue
    if len(parts) < 3 or parts[0] not in by_path:
        continue
    rel, n, stem, first, _, _ = by_path[parts[0]]
    if parts[1] == 'PARSE':
        key = (stem, first)
        if key in exceptions:
            used.add(key)
            excepted.append((rel, n))
        else:
            # R names the temporary chunk file. The chunk's own line number is what helps.
            why = parts[2].replace(parts[0] + ':', 'chunk line ', 1)
            parse_fail.append('PARSE-FAIL %s:%d %s' % (rel, n, why))
    elif parts[1] == 'MUFFLE':
        muffle.append('MUFFLE %s:%d %s' % (rel, n + int(parts[2]), parts[3]))
if r_version is None:
    die('Rscript printed no result line, so the parse did not finish:\n%s' % res.stderr.rstrip())
stale = ['STALE-EXCEPTION %s:%d %s | %s names no chunk that fails to parse'
         % (EXCEPTIONS.relative_to(ROOT), i, s, l)
         for (s, l), i in sorted(exceptions.items(), key=lambda x: x[1]) if (s, l) not in used]

if summary:
    print('files %d, chunks %d, evaluated %d, R %s'
          % (len(files), len(index), sum(1 for r in index if r[4]), r_version))
    print('parse failures %d, excepted %d, stale exceptions %d'
          % (len(parse_fail), len(excepted), len(stale)))
    print('muffling calls in evaluated chunks %d' % len(muffle))
else:
    for l in parse_fail + muffle + stale:
        print(l)
sys.exit(1 if parse_fail or muffle or stale else 0)
