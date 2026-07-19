export const meta = {
  name: 'exp-arm-combo',
  description: 'Native combo arm: lead plans and dispatches, script spawns workers, lead integrates',
  phases: [{ title: 'Lead' }, { title: 'Workers' }, { title: 'Review' }, { title: 'Integrate' }],
}
const A = typeof args === 'string' ? JSON.parse(args) : args
if (!A || !A.leadPrompt) throw new Error('bad args: ' + JSON.stringify(A).slice(0, 200))
const t0 = budget.spent()
const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    workers: {
      type: 'array', minItems: 1, maxItems: 3,
      items: { type: 'object', properties: { id: { type: 'string' }, instructions: { type: 'string' } }, required: ['id', 'instructions'] },
    },
    notes: { type: 'string' },
  },
  required: ['workers'],
}
phase('Lead')
const plan = await agent(A.leadPrompt, { model: A.leadModel, label: 'lead-plan', phase: 'Lead', schema: PLAN_SCHEMA })
if (!plan) throw new Error('lead plan returned null')
log('lead dispatched ' + plan.workers.length + ' worker(s)')
phase('Workers')
const workerReports = []
for (const w of plan.workers) {
  const r = await agent(
    A.workerPreamble.split('{{WORKER_ID}}').join(w.id) + '\n\n=== LEAD INSTRUCTIONS (verbatim) ===\n' + w.instructions,
    { model: A.workerModel, label: 'worker:' + w.id, phase: 'Workers' })
  workerReports.push('--- worker ' + w.id + ' report ---\n' + (r === null ? '(null)' : String(r)))
  log('worker ' + w.id + ' done')
}
const joined = workerReports.join('\n\n')
let reviewReport = '(no independent reviewer in this arm)'
if (A.reviewPrompt) {
  phase('Review')
  const rv = await agent(A.reviewPrompt.split('{{WORKER_REPORTS}}').join(joined), { model: A.reviewModel, label: 'review', phase: 'Review' })
  reviewReport = rv === null ? '(null)' : String(rv)
}
phase('Integrate')
const final = await agent(
  A.integratePrompt.split('{{WORKER_REPORTS}}').join(joined).split('{{REVIEW_REPORT}}').join(reviewReport).split('{{PLAN_NOTES}}').join(plan.notes || '(none)'),
  { model: A.leadModel, label: 'lead-integrate', phase: 'Integrate' })
return {
  arm: A.arm,
  tokens: budget.spent() - t0,
  workerCount: plan.workers.length,
  workers: plan.workers.map(w => w.id),
  planNotes: (plan.notes || '').slice(0, 2000),
  reviewReport: reviewReport.slice(0, 3000),
  final: final === null ? '(null)' : String(final),
}