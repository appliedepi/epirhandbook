#!/usr/bin/env bash
# Commit one fix batch: its translated files and its result file, signed.
# Usage: modernization/commit-batch.sh <batch-id>
# Refuses when the reconciliation checker fails for that batch.
set -euo pipefail
cd "$(dirname "$0")/.."
bid="$1"
python3 modernization/reconcile-fix-pass.py "$bid" > /tmp/fixpass/reconcile-"$bid".txt || { cat /tmp/fixpass/reconcile-"$bid".txt; echo "REFUSED: reconcile failed for $bid"; exit 1; }
read -r lang kind n fixed rejected deferred files < <(python3 - "$bid" <<'PY'
import csv, json, sys
bid = sys.argv[1]
idx = {r['batch']: r for r in csv.DictReader(open('modernization/findings/fix-pass/batch-index.tsv', encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)}
d = json.load(open('modernization/findings/fix-pass/%s.json' % bid, encoding='utf-8'))
c = {'fixed': 0, 'rejected': 0, 'deferred': 0}
for r in d['results']: c[r['verdict']] += 1
print(idx[bid]['lang'], idx[bid]['kind'], len(d['results']), c['fixed'], c['rejected'], c['deferred'], idx[bid]['files'].replace(',', ' '))
PY
)
# shellcheck disable=SC2086
git add modernization/findings/fix-pass/"$bid".json $files
if git diff --cached --quiet; then echo "nothing staged for $bid"; exit 0; fi
git -c commit.gpgsign=true commit -S -q -F - <<MSG
Fix pass $bid: $lang $kind, $fixed fixed, $rejected rejected, $deferred deferred

One agent verified and fixed $n findings of kind $kind in the $lang
translation. Rejected findings were judged wrong or not a defect and left
unedited. Deferred findings are correct but need a change outside the pass's
permissions. Verdicts and the exact old/new text are in
modernization/findings/fix-pass/$bid.json. Verified by
modernization/reconcile-fix-pass.py against the working tree.
MSG
sig=$(git log -1 --pretty=%G?)
echo "committed $bid: $lang $kind fixed=$fixed rejected=$rejected deferred=$deferred sig=$sig $(git log -1 --pretty=%h)"
[ "$sig" = G ]
