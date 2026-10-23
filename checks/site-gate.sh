#!/bin/bash
# Run check 18 locally, on a site assembled the way the deploy job assembles it.
#
# Usage: checks/site-gate.sh <lang>=<render output> [<lang>=<render output> ...]
#   e.g. checks/site-gate.sh en=html_outputs jp=content/jp/html_outputs
#
# The deploy job assembles every language with checks/assemble-site.sh, injects the language
# switcher with inject_language_links.sh, and only then runs check 18
# (checks/check-site-links.py). A local render holds one language or a few, so the switcher
# that languages.yml describes would link to languages that are not there, and check 18 would
# fail on links the deploy never has. This script injects the switcher for the languages you
# give, and no others, by handing the injector a languages.yml with only those entries.
#
# It needs docker and the book's common image, which carries the injector and R's yaml
# package. The image is the registry of docker-images.yml with the tag of its index row.
#
# The assembled site stays in a temporary folder, printed at the end, for inspection.
# Exit 0 when check 18 passes, 1 when it fails, 2 on a usage or input error.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
if [ "$#" -lt 1 ]; then
  echo "usage: checks/site-gate.sh <lang>=<render output> [<lang>=<render output> ...]" >&2
  exit 2
fi

registry="$(sed -n 's/^registry: *//p' "$repo/docker-images.yml")"
tag="$(awk '/- stem: index$/ {getline; print; exit}' "$repo/docker-images.yml" | sed 's/.*://')"
if [ -z "$registry" ] || [ -z "$tag" ]; then
  echo "site-gate: docker-images.yml gives no registry or no image tag for the index row" >&2
  exit 2
fi
image="$registry/epirhandbook-common:$tag"

work="$(mktemp -d)"
mkdir -p "$work/downloaded"
langs=""
for pair in "$@"; do
  lang="${pair%%=*}"
  dir="${pair#*=}"
  if [ "$lang" = "$pair" ] || [ ! -d "$dir" ]; then
    echo "site-gate: '$pair' is not <lang>=<an existing render output folder>" >&2
    exit 2
  fi
  case " $langs " in *" $lang "*)
    echo "site-gate: '$lang' is given twice" >&2; exit 2 ;; esac
  if ! grep -q "^  - code: $lang\$" "$repo/languages.yml"; then
    echo "site-gate: languages.yml declares no language '$lang'" >&2
    exit 2
  fi
  cp -a "$dir/." "$work/downloaded/site-$lang/"
  langs="$langs $lang"
done
langs="${langs# }"

main="$(sed -n 's/^main: *//p' "$repo/languages.yml")"
case " $langs " in *" $main "*) ;; *) main="${langs%% *}" ;; esac

"$repo/checks/assemble-site.sh" "$work/downloaded" "$work/site" "$main" "$langs"

# With one language there is nothing to switch to, and the injector stops because it modified
# no page. The deploy always has every language, so this case only happens locally.
if [ "$langs" = "$main" ]; then
  echo "site-gate: one language, so no switcher is injected"
  echo "site-gate: assembled $langs in $work/site"
  exec python3 "$repo/checks/check-site-links.py" "$work/site"
fi

cp "$repo/languages.yml" "$work/languages.full.yml"
docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$work:/work" -w /work "$image" \
  Rscript -e 'a <- commandArgs(TRUE); y <- yaml::read_yaml("languages.full.yml");
    keep <- strsplit(a[2], " ")[[1]]; y$main <- a[1];
    y$languages <- Filter(function(l) l$code %in% keep, y$languages);
    yaml::write_yaml(y, "languages.yml")' "$main" "$langs"

docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$work/site:/site" -v "$work/languages.yml:/quarto/languages.yml:ro" \
  -w /site "$image" inject_language_links.sh /site /quarto/languages.yml

echo "site-gate: assembled and injected $langs in $work/site"
python3 "$repo/checks/check-site-links.py" "$work/site"
