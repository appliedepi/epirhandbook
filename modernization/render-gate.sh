#!/usr/bin/env bash
# Phase G, the structural render gate: quarto render --no-execute on every translated chapter
# that changed since <base>, skipping files that carry inline R code (`r ...`), which fail under
# --no-execute at the inline expression regardless of the prose.
# Usage: modernization/render-gate.sh <base-commit> [head]
# Writes /tmp/render-gate/<stem>.log per file and /tmp/render-gate/SUMMARY.tsv, and deletes the
# .html and _files/ artifacts that a single-file render drops beside the source. A chapter whose
# .html the repository tracks is skipped: rendering it overwrites a committed artifact.
# A file with an odd number of fence lines FAILS before render: pandoc renders an unclosed
# fence with exit 0, so the render alone cannot see that class. YAML damage and inline R do exit 1.
set -uo pipefail
cd "$(dirname "$0")/.."
base="$1"; head="${2:-HEAD}"
out=/tmp/render-gate; rm -rf "$out"; mkdir -p "$out"
# Tracked files from the HEAD tree, read once: git ls-files fails while another git process holds
# the index lock, and a failed check rendered a tracked artifact on 2026-09-02.
git ls-tree -r HEAD --name-only > "$out/tracked.txt"
mapfile -t files < <(git diff --name-only "$base" "$head" -- 'chapters/*.qmd' | grep -E '\.[a-z]{2}\.qmd$' | sort)
pass=0; fail=0; skip=0
printf 'file\tresult\tseconds\n' > "$out/SUMMARY.tsv"
for f in "${files[@]}"; do
  stem="${f%.qmd}"
  if grep -q '`r ' "$f"; then printf '%s\tskip-inline-r\t0\n' "$f" >> "$out/SUMMARY.tsv"; skip=$((skip+1)); continue; fi
  if grep -qxF "$stem.html" "$out/tracked.txt"; then printf '%s\tskip-tracked-artifact\t0\n' "$f" >> "$out/SUMMARY.tsv"; skip=$((skip+1)); continue; fi
  if [ $(( $(grep -cE '^\s*```' "$f") % 2 )) -ne 0 ]; then printf '%s\tFAIL-fence-parity\t0\n' "$f" >> "$out/SUMMARY.tsv"; fail=$((fail+1)); continue; fi
  t0=$(date +%s)
  if timeout 180 quarto render "$f" --no-execute --to html > "$out/$(basename "$stem").log" 2>&1; then r=pass; pass=$((pass+1)); else r=FAIL; fail=$((fail+1)); fi
  printf '%s\t%s\t%s\n' "$f" "$r" "$(( $(date +%s) - t0 ))" >> "$out/SUMMARY.tsv"
  # Delete only artifacts that git does not track: some chapters commit their .html and _files.
  for a in "$stem.html" "${stem}_files"; do grep -q "^$a" "$out/tracked.txt" || rm -rf "$a"; done
done
echo "rendered: pass $pass, FAIL $fail, skipped inline-r $skip, of ${#files[@]} changed translated files"
grep -P '\tFAIL' "$out/SUMMARY.tsv" || true
[ "$fail" -eq 0 ]
