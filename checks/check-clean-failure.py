#!/usr/bin/env python3
"""Every check must report a missing input, not crash on it.

A check that dies with a FileNotFoundError traceback still blocks, so the repository is not
unsafe. It is unusable: the reader sees a stack trace instead of the one sentence that says
which file is missing and why the check needs it. Two boxes of issue 455 were this, and one
of them crashed four checks at once.

There is a second and worse failure this covers. A check whose input is EMPTY rather than
missing reports a clean tree and exits 0. Nothing is measured and the result says success.
So a check MUST refuse an empty file set as well as an absent one.

For each check and each required input, this builds a fixture without that input and asserts
three things about the run. For languages.yml it also builds a fixture where that file does not
parse as YAML:

  it exits 2                   a missing input is not a pass, and not a finding (exit 1)
  it prints no traceback       the reader gets a sentence, not a stack
  it names the full path       the sentence is actionable

The third test needs the absolute path of the input as this script builds it, `str(target)`.
A relative name is not enough. The word `site` is part of the program name `check-site-links`,
so every message of that check held it. The fixture folder is resolved first, so the path is
the one each check computes from its own resolved location. The two special cases below need
the full path of their input too.

One input cannot sit in that fixture. `check-landing-strings.py --slots` reads a rendered
page, so it gets a second fixture: two declared languages, and no render in either.

`sync-chunks.py` finds the chapter files of each translation with a glob, so an empty
translation folder drops out of its file set. A third fixture declares two languages and
empties the folder of the second.

`check-unparsed-links.py` renders each chapter with pandoc, so it has inputs that no file
removal reaches. Six more cases break one of them each:
  - a chapter that pandoc fails on;
  - a chapter that is not UTF-8;
  - a `--pandoc` that names no command;
  - no quarto and no pandoc on PATH;
  - an unknown argument;
  - `--fixture` with no value.
Each MUST exit 2 with no traceback and one message line, and the line MUST hold the text that
the case names. That text is the full path of the chapter or the command where one exists.

Usage: python3 checks/check-clean-failure.py [--summary]
Exit 0 when every case is clean, 1 when any check crashes, passes, exits other than 2 or
names no full path on a missing input, or when a check 10 case fails one of its tests.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

# check script -> (its arguments, the inputs it must refuse to run without).
# 'content' is the chapter set, and an EMPTY one must be refused too.
CASES = {
    'check-links.py': (['--summary'], ['languages.yml', 'content']),
    'check-data-reads.py': (['--summary'], ['languages.yml', 'content']),
    'check-unparsed-links.py': (['--summary'], ['content']),
    'check-grid-tables.py': (['--summary'], ['languages.yml', 'content']),
    'check-image-names.py': (['--summary'], ['content', 'images']),
    'check-landing-strings.py': (['--summary'], [
        'languages.yml', 'landing.yml', 'utils/landing-hero.R', 'content']),
    'check-image-version-refs.py': (
        ['--summary'], ['docker-images.yml', '.devcontainer.json', 'README.md']),
    # The two sync scripts write chapter files, so they run as a dry run.
    'sync-anchors.py': (['--dry-run'], ['languages.yml', 'content']),
    'sync-chunks.py': (['--dry-run'], ['languages.yml', 'content']),
    # Checks 8 and 6 compare two commits, so the fixture becomes a git repository for them.
    # An empty diff is their correct result, so they have no 'content' case.
    'chunk-parse-gate.py': (['HEAD', 'HEAD'], ['languages.yml']),
    # Check 16 reads the English chapters and its list of exempt chunks. It needs R.
    'check-english-parse.py': (['--summary'], ['content', 'checks/parse-exceptions.tsv']),
    'check-case.py': (['--summary'], ['content', 'images', 'data']),
    'check-ui-strings.py': (['--summary'], ['ael-extras.html', 'languages.yml']),
    # Check 24 reads only translated languages, so build_translated() adds Spanish.
    'check-translation-rules.py': (['--summary'], [
        'languages.yml', 'content', 'landing.yml', 'ael-extras.html',
        'checks/translation-exceptions.tsv', 'translation/es.yml', 'translation/all.yml']),
    # Check 19 reads the stem list and the English chapters. It needs R too.
    'check-suggested-packages.py': (['--summary'], ['languages.yml', 'content']),
    'render-gate.sh': (['HEAD', 'HEAD'], ['languages.yml']),
    # Checks 17 and 18 read what a render wrote, so they take paths, not the chapter set.
    'check-render-leg.py': (['html_outputs', 'render.log'], ['html_outputs', 'render.log']),
    'check-site-links.py': (['site'], ['site']),
    # Check 25 reads the assembled site as well. build() gives languages.yml its main language.
    # Both read the declared languages out of languages.yml when CI passes no --languages.
    'check-rendered-tables.py': (['site'], ['site', 'languages.yml']),
    # Check 29 reads the assembled site as check 25 does.
    'check-rendered-structure.py': (['site'], ['site', 'languages.yml']),
    # Check 26 reads every language, English included, so build() is enough.
    'check-raw-html.py': (['--summary'], ['languages.yml', 'content']),
    # Checks 27 and 28 read a translated chapter as well, so build_parity() adds French and
    # one chapter. Both read the name list of bold, and check 27 reads its exceptions.
    'check-parity.py': (['--summary'], [
        'languages.yml', 'content', 'checks/parity-exceptions.tsv', 'checks/bold-names.txt']),
    'check-markdown-form.py': (['--summary'], [
        'languages.yml', 'content', 'checks/bold-names.txt']),
}

# The inputs that MUST be refused when they are empty as well as when they are absent.
EMPTY = ('content', 'images', 'html_outputs', 'render.log', 'site', 'checks/bold-names.txt')

# A languages.yml that does not parse: the flow sequence never closes.
BROKEN = 'main: en\nlanguages: [\n'

summary = '--summary' in sys.argv[1:]

# The theme wiring check-landing-strings.py reads out of a project file. A fixture without
# it reports a real fault, which would mask the missing input each case is about.
WIRING = ('format:\n'
          '  html:\n'
          '    include-after-body:\n'
          '      - ../../ael-extras.html\n'
          '    theme:\n'
          '      light: [../../theme-light.scss, ../../theme-ael.scss]\n'
          '      dark: [../../theme-dark.scss, ../../theme-ael.scss]\n')


def CARDS_YAML(tag):
    """The three svc cards one landing.yml block needs, tagged so no two blocks match.

    check-landing-strings.py pins the card count at 3. A fixture with fewer reports a real
    fault, and that fault would mask the missing input each case is about.
    """
    out = ['  svc:\n']
    for i in (1, 2, 3):
        out.append('    - h: "H%s%d"\n      p: "P%s%d"\n      link: "L%s%d"\n'
                   '      href: "https://example.org/%d"\n' % (tag, i, tag, i, tag, i, i))
    return ''.join(out)


def build(tmp):
    """A minimal but complete fixture: one language, one chapter, one image."""
    (tmp / 'content' / 'en').mkdir(parents=True)
    (tmp / 'content' / 'en' / 'index.qmd').write_text(
        '# Title\n\n```{r}\nknitr::include_graphics(here::here("images", "real.png"))\n```\n',
        encoding='utf-8')
    (tmp / 'content' / 'en' / '_quarto.yaml').write_text(
        'project:\n  type: book\nbook:\n  title: "T"\n  chapters:\n  - index.qmd\n' + WIRING,
        encoding='utf-8')
    (tmp / 'images').mkdir()
    (tmp / 'images' / 'real.png').write_bytes(b'PNG')
    (tmp / 'data').mkdir()
    (tmp / 'data' / 'real.csv').write_text('a\n1\n', encoding='utf-8')
    (tmp / 'ael-extras.html').write_text(
        "<script>\n  var UI = {\n    en: { dark: 'Dark mode' }\n  };\n</script>\n", encoding='utf-8')
    (tmp / 'languages.yml').write_text(
        'main: en\nlanguages:\n  - code: en\n    label: "English"\n    title: "T"\n', encoding='utf-8')
    (tmp / 'docker-images.yml').write_text('images:\n  - stem: index\n    image: epirhandbook-basics:2.9\n', encoding='utf-8')
    (tmp / '.devcontainer.json').write_text(
        '{"image": "ghcr.io/appliedepi/aedockerpublic/epirhandbook-monolith:2.9"}\n', encoding='utf-8')
    (tmp / 'README.md').write_text('The 2.9 images are public.\n', encoding='utf-8')
    (tmp / 'landing.yml').write_text('en:\n  eyebrow: "E"\n' + CARDS_YAML('E'),
                                     encoding='utf-8')
    (tmp / 'utils').mkdir()
    (tmp / 'utils' / 'landing-hero.R').write_text(
        'landing_hero <- function(lang) paste0(s("eyebrow"), svcs())\n', encoding='utf-8')
    # What checks 17 and 18 read: one rendered page, a log that carries the four lines
    # check 17 requires, and one assembled site page.
    (tmp / 'html_outputs').mkdir()
    (tmp / 'html_outputs' / 'index.html').write_text('<html><body></body></html>\n', encoding='utf-8')
    (tmp / 'render.log').write_text(
        'EHB-ERROR\twriting_functions.qmd\terror-missing-argument\tm\n'
        'EHB-ERROR\twriting_functions.qmd\terror-stop\tm\n'
        'EHB-WARNING\tmissing_data.qmd\twarning-coercion-demo\tm\n'
        'EHB-WARNING\tggplot_tips.qmd\twarning-na-translate-demo\tm\n', encoding='utf-8')
    (tmp / 'site').mkdir()
    (tmp / 'site' / 'index.html').write_text('<html><body></body></html>\n', encoding='utf-8')
    shutil.copytree(HERE, tmp / 'checks')


def build_translated(tmp):
    """build() plus one translated language, es, with its chapter, strings and rules.

    The rules are translation/es.yml and translation/all.yml, both with no banned entry.
    The exceptions file holds its header row only. build() copies the real file, whose rows
    excuse hits that this fixture does not have, and check 24 reports each such row as stale.
    """
    build(tmp)
    (tmp / 'checks' / 'translation-exceptions.tsv').write_text(
        'lang\tfile\tmatch_text\trule_id\treason\n', encoding='utf-8')
    with open(tmp / 'languages.yml', 'a', encoding='utf-8') as f:
        f.write('  - code: es\n    label: "Español"\n    title: "TE"\n')
    (tmp / 'content' / 'es').mkdir()
    (tmp / 'content' / 'es' / 'index.qmd').write_text('# Título\n', encoding='utf-8')
    with open(tmp / 'landing.yml', 'a', encoding='utf-8') as f:
        f.write('es:\n  eyebrow: "M"\n')
    ui = tmp / 'ael-extras.html'
    ui.write_text(ui.read_text(encoding='utf-8').replace(
        "\n  };", ",\n    es: { dark: 'Modo oscuro' }\n  };"), encoding='utf-8')
    (tmp / 'translation').mkdir()
    (tmp / 'translation' / 'es.yml').write_text('banned: []\n', encoding='utf-8')
    (tmp / 'translation' / 'all.yml').write_text('banned: []\n', encoding='utf-8')


def build_parity(tmp):
    """build() plus one translated language, fr, and one chapter other than index.qmd.

    Check 27 compares the chapters other than index.qmd in the translated languages, so
    build() alone gives it nothing to compare. It refuses that, and the refusal would mask the
    missing input each case is about. The exceptions file holds its header row only.
    """
    build(tmp)
    (tmp / 'checks' / 'parity-exceptions.tsv').write_text(
        'lang\tfile\tsection\tkind\tenglish\ttranslation\treason\n', encoding='utf-8')
    with open(tmp / 'languages.yml', 'a', encoding='utf-8') as f:
        f.write('  - code: fr\n    label: "Français"\n    title: "TF"\n')
    quarto = tmp / 'content' / 'en' / '_quarto.yaml'
    quarto.write_text(quarto.read_text(encoding='utf-8').replace(
        '  - index.qmd\n', '  - index.qmd\n  - basics.qmd\n'), encoding='utf-8')
    (tmp / 'content' / 'en' / 'basics.qmd').write_text(
        '# Basics\n\nUse `x` and **dplyr**.\n', encoding='utf-8')
    (tmp / 'content' / 'fr').mkdir()
    (tmp / 'content' / 'fr' / 'index.qmd').write_text('# Titre\n', encoding='utf-8')
    (tmp / 'content' / 'fr' / 'basics.qmd').write_text(
        '# Bases\n\nUtilisez `x` et **dplyr**.\n', encoding='utf-8')


# The checks whose fixture needs more than build() gives.
BUILDERS = {'check-translation-rules.py': build_translated, 'check-parity.py': build_parity,
            'check-markdown-form.py': build_parity}


def build_rendered(tmp):
    """A fixture for `check-landing-strings.py --slots`: two languages, no rendered page.

    build() above renders nothing, so it cannot tell a refusal from a clean run. This
    fixture declares a second language and gives it a complete, distinct string block.
    Every static rule then holds, and the missing rendered page is the only fault left.
    """
    (tmp / 'languages.yml').write_text(
        'main: en\nlanguages:\n  - code: en\n    lang: en\n    label: "English"\n'
        '    title: "T"\n  - code: fr\n    lang: fr\n    label: "Français"\n'
        '    title: "TF"\n', encoding='utf-8')
    (tmp / 'landing.yml').write_text('en:\n  eyebrow: "E"\n' + CARDS_YAML('E')
                                     + 'fr:\n  eyebrow: "F"\n' + CARDS_YAML('F'),
                                     encoding='utf-8')
    (tmp / 'utils').mkdir()
    (tmp / 'utils' / 'landing-hero.R').write_text(
        'landing_hero <- function(lang) paste0(s("eyebrow"), svcs())\n', encoding='utf-8')
    for code in ('en', 'fr'):
        (tmp / 'content' / code).mkdir(parents=True)
        (tmp / 'content' / code / '_quarto.yaml').write_text(WIRING, encoding='utf-8')
    shutil.copytree(HERE, tmp / 'checks')


def commit(tmp):
    """Make the fixture a git repository with one commit, so HEAD names a commit."""
    git = ['git', '-C', str(tmp), '-c', 'user.name=fixture', '-c', 'user.email=fixture@example.org',
           '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=' + os.devnull]
    for args in (['init', '-q'], ['add', '-A'], ['commit', '-q', '-m', 'fixture']):
        subprocess.run(git + args, check=True, capture_output=True)


failures = []
cases = 0
for script, (script_args, inputs) in sorted(CASES.items()):
    for missing in inputs:
        for mode in ('absent', 'empty', 'broken'):
            if mode == 'empty' and missing not in EMPTY:
                continue
            if mode == 'broken' and missing != 'languages.yml':
                continue
            cases += 1
            with tempfile.TemporaryDirectory() as raw:
                tmp = pathlib.Path(raw).resolve() / 'fixture'
                tmp.mkdir()
                BUILDERS.get(script, build)(tmp)
                if 'HEAD' in script_args:
                    commit(tmp)
                target = tmp / missing
                if mode == 'absent':
                    shutil.rmtree(target) if target.is_dir() else target.unlink()
                elif mode == 'empty' and target.is_file():
                    target.write_text('', encoding='utf-8')
                elif mode == 'empty':
                    shutil.rmtree(target)
                    target.mkdir()
                else:
                    target.write_text(BROKEN, encoding='utf-8')
                # No --fixture. That flag makes a check derive its file set by globbing,
                # which deliberately bypasses languages.yml, so it would exercise a path
                # the repository never runs. Each check takes ROOT from its own location,
                # so copying checks/ into the fixture IS how the fixture becomes the root.
                # The sync scripts read from the working directory, so cwd is the root too.
                shell = ['bash'] if script.endswith('.sh') else [sys.executable]
                run = subprocess.run(
                    shell + [str(tmp / 'checks' / script)] + script_args,
                    capture_output=True, text=True, cwd=tmp, timeout=120)
                output = run.stdout + run.stderr
                label = f"{script} with {missing} {mode}"
                if run.returncode == 0:
                    failures.append(f"{label}: exited 0, so a missing input reads as a pass")
                elif 'Traceback' in output:
                    failures.append(f"{label}: crashed with a traceback instead of a message")
                elif run.returncode != 2:
                    failures.append(f"{label}: exited {run.returncode}, and a missing input MUST exit 2")
                elif str(target) not in output:
                    failures.append(f"{label}: the message never names the full path {target}")

# The rendered page that `check-landing-strings.py --slots` reads. It is the one input
# in this repository that a check can only see after a render, so build() cannot hold it.
cases += 1
with tempfile.TemporaryDirectory() as raw:
    tmp = pathlib.Path(raw).resolve() / 'fixture'
    tmp.mkdir()
    build_rendered(tmp)
    target = tmp / 'content' / 'fr' / 'html_outputs'
    run = subprocess.run(
        [sys.executable, str(tmp / 'checks' / 'check-landing-strings.py'), '--summary', '--slots'],
        capture_output=True, text=True, cwd=tmp, timeout=120)
    output = run.stdout + run.stderr
    label = "check-landing-strings.py --slots with the rendered page absent"
    if run.returncode == 0:
        failures.append(f"{label}: exited 0, so a missing input reads as a pass")
    elif 'Traceback' in output:
        failures.append(f"{label}: crashed with a traceback instead of a message")
    elif run.returncode != 2:
        failures.append(f"{label}: exited {run.returncode}, and a missing input MUST exit 2")
    elif str(target) not in output:
        failures.append(f"{label}: the message never names the full path {target}")

# An empty translation folder. sync-chunks.py globs each folder, so the language would drop
# out of the file set and the run would report no drift for a language it never read.
cases += 1
with tempfile.TemporaryDirectory() as raw:
    tmp = pathlib.Path(raw).resolve() / 'fixture'
    tmp.mkdir()
    build(tmp)
    target = tmp / 'content' / 'fr'
    (tmp / 'languages.yml').write_text(
        'main: en\nlanguages:\n  - code: en\n    label: "English"\n    title: "T"\n'
        '  - code: fr\n    label: "Français"\n    title: "TF"\n', encoding='utf-8')
    (tmp / 'content' / 'en' / 'basics.qmd').write_text('# Basics\n', encoding='utf-8')
    (tmp / 'content' / 'fr').mkdir()
    run = subprocess.run(
        [sys.executable, str(tmp / 'checks' / 'sync-chunks.py'), '--dry-run'],
        capture_output=True, text=True, cwd=tmp, timeout=120)
    output = run.stdout + run.stderr
    label = "sync-chunks.py with content/fr empty"
    if run.returncode == 0:
        failures.append(f"{label}: exited 0, so a missing input reads as a pass")
    elif 'Traceback' in output:
        failures.append(f"{label}: crashed with a traceback instead of a message")
    elif run.returncode != 2:
        failures.append(f"{label}: exited {run.returncode}, and a missing input MUST exit 2")
    elif str(target) not in output:
        failures.append(f"{label}: the message never names the full path {target}")

# Check 10: the inputs that only pandoc and the argument list reach. Each row holds:
#   label     the case
#   chapter   the bytes that replace content/en/index.qmd, or None
#   extra     the arguments after --summary
#   path      the PATH of the run, or None for the PATH of this script
#   needle    the text that the one message line MUST hold
# `{tmp}` is the fixture folder.
CHAPTER = '{tmp}/content/en/index.qmd'
for label, chapter, extra, path, needle in (
        ('a chapter that pandoc fails on', b'---\ntitle: [unclosed\n---\n\nText.\n', [],
         None, CHAPTER),
        ('a chapter that is not UTF-8', b'Caf\xe9 text.\n', [], None, CHAPTER),
        ('a --pandoc that names no command', None, ['--pandoc', '{tmp}/no-pandoc'], None,
         '{tmp}/no-pandoc'),
        ('no quarto and no pandoc on PATH', None, [], '{tmp}/empty-bin', 'no pandoc'),
        ('an unknown argument', None, ['--bogus'], None, 'Usage:'),
        ('--fixture with no value', None, ['--fixture'], None, 'Usage:')):
    cases += 1
    with tempfile.TemporaryDirectory() as raw:
        tmp = pathlib.Path(raw).resolve() / 'fixture'
        tmp.mkdir()
        build(tmp)
        if chapter is not None:
            (tmp / 'content' / 'en' / 'index.qmd').write_bytes(chapter)
        env = dict(os.environ)
        if path is not None:
            pathlib.Path(path.format(tmp=tmp)).mkdir()
            env['PATH'] = path.format(tmp=tmp)
        run = subprocess.run(
            [sys.executable, str(tmp / 'checks' / 'check-unparsed-links.py'), '--summary']
            + [x.format(tmp=tmp) for x in extra],
            capture_output=True, text=True, cwd=tmp, env=env, timeout=120)
        message = run.stderr.strip()
        needle = needle.format(tmp=tmp)
        label = f"check-unparsed-links.py with {label}"
        if run.returncode == 0:
            failures.append(f"{label}: exited 0, so a bad input reads as a pass")
        elif 'Traceback' in run.stdout + run.stderr:
            failures.append(f"{label}: crashed with a traceback instead of a message")
        elif run.returncode != 2:
            failures.append(f"{label}: exited {run.returncode}, and a bad input MUST exit 2")
        elif len(message.splitlines()) != 1:
            failures.append(f"{label}: wrote {len(message.splitlines())} lines on stderr, "
                            "and the message MUST be one line")
        elif needle not in message:
            failures.append(f"{label}: the message never names {needle}")

print(f"cases: {cases}")
print(f"checks that do not fail cleanly: {len(failures)}")
if failures and not summary:
    for f in failures:
        print(f)
sys.exit(1 if failures else 0)
