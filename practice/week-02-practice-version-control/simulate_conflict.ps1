# PowerShell script to demonstrate and automate merge conflict simulation and resolution
# Task: Practice: Version Control - Data Loading Module Integration

$folder = "practice/week-02-practice-version-control"
$featureBranch = "feature/data-loading-module"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "==> Git Branching, Pull Request & Conflict Resolution Simulation" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Ensure working directory is on main
Write-Host "`n[1] Checking out main branch..." -ForegroundColor Yellow
git checkout main

# 2. Stage base architecture
Write-Host "`n[2] Committing base DataHandler class and interfaces..." -ForegroundColor Yellow
git add "$folder/data_handler.py"
git commit -m "feat(data-handler): implement abstract DataHandler base class with lifecycle hooks"

# 3. Create and switch to feature branch
Write-Host "`n[3] Creating and switching to feature branch: $featureBranch..." -ForegroundColor Yellow
git checkout -b $featureBranch

# 4. Commit feature changes on feature branch (Batch loading, Audit Lineage)
Write-Host "`n[4] Committing feature implementation (batch chunking & audit metadata)..." -ForegroundColor Yellow
git add "$folder/data_loader.py" "$folder/test_data_loader.py" "$folder/__init__.py" "$folder/example_usage.py"
git commit -m "feat(data-loader): implement DataLoader with batch streaming and audit metadata"

# 5. Return to main and simulate concurrent changes from another teammate
Write-Host "`n[5] Returning to main branch and committing concurrent team updates..." -ForegroundColor Yellow
git checkout main

# Teammate commits strict schema validation and custom timeout logic in DataLoader
git add "$folder/data_loader.py"
git commit -m "refactor(data-loader): add strict schema validation and connection timeout settings"

# 6. Attempt merge (triggers merge conflict)
Write-Host "`n[6] Merging $featureBranch into main (Conflict Simulation)..." -ForegroundColor Yellow
git merge $featureBranch

Write-Host "`n[7] Reconciling merge conflict: Integrating both features into data_loader.py..." -ForegroundColor Cyan
git add "$folder/data_loader.py" "$folder/__init__.py"
git commit -m "Merge branch '$featureBranch' into main: Reconcile schema validation with batch chunking and audit metadata"

# 8. Show Git Graph
Write-Host "`n[8] Git commit history graph:" -ForegroundColor Green
git log --graph --oneline --all -n 8

# 9. Verify test suite
Write-Host "`n[9] Running pytest verification suite..." -ForegroundColor Green
python -m pytest "$folder/test_data_loader.py" -v

