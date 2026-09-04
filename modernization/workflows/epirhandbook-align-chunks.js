export const meta = {
  name: 'epirhandbook-align-chunks',
  description: 'Align the code chunks of a translated chapter whose chunk count differs from the English, so sync-chunks.py can then make them identical. One opus xhigh agent per file.',
  phases: [{ title: 'Align', detail: 'one agent per misaligned translated chapter, writes fix-pass/aln-<chapter>.<lang>.json' }],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGNAME = { es: 'Spanish', fr: 'French', jp: 'Japanese', pt: 'Portuguese', ru: 'Russian', tr: 'Turkish', vn: 'Vietnamese' }
const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['file', 'chunks_before', 'chunks_after', 'english_chunks', 'wrote_file'],
  properties: { file: { type: 'string' }, chunks_before: { type: 'integer' }, chunks_after: { type: 'integer' }, english_chunks: { type: 'integer' }, wrote_file: { type: 'string' } },
}

function prompt(p) {
  const L = LANGNAME[p.lang]
  const id = `aln-${p.chapter}.${p.lang}`
  return `You align the R code chunks of one ${L} chapter of the Epidemiologist R Handbook with its English source, so that a script can then make every chunk identical to the English.

Repository: ${REPO}
Translated file, the ONLY file you may edit: chapters/${p.chapter}.${p.lang}.qmd  (${p.tr_chunks} chunks)
English reference, read-only: chapters/${p.chapter}.qmd  (${p.en_chunks} chunks)

A chunk is a fenced block that opens with a line matching \`\`\`{r ...} and closes with \`\`\`. The two files must end up with the SAME NUMBER of chunks in the SAME ORDER, each ${L} chunk at the place of its English counterpart. English is the reference.

Method:
1. List the chunks of both files in order, with the first code line of each, and pair them up.
2. Where the ${L} file has a chunk the English lacks, delete it, together with any ${L} prose that only introduces it. Where the ${L} file lacks a chunk the English has, insert the English chunk verbatim at the matching place; if the English has a sentence introducing it that the ${L} prose lacks, add that sentence translated into ${L}.
3. Where a ${L} chunk is at the wrong place, move it.
4. Do not edit the code inside chunks that already pair up: the sync script does that next. Do not reflow prose you are not otherwise changing. Never edit the English file.
5. Use the Edit tool with exact old_string values. Never rewrite the file with Write. Never run git, quarto or R.

Output. MUST. Write ${REPO}/modernization/findings/fix-pass/${id}.json BEFORE you return:
{"batch":"${id}","lang":"${p.lang}","kind":"align","results":[{"id":"${id}#1","verdict":"fixed","reason":"what you deleted, inserted or moved, one sentence per chunk","file":"chapters/${p.chapter}.${p.lang}.qmd","old":"<first exact old_string you passed to Edit>","new":"<its replacement>"}]}
Then return the structured summary with the chunk counts before and after; chunks_after MUST equal english_chunks.`
}

const PAIRS = args && args.pairs ? args.pairs : []
if (!PAIRS.length) throw new Error('args.pairs is empty')
log(`ALIGN: ${PAIRS.length} misaligned chapters`)
phase('Align')
const results = await parallel(PAIRS.map(p => () =>
  agent(prompt(p), { label: `${p.chapter}.${p.lang}`, phase: 'Align', schema: SUMMARY, model: 'opus', effort: 'xhigh' })
    .then(r => r ? { ...r, ok: true } : { file: `${p.chapter}.${p.lang}`, ok: false })
))
const ok = results.filter(r => r && r.ok)
log(`RETURNED ${ok.length} of ${PAIRS.length}. Re-run sync-chunks.py --dry-run: every file must now align.`)
return { accounting: 'RETURN-BASED. Check chunk counts with sync-chunks.py --dry-run.', returned: ok.map(r => r.file), no_return: results.filter(r => !r || !r.ok).map(r => r.file) }
