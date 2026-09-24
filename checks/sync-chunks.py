#!/usr/bin/env python3
"""Make every R code chunk of every translated chapter identical in code to the English chunk,
keeping the translated comments where the code line is the same.

For each content/<lang>/<stem>.qmd whose chunk count equals the English chapter's, walk the
chunks in order. For each chunk, the output is the English chunk, line by line, except that a
line whose code part (the text before any # comment, right-stripped) equals the code part of a
line in the translated chunk keeps the translated line, so the translator's comment survives.
The fence line with the chunk options is taken from the English. A translated file whose
chunk count differs from the English is skipped and listed: it needs a hand alignment.

The landing page, content/<lang>/index.qmd, is outside the file set. Each language writes its
own landing page, so its chunks are not a copy of the English chunks.

Deterministic. No model, no network. Prints one line per changed file and a summary.
`checks/langs.py` reads `languages.yml` with PyYAML.

Usage:
    python3 checks/sync-chunks.py [--langs fr,es,vn,jp,pt,tr,ru] [--dry-run] [--only FILE ...]
"""
import argparse
import glob
import os
import re
import sys

from langs import read_languages

FENCE = re.compile(r'^(\s*)(`{3,})\s*\{r[ ,}]')
LANDING = 'index.qmd'


def languages():
    """The main language code and the translation codes, from `languages.yml`."""
    main, codes = read_languages('languages.yml')
    return main, [c for c in codes if c != main]


def chapters(lang):
    """The chapter files of one language folder, the landing page left out."""
    return [f for f in glob.glob('content/%s/*.qmd' % lang) if os.path.basename(f) != LANDING]


def split(text):
    """Return a list of segments: ('prose', lines) or ('chunk', fence_line, body_lines, close_line)."""
    segs, cur, fence, i = [], [], None, 0
    lines = text.split('\n')
    prose = []
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m:
            if prose: segs.append(('prose', prose)); prose = []
            fence = m.group(2); body = []; j = i + 1
            while j < len(lines) and not re.match(r'^\s*' + fence + r'\s*$', lines[j]):
                body.append(lines[j]); j += 1
            if j >= len(lines):
                raise ValueError('unclosed chunk at line %d' % (i + 1))
            segs.append(('chunk', lines[i], body, lines[j])); i = j + 1
        else:
            prose.append(lines[i]); i += 1
    if prose: segs.append(('prose', prose))
    return segs


def code_part(line):
    """The code before a # comment, ignoring # inside a string, right-stripped."""
    out, q = [], None
    for ch in line:
        if q:
            out.append(ch)
            if ch == q: q = None
        elif ch in '"\'':
            q = ch; out.append(ch)
        elif ch == '#':
            break
        else:
            out.append(ch)
    return ''.join(out).rstrip()


def merge(en_body, tr_body):
    """English code, translated comments where the line aligns. Returns (lines, kept, fallback).

    Lines are aligned with difflib on their code parts. In an aligned pair, a line with the
    same code keeps the translated line (its comment survives), and a comment-only line
    keeps the translated comment-only line. Every other line is the English line.

    A FULLY COMMENTED LINE NEVER SYNCS FROM ENGLISH, INCLUDING COMMENTED-OUT CODE.
    Its code part is the empty string on both sides, so the two always compare equal and the
    translated line always wins. That rule exists to protect a translator's prose comment, and
    it cannot tell prose from code that happens to be commented out. The caller is told the
    chunk changed, so a file can report as synced while such a line stays stale.

    This is deliberate, not a bug to fix here. Deciding it needs R: only a parse of the comment
    body separates `# nodos (circulos)`, which is a correct translation, from
    `# dir(path = here("data"), pattern = ".csv")`, which must follow English. See issue #458
    for the count (about 12 lines handbook-wide) and why the machinery was judged not worth it.
    Edit such a line by hand in every language.

    Deletion is not affected: output is built from en_body, so a line removed from English
    disappears from every translation.
    """
    import difflib
    ce = [code_part(l) for l in en_body]; ct = [code_part(l) for l in tr_body]
    def is_comment_only(l): return l.strip().startswith('#')
    pair = {}
    for blk in difflib.SequenceMatcher(None, ce, ct, autojunk=False).get_matching_blocks():
        for k in range(blk.size): pair[blk.a + k] = blk.b + k
    out, kept, fallback = [], 0, 0
    for i, l in enumerate(en_body):
        j = pair.get(i)
        if j is not None:
            t = tr_body[j]
            if ce[i].strip() and '#' in t and t != l: out.append(t); kept += 1; continue
            if not ce[i].strip() and is_comment_only(l) and is_comment_only(t) and t != l: out.append(t); kept += 1; continue
        out.append(l)
        if '#' in l and (i not in pair or tr_body[pair[i]] != l): fallback += 1
    return out, kept, fallback


