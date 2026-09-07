# Codex review of the fix pass, Turkish part 2

Range: BASE=491b5dbe2 HEAD=4a05d93731. 9 batches, 131 fixed entries, 131 hunks, plus the part-1 repair commit. Model gpt-5.6-sol, reasoning effort high, 199,301 tokens. Items 7 to 26 are the part-1 repairs, which the FINDINGS.md of this range did not list; they are authorised by codex-fixpass-tr-part1.md and are not defects.

I read all 131 hunks and all 131 findings.

- Wrong edits: 26.
- Overreach: 20 hunks.
- Wrong removals: 0. There are no `added` findings; the removals match the English.
- Wrong insertions: 0. There are no `missing` findings; the Farrington heading is correctly placed.
- No English file or executable `{r}` chunk changed. Two fenced code/output blocks were changed, which violates the stated boundary.

1. [combination_analysis.tr.qmd:103](/tmp/codex-ws/tr-part2/chapters/combination_analysis.tr.qmd:103) — NEW: `case_when()` converts `"evet"` and `"hayır"`. The adjacent chunk uses base `ifelse()` and literal values `"yes"` and `"no"`. Fix: describe `mutate()` with `ifelse()` and use `"yes"`/`"no"`.

2. [grouping.tr.qmd:368](/tmp/codex-ws/tr-part2/chapters/grouping.tr.qmd:368) — NEW: ``by = "months"``. The chunk uses `by = "month"`. Fix: use the exact literal `"month"`.

3. [tables_presentation.tr.qmd:245](/tmp/codex-ws/tr-part2/chapters/tables_presentation.tr.qmd:245) — NEW: “sütun 1, sütun 2 ve 4 ile 8 arasındaki sütunlar”. The code uses `j = c(4,5,7,8)`, excluding column 6. Fix: say “sütun 1, sütun 2 ve sütun 4, 5, 7 ve 8”.

4. [missing_data.tr.qmd:88](/tmp/codex-ws/tr-part2/chapters/missing_data.tr.qmd:88) — NEW link: `](#clean_case_when)`. This points within `missing_data.tr.qmd`, where that anchor does not exist. English links to the cleaning chapter. Fix: `](cleaning.tr.qmd#clean_case_when)`.

5. [errors.tr.qmd:85](/tmp/codex-ws/tr-part2/chapters/errors.tr.qmd:85) — NEW inside a fenced block: `# mutate(x = recode(x, OLD= NEW) içindeki x değişkeni yeniden belirtilmeden recode çalıştırıldı`. Fix: revert the fenced-block edit; put any corrected explanation outside the fence.

6. [errors.tr.qmd:105](/tmp/codex-ws/tr-part2/chapters/errors.tr.qmd:105) — NEW changes the comment and `Problem with mutate()` line inside another fenced block. Fix: revert this hunk and explain the error outside the fence.

7. [basics.tr.qmd:867](/tmp/codex-ws/tr-part2/chapters/basics.tr.qmd:867) — NEW: `` `<-` atama operatörünü "olarak tanımlanır" diye okuyabilirsiniz.`` No finding names this wording change. Fix: revert to OLD.

8. [cleaning.tr.qmd:200](/tmp/codex-ws/tr-part2/chapters/cleaning.tr.qmd:200) — NEW adds backticks around `replace =` and its example in the same hunk as the valid label-section removal. No finding names this formatting change. Fix: retain the removal but restore the OLD bullet.

9. [cleaning.tr.qmd:983](/tmp/codex-ws/tr-part2/chapters/cleaning.tr.qmd:983) — NEW changes `DOĞRU` to `` `TRUE` ``. Correct, but unnamed. Fix: revert or create a separate approved finding.

10. [cleaning.tr.qmd:1908](/tmp/codex-ws/tr-part2/chapters/cleaning.tr.qmd:1908) — NEW rewrites the complete `num_NA_dates` bullet. No finding names it. Fix: revert.

