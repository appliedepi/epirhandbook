#!/usr/bin/env bash
# Build a read-only codex workspace for one language's fix-pass diff.
# Usage: modernization/codex-bundle.sh <lang> <base-commit> [part-of-N e.g. 1/2]
# Writes /tmp/codex-ws/<lang>[-partN]/ with: CHANGES.diff, FINDINGS.md, the touched
# translated chapters and their English sources (current tree), and PROMPT.txt.
set -euo pipefail
cd "$(dirname "$0")/.."
lang="$1"; base="$2"; part="${3:-1/1}"
pn="${part%/*}"; pt="${part#*/}"
ws=/tmp/codex-ws/$lang; [ "$pt" != 1 ] && ws=$ws-part$pn
rm -rf "$ws"; mkdir -p "$ws/chapters"
mapfile -t files < <(git diff --name-only "$base" HEAD -- "chapters/*.$lang.qmd" | sort)
# split the file list into parts by position
sel=(); i=0; for f in "${files[@]}"; do if [ $(( i % pt )) -eq $(( pn - 1 )) ]; then sel+=("$f"); fi; i=$((i+1)); done
git diff "$base" HEAD -- "${sel[@]}" > "$ws/CHANGES.diff"
for f in "${sel[@]}"; do cp "$f" "$ws/chapters/"; en="${f%.$lang.qmd}.qmd"; cp "$en" "$ws/chapters/"; done
python3 - "$lang" "$ws" "${sel[@]}" <<'PY'
import glob, json, sys
lang, ws, sel = sys.argv[1], sys.argv[2], set(sys.argv[3:])
out = ['# Fix-pass verdicts for language %s, files in this part only' % lang, '']
for p in sorted(glob.glob('modernization/findings/fix-pass/%s.*.json' % lang)):
    d = json.load(open(p, encoding='utf-8'))
    for r in d['results']:
        if r['verdict'] == 'fixed' and r.get('file') in sel:
            out += ['## %s  (%s, %s)' % (r['id'], d['kind'], r['file']), 'reason: %s' % r.get('reason'), 'OLD: %s' % r.get('old'), 'NEW: %s' % r.get('new'), '']
open(ws + '/FINDINGS.md', 'w', encoding='utf-8').write('\n'.join(out))
print('fixed entries in part:', sum(1 for l in out if l.startswith('## ')))
PY
echo "workspace $ws: $(wc -c < "$ws/CHANGES.diff") bytes diff, ${#sel[@]} translated files"