def main():
    main_lang, translations = languages()
    ap = argparse.ArgumentParser()
    ap.add_argument('--langs', default=','.join(translations))
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only', nargs='*', default=None)
    ap.add_argument('--from-ref', default=None, help='read the translated files from this git ref instead of the working tree')
    args = ap.parse_args()
    langs = [l for l in args.langs.split(',') if l]
    if args.only:
        files = args.only
        # The run compares with, and writes to, the working-tree file. Under --from-ref it
        # also reads the translation from the ref, so the file must exist in both.
        gone = [f for f in files if not os.path.isfile(f)]
        if args.from_ref:
            import subprocess
            gone += [f for f in files if subprocess.run(
                ['git', 'cat-file', '-e', '%s:%s' % (args.from_ref, f)],
                capture_output=True).returncode != 0 and f not in gone]
        if gone:
            sys.exit('sync-chunks.py: --only names %d file(s) that do not exist in the working '
                     'tree%s, first: %s'
                     % (len(gone), ' or in %s' % args.from_ref if args.from_ref else '', gone[0]))
    else:
        # The file set comes from a glob, so a folder with no chapter file drops out of it in
        # silence. The run would then report a clean tree for a language it never read.
        for l in [main_lang] + langs:
            if not chapters(l):
                sys.exit('sync-chunks.py: content/%s/ is missing or holds no chapter file, so '
                         'this run would compare nothing for that language.' % l)
        files = sorted(f for l in langs for f in chapters(l))
        if not files:
            sys.exit('sync-chunks.py: no translation is selected, so this run would compare '
                     'nothing. Check languages.yml and --langs.')
    changed, chunks_changed, kept_total, fallback_total, skipped = 0, 0, 0, 0, []
    for tr in files:
        en = 'content/%s/%s' % (main_lang, os.path.basename(tr))
        if not os.path.exists(en):
            skipped.append((tr, 'no English chapter')); continue
        te = open(en, encoding='utf-8').read()
        if args.from_ref:
            import subprocess
            tt = subprocess.run(['git', 'show', '%s:%s' % (args.from_ref, tr)], capture_output=True, text=True).stdout
        else:
            tt = open(tr, encoding='utf-8').read()
        try:
            se, st = split(te), split(tt)
        except ValueError as e:
            skipped.append((tr, str(e))); continue
        ce = [s for s in se if s[0] == 'chunk']; ct = [s for s in st if s[0] == 'chunk']
        if len(ce) != len(ct):
            skipped.append((tr, 'chunk count %d vs English %d' % (len(ct), len(ce)))); continue
        out, k, n_changed, kept, fallback = [], 0, 0, 0, 0
        for s in st:
            if s[0] == 'prose':
                out.extend(s[1]); continue
            e = ce[k]; k += 1
            body, kk, fb = merge(e[2], s[2])
            new = [e[1]] + body + [e[3]]
            old = [s[1]] + s[2] + [s[3]]
            if new != old: n_changed += 1; kept += kk; fallback += fb
            out.extend(new)
        new_text = '\n'.join(out)
        current = open(tr, encoding='utf-8').read()
        if new_text != current:
            changed += 1; chunks_changed += n_changed; kept_total += kept; fallback_total += fallback
            print('%-40s chunks changed %3d, translated comments kept %3d, English comments used %3d' % (tr, n_changed, kept, fallback))
            if not args.dry_run:
                open(tr, 'w', encoding='utf-8', newline='').write(new_text)
    print('files %d, changed %d, chunks changed %d, translated comments kept %d, English comments used %d%s' % (
        len(files), changed, chunks_changed, kept_total, fallback_total, ' (dry run)' if args.dry_run else ''))
    for f, why in skipped: print('SKIPPED %s: %s' % (f, why))
    return 0


if __name__ == '__main__':
    sys.exit(main())
