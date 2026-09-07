export const meta = {
  name: 'epirhandbook-prose-drift-find',
  description: 'Read all 336 chapter-language pairs against English and record every prose difference',
  phases: [
    { title: 'Find', detail: 'one agent per chapter-language pair, writes JSON to /tmp/gate/prose' },
  ],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGS = ['es', 'fr', 'jp', 'pt', 'ru', 'tr', 'vn']

const STEMS = [
  'age_pyramid', 'basics', 'characters_strings', 'cleaning', 'collaboration',
  'combination_analysis', 'contact_tracing', 'data_table', 'data_used', 'dates',
  'deduplication', 'diagrams', 'directories', 'editorial_style', 'epicurves',
  'errors', 'factors', 'flexdashboard', 'ggplot_basics', 'ggplot_tips',
  'grouping', 'heatmaps', 'help', 'importing', 'interactive_plots',
  'iteration', 'joining_matching', 'missing_data', 'moving_average', 'network_drives',
  'packages_suggested', 'phylogenetic_trees', 'pivoting', 'r_projects', 'regression',
  'reportfactory', 'rmarkdown', 'shiny_basics', 'standardization', 'stat_tests',
  'survey_analysis', 'survival_analysis', 'tables_descriptive', 'tables_presentation',
  'time_series', 'transition_to_r', 'transmission_chains', 'writing_functions',
]

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

log(`Phase 1b find stage: ${PAIRS.length} pairs, ${STEMS.length} stems x ${LANGS.length} languages`)

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

log(`pairs attempted ${PAIRS.length}, returned ${ok.length}, FAILED ${failed.length}`)
log(`findings ${findings} | untrue ${totals.untrue} missing ${totals.missing} added ${totals.added} code_mismatch ${totals.code_mismatch} alignment ${totals.alignment_mismatch}`)
log(`segments: en ${segsEn}, tr ${segsTr}, unmatched ${unmatched}`)
if (failed.length) log(`FAILED PAIRS (coverage gap, MUST be re-run): ${failed.map(f => f.chapter + '.' + f.lang).join(', ')}`)

return {
  pairs_attempted: PAIRS.length,
  pairs_returned: ok.length,
  pairs_failed: failed.map(f => `${f.chapter}.${f.lang}`),
  findings_total: findings,
  by_kind: totals,
  by_lang: byLang,
  segments_en: segsEn,
  segments_tr: segsTr,
  unmatched_segments: unmatched,
}
