export const meta = {
  name: 'epirhandbook-fix-pass-wave',
  description: 'Prose fix pass, one wave of batches. Each agent verifies and fixes at most 20 findings of one language and one kind. Hard-sliced by args.',
  phases: [
    { title: 'Fix', detail: 'one opus xhigh agent per batch, edits chapters/<chapter>.<lang>.qmd, writes fix-pass/<batch>.json' },
  ],
}

// ONE WAVE. args.batches holds ONLY this wave's batches, built by
// modernization/make-batches.py so that no two batches share a file.
// That is the hard slice from modernization/RESUME.md section 4.
//
// Defect-2 mitigation is NOT here: a workflow script cannot read disk. The
// orchestrator MUST run modernization/reconcile-fix-pass.py on the batch ids
// after this returns. The result file is the artifact; the return value is a
// report about it.

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGNAME = { es: 'Spanish', fr: 'French', jp: 'Japanese', pt: 'Portuguese', ru: 'Russian', tr: 'Turkish', vn: 'Vietnamese' }

const SUMMARY = {
  type: 'object',
  additionalProperties: false,
  required: ['batch', 'n', 'fixed', 'rejected', 'deferred', 'wrote_file'],
  properties: {
    batch: { type: 'string' },
    n: { type: 'integer' },
    fixed: { type: 'integer' },
    rejected: { type: 'integer' },
    deferred: { type: 'integer' },
    wrote_file: { type: 'string' },
  },
}

function prompt(b) {
  const L = LANGNAME[b.lang]
  return `You verify AND fix, in ONE pass, one batch of findings from the epiRhandbook prose sweep.

Repository: ${REPO}
Batch: ${b.id}  (language ${b.lang} = ${L}, kind ${b.kind}, ${b.n} findings)
Evidence file, read it whole, once: /tmp/fixpass/batches/${b.id}.md
Files this batch MAY edit, and no others: ${b.files.join(', ')}

## What a finding is

Each finding is ONE earlier agent's UNVERIFIED claim that the ${L} translation differs from the English reference at the marked lines. The evidence file gives you, per finding: the finder's proposition, the reader consequence it claimed, the English span with 8 lines of context, and the ${L} span with 8 lines of context. Both were cut mechanically from the files at commit 52442a79.

## Your verdict, per finding

Decide from the evidence. Exactly one of:

- fixed: the finding is correct. Edit the ${L} file so that it says what the English says, in fluent ${L} that matches the register of the surrounding translation.
- rejected: the finding is wrong, or the difference is not a defect. Do NOT edit. Give the reason in one sentence. Not a defect: ordinary translator paraphrase, register, sentence order inside a segment, a paragraph split, a translated identifier or dataset label, a localised link label, a translated heading.
- deferred: the finding is correct, but the fix is outside the permissions below, or you cannot find the ${L} span text in the current file. Do NOT edit. Say what it needs in one sentence.

A rejection is a result, not a failure. Do not fix anything to make a count look better. Do not "improve" text that no finding names.

## What each kind means for the fix

- untrue: the translation asserts something the English does not. Make it say what the English says.
- missing: the translation drops a point the English makes. Add it, translated into ${L}, at the matching place.
- added: the translation carries content with no English source. Remove it. English is the reference, and the owner's standing decision is that translator additions are removed even when they are correct and useful.
- code_mismatch: the prose describes something the code chunk beside it does not do. Fix the ${L} PROSE to describe what the chunk does. If the English prose has the same mismatch, the defect is in the source: verdict rejected, reason "same in English". If the right fix is a change inside a code chunk: verdict deferred.
- alignment_mismatch: the segments pair wrongly. Fix only when the fix is a plain prose edit inside the ${L} file. Otherwise deferred.

## Permissions. Each of these is a MUST.

1. Edit ONLY the files listed above. Never edit an English chapters/<chapter>.qmd, any *.de.qmd, anything under _excluded/, data/, html_outputs/, renv/, site_libs/, or _quarto.yml.
2. Never edit inside a code chunk, that is between a line starting with \`\`\`{ and its closing \`\`\` line. Prose only. An inline code span inside prose MAY be corrected when the finding is about it.
3. Never rename a translated identifier: a variable, column, dataset or object name that the translator chose.
4. Never reflow, rewrap or re-indent a line you are not otherwise changing. Change the fewest lines that fix the finding. Keep the markdown structure exactly: headings and their {#anchor} attributes, list markers, bold, links, HTML comments, and trailing double-space line breaks.
5. Use the Edit tool with an exact old_string for every change. Never rewrite a file with Write. Never run git, quarto or R.
6. Line numbers in the evidence are from commit 52442a79. Earlier batches may have shifted them by a few lines. Find the text by content. Read at most about 40 lines around a span in the ${L} file when the evidence context is not enough. Do not read whole chapters.
7. If two findings name the same ${L} text, make one consistent edit and record it under both ids.

## Output. Each of these is a MUST.

Write ${REPO}/modernization/findings/fix-pass/${b.id}.json BEFORE you return, with this exact shape:

{"batch":"${b.id}","lang":"${b.lang}","kind":"${b.kind}",
 "results":[
  {"id":"<finding id copied verbatim from the evidence>","verdict":"fixed","reason":"one sentence","file":"chapters/<chapter>.${b.lang}.qmd","old":"<the exact text you replaced>","new":"<the exact replacement text>"},
  {"id":"...","verdict":"rejected","reason":"one sentence","file":null,"old":null,"new":null},
  {"id":"...","verdict":"deferred","reason":"one sentence","file":null,"old":null,"new":null}
 ]}

One entry per finding in the batch, all ${b.n} of them, ids copied verbatim. "old" and "new" MUST be the exact strings you passed to the Edit tool, so a script can confirm the edit landed. For a missing-kind insertion, "old" is the line you anchored on and "new" is that line plus the inserted text.

Then return the structured summary. fixed + rejected + deferred MUST equal ${b.n}.`
}

