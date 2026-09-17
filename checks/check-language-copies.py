#!/usr/bin/env python3
"""Every second copy of the language list must agree with languages.yml.

`languages.yml` is the one file that declares which languages ship. Everything that renders or
deploys reads it: the CI workflow, build_all_chapters.sh, inject_language_links.R and the checks.

`banner.html` is the exception. Its `const translations = {...}` object carries one key per
language, hard-coded, because the banner text is prose and there is nowhere else to put it.
That is a deliberate second copy, and a deliberate second copy is exactly the thing that drifts:
add a ninth language to languages.yml and the banner silently has no text for it, while every
other part of the system picks it up.

One rule: the key set of that object MUST equal the code set languages.yml declares.

`offline_long/standalone_html.R` used to be a third copy, with its own language vector and title
map that nothing checked. It excluded `en`, which is one of the two faults that made it unable to
run at all. It was deleted on 2026-09-16.

Usage: python3 checks/check-language-copies.py [--summary] [--fixture <dir>]
Exit 0 when every copy agrees, 1 on any disagreement.
"""
import pathlib
import re
import sys

args = sys.argv[1:]
known = {'--summary': 0, '--fixture': 1}
for a in args:
    if a.startswith('--') and a not in known:
        sys.exit(f"unknown argument {a}. Usage: check-language-copies.py [--summary] [--fixture <dir>]")

summary = '--summary' in args
root = pathlib.Path(args[args.index('--fixture') + 1] if '--fixture' in args else
                    pathlib.Path(__file__).resolve().parent.parent)

declared_path = root / 'languages.yml'
if not declared_path.is_file():
    sys.exit(f"check-language-copies.py: no {declared_path}. That file is the one declaration of "
             "which languages ship, and without it there is nothing to compare a copy against.")
declared = re.findall(r'^\s*-\s*code:\s*([A-Za-z0-9_]+)', declared_path.read_text(encoding='utf-8'), re.M)
if not declared:
    sys.exit(f"check-language-copies.py: {declared_path} declares no language. An empty list "
             "would match an empty copy and report agreement.")

banner_path = root / 'banner.html'
if not banner_path.is_file():
    sys.exit(f"check-language-copies.py: no {banner_path}, which holds the banner's own copy "
             "of the language list.")
banner = banner_path.read_text(encoding='utf-8')
block = re.search(r'const\s+translations\s*=\s*\{(.*?)\n\s*\}', banner, re.S)
if block is None:
    sys.exit(f"check-language-copies.py: no `const translations = {{...}}` in {banner_path}. "
             "If the banner stopped carrying its own copy, delete this check.")
copied = re.findall(r'^\s*([A-Za-z0-9_]+)\s*:', block.group(1), re.M)

problems = []
for code in declared:
    if code not in copied:
        problems.append(f"languages.yml declares '{code}', banner.html has no translation for it")
for code in copied:
    if code not in declared:
        problems.append(f"banner.html carries '{code}', languages.yml does not declare it")

print(f"languages declared: {len(declared)} ({' '.join(declared)})")
print(f"banner.html copies: {len(copied)} ({' '.join(copied)})")
print(f"disagreements: {len(problems)}")
if problems and not summary:
    for p in problems:
        print(p)
sys.exit(1 if problems else 0)
