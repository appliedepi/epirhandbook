#!/usr/bin/env bash
# Build a read-only codex workspace for one language's fix-pass commits in a range.
# Usage: modernization/codex-bundle.sh <lang> <base-commit> <head-commit> <label>
# Writes /tmp/codex-ws/<label>/ with: CHANGES.diff (that language's chapter edits in
# base..head), FINDINGS.md (the fixed entries of the fix-pass batches committed in that
# range), the touched translated chapters and their English sources as of <head>, and
# PROMPT.txt. Code only, no data.
set -euo pipefail
cd "$(dirname "$0")/.."
lang="$1"; base="$2"; head="$3"; label="$4"
ws=/tmp/codex-ws/$label
rm -rf "$ws"; mkdir -p "$ws/chapters"
git diff "$base" "$head" -- "chapters/*.$lang.qmd" > "$ws/CHANGES.diff"
mapfile -t files < <(git diff --name-only "$base" "$head" -- "chapters/*.$lang.qmd" | sort)
for f in "${files[@]}"; do
  git show "$head:$f" > "$ws/$f"
  en="${f%.$lang.qmd}.qmd"; git show "$head:$en" > "$ws/$en"
done
mapfile -t results < <(git log --name-only --pretty=format: "$base..$head" -- "modernization/findings/fix-pass/$lang.*.json" | sort -u | sed '/^$/d')
python3 - "$lang" "$ws" "$head" "${results[@]}" <<'PY'
import json, subprocess, sys
lang, ws, head, paths = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
out = ['# Fix-pass verdicts for language %s, batches committed in this range' % lang, '']
n = 0
for p in sorted(paths):
    d = json.loads(subprocess.run(['git', 'show', '%s:%s' % (head, p)], capture_output=True, text=True).stdout)
    for r in d['results']:
        if r['verdict'] == 'fixed':
            n += 1
            out += ['## %s  (%s, %s)' % (r['id'], d['kind'], r['file']), 'reason: %s' % r.get('reason'), 'OLD: %s' % r.get('old'), 'NEW: %s' % r.get('new'), '']
open(ws + '/FINDINGS.md', 'w', encoding='utf-8').write('\n'.join(out))
print('batches %d, fixed entries %d' % (len(paths), n))
PY
cp modernization/codex-prompt.txt "$ws/PROMPT.txt"
echo "workspace $ws: diff $(wc -c < "$ws/CHANGES.diff") bytes, ${#files[@]} translated files, hunks $(grep -c '^@@' "$ws/CHANGES.diff")"
find "$ws" -name '*.qs2' -o -name '*.xlsx' -o -name '*.rds' -o -name '*.csv' | head -3