const BATCHES = args && args.batches ? args.batches : []
if (!BATCHES.length) throw new Error('args.batches is empty: pass this wave\'s batches explicitly')
const files = new Set()
for (const b of BATCHES) for (const f of b.files) {
  if (files.has(f)) throw new Error('two batches in one wave share ' + f)
  files.add(f)
}
log(`WAVE ${args.wave}: ${BATCHES.length} batches, ${BATCHES.reduce((s, b) => s + b.n, 0)} findings, ${files.size} files, no file shared. Hard slice.`)

phase('Fix')

const results = await parallel(BATCHES.map(b => () =>
  agent(prompt(b), { label: b.id, phase: 'Fix', schema: SUMMARY, model: 'opus', effort: 'xhigh' })
    .then(r => r ? { ...r, ok: true } : { batch: b.id, ok: false })
))

const ok = results.filter(r => r && r.ok)
const failed = results.filter(r => !r || !r.ok)
const t = { fixed: 0, rejected: 0, deferred: 0 }
for (const r of ok) { t.fixed += r.fixed; t.rejected += r.rejected; t.deferred += r.deferred }
log(`RETURNED ${ok.length} of ${BATCHES.length}; fixed ${t.fixed} rejected ${t.rejected} deferred ${t.deferred}`)
if (failed.length) log(`NO RETURN VALUE: ${failed.map(f => f.batch).join(', ')} -- check fix-pass/*.json before calling these failed`)
log(`RECONCILE NOW: python3 modernization/reconcile-fix-pass.py ${BATCHES.map(b => b.id).join(' ')}`)

return {
  accounting: 'RETURN-BASED. Run reconcile-fix-pass.py before you trust any count.',
  wave: args.wave,
  batches: BATCHES.map(b => b.id),
  returned: ok.map(r => r.batch),
  no_return: failed.map(f => f.batch),
  totals: t,
}
