# CPL_EA_WHAT_RECHALLENGE_v0.1

## 1. Executive verdict

```text
PRIMARY VERDICT: WHAT_RECHALLENGE_ACCEPTED
WHAT_FREEZE_READINESS: READY
```

All five bounded repairs (`R-EA-W01`–`05`) are verified textually present in the committed `CPL_EA_WHAT_v0.1.md`, each closing the exact defect the WHAT Challenge identified, with concrete evidence re-confirmed against the actual document text (not merely trusted from the repair's own claims). Two minor, non-blocking observations were found during this pass — neither warrants another repair cycle. No regression into B3/B4/B5, no domain-authority leakage, no unit-cohesion change. `REQUIREMENTS_READINESS = READY`.

---

## 2. Canonical baselines

```text
Governance HEAD:                 e7d51842043408cccd97bf3811de73c756784849
CPL software baseline:             2ac075daea7d162825ed73ded0c7548011242a8f
Migration head:                     026

Original WHAT:        3a775a5f2b589dd7e526733bcff3c65edf84f4b9
WHAT Challenge:         ed1d18099a5e6cb09758522e739f4178eec62c27
Repaired WHAT (v0.1):    e7d51842043408cccd97bf3811de73c756784849
```

---

## 3. Re-challenge scope

Verified only `R-EA-W01`–`05` and regression effects. No unconstrained ontology review performed; no speculative improvement introduced or suggested as required.

---

## 4. R-EA-W01 verification (Execution identity)

Confirmed present in `§6a` of the committed text: `RunnerExecution` identity is explicitly stated as "the identity of that execution occurrence/instance — nothing else," with the required negations present verbatim — `SAME REQUEST/INPUT/CASE/RUNNER TYPE/DOMAIN INTENT ≠ SAME RUNNEREXECUTION`. `REPLAY RETRIEVAL OF EXISTING EXECUTION ≠ NEW EXECUTION ATTEMPT` present. The exact phrase `NEW EXECUTION ATTEMPT → NEW RUNNEREXECUTION` (arrow notation) confirmed present, though located in `§16` rather than `§6a` — both sections work together, which is acceptable since the mandate did not require single-section placement.

**One non-blocking observation:** the mandate's own test list asked the identity criterion to distinguish `RunnerExecution` identity from "Asset" and "artifact" specifically, alongside request/input/Case/runner-type/domain-operation. `§6a`'s explicit negation list covers five of these but omits Asset and artifact by name. This is not practically ambiguous (nothing in the document or schema suggests Asset or artifact identity could be confused with execution identity), but it is a literal gap against the mandate's test list.

```text
R-EA-W01 = CLOSED
```

---

## 5. R-EA-W02 verification (Artifact classification)

Confirmed present in `§11`: three explicit, named dimensions (Semantic function; Production/lifecycle role; Consumption/presentation role), each with its own example list, explicitly stated to coexist without contradiction. The mandate's own example combination (`DOMAIN DETERMINATION CARRIER + FINAL + PRODUCT-DISPLAYABLE`) appears verbatim as a worked example grounded in PGDR's real `GaragePreparationReport`. The three required non-equivalence statements (`SEMANTIC FUNCTION ≠ LIFECYCLE POSITION`, `≠ PRESENTATION ROLE`, `LIFECYCLE POSITION ≠ PRESENTATION ROLE`) are present verbatim. A full-document search confirmed no other section reintroduces the old flat, mutually-exclusive list — the phrase pattern (`technical artifact / intermediate / final / product-display` as one flat run) appears exactly zero times outside the now-restructured `§11`.

```text
R-EA-W02 = CLOSED
```

---

## 6. R-EA-W03 verification (History / parent_execution_id)

Confirmed present in `§16`: history reconstructability is explicitly narrowed to `RunnerExecution` identity, lifecycle transitions, produced artifacts, artifact correction/supersession, and *explicit governed provenance relations* — "execution attempts where conceptually distinct" (the original tension-causing phrase) has been removed and replaced with reasoning naming the WHAT Challenge finding (`EA-WC-04`) directly. `EXECUTION HISTORY ≠ EXECUTION LINEAGE GRAPH` present verbatim. `§18` confirmed to state `parent_execution_id` remains `EXISTING SUBSTRATE` + `SEMANTICALLY UNGOVERNED BY CPL_EA v0.1`, with the full seven-item prohibition list present verbatim: retry, replay, continuation, delegation, dependency, correction, derivation — all seven, none omitted.

```text
R-EA-W03 = CLOSED
```

---

## 7. R-EA-W04 verification (Idempotency)

Confirmed present in `§17`: `runner_executions_idempotency_uq` cited by exact name, with the precise scope stated (`(runner_type, idempotency_key) WHERE idempotency_key IS NOT NULL`). **Independently re-verified against the actual migration** (`migrations/versions/011_create_runner_executions.py`, re-checked out fresh this pass, not merely trusted from the WHAT's own citation) — the index genuinely exists exactly as described: `unique=True`, columns `["runner_type", "idempotency_key"]`, partial `WHERE idempotency_key IS NOT NULL`. `IMPLEMENTATION FACT ≠ FROZEN SEMANTIC MEANING` present verbatim. All three required non-equivalences present verbatim: `IDEMPOTENCY KEY ≠ RUNNEREXECUTION IDENTITY / INPUT IDENTITY / DOMAIN OPERATION IDENTITY`. Requirements-deferred items (scope, duplicate behavior, retrieval, conflict, retry interaction) all explicitly named as open for Requirements without requiring `RunnerExecution` ontology to be reinvented.

```text
R-EA-W04 = CLOSED
```

---

## 8. R-EA-W05 verification (Execution correction)

Confirmed present in `§16`: the asymmetry between `RunnerArtifact` (has `supersedes_artifact_id`) and `RunnerExecution` (has no equivalent) is named explicitly, not left implicit. `HISTORICAL EXECUTION OCCURRENCE ≠ MUTABLE DOMAIN FACT` and `CORRECTION OF EXECUTION REPRESENTATION ≠ REWRITING EXECUTION HISTORY` both present verbatim. The four-item conceptual permission list (A–D) present, including explicit domain separation: `CORRECTING EXECUTION REPRESENTATION ≠ CORRECTING VIR DETERMINATION` and `≠ CORRECTING PGDR DIAGNOSIS`, both present verbatim. No generic `RunnerExecution` supersession model was invented — the mandate's own prohibition is respected.

```text
R-EA-W05 = CLOSED
```

---

## 9. Invariant repair verification

19 invariant identifiers confirmed present (`EA-CI01`–`19`). `EA-CI14` confirmed explicitly retired, not silently deleted — its retirement text names the merge target (`EA-CI03`) and the reason (narrower restatement of the same rule). No identifier gap found.

Testing the seven required protections (§8 of the mandate) individually against the actual invariant text:

```text
1. RunnerExecution identity ≠ request/input/domain-op identity  — EA-CI18, PRESENT
2. New execution attempt → new RunnerExecution                    — EA-CI18, PRESENT
3. Artifact semantic function ≠ lifecycle role ≠ presentation role — EA-CI19, PRESENT
4. Execution history ≠ generic execution lineage                    — EA-CI17, PRESENT
5. parent_execution_id existence ≠ known semantic relation           — EA-CI17, PRESENT
6. Idempotency key ≠ RunnerExecution identity                          — NOT PRESENT
   as a standalone invariant-level statement in EA-CI16 or EA-CI18;
   the semantic content exists in body prose (§17) but is not
   reflected as its own invariant bullet.
7. Correction of execution representation ≠ rewriting historical
   occurrence                                                            — EA-CI12, PRESENT
```

**One non-blocking observation:** protection #6 is genuinely satisfied in the document's substantive text (`§17`'s `IDEMPOTENCY KEY ≠ RUNNEREXECUTION IDENTITY` line) but is not mirrored as a standalone bullet within the invariant registry itself (`EA-CI16` discusses the schema-field/constraint distinction generally; `EA-CI18` discusses execution identity without naming idempotency specifically). This is a documentation-completeness gap in the registry's cross-referencing, not a substantive gap in the WHAT's actual semantic content.

```text
INVARIANT_REPAIR = PASS
```

(Not `REPAIR_REQUIRED` — the underlying semantic protection exists and is enforceable; only its representation as a dedicated invariant bullet is missing, which does not block Requirements from proceeding since the governing text in `§17` is unambiguous on its own.)

---

## 10. BS-EA-01→06 regression check

All six findings confirmed present in the updated `§26` table with the full required seven-column structure (original concern, v0 treatment, challenge finding, v0.1 treatment, current status, next phase, freeze-blocking). No finding renamed, deleted, or silently upgraded to resolved without evidence — `BS-EA-01`'s upgrade to `RESOLVED` is legitimate (the Build Structure Challenge itself, not this repair, established the 0:N multiplicity finding with direct evidence). `BS-EA-04`/`05`/`06` correctly remain `CORRECTLY_DEFERRED`/`OPEN`/`CLOSED FOR CPL'S WHAT` respectively, unchanged, since none of the five repairs targeted them.

```text
BS-EA-01..06 ACCOUNTING = PASS
```

---

## 11. EA-WG gap regression check

All three questions confirmed retained. `EA-WG-01` correctly updated to note the dimension-mixing entanglement is resolved by `R-EA-W02` while the mechanism-choice question itself remains explicitly open — not silently converted into an assumption. `EA-WG-02`/`03` confirmed unchanged, correctly outside this repair's scope.

```text
EA-WG GAP ACCOUNTING = PASS
```

---

## 12. Implementation/WHAT consistency check

```text
runner_executions_idempotency_uq   — IMPLEMENTATION FACT ACKNOWLEDGED (§17, independently
                                       re-verified against the actual migration this pass)
RunnerExecution schema (other fields) — ALIGNED (unaffected by any repair)
RunnerArtifact schema                  — ALIGNED (unaffected by any repair)
parent_execution_id                     — UNDER-GOVERNED BUT COMPATIBLE (unchanged
                                       disposition, now more precisely bounded)
artifact_status                          — UNDER-GOVERNED BUT COMPATIBLE (unchanged,
                                       not targeted by this repair cycle)
supersedes_artifact_id                    — ALIGNED (unaffected)
```

No new divergence found; the one divergence this repair cycle existed to close (`idempotency_key`) is now acknowledged rather than contradicted.

---

## 13. Prior-governance regression check

Direct diff confirms `§20`/`§21`/`§22` (Case boundary, Asset boundary, Identity/initiator boundary) are **byte-unchanged** by any of the five repairs — none of `R-EA-W01`–`05` touched these sections. `CASE ≠ RUNNEREXECUTION`, `CASE EVENT ≠ RUNNERARTIFACT`, `CASE STATUS ≠ EXECUTION STATUS`, `EXECUTION REFERENCES ASSET ≠ EXECUTION OWNS ASSET IDENTITY`, `INITIATOR ≠ AUTHORITY` all remain exactly as originally stated.

```text
No GOVERNANCE_CONFLICT_FOUND.
```

---

## 14. Domain-authority regression check

`§9`, `§12`, `§13` (runner/domain authority, VIR artifact boundary, PGDR artifact boundary) confirmed unchanged by diff. VIR retains vehicle-identity determination authority; PGDR retains diagnostic authority — both stated identically to `v0`. The repaired sections (`§11` classification, `§17` idempotency) were specifically checked for any new domain-authority claim: none found — classification remains a CPL-representation concern (`ARTIFACT TYPE STRING ≠ DOMAIN AUTHORITY` preserved verbatim in `§11`); idempotency remains an execution-operation concern, never elevated to domain-operation semantics (`IDEMPOTENCY KEY ≠ DOMAIN OPERATION IDENTITY` explicit in `§17`).

```text
DOMAIN_AUTHORITY_BOUNDARY = PASS
```

---

## 15. Requirements-readiness verdict

Re-evaluating the five specific issues that previously caused `REPAIR_REQUIRED`:

```text
RunnerExecution identity           — now stated explicitly (§6a); READY
Artifact classification dimensions   — now stated explicitly, three dimensions (§11); READY
Execution history vs. lineage semantics — now narrowed and disambiguated (§16/§18); READY
Minimum idempotency meaning            — now acknowledged with frozen minimum
                                       interpretation (§17); READY
Execution correction semantics           — now named explicitly including the
                                       asymmetry (§16); READY
```

```text
REQUIREMENTS_READINESS = READY
```

---

## 16. CPL stop-condition check

No concrete contradictory evidence was produced by any of the five repairs. `POST_EA_COMMON_BLOCKER` and `CPL_MINIMUM_FOR_VIR_PGDR_REACHED` remain as previously established.

```text
POST_EA_COMMON_BLOCKER = NONE
CPL_MINIMUM_FOR_VIR_PGDR_REACHED = YES_AFTER_THIS_UNIT
```

---

## 17. New findings

```text
EA-WRC-01
Affected repair: R-EA-W01
Problem: §6a's explicit identity-negation list omits Asset and
  artifact, though the mandate's test list named them.
Evidence: CPL_EA_WHAT_v0.1.md §6a
Severity: MINOR
Blocking: NO
Required disposition: optional future documentation polish; not a
  substantive gap since no confusion risk was found anywhere in the
  document or schema between execution identity and Asset/artifact
  identity.

EA-WRC-02
Affected repair: R-EA-W04 (interacts with invariant registry)
Problem: "IDEMPOTENCY KEY ≠ RUNNEREXECUTION IDENTITY" is stated in
  body prose (§17) but not mirrored as a standalone invariant bullet
  in the EA-CI registry.
Evidence: CPL_EA_WHAT_v0.1.md §17 vs. EA-CI16/EA-CI18
Severity: MINOR
Blocking: NO
Required disposition: optional future documentation polish; the
  underlying semantic protection is unambiguous in the governing
  text regardless of registry cross-referencing.
```

Neither finding blocks acceptance; both are documentation-completeness notes, not semantic gaps requiring another repair cycle.

---

## 18. Final verdict

```text
PRIMARY VERDICT: WHAT_RECHALLENGE_ACCEPTED
```

All five required repairs are closed. No repair introduced a blocking regression. Requirements readiness is `READY`. The WHAT may proceed to the separate Freeze + Admission governance action.

---

## 19. Freeze readiness

```text
WHAT_FREEZE_READINESS = READY
```

This does not itself freeze or admit the Build Unit.

---

## 20. Recommended next governance action

```text
CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0

This is the moment "CPL_EA" formally becomes "B6" — a separate,
distinct governance action from this re-challenge, which only
establishes readiness.
```

---

## FINAL SUMMARY

```text
CPL_EA_WHAT_RECHALLENGE_v0.1
============================

GOVERNANCE BASELINE:
  e7d51842043408cccd97bf3811de73c756784849

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

R-EA-W01:
  CLOSED

R-EA-W02:
  CLOSED

R-EA-W03:
  CLOSED

R-EA-W04:
  CLOSED

R-EA-W05:
  CLOSED

INVARIANT REPAIR:
  PASS

BS-EA-01..06 ACCOUNTING:
  PASS

EA-WG GAP ACCOUNTING:
  PASS

DOMAIN AUTHORITY BOUNDARY:
  PASS

UNIT COHESION:
  PASS

REQUIREMENTS READINESS:
  READY

POST-EA COMMON BLOCKER:
  NONE

CPL_MINIMUM_FOR_VIR_PGDR_REACHED:
  YES_AFTER_THIS_UNIT

NEW RE-CHALLENGE FINDINGS:
  2 (EA-WRC-01, EA-WRC-02 — both minor, non-blocking)

PRIMARY VERDICT:
  WHAT_RECHALLENGE_ACCEPTED

WHAT FREEZE READINESS:
  READY

BUILD UNIT:
  NOT ADMITTED

B6:
  NOT ASSIGNED

REQUIREMENTS:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

NEXT GOVERNANCE ACTION:
  CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0
```

**STOP.** No additional WHAT repair performed, no WHAT freeze, no Build Unit admission, no B6 assignment, no requirements, no Execution Mandate, no CPL code/schema modification, no migrations, no VIR/PGDR modification.
