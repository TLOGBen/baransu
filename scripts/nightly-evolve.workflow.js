export const meta = {
  name: 'nightly-evolve-propose',
  description: 'Structure-axis evolve proposal (1 round, adoption deferred) for baransu skills: one finding per skill traced phenomenon → impact → root into a case-free brief, three blind seeds rewrite the root clause, a blind pick, append-only refusal, blind 3-judge panel on the winner, margin gate + body-size ceiling',
  phases: [ { title: 'Diagnose' }, { title: 'Seed' }, { title: 'Pick' }, { title: 'Judge' } ],
}

// --- convergence guard knobs (overridable via args) ---
// args = { skills?: string[], margin?: number, root?: string }
// Body-size ceiling is enforced by the CALLER (Bash precomputes eligible skills
// and passes them in args.skills) because the workflow sandbox has no fs access.
// args.root is REQUIRED — the previous hardcoded default pointed at a dead path.
// Adoption (writing scratch back to the live SKILL.md) is the CALLER's obligation
// and passes through evolve's Gate 1 (Authorization PAUSE / standing auth); this
// workflow only proposes. Structure-axis only: no benchmark, so no exam and no
// case-term list (evolve references/exam.md applies to real-exec runs).
// Top-level drivers may deliver args as a JSON-encoded string — tolerate both shapes.
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const ROOT = A.root
if (!ROOT) throw new Error('args.root required — pass the baransu repo/worktree root')
// The shipped skills = plugins/baransu/skills/ minus _shared. The sandbox cannot
// list the directory, so the caller SHOULD pass args.skills from `ls`; this
// fallback is kept in sync by hand (the CLAUDE.md Skills table, checked by
// scripts/verify-skills.py, is the list authority).
const ALL = ['codex-skill-transfer','draw','evolve','health','how','huh','hunt','learn','read','review','sayagain','ship','teach-me','think','ui','why','write']
const SKILLS = (Array.isArray(A.skills) && A.skills.length) ? A.skills : ALL
const MARGIN = (typeof A.margin === 'number') ? A.margin : 2.0   // min per-judge structure-point improvement to adopt
const SEEDS = ['a','b','c']
const LETTERS = ['P','Q','R']

const RUBRIC = `Structure-axis rubric (score each dimension 0..weight). STRUCTURE-AXIS-ONLY: dims 7-9 excluded. Score the decisions a reader gets right, never the number of rules on the page; length is a cost, never a ceiling.
1 Trigger Clarity (8): frontmatter description has unambiguous trigger phrases AND explicit not-for boundaries.
2 Stage Coherence (8): body stages ordered, anchored, no orphan/forward-ref.
3 Failure-Mode Encoding (8): failure paths handled by the definition or principle covering their class, stated once at the boundary where the condition is decided; a positive definition that keeps the wrong move from arising scores above a prohibition appended against it; a case list grown per incident, or vague caution, scores low.
4 Actionable Specificity (8): concrete directives that state the rule, not its history, each naming who acts on what (an unstated subject or object is read in its cheapest form); hedge words absent or pinned to a decision rule; a directive needing a paragraph to justify itself scores mid.
5 Economy (8): every clause changes a decision; no clause restates another's decision or rationale, covers a failure another already covers, or contradicts another (contradiction caps at half); equal decisions → the shorter version scores higher; words a decision needs are never a cost.
6 High-Risk Action Discipline (8): destructive ops gated/forbidden; vacuous full marks if no destructive surface.
Cluster {3,4,5} is a tension: an added clause pays for its words on 5 unless it changes a decision worth them; a deletion that drops a decision pays on 3 or 4. A gain in one that regresses a sibling is not strict.`

const OPERATIONS = `Operations (choose one, and say in why_kind why it beats the other three):
- add: only when implicated is "none" (no clause explains the phenomenon); a positive definition of what the step is or does, never a prohibition against the observed failure.
- delete / merge: only when the skill does better or no worse without the clause, or with two clauses as one, readable from the text alone here (a dangling reference, a contradiction, an exact restatement); "reads simpler" is not enough. A merge names the clause it absorbs, and the merged sentence covers every phenomenon each original explained; when no single sentence can, keep them apart.
- replace: restating the clause beats adding, deleting and merging.
- keep: none of the above can be shown better.
Write the bedrock as the rule that covers the class, stated once where the condition is decided, naming who does what to what; exact paste-ready text.`

