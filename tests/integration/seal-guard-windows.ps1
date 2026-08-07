param([Parameter(Mandatory=$true)][string]$Guard)
$ErrorActionPreference = 'Stop'
$fails = 0
function Report([bool]$ok, [string]$name) {
  if ($ok) { Write-Output "PASS: $name" } else { Write-Output "FAIL: $name"; $script:fails++ }
}
function New-Repo {
  $d = Join-Path $env:TEMP ("sg-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
  New-Item -ItemType Directory -Path (Join-Path $d 'src') -Force | Out-Null
  git -C $d init -q -b main | Out-Null
  git -C $d -c user.email=t@t -c user.name=t commit -q --allow-empty -m init | Out-Null
  Set-Content -Path (Join-Path $d 'src\main.rs') -Value 'fn main() {}'
  git -C $d add -A | Out-Null
  git -C $d -c user.email=t@t -c user.name=t commit -qm base | Out-Null
  return $d
}
function Touch-Surface([string]$repo) {
  Add-Content -Path (Join-Path $repo 'src\main.rs') -Value 'fn f() { println!("hi user"); }'
}
function New-TempDir {
  $d = Join-Path $env:TEMP ("sgt-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
  New-Item -ItemType Directory -Path $d -Force | Out-Null
  return $d
}
$errFile = Join-Path $env:TEMP 'sg-stderr.txt'
$outFile = Join-Path $env:TEMP 'sg-stdout.txt'
$inFile = Join-Path $env:TEMP 'sg-stdin.txt'
function Invoke-Guard([string]$StdinJson) {
  foreach ($f in @($errFile, $outFile)) { if (Test-Path $f) { Remove-Item $f -Force } }
  [System.IO.File]::WriteAllText($inFile, $StdinJson, (New-Object System.Text.UTF8Encoding($false)))
  $p = Start-Process -FilePath 'powershell' `
    -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Guard) `
    -RedirectStandardInput $inFile -RedirectStandardOutput $outFile -RedirectStandardError $errFile `
    -NoNewWindow -PassThru -Wait
  if (Test-Path $outFile) {
    $script:GuardOut = [System.IO.File]::ReadAllText($outFile, [System.Text.Encoding]::UTF8)
  } else { $script:GuardOut = '' }
  return $p.ExitCode
}
function Guard-Stderr {
  if (Test-Path $errFile) { return [System.IO.File]::ReadAllText($errFile, [System.Text.Encoding]::UTF8) }
  return ''
}

# S1 — loop protection: stop_hook_active true -> exit 0, no telemetry
$r = New-Repo; Touch-Surface $r; $t = New-TempDir
$env:CLAUDE_PROJECT_DIR = $r; $env:BARANSU_TELEMETRY_DIR = $t
$rc = Invoke-Guard '{"hook_event_name":"Stop","stop_hook_active": true}'
$noTelemetry = -not (Get-ChildItem -Path $t -Recurse -Filter 'seal-guard-*.jsonl' -ErrorAction SilentlyContinue)
Report (($rc -eq 0) -and $noTelemetry) 'S1 stop_hook_active=true exits 0 without telemetry'

# S2 — Claude-contract miss: exit 2 + instruction on stderr + block-mode telemetry
$rc = Invoke-Guard '{"stop_hook_active": false}'
$stderrText = Guard-Stderr
$repoLeaf = Split-Path $r -Leaf
$month = Get-Date -Format 'yyyy-MM'
$tline = Get-Content (Join-Path (Join-Path $t $repoLeaf) "seal-guard-$month.jsonl") -Tail 1 -Encoding UTF8
$parsed = $tline | ConvertFrom-Json
Report (($rc -eq 2) -and ($stderrText -match 'baransu:seal') -and ($stderrText -match 'SEAL_GUARD=log') -and ($parsed.mode -eq 'block') -and ($parsed.event -eq 'seal-miss') -and ($parsed.surfaces -eq 1)) 'S2 Claude miss: exit 2 + zh instruction + block telemetry'

# S3 — Codex-contract miss: PLUGIN_ROOT set -> exit 0 + decision:block JSON
$env:PLUGIN_ROOT = 'C:\fake\plugin'
$rc = Invoke-Guard '{"hook_event_name":"Stop"}'
$json = $null
try { $json = "$script:GuardOut" | ConvertFrom-Json } catch { $json = $null }
Report (($rc -eq 0) -and $json -and ($json.decision -eq 'block') -and ($json.reason -match 'baransu:seal') -and ($json.systemMessage -eq $json.reason)) 'S3 Codex miss: exit 0 + decision:block JSON'
Remove-Item Env:PLUGIN_ROOT

# S4 — SEAL_GUARD=log degrades to exit 0 with log-mode telemetry
$env:SEAL_GUARD = 'log'
$rc = Invoke-Guard '{"stop_hook_active": false}'
$tline = Get-Content (Join-Path (Join-Path $t $repoLeaf) "seal-guard-$month.jsonl") -Tail 1 -Encoding UTF8
$parsed = $tline | ConvertFrom-Json
Report (($rc -eq 0) -and ($parsed.mode -eq 'log')) 'S4 SEAL_GUARD=log exits 0 with log telemetry'
Remove-Item Env:SEAL_GUARD

# S5 — same-day seal-log evidence -> exit 0, no new telemetry
$t2 = New-TempDir
$env:BARANSU_TELEMETRY_DIR = $t2
$tdir2 = Join-Path $t2 $repoLeaf
New-Item -ItemType Directory -Path $tdir2 -Force | Out-Null
$today = Get-Date -Format 'yyyy-MM-dd'
Set-Content -Path (Join-Path $tdir2 "seal-log-$month.jsonl") -Value ('{"ts":"' + $today + 'T00:00:00","skill":"seal","result":"pass"}')
$rc = Invoke-Guard '{"stop_hook_active": false}'
$noNew = -not (Get-ChildItem -Path $t2 -Recurse -Filter 'seal-guard-*.jsonl' -ErrorAction SilentlyContinue)
Report (($rc -eq 0) -and $noNew) 'S5 same-day seal evidence exits 0 without telemetry'

# S6 — clean worktree -> exit 0
$r2 = New-Repo; $t3 = New-TempDir
$env:CLAUDE_PROJECT_DIR = $r2; $env:BARANSU_TELEMETRY_DIR = $t3
$rc = Invoke-Guard '{"stop_hook_active": false}'
Report ($rc -eq 0) 'S6 clean worktree exits 0'

Remove-Item -Recurse -Force $r, $r2, $t, $t2, $t3 -ErrorAction SilentlyContinue
Write-Output "=== ps-verify: fails=$fails"
if ($fails -gt 0) { exit 1 } else { exit 0 }
