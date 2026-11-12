#!/usr/bin/env python3
"""Report every images/ file a chapter names that does not exist.

Chapters reach the shared assets two ways, and both are checked:

  knitr::include_graphics(here::here("images", "<name>"))    the usual form
  ![alt](images/<name>) or ![alt](../../images/<name>)       plain markdown

COMMENTED LINES COUNT. A commented include_graphics is still a claim about the repository,
and the one this check was written for lived inside an R comment in all eight languages:
images/survanalysis.png, absent since before the migration, named by survival_analysis.qmd.
Nothing rendered it, so nothing caught it.

This is deliberately a NAME check, not a render check. It reads the sources, so it costs a
second and runs with the other static checks rather than behind the render gate.

Usage: python3 checks/check-image-names.py [--summary] [--fixture <dir>]
Exit 0 when every named image exists, 1 when any is missing, 2 on a missing input.
"""
import pathlib
import re
import sys

HERE_FORM = re.compile(r'here(?:::here)?\(\s*"images"\s*((?:,\s*"[^"]+"\s*)+)\)')
PIECE = re.compile(r'"([^"]+)"')
MARKDOWN_FORM = re.compile(r'!\[[^\]]*\]\(\s*(?:\.\./)*images/([^)\s]+)')

args = sys.argv[1:]
known = {'--summary': 0, '--fixture': 1}
for a in args:
    if a.startswith('--') and a not in known:
        sys.exit(f"unknown argument {a}. Usage: check-image-names.py [--summary] [--fixture <dir>]")

summary = '--summary' in args
root = pathlib.Path(args[args.index('--fixture') + 1] if '--fixture' in args else '.')
images = root / 'images'

chapters = sorted(root.glob('content/*/*.qmd'))
if not chapters:
    print(f"check-image-names.py: no chapter found under {root.resolve()}/content/<lang>/. "
          "An empty file set would otherwise report a clean tree.", file=sys.stderr)
    sys.exit(2)
if not images.is_dir() or not any(images.iterdir()):
    print(f"check-image-names.py: {images.resolve()} is missing or empty. "
          "Every name would report missing.", file=sys.stderr)
    sys.exit(2)

named, missing = {}, []
for chapter in chapters:
    text = chapter.read_text(encoding='utf-8')
    # group(1) is everything after "images", so ("images", "shiny", "a.gif")
    # yields ["shiny", "a.gif"], which is the path below images/.
    found = ['/'.join(PIECE.findall(m.group(1))) for m in HERE_FORM.finditer(text)]
    found += MARKDOWN_FORM.findall(text)
    for name in found:
        named.setdefault(name, []).append(str(chapter.relative_to(root)))

for name in sorted(named):
    if not (images / name).is_file():
        missing.append((name, named[name]))

print(f"files scanned: {len(chapters)}")
print(f"distinct image names: {len(named)}")
print(f"missing from images/: {len(missing)}")
if missing and not summary:
    for name, users in missing:
        print(f"images/{name}\tnamed by {len(users)} file(s), first {users[0]}")
sys.exit(1 if missing else 0)
