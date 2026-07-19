export const meta = {
  name: 'exp-arm-execute',
  description: 'analyze+execute style arm: spec, per-task TDAID impl/review loop, final coverage review',
  phases: [{ title: 'Spec' }, { title: 'TDAID' }, { title: 'Final' }],
}
const A = typeof args === 'string' ? JSON.parse(args) : args
if (!A || !A.specPrompt) throw new Error('bad args')
const t0 = budget.spent()
const sub = (s, k, v) => s.split(k).join(v)
phase('Spec')
const spec = await agent(A.specPrompt, { model: A.specModel, label: 'spec:' + A.arm, phase: 'Spec' })
if (spec === null) throw new Error('spec agent returned null')
const TIER_SCHEMA = { type: 'object', properties: { tier: { type: 'string' }, findings: { type: 'string' }, green_ok: { type: 'boolean' } }, required: ['tier', 'findings', 'green_ok'] }
const FINAL_SCHEMA = { type: 'object', properties: { needs_fixer: { type: 'boolean' }, report: { type: 'string' } }, required: ['needs_fixer', 'report'] }
const taskResults = []
for (const task of A.tasks) {
  let lastReview = null, implReport = null, attempts = 0, done = false
  while (attempts < 2 && !done) {
    attempts++
    let p = sub(A.implPrompt, '{{TASK}}', task)
    if (lastReview) p += '\n\ncorrection guidance — a reviewer found these issues with the previous attempt; address them:\n' + lastReview.findings
    implReport = await agent(p, { agentType: 'baransu:impl-agent', model: A.implModel, label: 'impl:' + task + '#' + attempts, phase: 'TDAID' })
    const rp = sub(sub(A.reviewPrompt, '{{TASK}}', task), '{{IMPL_REPORT}}', String(implReport))
    lastReview = await agent(rp, { agentType: 'baransu:review-agent', model: A.reviewModel, label: 'review:' + task + '#' + attempts, phase: 'TDAID', schema: TIER_SCHEMA })
    if (!lastReview) { done = true; break }
    const t = (lastReview.tier || '').toLowerCase()
    done = !(t.includes('needs judgment') || t.includes('correctness'))
  }
  taskResults.push({ task, attempts, tier: lastReview ? lastReview.tier : null, green: lastReview ? lastReview.green_ok : null, findings: lastReview ? String(lastReview.findings).slice(0, 800) : null })
  log('task ' + task + ': ' + (lastReview ? lastReview.tier : 'review-null') + ' after ' + attempts + ' attempt(s)')
}
phase('Final')
const fin = await agent(A.finalPrompt, { agentType: 'baransu:final-review-agent', model: A.finalModel, label: 'final-review', phase: 'Final', schema: FINAL_SCHEMA })
let fixer = null, fin2 = null
if (fin && fin.needs_fixer) {
  log('final review requests fixer')
  fixer = await agent(sub(A.fixerPrompt, '{{COVERAGE_REPORT}}', fin.report), { agentType: 'baransu:final-fixer-agent', model: A.implModel, label: 'final-fixer', phase: 'Final' })
  fin2 = await agent(A.finalPrompt + '\n\n(Second run: the final-fixer has since supplemented gaps from the first Coverage Report; re-verify everything from scratch.)', { agentType: 'baransu:final-review-agent', model: A.finalModel, label: 'final-review#2', phase: 'Final', schema: FINAL_SCHEMA })
}
return {
  arm: A.arm,
  tokens: budget.spent() - t0,
  specSummary: String(spec).slice(0, 1200),
  taskResults,
  finalNeedsFixer: fin ? fin.needs_fixer : null,
  finalReport: fin ? String(fin.report).slice(0, 2500) : null,
  fixer: fixer === null ? null : String(fixer).slice(0, 800),
  finalReport2: fin2 ? String(fin2.report).slice(0, 2000) : null,
}