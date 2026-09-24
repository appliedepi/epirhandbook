#!/usr/bin/env python3
"""The landing page gate: every language resolves its strings, its theme and its slots.

`landing.yml` is a second copy of the language list, and nothing else measures it.

Four inputs:

  languages.yml               the one declaration of which languages ship
  landing.yml                 one string block per language code
  utils/landing-hero.R        the only consumer, which names every key it reads
  content/<code>/_quarto.yaml the project file, one per declared language

Nine static rules, in the default run:

 1. Every code `languages.yml` declares has a block in `landing.yml`.
 2. Every block in `landing.yml` names a code `languages.yml` declares.
 3. The `en` block declares every key `utils/landing-hero.R` reads, and the hero
    reads every key the `en` block declares. English is the fallback of last resort,
    so a key absent there stops the render. A key nothing reads is dead configuration.
 4. Every key a translated block declares also exists under `en`.
 5. No value is an empty string. Omit the key instead, and the value falls back.
 6. No translated value is byte-identical to the English value for that key.
 7. No two languages give one key the same value.
10. Every translated block declares every translatable key.

Rule 7 is the pairwise rule, and it walks all 28 ordered pairs of the 8 languages.
Rule 6 compares each language against English alone. So rule 6 cannot see a language
that carries a THIRD language's text. A French block set to the Spanish values passed
rule 6 byte for byte. Rule 7 takes two exclusions, and both were measured on 2026-09-18.
A service-card href is one string in every language by design, and Spanish and
Portuguese spell two of the stat labels identically. Rule 6 takes the href exclusion
for the same reason, and takes no other. Both name the FIELD and the shape: a
URL-shaped value under any other key is one language carrying another's text.

Rule 10 is the completeness rule, and it closes the hole the other seven leave:

10. Every translated block declares every translatable key, or a pinned entry in
    OMISSIONS says why it does not.

A translatable key is one the hero reads and that INVARIANT does not name. Replace one
block with `fr: {}` and rules 1 to 7 all hold. Every key it declares exists under `en`,
no value is empty, and no value matches another language, because it declares nothing.
The declared key count falls from 166 to 142 and nothing else moves. That is how all
eight heroes shipped in English after the tagline was removed. Rule 10 names the
language and each key it lost.

Three omissions stay legal, and a rule that rejected every omission would be no fix. A
key INVARIANT names is not asked for, so a URL or a brand name never fires. An omission
OMISSIONS pins is allowed, and the entry carries its reason. The hero still falls back
to English for both, so the page renders either way. Every other omission is a fault,
whether the block lost one key or all of them.

Rule 8 is about the page rather than the strings:

8. Every `content/<code>/_quarto.yaml` names `../../ael-extras.html` in
   `include-after-body`, and names both token layers and `../../theme-ael.scss` in
   `theme.light` and in `theme.dark`.

`theme-ael.scss` hides the sidebar search box and the colour-scheme toggle from CSS,
with no condition on it. `ael-extras.html` is what puts both back, in the top app bar.
So a language that does not include it ships with no search box and no dark-mode
toggle, and the render reports nothing.

Rule 9 needs a rendered page, so `--slots` asks for it:

9. Every hero and band slot on every translated page carries the value its source gives
   for it. The English fallback counts. So do the three slots `landing.yml` does not
   key: the hero title, the chapter count and the language count.

A number here names a rule, never the order it runs in. Rule 10 is static and rule 9
needs a render, because rule 10 was written last.

Run `--slots` after `quarto render index.qmd --to html` in each language folder. It
refuses to run when a rendered page is absent. A check that passes because it found no
input reports a success it never measured.

Usage: python3 checks/check-landing-strings.py [--summary] [--slots]
Exit 0 when every rule holds, 1 on any problem.
"""
import itertools
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("check-landing-strings.py: no PyYAML. This check reads landing.yml and "
             "languages.yml with yaml.safe_load. Only a real YAML parser separates the string "
             "\"3\" from the number 3, and rule 4 rejects a value that is not a string. "
             "Install it with `sudo apt-get install -y python3-yaml`, or `pip install pyyaml`.")

ARGS = sys.argv[1:]
USAGE = ("Usage: check-landing-strings.py [--summary] [--slots] "
         "[--pages <template>] [--only <code>]")
