"""Each rule of view-judge.test.ts can say no: break the mod once per rule in a scratch copy of the test kit, run
the judge, and see that rule's test fail. Usage: python view_mutants.py <test kit folder>
"""
import pathlib
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
KIT = pathlib.Path(sys.argv[1])
ENGINE = 'hooks/engine/engine.ts'
PORT = 'hooks/adapters/claude-code/view/port.ts'
VIEW = 'hooks/adapters/claude-code/view/hooks.ts'
CARD = 'hooks/adapters/claude-code/view/card.ts'
HOOKS = 'hooks/adapters/claude-code/hooks.ts'

# rule → (file, text to replace, broken text, the judge test that must fail)
MUTANTS = {
    'E1 stop': (ENGINE, "await post(h, ports, memory, cardOf('結束這一輪前', findings, { kind: 'stop'", "void (h, ports, memory, cardOf('結束這一輪前', findings, { kind: 'stop'", 'E1 stop held'),
    'E2 agent call': (ENGINE, "const callId = S().agentCalls?.[e.agent]", "const callId = undefined as string | undefined", 'E2 a background subagent'),
    'E3 skill by name (P4)': (ENGINE, "isReview), S().skillCalls?.[e.name])", "isReview), Object.values(S().skillCalls ?? {}).pop())", 'E3 two Skill calls at once'),
    'E4 all drawn (P5)': (VIEW, "...cards.map(d => drawCard($, e, d))", "...cards.slice(-3).map(d => drawCard($, e, d))", 'E4 (W1) five cards'),
    'E4 cleared once entered (P8)': (ENGINE, "    if (!dropped(r)) clearShown(h, memory, shown)\n    // The prompt did not enter", "    clearShown(h, memory, shown)\n    // The prompt did not enter", 'E4 a message that never enters'),
    'E5 band cleared': (ENGINE, "    if (!dropped(r)) clearShown(h, memory, shown)\n    // The prompt did not enter", "    void shown\n    // The prompt did not enter", 'E5 the next message'),
    'E5 image only (P9)': (HOOKS, "(await engine.ready(hostOf($))).messageSent(() => next(e), droppedPrompt)", "next(e)", 'E5 a message of only an image'),
    'E6 skill call': (ENGINE, "isReview), S().skillCalls?.[e.name])", "isReview), undefined)", 'E6 a skill loaded'),
    'E7 fallback': (PORT, "await h.append(cardText(card))", "void cardText(card)", 'E7 no surface draws'),
    'E7 phone (P7)': (PORT, "    if (at) return\n", "    if (at) return\n    if (Math.random() < 2) return\n", 'E7 (W3)'),
    'F1 more': (CARD, "...(more > 0 ? [", "...(more > 99 ? [", 'F1: a card past its rows'),
    'F2 one per agent': (ENGINE, "callId ? `${callId}#agent:${e.agent}` : undefined)", "callId)", 'F2: two agents of one Workflow'),
}


def run(kit: pathlib.Path) -> str:
    r = subprocess.run(['claude', 'plugin', 'test', '.'], cwd=kit, capture_output=True, text=True, encoding='utf-8', timeout=300)
    return r.stdout + r.stderr


def main() -> int:
    bad = 0
    for name, (rel, old, new, test) in MUTANTS.items():
        scratch = KIT.parent / f'{KIT.name}-mutant'
        if scratch.exists():
            shutil.rmtree(scratch)
        shutil.copytree(KIT, scratch, ignore=shutil.ignore_patterns('node_modules'))
        f = scratch / rel
        src = f.read_text(encoding='utf-8')
        if src.count(old) != 1:
            print(f'??  {name}: the text to break is not there once'); bad += 1; continue
        f.write_text(src.replace(old, new), encoding='utf-8', newline='')
        out = run(scratch)
        caught = re.search(r'^\(fail\) ' + re.escape(test), out, re.M) is not None
        print(f"{'ok ' if caught else 'NO '} {name}: {'caught' if caught else 'not caught'} by '{test}'")
        bad += 0 if caught else 1
        shutil.rmtree(scratch)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
