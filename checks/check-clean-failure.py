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
three things about the run:

  it exits non-zero            a missing input is not a pass
  it prints no traceback       the reader gets a sentence, not a stack
  it names the missing thing   the sentence is actionable

Usage: python3 checks/check-clean-failure.py [--summary]
Exit 0 when every case is clean, 1 when any check crashes or passes on a missing input.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

# check script -> the inputs it must refuse to run without.
# 'content' is the chapter set, and an EMPTY one must be refused too.
CASES = {
    'check-links.py': ['languages.yml', 'content'],
    'check-data-reads.py': ['languages.yml', 'content'],
    'check-unparsed-links.py': ['content'],
    'check-image-names.py': ['content', 'images'],
    'check-language-copies.py': ['languages.yml', 'banner.html'],
    'check-image-version-refs.py': ['docker-images.yml', '.devcontainer.json', 'README.md'],
}

summary = '--summary' in sys.argv[1:]


def build(tmp):
    """A minimal but complete fixture: one language, one chapter, one image."""
    (tmp / 'content' / 'en').mkdir(parents=True)
    (tmp / 'content' / 'en' / 'index.qmd').write_text(
        '# Title\n\n```{r}\nknitr::include_graphics(here::here("images", "real.png"))\n```\n',
        encoding='utf-8')
    (tmp / 'content' / 'en' / '_quarto.yaml').write_text(
        'project:\n  type: book\nbook:\n  title: "T"\n  chapters:\n  - index.qmd\n', encoding='utf-8')
    (tmp / 'images').mkdir()
    (tmp / 'images' / 'real.png').write_bytes(b'PNG')
    (tmp / 'languages.yml').write_text(
        'main: en\nlanguages:\n  - code: en\n    label: "English"\n    title: "T"\n', encoding='utf-8')
    (tmp / 'banner.html').write_text(
        "<script>\n  const translations = {\n    en: 'a'\n  };\n</script>\n", encoding='utf-8')
    (tmp / 'docker-images.yml').write_text('images:\n  - stem: index\n    image: epirhandbook-basics:2.9\n', encoding='utf-8')
    (tmp / '.devcontainer.json').write_text(
        '{"image": "ghcr.io/appliedepi/aedockerpublic/epirhandbook-monolith:2.9"}\n', encoding='utf-8')
    (tmp / 'README.md').write_text('The 2.9 images are public.\n', encoding='utf-8')
    shutil.copytree(HERE, tmp / 'checks')


failures = []
cases = 0
for script, inputs in sorted(CASES.items()):
    for missing in inputs:
        for mode in ('absent', 'empty'):
            if mode == 'empty' and missing not in ('content', 'images'):
                continue
            cases += 1
            with tempfile.TemporaryDirectory() as raw:
                tmp = pathlib.Path(raw) / 'fixture'
                tmp.mkdir()
                build(tmp)
                target = tmp / missing
                if mode == 'absent':
                    shutil.rmtree(target) if target.is_dir() else target.unlink()
                else:
                    shutil.rmtree(target)
                    target.mkdir()
                # No --fixture. That flag makes a check derive its file set by globbing,
                # which deliberately bypasses languages.yml, so it would exercise a path
                # the repository never runs. Each check takes ROOT from its own location,
                # so copying checks/ into the fixture IS how the fixture becomes the root.
                run = subprocess.run(
                    [sys.executable, str(tmp / 'checks' / script), '--summary'],
                    capture_output=True, text=True, cwd=tmp, timeout=120)
                output = run.stdout + run.stderr
                label = f"{script} with {missing} {mode}"
                if run.returncode == 0:
                    failures.append(f"{label}: exited 0, so a missing input reads as a pass")
                elif 'Traceback' in output:
                    failures.append(f"{label}: crashed with a traceback instead of a message")
                elif missing.split('/')[0] not in output:
                    failures.append(f"{label}: the message never names {missing}")

print(f"cases: {cases}")
print(f"checks that do not fail cleanly: {len(failures)}")
if failures and not summary:
    for f in failures:
        print(f)
sys.exit(1 if failures else 0)
