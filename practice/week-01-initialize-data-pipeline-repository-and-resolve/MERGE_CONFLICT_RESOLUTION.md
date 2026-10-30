# Git Merge Conflict Resolution Walkthrough

## Overview
This document details the end-to-end collaborative Git workflow, conflict simulation, manual resolution, and verification for the production `DataPipeline` module between `main` and the feature branch (`feature/pipeline-initialization`).

---

## 1. Scenario Recap

- **Base Class**: `DataPipeline` provides modular Extraction, Transformation, and Loading (ETL) into SQLite/SQL databases.
- **Teammate's Modification (on `main`)**: Enforced strict schema validation (`required_columns`), error checking (`ValidationError`), and data quality filtering (`drop_nulls`).
- **Feature Branch Addition (on `feature/pipeline-initialization`)**: Added UTC audit tracking (`processed_at`, `pipeline_run_id`, `record_index`) and downstream batch chunking configuration (`batch_size`).
- **The Conflict**: Both developers modified the same method (`transform()`) within `pipeline.py`.

---

## 2. Step-by-Step Command Log

### Step 1: Base Pipeline Setup
```bash
# Ensure working branch is main
git checkout main

# Stage and commit initial base pipeline
git add practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py
git commit -m "feat(pipeline): base DataPipeline ETL class"
```

### Step 2: Create Feature Branch and Implement Audit Metadata
```bash
# Create and switch to feature branch
git checkout -b feature/pipeline-initialization

# Implement UTC audit metadata and batch chunking
git add practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py
git commit -m "feat(pipeline): add UTC audit metadata and batch chunking"
```

### Step 3: Teammate's Commit on `main` (Parallel Development)
```bash
# Switch back to main
git checkout main

# Teammate introduces schema validation and null filtering
git add practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py
git commit -m "refactor(pipeline): implement schema validation and null filtering"
```

### Step 4: Attempt Merge (Triggers Conflict)
```bash
git merge feature/pipeline-initialization
```

**Git Merge Conflict Output:**
```text
Auto-merging practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py
CONFLICT (content): Merge conflict in practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py
Automatic merge failed; fix conflicts and then commit the result.
```

---

## 3. Conflict Anatomy & Resolution

### Conflict Markers in `pipeline.py`
```python
<<<<<<< HEAD
    # -------------------------------------------------------------------------
    # Main Branch (Teammate's Changes):
    # Enforce schema validation and null filtering for data quality
    # -------------------------------------------------------------------------
    def transform(
        self,
        required_columns: Optional[List[str]] = None,
        drop_nulls: bool = True,
    ) -> pd.DataFrame:
        if self.raw_data is None:
            raise PipelineError("No data to transform. Run extraction first.")

        df = self.raw_data.copy()
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
        df = df.drop_duplicates()

        if required_columns:
            missing_cols = [c for c in required_columns if c not in df.columns]
            if missing_cols:
                raise ValidationError(f"Missing required columns in dataset: {missing_cols}")

        if drop_nulls:
            df = df.dropna()

        self.transformed_data = df
        return self.transformed_data
=======
    # -------------------------------------------------------------------------
    # Feature Branch (Your Changes):
    # Enforce UTC audit tracking, execution IDs, and batch configuration
    # -------------------------------------------------------------------------
    def transform(
        self,
        add_metadata: bool = True,
        batch_size: Optional[int] = None,
    ) -> pd.DataFrame:
        if self.raw_data is None:
            raise PipelineError("No data to transform. Run extraction first.")

        df = self.raw_data.copy()
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
        df = df.drop_duplicates()

        if add_metadata:
            df["processed_at"] = pd.Timestamp.now(tz="UTC").isoformat()
            df["pipeline_run_id"] = f"{self.name}_run"
            df["record_index"] = range(1, len(df) + 1)

        if batch_size is not None and batch_size > 0:
            logger.info(f"Configured batch chunking: {batch_size}")

        self.transformed_data = df
        return self.transformed_data
>>>>>>> feature/pipeline-initialization
```

### Resolution Strategy
1. **Reconcile Function Signature**: Include both sets of optional arguments:
   `def transform(self, required_columns=None, drop_nulls=True, add_metadata=True, batch_size=None)`
2. **Execute In Sequence**:
   - Apply base normalization first (strip whitespace, lowercase, eliminate duplicate rows).
   - Apply schema validation & null filtering (ensuring clean data before metadata attachment).
   - Enrich with UTC timestamp, execution run ID, and record index.
   - Configure batch processing parameters.
3. **Remove Git Conflict Markers**: Erase `<<<<<<< HEAD`, `=======`, and `>>>>>>> feature/pipeline-initialization`.

---

## 4. Completing the Merge and Verifying

### Stage and Commit Resolved Merge
```bash
git add practice/week-01-initialize-data-pipeline-repository-and-resolve/pipeline.py
git commit -m "Merge branch 'feature/pipeline-initialization' into main - reconcile schema validation and audit metadata"
```

### Run Automated Unit Test Suite
```bash
python -m pytest practice/week-01-initialize-data-pipeline-repository-and-resolve/test_pipeline.py -v
```

**Test Execution Results:**
```text
============================= test session starts =============================
collected 12 items

practice/.../test_pipeline.py::test_pipeline_initialization PASSED         [  8%]
practice/.../test_pipeline.py::test_extraction_empty_records_raises_error PASSED [ 16%]
practice/.../test_pipeline.py::test_extraction_valid_records PASSED        [ 25%]
practice/.../test_pipeline.py::test_transform_unextracted_raises_error PASSED [ 33%]
practice/.../test_pipeline.py::test_main_branch_schema_validation PASSED   [ 41%]
practice/.../test_pipeline.py::test_main_branch_drop_nulls PASSED          [ 50%]
practice/.../test_pipeline.py::test_feature_branch_audit_metadata PASSED   [ 58%]
practice/.../test_pipeline.py::test_feature_branch_batch_configuration PASSED [ 66%]
practice/.../test_pipeline.py::test_combined_resolved_transform PASSED    [ 75%]
practice/.../test_pipeline.py::test_load_to_sqlite PASSED                 [ 83%]
practice/.../test_pipeline.py::test_load_untransformed_raises_error PASSED [ 91%]
practice/.../test_pipeline.py::test_end_to_end_run_workflow PASSED         [100%]

============================= 12 passed in 1.17s ==============================
```

### Git Log Verification
```bash
git log --graph --oneline --all -n 6
```
```text
*   ae57259 (HEAD -> main) Merge branch 'feature/pipeline-initialization' into main - reconcile schema validation and audit metadata
|\  
| * c17a4a2 (feature/pipeline-initialization) feat(pipeline): add UTC audit metadata and batch chunking
* | 7128e24 refactor(pipeline): implement schema validation and null filtering
|/  
* 256b114 feat(pipeline): base DataPipeline ETL class
```

### Push to Remote Repository
```bash
# Push main branch
git push origin main

# Push feature branch for collaborative review
git push origin feature/pipeline-initialization
```

---

## 5. Summary of Deliverables
- [x] **Public GitHub Repository**: Configured with remote `origin` pointing to GitHub portfolio.
- [x] **Virtual Environment & Dependencies**: `requirements.txt` with pandas, sqlalchemy, and pytest.
- [x] **Initial Python Module**: Modular `DataPipeline` ETL class in `pipeline.py`.
- [x] **Conflict Simulated & Resolved**: Merge conflict triggered between `main` and `feature/pipeline-initialization` and reconciled cleanly.
- [x] **Test Verification**: 12/12 unit tests passing verifying both individual and combined functionality.
- [x] **Git History Log**: Documented merge DAG with commit parents.

