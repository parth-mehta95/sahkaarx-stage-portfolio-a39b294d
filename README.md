# SahkaarX Data Engineering Portfolio

Production data engineering repository containing data pipelines, SQL integration, automated testing, and collaborative Git workflow implementations.

## Public Repository URL
`https://github.com/parth-mehta95/sahkaarx-stage-portfolio-a39b294d`

---

## Featured Pipeline Project: Initial Pipeline & Merge Conflict Resolution

### Overview
This project establishes a production-ready ETL data pipeline (`DataPipeline`) with modular extraction, transformation, and SQL loading capabilities, along with a documented collaborative Git merge conflict simulation and resolution.

- **Location**: [`practice/week-01-initialize-data-pipeline-repository-and-resolve/`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/)
- **Core Pipeline Module**: [`pipeline.py`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py)
- **Unit Test Suite**: [`test_pipeline.py`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/test_pipeline.py) (12/12 passing)
- **Conflict Resolution Walkthrough**: [`MERGE_CONFLICT_RESOLUTION.md`](./practice/week-01-initialize-data-pipeline-repository-and-resolve/MERGE_CONFLICT_RESOLUTION.md)
- **Dependencies**: [`requirements.txt`](./requirements.txt)

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

### 4. Run Pipeline Unit Tests
```bash
python -m pytest practice/week-01-initialize-data-pipeline-repository-and-resolve/test_pipeline.py -v
```

---

## Git Workflow & Conflict Resolution

The repository demonstrates a branch-and-merge collaborative Git model:
- **`main`**: Production code branch with strict schema validation and null data handling.
- **`feature/pipeline-initialization`**: Feature branch introducing UTC audit tracking metadata and batch chunking.
- **Resolved Merge Commit**: Merged into `main`, reconciling overlapping edits into an integrated pipeline method.

```text
*   ae57259 (HEAD -> main) Merge branch 'feature/pipeline-initialization' into main
|\  
| * c17a4a2 (feature/pipeline-initialization) feat(pipeline): add UTC audit metadata and batch chunking
* | 7128e24 refactor(pipeline): implement schema validation and null filtering
|/  
* 256b114 feat(pipeline): base DataPipeline ETL class
```
