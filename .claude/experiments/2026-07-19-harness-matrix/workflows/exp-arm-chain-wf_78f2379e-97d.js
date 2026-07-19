export const meta = {
  name: 'exp-arm-chain',
  description: 'Run one experiment arm as a sequential agent chain',
  phases: [{ title: 'Arm' }],
}
const A = typeof args === 'string' ? JSON.parse(args) : args
if (!A || !Array.isArray(A.steps)) throw new Error('args.steps missing; got: ' + JSON.stringify(A).slice(0, 200))
const t0 = budget.spent()
const reports = []
for (let i = 0; i < A.steps.length; i++) {
  const step = A.steps[i]
  const prev = reports.length ? String(reports[reports.length - 1]) : '(none)'
  const prompt = step.prompt.split('{{PREV_REPORT}}').join(prev)
  const opts = { label: step.label, phase: 'Arm' }
  if (step.model) opts.model = step.model
  if (step.agentType) opts.agentType = step.agentType
  const r = await agent(prompt, opts)
  reports.push(r === null ? '(agent returned null)' : String(r))
  log(step.label + ' done')
}
return { arm: A.arm, tokens: budget.spent() - t0, reports }