const DIAG_SCHEMA={type:'object',additionalProperties:false,required:['has_finding','dimension','dimension_name','phenomenon','impact','implicated','flaw','origin','verification','brief'],properties:{has_finding:{type:'boolean'},dimension:{type:'integer',minimum:1,maximum:6},dimension_name:{type:'string'},phenomenon:{type:'string'},impact:{type:'string'},implicated:{type:'string'},flaw:{type:'string'},origin:{type:'string'},verification:{type:'string'},brief:{type:'string'}}}
const SEED_SCHEMA={type:'object',additionalProperties:false,required:['change_kind','absorbs','bedrock','why_kind'],properties:{change_kind:{type:'string',enum:['replace','delete','merge','add','keep']},absorbs:{type:'string'},bedrock:{type:'string'},why_kind:{type:'string'}}}
const MUT_SCHEMA={type:'object',additionalProperties:false,required:['scratch_path','mutation_summary','wrote_scratch_only','lines_removed','lines_added'],properties:{scratch_path:{type:'string'},mutation_summary:{type:'string'},wrote_scratch_only:{type:'boolean'},lines_removed:{type:'integer',minimum:0},lines_added:{type:'integer',minimum:0}}}
const RANK_SCHEMA={type:'object',additionalProperties:false,required:['scores','ranking'],properties:{scores:{type:'array',items:{type:'object',additionalProperties:false,required:['letter','overall','reason'],properties:{letter:{type:'string'},overall:{type:'number'},reason:{type:'string'}}}},ranking:{type:'array',items:{type:'string'}}}}
const COPY_SCHEMA={type:'object',additionalProperties:false,required:['copied'],properties:{copied:{type:'boolean'}}}
const SCORES={type:'object',additionalProperties:false,required:['d1','d2','d3','d4','d5','d6'],properties:{d1:{type:'number'},d2:{type:'number'},d3:{type:'number'},d4:{type:'number'},d5:{type:'number'},d6:{type:'number'}}}
const JUDGE_SCHEMA={type:'object',additionalProperties:false,required:['alpha_scores','beta_scores','reasoning'],properties:{alpha_scores:SCORES,beta_scores:SCORES,reasoning:{type:'string'}}}
const sum=(s)=>s.d1+s.d2+s.d3+s.d4+s.d5+s.d6
const allGE=(m,b)=>m.d1>=b.d1&&m.d2>=b.d2&&m.d3>=b.d3&&m.d4>=b.d4&&m.d5>=b.d5&&m.d6>=b.d6

