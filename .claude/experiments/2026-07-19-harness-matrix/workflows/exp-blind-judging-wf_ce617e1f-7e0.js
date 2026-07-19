export const meta = {
  name: 'exp-blind-judging',
  description: 'Blind-judge 10 de-identified experiment deliveries on 4 dimensions',
  phases: [{ title: 'Judge' }],
}
const A = typeof args === 'string' ? JSON.parse(args) : args
const t0 = budget.spent()
const SCHEMA = {
  type: 'object',
  properties: {
    arm: { type: 'string' },
    met_pinned: { type: 'array', items: { type: 'string' } },
    met_unpinned: { type: 'array', items: { type: 'string' } },
    partial: { type: 'array', items: { type: 'string' } },
    unmet: { type: 'array', items: { type: 'string' } },
    bugs: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string' }, desc: { type: 'string' } }, required: ['severity', 'desc'] } },
    arch_score: { type: 'number' },
    arch_notes: { type: 'string' },
    test_eff_score: { type: 'number' },
    mutations: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['arm', 'met_pinned', 'met_unpinned', 'partial', 'unmet', 'bugs', 'arch_score', 'arch_notes', 'test_eff_score', 'mutations', 'notes'],
}
const judge = (code) => () => agent(A.promptTemplate.split('{{ARM}}').join(code), { model: 'fable', label: 'judge:' + code, phase: 'Judge', schema: SCHEMA })
const results = []
for (const batch of [['ARM-1', 'ARM-2', 'ARM-3'], ['ARM-4', 'ARM-5', 'ARM-6'], ['ARM-7', 'ARM-8', 'ARM-9', 'ARM-10']]) {
  const r = await parallel(batch.map(judge))
  results.push(...r)
  log('batch done: ' + batch.join(','))
}
return { tokens: budget.spent() - t0, results: results.filter(Boolean) }