TAKES_VALUE = ('--pages', '--only')
opt = {}
i = 0
while i < len(ARGS):
    a = ARGS[i]
    if a in TAKES_VALUE:
        if i + 1 >= len(ARGS):
            sys.exit("%s needs a value. %s" % (a, USAGE))
        opt[a] = ARGS[i + 1]
        i += 2
        continue
    if a not in ('--summary', '--slots'):
        sys.exit("unknown argument %s. %s" % (a, USAGE))
    opt[a] = True
    i += 1
summary = '--summary' in opt
want_slots = '--slots' in opt
# Where a rendered landing page is. {code} is the language code. The render leg of
# .github/workflows/build-deploy.yml renders one language to the root of its output
# directory. It passes a template with no {code} and names the language with --only.
PAGES = opt.get('--pages', 'content/{code}/html_outputs/index.html')
ONLY = opt.get('--only')
for a in TAKES_VALUE:
    if a in opt and not want_slots:
        sys.exit("%s only means something with --slots, and --slots is not set. %s" % (a, USAGE))

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The href rule for rules 6 and 7. A service-card href is the same string in every
# language, because it points at one page of appliedepi.org. The exclusion names the FIELD
# as well as the shape. It matched any URL-shaped value until 2026-09-18. Two languages
# sharing a URL under any other key were exempted in silence. The gate applied an exclusion
# wider than the one it documented.
HREF = re.compile(r'^svc\[\d+\]\.href$')
URL = re.compile(r'^(https?://|mailto:)')


def shared_href(key, value):
    """True when the key is a service-card href and the value is the URL it holds."""
    return bool(HREF.match(key) and URL.match(value))


# The cognate allowlist for the pairwise check. Spanish and Portuguese spell these two
# words identically, so an identical value here is not a copy of one language by another.
# Each entry pins the key, the exact ordered language pair AND the exact value. The pinned
# value stops the entry masking any other string. Edit the Spanish word and the entry stops
# matching, so the check fires again.
COGNATES = {
    ("stat_chapters_label", ("es", "pt"), "capítulos"),
    ("stat_languages_label", ("es", "pt"), "idiomas"),
}

# Rule 10 asks every translated block for every key the hero reads, less these. Each one is
# language-invariant: a path, a URL, a brand name, or a line built out of the two. A
# translation of any of them would be the same string. So no block declares one, and the
# hero falls back to English on every page.
#
# This tuple is the whole of what rule 10 does not ask for, so read it as the exemption it
# is. Add a key here and seven landing pages may ship that string in English, with nothing
# left to report it.
INVARIANT = ('btn_start_href', 'btn_offline_href', 'np_brand', 'np_btn', 'np_btn_href',
             'np_links')

# The omission allowlist for rule 10. Each entry pins the key, the ONE language, and why
# that language leaves the key to the English fallback. An entry weakens the gate for one
# key of one block and nothing else.
#
# A stale entry is a hole, so the gate names one. Declare the key again and the entry stops
# matching anything. Rule 10 then reports the entry, and exempts nothing in silence.
OMISSIONS = (
    ("stat_used_num", "es",
     'the pre-plan page reads "3 millón de veces", which is a number-agreement error'),
    ("stat_used_num", "pt",
     'the pre-plan page reads "3 milhão de vezes", which is a number-agreement error'),
)

# The four fields of one service card, in the order utils/landing-hero.R writes them into
# the markup. The slot rule reads the rendered card with these names.
CARD = ('h', 'p', 'href', 'link')

# The number of service cards the band writes on every page. utils/landing-hero.R writes one
# card per entry of the svc list. Pinning the number here is what holds the expected slot
# total still. A total derived from the English list would move with the data. A MATCHED
# reduction of English and a translation would lower the expectation, and the run would then
# pass on fewer slots.
# Add a fourth card to landing.yml and this constant is the one place that changes.
CARDS = 3

