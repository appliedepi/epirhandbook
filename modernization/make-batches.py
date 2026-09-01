#!/usr/bin/env python3
"""Turn extracted.jsonl into fix batches: one language, one kind, at most N findings.

Reads the extractor's output and writes, in --out-dir:

    batches/<lang>.<kind>.<nn>.md   the evidence one fix agent reads
    index.tsv                       one row per batch: id, lang, kind, n, files, ids
    waves.tsv                       a schedule: wave, batch id. Batches in one wave
                                    share no translated file, so they can run at once.

Deterministic: the same extracted.jsonl gives the same batches and the same waves.
No model, no network.

Usage:
    python3 modernization/make-batches.py [--src /tmp/fixpass/extracted.jsonl]
        [--out-dir /tmp/fixpass] [--max 20] [--wave 12]
"""
import argparse
import collections
import json
import math
import os
import re
import sys

KINDS = ['untrue', 'missing', 'code_mismatch', 'added', 'alignment_mismatch']


def id_key(fid):
    m = re.match(r'^(.*)#(\d+)$', fid)
    return (m.group(1), int(m.group(2)))


def chunk(items, cap):
    """Split into ceil(n/cap) chunks of nearly equal size, preserving order."""
    k = math.ceil(len(items) / cap)
    size = math.ceil(len(items) / k)
    return [items[i:i + size] for i in range(0, len(items), size)]


def gutter(side, start, end):
    out = []
    n = side['context_start']
    for line in side['before']:
        out.append('%6d  | %s' % (n, line)); n += 1
    for line in side['text']:
        out.append('%6d >| %s' % (n, line)); n += 1
    for line in side['after']:
        out.append('%6d  | %s' % (n, line)); n += 1
    assert n - 1 == side['context_end']
    return '\n'.join(out)


def render(rec):
    en, tr = rec['en'], rec['tr']
    return '\n'.join([
        '## FINDING %s' % rec['id'],
        '',
        '- kind: %s' % rec['kind'],
        '- finder confidence: %s' % rec['confidence'],
        '- heading: %s' % rec['heading'],
        '- translated file to edit: %s' % tr['path'],
        '- finder proposition: %s' % rec['proposition'],
        '- finder reader_consequence: %s' % rec['reader_consequence'],
        '',
        'ENGLISH REFERENCE %s lines %d-%d, marked >, with context. Read-only.' % (en['path'], en['start'], en['end']),
        '~~~~~~~~~~',
        gutter(en, en['start'], en['end']),
        '~~~~~~~~~~',
        '',
        'TRANSLATION %s lines %d-%d, marked >, with context. Line numbers are at commit %s and may have shifted.' % (tr['path'], tr['start'], tr['end'], rec['ref']),
        '~~~~~~~~~~',
        gutter(tr, tr['start'], tr['end']),
        '~~~~~~~~~~',
        '',
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='/tmp/fixpass/extracted.jsonl')
    ap.add_argument('--out-dir', default='/tmp/fixpass')
    ap.add_argument('--max', type=int, default=20)
    ap.add_argument('--wave', type=int, default=12)
    args = ap.parse_args()

    recs = [json.loads(l) for l in open(args.src, encoding='utf-8')]
    groups = collections.defaultdict(list)
    for r in recs:
        groups[(r['lang'], r['kind'])].append(r)

    bdir = os.path.join(args.out_dir, 'batches')
    os.makedirs(bdir, exist_ok=True)
    for old in os.listdir(bdir):
        os.remove(os.path.join(bdir, old))

    batches = []
    for lang in sorted({k[0] for k in groups}):
        for kind in KINDS:
            items = groups.get((lang, kind))
            if not items:
                continue
            items.sort(key=lambda r: id_key(r['id']))
            for i, part in enumerate(chunk(items, args.max), start=1):
                bid = '%s.%s.%02d' % (lang, kind, i)
                files = sorted({r['tr']['path'] for r in part})
                body = [
                    '# BATCH %s: language %s, kind %s, %d findings' % (bid, lang, kind, len(part)),
                    '',
                    'Files this batch may edit: %s' % ', '.join(files),
                    '',
                ] + [render(r) for r in part]
                with open(os.path.join(bdir, bid + '.md'), 'w', encoding='utf-8') as fh:
                    fh.write('\n'.join(body))
                batches.append({'id': bid, 'lang': lang, 'kind': kind, 'n': len(part),
                                'files': files, 'ids': [r['id'] for r in part]})

    with open(os.path.join(args.out_dir, 'index.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('batch\tlang\tkind\tn\tfiles\tids\n')
        for b in batches:
            fh.write('\t'.join([b['id'], b['lang'], b['kind'], str(b['n']),
                                ','.join(b['files']), ','.join(b['ids'])]) + '\n')

    # Waves: greedy, largest batches first, no shared file inside one wave.
    pending = sorted(batches, key=lambda b: (-b['n'], b['id']))
    waves = []
    while pending:
        used, wave, rest = set(), [], []
        for b in pending:
            if len(wave) < args.wave and not (used & set(b['files'])):
                wave.append(b); used |= set(b['files'])
            else:
                rest.append(b)
        waves.append(wave); pending = rest
    with open(os.path.join(args.out_dir, 'waves.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('wave\tbatch\tn\n')
        for w, wave in enumerate(waves, start=1):
            for b in wave:
                fh.write('%d\t%s\t%d\n' % (w, b['id'], b['n']))

    print('findings   %d' % len(recs))
    print('batches    %d, max %d per batch' % (len(batches), args.max))
    print('waves      %d, max %d per wave: %s' % (len(waves), args.wave,
          ' '.join(str(len(w)) for w in waves)))
    assert sum(b['n'] for b in batches) == len(recs)
    assert sum(len(w) for w in waves) == len(batches)
    return 0


if __name__ == '__main__':
    sys.exit(main())
