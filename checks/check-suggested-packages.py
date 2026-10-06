#!/usr/bin/env python3
"""Every package that chapter 5 suggests must be used in the R code of another English chapter.

Chapter 5 is `content/<main>/packages_suggested.qmd`. Its packages are the arguments of each
`p_load()` call and the repositories of each `p_install_gh()` call in its R chunks. The other
chapters are every stem that `content/<main>/_quarto.yaml` declares, read by `checks/langs.py`.

One R process parses every R chunk of those chapters with `parse()` and `getParseData()`. A
package is used when one of these names it:

1. a `SYMBOL_PACKAGE` token, as in `pkg::f` and `pkg:::f`
2. an argument of `library()`, `require()`, `requireNamespace()` or `p_load()`, with or
   without `pacman::`
3. a repository string that ends in `/<pkg>` or `/<pkg>@<ref>`, in `p_load_gh()`,
   `p_install_gh()`, `p_load_current_gh()` or `install_github()`

A call counts only when it has no namespace or the namespace of the package that exports the
function: `base`, `pacman`, or `remotes` and `devtools` for `install_github()`. So
`other::p_load(x)` names no package. `p_load()`, `p_load_gh()` and `p_load_current_gh()` take
their packages from every unnamed argument and from `char =`. Each other function takes one: the
argument named `package` or `repo`, or else the first unnamed argument. So the `ref` in
`install_github("owner/a", "feature/b")` names no package. A string counts alone or inside `c()`.
The same rules give the packages of chapter 5.

A comment never counts, because the parser drops it. Another string never counts. A chunk that
does not parse adds no package, and the summary gives the count of those chunks. Check 16 fails
on such a chunk unless `checks/parse-exceptions.tsv` names it.

The check needs `Rscript` on PATH. Without it the check stops with exit 2 and one line that says
so. It never skips.

Exit 0 when every listed package is used, 1 when one is not, and 2 when the check cannot run.

Usage: python3 checks/check-suggested-packages.py [--summary]
"""
import os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'checks'))
FENCE_OPEN = re.compile(r'^\s*(`{3,})\s*\{r([ ,}].*)$')
CHAPTER5 = 'packages_suggested'

args = sys.argv[1:]
for a in args:
    if a != '--summary':
        sys.exit('unknown argument %s. Usage: %s' % (a, __doc__.strip().split('Usage: ')[1]))
summary = '--summary' in args


def die(msg):
    print('check-suggested-packages: %s' % msg, file=sys.stderr)
    sys.exit(2)


