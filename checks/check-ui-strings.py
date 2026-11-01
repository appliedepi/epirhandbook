#!/usr/bin/env python3
"""Check 23. Every language's interface strings in ael-extras.html carry the same keys.

ael-extras.html builds the app bar and the help box beside every chapter in the browser. Its
`var UI = { ... }` object holds one block of strings per language, keyed by the BCP-47 tag in
<html lang>. The script reads `ui.<key>` from the block of the page's language. A block that
lacks a key shows the word "undefined" in its place. It does not fall back to English. Only a
language with no block at all reads English.

So the check fails when:
  - a block lacks a key that the `en` block has, or has a key the `en` block lacks
  - a language in languages.yml, by its `lang:` tag, has no block
  - a block names a tag that languages.yml does not declare

Usage: python3 checks/check-ui-strings.py [--summary]
Exit 0 when clean, 1 on a finding, 2 on a missing input.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from langs import Unreadable, parse  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def blocks(path):
    """{tag: [keys]} for each language block of `var UI = { ... };` in one file."""
    if not path.is_file():
        raise Unreadable('no %s. It holds the interface strings this check compares.' % path.name)
    text = path.read_text(encoding='utf-8')
    m = re.search(r'var UI = \{(.*?)\n  \};', text, re.S)
    if not m:
        raise Unreadable('%s has no `var UI = { ... };` object.' % path.name)
    found = {}
    for tag, body in re.findall(r'^    ([a-z]{2,3}): \{(.*?)\}', m.group(1), re.S | re.M):
        found[tag] = re.findall(r"(\w+):\s*'", body)
    if not found:
        raise Unreadable('%s: the UI object holds no language block.' % path.name)
    return found


def main():
    found = blocks(ROOT / 'ael-extras.html')
    doc = parse(ROOT / 'languages.yml')
    tags = [e.get('lang') for e in doc.get('languages', [])] if isinstance(doc, dict) else []
    if not tags:
        raise Unreadable('languages.yml declares no language.')
    if 'en' not in found:
        raise Unreadable('ael-extras.html has no en block, the reference for the others.')
    ref = set(found['en'])
    bad = []
    for tag, keys in found.items():
        miss, extra = sorted(ref - set(keys)), sorted(set(keys) - ref)
        if miss:
            bad.append('%s lacks %s' % (tag, ' '.join(miss)))
        if extra:
            bad.append('%s has keys en lacks: %s' % (tag, ' '.join(extra)))
        if tag not in tags:
            bad.append('%s is not a lang: tag in languages.yml' % tag)
    for tag in tags:
        if tag not in found:
            bad.append('languages.yml declares lang %s, and ael-extras.html has no block for it' % tag)
    for b in bad:
        print('   %s' % b)
    print('interface strings: %d block(s), %d key(s) each in en, %d finding(s)'
          % (len(found), len(ref), len(bad)))
    return 1 if bad else 0


if __name__ == '__main__':
    if sys.argv[1:] not in ([], ['--summary']):
        sys.exit('usage: checks/check-ui-strings.py [--summary]')
    sys.exit(main())
