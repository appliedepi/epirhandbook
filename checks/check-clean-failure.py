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

  it exits non-zero            a missing input is not a pass
  it prints no traceback       the reader gets a sentence, not a stack
  it names the missing thing   the sentence is actionable

One input cannot sit in that fixture. `check-landing-strings.py --slots` reads a rendered
page, so it gets a second fixture: two declared languages, and no render in either.

Usage: python3 checks/check-clean-failure.py [--summary]
Exit 0 when every case is clean, 1 when any check crashes or passes on a missing input.
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
    'check-image-names.py': (['--summary'], ['content', 'images']),
    'check-landing-strings.py': (['--summary'], [
        'languages.yml', 'landing.yml', 'utils/landing-hero.R', 'content']),
    'check-image-version-refs.py': (
        ['--summary'], ['docker-images.yml', '.devcontainer.json', 'README.md']),
    # The two sync scripts write chapter files, so they run as a dry run. sync-chunks.py finds
    # its files with a glob, so it reads no stem list and has no 'content' case.
    'sync-anchors.py': (['--dry-run'], ['languages.yml', 'content']),
    'sync-chunks.py': (['--dry-run'], ['languages.yml']),
    # Checks 8 and 6 compare two commits, so the fixture becomes a git repository for them.
    # An empty diff is their correct result, so they have no 'content' case.
    'chunk-parse-gate.py': (['HEAD', 'HEAD'], ['languages.yml']),
    'render-gate.sh': (['HEAD', 'HEAD'], ['languages.yml']),
}

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
    shutil.copytree(HERE, tmp / 'checks')


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
            if mode == 'empty' and missing not in ('content', 'images'):
                continue
            if mode == 'broken' and missing != 'languages.yml':
                continue
            cases += 1
            with tempfile.TemporaryDirectory() as raw:
                tmp = pathlib.Path(raw) / 'fixture'
                tmp.mkdir()
                build(tmp)
                if 'HEAD' in script_args:
                    commit(tmp)
                target = tmp / missing
                if mode == 'absent':
                    shutil.rmtree(target) if target.is_dir() else target.unlink()
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
                elif missing.split('/')[0] not in output:
                    failures.append(f"{label}: the message never names {missing}")

# The rendered page that `check-landing-strings.py --slots` reads. It is the one input
# in this repository that a check can only see after a render, so build() cannot hold it.
cases += 1
with tempfile.TemporaryDirectory() as raw:
    tmp = pathlib.Path(raw) / 'fixture'
    tmp.mkdir()
    build_rendered(tmp)
    run = subprocess.run(
        [sys.executable, str(tmp / 'checks' / 'check-landing-strings.py'), '--summary', '--slots'],
        capture_output=True, text=True, cwd=tmp, timeout=120)
    output = run.stdout + run.stderr
    label = "check-landing-strings.py --slots with the rendered page absent"
    if run.returncode == 0:
        failures.append(f"{label}: exited 0, so a missing input reads as a pass")
    elif 'Traceback' in output:
        failures.append(f"{label}: crashed with a traceback instead of a message")
    elif 'content/fr/html_outputs' not in output:
        failures.append(f"{label}: the message never names content/fr/html_outputs")

print(f"cases: {cases}")
print(f"checks that do not fail cleanly: {len(failures)}")
if failures and not summary:
    for f in failures:
        print(f)
sys.exit(1 if failures else 0)