11. [editorial_style.tr.qmd:133](/tmp/codex-ws/tr-part2/chapters/editorial_style.tr.qmd:133) — NEW adds a trailing double-space hard break to `10 May 2021 |Versiyon 1.0.0'ın yayınlanması`. Fix: remove the added trailing space.

12. [factors.tr.qmd:113](/tmp/codex-ws/tr-part2/chapters/factors.tr.qmd:113) — NEW adds a trailing double-space hard break after the `NA` sentence. No finding names it. Fix: restore the original line ending.

13. [help.tr.qmd:14](/tmp/codex-ws/tr-part2/chapters/help.tr.qmd:14) — NEW: `[İşbirliği ve Github](collaboration.tr.qmd)`. This link change has no finding. Fix: revert.

14. [importing.tr.qmd:180](/tmp/codex-ws/tr-part2/chapters/importing.tr.qmd:180) — NEW changes translated folder descriptions to `"data"` and `"linelists"`. No finding names this change. Fix: revert.

15. [network_drives.tr.qmd:69](/tmp/codex-ws/tr-part2/chapters/network_drives.tr.qmd:69) — NEW: `[R temelleri](basics.tr.qmd)`. This link change is unnamed. Fix: revert.

16. [phylogenetic_trees.tr.qmd:134](/tmp/codex-ws/tr-part2/chapters/phylogenetic_trees.tr.qmd:134) — NEW changes `DOĞRU veya YANLIŞ` to `` `TRUE` veya `FALSE` ``. Correct but unnamed. Fix: revert or add a finding.

17. [regression.tr.qmd:319](/tmp/codex-ws/tr-part2/chapters/regression.tr.qmd:319) — NEW: `[Karakterler ve dizeler](characters_strings.tr.qmd)`. No finding names this link change. Fix: revert only the link.

18. [shiny_basics.tr.qmd:8](/tmp/codex-ws/tr-part2/chapters/shiny_basics.tr.qmd:8) — NEW bolds `**shiny**`. No finding names this formatting edit. Fix: revert.

19. [shiny_basics.tr.qmd:16](/tmp/codex-ws/tr-part2/chapters/shiny_basics.tr.qmd:16) — NEW changes the target to `flexdashboard.tr.qmd`. No finding names it. Fix: revert.

20. [survey_analysis.tr.qmd:32](/tmp/codex-ws/tr-part2/chapters/survey_analysis.tr.qmd:32) — NEW changes the R-basics target to `basics.tr.qmd`. Unnamed. Fix: revert.

21. [survey_analysis.tr.qmd:311](/tmp/codex-ws/tr-part2/chapters/survey_analysis.tr.qmd:311) — NEW changes the deduplication target to `deduplication.tr.qmd`. Unnamed. Fix: revert.

22. [survival_analysis.tr.qmd:46](/tmp/codex-ws/tr-part2/chapters/survival_analysis.tr.qmd:46) — NEW changes the R-basics target to `basics.tr.qmd`. Unnamed. Fix: revert.

23. [survival_analysis.tr.qmd:167](/tmp/codex-ws/tr-part2/chapters/survival_analysis.tr.qmd:167) — NEW changes the descriptive-tables target to `tables_descriptive.tr.qmd`. Unnamed. Fix: revert.

24. [tables_descriptive.tr.qmd:894](/tmp/codex-ws/tr-part2/chapters/tables_descriptive.tr.qmd:894) — Alongside valid corrections, NEW adds bold/code formatting and changes the link to `characters_strings.tr.qmd`. Those edits have no finding. Fix: retain `contains()`, `starts_with()`, and `statistic =`; revert the formatting and link changes.

25. [tables_presentation.tr.qmd:156](/tmp/codex-ws/tr-part2/chapters/tables_presentation.tr.qmd:156) — NEW adds a trailing double-space hard break. No finding names it. Fix: restore the OLD line ending.

26. [tables_presentation.tr.qmd:531](/tmp/codex-ws/tr-part2/chapters/tables_presentation.tr.qmd:531) — NEW rewrites the full R Markdown sentence for fluency, but no finding names it. Fix: revert.

VERDICT: BLOCK — 26 hunks wrong out of 131 read.
