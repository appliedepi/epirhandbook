#!/usr/bin/env python3
"""Reconcile one or more fix batches against the files on disk.

The result file is the artifact; an agent's return value is only a report
about it. This script reads modernization/findings/fix-pass/<batch>.json for
each batch named on the command line and checks, against the working tree:

  1. the result file exists and parses
  2. its ids are exactly the batch's ids from batch-index.tsv, in any order
  3. every verdict is fixed, rejected or deferred
  4. every "fixed" entry names a file the batch was allowed to edit, its
     "new" text is present in that file now, and its "old" text is absent
     (unless "old" is a substring of "new")
  5. every rejected or deferred entry carries a reason
  6. `git diff --name-only` touches nothing outside the union of the named
     batches' allowed files plus modernization/findings/fix-pass/

Prints one line per batch with the counts, then FAIL lines. Exits 1 on any
failure, 0 otherwise.

Usage:
    python3 modernization/reconcile-fix-pass.py tr.untrue.01 tr.added.01 ...
"""
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, 'modernization', 'findings', 'fix-pass')
VERDICTS = {'fixed', 'rejected', 'deferred'}


def main(batch_ids):
    index = {}
    with open(os.path.join(FIX, 'batch-index.tsv'), encoding='utf-8') as fh:
        for row in csv.DictReader(fh, delimiter='\t', quoting=csv.QUOTE_NONE):
            index[row['batch']] = row
    fails, allowed_all, totals = [], set(), {'fixed': 0, 'rejected': 0, 'deferred': 0}
    file_cache = {}

    def content(path):
        if path not in file_cache:
            p = os.path.join(ROOT, path)
            file_cache[path] = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        return file_cache[path]

    for bid in batch_ids:
        if bid not in index:
            fails.append('%s: not in batch-index.tsv' % bid); continue
        allowed = set(index[bid]['files'].split(','))
        allowed_all |= allowed
        want = index[bid]['ids'].split(',')
        path = os.path.join(FIX, bid + '.json')
        if not os.path.exists(path):
            fails.append('%s: NO RESULT FILE at %s' % (bid, path)); continue
        try:
            d = json.load(open(path, encoding='utf-8'))
        except Exception as e:
            fails.append('%s: result file does not parse: %s' % (bid, e)); continue
        results = d.get('results', [])
        got = [r.get('id') for r in results]
        if sorted(got) != sorted(want):
            fails.append('%s: ids differ. missing %s, extra %s' % (
                bid, sorted(set(want) - set(got)), sorted(set(got) - set(want))))
        counts = {'fixed': 0, 'rejected': 0, 'deferred': 0}
        for r in results:
            v = r.get('verdict')
            if v not in VERDICTS:
                fails.append('%s %s: bad verdict %r' % (bid, r.get('id'), v)); continue
            counts[v] += 1
            if v == 'fixed':
                f, old, new = r.get('file'), r.get('old'), r.get('new')
                if f not in allowed:
                    fails.append('%s %s: fixed file %r not in allowed set' % (bid, r.get('id'), f)); continue
                text = content(f)
                if text is None:
                    fails.append('%s %s: file %s missing' % (bid, r.get('id'), f)); continue
                if not isinstance(new, str) or not new:
                    fails.append('%s %s: fixed with empty new text' % (bid, r.get('id')))
                elif new not in text:
                    fails.append('%s %s: new text NOT in %s' % (bid, r.get('id'), f))
                if isinstance(old, str) and old and old in text and not (isinstance(new, str) and old in new):
                    fails.append('%s %s: old text STILL in %s' % (bid, r.get('id'), f))
            else:
                if not r.get('reason'):
                    fails.append('%s %s: %s without a reason' % (bid, r.get('id'), v))
        for k in counts:
            totals[k] += counts[k]
        print('%-28s n=%-3d fixed=%-3d rejected=%-3d deferred=%-3d' % (
            bid, len(results), counts['fixed'], counts['rejected'], counts['deferred']))

    diff = subprocess.run(['git', '-C', ROOT, 'diff', '--name-only'], capture_output=True, text=True)
    changed = [l for l in diff.stdout.split('\n') if l]
    stray = [c for c in changed if c not in allowed_all and not c.startswith('modernization/findings/fix-pass/')]
    if stray:
        fails.append('working tree changes outside allowed files: %s' % stray)
    print('TOTAL fixed=%d rejected=%d deferred=%d ; changed files %d' % (
        totals['fixed'], totals['rejected'], totals['deferred'], len(changed)))
    for f in fails:
        print('FAIL', f)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
