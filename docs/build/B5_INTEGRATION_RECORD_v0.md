# CPL — B5 Case Governance Integration Record v0

## 1. Authorization chain

```text
Governance HEAD that authorized B5 build:
  b2d2371e05dfefc488479a75a53aff37e64f5ed8

WHAT:                     FROZEN (f53fce8f0c79aa3b5f041a964883ab8283671584)
Requirements:              FROZEN (a36d9e8c2ca7a435e9cd7e1ec97ee38fcc0f9ad3, 115 requirements)
Execution Mandate:          ISSUED (b2d2371e05dfefc488479a75a53aff37e64f5ed8)
```

## 2. Accepted candidate

```text
Accepted candidate SHA:
  c60c592029389f09ab4b8da76281d762200c9c1e

Accepted tree SHA:
  7c0918581c5ac8e0cef0ed3fa141e9c223eded82

Base (code baseline):
  1bb3c724eddc9f9df4a7104ab99e8f6cdeafa628 (integrated B4 software baseline)

Prior WIP checkpoints on this branch (history, not separately accepted):
  f6fca74  initial WIP checkpoint
  00cdfee  R1-R6 bounded repair
  c60c592  R7 bounded repair (final)
```

## 3. Independent DevOps Verification (pre-integration)

Performed from a completely fresh workspace (fresh clone from bundle, fresh venv, fresh PostgreSQL role/database), not reusing the build sandbox.

```text
SHA/tree identity:              PASS
B4 baseline ancestry:           PASS
Previous candidate ancestry:    PASS (00cdfee confirmed ancestor)
Clean checkout / working tree:  PASS
Migration 025->026:              PASS
Migration round-trip:           PASS
Deferred FK (canonical_case_decisions.case_id):
  condeferrable=t, condeferred=t — verified directly via pg_constraint
Full regression:                190/190 (152 B1-B4 + 38 B5, independently
                                  recomputed, not trusted from the report)
/health, /ready:                PASS
```

**Original adversarial probes performed independently** (not reused from the candidate's own test suite):
1. Raw SQL statement-order interception at the SQLAlchemy engine level — confirmed `INSERT INTO canonical_case_decisions` fires before `INSERT INTO cases`.
2. Deferred-FK integrity-bypass probe — an orphaned decision (no matching Case) was deliberately committed; `COMMIT` correctly failed with `IntegrityError`, proving the deferred constraint still genuinely enforces referential integrity.
3. `UNRESOLVED` boundary probe — confirmed a `REJECTED` (non-`HOLD`) B4 asset-merge decision does not incorrectly trigger `UNRESOLVED`.
4. Idempotency-by-identity probe — replayed `create_case` with the same idempotency key but different Contact/Asset payload; confirmed the original result is returned and no second Case is created.

**Verdict:** `ACCEPT_CANDIDATE`

## 4. Integration strategy

`NO-FF MERGE`, following the same mechanism used for B4 integration. A fresh integration branch (`b5-integration`) was created from the exact canonical pre-integration `main`, then the exact accepted candidate commit was merged into it by SHA (never by branch name), preserving both histories.

```text
Pre-integration canonical main:
  b2d2371e05dfefc488479a75a53aff37e64f5ed8

Merge conflicts:
  NONE

Integrated SHA:
  2ac075daea7d162825ed73ded0c7548011242a8f

Integrated tree:
  93bfe9b3cac951e5ab31f6cae982712b4d44b46f

Integration parents:
  parent 1: b2d2371e05dfefc488479a75a53aff37e64f5ed8 (governance main)
  parent 2: c60c592029389f09ab4b8da76281d762200c9c1e (accepted candidate)
```

**Candidate content preservation:** the diff between the accepted candidate and the integrated result is exactly the 16 main-side governance documents (all pure additions) — zero unexpected implementation delta.

**Governance preservation:** `docs/build/` is byte-identical between pre-integration main and the integrated commit.

## 5. Main before / after integration

```text
main BEFORE:
  b2d2371e05dfefc488479a75a53aff37e64f5ed8

main AFTER:
  2ac075daea7d162825ed73ded0c7548011242a8f
```

Both the accepted candidate lineage and the pre-integration governance lineage are confirmed ancestors of the final `main`.

## 6. Post-integration migration results

```text
Prior migrations 001-021:  unchanged (single linear chain, no
                             duplicate down_revision)
Migration head:              026
Fresh PostgreSQL clean install (from real pushed main, fresh clone,
  fresh venv, fresh DB, fresh role):  PASS
Migration round-trip (025<->026):     PASS
Deferred FK re-confirmed on
  post-integration database:          condeferrable=t, condeferred=t
```

## 7. Test composition (independently recomputed on real, pushed main)

```text
B1-B4 baseline:   152 / 152
B5 (all four
  B5 test files):  38 / 38
                   ------
TOTAL:            190 / 190

Composition verified by isolated pytest runs (--ignore flags), not
merely by reading the reported total.
```

## 8. Health checks (real, pushed main, independent clone)

```text
/health:  {"status":"ok","service":"cpl"}          PASS
/ready:   {"application":"ready","database":"reachable"}   PASS
```

## 9. Residual non-blocking observations (NOT corrected by this integration)

Per explicit instruction, integration does not correct these — they are recorded for a separate post-integration change:

```text
OBS-01
The candidate's own docs/B5_CANDIDATE_REQUIREMENT_TRACEABILITY_v0.md
contains a stale "184/184" evidence-count line, superseded by the
final report's correct 190/190. Documentary inconsistency only, not
a code defect. Independently confirmed: 190/190 is the accurate
count (152+38); 184/184 predates the R7 repair's 6 additional tests.

OBS-02
CaseOutcome.AUTHORITY_REJECTION is defined as a constant in
app/cpl/cases/outcomes.py but is never referenced anywhere in the
implementation — the actual authority-denial mechanism is the
AuthorityDeniedError exception type, entirely outside this enum.
Functionally the five failure categories remain distinguishable
(confirmed: AuthorityDeniedError is never conflated with
IntegrityError/TECHNICAL_FAILURE), and REQ-B5-080's text requires
distinguishability, not a shared representation mechanism — so this
did not block ACCEPT_CANDIDATE. Requires a small design decision in
a follow-up change: remove the dead constant, or align the exception
path to populate it explicitly.
```

Neither observation was corrected in this integration. `main` at `2ac075d` still contains both exactly as accepted.

## 10. Final status

```text
B5_CASE_GOVERNANCE

Accepted candidate:     c60c592 (VERIFIED, ACCEPT_CANDIDATE)
Integration method:     NO-FF MERGE
Integrated SHA:          2ac075daea7d162825ed73ded0c7548011242a8f
main (pushed, verified): 2ac075daea7d162825ed73ded0c7548011242a8f
Post-integration regression: 190/190 PASS
Post-integration health:     PASS

FINAL VERDICT:
  B5_INTEGRATED
```

Integration does not itself close B5. A separate `B5 Closure` artifact is required before the next Build Unit's structuring may be authorized — matching the B4 precedent (`B4_CLOSURE_AND_B5_AUTHORIZATION_v0.md`).
