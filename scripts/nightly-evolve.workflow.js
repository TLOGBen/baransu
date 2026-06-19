export const meta = {
  name: 'nightly-evolve-propose',
  description: 'Structure-axis evolve proposal (1 round, adoption deferred) for baransu skills, with a convergence guard: margin gate + body-size ceiling',
  phases: [ { title: 'Diagnose' }, { title: 'Mutate' }, { title: 'Judge' } ],
}

// --- convergence guard knobs (overridable via args) ---
// args = { skills?: string[], margin?: number, root?: string }
// Body-size ceiling is enforced by the CALLER (Bash precomputes eligible skills
// and passes them in args.skills) because the workflow sandbox has no fs access.
const ROOT = (args && args.root) || '/home/vakarve/projects/baransu/.claude/worktrees/nightly-evolve-codex-ship'
const ALL = ['analyze','book','codex-skill-transfer','design','evolve','execute','health','hunt','learn','read','review','ship','think','write']
const SKILLS = (args && Array.isArray(args.skills) && args.skills.length) ? args.skills : ALL
const MARGIN = (args && typeof args.margin === 'number') ? args.margin : 2.0   // min per-judge structure-point improvement to adopt

const RUBRIC = `Structure-axis rubric (score each dimension 0..weight). STRUCTURE-AXIS-ONLY: dims 7-9 excluded.
1 Trigger Clarity (8): frontmatter description has unambiguous trigger phrases AND explicit not-for boundaries.
2 Stage Coherence (8): body stages ordered, anchored, no orphan/forward-ref.
3 Failure-Mode Encoding (8): failure paths as if<condition>then<recovery>, not vague.
4 Actionable Specificity (8): concrete directives; hedge words absent or pinned to a decision rule.
5 Constraint Explicitness (8): hard rules/invariants/red-lines as named constraints, not buried.
6 High-Risk Action Discipline (8): destructive ops gated/forbidden; vacuous full marks if no destructive surface.
Cluster {3,4,5} move together; a gain in one that regresses a sibling is not strict.`

const DIAG_SCHEMA={type:'object',additionalProperties:false,required:['weakest_dimension','weakest_name','improvement_direction'],properties:{weakest_dimension:{type:'integer',minimum:1,maximum:6},weakest_name:{type:'string'},improvement_direction:{type:'string'}}}
const MUT_SCHEMA={type:'object',additionalProperties:false,required:['scratch_path','mutation_summary','wrote_scratch_only'],properties:{scratch_path:{type:'string'},mutation_summary:{type:'string'},wrote_scratch_only:{type:'boolean'}}}
const SCORES={type:'object',additionalProperties:false,required:['d1','d2','d3','d4','d5','d6'],properties:{d1:{type:'number'},d2:{type:'number'},d3:{type:'number'},d4:{type:'number'},d5:{type:'number'},d6:{type:'number'}}}
const JUDGE_SCHEMA={type:'object',additionalProperties:false,required:['alpha_scores','beta_scores','reasoning'],properties:{alpha_scores:SCORES,beta_scores:SCORES,reasoning:{type:'string'}}}
const sum=(s)=>s.d1+s.d2+s.d3+s.d4+s.d5+s.d6
const allGE=(m,b)=>m.d1>=b.d1&&m.d2>=b.d2&&m.d3>=b.d3&&m.d4>=b.d4&&m.d5>=b.d5&&m.d6>=b.d6

const results = await pipeline(
  SKILLS,
  (skill)=>agent(`Target SKILL.md: ${ROOT}/plugins/baransu/skills/${skill}/SKILL.md\n\nSTRUCTURE-AXIS-ONLY: weakest dimension ONLY from dims 1-6.\n\n${RUBRIC}\n\nRead in full, score dims 1-6, pick the single weakest by weighted headroom, propose ONE concrete single-variable improvement (minimal, respect cluster {3,4,5}). Prefer in-place rewording over net additions when the dimension allows. Diagnose only; never edit.`,{agentType:'baransu:evolve-diagnostician',phase:'Diagnose',label:`diag:${skill}`,schema:DIAG_SCHEMA}),
  (diag,skill)=>{ if(!diag) return null; const scratch=`${ROOT}/.claude/evolve/${skill}/scratch.md`; const real=`${ROOT}/plugins/baransu/skills/${skill}/SKILL.md`;
    return agent(`Read ${real}. Apply EXACTLY ONE single-variable change addressing ONLY dimension ${diag.weakest_dimension} (${diag.weakest_name}): ${diag.improvement_direction}\n\nHARD RULES:\n- Do NOT edit ${real}. Write the FULL revised file to ${scratch} via the Write tool (creates parent dirs).\n- Minimal single-variable change; do not touch other dimensions; respect cluster {3,4,5}; preserve frontmatter + English-body convention + every required section.\nReturn scratch_path=${scratch}, mutation_summary, wrote_scratch_only=true.`,{agentType:'general-purpose',phase:'Mutate',label:`mutate:${skill}`,schema:MUT_SCHEMA}).then(m=>m?{diag,mut:m}:null) },
  (prev,skill,i)=>{ if(!prev) return null; const real=`${ROOT}/plugins/baransu/skills/${skill}/SKILL.md`; const scratch=prev.mut.scratch_path; const even=(i%2)===0; const alphaPath=even?real:scratch; const betaPath=even?scratch:real; const mutatedLabel=even?'beta':'alpha';
    return parallel([0,1,2].map(j=>()=>agent(`Two versions of a SKILL.md. One is a proposed single-variable revision of the other; do NOT assume which.\nalpha = ${alphaPath}\nbeta = ${betaPath}\n\n${RUBRIC}\n\nRead BOTH in full. Score each independently on dims 1-6. Return alpha_scores, beta_scores, brief reasoning.`,{agentType:'baransu:evolve-judge',phase:'Judge',label:`judge${j}:${skill}`,schema:JUDGE_SCHEMA}))).then(raw=>{
      const votes=raw.filter(Boolean).map(v=>{const m=v[mutatedLabel+'_scores'];const b=v[(mutatedLabel==='beta'?'alpha':'beta')+'_scores'];const mt=sum(m),bt=sum(b);return{mutatedTotal:mt,baseTotal:bt,delta:mt-bt,strict:mt>bt&&allGE(m,b)}});
      const keepCount=votes.filter(v=>v.strict).length;
      const minMargin=votes.length?Math.min(...votes.map(v=>v.delta)):0;
      // CONVERGENCE GUARD: auto-adopt requires unanimous 3/3 strict AND a meaningful margin.
      const unanimous=keepCount>=3 && votes.length>=3;
      const meaningful=minMargin>=MARGIN;
      const keep=unanimous && meaningful;
      const reason = !unanimous ? 'not-unanimous' : (!meaningful ? `margin-converged(min ${minMargin} < ${MARGIN})` : 'adopt');
      return {skill,weakest_dimension:prev.diag.weakest_dimension,weakest_name:prev.diag.weakest_name,mutation_summary:prev.mut.mutation_summary,scratch_path:prev.mut.scratch_path,votes,keepCount,minMargin,keep,reason}; }) }
)
const clean=results.filter(Boolean)
const kept=clean.filter(r=>r.keep)
const converged=clean.filter(r=>!r.keep)
log(`nightly-evolve: ${clean.length}/${SKILLS.length} evaluated · ${kept.length} adopt · ${converged.length} converged/held (margin<${MARGIN} or not 3/3)`)
return { margin:MARGIN, evaluated:clean.length, adopt:kept.map(r=>r.skill), converged:converged.map(r=>({skill:r.skill,reason:r.reason})), proposals:clean }
