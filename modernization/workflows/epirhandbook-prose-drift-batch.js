export const meta = {
  name: 'epirhandbook-prose-drift-batch',
  description: 'Prose sweep, one batch of whole chapters x 7 languages, hard-sliced so it cannot overshoot quota',
  phases: [
    { title: 'Find', detail: 'one agent per chapter-language pair, writes JSON to /tmp/gate/prose' },
  ],
}

// BATCH RUN. Shape B, the hard slice from modernization/RESUME.md section 4.
// STEMS holds ONLY the chapters this batch reads. It is NOT the 48-stem corpus.
// Cutting STEMS is defect-1 mitigation: the 336-pair run had no guard and the
// session limit killed 253 agents mid-flight. A hard slice cannot overshoot.
//
// Defect-2 mitigation is NOT in this script, because a workflow script has no
// filesystem access. The orchestrator MUST reconcile against /tmp/gate/prose/*.json
// after this run returns. The file is the artifact. A return value is only a
// report about the artifact, and 11 agents once wrote a file and then died
// before returning.

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGS = ['es', 'fr', 'jp', 'pt', 'ru', 'tr', 'vn']

// Wave 1 read ['r_projects', 'errors'], the two smallest remaining chapters:
// 14 pairs, 33 findings, 728,283 tokens, 52,020 per pair.
// Wave 2 reads the two LARGEST remaining chapters, to measure the cost end that
// wave 1 leaves unmeasured. Wave 1 proved only that a 5.4 KB and a 9.4 KB chapter
// both cost about 52k, so agent overhead dominates at the small end.
// Wave 2 read ['epicurves', 'shiny_basics'], the two largest: 14 pairs, 101
// findings, 1,688,619 tokens, 120,616 per pair. With wave 1 that gives a cost
// model: tokens_per_pair ~= 45,900 + 1,121 * (English chapter KB). It predicts
// the older 9.6 KB 5-pair run at 56,700 against a measured 54,820.
// Wave 3 takes the next four largest, working down the size order.
// Wave 3 read the next four largest: 28 pairs, 171 findings, 3,226,830 tokens,
// 115,244 per pair. The cost model predicted 3.14M against that 3.23M, a 2.7% error.
// Wave 4 takes the four CHEAPEST remaining chapters, because the window is nearly
// spent and cheap-first completes twice the chapters per token.
// Wave 4 read the four cheapest: 28 pairs, 75 findings, 1,564,794 tokens, 55,885
// per pair. The cost model predicted 1.56M against that 1.5648M, a 0.3% error.
// Wave 5 continues cheap-first over the seven cheapest remaining chapters.
// Sized to a 5% allocation of the weekly budget at ~705,000 tokens per point.
// Wave 6, 2026-09-01, resumes Phase C after the reboot cleared /tmp/gate/prose.
// Cheap-first again: the four cheapest of the 15 remaining chapters.
// 28 pairs. The cost model puts this at 2,056,547 tokens, about 2.9 quota points.
// Phase A, the deterministic segmenter, is deliberately SKIPPED. It cannot touch
// the 45,900-token fixed overhead, which is 55% of the per-pair cost at these
// chapter sizes, and adopting it now would read the last 105 pairs by a method
// the first 231 were not read by.
// Wave 6 read 28 pairs, 142 findings, 2,428,408 tokens, 86,729 per pair. The cost
// model predicted 2,052,198 against that 2,428,408, an 18.3% UNDER-prediction and
// four times its worst earlier error. Multiply the model by 1.18 until a further
// batch revises the correction.
// Wave 7, 2026-09-01, continues cheap-first over the five cheapest remaining.
// 35 pairs. Bare model 2.73M, corrected 3.22M.
// Wave 7 read 35 pairs, 169 findings, 3,182,493 tokens, 90,928 per pair. Bare model
// 2,732,146, ratio 1.165. With wave 6's 1.183 over 63 pairs the correction is 1.173.
// Wave 8, 2026-09-01, takes four of the last six chapters, all of them large.
// 28 pairs. Bare model 2.57M, corrected 3.01M.
const STEMS = ['survival_analysis', 'survey_analysis', 'joining_matching', 'rmarkdown']

const SUMMARY = {
  type: 'object',
  additionalProperties: false,
  required: ['chapter', 'lang', 'en_segments', 'tr_segments', 'mapped', 'unmatched_en', 'unmatched_tr', 'findings_total', 'by_kind', 'wrote_file'],
  properties: {
    chapter: { type: 'string' },
    lang: { type: 'string' },
    en_segments: { type: 'integer' },
    tr_segments: { type: 'integer' },
    mapped: { type: 'integer' },
    unmatched_en: { type: 'integer' },
    unmatched_tr: { type: 'integer' },
    findings_total: { type: 'integer' },
    by_kind: {
      type: 'object', additionalProperties: false,
      required: ['untrue', 'missing', 'added', 'code_mismatch', 'alignment_mismatch'],
      properties: {
        untrue: { type: 'integer' }, missing: { type: 'integer' }, added: { type: 'integer' },
        code_mismatch: { type: 'integer' }, alignment_mismatch: { type: 'integer' },
      },
    },
    wrote_file: { type: 'string' },
  },
}

