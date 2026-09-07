#!/usr/bin/env python3
"""Apply the repairs from the codex review of the fix pass, Turkish part 1.

Every edit is an exact string replacement, and the script exits 1 if any
old string is not found exactly once. Verified against the files by hand
before this script was written; see modernization/reviews/codex-fixpass-tr-part1.md.

Rejected codex items, not applied: interactive_plots.tr.qmd (the removed count
has no English PROSE source; the English prose is the reference) and
data_used.tr.qmd (the English offline-download list has three bullets, the
Turkish had four; the deleted point lives lower on the page in both languages).
grouping.tr.qmd was already correct in the tree when the review landed.
"""
import re
import sys

EDITS = [
    # 3. nine cross-links must point at the Turkish chapter
    ('chapters/help.tr.qmd', '](collaboration.qmd)', '](collaboration.tr.qmd)'),
    ('chapters/network_drives.tr.qmd', '](basics.qmd)', '](basics.tr.qmd)'),
    ('chapters/regression.tr.qmd', '](characters_strings.qmd)', '](characters_strings.tr.qmd)'),
    ('chapters/shiny_basics.tr.qmd', '](flexdashboard.qmd)', '](flexdashboard.tr.qmd)'),
    ('chapters/survey_analysis.tr.qmd', '](basics.qmd)', '](basics.tr.qmd)'),
    ('chapters/survey_analysis.tr.qmd', '](deduplication.qmd)', '](deduplication.tr.qmd)'),
    ('chapters/survival_analysis.tr.qmd', '](basics.qmd)', '](basics.tr.qmd)'),
    ('chapters/survival_analysis.tr.qmd', '](tables_descriptive.qmd)', '](tables_descriptive.tr.qmd)'),
    ('chapters/tables_descriptive.tr.qmd',
     "• Denklemin sağ tarafı, stringr'den str_glue() sözdizimini kullanır (bkz. [Karakterler ve dizeler](characters_strings.qmd))",
     "• Denklemin sağ tarafı, **stringr**'den `str_glue()` sözdizimini kullanır (bkz. [Karakterler ve dizeler](characters_strings.tr.qmd))"),
    # 1. literal folder names beside the code
    ('chapters/importing.tr.qmd',
     '"veri" ve "çizgi listeleri" alt klasörlerinde',
     '"data" ve "linelists" alt klasörlerinde'),
    # 6, 7 and the sweep's third: R literals in edited lines
    ('chapters/cleaning.tr.qmd',
     'Belirli bir satır için en üstteki ölçüt DOĞRU olarak',
     'Belirli bir satır için en üstteki ölçüt `TRUE` olarak'),
    ('chapters/cleaning.tr.qmd',
     '• Yeni sütun num_NA_dates oluşturur, her satır için adında "date" geçen sütunlardan is.na() öğesinin DOĞRU olarak değerlendirildiği sütun sayısı tanımlanır.',
     '• Yeni `num_NA_dates` sütununu oluşturur; her satır için adında "date" geçen sütunlardan `is.na()` sonucunun `TRUE` olduğu sütunların sayısını verir.'),
    ('chapters/phylogenetic_trees.tr.qmd',
     'bir DOĞRU veya YANLIŞ mantıksal vektörü',
     'bir `TRUE` veya `FALSE` mantıksal vektörü'),
    # 10. inline-code markup dropped from an insertion
    ('chapters/cleaning.tr.qmd',
     '• replace = argümanına bir vektör vererek belirli ad değişikliklerini belirtebilirsiniz (ör. replace = c(onset = "date_of_onset"))',
     '• `replace = ` argümanına bir vektör vererek belirli ad değişikliklerini belirtebilirsiniz (ör. `replace = c(onset = "date_of_onset")`)'),
    # 11. package name styling
    ('chapters/shiny_basics.tr.qmd', 'shiny ile bir gösterge paneli üretmek', '**shiny** ile bir gösterge paneli üretmek'),
    # 8, 9. fluency
    ('chapters/basics.tr.qmd',
     '`<-` atama operatörünü "şu şekilde tanımlanır" sözcükleri olarak düşünebilirsiniz.',
     '`<-` atama operatörünü "olarak tanımlanır" diye okuyabilirsiniz.'),
    ('chapters/tables_presentation.tr.qmd',
     'Tablo nesnesi R markdown kod parçası içinde çağrılırsa, bu tablo otomatik bir belgenize, yani bir R markdown çıktısına entegre edilebilir.',
     'Tablo nesnesi bir R Markdown kod parçasında çağrılırsa, tablo otomatik bir belgeye, yani R Markdown çıktısına entegre edilebilir.'),
]

# 12. trailing double-space line breaks lost on edited lines, all languages.
# Each entry: file, the end of the line as it is now (no trailing spaces).
TRAIL = [
    ('chapters/cleaning.es.qmd', 'para especificar el orden del factor de los nuevos valores.'),
    ('chapters/data_used.pt.qmd', 'os dados de exemplo (processo de instalação descrito abaixo)'),
    ('chapters/data_used.pt.qmd', 'ser baixados como arquivos .rds clicando nos seguintes links:'),
    ('chapters/editorial_style.es.qmd', '10 Mayo 2021    |Lanzamiento de la versión 1.0.0'),
    ('chapters/editorial_style.pt.qmd', '10 Maio 2021   |Lançamento da versão 1.0.0'),
    ('chapters/editorial_style.tr.qmd', "10 May 2021    |Versiyon 1.0.0'ın yayınlanması"),
    ('chapters/factors.tr.qmd', "`NA`'nın bir faktör seviyesi olmadığını unutmayın."),
    ('chapters/tables_presentation.tr.qmd', 'Çıktı `table` olarak kaydedilmiştir.'),
]


def main():
    fails = 0
    for path, old, new in EDITS:
        s = open(path, encoding='utf-8').read()
        n = s.count(old)
        if n != 1:
            print('FAIL %s: old string found %d times: %r' % (path, n, old[:70])); fails += 1; continue
        open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
        print('ok   %s: %s' % (path, new[:70]))
    for path, end in TRAIL:
        s = open(path, encoding='utf-8').read()
        pat = re.compile('^(.*' + re.escape(end) + ') {0,1}$', re.M)
        hits = pat.findall(s)
        if len(hits) != 1:
            print('FAIL %s: line ending %r found %d times without two trailing spaces' % (path, end[-40:], len(hits))); fails += 1; continue
        s = pat.sub(lambda m: m.group(1) + '  ', s, count=1)
        open(path, 'w', encoding='utf-8', newline='').write(s)
        print('ok   %s: restored two trailing spaces after %r' % (path, end[-40:]))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
