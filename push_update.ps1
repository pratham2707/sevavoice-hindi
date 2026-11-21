#!/usr/bin/env pwsh
# push_update.ps1 — Easy future updates for sevavoice-hindi
# Stages changes, verifies .env is not tracked, commits, and pushes to origin main.
#
# Usage:
#   ./push_update.ps1                          # default message
#   ./push_update.ps1 "feat: add new endpoint" # custom message

param(
    [Parameter(Mandatory = $false)]
    [string]$Message = "chore: update project"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $projectRoot

Write-Host "==> Checking git status..." -ForegroundColor Cyan

# Ensure we're in a git repo
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: .git directory not found. Run 'git init' first." -ForegroundColor Red
    Pop-Location
    exit 1
}

# Check that .env is NOT tracked by git
$trackedEnv = git ls-files --error-unmatch .env 2>$null
if ($trackedEnv) {
    Write-Host "ERROR: .env is tracked by git! Remove it before pushing." -ForegroundColor Red
    Write-Host "Run: git rm --cached .env" -ForegroundColor Yellow
    Pop-Location
    exit 1
}

# Stage all changes (safe: .gitignore excludes .env, .venv, __pycache__, etc.)
Write-Host "==> Staging changes..." -ForegroundColor Cyan
git add .

# Show what's staged for confirmation
Write-Host "==> Staged files:" -ForegroundColor Cyan
git diff --cached --name-only

# Commit
Write-Host "==> Committing: $Message" -ForegroundColor Cyan
git commit -m $Message

# Push
Write-Host "==> Pushing to origin main..." -ForegroundColor Cyan
git push -u origin main

Write-Host "==> Done!" -ForegroundColor Green
Pop-Location