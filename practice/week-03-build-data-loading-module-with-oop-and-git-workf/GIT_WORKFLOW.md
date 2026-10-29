# Step-by-Step Git Workflow and Conflict Resolution Guide

This document provides the exact commands and workflow to fulfill the submission requirements:
1. Create feature branch from `main` and add `DatabaseLoader` class
2. Commit changes and push to remote feature branch
3. Open pull request on GitHub with description of changes
4. Resolve any merge conflicts and update PR
5. Merge to `main` after review

---

## Step 1: Create Feature Branch from `main`

Ensure your local `main` branch is up to date, then branch off:

```bash
# Switch to main branch and pull latest changes
git checkout main
git pull origin main

# Create and switch to the feature branch
git checkout -b feature/database-loader
```

---

## Step 2: Implement and Commit Changes with Clear Messages

Stage and commit files with structured conventional commit messages:

```bash
# Stage DataHandler and DatabaseLoader implementations
git add practice/week-03-build-data-loading-module-with-oop-and-git-workf/data_handler.py
git commit -m "feat(data-loader): implement abstract DataHandler base class with lifecycle hooks"

git add practice/week-03-build-data-loading-module-with-oop-and-git-workf/database_loader.py
git commit -m "feat(database-loader): implement DatabaseLoader extending DataHandler for SQL execution"

git add practice/week-03-build-data-loading-module-with-oop-and-git-workf/__init__.py
git commit -m "feat(module): export DataHandler, DatabaseLoader, and custom exceptions"

# Stage unit tests and demo
git add practice/week-03-build-data-loading-module-with-oop-and-git-workf/test_database_loader.py
git commit -m "test(database-loader): add comprehensive unit test suite covering OOP and SQL operations"

git add practice/week-03-build-data-loading-module-with-oop-and-git-workf/example_usage.py
git commit -m "docs(demo): add runnable example script demonstrating DatabaseLoader usage"

# Push feature branch to GitHub remote
git push -u origin feature/database-loader
```

---

## Step 3: Open Pull Request on GitHub

1. Navigate to your repository on GitHub.
2. Click **Compare & pull request** for `feature/database-loader`.
3. Set base repository: `main` <- head repository: `feature/database-loader`.
4. Copy the contents of [`PULL_REQUEST.md`](./PULL_REQUEST.md) into the PR description.
5. Assign reviewers and label as `enhancement` / `data-engineering`.

---

## Step 4: Conflict Resolution Workflow

If another commit has updated `main` while your branch was in review, GitHub will flag merge conflicts. Follow these steps to resolve them:

```bash
# Fetch latest updates from remote
git fetch origin

# Ensure you are on your feature branch
git checkout feature/database-loader

# Merge main into your feature branch to trigger conflict resolution locally
git merge origin/main
```

### Locating and Resolving Conflict Markers
Git marks conflicting sections in affected files:

```text
<<<<<<< HEAD (current feature branch)
from data_handler import DataHandler
from database_loader import DatabaseLoader
=======
from base_config import DEFAULT_DB_PATH
>>>>>>> origin/main
```

1. Edit the file to integrate the intended changes cleanly.
2. Remove all `<<<<<<<`, `=======`, and `>>>>>>>` markers.
3. Verify test suite passes:
   ```bash
   python -m unittest practice/week-03-build-data-loading-module-with-oop-and-git-workf/test_database_loader.py
   ```
4. Stage the resolved files:
   ```bash
   git add practice/week-03-build-data-loading-module-with-oop-and-git-workf/
   ```
5. Commit the merge resolution:
   ```bash
   git commit -m "Merge branch 'main' into feature/database-loader: resolve conflicts in module exports"
   ```
6. Push the updated feature branch to update the PR:
   ```bash
   git push origin feature/database-loader
   ```

---

## Step 5: Merge to `main` After Review

Once approved on GitHub:
1. Merge the Pull Request via GitHub interface (or locally):
   ```bash
   git checkout main
   git merge --no-ff feature/database-loader -m "Merge pull request: DatabaseLoader module with OOP and Git workflow"
   git push origin main
   ```
2. Delete the remote feature branch if desired:
   ```bash
   git push origin --delete feature/database-loader
   ```

---

## Deliverables & Submission Checklist

- [x] **`DatabaseLoader` class extending `DataHandler`**: Implemented in [`database_loader.py`](./database_loader.py) and [`data_handler.py`](./data_handler.py).
- [x] **Connects to SQL Database**: Verified with SQLite in-memory and persistent storage.
- [x] **Clear Commit Messages**: Documented in [`PULL_REQUEST.md`](./PULL_REQUEST.md) and [`GIT_WORKFLOW.md`](./GIT_WORKFLOW.md).
- [x] **Conflict Resolution Steps**: Documented in detail with reproducible commands.
- [x] **Ready for GitHub submission**: PR templates, guides, and test scripts prepared.

