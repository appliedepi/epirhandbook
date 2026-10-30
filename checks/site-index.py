#!/usr/bin/env python3
"""Write a sitemap.xml per language, and llms.txt and robots.txt, for an assembled site.

Usage: python3 checks/site-index.py <site> <mainlanguage> "<langs>"

checks/assemble-site.sh runs this on the tree it assembled, so the deploy job and
checks/site-gate.sh write the same files. Nothing goes into the site root: the published host
redirects every root path into /<mainlanguage>/ (checked on 2026-10-30). So llms.txt and
robots.txt go into <site>/<mainlanguage>/ and are served at /llms.txt and /robots.txt through
that redirect.

A sitemap may list only URLs under its own folder, so each language gets its own
<site>/<lang>/sitemap.xml with its own pages, and robots.txt names every one of them.

Every value comes from the file that already holds it:

  the address         languages.yml site_url
  the pages           content/<lang>/_quarto.yaml book.chapters, in file order
  the parts           the `part:` entries of content/<main>/_quarto.yaml
  the book title      languages.yml title of the main language
  the summary         landing.yml subtitle of the main language
  the Applied Epi part landing.yml: the publisher, its description, the course line, the
                      notify line, the contact links and the service cards of the main language
  a page's title      the built page's own <title>
  a language's label  languages.yml label

A declared chapter with no built page fails the build, because a sitemap must not list a dead
page.
"""
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from langs import Unreadable, parse, read_languages, read_site_url  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def outline(path):
    """The chapters of one project file as [(part title or None, [stems])], in file order."""
    doc = parse(path)
    book = doc.get('book') if isinstance(doc, dict) and isinstance(doc.get('book'), dict) else {}
    groups = []

    def add(part, stem):
        if not groups or groups[-1][0] != part:
            groups.append((part, []))
        groups[-1][1].append(stem)

    def walk(items, part):
        for x in items if isinstance(items, list) else []:
            if isinstance(x, str) and x.endswith('.qmd'):
                add(part, x[:-len('.qmd')])
            elif isinstance(x, dict) and 'part' in x:
                title = x['part']
                if isinstance(title, str) and title.endswith('.qmd'):
                    add(title, title[:-len('.qmd')])
                walk(x.get('chapters'), title if isinstance(title, str) else None)

    walk(book.get('chapters'), None)
    return groups


def markdown(fragment):
    """One landing.yml HTML fragment as Markdown: links kept, other tags dropped."""
    text = re.sub(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', fragment, flags=re.S)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', text)).split())


def page_title(page):
    """The chapter title of one built page: its <title> before the book title, unnumbered."""
    text = page.read_text(encoding='utf-8', errors='surrogateescape')
    m = re.search(r'<title>(.*?)</title>', text, re.S)
    if not m:
        raise Unreadable('%s has no <title>, so llms.txt cannot name it.' % page)
    title = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).split(' – ')[0]
    return re.sub(r'^\d+\s+', '', ' '.join(title.split()))


def main(site, mainlang, langs):
    site = pathlib.Path(site)
    url = read_site_url(ROOT / 'languages.yml')
    _, codes = read_languages(ROOT / 'languages.yml')
    entries = {e['code']: e for e in parse(ROOT / 'languages.yml')['languages']}
    missing = [c for c in langs if c not in codes]
    if missing:
        raise Unreadable('languages.yml declares no language %s.' % ' '.join(missing))

    total = 0
    for lang in langs:
        pages = []
        for _, stems in outline(ROOT / 'content' / lang / '_quarto.yaml'):
            for stem in stems:
                if not (site / lang / (stem + '.html')).is_file():
                    raise Unreadable('content/%s/_quarto.yaml declares %s, but the assembled '
                                     'site has no %s/%s.html.' % (lang, stem, lang, stem))
                pages.append('%s/%s/%s.html' % (url, lang, stem))
        (site / lang / 'sitemap.xml').write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + ''.join('  <url><loc>%s</loc></url>\n' % html.escape(p) for p in pages)
            + '</urlset>\n', encoding='utf-8')
        total += len(pages)

    out = site / mainlang

    landing = parse(ROOT / 'landing.yml')
    strings = landing.get(mainlang, {}) if isinstance(landing, dict) else {}
    need = ['subtitle', 'np_brand', 'np_lead', 'np_trust', 'np_notify', 'np_links', 'svc']
    gone = [k for k in need if not strings.get(k)]
    if gone:
        raise Unreadable('landing.yml has no %s for %s, and llms.txt uses it.'
                         % (' '.join(gone), mainlang))
    brand = strings['np_brand']
    home = re.search(r'href="([^"]+)"', strings['np_links'])
    lines = ['# %s' % entries[mainlang]['title'], '',
             '> %s' % markdown(strings['subtitle']), '',
             'Published by [%s](%s).' % (brand, home.group(1) if home else url), '',
             markdown(strings['np_lead'].replace('{brand}', brand)), '',
             markdown(strings['np_trust']), '',
             markdown(strings['np_notify']), '',
             'Contact: %s' % markdown(strings['np_links']), '',
             '## What %s offers' % brand, '']
    cards = strings['svc'] if isinstance(strings['svc'], list) else []
    for n, c in enumerate(cards, 1):
        if not isinstance(c, dict) or not all(c.get(k) for k in ('h', 'p', 'href')):
            raise Unreadable('landing.yml: service card %d of %s lacks h, p or href, and '
                             'llms.txt lists every card.' % (n, mainlang))
    if not cards:
        raise Unreadable('landing.yml: svc of %s is not a list of cards.' % mainlang)
    lines += ['- [%s](%s): %s' % (markdown(c['h']), c['href'], markdown(c['p'])) for c in cards]
    lines.append('')
    for part, stems in outline(ROOT / 'content' / mainlang / '_quarto.yaml'):
        lines += ['## %s' % (part or 'Start here'), '']
        lines += ['- [%s](%s/%s/%s.html)' % (page_title(site / mainlang / (s + '.html')),
                                            url, mainlang, s) for s in stems]
        lines.append('')
    others = [c for c in langs if c != mainlang]
    if others:
        lines += ['## Other languages', '']
        lines += ['- [%s](%s/%s/index.html)' % (entries[c]['label'], url, c) for c in others]
        lines.append('')
    out.joinpath('llms.txt').write_text('\n'.join(lines), encoding='utf-8')

    out.joinpath('robots.txt').write_text(
        'User-agent: *\nAllow: /\n\n'
        + ''.join('Sitemap: %s/%s/sitemap.xml\n' % (url, c) for c in langs), encoding='utf-8')
    print('site-index: wrote %d sitemap.xml files (%d pages), and llms.txt and robots.txt '
          'into %s/' % (len(langs), total, mainlang))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('usage: checks/site-index.py <site> <mainlanguage> "<langs>"')
    main(sys.argv[1], sys.argv[2], sys.argv[3].split())
