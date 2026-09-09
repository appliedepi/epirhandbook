#!/usr/bin/env python3
"""Parse every R code chunk of every changed translated chapter with R, before and after.

For each chapters/<chapter>.<lang>.qmd changed between BASE and HEAD, extract the ```{r ...}
chunks from both versions, parse every chunk in ONE R process, and compare the two versions
chunk index by chunk index. The gate FAILS when a chunk index fails to parse after and did not
fail before, unless the English chunk at that index fails too: that is the source's pseudo-code
or defect, not a regression. It prints every failing chunk after, so a pre-existing failure is
visible too.

The per-index comparison is what makes the gate honest. A count comparison reads "same" when one
chunk breaks and another is repaired in the same file.

Proved red: an extra closing parenthesis is reported by parse(). Proved red again on a file where
one chunk breaks and another is fixed in the same commit.

Exit 0 when no chunk regresses, 1 when one does, 2 when the gate cannot run: a base or head that
is not a commit, a git command that fails, or a missing or failing Rscript.

Usage: python3 checks/chunk-parse-gate.py <base> [head]
"""
import os, re, shutil, subprocess, sys, tempfile

USAGE = __doc__.strip().split('Usage: ')[1].strip()
if len(sys.argv) < 2:
    print('Usage: %s' % USAGE, file=sys.stderr)
    sys.exit(2)
base = sys.argv[1]; head = sys.argv[2] if len(sys.argv) > 2 else 'HEAD'


def die(msg, detail=''):
    print('chunk-parse-gate: %s' % msg, file=sys.stderr)
    if detail:
        print(detail.rstrip(), file=sys.stderr)
    sys.exit(2)


def git(args):
    return subprocess.run(['git'] + args, capture_output=True, text=True)


for c in (base, head):
    if git(['cat-file', '-e', '%s^{commit}' % c]).returncode != 0:
        die("'%s' is not a commit in this repository" % c)

rscript = shutil.which('Rscript')
if rscript is None:
    die('Rscript is not on PATH. This gate parses every chunk with R.')

d = git(['diff', '--name-only', base, head, '--', 'chapters/'])
if d.returncode != 0:
    die('git diff %s %s failed' % (base, head), d.stderr)
files = [f for f in d.stdout.split() if re.search(r'\.[a-z]{2}\.qmd$', f)]
FENCE_OPEN = re.compile(r'^\s*(`{3,})\s*\{r[ ,}]')


def chunks(text):
    out, cur, fence = [], None, None
    for line in text.split('\n'):
        if cur is None:
            m = FENCE_OPEN.match(line)
            if m: fence = m.group(1); cur = []
        elif re.match(r'^\s*' + fence + r'\s*$', line): out.append('\n'.join(cur)); cur = None
        else: cur.append(line)
    return out


tmp = tempfile.mkdtemp(prefix='parse-gate-')
index = []  # (file, version, i, path)
for f in files:
    show = git(['show', '%s:%s' % (base, f)])
    if show.returncode != 0:
        # A file added since base has no version at base, and that is not an error.
        if git(['cat-file', '-e', '%s:%s' % (base, f)]).returncode == 0:
            subprocess.run(['rm', '-rf', tmp])
            die('git show %s:%s failed' % (base, f), show.stderr)
        old = ''
    else:
        old = show.stdout
    new = open(f, encoding='utf-8').read() if os.path.exists(f) else ''
    en_path = re.sub(r'\.[a-z]{2}\.qmd$', '.qmd', f)
    english = open(en_path, encoding='utf-8').read() if os.path.exists(en_path) else ''
    for version, text in (('before', old), ('after', new), ('english', english)):
        for i, c in enumerate(chunks(text)):
            p = os.path.join(tmp, '%s__%s__%d.R' % (os.path.basename(f), version, i))
            open(p, 'w', encoding='utf-8').write(c); index.append((f, version, i, p))
listing = os.path.join(tmp, 'files.txt'); open(listing, 'w').write('\n'.join(p for _, _, _, p in index))
r_code = '''
fs <- readLines(commandArgs(TRUE)[1]); out <- character(0)
for (f in fs) { e <- tryCatch({parse(file = f, keep.source = FALSE); NA_character_}, error = function(err) conditionMessage(err))
  if (!is.na(e)) out <- c(out, paste0(f, "\\t", gsub("\\n", " ", e))) }
writeLines(out)
'''
res = subprocess.run([rscript, '-e', r_code, listing], capture_output=True, text=True)
if res.returncode != 0:
    subprocess.run(['rm', '-rf', tmp])
    die('Rscript exited %d while parsing the chunks' % res.returncode, res.stderr)
fails = {}
for line in res.stdout.split('\n'):
    if '\t' in line:
        p, msg = line.split('\t', 1); fails[p] = msg[:160]
worse, regressed_n = 0, 0
for f in files:
    at = {(v, i): p for (ff, v, i, p) in index if ff == f}
    idx = {v: {i for (vv, i) in at if vv == v and at[(vv, i)] in fails}
           for v in ('before', 'after', 'english')}
    regressed = sorted(idx['after'] - idx['before'] - idx['english'])
    regressed_n += len(regressed)
    if regressed:
        worse += 1
    if idx['after'] or idx['before']:
        flag = 'WORSE' if regressed else ('better' if len(idx['after']) < len(idx['before']) else 'same')
        print('%-45s before %d after %d  %s' % (f, len(idx['before']), len(idx['after']), flag))
        for i in regressed:
            q = at[('after', i)]
            first = open(q, encoding='utf-8').read().strip().split('\n')[0][:80]
            print('     after-fail: chunk %d | %s | %s' % (i, fails[q], first))
        known = sorted(idx['after'] - set(regressed))
        if known:
            print('     after-fail-known: chunk %s also fails before, or in the English chapter'
                  % ', '.join(str(i) for i in known))
print('files %d, chunks parsed %d, chunks that fail after and did not fail before: %d, files worse: %d'
      % (len(files), len(index), regressed_n, worse))
subprocess.run(['rm', '-rf', tmp])
sys.exit(1 if worse else 0)
