#!/bin/bash
# Assemble one site tree from the render output of each language.
#
# Usage: checks/assemble-site.sh <downloaded> <site> <mainlanguage> "<lang> <lang> ..."
#
#   <downloaded>   holds one folder site-<lang>/ per language, the output of that language's
#                  render: the artifacts in CI, or html_outputs copies locally
#   <site>         the tree to write; it MUST NOT exist yet
#
# The assemble-deploy job of .github/workflows/build-deploy.yml runs this, and
# checks/site-gate.sh runs it locally. One script, so the tree a local check 18 grades is the
# tree CI deploys.
#
# Every language lands under its own <lang>/, the main language included. Each one carries its
# own images/ copy, so a language folder is a complete site on its own. The site root holds a
# redirect stub to the main language, llms.txt and robots.txt: no page, and no images/ copy.
# Each language folder also gets a sitemap.xml, and the main one a copy of llms.txt and
# robots.txt, written last.
#
# This script reads <downloaded> and never writes to it. The artifacts are the render legs'
# only output, and a second run must see what the first one saw.
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "usage: checks/assemble-site.sh <downloaded> <site> <mainlanguage> \"<langs>\"" >&2
  exit 2
fi
downloaded="$1"
site="$2"
mainlanguage="$3"
langs="$4"
repo="$(cd "$(dirname "$0")/.." && pwd)"

if [ -z "$langs" ]; then
  echo "::error::no language was given, so there is nothing to assemble" >&2
  exit 1
fi
if [ -e "$site" ]; then
  echo "::error::$site exists already. Assemble into a fresh path, so no stale page survives." >&2
  exit 1
fi

# A declared language with no artifact means a render leg produced nothing. Deploying the rest
# would drop that language from the site silently, and the switcher would still link to it.
for lang in $langs; do
  if [ ! -d "$downloaded/site-$lang" ]; then
    echo "::error::languages.yml declares '$lang', but no artifact site-$lang was downloaded" >&2
    exit 1
  fi
done

# The other direction. An artifact for a code languages.yml does not declare would publish a
# directory the switcher never links to.
mkdir -p "$site"
for dir in "$downloaded"/site-*; do
  code="$(basename "$dir")"
  code="${code#site-}"
  case " $langs " in
    *" $code "*) ;;
    *) echo "::error::artifact site-$code is not a language languages.yml declares ($langs)" >&2; exit 1 ;;
  esac
  mkdir -p "$site/$code"
  cp -a "$dir/." "$site/$code/"
done

# Every language folder is self-contained: it carries its own images/ copy, and its pages
# reach that copy relatively. No page holds a root-absolute path, so the Cloudflare rule that
# redirects root paths into /<mainlanguage>/ never sees an image request. It also makes one
# language folder a standalone site, which is what the offline zip needs.
for lang in $langs; do
  mkdir -p "$site/$lang/images"
  cp -a "$repo/images/." "$site/$lang/images"/
done

# There is deliberately NO images/ copy at the site root. Cloudflare 301s every root path into
# /<mainlanguage>/, verified against the live site on 2026-09-16:
#   /images/Applied_Epi_logo.png -> 301 -> /en/images/Applied_Epi_logo.png -> 200
# So a link that predates this layout is redirected into a language folder and served from
# that language's own copy. A root copy could never be reached.
#
# Leaving one out also makes a whole class of bug impossible rather than merely detected:
# with a root copy present, a page path with one ../ too many resolves to a real file, so it
# passes an existence check while the browser still requests /images/. Without it, that path
# resolves to nothing.

# Each page carries the ../../images/ of content/<lang>/_quarto.yaml, which is relative to
# that language's project directory. Rewrite it to a path relative to the page's OWN depth
# under <site>/<lang>/: a chapter at <site>/en/gis.html gets images/, an alias stub at
# <site>/en/new_pages/gis.en.html gets ../images/.
#
# This step only rewrites. The check is a separate step, after the switcher injection,
# because that injection is the last thing that rewrites a page.
#
# build_all_chapters.sh still writes one root images/ copy and does no rewrite, so a local
# whole-book render does not match this tree. Bringing it into line needs a new image line:
# epirhandbook#455, box F50.
python3 - "$site" "$langs" <<'PY'
import pathlib
import re
import sys

site = pathlib.Path(sys.argv[1])
langs = sys.argv[2].split()

# Any number of ../ before images/ names the shared assets folder.
# The handbook has no other directory of that name.
emitted = re.compile(r'(src|href)="(?:\./)?(?:\.\./)+images/')

rewritten = 0
for lang in langs:
    root = site / lang
    for page in root.rglob("*.html"):
        depth = len(page.relative_to(root).parts) - 1
        prefix = "../" * depth
        before = page.read_text(encoding="utf-8", errors="surrogateescape")
        after = emitted.sub(lambda m: f'{m.group(1)}="{prefix}images/', before)
        if after != before:
            page.write_text(after, encoding="utf-8", errors="surrogateescape")
            rewritten += 1
print(f"rewrote the images path on {rewritten} page(s)")
PY

# The root redirect stub, byte-for-byte what build_all_chapters.sh writes for a whole-book
# render. Four lines, and the only page at the site root.
printf '%s\n' \
  '<!DOCTYPE html>' \
  "<html lang=\"$mainlanguage\"><head><meta charset=\"utf-8\"><title>Redirect to $mainlanguage/</title>" \
  "<meta http-equiv=\"refresh\" content=\"0;URL='$mainlanguage/'\"><link rel=\"canonical\" href=\"$mainlanguage/\"></head>" \
  '<body></body></html>' \
  > "$site/index.html"

# A sitemap.xml per language, and llms.txt and robots.txt, generated from the chapter lists and
# the pages just assembled. llms.txt and robots.txt go into the root and into the main
# language's folder. checks/site-index.py carries the details.
python3 "$repo/checks/site-index.py" "$site" "$mainlanguage" "$langs"
