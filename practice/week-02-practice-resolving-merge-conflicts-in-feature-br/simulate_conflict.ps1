# PowerShell script to automate / demonstrate merge conflict simulation and resolution

$targetFile = "practice/week-02-practice-resolving-merge-conflicts-in-feature-br/data_handler.py"
$branchName = "feature/data-handler-summary"

Write-Host "==> Starting Merge Conflict Demonstration..." -ForegroundColor Cyan

# 1. Ensure we are on main
git checkout main

# 2. Stage current base state
git add $targetFile
git commit -m "feat: base DataHandler class" -q

# 3. Create feature branch and commit feature addition
git checkout -b $branchName
git add $targetFile
git commit -m "feat(data-handler): implement get_summary_statistics" -q

# 4. Return to main and commit teammate's changes
git checkout main
git add $targetFile
git commit -m "refactor(data-handler): implement validate_and_clean" -q

# 5. Attempt merge (will trigger conflict)
Write-Host "==> Attempting merge from $branchName into main..." -ForegroundColor Yellow
git merge $branchName

Write-Host "==> Staging resolved file and completing merge..." -ForegroundColor Green
git add $targetFile
git commit -m "Merge branch '$branchName' into main - preserve validate_and_clean and get_summary_statistics" -q

Write-Host "==> Git Graph:" -ForegroundColor Cyan
git log --graph --oneline --all -n 5

