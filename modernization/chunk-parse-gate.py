#!/usr/bin/env python3
"""Parse every R code chunk of every changed translated chapter with R, before and after.

For each chapters/<chapter>.<lang>.qmd changed between BASE and HEAD, extract the ```{r ...}
chunks from both versions, parse every chunk in ONE R process, and report per file the count
of chunks that fail to parse. The gate FAILS if any file has MORE parse failures after than
before. It prints every failing chunk after, so a pre-existing failure is visible too.

Proved red: an extra closing parenthesis is reported by parse().

Usage: python3 modernization/chunk-parse-gate.py <base> [head]
"""
import json, os, re, subprocess, sys, tempfile

base = sys.argv[1]; head = sys.argv[2] if len(sys.argv) > 2 else 'HEAD'
files = [f for f in subprocess.run(['git', 'diff', '--name-only', base, head, '--', 'chapters/'], capture_output=True, text=True).stdout.split() if re.search(r'\.[a-z]{2}\.qmd$', f)]
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
    old = subprocess.run(['git', 'show', '%s:%s' % (base, f)], capture_output=True, text=True).stdout
    new = open(f, encoding='utf-8').read()
    for version, text in (('before', old), ('after', new)):
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
res = subprocess.run(['Rscript', '-e', r_code, listing], capture_output=True, text=True)
fails = {}
for line in res.stdout.split('\n'):
    if '\t' in line:
        p, msg = line.split('\t', 1); fails[p] = msg[:160]
worse = 0
for f in files:
    fo = [p for (ff, v, i, p) in index if ff == f and v == 'before' and p in fails]
    fn = [p for (ff, v, i, p) in index if ff == f and v == 'after' and p in fails]
    if fn or fo:
        flag = 'WORSE' if len(fn) > len(fo) else ('better' if len(fn) < len(fo) else 'same')
        if len(fn) > len(fo): worse += 1
        print('%-45s before %d after %d  %s' % (f, len(fo), len(fn), flag))
        for p in fn: print('     after-fail: %s | %s' % (fails[p], open(p, encoding='utf-8').read().strip().split('\n')[0][:80]))
print('files %d, chunks parsed %d, files with more parse failures after than before: %d' % (len(files), len(index), worse))
subprocess.run(['rm', '-rf', tmp])
sys.exit(1 if worse else 0)
