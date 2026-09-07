#!/usr/bin/env python3
"""Rebuild both prose-sweep TSVs from the JSON files, which are the record.

Read modernization/findings/prose-sweep/*.json and write the two derived tables.
Never append. The JSON files are the only input.

Usage:
    python3 modernization/rebuild-tsv.py [--only-pairs FILE] [--out-dir DIR]

--only-pairs restricts the rebuild to the pair names listed in FILE, one
"<chapter>.<lang>" per line. Use it to reproduce an earlier record and compare.
"""
import argparse
import glob
import json
import os
import sys

DRIFT_COLS = ['chapter', 'lang', 'heading', 'segment_index', 'kind', 'en_span',
              'tr_span', 'proposition', 'reader_consequence', 'confidence']
COVERAGE_COLS = ['chapter', 'lang', 'en_segment_id', 'tr_segment_id', 'relation',
                 'confidence', 'reviewed']


def cell(value):
    """Render one JSON value as one TSV field.

    A JSON null becomes the literal NA, which R reads as a missing value.
    A JSON boolean becomes TRUE or FALSE, which R reads as a logical.
    """
    if value is None:
        return 'NA'
    if value is True:
        return 'TRUE'
    if value is False:
        return 'FALSE'
    return str(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='modernization/findings/prose-sweep')
    ap.add_argument('--out-dir', default='modernization/findings')
    ap.add_argument('--only-pairs', default=None)
    args = ap.parse_args()

    keep = None
    if args.only_pairs:
        with open(args.only_pairs, encoding='utf-8') as fh:
            keep = {line.strip() for line in fh if line.strip()}

    drift, coverage, dirty = [], [], []
    files = sorted(glob.glob(os.path.join(args.src, '*.json')))
    used = 0
    for path in files:
        pair = os.path.basename(path)[:-len('.json')]
        if keep is not None and pair not in keep:
            continue
        used += 1
        with open(path, encoding='utf-8') as fh:
            d = json.load(fh)
        chapter, lang = d['chapter'], d['lang']
        for f in d['findings']:
            row = [chapter, lang] + [cell(f.get(c)) for c in DRIFT_COLS[2:]]
            drift.append(row)
        for c in d['coverage']:
            row = [chapter, lang] + [cell(c.get(k)) for k in COVERAGE_COLS[2:]]
            coverage.append(row)

    # No field may hold a tab, a newline or a carriage return. One that did
    # would split a row silently, and the reader would never see the break.
    for name, rows in (('drift', drift), ('coverage', coverage)):
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                if '\t' in v or '\n' in v or '\r' in v:
                    dirty.append('%s row %d field %d' % (name, i, j))

    def write(path, cols, rows):
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write('\t'.join(cols) + '\n')
            for row in rows:
                fh.write('\t'.join(row) + '\n')

    write(os.path.join(args.out_dir, 'language-prose-drift.tsv'), DRIFT_COLS, drift)
    write(os.path.join(args.out_dir, 'language-prose-coverage.tsv'), COVERAGE_COLS, coverage)

    print('pairs read       %d of %d files' % (used, len(files)))
    print('drift rows       %d' % len(drift))
    print('coverage rows    %d' % len(coverage))
    print('whitespace fields needing cleaning: %d' % len(dirty))
    for x in dirty[:10]:
        print('   ', x)
    return 1 if dirty else 0


if __name__ == '__main__':
    sys.exit(main())
