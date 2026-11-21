# One-click publish: rebuild README / index -> commit -> push
# Usage: powershell -ExecutionPolicy Bypass -File tools/publish.ps1 "commit message"
param([string]$msg)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:PYTHONUTF8 = "1"
python tools/build.py
if ($LASTEXITCODE -ne 0) { throw "build.py failed" }

git add -A
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "Nothing to commit." -ForegroundColor Yellow    return
}

if (-not $msg) { $msg = "update solutions " + (Get-Date -Format "yyyy-MM-dd") }
git commit -m $msg
git push
Write-Host "Pushed. Pages will refresh in about 30s: https://kaiyuzhao116.github.io/leetcode-hot100-visual/" -ForegroundColor Green
