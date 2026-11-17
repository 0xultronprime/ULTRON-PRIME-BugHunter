# =====================================================================
# install-ultron.ps1 — One-click installer for ULTRON PRIME BugHunter
# Windows / PowerShell. Native port of scripts/install-ultron.sh.
#
# Installs:
#   - skills/* (86) -> ~\.claude\skills\ (and, when forced/detected,
#     ~\.agents\skills\, ~\.hermes\skills\, ~\.gemini\config\skills\)
#   - commands\*.md -> ~\.claude\commands\
#   - ultron CLI -> ~\.local\bin\ultron.cmd (wraps ultron.py)
#   - cbh CLI is left untouched.
#
# Flags: -All -Agents -Hermes -AntiGravity -NoProfile -Uninstall -Help
# Idempotent. Requires: PowerShell 5.1+ / 7+. No network calls.
# =====================================================================
[CmdletBinding()]
param(
  [switch]$All, [switch]$Agents, [switch]$Hermes, [switch]$AntiGravity,
  [switch]$NoProfile, [switch]$Uninstall, [switch]$Help
)
if ($Help) { Get-Content $PSCommandPath -TotalCount 16 | ForEach-Object { $_ -replace '^# ?','' }; exit 0 }
$RepoDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$Bundle = "ultron-prime-bughunter"
$ManifestDir = Join-Path $HOME ".claude\.skill-manifests"
$Manifest = Join-Path $ManifestDir "$Bundle.txt"
$BinDir = Join-Path $HOME ".local\bin"

if ($Uninstall) {
  if (Test-Path $Manifest) {
    Get-Content $Manifest | Where-Object { $_ } | ForEach-Object { if (Test-Path $_) { Remove-Item $_ -Recurse -Force } }
    Remove-Item $Manifest -Force; Remove-Item (Join-Path $BinDir "ultron.cmd") -Force -ErrorAction SilentlyContinue
    Write-Host "ULTRON PRIME BugHunter uninstalled."
  } else { Write-Host "No manifest at $Manifest — nothing tracked to uninstall." }
  exit 0
}
New-Item -ItemType Directory -Force -Path $ManifestDir, $BinDir | Out-Null
Set-Content -Path $Manifest -Value $null

function Install-SkillsTo($dest) {
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Get-ChildItem "$RepoDir\skills" -Directory | ForEach-Object {
    $target = Join-Path $dest $_.Name
    if (Test-Path $target) { Remove-Item $target -Recurse -Force }
    Copy-Item $_.FullName $target -Recurse
    Add-Content -Path $Manifest -Value $target
  }
  Write-Host "  skills -> $dest"
}
Write-Host "ULTRON PRIME BugHunter — installing..."
Install-SkillsTo (Join-Path $HOME ".claude\skills")
New-Item -ItemType Directory -Force -Path (Join-Path $HOME ".claude\commands") | Out-Null
Copy-Item "$RepoDir\commands\*.md" (Join-Path $HOME ".claude\commands\") -Force
Add-Content -Path $Manifest -Value (Join-Path $HOME ".claude\commands")
if ($Agents -or ($All -and (Test-Path "$HOME\.agents"))) { Install-SkillsTo (Join-Path $HOME ".agents\skills") }
if ($Hermes -or ($All -and (Test-Path "$HOME\.hermes"))) { Install-SkillsTo (Join-Path $HOME ".hermes\skills") }
if ($AntiGravity -or ($All -and (Test-Path "$HOME\.gemini"))) { Install-SkillsTo (Join-Path $HOME ".gemini\config\skills") }

$UltronCmd = Join-Path $BinDir "ultron.cmd"
"@echo off`r`npython `"$RepoDir\ultron.py`" %*" | Set-Content -Path $UltronCmd -Encoding Ascii
Add-Content -Path $Manifest -Value $UltronCmd
Write-Host "  ultron CLI -> $UltronCmd"
if (-not $NoProfile) {
  $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
  if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    Write-Host "  PATH: $BinDir added to user PATH (restart terminal to pick up)"
  }
}
Write-Host ""
Write-Host "Done. Verify with:"
Write-Host "  ultron version"
Write-Host "  ultron skills     # should list 86 skills"
Write-Host "  ultron triage sample-findings.json"
Write-Host "  ultron report sample-findings.json --out sample-report.html"
Write-Host "Original cbh CLI is untouched: cbh --help"
