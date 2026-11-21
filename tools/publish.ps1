# One-click publish: rebuild README / index -> commit -> push
# Usage: tools\publish.ps1 "commit message"
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
    Write-Host "Nothing to commit." -ForegroundColor Yellow
    return
}

if (-not $msg) { $msg = "update solutions " + (Get-Date -Format "yyyy-MM-dd") }
git commit -m $msg

git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "Direct push failed, retrying through 127.0.0.1:12450 ..." -ForegroundColor Yellow
    git -c http.proxy=http://127.0.0.1:12450 push
}
if ($LASTEXITCODE -ne 0) { throw "git push failed, check your network" }

Write-Host "Pushed. Pages refresh in about 30s: https://kaiyuzhao116.github.io/leetcode-hot100-visual/" -ForegroundColor Green
