# PowerShell script to automate / demonstrate merge conflict simulation and resolution
# Task: Initialize Data Pipeline Repository and Resolve Merge Conflict

$targetFile = "practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py"
$branchName = "feature/pipeline-initialization"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "==> Starting Git Merge Conflict Simulation & Resolution...  " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Ensure working directory is on main
git checkout main

# 2. Stage current base state of the data pipeline module
git add $targetFile
git commit -m "feat(pipeline): base DataPipeline ETL class" -q

# 3. Create feature branch and commit feature addition (audit metadata and batching)
git checkout -b $branchName
git add $targetFile
git commit -m "feat(pipeline): add UTC audit metadata and batch chunking" -q

# 4. Return to main and commit teammate's changes (schema validation and null filtering)
git checkout main
git add $targetFile
git commit -m "refactor(pipeline): implement schema validation and null filtering" -q

# 5. Attempt merge (will trigger conflict)
Write-Host "==> Attempting merge from $branchName into main..." -ForegroundColor Yellow
git merge $branchName

Write-Host "==> Resolving conflict: Combining schema validation with audit metadata..." -ForegroundColor Cyan
# 6. Stage resolved file and complete merge
git add $targetFile
git commit -m "Merge branch '$branchName' into main - reconcile schema validation and audit metadata" -q

Write-Host "==> Git Graph:" -ForegroundColor Green
git log --graph --oneline --all -n 6

Write-Host "==> Running Test Suite to Verify Resolved Pipeline..." -ForegroundColor Green
python -m pytest practice/week-01-initialize-data-pipeline-repository-and-resolve/test_pipeline.py -v

