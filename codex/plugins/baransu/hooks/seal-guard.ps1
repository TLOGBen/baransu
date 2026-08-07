# seal-guard.ps1 — Windows-native port of seal-guard.sh (Stop hook).
# Behavioral contract is identical to the bash implementation, line for line:
#   - stdin `stop_hook_active: true` -> exit 0 (loop protection)
#   - not a git repo / clean worktree / no user-facing surface -> exit 0
#   - same-day seal-log line or `SEAL:` commit trailer -> exit 0
#   - miss: append one telemetry JSONL line in EVERY mode, then
#       Codex (PLUGIN_ROOT set): stdout {"decision":"block",...} + exit 0
#       Claude:                  stderr message + exit 2
#   - SEAL_GUARD=log|off degrade to exit 0 after telemetry
# Any detection failure degrades to exit 0 — a heuristic guard must never
# wedge a session on its own bugs (same clause as the bash version).
#
# Env tunables mirror the bash version: SEAL_GUARD, SEAL_GUARD_PATTERNS,
# SEAL_GUARD_PATHS, BARANSU_TELEMETRY_DIR. Note: patterns here are .NET
# regex, not POSIX ERE — the shipped defaults are equivalent; a custom
# SEAL_GUARD_PATTERNS must avoid POSIX classes like [[:alnum:]] (use \w / \W).
# Requires Windows PowerShell 5.1+ (no pwsh-only syntax).

$ErrorActionPreference = 'Stop'
try {
  # --- loop protection (official Stop-hook contract) -------------------------
  $stdinText = ''
  try { $stdinText = [Console]::In.ReadToEnd() } catch { $stdinText = '' }
  if ($stdinText -match '"stop_hook_active"\s*:\s*true') { exit 0 }

  $mode = $env:SEAL_GUARD
  if (-not $mode) { $mode = 'block' }

  # --- early exits ------------------------------------------------------------
  $projectDir = $env:CLAUDE_PROJECT_DIR
  if (-not $projectDir) { $projectDir = (Get-Location).Path }
  $gitRoot = & git -C "$projectDir" rev-parse --show-toplevel 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $gitRoot) { exit 0 }
  $gitRoot = "$gitRoot".Trim()

  # Only uncommitted changes count (conservative by design — misses acceptable).
  $diffLines = & git -C "$gitRoot" diff HEAD --unified=0 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $diffLines) { exit 0 }

  # --- user-facing surface heuristic (tunable) --------------------------------
  # Added lines only; source dirs only; test paths excluded. Same default sets
  # as seal-guard.sh; (^|\W) is the .NET equivalent of (^|[^[:alnum:]_]).
  $patterns = $env:SEAL_GUARD_PATTERNS
  if (-not $patterns) { $patterns = 'println!|eprintln!|console\.(log|error|warn)|printf\(|(^|\W)print\(' }
  $paths = $env:SEAL_GUARD_PATHS
  if (-not $paths) { $paths = 'src|app|lib|bin|cli|ui' }

  $touched = 0
  $currentFile = ''
  foreach ($line in @($diffLines)) {
    if ($line -match '^\+\+\+ b/(.*)$') { $currentFile = $Matches[1]; continue }
    if ($line -notmatch '^\+[^+]') { continue }
    if ($currentFile -notmatch "^($paths)/") { continue }
    if ($currentFile -match 'test|spec') { continue }
    if ($line -match $patterns) { $touched++ }
  }
  if ($touched -eq 0) { exit 0 }

  # --- seal evidence ----------------------------------------------------------
  if ($env:PLUGIN_ROOT) {
    $defaultTelemetryRoot = Join-Path $HOME '.codex\baransu\telemetry'
  } else {
    $defaultTelemetryRoot = Join-Path $HOME '.claude\baransu\telemetry'
  }
  $troot = $env:BARANSU_TELEMETRY_DIR
  if (-not $troot) { $troot = $defaultTelemetryRoot }
  $tdir = Join-Path $troot (Split-Path $gitRoot -Leaf)
  $month = Get-Date -Format 'yyyy-MM'
  $today = Get-Date -Format 'yyyy-MM-dd'
  $sealLog = Join-Path $tdir "seal-log-$month.jsonl"
  if ((Test-Path $sealLog) -and (Select-String -Path $sealLog -Pattern ([regex]::Escape($today)) -Quiet)) {
    exit 0
  }
  $lastMsg = & git -C "$gitRoot" log -1 --format=%B 2>$null
  if ($LASTEXITCODE -eq 0 -and (@($lastMsg) | Where-Object { $_ -match '^SEAL:' })) {
    exit 0
  }

  # --- miss: telemetry in every mode -------------------------------------------
  try {
    New-Item -ItemType Directory -Force -Path $tdir | Out-Null
    $ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'
    $entry = New-Object System.Collections.Specialized.OrderedDictionary
    $entry['ts'] = $ts
    $entry['event'] = 'seal-miss'
    $entry['mode'] = $mode
    $entry['repo'] = "$gitRoot"
    $entry['surfaces'] = $touched
    $json = ConvertTo-Json -InputObject $entry -Compress
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::AppendAllText((Join-Path $tdir "seal-guard-$month.jsonl"), "$json`n", $utf8NoBom)
  } catch { exit 0 }

  # --- verdict -----------------------------------------------------------------
  if ($mode -eq 'off' -or $mode -eq 'log') { exit 0 }

  $message = '偵測到 user-facing 變更尚未 /baransu:seal——請執行 seal 收尾（單次窄域驗收＋直接修正權），或設 SEAL_GUARD=log 降級為僅記錄。'
  if ($env:PLUGIN_ROOT) {
    $verdict = New-Object System.Collections.Specialized.OrderedDictionary
    $verdict['decision'] = 'block'
    $verdict['reason'] = $message
    $verdict['systemMessage'] = $message
    $out = ConvertTo-Json -InputObject $verdict -Compress
    $stdout = New-Object System.IO.StreamWriter([Console]::OpenStandardOutput(), (New-Object System.Text.UTF8Encoding($false)))
    $stdout.WriteLine($out)
    $stdout.Flush()
    exit 0
  }
  $stderr = New-Object System.IO.StreamWriter([Console]::OpenStandardError(), (New-Object System.Text.UTF8Encoding($false)))
  $stderr.WriteLine($message)
  $stderr.Flush()
  exit 2
} catch {
  # Detection failure degrades to allow-stop; never wedge the session.
  exit 0
}