# Every scalar slot rule 9 reads out of a rendered page, one value each, in the order
# utils/landing-hero.R writes them. 18 of them are landing.yml keys and 3 are not. The
# expected slot total is the count of this tuple plus the count of CARD times CARDS. So a
# slot added to the markup must be added here, or the total stops matching.
#
# The tuple covered 12 slots until 2026-09-18. It read neither button target, neither
# computed count, the hero title nor four of the six nonprofit-band fields. Every one of
# those is a rendered slot, and `slots read:` counted none of them. The count was honest
# and the coverage was narrower than "transport is verified" implies. Rule 10 now asks the
# hero for its key list and names any key this tuple omits.
SCALAR_SLOTS = ('eyebrow', 'hero_title', 'subtitle', 'search_placeholder', 'search_label',
                'btn_start_href', 'btn_start', 'btn_offline_href', 'btn_offline',
                'stat_used_num', 'stat_used_label', 'stat_chapters_num',
                'stat_chapters_label', 'stat_languages_num', 'stat_languages_label',
                'np_brand', 'np_lead', 'np_trust', 'np_btn_href', 'np_btn', 'np_links')

# The three slots landing.yml does not key. Each already has one home, and a second copy of
# it is the thing that drifts. So rule 9 reads each one from its own home:
#   hero_title           languages.yml, the title of this language
#   stat_chapters_num    content/<main>/_quarto.yaml, book.chapters less NOT_CHAPTERS
#   stat_languages_num   languages.yml, the count of declared codes
# utils/landing-hero.R counts the same three the same way.
COMPUTED_SLOTS = ('hero_title', 'stat_chapters_num', 'stat_languages_num')

# The book pages the hero does not count as chapters. utils/landing-hero.R names the same
# three, and a fourth page added there must be added here too.
NOT_CHAPTERS = ('index', 'about', 'acknowledgements')

# The theme wiring every content/<code>/_quarto.yaml must carry. Each entry is a dotted key
# path in that file, the values the path must hold, and what a reader loses without them.
# theme-ael.scss hides the sidebar search box and the colour-scheme toggle with
# `display: none !important`, from CSS and with no condition on it. ael-extras.html is the
# file that puts both back, in the top app bar.
#
# The path is the point. Quarto reads these keys under format.html and nowhere else. A value
# parked under book:, or under a stray top-level key, satisfies a grep of the file and
# changes nothing. Name the VALUE too, never the key alone. On 2026-09-18
# every project file named theme-dark.scss on its own. So a `--brand` or `Spectral` probe
# stayed green while the language was un-wired from theme-ael.scss.
WIRING = (
    ('format.html.include-after-body', ['../../ael-extras.html'],
     'so this language ships with no search box and no colour-scheme toggle'),
    ('format.html.theme.light', ['../../theme-light.scss', '../../theme-ael.scss'],
     'so this language renders light mode without that layer'),
    ('format.html.theme.dark', ['../../theme-dark.scss', '../../theme-ael.scss'],
     'so this language renders dark mode without that layer'),
)


def flat(block, code, problems):
    """Every string one block declares, with `svc` flattened to `svc[i].field`.

    A value of any other type is a NAMED failure here, never a silent omission. The hero
    writes each of these into the page as text, so `btn_start: []` reaches the reader as a
    rendering of an empty list. A reader that drops such a value hides it from rules 4 to 7,
    and the gate's blind spot is whatever it declines to look at.
    """
    out = {}
    for k, v in sorted((block or {}).items()):
        if k == 'svc':
            if not isinstance(v, list):
                continue            # the svc rules below name a malformed svc
            for i, card in enumerate(v, 1):
                if not isinstance(card, dict):
                    problems.append("%s: svc card %d is %r, and the hero reads four named "
                                    "fields from each card" % (code, i, card))
                    continue
                for field, s in sorted(card.items()):
                    if isinstance(s, str):
                        out['svc[%d].%s' % (i, field)] = s
                    else:
                        problems.append("%s: key 'svc[%d].%s' is %r, and the hero writes that "
                                        "field into the page as text" % (code, i, field, s))
            continue
        if isinstance(v, str):
            out[k] = v
        else:
            problems.append("%s: key '%s' is %r, and the hero writes that value into the page "
                            "as text" % (code, k, v))
    return out


def check_cards(code, cards, problems):
    """One block's svc list, against the pinned shape: CARDS cards, each carrying CARD."""
    if len(cards) != CARDS:
        problems.append("%s: svc declares %d cards, and the band writes %d on every page"
                        % (code, len(cards), CARDS))
    for i, card in enumerate(cards, 1):
        if not isinstance(card, dict):
            continue                # flat() names it
        if set(card) != set(CARD):
            problems.append("%s: svc card %d declares the fields %s, and the hero reads %s"
                            % (code, i, sorted(card), sorted(CARD)))
        for field in CARD:
            v = card.get(field)
            if isinstance(v, str) and not v.strip():
                problems.append("%s: svc card %d gives '%s' an empty string, and the hero "
                                "writes that field into the page" % (code, i, field))


