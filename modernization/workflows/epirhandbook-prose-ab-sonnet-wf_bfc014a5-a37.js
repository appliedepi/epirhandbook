export const meta = {
  name: 'epirhandbook-prose-ab-sonnet',
  description: 'A/B four already-swept pairs on Sonnet medium against the Opus baseline',
  phases: [{ title: 'SonnetAB', detail: 'same prompt, model sonnet, effort medium, separate output dir' }],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'

const PAIRS = [
  { stem: 'basics', lang: 'tr' },
  { stem: 'basics', lang: 'jp' },
  { stem: 'collaboration', lang: 'fr' },
  { stem: 'data_table', lang: 'ru' },
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
- A PARAGRAPH SPLIT IS NOT AN ADDITION. Japanese and Vietnamese routinely split one English paragraph into two or three shorter ones. Same content, more paragraphs, no finding. Record 'added' only for genuinely new PROPOSITIONAL CONTENT.
- A translated identifier or dataset label. A localised link label. A translated heading.

## Every finding MUST carry

- en_span and tr_span as "file:startline-endline" with REAL line numbers.
- proposition: ONE atomic claim, present on one side and absent or contradicted on the other.
- reader_consequence: what a reader of that language does wrong or misses.
- confidence: high, medium or low.

A finding you cannot anchor to exact line ranges on both sides is not a finding.

## Output

Write /tmp/gate/prose-sonnet/${stem}.${lang}.json with exactly:

{"chapter":"${stem}","lang":"${lang}",
 "coverage":[{"en_segment_id":"S1.P1","tr_segment_id":"S1.P1","relation":"1-1","confidence":"high","reviewed":true}],
 "findings":[{"heading":"...","segment_index":"S3.P2","kind":"untrue","en_span":"chapters/${stem}.qmd:120-126","tr_span":"chapters/${stem}.${lang}.qmd:131-138","proposition":"...","reader_consequence":"...","confidence":"high"}]}

coverage MUST account for EVERY segment on BOTH sides. relation is 1-1, 1-many, many-1, unmatched-en or unmatched-tr. If there are no findings, write "findings":[] with a full coverage array.

Then return the structured summary. findings_total MUST equal the findings array length.`
}

log('A/B: 4 pairs, model sonnet, effort medium, same prompt as the Opus baseline')
phase('SonnetAB')

const results = await parallel(PAIRS.map(p => () =>
  agent(prompt(p.stem, p.lang), {
    label: `sonnet:${p.stem}.${p.lang}`,
    phase: 'SonnetAB',
    schema: SUMMARY,
    model: 'sonnet',
    effort: 'medium',
  }).then(r => r ? { ...r, ok: true } : { chapter: p.stem, lang: p.lang, ok: false })
))

const ok = results.filter(r => r && r.ok)
for (const r of ok) {
  log(`${r.chapter}.${r.lang}: findings ${r.findings_total} | untrue ${r.by_kind.untrue} missing ${r.by_kind.missing} added ${r.by_kind.added} code ${r.by_kind.code_mismatch} | segments en ${r.en_segments} tr ${r.tr_segments}`)
}

return {
  attempted: PAIRS.length,
  returned: ok.length,
  failed: results.filter(r => !r || !r.ok).map(f => `${f.chapter}.${f.lang}`),
  per_pair: ok.map(r => ({ pair: `${r.chapter}.${r.lang}`, findings: r.findings_total, by_kind: r.by_kind, en_segments: r.en_segments, tr_segments: r.tr_segments })),
}
