export const meta = {
  name: 'epirhandbook-prose-drift-finish-started',
  description: 'Finish the 5 outstanding pairs in the two partially-completed chapters',
  phases: [{ title: 'Finish', detail: 'directories.tr and editorial_style es/jp/tr/vn' }],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'

const PAIRS = [
  { stem: 'directories', lang: 'tr' },
  { stem: 'editorial_style', lang: 'es' },
  { stem: 'editorial_style', lang: 'jp' },
  { stem: 'editorial_style', lang: 'tr' },
  { stem: 'editorial_style', lang: 'vn' },
]

const SUMMARY = {
  type: 'object',
  additionalProperties: false,
  required: ['chapter', 'lang', 'en_segments', 'tr_segments', 'mapped', 'unmatched_en', 'unmatched_tr', 'findings_total', 'by_kind', 'wrote_file'],
  properties: {
    chapter: { type: 'string' }, lang: { type: 'string' },
    en_segments: { type: 'integer' }, tr_segments: { type: 'integer' },
    mapped: { type: 'integer' }, unmatched_en: { type: 'integer' }, unmatched_tr: { type: 'integer' },
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

1. Split BOTH files into sections at markdown headings (^#{1,6} then whitespace, OUTSIDE code chunks). Before matching heading text, STRIP the trailing attribute block: {#anchor}, {.unnumbered}, {#id .class}.
2. Align sections in order. Where they do not align, use position and any untranslated {#anchor} id, and record leftovers as unmatched.
3. Inside each section the unit is a SEGMENT: a run of prose between two code-chunk boundaries. A chunk opens on ^\\s*\`\`\`+\\{ and closes on ^\\s*\`\`\`+\\s*$.
4. For each aligned segment pair, state what the English says and what the translation says, then compare.

## Finding kinds

- untrue    : the translation states something the English does not support, or that the code beside it contradicts
- missing   : the translation omits a substantive point the English makes
- added     : the translation contains content the English does not have, EVEN IF correct and useful
- code_mismatch : the prose describes code that is not in the chunk beside it
- alignment_mismatch : a section or segment on either side has no counterpart

## NOT findings. Read twice.

- Wording, register, tone, sentence order within a segment, ordinary paraphrase.
- A PARAGRAPH SPLIT IS NOT AN ADDITION. Same content in more paragraphs is no finding. Record 'added' only for genuinely new PROPOSITIONAL CONTENT.
- A translated identifier or dataset label. A localised link label. A translated heading.

## Every finding MUST carry

- en_span and tr_span as "file:startline-endline" with REAL line numbers.
- proposition: ONE atomic claim, present on one side and absent or contradicted on the other.
- reader_consequence: what a reader of that language does wrong or misses.
- confidence: high, medium or low.

A finding you cannot anchor to exact line ranges on both sides is not a finding.

## Output

Write /tmp/gate/prose/${stem}.${lang}.json with exactly:

{"chapter":"${stem}","lang":"${lang}",
 "coverage":[{"en_segment_id":"S1.P1","tr_segment_id":"S1.P1","relation":"1-1","confidence":"high","reviewed":true}],
 "findings":[{"heading":"...","segment_index":"S3.P2","kind":"untrue","en_span":"chapters/${stem}.qmd:120-126","tr_span":"chapters/${stem}.${lang}.qmd:131-138","proposition":"...","reader_consequence":"...","confidence":"high"}]}

coverage MUST account for EVERY segment on BOTH sides. relation is 1-1, 1-many, many-1, unmatched-en or unmatched-tr. If there are no findings, write "findings":[] with a full coverage array.

Then return the structured summary. findings_total MUST equal the findings array length.`
}

log(`finishing ${PAIRS.length} outstanding pairs in 2 partially-completed chapters`)
phase('Finish')

const results = await parallel(PAIRS.map(p => () =>
  agent(prompt(p.stem, p.lang), { label: `${p.stem}.${p.lang}`, phase: 'Finish', schema: SUMMARY })
    .then(r => r ? { ...r, ok: true } : { chapter: p.stem, lang: p.lang, ok: false })
))

const ok = results.filter(r => r && r.ok)
const failed = results.filter(r => !r || !r.ok)
let findings = 0
const totals = { untrue: 0, missing: 0, added: 0, code_mismatch: 0, alignment_mismatch: 0 }
for (const r of ok) { findings += r.findings_total; for (const k of Object.keys(totals)) totals[k] += r.by_kind[k] }

log(`returned ${ok.length} of ${PAIRS.length}, findings ${findings}`)
if (failed.length) log(`FAILED: ${failed.map(f => f.chapter + '.' + f.lang).join(', ')}`)

return { attempted: PAIRS.length, returned: ok.length, failed: failed.map(f => `${f.chapter}.${f.lang}`), findings_total: findings, by_kind: totals }