def project_paths(doc):
    """Every mapping key of a Quarto project file, as a dotted path to the list it holds.

    doc is the file as yaml.safe_load returns it. A grep cannot answer the question rule 8
    asks. `include-after-body` under `book:` satisfies a grep of the file, and Quarto ignores
    it. So the walk records the path each key sits at in the parsed mappings.

    A value is returned as a list in every case. A sequence gives its items, a mapping or an
    empty value gives an empty list, and any other scalar gives a one-item list. A key inside
    a sequence item has no dotted path, so the walk does not go into a sequence.
    """
    out = {}

    def walk(node, prefix):
        for key, value in node.items():
            path = prefix + str(key)
            if isinstance(value, dict):
                out[path] = []
                walk(value, path + '.')
            elif isinstance(value, list):
                out[path] = value
            else:
                out[path] = [] if value is None else [value]

    if isinstance(doc, dict):
        walk(doc, '')
    return out


def need(path, why):
    """Stop with one sentence when a required input is absent."""
    if not path.is_file():
        sys.exit("check-landing-strings.py: no %s. %s" % (path, why))
    return path


class NoDuplicates:
    """A loader mixin that refuses a mapping with a duplicate key.

    PyYAML keeps the last value of a duplicate key and says nothing, so a second block for
    one language would silently replace the first.
    """

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


class Loader(NoDuplicates, yaml.SafeLoader):
    """The loader for landing.yml and the project files."""


class Strings(NoDuplicates, yaml.BaseLoader):
    """The loader for languages.yml: every scalar stays a string.

    yaml.safe_load reads an unquoted `no` as False. The Norwegian code `no` would then drop
    out of the code list, and every rule would pass without measuring that language.
    """


def load(path, loader=None):
    """One YAML file, or one sentence naming THAT file.

    The handler read both files under one `try` until 2026-09-18, and its message named
    landing.yml whichever file had failed. A parse error in languages.yml sent the reader
    to the wrong file.
    """
    try:
        return yaml.load(path.read_text(encoding='utf-8'), Loader=loader or Loader)
    except yaml.YAMLError as e:
        sys.exit("check-landing-strings.py: %s does not parse as YAML: %s"
                 % (path, str(e).replace('\n', ' ')))


need(ROOT / 'languages.yml',
     "That file is the one declaration of which languages ship, and this check needs the "
     "code list to know which landing blocks to expect.")
need(ROOT / 'landing.yml',
     "That file holds every string the landing hero and the nonprofit band show.")
need(ROOT / 'utils' / 'landing-hero.R',
     "That file is the only consumer of landing.yml, and it names every key the hero reads.")

langs_doc = load(ROOT / 'languages.yml', Strings)
landing = load(ROOT / 'landing.yml')
for path, doc in ((ROOT / 'languages.yml', langs_doc), (ROOT / 'landing.yml', landing)):
    if not isinstance(doc, dict):
        sys.exit("check-landing-strings.py: %s is not a mapping at its top level. This check "
                 "reads it by key, so it cannot measure a file of another shape." % path)

entries = langs_doc.get('languages') or []
codes = [e.get('code') for e in entries if isinstance(e, dict) and e.get('code')]
main = langs_doc.get('main')
if not codes:
    sys.exit("check-landing-strings.py: %s declares no language. An empty code list would "
             "match an empty landing.yml and report agreement." % (ROOT / 'languages.yml'))
if main not in codes:
    sys.exit("check-landing-strings.py: %s declares main: %r, which is not one of its own "
             "codes. The fallback language must be one that ships."
             % (ROOT / 'languages.yml', main))

hero_text = (ROOT / 'utils' / 'landing-hero.R').read_text(encoding='utf-8')
required = sorted(set(re.findall(r's\("([A-Za-z0-9_]+)"\)', hero_text)))
if not required:
    sys.exit("check-landing-strings.py: %s names no s(\"key\") call, so this check cannot "
             "tell which keys the hero reads. Read the file, then repair the check or the "
             "hero." % (ROOT / 'utils' / 'landing-hero.R'))

