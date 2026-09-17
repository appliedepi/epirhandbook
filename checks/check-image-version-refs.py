#!/usr/bin/env python3
"""Every image version named in prose must be one the repository actually uses.

`docker-images.yml` maps each chapter to a render image, and `.devcontainer.json` names the
image a contributor opens the repository in. Those are the two files that decide which image
line is live. Prose is not: README.md describes the image line in sentences, in a
`.devcontainer.json` code block, and in a path like `epirhandbook/<version>/generate_groups.py`.

Prose does not fail a build, so it rots silently. After the 2.9 migration README.md still said
2.8 in three places, including a code block claiming to show the contents of
`.devcontainer.json`, which by then said 2.9. A contributor copying that block would have
opened the repository in the wrong image.

One rule: every `2.<n>` an image sentence, a ghcr.io reference or an `epirhandbook/<version>/`
path names in a documentation file MUST be a version that `docker-images.yml` or
`.devcontainer.json` names. A version that only prose believes in is drift.

A version `docker-images.yml` names in a COMMENT counts as used. The manifest documents pinning
a chapter back to an older image, and that is a real option, not a stale reference.

Usage: python3 checks/check-image-version-refs.py [--summary] [--fixture <dir>]
Exit 0 when every prose version is live, 1 when prose names one nothing uses.
"""
import pathlib
import re
import sys

args = sys.argv[1:]
known = {'--summary': 0, '--fixture': 1}
for a in args:
    if a.startswith('--') and a not in known:
        sys.exit(f"unknown argument {a}. Usage: check-image-version-refs.py [--summary] [--fixture <dir>]")

summary = '--summary' in args
root = pathlib.Path(args[args.index('--fixture') + 1] if '--fixture' in args else
                    pathlib.Path(__file__).resolve().parent.parent)

# An image DECLARATION, not any 2.<n> in the file. Both of those files carry narrative
# comments mentioning past lines ("2.8 and 2.9 publish six GROUP images"), and counting those
# as live made every superseded version acceptable forever. The gate then could not have caught
# the defect it was written for.
VERSION = re.compile(r'image"?\s*:\s*"?[^\s"\']*:(2\.\d+)')
# Only where a number is unambiguously an image version.
IN_PROSE = re.compile(
    r'ghcr\.io/[^\s"\']*?:(2\.\d+)'          # a pulled image
    r'|epirhandbook/(2\.\d+)/'               # a path inside the image repository
    r'|\bThe (2\.\d+) images\b'              # "The 2.9 images are public"
)

sources = {'docker-images.yml': root / 'docker-images.yml',
           '.devcontainer.json': root / '.devcontainer.json'}
for name, path in sources.items():
    if not path.is_file():
        sys.exit(f"check-image-version-refs.py: no {path}. That file is one of the two that "
                 "decide which image line is live, so prose cannot be checked against it.")

live = set()
for path in sources.values():
    live.update(VERSION.findall(path.read_text(encoding='utf-8')))
if not live:
    sys.exit("check-image-version-refs.py: neither docker-images.yml nor .devcontainer.json "
             "names an image version. An empty set would match nothing and report agreement.")

# README.md is REQUIRED, not merely one of a list. With it absent and checks/README.md
# present the doc list stays non-empty, so the check would pass while the file it was written
# about had gone. Check 12 caught exactly that.
main_doc = root / 'README.md'
if not main_doc.is_file():
    sys.exit(f"check-image-version-refs.py: no {main_doc}. That file is the prose this check "
             "is about, and without it nothing is measured.")
docs = [main_doc] + [p for p in [root / 'checks' / 'README.md'] if p.is_file()]

stale = []
checked = 0
for doc in docs:
    for number, line in enumerate(doc.read_text(encoding='utf-8').splitlines(), 1):
        for match in IN_PROSE.finditer(line):
            version = next(g for g in match.groups() if g)
            checked += 1
            if version not in live:
                stale.append(f"{doc.relative_to(root)}:{number} names {version}, "
                             f"live versions are {' '.join(sorted(live))}")

print(f"live image versions: {' '.join(sorted(live))}")
print(f"prose references checked: {checked}")
print(f"stale: {len(stale)}")
if stale and not summary:
    for s in stale:
        print(s)
sys.exit(1 if stale else 0)
