#!/usr/bin/env python3
"""Report markdown that LOOKS like a link but that pandoc did not turn into one.

check-links.py asks pandoc which links it found, then checks their targets. Anything that
never parses as a link is invisible to it by construction, and its own header says so for one
form. Four defects have come out of that blind spot, all found by reading:

  [text][label]                 a reference link whose [label]: definition does not exist
  [text(url)]                   the bracket and the paren transposed
  text](url)                    the opening bracket missing
  [text](url) after a bare $    two unescaped dollars pair as TeX math and swallow the link

Every one renders as literal bracket text on the published page.

THE RULE, one line: a link that parsed leaves no brackets behind. Render the chapter, then
look for a residual `](` or `][`. Four things are removed first, because each produces that
signature without being a defect:

  fenced code blocks   ```{r} ... ```      R code is full of x[[1]][2]
  HTML comments        <!-- ... -->        pandoc passes them through unparsed
  inline R             `r "https://..."`   Quarto evaluates these, pandoc does not
  rendered code        <code>, <pre>       inline spans that survived as code

Usage: python3 checks/check-unparsed-links.py [--summary] [--fixture <dir>] [--pandoc <cmd>]
Exit 0 when every chapter is clean, 1 when any chapter holds an unparsed link.
"""
import pathlib
import re
import shutil
import subprocess
import sys

FENCE = re.compile(r'^( *)(`{3,}|~{3,})(.*)$')
COMMENT = re.compile(r'<!--.*?-->', re.S)
INLINE_R = re.compile(r'`r\s[^`]*`')
HTML_CODE = re.compile(r'<code.*?</code>|<pre.*?</pre>', re.S)
# Two signatures, because they catch different failures.
#   ]( or ][   the link text closed and the target began, but nothing parsed
#   [ ... ]    a bracketed span whose content looks like a link TARGET. This is the
#              transposed form [text(url)], which contains neither of the above:
#              the brackets and parens nest the wrong way round.
SIGNATURE = re.compile(
    r'\]\(|\]\[|'
    r'\[[^\]]{0,120}?(?:\.qmd|\.html|https?://|\(#)[^\]]{0,120}?\]'
)

args = sys.argv[1:]
known = {'--summary': 0, '--fixture': 1, '--pandoc': 1}
for a in args:
    if a.startswith('--') and a not in known:
        sys.exit(f"unknown argument {a}. Usage: check-unparsed-links.py [--summary] [--fixture <dir>] [--pandoc <cmd>]")


def opt(name):
    return args[args.index(name) + 1] if name in args else None


summary = '--summary' in args
root = pathlib.Path(opt('--fixture') or '.')
pandoc = (opt('--pandoc') or '').split() or (['quarto', 'pandoc'] if shutil.which('quarto') else ['pandoc'])


def strip_fences(text):
    out, fence = [], None
    for line in text.splitlines():
        m = FENCE.match(line)
        if fence is None and m:
            fence = m.group(2)
            out.append('')
            continue
        if fence is not None:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence):
                fence = None
            out.append('')
            continue
        out.append(line)
    return '\n'.join(out)


chapters = sorted(root.glob('content/*/*.qmd'))
if not chapters:
    sys.exit(f"check-unparsed-links.py: no chapter found under {root}/content/<lang>/. "
             "An empty file set would otherwise report a clean tree.")

findings = []
for chapter in chapters:
    source = INLINE_R.sub('RCODE', COMMENT.sub('', strip_fences(chapter.read_text(encoding='utf-8'))))
    html = subprocess.run(pandoc + ['-f', 'markdown', '-t', 'html'],
                          input=source, capture_output=True, text=True).stdout
    rendered = HTML_CODE.sub('', html)
    for match in SIGNATURE.finditer(rendered):
        context = rendered[max(0, match.start() - 45):match.start() + 40].replace('\n', ' ').strip()
        findings.append((str(chapter.relative_to(root)), match.group(0), context))

print(f"files scanned: {len(chapters)}")
print(f"pandoc: {' '.join(pandoc)}")
print(f"unparsed links: {len(findings)}")
if findings and not summary:
    for shown, signature, context in findings:
        print(f"{shown}\t{signature}\t{context}")
sys.exit(1 if findings else 0)
