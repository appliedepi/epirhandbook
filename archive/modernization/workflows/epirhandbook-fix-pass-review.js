export const meta = {
  name: 'epirhandbook-fix-pass-review',
  description: 'Adversarial review of the fix-pass diff, one Claude agent per language part. Flag only, never fix. Replaces the codex calls the usage limit blocked.',
  phases: [
    { title: 'Review', detail: 'one opus xhigh agent per diff part, writes /tmp/review/<lang>.part<N>.json' },
  ],
}

// args.parts: [{lang, part, bytes, hunks, files, fixed}]. Hard slice: only what is passed.
// Each agent reads /tmp/codex-ws/<lang>/CHANGES.part<N>.diff and FINDINGS.part<N>.md, plus the
// chapter files in that workspace for context. It writes a JSON file. The orchestrator counts
// the files on disk, then verifies every flagged item against the repository before any repair.

const LANGNAME = { es: 'Spanish', fr: 'French', jp: 'Japanese', pt: 'Portuguese', ru: 'Russian', tr: 'Turkish', vn: 'Vietnamese' }

const SUMMARY = {
  type: 'object', additionalProperties: false,
  required: ['lang', 'part', 'hunks_read', 'hunks_total', 'flagged', 'wrote_file'],
  properties: {
    lang: { type: 'string' }, part: { type: 'integer' }, hunks_read: { type: 'integer' },
    hunks_total: { type: 'integer' }, flagged: { type: 'integer' }, wrote_file: { type: 'string' },
  },
}

function prompt(p) {
  const L = LANGNAME[p.lang]
  const ws = `/tmp/codex-ws/${p.lang}`
  return `You are the adversarial reviewer of a batch of edits to ${L} chapters of the Epidemiologist R Handbook (Quarto .qmd). Argue against the edits. Find the wrong ones. FLAG, DO NOT FIX: you MUST NOT edit any file.

Workspace, read-only, NOT a git repository, do not run git: ${ws}
- ${ws}/CHANGES.part${p.part}.diff : the diff you review. ${p.hunks} hunks over ${p.nfiles} files.
- ${ws}/FINDINGS.part${p.part}.md : per edit, the finder's reason and the exact OLD and NEW text.
- ${ws}/chapters/<chapter>.${p.lang}.qmd : the CURRENT post-edit ${L} file, and chapters/<chapter>.qmd its English source, for context.

Context. An earlier sweep compared each translated chapter against its English source and recorded findings of five kinds: untrue (the translation asserts what the English does not), missing (the translation drops an English point), added (the translation adds content with no English source; the owner's rule is that such additions are REMOVED), code_mismatch (the prose describes what the code chunk beside it does not do), alignment_mismatch. A fix agent then verified each finding from the spans and either edited the ${L} file or rejected the finding. English is the reference. Only translated files may change.

Read EVERY hunk in the diff. For each hunk, judge the NEW text against the English source at that place and against the ${L} file around it. Report a hunk ONLY if one of these holds:

1. WRONG MEANING: the NEW text says something the English does not say, or drops something the English says, or contradicts the code chunk beside it. This is the most severe class. A hunk that introduces an error the English does not have is the worst outcome; hunt for those first.
2. BROKEN MARKUP: damage to markdown, a link target, a {#anchor}, inline code, a list marker, an HTML comment, a table, or a trailing double-space hard line break; an inserted internal link that points at chapter.qmd instead of chapter.${p.lang}.qmd; an R literal such as TRUE, FALSE, NA rendered as a ${L} word; a literal folder or file name from the code translated.
3. NOT ${L.toUpperCase()}: the NEW text is not fluent, correct ${L}, or leaves English text in a ${L} sentence, or mixes registers with the surrounding translation.
4. OVERREACH: the hunk changes text no finding names, reflows lines, renames a translated identifier (a variable, column, dataset or object name the translator chose), or edits inside a code chunk.
5. WRONG REMOVAL: a deletion (kind added) of content the English page does have, anywhere on the page.
6. WRONG INSERTION: an insertion (kind missing) that is not a correct translation of the English point, or is placed where the English does not have it.

Do NOT report: ordinary translator paraphrase, register, sentence order inside a segment, a paragraph split, a translated heading, a localised link label, or a difference that the English source itself carries (say "same in English" to yourself and move on).

Output. Write ${'/tmp/review/' + p.lang + '.part' + p.part + '.json'} BEFORE you return, with this exact shape:
{"lang":"${p.lang}","part":${p.part},"hunks_total":${p.hunks},"hunks_read":<integer>,
 "items":[{"file":"chapters/<chapter>.${p.lang}.qmd","severity":"wrong-meaning|broken-markup|not-fluent|overreach|wrong-removal|wrong-insertion","new_text":"<the exact NEW text of the hunk, or the exact fragment that is wrong, copied verbatim so a script can find it>","problem":"one or two sentences","proposed_fix":"<the exact replacement text, or 'revert', or 'none'>"}]}
Most severe first. hunks_read MUST equal hunks_total; if you could not read every hunk, say which in a final item with severity "not-read". Then return the structured summary.`
}

const PARTS = args && args.parts ? args.parts : []
if (!PARTS.length) throw new Error('args.parts is empty')
log(`REVIEW: ${PARTS.length} parts, ${PARTS.reduce((s, p) => s + p.hunks, 0)} hunks`)
phase('Review')
const results = await parallel(PARTS.map(p => () =>
  agent(prompt(p), { label: `${p.lang}.part${p.part}`, phase: 'Review', schema: SUMMARY, model: 'opus', effort: 'xhigh' })
    .then(r => r ? { ...r, ok: true } : { lang: p.lang, part: p.part, ok: false })
))
const ok = results.filter(r => r && r.ok)
log(`RETURNED ${ok.length} of ${PARTS.length}; flagged ${ok.reduce((s, r) => s + r.flagged, 0)}; RECONCILE against /tmp/review/*.json`)
return { accounting: 'RETURN-BASED. Count /tmp/review/*.json.', returned: ok.map(r => `${r.lang}.part${r.part}`), no_return: results.filter(r => !r || !r.ok).map(r => `${r.lang}.part${r.part}`), flagged: ok.reduce((s, r) => s + r.flagged, 0) }