function prompt(stem, lang) {
  return `Compare one translated handbook chapter against its English original and record every prose difference. READ-ONLY on the repo: you MUST NOT edit any .qmd file.

ENGLISH:     ${REPO}/chapters/${stem}.qmd
TRANSLATION: ${REPO}/chapters/${stem}.${lang}.qmd   (language code: ${lang})

## Method

1. Split BOTH files into sections at markdown headings (lines matching ^#{1,6} followed by whitespace, OUTSIDE code chunks). Before matching heading text, STRIP the trailing attribute block: {#anchor}, {.unnumbered}, {#id .class}. 41 percent of headings carry one and they are often untranslated, so they align the sections for you.
2. Align sections in order. Most pairs align exactly. Where they do not, align on position and on any untranslated {#anchor} id, and record the leftovers as unmatched.
3. Inside each section the unit of comparison is a SEGMENT: a run of prose between two code-chunk boundaries. A code chunk opens on a line matching ^\\s*\`\`\`+\\{ and closes on ^\\s*\`\`\`+\\s*$. Prose before the first chunk, between chunks, and after the last chunk are separate segments.
4. For each aligned segment pair, state to yourself what the English says and what the translation says, then compare.

## What to record as a finding

- untrue    : the translation states something the English does not support, or that the code beside it contradicts
- missing   : the translation omits a substantive point the English makes
- added     : the translation contains content the English does not have, EVEN IF correct and useful
- code_mismatch : the prose describes code that is not in the chunk beside it
- alignment_mismatch : a section or segment on either side has no counterpart

## What is NOT a finding. Read this twice.

- Wording, register, tone, sentence order within a segment, ordinary translator paraphrase.
- A PARAGRAPH SPLIT IS NOT AN ADDITION. Japanese and Vietnamese routinely split one English paragraph into two or three shorter ones. Same content, more paragraphs, no finding. Only record 'added' when there is genuinely new PROPOSITIONAL CONTENT.
- A translated identifier, variable name, or dataset label. Portuguese caso_tabela for English case_table is a translator's choice.
- A localised link label or a translated heading.

## Every finding MUST carry

- en_span and tr_span as "file:startline-endline" using the REAL line numbers of those files.
- proposition: ONE atomic claim, present on one side and absent or contradicted on the other. One claim per finding. Split compound differences into separate findings.
- reader_consequence: what a reader of that language does wrong, or misses, because of this.
- confidence: high, medium or low.

Do not report a finding you cannot anchor to exact line ranges on both sides. If you cannot anchor it, it is not a finding.

## Output

Write a JSON file to /tmp/gate/prose/${stem}.${lang}.json with this exact shape:

{"chapter":"${stem}","lang":"${lang}",
 "coverage":[{"en_segment_id":"S1.P1","tr_segment_id":"S1.P1","relation":"1-1","confidence":"high","reviewed":true}],
 "findings":[{"heading":"...","segment_index":"S3.P2","kind":"untrue","en_span":"chapters/${stem}.qmd:120-126","tr_span":"chapters/${stem}.${lang}.qmd:131-138","proposition":"...","reader_consequence":"...","confidence":"high"}]}

The coverage array MUST account for EVERY segment on BOTH sides. relation is one of 1-1, 1-many, many-1, unmatched-en, unmatched-tr. A segment you did not read is a coverage failure, not an absent finding. If a pair genuinely has no findings, write the file with "findings":[] and a full coverage array.

Then return the structured summary. findings_total MUST equal the length of the findings array you wrote.`
}

const PAIRS = []
for (const stem of STEMS) for (const lang of LANGS) PAIRS.push({ stem, lang })

log(`BATCH: ${PAIRS.length} pairs = ${STEMS.length} stems (${STEMS.join(', ')}) x ${LANGS.length} languages`)
log(`This batch is a hard slice. It reads ONLY these ${STEMS.length} chapters, not the 48-stem corpus.`)

phase('Find')

const results = await parallel(PAIRS.map(p => () =>
  agent(prompt(p.stem, p.lang), {
    label: `${p.stem}.${p.lang}`,
    phase: 'Find',
    schema: SUMMARY,
  }).then(r => r ? { ...r, ok: true } : { chapter: p.stem, lang: p.lang, ok: false })
))

const ok = results.filter(r => r && r.ok)
const failed = results.filter(r => !r || !r.ok)

const totals = { untrue: 0, missing: 0, added: 0, code_mismatch: 0, alignment_mismatch: 0 }
let findings = 0, segsEn = 0, segsTr = 0, unmatched = 0
for (const r of ok) {
  findings += r.findings_total
  segsEn += r.en_segments
  segsTr += r.tr_segments
  unmatched += r.unmatched_en + r.unmatched_tr
  for (const k of Object.keys(totals)) totals[k] += r.by_kind[k]
}

const byLang = {}
for (const r of ok) {
  byLang[r.lang] = byLang[r.lang] || { pairs: 0, findings: 0 }
  byLang[r.lang].pairs++
  byLang[r.lang].findings += r.findings_total
}

log(`pairs attempted ${PAIRS.length}, RETURNED ${ok.length}, no return ${failed.length}`)
log(`findings ${findings} | untrue ${totals.untrue} missing ${totals.missing} added ${totals.added} code_mismatch ${totals.code_mismatch} alignment ${totals.alignment_mismatch}`)
log(`segments: en ${segsEn}, tr ${segsTr}, unmatched ${unmatched}`)
if (failed.length) log(`NO RETURN VALUE: ${failed.map(f => f.chapter + '.' + f.lang).join(', ')} -- check /tmp/gate/prose before calling these failed`)
log(`RECONCILE NOW: ls /tmp/gate/prose/*.json | wc -l . The count below is return-based and MAY undercount.`)

return {
  accounting: 'RETURN-BASED. Reconcile against /tmp/gate/prose/*.json before you trust pairs_returned.',
  batch_stems: STEMS,
  pairs_attempted: PAIRS.length,
  pairs_returned: ok.length,
  pairs_no_return: failed.map(f => `${f.chapter}.${f.lang}`),
  findings_total: findings,
  by_kind: totals,
  by_lang: byLang,
  segments_en: segsEn,
  segments_tr: segsTr,
  unmatched_segments: unmatched,
}
