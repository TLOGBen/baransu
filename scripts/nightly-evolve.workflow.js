export const meta = {
  name: 'nightly-evolve-propose',
  description: 'Structure-axis evolve proposal (1 round, adoption deferred) for baransu skills: one finding per skill (replace/delete the implicated clause), append-only refusal, blind 3-judge panel, margin gate + body-size ceiling',
  phases: [ { title: 'Diagnose' }, { title: 'Replace' }, { title: 'Judge' } ],
}

// --- convergence guard knobs (overridable via args) ---
// args = { skills?: string[], margin?: number, root?: string }
// Body-size ceiling is enforced by the CALLER (Bash precomputes eligible skills
// and passes them in args.skills) because the workflow sandbox has no fs access.
// args.root is REQUIRED — the previous hardcoded default pointed at a dead path.
// Adoption (writing scratch back to the live SKILL.md) is the CALLER's obligation
// and passes through evolve's Gate 1 (Authorization PAUSE / standing auth); this
// workflow only proposes.
// Top-level drivers may deliver args as a JSON-encoded string — tolerate both shapes.
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const ROOT = A.root
if (!ROOT) throw new Error('args.root required — pass the baransu repo/worktree root')
// The shipped skills = plugins/baransu/skills/ minus _shared. The sandbox cannot
// list the directory, so the caller SHOULD pass args.skills from `ls`; this
// fallback is kept in sync by hand (the CLAUDE.md Skills table, checked by
// scripts/verify-skills.py, is the list authority).
const ALL = ['codex-skill-transfer','draw','evolve','health','huh','hunt','learn','read','review','sayagain','ship','think','ui','write']
const SKILLS = (Array.isArray(A.skills) && A.skills.length) ? A.skills : ALL
const MARGIN = (typeof A.margin === 'number') ? A.margin : 2.0   // min per-judge structure-point improvement to adopt

const RUBRIC = `Structure-axis rubric (score each dimension 0..weight). STRUCTURE-AXIS-ONLY: dims 7-9 excluded. Score the decisions a reader gets right, never the number of rules on the page; length is a cost.
1 Trigger Clarity (8): frontmatter description has unambiguous trigger phrases AND explicit not-for boundaries.
2 Stage Coherence (8): body stages ordered, anchored, no orphan/forward-ref.
3 Failure-Mode Encoding (8): failure paths handled by the principle covering their class, one if<condition>then<recovery> at the boundary where the condition is decided — not a case list that grows per incident, not vague.
4 Actionable Specificity (8): concrete directives that state the rule, not its history; hedge words absent or pinned to a decision rule; a directive needing a paragraph to justify itself scores mid.
5 Economy (8): every clause changes a decision; no clause restates another's decision or rationale, covers a failure another already covers, or contradicts another (contradiction caps at half); equal decisions → the shorter version scores higher.
6 High-Risk Action Discipline (8): destructive ops gated/forbidden; vacuous full marks if no destructive surface.
Cluster {3,4,5} is a tension: an added rule pays for its words on 5 unless it displaces a clause; a deletion that drops a decision pays on 3 or 4. A gain in one that regresses a sibling is not strict.`

const DIAG_SCHEMA={type:'object',additionalProperties:false,required:['has_finding','dimension','dimension_name','failure','implicated','flaw','origin','replacement','change_kind','displaces'],properties:{has_finding:{type:'boolean'},dimension:{type:'integer',minimum:1,maximum:6},dimension_name:{type:'string'},failure:{type:'string'},implicated:{type:'string'},flaw:{type:'string'},origin:{type:'string'},replacement:{type:'string'},change_kind:{type:'string',enum:['replace','delete','add','none']},displaces:{type:'string'}}}
const MUT_SCHEMA={type:'object',additionalProperties:false,required:['scratch_path','mutation_summary','wrote_scratch_only','lines_removed','lines_added'],properties:{scratch_path:{type:'string'},mutation_summary:{type:'string'},wrote_scratch_only:{type:'boolean'},lines_removed:{type:'integer',minimum:0},lines_added:{type:'integer',minimum:0}}}
const SCORES={type:'object',additionalProperties:false,required:['d1','d2','d3','d4','d5','d6'],properties:{d1:{type:'number'},d2:{type:'number'},d3:{type:'number'},d4:{type:'number'},d5:{type:'number'},d6:{type:'number'}}}
const JUDGE_SCHEMA={type:'object',additionalProperties:false,required:['alpha_scores','beta_scores','reasoning'],properties:{alpha_scores:SCORES,beta_scores:SCORES,reasoning:{type:'string'}}}
const sum=(s)=>s.d1+s.d2+s.d3+s.d4+s.d5+s.d6
const allGE=(m,b)=>m.d1>=b.d1&&m.d2>=b.d2&&m.d3>=b.d3&&m.d4>=b.d4&&m.d5>=b.d5&&m.d6>=b.d6

