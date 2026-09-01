#!/usr/bin/env python3
"""Extract the evidence for every prose-sweep finding, mechanically.

For each finding in modernization/findings/prose-sweep/*.json, read the English
span and the translated span from the files AS THEY WERE at the sweep commit,
with CONTEXT lines of context on each side. No model, no network. Deterministic.

Files are read with `git show <ref>:<path>`, never from the working tree, so a
fix that shifts line numbers in a chapter cannot corrupt the evidence for the
findings that follow it. The default ref is the commit the sweep was read at.

Outputs, in --out-dir:

    extracted.jsonl     one JSON object per finding whose BOTH spans parse,
                        name the expected file, and lie inside that file
    unextractable.tsv   one row per finding that fails any of those tests,
                        with the side and the reason. Never dropped, never guessed.

Every finding lands in exactly one of the two files. The script exits 1 if
that accounting does not hold.

A finding's id is "<chapter>.<lang>#<n>", where n is its 1-based position in
the findings array of its JSON file. That is stable and reconstructible.

Usage:
    python3 modernization/extract-spans.py [--ref 52442a79] [--context 8]
        [--src modernization/findings/prose-sweep] [--out-dir /tmp/fixpass]
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

SPAN = re.compile(r'^chapters/([A-Za-z0-9_]+)((?:\.[a-z]{2})?)\.qmd:(\d+)-(\d+)$')


class FileCache:
    """Lines of each chapter file at one git ref. None if the ref lacks the file."""

    def __init__(self, repo, ref):
        self.repo, self.ref, self.cache = repo, ref, {}

    def lines(self, path):
        if path not in self.cache:
            p = subprocess.run(['git', '-C', self.repo, 'show', '%s:%s' % (self.ref, path)],
                               capture_output=True)
            if p.returncode != 0:
                self.cache[path] = None
            else:
                self.cache[path] = p.stdout.decode('utf-8').split('\n')
                # A file that ends in a newline splits to a trailing empty
                # element that is not a line. Drop it.
                if self.cache[path] and self.cache[path][-1] == '':
                    self.cache[path].pop()
        return self.cache[path]


def parse_span(span, expected_path):
    """Return (path, start, end) or raise ValueError with the reason."""
    if not isinstance(span, str):
        raise ValueError('span is not a string: %r' % (span,))
    m = SPAN.match(span)
    if not m:
        raise ValueError('span does not match file:START-END: %r' % span)
    path = 'chapters/%s%s.qmd' % (m.group(1), m.group(2))
    if path != expected_path:
        raise ValueError('span names %s, expected %s' % (path, expected_path))
    start, end = int(m.group(3)), int(m.group(4))
    if start > end:
        raise ValueError('span start %d is after end %d' % (start, end))
    return path, start, end


def extract(files, path, start, end, context):
    lines = files.lines(path)
    if lines is None:
        raise ValueError('file %s does not exist at the ref' % path)
    n = len(lines)
    if start < 1 or end > n:
        raise ValueError('span %d-%d is outside %s, which has %d lines' % (start, end, path, n))
    c0, c1 = max(1, start - context), min(n, end + context)
    return {
        'path': path, 'start': start, 'end': end, 'nlines': n,
        'context_start': c0, 'context_end': c1,
        'before': lines[c0 - 1:start - 1],
        'text': lines[start - 1:end],
        'after': lines[end:c1],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--ref', default='52442a79')
    ap.add_argument('--context', type=int, default=8)
    ap.add_argument('--src', default='modernization/findings/prose-sweep')
    ap.add_argument('--out-dir', default='/tmp/fixpass')
    args = ap.parse_args()

    files = FileCache(args.repo, args.ref)
    os.makedirs(args.out_dir, exist_ok=True)
    extracted, unextractable, total = [], [], 0

    for jpath in sorted(glob.glob(os.path.join(args.src, '*.json'))):
        with open(jpath, encoding='utf-8') as fh:
            d = json.load(fh)
        chapter, lang = d['chapter'], d['lang']
        en_path = 'chapters/%s.qmd' % chapter
        tr_path = 'chapters/%s.%s.qmd' % (chapter, lang)
        for i, f in enumerate(d['findings'], start=1):
            total += 1
            fid = '%s.%s#%d' % (chapter, lang, i)
            base = {
                'id': fid, 'chapter': chapter, 'lang': lang, 'kind': f.get('kind'),
                'confidence': f.get('confidence'), 'heading': f.get('heading'),
                'segment_index': f.get('segment_index'),
                'proposition': f.get('proposition'),
                'reader_consequence': f.get('reader_consequence'),
                'en_span': f.get('en_span'), 'tr_span': f.get('tr_span'),
            }
            problems = []
            sides = {}
            for side, span, path in (('en', f.get('en_span'), en_path),
                                     ('tr', f.get('tr_span'), tr_path)):
                try:
                    p, a, b = parse_span(span, path)
                    sides[side] = extract(files, p, a, b, args.context)
                except ValueError as e:
                    problems.append((side, str(e)))
            if problems:
                for side, reason in problems:
                    unextractable.append([fid, chapter, lang, base['kind'] or '', side,
                                          str(base['%s_span' % side]), reason])
            else:
                base['ref'] = args.ref
                base['en'] = sides['en']
                base['tr'] = sides['tr']
                extracted.append(base)

    with open(os.path.join(args.out_dir, 'extracted.jsonl'), 'w', encoding='utf-8') as fh:
        for rec in extracted:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    with open(os.path.join(args.out_dir, 'unextractable.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(['id', 'chapter', 'lang', 'kind', 'side', 'span', 'reason']) + '\n')
        for row in unextractable:
            fh.write('\t'.join(row) + '\n')

    bad_ids = {r[0] for r in unextractable}
    print('findings read        %d' % total)
    print('extracted            %d' % len(extracted))
    print('unextractable        %d findings, %d sides' % (len(bad_ids), len(unextractable)))
    print('ref                  %s, context %d' % (args.ref, args.context))
    if len(extracted) + len(bad_ids) != total:
        print('ACCOUNTING FAILURE: %d + %d != %d' % (len(extracted), len(bad_ids), total))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
