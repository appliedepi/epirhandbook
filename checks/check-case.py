#!/usr/bin/env python3
"""Check 22. Every file name under content/, images/ and data/ is lowercase.

A web server and git on Linux treat Dates.png and dates.png as two files. macOS and Windows
treat them as one. So a mixed-case name works on the published site and breaks for a reader
who downloads the handbook or the data: two names that differ only by case overwrite each
other when unzipped, and a link with the wrong case works on one machine and not another.
One rule removes the whole class: every name is lowercase.

The final extension MAY be .R, .Rmd or .Rproj, which is how R spells them. Because that lets
foo.R and foo.r both pass, the check also fails on two names that differ only by case. Files
outside the three folders, such as README.md, are not checked, and neither are the files a
local render writes, which .gitignore keeps out of git.

With --tree DIR, the check reads one built tree instead, and fails when two of its files
differ only by case. The deploy job runs it on each offline copy before zipping it, because
that tree also holds third-party files the rule above cannot reach.

Usage: python3 checks/check-case.py [--summary]
       python3 checks/check-case.py --tree DIR
Exit 0 when clean, 1 on a finding, 2 on a missing input.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FOLDERS = ['content', 'images', 'data']
R_EXTENSIONS = ('.R', '.Rmd', '.Rproj')


def ignored(rel):
    """True for a file a local render or tool writes, which .gitignore keeps out of git."""
    parts = rel.parts
    return (any(p in ('.quarto', 'html_outputs', '__pycache__', '.Rproj.user') for p in parts)
            or parts[-1] == '.DS_Store'
            or (parts[0] == 'content' and any(p.endswith('_files') for p in parts[:-1])))


def lowercase(name):
    for ext in R_EXTENSIONS:
        if name.endswith(ext):
            name = name[:-len(ext)]
            break
    return name == name.lower()


def check_repo(summary):
    bad, seen, groups = [], 0, {}
    for folder in FOLDERS:
        top = ROOT / folder
        if not top.is_dir():
            sys.stderr.write('check-case.py: no %s/ folder. The check reads every file name '
                             'in content/, images/ and data/.\n' % folder)
            sys.exit(2)
        files = [p for p in top.rglob('*') if p.is_file() and not ignored(p.relative_to(ROOT))]
        if not files:
            sys.stderr.write('check-case.py: %s/ holds no file, so there is nothing to '
                             'check.\n' % folder)
            sys.exit(2)
        for p in files:
            seen += 1
            rel = p.relative_to(ROOT)
            if not all(lowercase(part) for part in rel.parts):
                bad.append(str(rel))
            groups.setdefault(str(rel).lower(), []).append(str(rel))
    clashes = sorted(v for v in groups.values() if len(v) > 1)
    for b in sorted(bad):
        print('   NOT LOWERCASE %s' % b)
    for c in clashes:
        print('   SAME NAME BUT CASE: %s' % ' | '.join(sorted(c)))
    print('lowercase names: %d file(s) in %s, %d not lowercase, %d case clash(es)'
          % (seen, ', '.join(FOLDERS), len(bad), len(clashes)))
    return 1 if bad or clashes else 0


def check_tree(tree):
    tree = pathlib.Path(tree)
    if not tree.is_dir():
        sys.stderr.write('check-case.py: %s is not a folder.\n' % tree)
        sys.exit(2)
    groups = {}
    for p in tree.rglob('*'):
        if p.is_file():
            rel = str(p.relative_to(tree))
            groups.setdefault(rel.lower(), []).append(rel)
    if not groups:
        sys.stderr.write('check-case.py: %s holds no file.\n' % tree)
        sys.exit(2)
    clashes = sorted(v for v in groups.values() if len(v) > 1)
    for c in clashes:
        print('   SAME NAME BUT CASE: %s' % ' | '.join(sorted(c)))
    print('case clashes in %s: %d file(s), %d clash(es)' % (tree, sum(len(v) for v in groups.values()), len(clashes)))
    return 1 if clashes else 0


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['--tree'] and len(args) == 2:
        sys.exit(check_tree(args[1]))
    if args in ([], ['--summary']):
        sys.exit(check_repo('--summary' in args))
    sys.stderr.write('usage: checks/check-case.py [--summary] | --tree DIR\n')
    sys.exit(2)