const results = await pipeline(
  SKILLS,
  (skill)=>agent(`Diagnose mode. Target SKILL.md: ${ROOT}/plugins/baransu/skills/${skill}/SKILL.md\nProvenance sources: ${ROOT}/plugins/baransu/skills/evolve/references/provenance.md (section "Clause provenance"), ${ROOT}/CHANGELOG.md, git history of the target.\n\nSTRUCTURE-AXIS-ONLY: dims 1-6; no benchmark output is supplied, so the only admissible phenomena are static — a clause that contradicts another clause, a clause whose side effect is visible in the text (a rule restated, a case list grown per incident, a guard that hides the fault it was added for, a prohibition patched on where a definition belongs), a clause with an unstated subject or object, or a principle-level flaw.\n\n${RUBRIC}\n\nRead in full and score dims 1-6. Then return ONE finding traced as a chain: phenomenon (what is wrong, with the evidence), impact (the outcome of the skill's user it fails — a phenomenon that costs the user nothing is not a finding), implicated (the verbatim clause, or "none" after reading the whole skill), flaw (principle | contradiction: <other clause> | side-effect: <what it causes> | subject: <the actor or object left unstated>), origin (the problem that clause was added to solve, with its source: rationale-in-text | git/CHANGELOG <ref> | unknown), verification (the behaviour that would show a fix worked), dimension (1-6), and brief — the phenomenon, impact and root restated in general terms with the implicated clause verbatim and NO proposed wording, for three seed authors who will each rewrite the clause. If nothing is wrong, return has_finding=false — never manufacture a weakness from the lowest-scoring dimension. Diagnose only; never edit.`,{agentType:'baransu:evolve-diagnostician',phase:'Diagnose',label:`diag:${skill}`,schema:DIAG_SCHEMA}),
  (diag,skill,i)=>{ if(!diag) return null; if(!diag.has_finding) return {skill,held:'no-finding'}
    const real=`${ROOT}/plugins/baransu/skills/${skill}/SKILL.md`; const dir=`${ROOT}/.claude/evolve/${skill}`
    // Seeds see the brief, the target and the rubric only — never another seed.
    return parallel(SEEDS.map(x=>()=>agent(`Seed mode. Target SKILL.md: ${real}\nProvenance: ${ROOT}/plugins/baransu/skills/evolve/references/provenance.md\n\nBrief:\n${diag.brief}\n\nimplicated: ${diag.implicated}\n\n${RUBRIC}\n\n${OPERATIONS}\n\nRead the target in full. Return ONE bedrock: change_kind, absorbs (merge only, the verbatim clause absorbed; else ""), bedrock (the exact new text; "" for delete or keep), why_kind. Do not open any other file under ${dir}. Never edit.`,{agentType:'baransu:evolve-diagnostician',phase:'Seed',label:`seed-${x}:${skill}`,schema:SEED_SCHEMA}).then(s=>{
        if(!s||s.change_kind==='keep') return null
        if(s.change_kind==='add'&&diag.implicated.trim().toLowerCase()!=='none') return {x,seed:s,refused:'add-with-implicated-clause'}
        const scratch=`${dir}/scratch/seed-${x}.md`
        return agent(`Read ${real}. Apply EXACTLY this one bedrock and nothing else.\nchange_kind: ${s.change_kind}\nimplicated clause: ${diag.implicated}\n${s.change_kind==='merge'?`absorbs: ${s.absorbs}\n`:''}bedrock: ${s.bedrock}\n\nHARD RULES:\n- replace: the implicated clause out, the bedrock in. delete: the clause out, nothing in. merge: the implicated clause and the absorbed clause out, the bedrock in. add: the bedrock in.\n- Do NOT edit ${real}. Write the FULL revised file to ${scratch} via the Write tool (creates parent dirs).\n- Touch nothing but those clauses; preserve frontmatter + English-body convention + every required section.\n- Then run a real line diff between ${real} and ${scratch} and report lines_removed (existing non-blank lines removed or rewritten) and lines_added.\nReturn scratch_path=${scratch}, mutation_summary, wrote_scratch_only=true, lines_removed, lines_added.`,{agentType:'general-purpose',phase:'Seed',label:`apply-${x}:${skill}`,schema:MUT_SCHEMA}).then(m=>m?{x,seed:s,mut:m}:null) })))
      .then(seeds=>{
        // SUBTRACTION GATE (evolve SKILL.md Stage 3 / safety-gates Gate 4), per seed:
        // an append-only diff passes only as an add for a phenomenon no clause explains.
        const live=seeds.filter(Boolean).filter(s=>!s.refused).filter(s=>s.mut.lines_removed>0||s.seed.change_kind==='add')
        const refused=seeds.filter(Boolean).filter(s=>s.refused||!live.includes(s)).map(s=>({seed:s.x,reason:s.refused||'append-only-refused'}))
        return {diag,live,refused} }) },
  (prev,skill,i)=>{ if(!prev) return null; if(prev.held) return prev
    const {diag,live,refused}=prev
    if(!live.length) return {skill,held:'no-surviving-seed',refused}
    const dir=`${ROOT}/.claude/evolve/${skill}`; const pick=`${dir}/panel/round-1/seeds`
    // Blind pick: letters rotate with the skill index so seed a is not always P.
    const lettered=live.map((s,k)=>({...s,letter:LETTERS[(k+i)%LETTERS.length]}))
    const promote=(w,ranks)=>({diag,winner:w,refused,ranks})
    if(lettered.length===1) return promote(lettered[0],null)
    return agent(`Copy these files byte-identically (no headers, no annotations, exact bytes), creating parent dirs:\n${lettered.map(s=>`${s.mut.scratch_path} -> ${pick}/${s.letter}.md`).join('\n')}\nReturn copied=true when every copy is written.`,{agentType:'general-purpose',phase:'Pick',label:`letter:${skill}`,schema:COPY_SCHEMA}).then(c=>{
      if(!c||!c.copied) return {skill,held:'pick-copy-failed',refused}
      return agent(`Rank mode. Brief:\n${diag.brief}\n\nSeed versions of one SKILL.md, under shuffled letters:\n${lettered.map(s=>`${s.letter} = ${pick}/${s.letter}.md`).join('\n')}\n\n${RUBRIC}\n\nScore each seed on dims 1-6 and on how fully it explains the brief's phenomenon; give each an overall 1-10 and one line why; rank them (tie → the seed whose lowest dimension is higher). You decide nothing about keeping.`,{agentType:'baransu:evolve-judge',phase:'Pick',label:`pick:${skill}`,schema:RANK_SCHEMA}).then(r=>{
        const top=r&&r.ranking&&lettered.find(s=>s.letter===r.ranking[0])
        return top?promote(top,r.scores):{skill,held:'pick-failed',refused} }) }) },
  (prev,skill,i)=>{ if(!prev) return null; if(prev.held) return prev
    const {diag,winner,refused,ranks}=prev
    const real=`${ROOT}/plugins/baransu/skills/${skill}/SKILL.md`; const panel=`${ROOT}/.claude/evolve/${skill}/panel/round-1`; const even=(i%2)===0
    // Mechanical blinding (evolve SKILL.md Stage 5 contract): judges must never see
    // live-vs-scratch path names; round parity decides which side is the mutation.
    const alphaPath=`${panel}/alpha.md`; const betaPath=`${panel}/beta.md`; const mutatedLabel=even?'beta':'alpha'
    return agent(`Copy byte-identically (no headers, no annotations, exact bytes), creating parent dirs:\n${real} -> ${panel}/${even?'alpha':'beta'}.md\n${winner.mut.scratch_path} -> ${panel}/${even?'beta':'alpha'}.md\nReturn copied=true when both copies are written.`,{agentType:'general-purpose',phase:'Judge',label:`blind:${skill}`,schema:COPY_SCHEMA}).then(c=>{
      if(!c||!c.copied) return {skill,held:'panel-copy-failed',refused}
      return parallel([0,1,2].map(j=>()=>agent(`Pair mode. Two versions of a SKILL.md. One is a proposed single-decision revision of the other; do NOT assume which.\nalpha = ${alphaPath}\nbeta = ${betaPath}\n\n${RUBRIC}\n\nRead BOTH in full. Score each independently on dims 1-6. Return alpha_scores, beta_scores, brief reasoning.`,{agentType:'baransu:evolve-judge',phase:'Judge',label:`judge${j}:${skill}`,schema:JUDGE_SCHEMA}))).then(raw=>{
        const votes=raw.filter(Boolean).map(v=>{const m=v[mutatedLabel+'_scores'];const b=v[(mutatedLabel==='beta'?'alpha':'beta')+'_scores'];const mt=sum(m),bt=sum(b);return{mutatedTotal:mt,baseTotal:bt,delta:mt-bt,strict:mt>bt&&allGE(m,b)}})
        const keepCount=votes.filter(v=>v.strict).length
        const minMargin=votes.length?Math.min(...votes.map(v=>v.delta)):0
        // CONVERGENCE GUARD: a proposal is forwarded only on unanimous 3/3 strict AND a meaningful margin.
        // (Adoption itself stays with the caller via evolve Gate 1 — this script never writes back.)
        const unanimous=keepCount>=3 && votes.length>=3
        const meaningful=minMargin>=MARGIN
        const keep=unanimous && meaningful
        const reason = !unanimous ? 'not-unanimous' : (!meaningful ? `margin-converged(min ${minMargin} < ${MARGIN})` : 'propose')
        // A static delete/merge is ablated only by the exam, which nightly never runs.
        const ablation=(winner.seed.change_kind==='delete'||winner.seed.change_kind==='merge')?'未經消融':''
        return {skill,dimension:diag.dimension,dimension_name:diag.dimension_name,phenomenon:diag.phenomenon,impact:diag.impact,implicated:diag.implicated,flaw:diag.flaw,origin:diag.origin,brief:diag.brief,seed:winner.x,letter:winner.letter,change_kind:winner.seed.change_kind,why_kind:winner.seed.why_kind,ranks,refused,ablation,mutation_summary:winner.mut.mutation_summary,lines_removed:winner.mut.lines_removed,lines_added:winner.mut.lines_added,scratch_path:winner.mut.scratch_path,votes,keepCount,minMargin,keep,reason} }) }) }
)
const clean=results.filter(Boolean)
const kept=clean.filter(r=>r.keep)
const held=clean.filter(r=>r.held)
const converged=clean.filter(r=>!r.keep&&!r.held)
log(`nightly-evolve: ${clean.length}/${SKILLS.length} evaluated · ${kept.length} adopt · ${held.length} held (no-finding / no-surviving-seed / copy or pick failure) · ${converged.length} converged (margin<${MARGIN} or not 3/3)`)
return { margin:MARGIN, evaluated:clean.length, adopt:kept.map(r=>r.skill), held:held.map(r=>({skill:r.skill,reason:r.held})), converged:converged.map(r=>({skill:r.skill,reason:r.reason})), proposals:clean }
