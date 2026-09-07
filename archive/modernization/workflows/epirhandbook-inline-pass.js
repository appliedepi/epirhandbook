export const meta = {
  name: 'epirhandbook-inline-pass',
  description: 'Inline-code pass: every `span` in translated prose that occurs nowhere in the English chapter. One opus xhigh agent per batch sorts each span into fix, keep or noise, and edits the fixes.',
  phases: [
    { title: 'Fix', detail: 'one agent per batch of at most 40 spans, edits prose only, writes fix-pass/<batch>.json' },
  ],
}

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGNAME = { es: 'Spanish', fr: 'French', jp: 'Japanese', pt: 'Portuguese', ru: 'Russian', tr: 'Turkish', vn: 'Vietnamese' }

const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['batch', 'n', 'fixed', 'rejected', 'deferred', 'wrote_file'],
  properties: { batch: { type: 'string' }, n: { type: 'integer' }, fixed: { type: 'integer' }, rejected: { type: 'integer' }, deferred: { type: 'integer' }, wrote_file: { type: 'string' } },
}

function prompt(b) {
  const L = LANGNAME[b.lang]
  return `You review inline code spans in ${L} prose of the Epidemiologist R Handbook (Quarto .qmd) and fix the wrong ones.

Repository: ${REPO}
Batch: ${b.id}  (language ${b.lang} = ${L}, ${b.n} spans)
Evidence file, read it whole, once: /tmp/inline/batches/${b.id}.md
Files this batch MAY edit, and no others: ${b.files.join(', ')}

## What the evidence is

Every \`span\` in the ${L} prose of these chapters that occurs NOWHERE in the English chapter, neither in its prose nor in its code. The code chunks of every ${L} chapter were just made identical to the English chunks, so any object, column, function, argument or file name that a span names must now match what the English uses. Each span comes with the ${L} paragraph it sits in. Read the English chapter chapters/<chapter>.qmd at the matching place for what the span should be.

## Your verdict, per span

- fixed: the span is wrong. Edit it. Cases: a translated or misspelled function, argument, keyword, object, column, dataset, package or file name (liste for list, spilit_by, lineliset, DOĞRU for TRUE, faixa_etaria for age_group); an R output label translated (f grubunda ortalama for mean in group f); a stray space inside a call (render () for render()); a translated string that the code beside it uses literally.
- rejected: the span is right as it is. Cases: a placeholder the reader replaces (setwd("klasör konumu"), rename(nouveau_nom = ancien_nom), ?función); a ${L} word the author put in code font on purpose; punctuation or markup noise (\`、\`, \`[ ]\`, \`\\\`). Say which case in one sentence.
- deferred: wrong, but the fix needs more than the span (a sentence rewrite, a code change). One sentence what it needs.

## Rules. Each is a MUST.

1. Edit ONLY the files listed above, and ONLY prose: never a line inside a code chunk, never an English file.
2. Change the span text and nothing else on the line, unless the sentence around it names the same wrong thing again. Keep the backticks. Keep trailing double spaces.
3. Use the Edit tool with an exact old_string. Never rewrite a file with Write. Never run git, quarto or R.
4. When the same wrong span occurs several times in one file, fix every occurrence and record them under the one span id, with the count in "reason".

## Output. MUST.

Write ${REPO}/modernization/findings/fix-pass/${b.id}.json BEFORE you return:
{"batch":"${b.id}","lang":"${b.lang}","kind":"inline",
 "results":[{"id":"${b.id}#1","verdict":"fixed","reason":"one sentence","file":"chapters/<chapter>.${b.lang}.qmd","old":"<exact text replaced>","new":"<exact replacement>"},
            {"id":"${b.id}#2","verdict":"rejected","reason":"one sentence","file":null,"old":null,"new":null}]}
One entry per span, ids ${b.id}#1 to ${b.id}#${b.n} in evidence order. Then return the structured summary. fixed + rejected + deferred MUST equal ${b.n}.`
}

const BATCHES = args && args.batches ? args.batches : []
if (!BATCHES.length) throw new Error('args.batches is empty')
const files = new Set()
for (const b of BATCHES) for (const f of b.files) { if (files.has(f)) throw new Error('two batches in one wave share ' + f); files.add(f) }
log(`INLINE WAVE ${args.wave}: ${BATCHES.length} batches, ${BATCHES.reduce((s, b) => s + b.n, 0)} spans`)
phase('Fix')
const results = await parallel(BATCHES.map(b => () =>
  agent(prompt(b), { label: b.id, phase: 'Fix', schema: SUMMARY, model: 'opus', effort: 'xhigh' })
    .then(r => r ? { ...r, ok: true } : { batch: b.id, ok: false })
))
const ok = results.filter(r => r && r.ok)
const t = { fixed: 0, rejected: 0, deferred: 0 }
for (const r of ok) { t.fixed += r.fixed; t.rejected += r.rejected; t.deferred += r.deferred }
log(`RETURNED ${ok.length} of ${BATCHES.length}; fixed ${t.fixed} rejected ${t.rejected} deferred ${t.deferred}. RECONCILE NOW.`)
return { accounting: 'RETURN-BASED. Run reconcile-fix-pass.py.', wave: args.wave, returned: ok.map(r => r.batch), no_return: results.filter(r => !r || !r.ok).map(r => r.batch), totals: t }
