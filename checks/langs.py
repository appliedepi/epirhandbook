"""Read the language list and the stem list for the checks under checks/.

`languages.yml` declares the languages, and its `main:` key names the reference language.
`content/<main>/_quarto.yaml` is the reference project file. Its `book.chapters` list is the stem
list. Checks 1 to 8 read these two files through the functions below. Checks 9 and 15 use the
loader, and check 9 also uses the walk in project().

PyYAML reads both files with `Loader`, which is `yaml.BaseLoader` that refuses a duplicate key.
BaseLoader makes every scalar a string. `yaml.safe_load` reads an unquoted `no` as False, so the
Norwegian code `no` would not survive it. PyYAML keeps the last value of a duplicate key and says
nothing, so a second `main:` would replace the first in silence.

A file this module cannot read raises `Unreadable`, which is a `SystemExit`. If no caller catches
it, the script stops with exit status 1 and one line on stderr that names the file. A caller that
needs its own words or its own exit status catches it and reads `why`.
"""
import os
import re
import sys


def prog():
    """The name of the running script, for the start of a message.

    A heredoc run as `python3 -` has no script name, so the message names this module.
    """
    name = sys.argv[0] if sys.argv else ''
    return os.path.basename(name) if name not in ('', '-', '-c') else 'checks/langs.py'


try:
    import yaml
except ImportError:
    sys.exit('%s: no PyYAML. The checks read languages.yml and the project files with it. '
             'Install it with `sudo apt-get install -y python3-yaml`, or `pip install pyyaml`.'
             % prog())


class Unreadable(SystemExit):
    """One input file that this module cannot read. `why` is one sentence that names the file."""

    def __init__(self, why):
        self.why = why
        super().__init__('%s: %s' % (prog(), why))


class NoDuplicates:
    """A loader mixin that refuses a mapping with a duplicate key."""

    def construct_mapping(self, node, deep=False):
        # Compare the key nodes by tag and text, before construction. A merge key `<<` is
        # skipped, because SafeLoader expands it later. Comparing constructed values would
        # also treat the keys `true` and `1` as one key.
        seen = set()
        for k, _ in node.value:
            if not isinstance(k, yaml.ScalarNode) or k.tag == 'tag:yaml.org,2002:merge':
                continue
            if (k.tag, k.value) in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, 'duplicate key %s' % k.value, k.start_mark)
            seen.add((k.tag, k.value))
        return super().construct_mapping(node, deep)


class Loader(NoDuplicates, yaml.BaseLoader):
    """yaml.BaseLoader that refuses a duplicate key. Every scalar stays a string."""


def parse(path):
    """The YAML document in one file, parsed with Loader.

    Raises Unreadable when the file cannot be read or does not parse. The message names the
    file, and the line when PyYAML reports one.
    """
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable('%s cannot be read: %s' % (path, e)) from None
    try:
        return yaml.load(text, Loader=Loader)
    except yaml.YAMLError as e:
        mark = getattr(e, 'problem_mark', None)
        at = ', line %d' % (mark.line + 1) if mark else ''
        why = getattr(e, 'problem', None) or str(e)
        raise Unreadable('%s does not parse as YAML%s: %s'
                         % (path, at, ' '.join(why.split()))) from None


def read_languages(path):
    """The main code and the declared codes of one languages.yml: (main, codes).

    codes holds every `code:` of the `languages:` list, in file order, main included. Raises
    Unreadable when the file is missing, does not parse, or declares no `main:` or no code. It
    also raises when an entry has no code, when a code is not 2 or 3 lowercase letters, when
    a code repeats, or when `main:` is not one of the codes. A code names a folder and a site
    path, and the build accepts only that shape, so a narrower list here would check a
    different set of languages from the one that ships.
    """
    if not os.path.isfile(path):
        raise Unreadable('no %s. That file is the one declaration of which languages ship.'
                         % path)
    doc = parse(path)
    doc = doc if isinstance(doc, dict) else {}
    main = doc.get('main')
    if not isinstance(main, str) or not main:
        raise Unreadable('%s declares no main: language, and that language names the '
                         'reference project file.' % path)
    entries = doc.get('languages')
    entries = entries if isinstance(entries, list) else []
    if not entries:
        raise Unreadable('%s declares no language. An empty list would check nothing and '
                         'report a clean tree.' % path)
    codes = []
    for n, e in enumerate(entries, 1):
        code = e.get('code') if isinstance(e, dict) else None
        if not isinstance(code, str) or not re.fullmatch(r'[a-z]{2,3}', code):
            raise Unreadable('%s: languages item %d has code %r. A code is 2 or 3 lowercase '
                             'letters.' % (path, n, code))
        if code in codes:
            raise Unreadable('%s declares the code %s twice.' % (path, code))
        codes.append(code)
    if main not in codes:
        raise Unreadable('%s: main: %s is not one of the declared codes %s.'
                         % (path, main, ' '.join(codes)))
    return main, codes


def read_stems(path):
    """The stems of one Quarto project file, in file order.

    The list is the first item that project() returns. Raises Unreadable when the file is
    missing, does not parse, or declares no chapter. An empty list would check nothing and
    report a clean tree.
    """
    if not os.path.isfile(path):
        raise Unreadable('no %s. That project file holds the stem list, in book.chapters.'
                         % path)
    stems = project(parse(path))[0]
    if not stems:
        raise Unreadable('%s declares no chapter in book.chapters.' % path)
    return stems


def project(doc):
    """One parsed project file: (stems in order, part count, lang, book title).

    The stems are the `.qmd` entries of `book.chapters`, in file order. A part is a mapping
    with a `part:` key, and its own `chapters:` list gives its stems in its place. A part may
    name a `.qmd` file instead of a title. Quarto renders that file as the part page, so it is
    a stem too, and it comes before the part's chapters.
    """
    doc = doc if isinstance(doc, dict) else {}
    book = doc.get('book') if isinstance(doc.get('book'), dict) else {}
    stems, parts = [], 0

    def walk(items):
        nonlocal parts
        for x in items if isinstance(items, list) else []:
            if isinstance(x, str) and x.endswith('.qmd'):
                stems.append(x[:-len('.qmd')])
            elif isinstance(x, dict):
                if 'part' in x:
                    parts += 1
                    if isinstance(x['part'], str) and x['part'].endswith('.qmd'):
                        stems.append(x['part'][:-len('.qmd')])
                walk(x.get('chapters'))

    walk(book.get('chapters'))
    lang, title = doc.get('lang'), book.get('title')
    return (stems, parts,
            lang if isinstance(lang, str) else '',
            title if isinstance(title, str) else '')