# The R code. It reads a list of chunk files and a list of roles, `listed` for a chunk of
# chapter 5 and `user` for any other chunk. It prints one line for each finding:
# `LISTED\t<pkg>\t<file>\t<line in chunk>`, `USED\t<pkg>\t<file>` or `PARSE\t<file>`.
R_CODE = r'''
LOADERS <- c("library", "require", "requireNamespace", "p_load")
GITHUB <- c("p_load_gh", "p_install_gh", "p_load_current_gh", "install_github")
# The package that exports each function. A call with another namespace, as `other::p_load()`,
# is not this function and names no package.
HOME <- list(library = "base", require = "base", requireNamespace = "base",
  p_load = "pacman", p_load_gh = "pacman", p_install_gh = "pacman",
  p_load_current_gh = "pacman", install_github = c("remotes", "devtools"))
fname <- function(head) {
  if (is.name(head)) return(as.character(head))
  if (is.call(head) && is.name(head[[1]]) && as.character(head[[1]]) %in% c("::", ":::")) {
    f <- as.character(head[[3]])
    if (f %in% names(HOME) && !(as.character(head[[2]]) %in% HOME[[f]])) return("")
    return(f)
  }
  ""
}
# The strings in one argument: a string, or a c() call of strings, as `char = c("a", "b")` is.
strs <- function(x) {
  if (is.character(x)) return(x)
  if (is.call(x) && identical(x[[1]], as.name("c"))) return(unlist(lapply(as.list(x)[-1], strs)))
  character(0)
}
# The arguments of one call that name its packages. pacman 0.5.1 takes them through `...` and
# `char` in p_load(), p_load_gh() and p_load_current_gh(). Every other function here takes ONE:
# the argument named `package` or `repo`, or else the first unnamed argument. A later unnamed
# argument is another formal, as `ref` is in install_github().
pkg_args <- function(e, f) {
  a <- as.list(e)[-1]
  n <- names(a)
  if (is.null(n)) n <- rep("", length(a))
  if (f %in% c("p_load", "p_load_gh", "p_load_current_gh")) return(a[n %in% c("", "char")])
  named <- a[n %in% c("package", "repo")]
  if (length(named)) return(head(named, 1))
  head(a[n == ""], 1)
}
loaded <- function(e, f) {
  out <- character(0)
  for (x in pkg_args(e, f)) {
    if (is.name(x) && nzchar(as.character(x))) out <- c(out, as.character(x))
    out <- c(out, strs(x))
  }
  out
}
repos <- function(e, f) {
  out <- character(0)
  for (x in unlist(lapply(pkg_args(e, f), strs))) {
    m <- regmatches(x, regexec("/([A-Za-z][A-Za-z0-9.]*)(@[^/]*)?$", x))[[1]]
    if (length(m)) out <- c(out, m[2])
  }
  out
}
# Every package a call names, by the rules above. `which` limits the call names.
walk <- function(e, which, hits) {
  if (is.call(e)) {
    f <- fname(e[[1]])
    if (f %in% intersect(LOADERS, which)) hits <- c(hits, loaded(e, f))
    if (f %in% intersect(GITHUB, which)) hits <- c(hits, repos(e, f))
  }
  if (is.call(e) || is.pairlist(e) || is.expression(e)) {
    l <- as.list(e)
    # An empty argument, as in x[, 1], is the empty symbol. It cannot be passed on.
    for (i in seq_along(l)) if (!(is.name(l[[i]]) && !nzchar(as.character(l[[i]])))) hits <- walk(l[[i]], which, hits)
  }
  hits
}
fs <- readLines(commandArgs(TRUE)[1])
roles <- readLines(commandArgs(TRUE)[2])
for (k in seq_along(fs)) {
  f <- fs[k]
  ex <- tryCatch(parse(file = f, keep.source = TRUE), error = function(err) err)
  if (inherits(ex, "error")) {
    cat("PARSE\t", f, "\n", sep = "")
    next
  }
  pd <- getParseData(ex)
  if (roles[k] == "listed") {
    for (p in unique(walk(ex, c("p_load", "p_install_gh"), character(0)))) {
      # The line of the first token that names the package, as a symbol or inside a string.
      hit <- pd$token %in% c("SYMBOL", "STR_CONST") &
        (pd$text == p | grepl(paste0("/", p, "(@[^/]*)?[\"']$"), pd$text))
      cat("LISTED\t", p, "\t", f, "\t", pd$line1[hit][1], "\n", sep = "")
    }
  } else {
    used <- c(pd$text[pd$token == "SYMBOL_PACKAGE"], walk(ex, c(LOADERS, GITHUB), character(0)))
    for (p in unique(used)) cat("USED\t", p, "\t", f, "\n", sep = "")
  }
}
cat("R_VERSION\t", R.version$major, ".", R.version$minor, "\n", sep = "")
'''


def chunks(text):
    """Every R chunk: (header line number, body lines)."""
    out, cur, fence = [], None, None
    for n, line in enumerate(text.split('\n'), 1):
        if cur is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence, cur = m.group(1), (n, [])
        elif re.match(r'^\s*' + fence + r'\s*$', line):
            out.append(cur)
            cur = None
        else:
            cur[1].append(line)
    return out


