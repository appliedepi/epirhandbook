export const meta = {
  name: 'epirhandbook-fix-pass-deferred',
  description: 'Deferred-fix pass: the findings the fix pass could not touch because the defect sits inside a code chunk. Agents MAY edit code chunks in translated files, to make them match the English chunk.',
  phases: [
    { title: 'Fix', detail: 'one opus xhigh agent per batch, may edit code chunks in chapters/<chapter>.<lang>.qmd, writes fix-pass/<batch>.json' },
  ],
}

// Same shape as epirhandbook-fix-pass-wave.js: args.batches is the hard slice, no two
// batches in one wave share a file, the result file on disk is the artifact.

const REPO = '/home/raw996/ae/epiRhandbook_eng'
const LANGNAME = { es: 'Spanish', fr: 'French', jp: 'Japanese', pt: 'Portuguese', ru: 'Russian', tr: 'Turkish', vn: 'Vietnamese' }

const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['batch', 'n', 'fixed', 'rejected', 'deferred', 'wrote_file'],
  properties: { batch: { type: 'string' }, n: { type: 'integer' }, fixed: { type: 'integer' }, rejected: { type: 'integer' }, deferred: { type: 'integer' }, wrote_file: { type: 'string' } },
}

function prompt(b) {
  const L = LANGNAME[b.lang]
  return `You fix the DEFERRED findings of the epiRhandbook prose sweep: the ones an earlier fix agent confirmed but could not touch, because the defect sits inside a code chunk, or needs a structural change.

Repository: ${REPO}
Batch: ${b.id}  (language ${b.lang} = ${L}, ${b.n} findings)
Evidence file, read it whole, once: /tmp/fixpass/batches/${b.id}.md
Files this batch MAY edit, and no others: ${b.files.join(', ')}

## What you have

Per finding: the finder's proposition, the English span and the ${L} span with context as they were at commit 52442a79, and the reason the earlier agent deferred it. Line numbers may have shifted since: locate the text by content in the current file. The English chapter chapters/<chapter>.qmd is the reference; read the matching English chunk before you edit a ${L} chunk.

## Your verdict, per finding

- fixed: you made the ${L} file right. Say what you changed.
- rejected: the finding is wrong, or the ${L} file already matches the English at that place. Do NOT edit. One sentence why.
- deferred: still not fixable under the rules below. One sentence what it needs.

## What you MAY do now, that the first pass could not

1. Edit inside a code chunk of a ${L} file, to make the chunk do what the matching English chunk does: restore an R function name, an argument name, a keyword, a package name, a literal value, a file or folder name, a chunk option, or a comment, that the translator changed or mistyped. Copy the English chunk's line for that place.
2. Add a code chunk the ${L} file lacks and the English has, copied verbatim from the English, at the matching place.
3. Restore or correct a chunk fence, a heading level, or a section the English has.

## What you MUST NOT do

1. Never edit an English chapters/<chapter>.qmd, any *.de.qmd, anything under _excluded/, data/, html_outputs/, renv/, site_libs/, or _quarto.yml.
2. Never rename a translator's own object, column or dataset name that the ${L} chapter uses consistently and that is valid R (for example a Portuguese data frame called caso_tabela). Restore a name ONLY where the ${L} chunk's name is not valid R, is inconsistent within the chapter, or breaks a call to a package function that expects a specific name. A translated R FUNCTION, ARGUMENT or KEYWORD (liste() for list(), ici() for here(), em for in, couleur = for color =) is never a translator's choice: restore it.
3. Never reflow, rewrap or re-indent a line you are not otherwise changing. Change the fewest lines that fix the finding. Keep chunk options, labels, comments and blank lines as they are unless the finding is about them.
4. Use the Edit tool with an exact old_string for every change. Never rewrite a file with Write. Never run git, quarto or R.
5. Keep ${L} comments in ${L}. When you copy an English chunk, keep its comments in English rather than invent a translation.

## Output. Each of these is a MUST.

Write ${REPO}/modernization/findings/fix-pass/${b.id}.json BEFORE you return, with this exact shape:

{"batch":"${b.id}","lang":"${b.lang}","kind":"deferred",
 "results":[
  {"id":"<finding id copied verbatim>","verdict":"fixed","reason":"one sentence","file":"chapters/<chapter>.${b.lang}.qmd","old":"<the exact text you replaced>","new":"<the exact replacement text>"},
  {"id":"...","verdict":"rejected","reason":"one sentence","file":null,"old":null,"new":null},
  {"id":"...","verdict":"deferred","reason":"one sentence","file":null,"old":null,"new":null}
 ]}

One entry per finding, all ${b.n}, ids verbatim. For a finding that needed several edits, "old" and "new" are the first edit and "reason" lists the others. Then return the structured summary. fixed + rejected + deferred MUST equal ${b.n}.`
}

const BATCHES = args && args.batches ? args.batches : []
if (!BATCHES.length) throw new Error('args.batches is empty')
const files = new Set()
for (const b of BATCHES) for (const f of b.files) { if (files.has(f)) throw new Error('two batches in one wave share ' + f); files.add(f) }
log(`DEFERRED WAVE ${args.wave}: ${BATCHES.length} batches, ${BATCHES.reduce((s, b) => s + b.n, 0)} findings, ${files.size} files`)
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
