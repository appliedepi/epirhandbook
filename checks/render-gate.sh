#!/usr/bin/env bash
# Phase G, the structural render gate: quarto render --no-execute on every translated chapter
# that changed since <base>.
# Usage: checks/render-gate.sh <base-commit> [head]
#
# Each file renders as a temporary copy beside the original, chapters/<stem>.render-gate-tmp.<lang>.qmd.
# In that copy every inline R expression `r ...` outside a fenced block becomes the placeholder
# INLINE_R. quarto render --no-execute stops at an inline R expression, so the placeholder is what
# lets the gate read a file that holds one. The copy sits in the chapters/ folder, so _quarto.yml
# and every relative path resolve as they do for the original. A trap deletes every copy and every
# artifact beside it, in chapters/ and in the project's html_outputs/ folder, on success and on
# failure.
#
# Exit 0 when every file renders, 1 when a file FAILS, 2 when the gate cannot run: a base or head
# that is not a commit, a git diff that fails, or a copy path that already exists or is tracked.
#
# Writes /tmp/render-gate/<stem>.log per file and /tmp/render-gate/SUMMARY.tsv.
# A file with an odd number of fence lines FAILS before render. Pandoc renders an unclosed
# fence with exit 0, so the render alone cannot see that class. YAML damage does exit 1.
# The gate needs quarto and git. It runs no R: --no-execute skips the knitr engine.
set -uo pipefail
cd "$(dirname "$0")/.."
if [ $# -lt 1 ]; then echo "Usage: checks/render-gate.sh <base-commit> [head]" >&2; exit 2; fi
base="$1"; head="${2:-HEAD}"
out=/tmp/render-gate; rm -rf "$out"; mkdir -p "$out"

cleanup() {
  rm -f chapters/*.render-gate-tmp.*.qmd chapters/*.render-gate-tmp.*.html
  rm -rf chapters/*.render-gate-tmp.*_files
  rm -rf html_outputs/chapters/*.render-gate-tmp.*
}
# The cleanup deletes every path that matches the temporary-copy pattern. Refuse to run at all
# when the repository tracks one, rather than delete a tracked file.
tracked=$(git ls-files -- 'chapters/*.render-gate-tmp.*' 'html_outputs/chapters/*.render-gate-tmp.*')
if [ -n "$tracked" ]; then
  echo "render-gate: the repository tracks a render-gate temporary path; refusing to delete it:" >&2
  echo "$tracked" >&2
  exit 2
fi
trap cleanup EXIT
cleanup

for c in "$base" "$head"; do
  if ! git cat-file -e "$c^{commit}" 2>/dev/null; then
    echo "render-gate: '$c' is not a commit in this repository" >&2; exit 2
  fi
done
if ! git diff --name-only "$base" "$head" -- 'chapters/*.qmd' > "$out/diff.txt" 2>"$out/diff.err"; then
  echo "render-gate: git diff $base $head failed:" >&2; cat "$out/diff.err" >&2; exit 2
fi
mapfile -t files < <(grep -E '\.[a-z]{2}\.qmd$' "$out/diff.txt" | sort)

pass=0; fail=0; gone=0; inline=0
printf 'file\tresult\tseconds\n' > "$out/SUMMARY.tsv"
for f in "${files[@]}"; do
  if [ ! -f "$f" ]; then
    printf '%s\tskip-deleted\t0\n' "$f" >> "$out/SUMMARY.tsv"; gone=$((gone+1)); continue
  fi
  if [ $(( $(grep -cE '^\s*```' "$f") % 2 )) -ne 0 ]; then
    printf '%s\tFAIL-fence-parity\t0\n' "$f" >> "$out/SUMMARY.tsv"; fail=$((fail+1)); continue
  fi
  grep -q '`r ' "$f" && inline=$((inline+1))
  stem="${f%.qmd}"                       # chapters/gis.es
  lang="${stem##*.}"                     # es
  copy="${stem%.*}.render-gate-tmp.$lang.qmd"
  if git ls-files --error-unmatch "$copy" >/dev/null 2>&1; then
    echo "render-gate: $copy is tracked; refusing to write over it" >&2; exit 2
  fi
  if [ -e "$copy" ]; then
    echo "render-gate: $copy already exists; refusing to overwrite it" >&2; exit 2
  fi
  if ! python3 - "$f" "$copy" <<'PY'
import io, re, sys

src, dst = sys.argv[1], sys.argv[2]
FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
# An inline R expression may wrap onto the next line, and it may not cross a blank line.
# Without that bound the match runs to the next backtick anywhere in the file, and one
# unterminated expression then swallows whole paragraphs into the placeholder.
INLINE = re.compile(r'`r[ \t\n](?:[^`\n]|\n(?![ \t]*\n))*`')
OPENER = re.compile(r'`r[ \t\n]')
lines = io.open(src, encoding='utf-8', newline='').read().split('\n')
marked, fence = [], None
for l in lines:
    m = FENCE.match(l)
    code = m is None or len(m.group(1)) > 3
    if fence is None and not code:
        fence = m.group(2); marked.append((False, l)); continue
    if fence is not None:
        if not code and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) \
                and not m.group(3).strip():
            fence = None
        marked.append((False, l)); continue
    marked.append((True, l))
out, buf = [], []


def flush():
    """Replace every inline R expression in the buffered prose, keeping the line count."""
    if not buf:
        return
    t = INLINE.sub(lambda m: 'INLINE_R' + '\n' * m.group(0).count('\n'), '\n'.join(buf))
    out.extend(t.split('\n'))
    del buf[:]


for is_prose, l in marked:
    if is_prose:
        buf.append(l)
    else:
        flush(); out.append(l)
flush()
if len(out) != len(lines):
    sys.exit('%s: line count changed, %d -> %d' % (src, len(lines), len(out)))
left = [(n, l) for n, (is_prose, l) in enumerate(zip([p for p, _ in marked], out), 1)
        if is_prose and OPENER.search(l)]
if left:
    sys.exit('%s: an inline R expression does not close inside its paragraph, line %d: %s'
             % (src, left[0][0], left[0][1].strip()[:120]))
io.open(dst, 'w', encoding='utf-8', newline='').write('\n'.join(out))
PY
  then
    printf '%s\tFAIL-placeholder\t0\n' "$f" >> "$out/SUMMARY.tsv"; fail=$((fail+1)); continue
  fi
  t0=$(date +%s)
  if timeout 180 quarto render "$copy" --no-execute --to html > "$out/$(basename "$stem").log" 2>&1
  then r=pass; pass=$((pass+1)); else r=FAIL; fail=$((fail+1)); fi
  printf '%s\t%s\t%s\n' "$f" "$r" "$(( $(date +%s) - t0 ))" >> "$out/SUMMARY.tsv"
  rm -f "$copy" "${copy%.qmd}.html"; rm -rf "${copy%.qmd}_files"
  rm -rf html_outputs/"${copy%.qmd}".html html_outputs/"${copy%.qmd}"_files
done
echo "rendered: pass $pass, FAIL $fail, deleted $gone, of ${#files[@]} changed translated files"
echo "skipped inline-r 0: the gate renders inline R through the INLINE_R placeholder; $inline of these files carry inline R"
grep -P '\tFAIL' "$out/SUMMARY.tsv" || true
# A FAIL without its reason is unreadable in CI, where /tmp/render-gate is gone when the job ends.
# Print the last lines of the first failing render log, prefixed so the caller can pass them on.
first=$(grep -P '\tFAIL\t' "$out/SUMMARY.tsv" | head -1 | cut -f1)
if [ -n "$first" ]; then
  echo "FAIL-LOG $first (last 25 lines):"
  tail -25 "$out/$(basename "${first%.qmd}").log" | sed 's/^/FAIL-LOG   /'
fi
[ "$fail" -eq 0 ]
