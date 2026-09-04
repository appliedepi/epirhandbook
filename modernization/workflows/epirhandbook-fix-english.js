export const meta = {
  name: 'epirhandbook-fix-english',
  description: 'Fix the recorded defects in the ENGLISH source chapters, one opus xhigh agent per chapter. The first pass that may edit an English file.',
  phases: [{ title: 'Fix', detail: 'one agent per English chapter, writes fix-pass/src-<chapter>.json' }],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['chapter', 'n', 'fixed', 'rejected', 'wrote_file'],
  properties: { chapter: { type: 'string' }, n: { type: 'integer' }, fixed: { type: 'integer' }, rejected: { type: 'integer' }, wrote_file: { type: 'string' } },
}

function prompt(p) {
  const id = `src-${p.chapter}`
  const list = p.defects.map((d, i) => `${i + 1}. ${d}`).join('\n')
  return `You fix recorded defects in ONE English chapter of the Epidemiologist R Handbook (Quarto .qmd).

Repository: ${REPO}
File, the ONLY file you may edit: chapters/${p.chapter}.qmd
Defects, found while the seven translations were being aligned to this chapter; each was verified by a reviewer against this file and its code:

${list}

For each defect: read the place in the file, confirm it, and make the smallest edit that makes the prose true to the code beside it, or the code valid, or the link resolve. Where prose and code disagree, the CODE is right unless the defect says otherwise: change the prose. An eval=F pseudo-code chunk that does not parse gets the missing or extra bracket fixed and nothing else; a deliberate fragment such as a single scale_x_date() argument may be closed so it parses. For a dead link, target the page or anchor the sentence means; for an empty link target, the documentation page the sentence names, if you know its URL with certainty, otherwise drop the link markup and keep the words.

Verdict per defect: fixed, with the exact old and new text, or rejected with one sentence why (for example, the defect is not in this file as described).

Rules. Each is a MUST.
1. Edit only chapters/${p.chapter}.qmd. Never a translated file.
2. Change the fewest lines. No reflow. Keep trailing double spaces, {#anchor} blocks, chunk options.
3. Use the Edit tool with exact old_string values. Never rewrite the file with Write. Never run git, quarto or R.

Output. MUST. Write ${REPO}/modernization/findings/fix-pass/${id}.json BEFORE you return:
{"batch":"${id}","lang":"en","kind":"source","results":[{"id":"${id}#1","verdict":"fixed","reason":"one sentence","file":"chapters/${p.chapter}.qmd","old":"<exact text replaced>","new":"<exact replacement>"}, ...]}
One entry per defect, ids ${id}#1 to ${id}#${p.defects.length} in the order above. Then return the structured summary.`
}

const CHAPTERS = args && args.chapters ? args.chapters : []
if (!CHAPTERS.length) throw new Error('args.chapters is empty')
log(`ENGLISH: ${CHAPTERS.length} chapters, ${CHAPTERS.reduce((s, c) => s + c.defects.length, 0)} defects`)
phase('Fix')
const results = await parallel(CHAPTERS.map(p => () =>
  agent(prompt(p), { label: p.chapter, phase: 'Fix', schema: SUMMARY, model: 'opus', effort: 'xhigh' })
    .then(r => r ? { ...r, ok: true } : { chapter: p.chapter, ok: false })
))
const ok = results.filter(r => r && r.ok)
log(`RETURNED ${ok.length} of ${CHAPTERS.length}; fixed ${ok.reduce((s, r) => s + r.fixed, 0)} rejected ${ok.reduce((s, r) => s + r.rejected, 0)}`)
return { accounting: 'RETURN-BASED. Count fix-pass/src-*.json and read the diffs.', returned: ok.map(r => r.chapter), no_return: results.filter(r => !r || !r.ok).map(r => r.chapter) }