# The inputs come first, so a missing file is named even where R is also missing.
os.chdir(ROOT)
from langs import Unreadable, read_languages, read_stems
try:
    main, _ = read_languages('languages.yml')
    stems = read_stems('content/%s/_quarto.yaml' % main)
except Unreadable as e:
    die(e.why)
ch5 = 'content/%s/%s.qmd' % (main, CHAPTER5)
if CHAPTER5 not in stems:
    die('content/%s/_quarto.yaml declares no %s.qmd, so no package list is checked.'
        % (main, CHAPTER5))
missing = ['content/%s/%s.qmd' % (main, s) for s in stems
           if not os.path.isfile('content/%s/%s.qmd' % (main, s))]
if missing:
    die('%s is missing. content/%s/_quarto.yaml declares it.' % (missing[0], main))

rscript = shutil.which('Rscript')
if rscript is None:
    die('Rscript is not on PATH, so no chunk was parsed. Check 19 needs R. '
        'Run it where R is installed, for example in the book\'s image.')

tmp = tempfile.mkdtemp(prefix='suggested-packages-')
try:
    index = []  # (chapter file, header line, role, chunk path)
    for s in dict.fromkeys(stems):
        rel = 'content/%s/%s.qmd' % (main, s)
        role = 'listed' if s == CHAPTER5 else 'user'
        for k, (n, body) in enumerate(chunks(Path(rel).read_text(encoding='utf-8'))):
            p = os.path.join(tmp, '%s__%d.R' % (s, k))
            Path(p).write_text('\n'.join(body) + '\n', encoding='utf-8')
            index.append((rel, n, role, p))
    if not any(r[2] == 'listed' for r in index):
        die('%s holds no R chunk, so no package list is checked.' % ch5)
    listing = os.path.join(tmp, 'files.txt')
    Path(listing).write_text('\n'.join(r[3] for r in index) + '\n', encoding='utf-8')
    roles = os.path.join(tmp, 'roles.txt')
    Path(roles).write_text('\n'.join(r[2] for r in index) + '\n', encoding='utf-8')
    res = subprocess.run([rscript, '-e', R_CODE, listing, roles], capture_output=True, text=True)
    if res.returncode != 0:
        die('Rscript exited %d while parsing the chunks:\n%s' % (res.returncode, res.stderr.rstrip()))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

by_path = {r[3]: r for r in index}
listed, used, unparsed, r_version = {}, {}, [], None
for line in res.stdout.split('\n'):
    parts = line.split('\t')
    if parts[0] == 'R_VERSION':
        r_version = parts[1]
    elif parts[0] == 'PARSE' and parts[1] in by_path:
        unparsed.append(by_path[parts[1]])
    elif parts[0] == 'LISTED' and len(parts) == 4 and parts[2] in by_path:
        rel, n = by_path[parts[2]][:2]
        at = n + int(parts[3]) if parts[3] != 'NA' else n
        listed.setdefault(parts[1], '%s:%d' % (rel, at))
    elif parts[0] == 'USED' and len(parts) == 3 and parts[2] in by_path:
        used.setdefault(parts[1], by_path[parts[2]][0])
if r_version is None:
    die('Rscript printed no result line, so the parse did not finish:\n%s' % res.stderr.rstrip())
if not listed:
    die('%s names no package in a p_load() or p_install_gh() call, so nothing is checked.' % ch5)

unused = sorted(p for p in listed if p not in used)
if summary:
    print('chapters %d, chunks %d, chunks that do not parse %d, R %s'
          % (len(dict.fromkeys(stems)), len(index), len(unparsed), r_version))
    print('packages listed in %s %d, used %d, unused %d'
          % (ch5, len(listed), len(listed) - len(unused), len(unused)))
for p in unused:
    print('UNUSED %s at %s: no other declared chapter of content/%s/ uses it in R code'
          % (p, listed[p], main))
sys.exit(1 if unused else 0)
