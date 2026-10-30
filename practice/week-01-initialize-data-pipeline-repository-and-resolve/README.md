# Initialize Data Pipeline Repository and Resolve Merge Conflict

## Task Brief
Create GitHub repo with virtual environment, initialize feature branch, simulate merge conflict with main, and resolve using Git conflict resolution techniques.

## Scenario
Your data team needs a production-ready pipeline repo. Initialize it, practice conflict resolution, and establish collaborative Git workflow.

## Deliverables
- [x] Public GitHub repository configured and initialized
- [x] Production dependencies specified in [`requirements.txt`](./requirements.txt)
- [x] Initial Python pipeline module implemented in [`pipeline.py`](./pipeline.py)
- [x] Automated unit test suite in [`test_pipeline.py`](./test_pipeline.py)
- [x] Conflict simulation and resolution walkthrough in [`MERGE_CONFLICT_RESOLUTION.md`](./MERGE_CONFLICT_RESOLUTION.md)
- [x] PowerShell simulation automation in [`simulate_conflict.ps1`](./simulate_conflict.ps1)

## Success Criteria
- [x] **Conflict Resolution**: Feature branch `feature/pipeline-initialization` created, conflicting changes merged, conflict manually resolved, and committed into history.
- [x] **Code Quality**: Both teammates' features (strict schema validation + UTC audit metadata enrichment) preserved and working harmoniously.
- [x] **Verification**: All 12 unit tests passing cleanly.

---

## Architecture & Pipeline Design

The `DataPipeline` module provides a modular ETL workflow:
1. **Extraction**: `extract_from_records()` converts incoming dictionary records into a DataFrame.
2. **Transformation**: `transform()` performs:
   - Column normalization (lowercase, stripping whitespace, snake_case).
   - Duplicate row removal.
   - **Schema Validation** (from `main` branch): Verifies required columns, raises `ValidationError`.
   - **Data Quality** (from `main` branch): Null filtering with configurable `drop_nulls`.
   - **Audit Metadata** (from `feature` branch): Attaches `processed_at` (UTC ISO timestamp), `pipeline_run_id`, and `record_index`.
   - **Batch Configuration** (from `feature` branch): Configurable `batch_size`.
3. **Loading**: `load_to_sqlite()` loads transformed data into an SQL table via SQLAlchemy with transaction management.
4. **End-to-End Execution**: `run()` orchestrates the full pipeline flow.

---

## Project Setup & Virtual Environment

### 1. Initialize Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Project Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Pipeline Script
```bash
python practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py
```

### 4. Run Automated Test Suite
```bash
python -m pytest practice/week-01-initialize-data-pipeline-repository-and-resolve/test_pipeline.py -v
```

---

## Conflict Resolution Summary

During development, two parallel feature enhancements modified the `transform()` method:
- **`main`**: Introduced strict column checking and null value filtering for data sanitization.
- **`feature/pipeline-initialization`**: Introduced audit metadata tracking and batch configuration.

Merging `feature/pipeline-initialization` into `main` triggered a Git content conflict in `pipeline.py`.
The conflict was manually resolved by combining the parameters into a unified method signature and chaining the validation before metadata enrichment.

```text
*   ae57259 (HEAD -> main) Merge branch 'feature/pipeline-initialization' into main - reconcile schema validation and audit metadata
|\  
| * c17a4a2 (feature/pipeline-initialization) feat(pipeline): add UTC audit metadata and batch chunking
* | 7128e24 refactor(pipeline): implement schema validation and null filtering
|/  
* 256b114 feat(pipeline): base DataPipeline ETL class
```

Refer to [`MERGE_CONFLICT_RESOLUTION.md`](./MERGE_CONFLICT_RESOLUTION.md) for full step-by-step conflict markers and resolution details.

---

## Files in this Directory
- [`pipeline.py`](./pipeline.py): Production `DataPipeline` class with resolved ETL functionality.
- [`test_pipeline.py`](./test_pipeline.py): 12 unit tests verifying extraction, transformation, conflict resolution, and SQL loading.
- [`requirements.txt`](./requirements.txt): Core dependencies (`pandas`, `SQLAlchemy`, `pytest`).
- [`MERGE_CONFLICT_RESOLUTION.md`](./MERGE_CONFLICT_RESOLUTION.md): Complete Git conflict simulation, marker breakdown, and resolution documentation.
- [`simulate_conflict.ps1`](./simulate_conflict.ps1): Automated script to recreate the Git merge conflict on demand.