problems = []
translated = [c for c in codes if c != main]
en = landing.get(main) or {}
# One flattening per declared block. flat() NAMES a malformed value, so flattening the same
# block twice would report the same fault twice.
F = {c: flat(landing.get(c), c, problems) for c in codes}
en_flat = F[main]

# Rule 1 and rule 2: the code list and the block list are the same set.
for c in codes:
    if not isinstance(landing.get(c), dict):
        problems.append("languages.yml declares '%s', landing.yml has no block for it, so that "
                        "landing page is English with nothing to report it" % c)
for k in landing:
    if k not in codes:
        problems.append("landing.yml carries a block '%s', languages.yml declares no such code" % k)

# Rule 3: English is the fallback of last resort, so it declares every key the hero reads.
for k in required:
    if k not in en_flat:
        problems.append("the '%s' block declares no '%s', and the hero reads that key on every "
                        "page, so the render stops" % (main, k))
en_cards = en.get('svc')
if not isinstance(en_cards, list) or not en_cards:
    problems.append("the '%s' block declares no svc list, and the hero reads one on every page"
                    % main)
    en_cards = []
else:
    check_cards(main, en_cards, problems)

# Rule 3b: no English value is an empty string. English is the fallback of last resort, so an
# empty value there reaches every page that does not declare the key. That is worse than an
# empty value in one language, and rule 5 alone cannot see it.
for k, v in sorted(en_flat.items()):
    if not v.strip():
        problems.append("the '%s' block: key '%s' is an empty string, and it is the fallback of "
                        "last resort, so every page that omits the key shows nothing"
                        % (main, k))

# Rule 3c: the mirror of rule 3, and rule 3 is blind to what it catches. Rule 3 runs the hero's
# keys to `en` and names the ones `en` does not declare. Nothing ran `en` to the hero, so a key
# under `en` that no code reads met no rule at all. `donate_label` sat there from the day the
# donation form went, on 2026-09-18, and the gate passed it on every run.
#
# The legal set is the hero's own, read out of utils/landing-hero.R. A list written here would
# go stale on the next rename and exempt the key it named. `svc` is the one key svcs() reads
# rather than s(), and rule 10 pins it the same way for the same reason. The 6 INVARIANT keys
# are legal: the hero reads every one of them, and INVARIANT says only that no translated block
# has to declare them.
#
# `en` is the only block this asks about. Rule 4 names any key a translated block declares and
# `en` does not. So between rule 4 and this rule, every declared key meets a question.
for k in sorted(set(en) - set(required) - {'svc'}):
    problems.append("the '%s' block declares '%s', and no s(\"%s\") call in "
                    "utils/landing-hero.R reads it, so nothing renders that value. Delete the "
                    "key, or read it in the hero" % (main, k, k))

# Rule 9 reads a pinned list of slots, and this is what holds that list against the hero. A
# key the hero writes and SCALAR_SLOTS omits is a slot nothing measures. The printed total
# stays honest about its own count and says nothing about the slot, so the check cannot fail
# on it. This runs in every mode, because it needs no rendered page.
for k in sorted(set(required) | set(COMPUTED_SLOTS)):
    if k not in SCALAR_SLOTS:
        problems.append("rule 9 reads no '%s' slot, and the hero writes that value into every "
                        "page. Add the key to SCALAR_SLOTS, with the pattern that reads it out "
                        "of the rendered markup." % k)

# Rule 10: every translated block declares every translatable key.
#
# The set is the keys the hero reads, less the language-invariant ones, plus the svc list.
# It comes from utils/landing-hero.R and not from landing.yml, so no edit to the data can
# lower it. `en` must declare the key too. A key only the hero names is rule 3's fault, and
# one report of it beats seven.
translatable = sorted(((set(required) & set(en_flat)) - set(INVARIANT)) | {'svc'})
allowed = {(k, c) for k, c, _ in OMISSIONS}

