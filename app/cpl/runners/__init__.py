"""CPL-06 Runner Persistence Service — B6 Execution/Artifact Governance.

Implements docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md
(REQ-B6-001 -> REQ-B6-090 active set, 99 requirements) against
docs/build/B6_EXECUTION_ARTIFACT_EXECUTION_MANDATE_v0.md.

    EXECUTION (execution.py)
        admit_execution, transition_status, persist_runner_report,
        retry_execution

    IDEMPOTENCY (idempotency.py)
        find_existing_by_key, compare_intent

    ARTIFACTS (artifacts.py)
        register_artifact, supersede_artifact,
        check_supersession_consistency

    CLASSIFICATION (classification.py)
        validate_classification

    CORRECTION (correction.py)
        correct_execution_metadata, reconstruct_original_value

    AUTHORITY (authority.py)
        RunnerAuthority

    OUTCOMES (outcomes.py)
        RunnerOutcome, RunnerResult
"""
