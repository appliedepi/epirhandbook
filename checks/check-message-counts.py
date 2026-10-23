#!/usr/bin/env python3
"""Report a count written into the message text of a check.

Check 20. A check prints counts it measured. A count typed into its message text goes stale
when the repository changes, and it then misstates what the check did. On 2026-10-02
`check-sync.sh` announced "the 416 declared chapter files" while it scanned 400.

The check reads every `.py` and `.sh` file under `checks/`. In each line that prints or
exits with a message (`print`, `echo`, `printf`, `sys.exit`, `die`, `drift`, `.append`), it
looks inside the quoted text for a number of two or more digits. These are allowed:

  a check number       "== 19." or "check 19" / "Check 19"
  a date               2026-10-02
  a version            2.9, 4.5
  a tail length        "last 20 lines"
  a line marked        a trailing comment `# count-ok: <reason>`

Exit 1 on any other number, 2 when checks/ holds no script.

Usage: python3 checks/check-message-counts.py [--summary]
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

args = sys.argv[1:]
for a in args:
    if a != '--summary':
        sys.exit('unknown argument %s. Usage: %s' % (a, __doc__.strip().split('Usage: ')[1]))
summary = '--summary' in args

EMITS = re.compile(r'\b(print|echo|printf|sys\.exit|die|drift|append)\b')
QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
NUMBER = re.compile(r'(?<![\w.%-])\d{2,}(?![\w.])')
ALLOWED = [
    re.compile(r'== \d+\.'),
    re.compile(r'\b[Cc]heck \d+'),
    re.compile(r'\b\d{4}-\d{2}-\d{2}\b'),
    re.compile(r'\b\d+\.\d+\b'),
    re.compile(r'\blast \d+ lines\b'),
]


def numbers(text):
    """The numbers in text that no allowed pattern covers."""
    covered = set()
    for pattern in ALLOWED:
        for m in pattern.finditer(text):
            covered.update(range(m.start(), m.end()))
    return [m.group() for m in NUMBER.finditer(text) if m.start() not in covered]


scripts = sorted(p for p in HERE.iterdir() if p.suffix in ('.py', '.sh') and p.name != Path(__file__).name)
if not scripts:
    print('check-message-counts.py: %s holds no .py or .sh file, so nothing would be read.' % HERE,
          file=sys.stderr)
    sys.exit(2)

found = []
for path in scripts:
    for n, line in enumerate(path.read_text(encoding='utf-8').split('\n'), 1):
        if re.search(r'#\s*count-ok:\s*\S', line) or not EMITS.search(line):
            continue
        for q in QUOTED.findall(line):
            for num in numbers(q):
                found.append((path.name, n, num, line.strip()))

if summary:
    print('scripts read %d, typed counts in messages %d' % (len(scripts), len(found)))
for name, n, num, line in found:
    if not summary or found:
        print('COUNT checks/%s:%d %s in: %s' % (name, n, num, line[:120]))
sys.exit(1 if found else 0)