# Rules 4, 5, 6 and 10, over every translated block.
keys_declared, en_urls, complete = 0, 0, 0
for c in translated:
    blk = landing.get(c)
    if not isinstance(blk, dict):
        continue
    keys_declared += len(F[c])
    missing = [k for k in translatable if k not in blk and (k, c) not in allowed]
    if missing:
        problems.append("%s: the block omits %d of the %d keys a translated block MUST declare, "
                        "and each one falls back to '%s', so this page ships that slot in "
                        "English: %s" % (c, len(missing), len(translatable), main,
                                         ' '.join(missing)))
    else:
        complete += 1
    for k, v in sorted(F[c].items()):
        if k not in en_flat:
            problems.append("%s: key '%s' is not declared under '%s', so nothing can fall back "
                            "to it" % (c, k, main))
        if not v.strip():
            problems.append("%s: key '%s' is an empty string. Omit the key, and it falls back "
                            "to '%s'" % (c, k, main))
        elif k in en_flat and v.strip() == en_flat[k].strip():
            if shared_href(k, v):
                en_urls += 1
            else:
                problems.append("%s: key '%s' is byte-identical to '%s'. Omit it, or translate it"
                                % (c, k, main))
    # Rules 4b, 4c and 4d. A translated `svc: []`, a shortened card list or a malformed
    # field used to pass every rule here. Rule 9 then took the short list as the expected
    # one, so the slot total fell and nothing failed.
    cards = blk.get('svc')
    if cards is None:
        pass                        # the key is absent, so the hero falls back to English
    elif not isinstance(cards, list) or not cards:
        problems.append("%s: svc is %r. Omit the key to fall back to '%s', because an empty "
                        "list renders a band with no service cards" % (c, cards, main))
    else:
        check_cards(c, cards, problems)

# Rule 10b: every pinned omission still describes the block it names. An entry that no longer
# matches exempts nothing today and permits the same loss tomorrow, in silence.
for key, code, why in OMISSIONS:
    pinned = landing.get(code)
    if isinstance(pinned, dict) and key in pinned:
        problems.append("the pinned omission of '%s' in '%s' is stale: that block declares the "
                        "key now. Delete the entry, or rule 10 lets the key go missing again "
                        "without a word. The entry reads: %s" % (key, code, why))

# Rule 7: pairwise distinctness across every ordered pair of declared languages.
pairs = list(itertools.combinations(codes, 2))
urls, cognates = 0, 0
for a, b in pairs:
    for k in sorted(set(F[a]) & set(F[b])):
        if F[a][k] != F[b][k]:
            continue
        v = F[a][k]
        if shared_href(k, v):
            urls += 1
            continue
        if (k, (a, b), v) in COGNATES:
            cognates += 1
            continue
        problems.append("%s and %s both give key '%s' the same value, so one page carries the "
                        "other language's text: %r" % (a, b, k, v[:80]))

# Rule 8: every language's project file names the theme layers and the app bar.
gone = [c for c in codes if not (ROOT / 'content' / c / '_quarto.yaml').is_file()]
if gone:
    sys.exit("check-landing-strings.py: no %s. languages.yml declares that code, and rule 8 "
             "reads each project file for the theme wiring. Without the file this check "
             "measures no wiring, and it will not report a pass it did not measure."
             % ', no '.join('content/%s/_quarto.yaml' % c for c in gone))
wired = 0
for c in codes:
    project = ROOT / 'content' / c / '_quarto.yaml'
    paths = project_paths(load(project))
    faults = 0
    if 'format.html' not in paths:
        faults += 1
        problems.append("%s: content/%s/_quarto.yaml declares no format.html block, and Quarto "
                        "reads the theme and the app bar from there alone" % (c, c))
    for key, want, cost in WIRING:
        got = paths.get(key)
        for value in want:
            if got is None or value not in got:
                faults += 1
                problems.append("%s: content/%s/_quarto.yaml does not name %s under %s, %s"
                                % (c, c, value, key, cost))
    if not faults:
        wired += 1

print("languages declared: %d (%s)" % (len(codes), ' '.join(codes)))
print("project files wired to the theme and the app bar: %d of %d" % (wired, len(codes)))
print("keys the hero reads: %d, plus the svc cards (from utils/landing-hero.R)" % len(required))
print("keys declared: %d across the %d translated blocks; '%s' declares %d"
      % (keys_declared, len(translated), main, len(en_flat)))
print("translated blocks complete: %d of %d; a complete block declares %d keys, and %d pinned "
      "omissions are allowed" % (complete, len(translated), len(translatable), len(OMISSIONS)))
print("against '%s': %d values match it and are service-card hrefs, which the href rule allows"
      % (main, en_urls))
