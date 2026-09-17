export const meta = {
  name: 'epirhandbook-align-headings',
  description: 'Align the heading sequence of a translated chapter with the English: same count, same levels, same order. One opus xhigh agent per file.',
  phases: [{ title: 'Align', detail: 'one agent per chapter, edits heading lines only, writes fix-pass/hdg-<chapter>.<lang>.json' }],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGNAME = { es: 'Spanish', fr: 'French', jp: 'Japanese', pt: 'Portuguese', ru: 'Russian', tr: 'Turkish', vn: 'Vietnamese' }
const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['file', 'headings_before', 'headings_after', 'english_headings', 'wrote_file'],
  properties: { file: { type: 'string' }, headings_before: { type: 'integer' }, headings_after: { type: 'integer' }, english_headings: { type: 'integer' }, wrote_file: { type: 'string' } },
}

function prompt(p) {
  const L = LANGNAME[p.lang]
  const id = `hdg-${p.chapter}.${p.lang}`
  return `You align the headings of one ${L} chapter of the Epidemiologist R Handbook with its English source.

Repository: ${REPO}
Translated file, the ONLY file you may edit: chapters/${p.chapter}.${p.lang}.qmd
English reference, read-only: chapters/${p.chapter}.qmd
Known difference: ${p.note}

A heading is a line that starts with one to six # characters followed by a space, OUTSIDE code chunks. The ${L} file must end up with the SAME sequence of heading levels as the English, in the same order: the same count, and level for level. Heading TEXT stays in ${L}.

Method:
1. List the headings of both files in order with their levels and pair them up.
2. Where a ${L} heading has the wrong level, change only its # characters.
3. Where the ${L} file has a heading the English lacks, remove that heading line (keep the prose under it unless it exists only to introduce that heading). Where it lacks a heading the English has, insert one at the matching place with the English heading text translated into ${L}, and copy the English attribute block, such as {#anchor} or {.unnumbered}, verbatim.
4. Change nothing else. Never edit inside a code chunk. Never reflow prose. Never edit the English file.
5. Use the Edit tool with exact old_string values. Never rewrite the file with Write. Never run git, quarto or R.

Output. MUST. Write ${REPO}/modernization/findings/fix-pass/${id}.json BEFORE you return:
{"batch":"${id}","lang":"${p.lang}","kind":"headings","results":[{"id":"${id}#1","verdict":"fixed","reason":"one sentence per heading changed","file":"chapters/${p.chapter}.${p.lang}.qmd","old":"<first exact old_string>","new":"<its replacement>"}]}
Then return the structured summary. headings_after MUST equal english_headings.`
}

const PAIRS = args && args.pairs ? args.pairs : []
if (!PAIRS.length) throw new Error('args.pairs is empty')
log(`HEADINGS: ${PAIRS.length} chapters`)
phase('Align')
const results = await parallel(PAIRS.map(p => () =>
  agent(prompt(p), { label: `${p.chapter}.${p.lang}`, phase: 'Align', schema: SUMMARY, model: 'opus', effort: 'xhigh' })
    .then(r => r ? { ...r, ok: true } : { file: `${p.chapter}.${p.lang}`, ok: false })
))
const ok = results.filter(r => r && r.ok)
log(`RETURNED ${ok.length} of ${PAIRS.length}. Verify the heading sequences mechanically.`)
return { accounting: 'RETURN-BASED. Verify heading sequences against the English.', returned: ok.map(r => r.file), no_return: results.filter(r => !r || !r.ok).map(r => r.file) }
