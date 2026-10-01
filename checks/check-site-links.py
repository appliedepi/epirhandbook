#!/usr/bin/env python3
"""Fail when a page of the assembled site links to a file or a fragment that does not exist.

Check 18. It runs in the assemble-deploy job of `.github/workflows/build-deploy.yml`, after the
language switcher injection, which is the last step that changes a page.

The check reads every `href` and `src` attribute of every `.html` file under the site folder.
It uses Python's html.parser, so text inside a <script> element is not an attribute and is not
read. A JavaScript template such as `' + logoSrc + '` or `${href}` is therefore never a link.

It skips a value with a URL scheme, such as `https:`, `mailto:`, `javascript:` or `data:`, and
a value that starts with `//`. Every other value is a path. A path that starts with `/` resolves
from the site folder, and any other path resolves from the folder of its page. The check fails on
each of these:

1. A path that resolves to no file. A folder counts as its index.html. File names compare with
   exact case, as on the Linux host that serves the site.
2. A path that resolves outside the site folder.
3. A `#fragment` that no element of the target page carries as its id. This holds for a
   fragment on the same page and on another page. A `name` attribute does not count, and
   neither does `#top` without an element whose id is `top`. An empty fragment, such as
   `href="#"`, needs no element, because the HTML standard scrolls it to the top.
4. A page with a <base> element, because it changes how every path on that page resolves.

Exit 0 when every link resolves, 1 when one does not, and 2 when the site folder is missing or
holds no page.

Usage: python3 checks/check-site-links.py <site dir>
"""
import os
import re
import sys
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

SCHEME = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:')


def die(msg):
    print('check-site-links: %s' % msg, file=sys.stderr)
    sys.exit(2)


class Page(HTMLParser):
    """Collect the href and src values, the ids and the <base> elements of one page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.base = [], set(), False

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is None:
                continue
            if name in ('href', 'src'):
                self.refs.append((tag, name, value, self.getpos()[0]))
            if name == 'id':
                self.ids.add(value)
        if tag == 'base':
            self.base = True

    handle_startendtag = handle_starttag


@lru_cache(maxsize=None)
def listing(folder):
    """The exact names in a folder, or an empty set when it is not a folder."""
    try:
        return frozenset(os.listdir(folder))
    except OSError:
        return frozenset()


def exists_exact(path, root):
    """True when every part of path below root is in its parent folder with this exact case."""
    current = root
    for part in path.relative_to(root).parts:
        if part not in listing(str(current)):
            return False
        current = current / part
    return True


def main(argv):
    if len(argv) != 1:
        die('expected 1 argument. Usage: %s' % __doc__.strip().split('Usage: ')[1])
    site = Path(argv[0])
    if not site.is_dir():
        die('%s is not a directory. It is the assembled site.' % site)
    site = site.resolve()
    pages = sorted(site.rglob('*.html'))
    if not pages:
        die('%s holds no .html file.' % site)

    parsed = {}

    def parse(page):
        if page not in parsed:
            p = Page()
            p.feed(page.read_text(encoding='utf-8', errors='replace'))
            p.close()
            parsed[page] = p
        return parsed[page]

    failures, checked = [], 0
    for page in pages:
        shown = page.relative_to(site)
        p = parse(page)
        if p.base:
            failures.append('%s: a <base> element, which this check does not resolve' % shown)
            continue
        for tag, attr, value, line in p.refs:
            value = value.strip()
            if not value or value.startswith('//') or SCHEME.match(value):
                continue
            checked += 1
            where = '%s line %d: <%s %s="%s">' % (shown, line, tag, attr, value)
            path, _, fragment = value.partition('#')
            path = unquote(path.split('?', 1)[0])
            if not path:
                target = page
            else:
                base = site if path.startswith('/') else page.parent
                target = Path(os.path.normpath(base / path.lstrip('/')))
                if target != site and site not in target.parents:
                    failures.append('%s resolves outside the site folder' % where)
                    continue
                if target.is_dir() and exists_exact(target, site):
                    target = target / 'index.html'
                if not (target.is_file() and exists_exact(target, site)):
                    failures.append('%s resolves to %s, which does not exist'
                                    % (where, target.relative_to(site)))
                    continue
            if not fragment or target.suffix != '.html':
                continue
            ids = parse(target).ids
            if fragment not in ids and unquote(fragment) not in ids:
                failures.append('%s: %s has no element with id "%s"'
                                % (where, target.relative_to(site), unquote(fragment)))

    for f in failures:
        print(f)
    print('site links: %d page(s), %d relative reference(s), %d failure(s)'
          % (len(pages), checked, len(failures)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
