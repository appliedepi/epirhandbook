"""Make search work in one offline language folder opened from file://.

quarto-search.js loads its index with fetch("search.json"), and a browser
refuses fetch on a file:// page. It also shows an alert and gives up when it
sees file://. This rewrites the offline copy only, never site/:

1. search.json is also written as search.js, a classic script that sets
   window.quartoSearchDocs. A <script> tag may load a file:// script.
2. quarto-search.js reads window.quartoSearchDocs instead of fetching, and no
   longer stops on file://.
3. Every page that loads quarto-search.js loads search.js first, with defer.

Usage: python3 checks/offline-search.py <language folder>
"""

import json
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
index = root / "search.json"
search = root / "site_libs" / "quarto-search" / "quarto-search.js"

docs = json.loads(index.read_text(encoding="utf-8"))
if not isinstance(docs, list) or not docs:
    sys.exit(f"::error::{index} is not a non-empty list of search documents")
(root / "search.js").write_text(
    # U+2028 and U+2029 are line breaks to an older JavaScript parser.
    "window.quartoSearchDocs = "
    + json.dumps(docs, ensure_ascii=False).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    + ";\n",
    encoding="utf-8",
)

STOP = re.compile(r'    if \(window\.location\.protocol === "file:" && !shownWarning\) \{\n.*?\n    \}\n', re.DOTALL)
FETCH = 'const response = await fetch(offsetURL("search.json"));'
READ = "const response = { status: 200, json: () => Promise.resolve(window.quartoSearchDocs) };"

js = search.read_text(encoding="utf-8")
js, n_stop = STOP.subn("", js)
if n_stop != 1 or js.count(FETCH) != 1:
    sys.exit(f"::error::{search} has {n_stop} file:// stop(s) and {js.count(FETCH)} search.json fetch(es), expected 1 and 1")
search.write_text(js.replace(FETCH, READ), encoding="utf-8")

# The counts above prove text was replaced, not that the result runs. A stop
# block laid out differently by a future Quarto could leave a stray `else`.
parsed = subprocess.run(
    ["node", "-e", "new (require('vm').Script)(require('fs').readFileSync(process.argv[1], 'utf8'))", str(search)],
    capture_output=True, text=True,
)
if parsed.returncode != 0:
    sys.exit(f"::error::{search} does not parse after the rewrite:\n{parsed.stderr}")

SEARCH_TAG = re.compile(r'<script src="((?:\.\./)*)site_libs/quarto-search/quarto-search\.js"></script>')

pages = 0
for page in root.rglob("*.html"):
    html = page.read_text(encoding="utf-8")
    html, n = SEARCH_TAG.subn(r'<script src="\1search.js" defer></script>\g<0>', html)
    if n > 1:
        sys.exit(f"::error::{page} loads quarto-search.js {n} times")
    if "quarto-search.js" in html and n == 0:
        sys.exit(f"::error::{page} loads quarto-search.js in a form this rewrite does not recognise")
    if n:
        page.write_text(html, encoding="utf-8")
        pages += 1

if pages == 0:
    sys.exit(f"::error::no page under {root} loads quarto-search.js, so the rewrite matched nothing")
print(f"  {root.name}: search index inlined for {pages} page(s), {len(docs)} search document(s)")
