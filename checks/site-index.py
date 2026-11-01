#!/usr/bin/env python3
"""Write a sitemap.xml per language, and llms.txt and robots.txt, for an assembled site.

Usage: python3 checks/site-index.py <site> <mainlanguage> "<langs>"

checks/assemble-site.sh runs this on the tree it assembled, so the deploy job and
checks/site-gate.sh write the same files. llms.txt and robots.txt go into the site root, where
a crawler looks for them. A copy of each also goes into <site>/<mainlanguage>/, because
epirhandbook.com redirects every root path into /<mainlanguage>/ (checked on 2026-10-30) and
serves them from there.

A sitemap may list only URLs under its own folder, so each language gets its own
<site>/<lang>/sitemap.xml with its own pages, and robots.txt names every one of them.

`website: llms-txt: true` in each content/<lang>/_quarto.yaml makes Quarto write a Markdown
copy of every page, <lang>/<stem>.llms.md, and a llms.txt. On a single-chapter render Quarto
writes llms.txt only when it is absent, and lists only that chapter. So the image's
build_one_chapter.sh moves it to <lang>/llms-parts/<stem>.txt after each render. This script
joins the main language's parts into one llms.txt: Quarto's header (the book title and
website.description) and Quarto's entry for each chapter, in chapter order under the part
headings, with the chapter-number markup removed. It then deletes every llms-parts/ folder.

Every value comes from the file that already holds it:

  the address         languages.yml site_url
  the pages           content/<lang>/_quarto.yaml book.chapters, in file order
  the parts           the `part:` entries of content/<main>/_quarto.yaml
  the top of llms.txt Quarto's header in llms-parts/<first stem>.txt, which holds
                      website.description of content/<main>/_quarto.yaml
  a page's entry      Quarto's entry in llms-parts/<stem>.txt
  a language's label  languages.yml label

A declared chapter with no built page, no Markdown copy or no saved llms.txt part fails the
build, because a sitemap or llms.txt must not list a dead page or miss a live one.
"""
import html
import pathlib
import re
import shutil
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


def llms_entry(path, prefix):
    """The one page entry of a llms.txt that Quarto wrote for one render, cleaned.

    Quarto writes a numbered chapter as `- [[2]{.chapter-number}  [Title]{.chapter-title}](x)`,
    and a chapter whose heading has an id wraps that in `[...]{#id .quarto-section-identifier}`.
    No Markdown reader parses either as one link. The number goes, every `[text]{attributes}`
    span becomes its text, and the entry becomes `- [Title](<prefix>/x)`.
    """
    pages = path.read_text(encoding='utf-8').rpartition('\n## Pages\n')[2]
    found = [l for l in pages.splitlines() if l.startswith('- [')]
    if len(found) != 1:
        raise Unreadable('%s holds %d page entries. Quarto writes one per render.'
                         % (path, len(found)))
    m = re.fullmatch(r'- \[(.*)\]\(([^()]+)\)', found[0])
    if not m:
        raise Unreadable('%s: the entry %r is not a Markdown link.' % (path, found[0]))
    title, href = m.groups()
    if href != path.stem + '.llms.md':
        raise Unreadable('%s links to %s, not to %s.llms.md.' % (path, href, path.stem))
    title = re.sub(r'\[[^\[\]]*\]\{\.chapter-number[^{}]*\}\s*', '', title)
    while True:
        unwrapped = re.sub(r'\[([^\[\]]*)\]\{[^{}]*\}', r'\1', title)
        if unwrapped == title:
            break
        title = unwrapped
    if re.search(r'\]\{|\{[.#]', title):
        raise Unreadable('%s: the entry title %r still holds Pandoc markup.' % (path, title))
    return '- [%s](%s/%s)' % (title, prefix, href)


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
                for ext in ('.html', '.llms.md'):
                    if not (site / lang / (stem + ext)).is_file():
                        raise Unreadable('content/%s/_quarto.yaml declares %s, but the assembled '
                                         'site has no %s/%s%s.' % (lang, stem, lang, stem, ext))
                pages.append('%s/%s/%s.html' % (url, lang, stem))
        (site / lang / 'sitemap.xml').write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + ''.join('  <url><loc>%s</loc></url>\n' % html.escape(p) for p in pages)
            + '</urlset>\n', encoding='utf-8')
        total += len(pages)

    groups = outline(ROOT / 'content' / mainlang / '_quarto.yaml')
    parts = site / mainlang / 'llms-parts'
    for _, stems in groups:
        for s in stems:
            if not (parts / (s + '.txt')).is_file():
                raise Unreadable('the assembled site has no %s/llms-parts/%s.txt. The image\'s '
                                 'build_one_chapter.sh saves one after each chapter render.'
                                 % (mainlang, s))
    first = parts / (groups[0][1][0] + '.txt')
    head, pages, _ = first.read_text(encoding='utf-8').rpartition('\n## Pages\n')
    if not pages or not head.startswith('# '):
        raise Unreadable('%s does not hold the book title and a "## Pages" list.' % first)
    lines = [head.rstrip(), '']
    for part, stems in groups:
        lines += ['## %s' % (part or 'Start here'), '']
        lines += [llms_entry(parts / (s + '.txt'), '%s/%s' % (url, mainlang)) for s in stems]
        lines.append('')
    others = [c for c in langs if c != mainlang]
    if others:
        lines += ['## Other languages', '']
        lines += ['- [%s](%s/%s/index.html)' % (entries[c]['label'], url, c) for c in others]
        lines.append('')
    robots = ('User-agent: *\nAllow: /\n\n'
              + ''.join('Sitemap: %s/%s/sitemap.xml\n' % (url, c) for c in langs))
    for out in (site, site / mainlang):
        out.joinpath('llms.txt').write_text('\n'.join(lines), encoding='utf-8')
        out.joinpath('robots.txt').write_text(robots, encoding='utf-8')
    for lang in langs:
        shutil.rmtree(site / lang / 'llms-parts', ignore_errors=True)
    print('site-index: wrote %d sitemap.xml files (%d pages), and llms.txt and robots.txt '
          'into the site root and %s/' % (len(langs), total, mainlang))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('usage: checks/site-index.py <site> <mainlanguage> "<langs>"')
    main(sys.argv[1], sys.argv[2], sys.argv[3].split())
