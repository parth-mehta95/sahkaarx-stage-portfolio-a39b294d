# SahkaarX Data Engineering Portfolio

Production data engineering repository containing data pipelines, SQL integration, automated testing, and collaborative Git workflow implementations.

## Public Repository URL
`https://github.com/parth-mehta95/sahkaarx-stage-portfolio-a39b294d`

---

## Featured Projects & Weekly Milestones

### Week 2: Version Control — Production Data Loading Module, Pull Request & Peer Review

- **Location**: [`practice/week-02-practice-version-control/`](./practice/week-02-practice-version-control/)
- **Core Modules**:
  - [`data_handler.py`](./practice/week-02-practice-version-control/data_handler.py): Abstract base class (`DataHandler`) with connection lifecycle, context manager protocol, and error hierarchy.
  - [`data_loader.py`](./practice/week-02-practice-version-control/data_loader.py): Production `DataLoader` module extending `DataHandler`, supporting parameterized SQL execution, batch chunking, schema validation, audit metadata lineage, and transaction rollback safety.
  - [`example_usage.py`](./practice/week-02-practice-version-control/example_usage.py): Runnable end-to-end pipeline demonstration script.
- **Unit Test Suite**: [`test_data_loader.py`](./practice/week-02-practice-version-control/test_data_loader.py) (**22/22 passing**)
- **Pull Request Documentation**: [`PULL_REQUEST.md`](./practice/week-02-practice-version-control/PULL_REQUEST.md) (PR #24 merged into `main`)
- **Merge Conflict Resolution**: [`MERGE_CONFLICT_RESOLUTION.md`](./practice/week-02-practice-version-control/MERGE_CONFLICT_RESOLUTION.md)
- **Peer Code Review**: [`PEER_PULL_REQUEST_REVIEW.md`](./practice/week-02-practice-version-control/PEER_PULL_REQUEST_REVIEW.md) (Review on teammate PR #25)
- **Conflict Automation Script**: [`simulate_conflict.ps1`](./practice/week-02-practice-version-control/simulate_conflict.ps1)

---

### Week 1: Initial Pipeline & Merge Conflict Resolution

- **Location**: [`practice/week-01-initialize-data-pipeline-repository-and-resolve/`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/)
- **Core Pipeline Module**: [`pipeline.py`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py)
- **Unit Test Suite**: [`test_pipeline.py`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/test_pipeline.py) (**12/12 passing**)
- **Conflict Resolution Walkthrough**: [`MERGE_CONFLICT_RESOLUTION.md`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/MERGE_CONFLICT_RESOLUTION.md)
- **Conflict Simulation Script**: [`simulate_conflict.ps1`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/simulate_conflict.ps1)

---

## Quickstart & Environment Setup

### 1. Initialize Python Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate    # Linux / macOS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Environment
```bash
python test_environment.py
```

### 4. Run All Unit Test Suites (34/34 passing)
```bash
python -m pytest practice/ -v
```

### 5. Run Week 2 Data Loading Pipeline Demonstration
```bash
python practice/week-02-practice-version-control/example_usage.py
```

---

## Git Workflow & Branch Model

The repository demonstrates a branch-and-merge collaborative Git model with conflict resolution:
- **`main`**: Production release branch with schema validation and null data handling.
- **`feature/data-loading-module`**: Feature branch introducing `DataLoader`, batch streaming, audit lineage, and transactions.
- **Resolved Pull Request**: Merged into `main`, reconciling overlapping edits into an integrated pipeline module.

```text
*   ae57259 (HEAD -> main) Merge pull request #24 from feature/data-loading-module
|\  
| * d4e5127 feat(loader): add batch chunking and audit metadata tagging
| * c3b8901 feat(loader): add transaction context manager with automatic rollback
| * c17a4a2 fix(security): enforce parameterized query bindings against SQL injection
* | 7128e24 refactor(loader): add connection timeout and schema validation logic
|/  
* 256b114 feat(handler): base DataHandler abstract class
```
