"""Stage the paired skills for Claude's native eval runner; no product writes.

python run-routing.py <repository-root> <new-evidence-directory>
The runner forbids eval-dir inside skills/, so the suite is copied outside it.
This evaluates route decisions only; the map-page browser dogfood is separate.
"""
from pathlib import Path
import shutil
import subprocess
import sys

repo, output = (Path(p).resolve() for p in sys.argv[1:])
output.mkdir(parents=True, exist_ok=False)
stage = output / 'plugin'
source = repo / 'plugins/baransu'
for skill in ('draw', 'ui', '_shared'):
    shutil.copytree(source / 'skills' / skill, stage / 'skills' / skill,
                    ignore=shutil.ignore_patterns('evals', '__pycache__', 'node_modules'))
shutil.copytree(source / '.claude-plugin', stage / '.claude-plugin')
suite = stage / 'evals'
suite.mkdir()
for case in (source / 'skills/draw/evals').glob('*-route'):
    shutil.copytree(case, suite / case.name)
command = ['claude', 'plugin', 'eval', str(stage), '--eval-dir', 'evals',
           '--case', '*route', '--runs', '1', '--ablation', 'none',
           '--no-publish', '--trust-plugin', '--output-dir', str(output / 'results')]
with (output / 'command.txt').open('w', encoding='utf-8') as f:
    f.write(subprocess.list2cmdline(command) + '\n')
result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
(output / 'run.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
print(result.stdout, end='')
print(result.stderr, end='', file=sys.stderr)
sys.exit(result.returncode)
