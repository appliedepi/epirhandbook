#!/usr/bin/env python3
"""Sum the tokens each fix agent used, from a workflow's transcript directory.

Tokens per agent = sum over its assistant messages of input + cache creation +
cache read + output. The batch id is read from the agent's own prompt.
Usage: python3 modernization/agent-cost.py <workflow transcript dir> [more dirs]
Prints: batch  n_findings  evidence_KB  tokens, then a least-squares line tokens ~ a + b*KB.
"""
import csv, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
idx = {r['batch']: r for r in csv.DictReader(open(os.path.join(ROOT, 'modernization/findings/fix-pass/batch-index.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
rows = []
for d in sys.argv[1:]:
    for p in sorted(glob.glob(os.path.join(d, 'agent-*.jsonl'))):
        bid, tok, turns = None, 0, 0
        for l in open(p, encoding='utf-8'):
            try: o = json.loads(l)
            except Exception: continue
            if bid is None:
                m = re.search(r'Batch: ([a-z]{2}\.[a-z_]+\.\d\d)', l)
                if m: bid = m.group(1)
            u = (o.get('message') or {}).get('usage')
            if u:
                turns += 1
                tok += u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('cache_read_input_tokens', 0) + u.get('output_tokens', 0)
        kb = os.path.getsize('/tmp/fixpass/batches/%s.md' % bid) / 1024 if bid and os.path.exists('/tmp/fixpass/batches/%s.md' % bid) else float('nan')
        n = int(idx[bid]['n']) if bid in idx else -1
        rows.append((bid, n, kb, tok, turns))
        print('%-24s n=%-3d evidence=%6.1f KB  turns=%-3d tokens=%d' % (bid, n, kb, turns, tok))
tot = sum(r[3] for r in rows)
print('agents %d  total tokens %d  mean %d' % (len(rows), tot, tot / max(1, len(rows))))
xs = [r[2] for r in rows]; ys = [r[3] for r in rows]
if len(rows) >= 2 and max(xs) > min(xs):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    ss = sum((y - my) ** 2 for y in ys); sr = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    print('fit: tokens ~= %.0f + %.0f * evidence_KB   (R2 %.3f, %d points, KB range %.1f-%.1f)' % (a, b, 1 - sr / ss if ss else float('nan'), len(rows), min(xs), max(xs)))
