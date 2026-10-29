# Practice Resolving Merge Conflicts in Feature Branch

## Task Brief
Create a feature branch, simulate a merge conflict with main, and resolve it using Git conflict resolution techniques.

## Scenario
A teammate modified the DataHandler class while you added a new method. Resolve the merge conflict and merge your feature branch cleanly.

## Deliverables
- [x] Feature branch with conflict resolution (`feature/data-handler-summary`)
- [x] Merged code in main branch (`data_handler.py`)
- [x] Comprehensive test suite (`test_data_handler.py`)
- [x] Conflict resolution documentation (`MERGE_CONFLICT_RESOLUTION.md`)

## Success Criteria
- [x] Merge conflict identified and resolved correctly
- [x] Both changes preserved in final code (teammate's `validate_and_clean` + feature's `get_summary_statistics`)

## Files in this Directory
- [`data_handler.py`](./data_handler.py): Resolved `DataHandler` class containing both the teammate's data cleaning method and the new summary statistics method.
- [`test_data_handler.py`](./test_data_handler.py): Unit tests verifying both methods independently and in conjunction.
- [`MERGE_CONFLICT_RESOLUTION.md`](./MERGE_CONFLICT_RESOLUTION.md): Complete walkthrough detailing the Git conflict simulation, conflict markers, manual resolution, and verification.
- [`simulate_conflict.ps1`](./simulate_conflict.ps1): Automated script to recreate the branch conflict and merge commit sequence in Git.