const results = await pipeline(
  SKILLS,
  (skill)=>agent(`Target SKILL.md: ${ROOT}/plugins/baransu/skills/${skill}/SKILL.md\nProvenance sources: ${ROOT}/plugins/baransu/skills/evolve/references/provenance.md (section "Clause provenance"), ${ROOT}/CHANGELOG.md, git history of the target.\n\nSTRUCTURE-AXIS-ONLY: dims 1-6; no benchmark output is supplied, so the only admissible failures are static — a clause that contradicts another clause, a clause whose side effect is visible in the text (a rule restated, a case list grown per incident, a guard that hides the fault it was added for), or a principle-level flaw.\n\n${RUBRIC}\n\nRead in full and score dims 1-6. Then return ONE finding: failure (what is wrong, with the evidence), implicated (the verbatim clause, or "none" after reading the whole skill), flaw (principle | contradiction: <other clause> | side-effect: <what it causes>), origin (the problem that clause was added to solve, with its source: rationale-in-text | git/CHANGELOG <ref> | unknown), replacement (the exact new text that solves the origin problem and the failure with fewer words, or "delete" naming the clause that now carries the origin problem), change_kind (replace | delete | add), displaces (for add only: the verbatim clause the addition displaces — an add that displaces nothing is not a finding), dimension (1-6 the failure lands on). If nothing is wrong, return has_finding=false and change_kind="none" — never manufacture a weakness from the lowest-scoring dimension. Diagnose only; never edit.`,{agentType:'baransu:evolve-diagnostician',phase:'Diagnose',label:`diag:${skill}`,schema:DIAG_SCHEMA}),
  (diag,skill,i)=>{ if(!diag||!diag.has_finding||diag.change_kind==='none') return diag?{skill,held:'no-finding'}:null; if(diag.change_kind==='add'&&!diag.displaces.trim()) return {skill,held:'add-without-displacement'}; const scratch=`${ROOT}/.claude/evolve/${skill}/scratch.md`; const real=`${ROOT}/plugins/baransu/skills/${skill}/SKILL.md`; const panel=`${ROOT}/.claude/evolve/${skill}/panel/round-1`; const even=(i%2)===0;
    // Mechanical blinding (evolve SKILL.md Stage 5 contract): judges must never see
    // live-vs-scratch path names. The replace agent writes byte-identical copies to
    // neutral panel paths; round parity decides which side is the mutation.
    return agent(`Read ${real}. Apply EXACTLY this one finding and nothing else.\nchange_kind: ${diag.change_kind}\nimplicated clause: ${diag.implicated}\n${diag.change_kind==='add'?`displaces: ${diag.displaces}\n`:''}replacement: ${diag.replacement}\n\nHARD RULES:\n- replace: the implicated clause out, the replacement in. delete: the clause out, nothing in. add: the new clause in AND the displaced clause out.\n- Do NOT edit ${real}. Write the FULL revised file to ${scratch} via the Write tool (creates parent dirs).\n- Touch nothing but that clause; preserve frontmatter + English-body convention + every required section.\n- Then run a real line diff between ${real} and ${scratch} and report lines_removed (existing non-blank lines removed or rewritten) and lines_added. A diff that removes nothing will be refused.\n- Then write two byte-identical blinded copies: copy ${real} unchanged to ${panel}/${even?'alpha':'beta'}.md and your revised version to ${panel}/${even?'beta':'alpha'}.md — no headers, no annotations, exact bytes.\nReturn scratch_path=${scratch}, mutation_summary, wrote_scratch_only=true, lines_removed, lines_added.`,{agentType:'general-purpose',phase:'Replace',label:`replace:${skill}`,schema:MUT_SCHEMA}).then(m=>m?{diag,mut:m}:null) },
  (prev,skill,i)=>{ if(!prev) return null; if(prev.held) return prev;
    // SUBTRACTION GATE (evolve SKILL.md Stage 3 / safety-gates Gate 4): an append-only
    // candidate never reaches the panel. lines_removed is the replace agent's diff
    // report; the caller may re-verify with `diff` before adopting.
    if(prev.mut.lines_removed===0) return {skill,held:'append-only-refused',change_kind:prev.diag.change_kind,implicated:prev.diag.implicated,scratch_path:prev.mut.scratch_path};
    const panel=`${ROOT}/.claude/evolve/${skill}/panel/round-1`; const even=(i%2)===0; const alphaPath=`${panel}/alpha.md`; const betaPath=`${panel}/beta.md`; const mutatedLabel=even?'beta':'alpha';
    return parallel([0,1,2].map(j=>()=>agent(`Two versions of a SKILL.md. One is a proposed single-clause revision of the other; do NOT assume which.\nalpha = ${alphaPath}\nbeta = ${betaPath}\n\n${RUBRIC}\n\nRead BOTH in full. Score each independently on dims 1-6. Return alpha_scores, beta_scores, brief reasoning.`,{agentType:'baransu:evolve-judge',phase:'Judge',label:`judge${j}:${skill}`,schema:JUDGE_SCHEMA}))).then(raw=>{
      const votes=raw.filter(Boolean).map(v=>{const m=v[mutatedLabel+'_scores'];const b=v[(mutatedLabel==='beta'?'alpha':'beta')+'_scores'];const mt=sum(m),bt=sum(b);return{mutatedTotal:mt,baseTotal:bt,delta:mt-bt,strict:mt>bt&&allGE(m,b)}});
      const keepCount=votes.filter(v=>v.strict).length;
      const minMargin=votes.length?Math.min(...votes.map(v=>v.delta)):0;
      // CONVERGENCE GUARD: a proposal is forwarded only on unanimous 3/3 strict AND a meaningful margin.
      // (Adoption itself stays with the caller via evolve Gate 1 — this script never writes back.)
      const unanimous=keepCount>=3 && votes.length>=3;
      const meaningful=minMargin>=MARGIN;
      const keep=unanimous && meaningful;
      const reason = !unanimous ? 'not-unanimous' : (!meaningful ? `margin-converged(min ${minMargin} < ${MARGIN})` : 'propose');
      return {skill,dimension:prev.diag.dimension,dimension_name:prev.diag.dimension_name,change_kind:prev.diag.change_kind,failure:prev.diag.failure,implicated:prev.diag.implicated,origin:prev.diag.origin,mutation_summary:prev.mut.mutation_summary,lines_removed:prev.mut.lines_removed,lines_added:prev.mut.lines_added,scratch_path:prev.mut.scratch_path,votes,keepCount,minMargin,keep,reason}; }) }
)
const clean=results.filter(Boolean)
const kept=clean.filter(r=>r.keep)
const held=clean.filter(r=>r.held)
const converged=clean.filter(r=>!r.keep&&!r.held)
log(`nightly-evolve: ${clean.length}/${SKILLS.length} evaluated · ${kept.length} adopt · ${held.length} held (no-finding / append-only-refused / add-without-displacement) · ${converged.length} converged (margin<${MARGIN} or not 3/3)`)
return { margin:MARGIN, evaluated:clean.length, adopt:kept.map(r=>r.skill), held:held.map(r=>({skill:r.skill,reason:r.held})), converged:converged.map(r=>({skill:r.skill,reason:r.reason})), proposals:clean }
