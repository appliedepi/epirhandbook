#!/usr/bin/env python3
"""Parse every R code chunk of every changed translated chapter with R, before and after.

For each chapters/<chapter>.<lang>.qmd changed between BASE and HEAD, extract the ```{r ...}
chunks from both versions, run Rscript parse() on each, and report the count of chunks that
fail to parse. The gate FAILS if any file has MORE parse failures after than before. It prints
every failing chunk after, so a pre-existing failure is visible too.

Usage: python3 modernization/chunk-parse-gate.py <base> [head]
"""
import re, subprocess, sys, tempfile, os
base = sys.argv[1]; head = sys.argv[2] if len(sys.argv) > 2 else 'HEAD'
files = [f for f in subprocess.run(['git','diff','--name-only',base,head,'--','chapters/'],capture_output=True,text=True).stdout.split() if re.search(r'\.[a-z]{2}\.qmd$', f)]
FENCE_OPEN = re.compile(r'^\s*(`{3,})\s*\{r[ ,}]')

def chunks(text):
    out, cur, fence = [], None, None
    for line in text.split('\n'):
        if cur is None:
            m = FENCE_OPEN.match(line)
            if m: fence = m.group(1); cur = []
        else:
            if re.match(r'^\s*' + fence + r'\s*$', line): out.append('\n'.join(cur)); cur = None
            else: cur.append(line)
    return out

def parse_fail(code):
    with tempfile.NamedTemporaryFile('w', suffix='.R', delete=False, encoding='utf-8') as fh:
        fh.write(code); p = fh.name
    r = subprocess.run(['Rscript', '-e', 'invisible(parse(file = commandArgs(TRUE)[1], keep.source = FALSE))', p], capture_output=True, text=True)
    os.unlink(p)
    return None if r.returncode == 0 else r.stderr.strip().split('\n')[0][:160]

worse = 0
for f in files:
    old = subprocess.run(['git','show','%s:%s' % (base, f)],capture_output=True,text=True).stdout
    new = open(f, encoding='utf-8').read()
    fo = [c for c in chunks(old) if parse_fail(c)]
    fn = [(c, parse_fail(c)) for c in chunks(new)]; fn = [(c, e) for c, e in fn if e]
    flag = 'WORSE' if len(fn) > len(fo) else ('better' if len(fn) < len(fo) else 'same')
    if len(fn) > len(fo): worse += 1
    if fn or fo: print('%-45s before %d after %d  %s' % (f, len(fo), len(fn), flag))
    for c, e in fn: print('     after-fail: %s | %s' % (e, c.strip().split('\n')[0][:80]))
print('files %d, files with more parse failures after than before: %d' % (len(files), worse))
sys.exit(1 if worse else 0)
