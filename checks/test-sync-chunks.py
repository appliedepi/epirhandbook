#!/usr/bin/env python3
"""Tests of merge() in checks/sync-chunks.py: a translated heading stays above its own code line.

Issue #461. English deleted a heading and the code line under it. The old merge() paired the
comment-only lines by position, so in fr the next heading became `# Apprendre R`.

Usage:
    python3 checks/test-sync-chunks.py
"""
import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # sync-chunks.py imports langs.py from this folder
spec = importlib.util.spec_from_file_location('sync_chunks', os.path.join(HERE, 'sync-chunks.py'))
sync_chunks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_chunks)
merge = sync_chunks.merge

TR = ['# a', 'x1 <- 1', '# b', 'x2 <- 2', '# c', 'x3 <- 3']


class HeadingStaysWithItsCode(unittest.TestCase):

    def test_english_deletes_heading_and_its_code(self):
        en = ['# A', 'x1 <- 1', '# C', 'x3 <- 3']
        out, kept, fallback = merge(en, TR)
        self.assertNotIn('# b', out)
        self.assertEqual(out[out.index('x1 <- 1') - 1], '# a')
        # `# b` belongs to the deleted x2. `# c` sits after x2, so it stays with x3.
        self.assertEqual(out[out.index('x3 <- 3') - 1], '# c')
        self.assertEqual(out, ['# a', 'x1 <- 1', '# c', 'x3 <- 3'])
        self.assertEqual((kept, fallback), (2, 0))

    def test_english_deletes_heading_only(self):
        en = ['# A', 'x1 <- 1', 'x2 <- 2', '# C', 'x3 <- 3']
        out, kept, fallback = merge(en, TR)
        self.assertNotIn('# b', out)
        self.assertEqual(out, ['# a', 'x1 <- 1', 'x2 <- 2', '# c', 'x3 <- 3'])
        self.assertEqual((kept, fallback), (2, 0))

    def test_packages_suggested_chunk(self):
        # Lines 10-21 of the English chunk at b5fc2dea, and lines 10-25 of the fr chunk before it.
        en = ['# Ensures the package "pacman" is installed',
              'if (!require("pacman")) install.packages("pacman")', '', '',
              '# Packages available from CRAN', '##############################',
              'pacman::p_load(', '     ',
              '     # project and file management', '     #############################',
              '     here,     # file paths relative to R project root folder',
              '     rio,      # import/export of many types of data']
        tr = ['# S\'assure de l\'installation du paquet "pacman".',
              'if (!require("pacman")) install.packages("pacman")', '', '',
              '#  Paquets du CRAN', '##############################',
              'pacman::p_load(', '     ',
              '     # Apprendre R', '     ############',
              '     learnr,   # tutos interactifs dans le volet tutos de RStudio',
              '     swirl,    # tutoriels interactifs dans la console R', '        ',
              '     # Gestion des projets et des dossiers', '     #############################',
              '     here,     # chemins de fichiers relatifs au dossier racine du projet R',
              '     rio,      # import/export de nombreux types de données']
        out, kept, fallback = merge(en, tr)
        self.assertNotIn('     # Apprendre R', out)
        # `# Apprendre R` belongs to the deleted learnr. The heading of here, stays above it.
        self.assertEqual(out[8:11], tr[13:16])
        self.assertEqual((kept, fallback), (5, 0))

    def test_unchanged_chunk_keeps_every_translated_line(self):
        en = ['# A', 'x1 <- 1', '# B', 'x2 <- 2', '# C', 'x3 <- 3']
        out, kept, fallback = merge(en, TR)
        self.assertEqual(out, TR)
        self.assertEqual((kept, fallback), (3, 0))


if __name__ == '__main__':
    unittest.main(verbosity=2)
