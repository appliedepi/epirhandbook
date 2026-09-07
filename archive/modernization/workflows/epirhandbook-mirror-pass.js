export const meta = {
  name: 'epirhandbook-mirror-pass',
  description: 'After the English source fixes: one opus xhigh agent per language makes the translated prose follow the corrected English at the listed places, and finishes the inline-code spans deferred to a sentence rewrite.',
  phases: [{ title: 'Fix', detail: 'one agent per language, prose only, writes fix-pass/mir-<lang>.json' }],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGNAME = { es: 'Spanish', fr: 'French', jp: 'Japanese', pt: 'Portuguese', ru: 'Russian', tr: 'Turkish', vn: 'Vietnamese' }
const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['lang', 'n', 'fixed', 'rejected', 'deferred', 'wrote_file'],
  properties: { lang: { type: 'string' }, n: { type: 'integer' }, fixed: { type: 'integer' }, rejected: { type: 'integer' }, deferred: { type: 'integer' }, wrote_file: { type: 'string' } },
}

function prompt(p) {
  const L = LANGNAME[p.lang]
  const id = `mir-${p.lang}`
  const list = p.items.map((d, i) => `${i + 1}. [${d.file}] ${d.task}`).join('\n')
  return `You finish the ${L} translation of the Epidemiologist R Handbook at ${p.items.length} listed places. Prose only.

Repository: ${REPO}
Files you MAY edit: ${p.files.join(', ')}. No other file, never an English chapters/<chapter>.qmd.
The English chapters were corrected today; read the English at each place FIRST and make the ${L} say what the corrected English says. The code chunks of the ${L} chapters are already identical to the English; do not touch a line inside a code chunk.

${list}

Verdict per item: fixed, with the exact old and new text of the first edit; rejected, one sentence, if the ${L} already says what the corrected English says; deferred, one sentence, if it needs more than you may do.

Rules. Each is a MUST. Change the fewest lines. No reflow of untouched lines; a fixed-width grid table may be re-aligned only within the rows you change. Keep trailing double spaces, backticks, {#anchor} blocks. Use the Edit tool with exact old_string values; never Write a whole file; never run git, quarto or R.

Output. MUST. Write ${REPO}/modernization/findings/fix-pass/${id}.json BEFORE you return:
{"batch":"${id}","lang":"${p.lang}","kind":"mirror","results":[{"id":"${id}#1","verdict":"fixed","reason":"one sentence","file":"chapters/<chapter>.${p.lang}.qmd","old":"<exact text replaced>","new":"<exact replacement>"}, ...]}
One entry per item, ids ${id}#1 to ${id}#${p.items.length} in the order above. Then return the structured summary.`
}

const LANGS = args && args.langs ? args.langs : []
if (!LANGS.length) throw new Error('args.langs is empty')
log(`MIRROR: ${LANGS.length} languages, ${LANGS.reduce((s, p) => s + p.items.length, 0)} items`)
phase('Fix')
const results = await parallel(LANGS.map(p => () =>
  agent(prompt(p), { label: p.lang, phase: 'Fix', schema: SUMMARY, model: 'opus', effort: 'xhigh' })
    .then(r => r ? { ...r, ok: true } : { lang: p.lang, ok: false })
))
const ok = results.filter(r => r && r.ok)
log(`RETURNED ${ok.length} of ${LANGS.length}; fixed ${ok.reduce((s, r) => s + r.fixed, 0)} rejected ${ok.reduce((s, r) => s + r.rejected, 0)} deferred ${ok.reduce((s, r) => s + r.deferred, 0)}`)
return { accounting: 'RETURN-BASED. Count fix-pass/mir-*.json.', returned: ok.map(r => r.lang), no_return: results.filter(r => !r || !r.ok).map(r => r.lang) }
