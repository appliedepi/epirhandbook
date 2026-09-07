#!/usr/bin/env python3
"""Emit the Workflow args for one wave: the wave's batches that have no result file yet.

Reads /tmp/fixpass/waves.tsv and modernization/findings/fix-pass/batch-index.tsv.
Skips any batch whose fix-pass/<batch>.json already exists, so a wave can be re-run
after a kill without repeating finished batches. Prints the JSON to stdout.

Usage: python3 modernization/wave-args.py <wave-number> [--max N]
"""
import csv, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, 'modernization', 'findings', 'fix-pass')
wave = sys.argv[1]
cap = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 99
idx = {r['batch']: r for r in csv.DictReader(open(os.path.join(FIX, 'batch-index.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
ids = [r['batch'] for r in csv.DictReader(open('/tmp/fixpass/waves.tsv', encoding='utf-8'), delimiter='\t') if r['wave'] == wave]
out, skipped = [], []
for i in ids:
    if os.path.exists(os.path.join(FIX, i + '.json')):
        skipped.append(i); continue
    r = idx[i]
    out.append({'id': i, 'lang': r['lang'], 'kind': r['kind'], 'n': int(r['n']), 'files': r['files'].split(',')})
out = out[:cap]
sys.stderr.write('wave %s: %d batches, %d findings; skipped done: %s\n' % (wave, len(out), sum(b['n'] for b in out), skipped))
print(json.dumps({'wave': 'w' + wave, 'batches': out}))