print("pairwise: %d ordered language pairs; %d service-card hrefs and %d allowed cognates skipped"
      % (len(pairs), urls, cognates))

# Rule 9: the transport rule. It reads a rendered page, so it runs only on request.
if want_slots:
    if ONLY is not None and ONLY not in codes:
        sys.exit("check-landing-strings.py --only %s: languages.yml declares no such code. It "
                 "declares %s." % (ONLY, ' '.join(codes)))
    selected = [ONLY] if ONLY else translated
    if '{code}' not in PAGES and len(selected) > 1:
        sys.exit("check-landing-strings.py --pages %s: the template holds no {code}, so every "
                 "language would read one file. Add {code}, or name one language with --only."
                 % PAGES)

    def page(c):
        return ROOT / PAGES.format(code=c)

    absent = [PAGES.format(code=c) for c in selected if not page(c).is_file()]
    if absent:
        sys.exit("check-landing-strings.py --slots: no %s. Render each language first, with "
                 "`cd content/<code> && quarto render index.qmd --to html`. This mode measures "
                 "nothing without a rendered page, and it will not report success it did not "
                 "measure." % ', no '.join(absent))

    # One pattern per rendered slot, keyed by the slot names its groups fill, in order. A
    # pattern anchors on the element that holds the value AND on its container where the page
    # carries the element more than once. The band logo is one of five images on the page, so
    # its pattern starts at the lockup that holds it.
    ONE = {
        ('eyebrow',): r'<div class="ael-eyebrow">(.*?)</div>',
        ('hero_title',): r'<h1 class="ael-htitle">(.*?)</h1>',
        ('subtitle',): r'<p class="ael-hsub">(.*?)</p>',
        ('search_placeholder', 'search_label'):
            r'<input id="ael-hsearch-input".*?placeholder="(.*?)" aria-label="(.*?)">',
        ('btn_start_href', 'btn_start'): r'<a class="btn light" href="([^"]*)">(.*?)</a>',
        ('btn_offline_href', 'btn_offline'): r'<a class="btn out" href="([^"]*)">(.*?)</a>',
        ('np_brand',): r'<div class="nplockup">\s*<img src="[^"]*" alt="([^"]*)">',
        ('np_lead',): r'<p class="nplead">(.*?)</p>',
        ('np_trust',): r'<div class="nptrust">(.*?)</div>\s*<div class="svcs">',
        ('np_btn_href', 'np_btn'):
            r'<div class="npfoot">\s*<a class="btn" href="([^"]*)">(.*?)</a>',
        ('np_links',): r'<div class="nplinks">(.*?)</div>',
    }
    CARD_RE = (r'<div class="svc"><div class="svch">(.*?)</div><p class="svcp">(.*?)</p>'
               r'<a class="svclink" href="([^"]*)">(.*?)</a></div>')

    # The two counts the hero computes. languages.yml and content/<main>/_quarto.yaml hold
    # them, landing.yml holds no copy, and utils/landing-hero.R counts them the same way.
    titles = {e['code']: e.get('title') for e in entries
              if isinstance(e, dict) and e.get('code')}
    book = load(ROOT / 'content' / main / '_quarto.yaml') or {}
    stems = []
    for x in ((book.get('book') or {}).get('chapters') or []):
        if isinstance(x, str):
            stems.append(x)
        elif isinstance(x, dict):
            stems.extend(y for y in (x.get('chapters') or []) if isinstance(y, str))
    chapters_n = len({re.sub(r'\.qmd$', '', s) for s in stems} - set(NOT_CHAPTERS))

    slots_read, fallbacks, mismatches = 0, 0, []
    for c in selected:
        text = page(c).read_text(encoding='utf-8')
        blk = landing.get(c) or {}
        got = {}
        # findall, never search. search reads the FIRST occurrence and stops, so a second
        # copy of a slot carrying the wrong value passes while the total still matches.
        # Upward drift has to fail the count as surely as downward drift does.
        for keys, pattern in ONE.items():
            hits = re.findall(pattern, text, re.S)
            name = '/'.join(keys)
            if not hits:
                mismatches.append("%s: the rendered page carries no '%s' slot at all" % (c, name))
            elif len(hits) > 1:
                mismatches.append("%s: the rendered page carries %d '%s' slots, and the hero "
                                  "writes one" % (c, len(hits), name))
            elif len(keys) == 1:
                got[keys[0]] = hits[0]
            else:
                for k, value in zip(keys, hits[0]):
                    got[k] = value
        nums = re.findall(r'<div class="statnum">(.*?)</div>', text, re.S)
        labels = re.findall(r'<div class="statlbl">(.*?)</div>', text, re.S)
        if len(nums) != 3 or len(labels) != 3:
            mismatches.append("%s: the rendered page carries %d stat numbers and %d stat labels, "
                              "and the hero writes 3 of each" % (c, len(nums), len(labels)))
        else:
            got['stat_used_num'], got['stat_chapters_num'], got['stat_languages_num'] = nums
            got['stat_used_label'], got['stat_chapters_label'], got['stat_languages_label'] = labels

        computed = {'hero_title': titles.get(c),
                    'stat_chapters_num': str(chapters_n),
                    'stat_languages_num': str(len(codes))}
        brand = blk.get('np_brand', en_flat.get('np_brand', ''))
        for k in SCALAR_SLOTS:
            if k not in got:
                continue            # the mismatch list already names the slot it could not read
            slots_read += 1
            if k in computed:
                if got[k] != computed[k]:
                    mismatches.append("%s: slot '%s'\n     got  %r\n     want %r"
                                      % (c, k, got[k], computed[k]))
                continue
            want = blk[k] if k in blk else en_flat.get(k)
            if k not in blk:
                fallbacks += 1
            if k == 'np_lead' and want is not None:
                want = want.replace('{brand}', '<span class="brandname">%s</span>' % brand)
            if want is None:
                mismatches.append("%s: the rendered page shows a '%s' slot that neither '%s' nor "
                                  "'%s' declares" % (c, k, c, main))
            elif got[k] != want:
                mismatches.append("%s: key '%s'\n     got  %r\n     want %r" % (c, k, got[k], want))

        cards = re.findall(CARD_RE, text, re.S)
        own = blk.get('svc') if isinstance(blk.get('svc'), list) else None
        wanted = own if own is not None else (en_cards or [])
        # CARDS is the authority on how many cards a page carries. A comparison against a
        # SHORT translated list would accept the loss that list caused. A comparison against
        # the English list would accept a matched reduction of both.
        if len(cards) != CARDS:
            mismatches.append("%s: the rendered page shows %d service cards, and the band "
                              "writes %d" % (c, len(cards), CARDS))
        if len(wanted) != CARDS:
            mismatches.append("%s: landing.yml gives %d service cards for this page, and the "
                              "band writes %d" % (c, len(wanted), CARDS))
        for i, (card, wcard) in enumerate(zip(cards, wanted), 1):
            for value, f in zip(card, CARD):
                slots_read += 1
                if own is None:
                    fallbacks += 1
                if value != (wcard.get(f) if isinstance(wcard, dict) else None):
                    mismatches.append("%s: key 'svc[%d].%s'\n     got  %r\n     want %r"
                                      % (c, i, f, value,
                                         wcard.get(f) if isinstance(wcard, dict) else None))

    # The count is an ASSERTION, not a print. A printed number nobody compares is decoration,
    # and a slot that goes unread lowers the total in silence. CARDS pins the per-page figure,
    # so a matched reduction of the English list and a translated list cannot lower it.
    per_page = len(SCALAR_SLOTS) + len(CARD) * CARDS
    expected = len(selected) * per_page
    print("slots read: %d across the %d rendered page(s); %d of them fall back to '%s'"
          % (slots_read, len(selected), fallbacks, main))
    print("slots expected: %d, which is %d page(s) x (%d scalar slots + %d fields x %d cards)"
          % (expected, len(selected), len(SCALAR_SLOTS), len(CARD), CARDS))
    if slots_read != expected:
        mismatches.append("rule 9 read %d slots and expected %d. The expectation is pinned, so "
                          "the data cannot move it. A total below it means a slot went unread, "
                          "and a check that reads nothing reports nothing."
                          % (slots_read, expected))
    print("slot mismatches: %d" % len(mismatches))
    problems.extend(mismatches)
else:
    print("slots read: 0. This run does not measure transport. Render each language, then "
          "add --slots.")

print("problems: %d" % len(problems))
if problems and not summary:
    for p in problems:
        print(p)
sys.exit(1 if problems else 0)
