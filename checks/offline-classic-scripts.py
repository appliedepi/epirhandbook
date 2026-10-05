"""Make one offline language folder run its Quarto scripts from file://.

Quarto loads quarto.js and tabsets.js as ES modules (type="module"). A browser
refuses a module script on a file:// page, so an unzipped offline copy runs
neither. quarto.js builds the table of contents in the right margin, so the
offline pages show its title and nothing else.

This rewrites the offline copy only, never site/:

1. quarto.js becomes one classic script, with tabsets.js inlined in front of it.
   Both are wrapped in one function, so their top-level names stay private, as
   they were in the modules.
2. Every page loads quarto.js with defer instead of type="module". A module
   script is deferred too, so the run order does not change.
3. Every page drops its tabsets.js tag, because quarto.js now carries it.

Usage: python3 checks/offline-classic-scripts.py <language folder>
"""

import pathlib
import re
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
libs = root / "site_libs" / "quarto-html"
quarto = libs / "quarto.js"
tabsets = libs / "tabsets" / "tabsets.js"

IMPORT = 'import * as tabsets from "./tabsets/tabsets.js";\n'
EXPORT = "export function init()"

q = quarto.read_text(encoding="utf-8")
t = tabsets.read_text(encoding="utf-8")
if not q.startswith(IMPORT):
    sys.exit(f"::error::{quarto} no longer starts with the tabsets import this rewrite expects")
if t.count(EXPORT) != 1:
    sys.exit(f"::error::{tabsets} no longer has the one exported init() this rewrite expects")

t = t.replace(EXPORT, "function init()")
quarto.write_text(
    '(() => {\n"use strict";\nconst tabsets = (() => {\n' + t + "\nreturn { init };\n})();\n"
    + q[len(IMPORT):] + "\n})();\n",
    encoding="utf-8",
)

# A text check cannot prove the result runs as a classic script. Parsing can.
# vm.Script parses only as a classic script, so any import, export, import.meta
# or top-level await left over from a future Quarto fails here. node --check is
# not enough: recent Node retries a file as a module when it fails as a script.
parsed = subprocess.run(
    ["node", "-e", "new (require('vm').Script)(require('fs').readFileSync(process.argv[1], 'utf8'))", str(quarto)],
    capture_output=True, text=True,
)
if parsed.returncode != 0:
    sys.exit(f"::error::{quarto} does not parse as a classic script:\n{parsed.stderr}")

QUARTO_TAG = re.compile(r'(<script src="[^"]*site_libs/quarto-html/quarto\.js") type="module">')
MODULE_TAG = re.compile(r"<script\b[^>]*\btype\s*=\s*[\"']?module\b", re.IGNORECASE)
TABSETS_TAG = re.compile(r'<script src="[^"]*site_libs/quarto-html/tabsets/tabsets\.js" type="module"></script>')

pages = 0
for page in root.rglob("*.html"):
    html = page.read_text(encoding="utf-8")
    html, nq = QUARTO_TAG.subn(r"\1 defer>", html)
    html, nt = TABSETS_TAG.subn("", html)
    if nq != nt or nq > 1:
        sys.exit(f"::error::{page} has {nq} quarto.js and {nt} tabsets.js module tag(s), expected 1 and 1 or none")
    if MODULE_TAG.search(html):
        sys.exit(f"::error::{page} still loads a module script, which a file:// page cannot run")
    if nq:
        page.write_text(html, encoding="utf-8")
        pages += 1

if pages == 0:
    sys.exit(f"::error::no page under {root} loads quarto.js, so the rewrite matched nothing")
print(f"  {root.name}: quarto.js made classic in {pages} page(s)")
