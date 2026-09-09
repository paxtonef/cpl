# B6_EXECUTION_ARTIFACT_REQUIREMENT_CHALLENGE_v0

## 1. Executive verdict

```text
PRIMARY VERDICT: REQUIREMENTS_REPAIR_REQUIRED
```

The matrix's structure survives adversarial challenge — no requirement was found to reinterpret the frozen
WHAT, collapse `DOMAIN DETERMINES DOMAIN TRUTH`, or contradict B3/B4/B5. But this challenge, working directly
against the committed file rather than trusting the matrix's own self-report, found **12 genuine findings**
(`RC-B6-01`–`12`), three of them `MAJOR`: an unresolved canonical-authority question inside `REQ-B6-057`
itself (the matrix flagged the divergence but didn't finish resolving it), a missing concurrency
requirement in the idempotency contract, and a real authority-collapse contradiction between `REQ-B6-015`
and `REQ-B6-077`. It also found that the matrix's own claim of `19/19` active-invariant coverage was
incorrect — `EA-CI08` and `EA-CI09` are cited by zero requirements. None of the 12 findings rises to
`WHAT_CONFLICT_DISCOVERED` or `GOVERNANCE_CONFLICT_FOUND`; all are bounded, Requirements-level repairs.

---

## 2. Canonical baselines

```text
Governance HEAD:          6cf1892c720473094a4cab25aa0a2be7fcccae05
CPL software baseline:      2ac075daea7d162825ed73ded0c7548011242a8f
Migration head:                026
Frozen WHAT:                      docs/build/CPL_EA_WHAT_v0.1.md @ e7d5184204340840cccd97bf3811de73c756784849
WHAT Re-Challenge:                   docs/build/CPL_EA_WHAT_RECHALLENGE_v0.1.md @ 3eb76f115a9052a2a2861a71180e56f25a571981
Freeze + Admission:                     docs/build/CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0.md @ 3092d7c69e59191fdfc945304fd71d5a8bf0b08d
Requirement Matrix:                        docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.md @ 6cf1892c720473094a4cab25aa0a2be7fcccae05
```

Baseline re-verified via `git ls-remote` against the real GitHub repository immediately before this
challenge; HEAD confirmed at `6cf1892c720473094a4cab25aa0a2be7fcccae05`, matching the matrix's own commit —
this challenge is being run against the actual pushed file, not a local draft.

---

## 3. Challenge methodology

Every claim below was checked directly against the committed file (`grep`/exact re-read of the requirement
text), not recalled from having authored it. Where the matrix made a self-reported statistic (e.g., "19/19
EA-CI coverage," "87/87 traceable"), this challenge recomputed it independently per §48's explicit
instruction not to trust the matrix's summary. Findings are reported only where they meet a concrete,
falsifiable bar — a missing citation, a contradictory pair of requirement statements, an unaddressed
executable constraint, or a genuinely unresolved question the matrix claimed to have closed. Stylistic
preferences are not findings.

---

## 4. Requirement inventory verification

```text
REQUIREMENT_ID_INTEGRITY = PASS
```

Independently re-extracted every `**REQ-B6-NNN**` header from the committed file: 87 headers, IDs 001
through 087, strictly sequential, zero duplicates, zero gaps, zero malformed IDs. Cross-checked the §30
index table's per-section counts against actual header counts per section — they match exactly. No
requirement is cited elsewhere in the document under an ID that doesn't have a corresponding header (spot-
checked all internal cross-references: REQ-B6-004, 009, 016, 025, 033, 057, 061, 076–079, 080 are all
referenced from other requirements and all exist).

---

## 5. Traceability audit

```text
TRACEABILITY = 86/87 VALID
OVERCLAIMS: 1
ORPHANS: 0
```

**Overclaim found — `REQ-B6-082`:** cites `Source: WHAT §36 (this instruction)`. The frozen WHAT
(`CPL_EA_WHAT_v0.1.md`) contains sections 1 through 30 only (confirmed by direct re-read of the full
document); there is no WHAT §36. The parenthetical "(this instruction)" suggests the author meant to cite
§36 of the *Requirements Construction Instruction* that produced this matrix, not a WHAT section — but wrote
it as if it were a WHAT citation. The underlying requirement content (produced-vs-registered distinction) is
legitimately sourced from that instruction's §36; only the label is wrong. This is a citation-hygiene defect,
not a content problem — see `RC-B6-05`.

No orphan requirements found: every one of the 87 traces to at least one of a WHAT section, an `EA-CI`
invariant, a `BS-EA`/`EA-WG`/`EA-WRC` identifier, or an explicitly named executable constraint.

One borderline case examined and **cleared**: `REQ-B6-011`/`REQ-B6-012` (CANCELLED/BLOCKED semantics) cite
`WHAT §23`, whose illustrative list names cancellation but not `BLOCKED` at all. This looked at first like a
possible overclaim, but §23 itself states "exact vocabulary is Requirements-phase, not frozen here" — meaning
the WHAT explicitly delegates vocabulary-filling to Requirements. Resolving `BLOCKED`'s meaning is therefore
a `VALID REQUIREMENTS-LEVEL RESOLUTION` (see §6), not an overclaim; the matrix's own Notes field already
disclosed that `BLOCKED` wasn't in the WHAT's illustrative list, which is the honest behavior this challenge
is checking for.

---

## 6. WHAT-overreach analysis

Every requirement touching an area the WHAT left open was checked against the three-way classification.

| Area | Requirement(s) | Classification |
|---|---|---|
| execution_status exact vocabulary | REQ-B6-008, 011, 012 | VALID REQUIREMENTS-LEVEL RESOLUTION (§23 explicitly delegates) |
| Lifecycle transition table | REQ-B6-009, 010 | VALID REQUIREMENTS-LEVEL RESOLUTION |
| Canonical decision mechanism (object shape) | REQ-B6-061, 076–079 | Correctly deferred to HOW — matrix requires *that* a decision exists, not its shape. VALID |
| artifact classification vocabulary | REQ-B6-027, 028 | VALID — WHAT §11 explicitly permits Requirements to fix minimum vocabulary |
| parent_execution_id semantics | REQ-B6-006, 043–045 | Correctly left ungoverned (negative requirements only). VALID |
| Provenance relation model | REQ-B6-046–049 | VALID — WHAT §15 lists dimensions without fixing mechanism |
| Idempotency semantics | REQ-B6-035–042 | VALID — WHAT §17 explicitly assigns operational contract to Requirements; see §11 below for a gap in *completeness*, not overreach |
| Correction semantics | REQ-B6-063, 064 | VALID — WHAT §16 explicitly leaves mechanism (B) to Requirements/HOW |
| External artifact rules | REQ-B6-053 | VALID — minimal, does not invent a new external-reference ontology |

No `WHAT REINTERPRETATION` found anywhere in the matrix. No `UNSUPPORTED GENERALIZATION` found. This is a
genuinely clean result — the matrix's negative-requirement discipline (§14, §21, §25 of the matrix) held up
under adversarial reading.

---

## 7. Atomicity analysis

```text
ATOMICITY = REPAIR_REQUIRED
```

Two requirements bundle multiple independently verifiable obligations into a single ID:

- **`REQ-B6-008`** — one requirement asserts the semantic mapping for all 7 `execution_status` values
  simultaneously. A verifier could find `CANCELLED`'s mapping correct while `BLOCKED`'s is wrong, but both
  outcomes report against the same ID, obscuring which value failed.
- **`REQ-B6-032`** — same pattern for the 4 `artifact_status` values.

Recommended split: `REQ-B6-008` → one sub-requirement per enum value (7), `REQ-B6-032` → one per value (4).
This is a mechanical split, not a semantic change, and does not affect the requirement count target — see
`RC-B6-09`.

All other requirements were checked and contain exactly one independently verifiable obligation each.

---

## 8. Testability analysis

```text
TESTABILITY = PASS
```

Searched the full text for `appropriate`, `correct(ly)`, `sufficient(ly)`, `meaningful`, `relevant`, `as
needed`, `where applicable`, `supported`, `valid` without accompanying determination criteria. Results:

- `sufficiently` appears once (`REQ-B6-065`), immediately followed by an explicit enumerated list of what
  must be reconstructable — has criteria, not vague.
- `valid` appears only inside the phrase "valid-transition set," each time immediately followed by the
  explicit transition table (`REQ-B6-009`, `034`) — has criteria.
- `supported` appears only inside a direct quotation of WHAT §23's own text ("cancellation, only if
  supported"), not as a requirement's own acceptance criterion.
- `correct` appears only inside negative requirements describing what must NOT be inferred (e.g., "correct,
  accepted, or true") — used to name a prohibited inference, not as an untestable positive criterion.
- `appropriate`, `meaningful`, `relevant`, `as needed`, `where applicable` — zero occurrences.

No `NON_TESTABLE_REQUIREMENT` found.

---

## 9. Authority analysis

```text
AUTHORITY_BOUNDARY = FAIL
```

For each of the four mutation types, requester/reporter/decider/canonical-owner/domain-owner were traced.
Three of the four are clean. The fourth is not:

**Execution admission** (REQ-B6-076): requester = caller; decider = named governed authority evaluation;
canonical owner = CPL. Clean.

**Artifact registration** (REQ-B6-078): producer = runner; decider = governed decision (possibly
lightweight); canonical owner = CPL. Clean.

**Artifact correction/supersession** (REQ-B6-061, 079): decider = governed decision, required before effect.
Clean.

**Execution lifecycle transition — FAILS.** `REQ-B6-077` states: *"Every `execution_status` transition ...
SHALL require a governed decision record ... Transition without a decision record is rejected."* `REQ-B6-015`
states, for the runner-reported case specifically: *"A runner's self-reported completion/failure signal
SHALL be recorded as `execution_status` only ... it SHALL NOT, by itself, constitute a canonical governance
decision requiring separate authority-gated approval — recording the report and governing the representation
transition are the same act at this layer."*

Read together, for a `RUNNING → COMPLETED` or `RUNNING → FAILED` transition: `REQ-B6-077` requires a governed
decision record to exist before the transition is accepted; `REQ-B6-015` says the runner's raw report *is*
that act, with no separate approval step. This is exactly the collapse pattern this challenge was instructed
to treat as blocking: `RUNNER REPORT = CANONICAL DECISION`. As currently worded, an implementer cannot
satisfy both requirements simultaneously without silently picking an interpretation — either they add a
"decision" step so thin it's indistinguishable from just recording the report (satisfying REQ-B6-077's letter
while contradicting REQ-B6-015's stated intent to avoid "over-engineering"), or they skip the decision record
for runner-reported transitions (satisfying REQ-B6-015 while violating REQ-B6-077's explicit rejection rule).
See `RC-B6-03`.

---

## 10. RunnerExecution identity challenge

```text
RUNNEREXECUTION_IDENTITY = PASS
```

All eight stress scenarios tested:

1. Same request repeated (no replay rule) → REQ-B6-001, 004: new identity. Unambiguous.
2. Same payload, new intent → REQ-B6-038's comparison (case_id/asset_id/execution_purpose) → conflict if any
   differ under a shared idempotency key, or simply a new row if no key is shared. Unambiguous.
3. Same idempotency key, same intent → REQ-B6-036: replay, existing row returned. Unambiguous.
4. New key, same payload → REQ-B6-039: new row. Unambiguous.
5. Retry after technical failure → REQ-B6-040: governed identically to any duplicate submission. Unambiguous.
6. Retry after completed execution (same key) → REQ-B6-036 applies identically (no special-casing by prior
   terminal state) — this is itself only implicitly derivable (REQ-B6-036 doesn't explicitly exclude
   terminal-state prior rows), but no requirement contradicts it either. Adequate, not a finding.
7. Duplicate concurrent submission → **not fully resolved at the identity level; resolved (or rather, not
   resolved) at the idempotency-contract level** — see §11 below, `RC-B6-02`.
8. Partial failure during registration → REQ-B6-080/081 (atomicity, no-duplicate-effect). Adequate.

Scenario 7's gap is real but belongs to the idempotency contract, not the identity model itself — the
identity *rules* (REQ-B6-001–006) are internally consistent; what's missing is the *mechanical* concurrency
behavior when two requests race to apply those rules simultaneously. Filed at `RC-B6-02`.

---

## 11. Idempotency / replay / retry challenge

```text
IDEMPOTENCY_CONTRACT = REPAIR_REQUIRED
```

Checked against the required list: key scope (REQ-B6-035, defined, matches the enforced index) — PASS; same
key + same intent (REQ-B6-036) — PASS; same key + different intent (REQ-B6-037, 038) — PASS; replay outcome
fidelity (§12 below) — PASS; retry distinction (REQ-B6-040) — PASS; key-absence behavior (REQ-B6-039) — PASS;
conflict category (REQ-B6-037) — PASS.

**Concurrency behavior — MISSING.** The word "concurren" does not appear anywhere in the committed matrix.
`runner_executions_idempotency_uq` is a database-enforced unique index; when two requests race to submit the
same `(runner_type, idempotency_key)` simultaneously, one insert succeeds and the other hits the constraint
violation at the database layer. REQ-B6-036 describes the *intended* outcome (retrieve the existing row) but
never states what the losing writer's application code must do when it discovers the row didn't exist a
moment ago (per its own pre-check) but does exist now (per the constraint violation it just received). Left
unstated, an implementer has two choices with materially different observable behavior: (a) catch the
violation and re-read the winning row, applying REQ-B6-036/037 against it — the behavior the matrix clearly
intends; or (b) surface the raw database error to the caller — which would make REQ-B6-036's "SHALL retrieve
... rather than error" promise false under concurrent load specifically, the one condition where an
idempotency contract is under the most pressure to hold. This is not a hypothetical edge case; it is the
central reason idempotency keys exist. See `RC-B6-02`.

No contradiction found with the existing unique index's actual semantics (`(runner_type, idempotency_key)`
partial-unique) — REQ-B6-035's scope statement matches it exactly.

---

## 12. Replay outcome fidelity

Checked whether replay is required to recover more than "no duplicate row." `REQ-B6-036` requires retrieval
of the *existing `RunnerExecution`* itself (not a newly constructed equivalent record), which by construction
carries forward its actual identity, its actual current `execution_status`, and its actual produced artifacts
— there is no code path in the matrix that would construct a "similar but distinct" result object instead of
returning the real row. `SAME OPERATION IDENTITY → SAME GOVERNED OUTCOME` is preserved by this mechanism
directly, not merely asserted. No flag.

One narrower question: does a replay of a request whose *original* submission was rejected pre-materialization
(REQ-B6-076's "no row" branch) need to reproduce that same rejection deterministically? Since no
`RunnerExecution` row is created on rejection, no idempotency-key entry is ever persisted for it either (the
partial unique index only covers non-null keys on existing rows) — so a resubmission is indistinguishable from
a first submission and is correctly re-evaluated from scratch by REQ-B6-076. This is consistent, not a gap,
though it is nowhere stated explicitly. Noted, not filed as a finding (too minor to warrant its own RC item;
folded into the general observation that idempotency only engages after successful materialization).

---

## 13. Retry challenge

Confirmed: no requirement defines retry through `parent_execution_id` (verified by direct grep — zero
requirements reference `parent_execution_id` outside §14's own negative-requirement block and REQ-B6-084).
Retry always creates a new `RunnerExecution` by default (REQ-B6-004); it may reuse the prior attempt's
idempotency key, in which case REQ-B6-040 routes it through the standard duplicate-submission contract
(REQ-B6-036/037) rather than automatically creating a new row — meaning "retry" and "new RunnerExecution" are
not perfectly synonymous in all cases, which is correct and intentional (a retry with the *same* key against
a still-non-terminal prior row is legitimately a replay, not a new attempt). No inconsistency found.

---

## 14. parent_execution_id negative-requirement challenge

```text
PARENT_EXECUTION_ID_BOUNDARY = PASS
```

Verified all seven prohibited readings (retry, replay, continuation, delegation, dependency, correction,
derivation) are explicitly named in `REQ-B6-043`. Checked all other 86 requirements for accidental reliance on
`parent_execution_id` semantics — none found; the field is referenced only in §14's own negative requirements
and in `REQ-B6-084`'s ontology-level restatement, both of which treat it as opaque. No contradiction.

---

## 15. RunnerArtifact identity challenge

```text
RUNNERARTIFACT_IDENTITY = PASS
```

All nine stress scenarios checked. Same content/different execution and same execution/multiple equal
payloads both resolve deterministically to distinct identities (REQ-B6-018, no dedup rule exists). Metadata,
content, and classification correction are distinguished (REQ-B6-059). Supersession is deterministic subject
to `RC-B6-01`'s canonical-authority gap (identity itself stays stable per REQ-B6-021; the gap is about status
consistency, not identity). Hash-changed is covered as an integrity-mismatch case (REQ-B6-055), distinct from
identity. Duplicate registration request produces a new artifact deterministically (no dedup rule, consistent
with REQ-B6-018). External reference moved is only lightly touched (REQ-B6-053) but does not produce
non-deterministic identity behavior — it is a completeness gap in scope definition, not an identity-determinism
failure; not filed separately, since RM-B6-01's `artifact_type`/external-reference resolution already covers
adjacent ground.

---

## 16. Artifact classification challenge

```text
ARTIFACT_CLASSIFICATION = REPAIR_REQUIRED
```

The three dimensions remain independent and non-flattening (REQ-B6-026), and no requirement anywhere forces
mutual exclusivity between them — confirmed by re-reading REQ-B6-026–030 directly. However, checked against
§16's specific validation-taxonomy test (invalid value / unsupported value / contradictory combination /
missing required dimension / optional dimension), the matrix has **no requirement stating whether all three
dimensions are mandatory at artifact registration, or distinguishing these five failure/absence modes**.
REQ-B6-054 in an earlier abandoned draft of this matrix addressed exactly this gap (an explicit
`UNCLASSIFIED` state) but that language did not survive into the committed 87-requirement version. This is a
genuine, verifiable omission — not a hypothetical one, since REQ-B6-078 (artifact registration requires a
governed decision) implicitly requires *something* to be checked at registration time, and classification
completeness is a natural candidate for that check, but nothing says so. See `RC-B6-11`.

---

## 17. REJECTED / SUPERSEDED semantics challenge

**`REJECTED`:** `REQ-B6-033` pins this to exactly one of the five candidate meanings the challenge instruction
lists — "registration rejected" for a structural reason (schema/type validation failure at the JSONB
boundary) — and explicitly prohibits all four other readings (semantically invalid content, domain assertion
rejected, lifecycle rejected in a domain sense, authority rejected). This is unambiguous as written. No repair
needed for `REJECTED` itself.

**`SUPERSEDED`:** here the challenge instruction's question set exposes the real gap. `REQ-B6-032` and
`REQ-B6-057` establish that `SUPERSEDED` is "a status value" set on the old artifact in coordination with the
"actual supersession relation" (`supersedes_artifact_id`) on the new artifact — so far, unambiguous, both
mechanisms are named. But asked directly, "which one is canonical if they were ever found to disagree despite
the coordinated-write requirement (e.g., after a bug, a manual DB edit, or an incomplete migration
backfill)?" — the matrix has no answer. `REQ-B6-057`'s "coordinated write" requirement prevents divergence at
write time under normal operation; it does not designate an authority for read-time reconciliation or repair.
This is the substance of `RC-B6-01`, expanded in §16 below.

---

## 18. REQ-B6-057 divergence analysis

```text
REQ-B6-057 = REPAIR_REQUIRED
```

Applying the challenge's own diagnostic questions directly to the requirement as written:

- **Is status derivative from relation?** Not stated. `REQ-B6-057` requires them to be written together but
  does not say one is computed *from* the other.
- **Is relation authoritative?** Not stated.
- **Are both independent?** Explicitly ruled out — the requirement forbids independent writes. But "not
  independently writable" is not the same claim as "one is authoritative for read/repair purposes."
  `Neither field SHALL be settable independently of the other by ordinary application code` constrains
  *write* paths only.
- **Which is canonical?** Unanswered.

Tested the two invalid states the challenge instruction names directly against the requirement text:
`status = SUPERSEDED AND supersedes_artifact_id IS NULL` (on the *referencing* artifact this would be
nonsensical, but the invalid state the WHAT/schema pairing actually produces is on the *referenced* artifact:
`status = SUPERSEDED` with **no other row's** `supersedes_artifact_id` pointing to it) and
`supersedes_artifact_id IS NOT NULL AND status != SUPERSEDED` (on the *referenced* artifact, meaning a
superseding link exists but the old row was never marked). `REQ-B6-057`'s "Failure" field already names both
of these exact scenarios as failure conditions — so the requirement correctly identifies what *not* to allow,
but its normative language only constrains the write path, leaving no requirement for what a consistency
check or read-time repair procedure should treat as ground truth if the constraint is ever found violated
(e.g., by a future migration bug or manual intervention).

This does **not** rise to `WHAT_CONFLICT_DISCOVERED` — nothing here contradicts the WHAT's supersession
semantics; the WHAT only names `supersedes_artifact_id` as substrate (§16) and is silent on `artifact_status`
entirely, so there is no frozen position for a repaired REQ-B6-057 to violate. The fix is a bounded addition:
designate `supersedes_artifact_id` — the relational fact, directly inspectable and already the WHAT-
acknowledged substrate — as canonical, with `artifact_status = SUPERSEDED` as a derived/denormalized
projection that a periodic or on-read consistency check can verify and, if found wrong, repair by recomputing
status from the relation (never the reverse). See `RC-B6-01`.

---

## 19. Artifact status challenge

Re-confirmed `artifact_status` never implies domain validity, diagnostic correctness, VIR/PGDR acceptance,
publication authority, or content integrity anywhere in the matrix — `REQ-B6-031` prohibits the first reading
generally, `REQ-B6-033` specifically closes off the `REJECTED`-as-domain-rejection risk, and integrity is
explicitly handled by a separate mechanism (§17 of the matrix, content hash) that `REQ-B6-055` keeps distinct
from `REJECTED`. `ARTIFACT STATUS ≠ DOMAIN VALIDITY` holds throughout. No flag beyond the `SUPERSEDED`
authority gap already filed at `RC-B6-01`.

---

## 20. Artifact multiplicity analysis

```text
ARTIFACT_MULTIPLICITY = PASS
```

No requirement assumes `COMPLETED EXECUTION → AT LEAST ONE ARTIFACT` or `ONE EXECUTION → ONE FINAL ARTIFACT`
— confirmed by reading every requirement that mentions `COMPLETED` or artifact count (REQ-B6-023, 024, 068).
REQ-B6-068 explicitly guards against the first wrong assumption. No requirement anywhere references a
"the final artifact" (singular, definite) for an execution — always "artifacts" or explicit multiplicity
language. The negative test passes cleanly.

A narrower, positive-completeness observation (not a negative-test failure, so not blocking this dimension's
PASS verdict): REQ-B6-023's zero-artifact case is illustrated only via "technical failure before output"; a
`COMPLETED` execution with zero artifacts by design (e.g., a side-effect-only runner) is not explicitly named
as a permitted scenario, though nothing forbids it either. Filed as a minor completeness item, `RC-B6-08`.

---

## 21. RunnerArtifact-without-execution challenge

Confirmed `RunnerArtifact` cannot exist without an owning `RunnerExecution` — `execution_id NOT NULL` plus FK
(migration 012), restated as a governed requirement at REQ-B6-022. `GENERIC ARTIFACT ≠ RUNNERARTIFACT` is
preserved by construction: nothing in the matrix provides a path for an imported/manual/external document to
become a `RunnerArtifact` row without an execution. No flag.

---

## 22. Provenance challenge

Re-verified `REQ-B6-048` explicitly distinguishes `PRODUCED BY` from `DERIVED FROM`, `USED AS INPUT` from
`SUPERSEDES`, and `REFERENCES` from `PRODUCED BY` — all five relation types named in the challenge instruction
appear and are kept separate. No generic, undifferentiated "relatedTo" field or mechanism exists anywhere in
the matrix. No flag.

---

## 23. VIR → PGDR handoff challenge

```text
HANDOFF_BOUNDARY = PASS
```

Confirmed the matrix requires only identity/provenance guarantees (REQ-B6-050) and explicitly excludes
transformation logic, VIN confidence semantics, diagnostic input meaning, and diagnosis-transformation logic
from B6's scope (REQ-B6-050's "SHALL NOT guarantee... transformation logic," REQ-B6-051's no-direct-coupling
rule). No domain leakage found. `BS-EA-05` is honestly left partially open (REQ-B6-052) rather than falsely
marked resolved — this is correct behavior, not underdefinition in the blocking sense, since `EA-WG-03`
explicitly authorizes this exact deferral.

---

## 24. Content integrity challenge

```text
INTEGRITY_MODEL = PASS
```

Hash mandatory for embedded content (REQ-B6-053) — stated. Externally referenced content may omit hash — 
stated, same requirement. Exact material hashed — stated precisely (`payload` JSONB as persisted, REQ-B6-054)
— no canonical-serialization ambiguity is introduced since the requirement points at the persisted bytes, not
a re-serialization. Mutable external content retaining the same artifact identity — not directly addressed,
but this is a corollary of REQ-B6-053's own external-reference allowance combined with REQ-B6-018's identity-
independent-of-content rule; no contradiction, and external-reference handling generally is already flagged
as underdeveloped via RM-B6-01's adjacent territory, so not filed as a separate item. Mismatch behavior —
explicit and distinguished from `REJECTED` (REQ-B6-055). Algorithm not prescribed beyond acknowledging the
existing nullable pair (correctly left to HOW). No flag.

---

## 25. Correction / history analysis

```text
HISTORY_RECONSTRUCTABILITY = PASS
```

Metadata, content, classification correction, supersession, new-artifact, and domain-correction are
distinguished (REQ-B6-059, 060). No path allows history to be overwritten — supersession is additive
(REQ-B6-058, backed by the existing FK RESTRICT on `supersedes_artifact_id`), and execution correction is
append-only by requirement (REQ-B6-064). `CORRECTION ≠ HISTORY ERASURE` and `SUPERSESSION ≠ DELETION` both
hold. History reconstruction (REQ-B6-065) covers execution identity/lifecycle, produced artifacts, artifact
supersession/correction, and governed provenance, without requiring event sourcing and without requiring
`parent_execution_id` lineage inference. No flag beyond `RC-B6-01`'s canonical-authority gap, which is a
consistency question, not a reconstructability one.

---

## 26. Execution correction challenge

Each named scenario resolved: incorrect runner-version/timestamp metadata → representation correction
(REQ-B6-063 category A/B, via the append-only log at REQ-B6-064); wrong Case/Asset reference → this is NOT
addressed as a correction case anywhere — the matrix has no requirement for correcting a mis-assigned
`case_id`/`asset_id` on a `RunnerExecution`. This is arguably out of scope (a Case/Asset assignment error is
plausibly a data-entry error the requesting layer should have caught before materialization, not a B6
correction concern), but the matrix doesn't say so explicitly either — it's silent rather than deliberately
excluded. Given the low likelihood this is a real operational need (the WHAT's own correction-boundary list,
§16 categories A–C, does not mention Case/Asset reassignment either), this is judged genuinely out of scope
rather than a gap, and is not filed as an RC item. Incorrectly reported execution status → covered by REQ-B6-
063 category B, subject to the `RC-B6-03` authority-collapse question about whether runner-reported status
even requires the same correction gate. Genuine rerun → new `RunnerExecution` (REQ-B6-063 category C),
unambiguous.

---

## 27. Canonical decision model challenge

```text
CANONICAL_DECISION_MODEL = REPAIR_REQUIRED
```

Execution admission, artifact registration, and artifact correction/supersession all require a governed
decision with a coherent, explained rationale (REQ-B6-076, 078, 061/079). Execution lifecycle transition also
formally requires one (REQ-B6-077) — but `REQ-B6-015` undercuts that requirement specifically for
runner-reported transitions, creating exactly the "asymmetric governance without justification" this section
is designed to catch: three of four mutation types get an unambiguous decision gate; the fourth gets a
decision gate on paper (REQ-B6-077) that a sibling requirement (REQ-B6-015) says isn't really a gate at all.
This is the same underlying issue as `RC-B6-03`, viewed from the decision-model-coherence angle rather than
the authority-collapse angle — filed as one finding, not two, since the repair is identical.

---

## 28. Decision/effect failure-injection test

For each of the five failure points (before decision / after decision before effect / after effect before
trace / during replay / concurrent duplicate), the matrix's atomicity section (REQ-B6-080, 081) requires
externally observable consistency and forbids duplicate canonical effects on retry/replay. This adequately
covers points A, B, C, and D for the three unambiguous mutation types. Point E (concurrent duplicate) for the
idempotency-keyed execution-admission case is exactly `RC-B6-02`'s gap — the atomicity requirement says no
duplicate effect may result, but does not itself specify the mechanical recovery path (catch-and-retrieve) for
the concurrent-insert race, leaving a verifier unable to test "no duplicate effect" without first knowing what
the losing writer is supposed to do. No new finding beyond `RC-B6-02` and `RC-B6-03`/`RC-B6-27` (decision-
model coherence).

---

## 29. Failure model challenge

```text
FAILURE_MODEL = REPAIR_REQUIRED
```

Technical failure, structural artifact invalidity, integrity failure, and domain-rejection-exclusion are all
distinguished and non-collapsing (REQ-B6-066–068). However, WHAT §23 explicitly frames the question of
whether B5's five-category discipline (`AUTHORITY_REJECTION`/`SEMANTIC_REJECTION`/`UNRESOLVED`/`CONFLICT`/
`TECHNICAL_FAILURE`) applies unchanged to B6 or needs adaptation as an open **Requirements-phase** question —
not a rhetorical aside, a direct assignment of work to this matrix. `REQ-B6-066`'s category list maps cleanly
onto `AUTHORITY_REJECTION` (no-row case) and `TECHNICAL_FAILURE` (`FAILED`), but never states whether
`SEMANTIC_REJECTION`, `UNRESOLVED`, or `CONFLICT` apply to B6, were deliberately merged into existing
categories, or were deliberately excluded and why. This is a named, WHAT-flagged open question the matrix
simply didn't address — not a hypothetical gap. See `RC-B6-12`.

---

## 30. Negative boundary stress test

```text
NEGATIVE_BOUNDARY_STRENGTH = PASS
```

Checked that each prohibited-scope item in `REQ-B6-083` is backed by a specific, observable-behavior-
constraining requirement elsewhere, not just an assertion: workflow engine / scheduler / orchestration → no
canonical decision object anywhere governs cross-execution sequencing or dependency (confirmed absent);
runner registry / package manager → REQ-B6-075 explicitly limits runner_type/version to provenance only;
generic evidence ontology / generic artifact platform → REQ-B6-018's identity-independence and REQ-B6-026's
fixed three-dimension classification (not an open-ended taxonomy) constrain this; generic state engine →
REQ-B6-009/034's fixed, closed transition tables (not a generic configurable state machine) constrain this;
generic lineage graph → REQ-B6-084 explicitly bars introducing the concept; domain truth engine → §21 of the
matrix (REQ-B6-069–071) constrains this with specific, testable prohibitions; generic agent framework →
nothing in the matrix introduces multi-agent coordination primitives. Each prohibition is load-bearing, not
decorative. PASS confirmed, no repair needed.

---

## 31. B3/B4/B5 regression analysis

No requirement redefines `Contact` identity, authority, initiator, or runner identity (REQ-B6-074 preserves
B3 exclusivity; `CONTACT ≠ AUTHORITY` and `INITIATOR ≠ AUTHORITY` both hold via REQ-B6-014, 022). No
requirement grants B6 authority over physical Asset sameness, Asset merge, Asset survivor selection, Asset
identifiers, or `ContactAssetRelationship` (REQ-B6-073, explicit prohibition list matches B4's boundary
exactly). No requirement reinterprets `Case`, `CaseEvent`, `Case` status, `Case` history, or `Case` execution
references (REQ-B6-072). `CASE ≠ RUNNEREXECUTION`, `CASE EVENT ≠ RUNNERARTIFACT`, `CASE STATUS ≠ EXECUTION
STATUS` all hold. No `GOVERNANCE_CONFLICT_FOUND`.

One traceability-completeness gap surfaced here, not a semantic regression: `EA-CI08` ("Case ≠ Execution") and
`EA-CI09` ("CaseEvent ≠ RunnerArtifact") — both invariants whose natural home is exactly REQ-B6-072 — are
never cited by any requirement in the matrix, despite REQ-B6-072 substantively covering the same ground. See
§29 below and `RC-B6-04`.

---

## 32. Existing B2 substrate analysis

Recomputed the `ALIGNED` / `UNDER-GOVERNED BUT COMPATIBLE` / `REQUIRES REQUIREMENT-LEVEL SEMANTICS` /
`IMPLEMENTATION DIVERGENCE` / `GOVERNANCE CONFLICT` classification for every relevant field, checking whether
the matrix actually performed this classification or merely implied it.

| Field/constraint | Classification | Requirement | Verified in matrix? |
|---|---|---|---|
| execution_id (PK) | ALIGNED | — | Implicit, adequate |
| case_id, asset_id (FK) | ALIGNED | REQ-B6-072, 073 | Yes |
| runner_type, runner_version | ALIGNED | REQ-B6-046, 075 | Yes |
| execution_purpose | UNDER-GOVERNED BUT COMPATIBLE | REQ-B6-038 (used, not deeply defined) | Partially |
| execution_status (7 values) | REQUIRES REQUIREMENT-LEVEL SEMANTICS | REQ-B6-008–012 | Yes |
| parent_execution_id | ALIGNED (opaque) | REQ-B6-043, 044 | Yes |
| `runner_executions_not_self_parent_chk` | ALIGNED | REQ-B6-044 | Yes |
| `runner_executions_time_chk` | **UNCLASSIFIED** | **none** | **No — genuine gap, see RC-B6-06** |
| `runner_executions_completed_at_chk` | ALIGNED | REQ-B6-013 | Yes |
| initiated_by_contact_id | ALIGNED | REQ-B6-014, 021, 074 | Yes |
| idempotency_key | REQUIRES REQUIREMENT-LEVEL SEMANTICS | REQ-B6-035–042 | Yes, minus concurrency (RC-B6-02) |
| `runner_executions_idempotency_uq` | ALIGNED (scope preserved) | REQ-B6-035 | Yes |
| FK RESTRICT (case/asset/parent/initiator) | **UNCLASSIFIED beyond supersedes_artifact_id's** | **none for these four** | **No — see RC-B6-10** |
| artifact_id (PK) | ALIGNED | REQ-B6-018 | Yes |
| execution_id (FK, NOT NULL) | ALIGNED | REQ-B6-022 | Yes |
| artifact_type | REQUIRES REQUIREMENT-LEVEL SEMANTICS, unresolved | REQ-B6-030 | Yes (open, RM-B6-01) |
| `schema_name`, `schema_version` | **UNDER-GOVERNED, no dedicated requirement** | REQ-B6-032 (mentioned only) | **Weak — see RC-B6-07** |
| artifact_status (4 values) | REQUIRES REQUIREMENT-LEVEL SEMANTICS | REQ-B6-031–034 | Yes, minus canonical-authority (RC-B6-01) |
| payload (JSONB) | ALIGNED (opaque) | REQ-B6-018, 033 | Yes |
| hash_algorithm/content_hash pair | ALIGNED | REQ-B6-020, 053–056 | Yes |
| `runner_artifacts_hash_pair_chk` | ALIGNED | REQ-B6-020 | Yes |
| supersedes_artifact_id | REQUIRES REQUIREMENT-LEVEL SEMANTICS | REQ-B6-021, 057–061 | Yes, canonical-authority gap open (RC-B6-01) |
| `runner_artifacts_not_self_superseded_chk` | ALIGNED | REQ-B6-021 | Yes |
| FK RESTRICT (execution_id, supersedes_artifact_id) | ALIGNED | REQ-B6-022, 058 | Yes |

No `GOVERNANCE CONFLICT` classification needed anywhere. Three fields/constraints were found unclassified or
under-addressed where the matrix should have named them (`runner_executions_time_chk`, the three unaddressed
FK RESTRICT behaviors, `schema_name`/`schema_version`) — filed as `RC-B6-06`, `RC-B6-10`, `RC-B6-07`.

---

## 33. RM-B6-01 challenge

```text
RM-B6-01 = NON_BLOCKING
```

Retrieved exactly: *"Whether the existing `artifact_type` free-text column maps to classification dimension
A, is retired, or coexists with a distinct documented purpose is unresolved."* Test: could an implementer or
verifier proceed with the *rest* of the matrix (identity, lifecycle, idempotency, correction, etc.) without
first resolving this? Yes — `artifact_type`'s resolution affects only the classification mechanism (§11 of
the matrix), and REQ-B6-029 already prevents any other requirement from silently depending on `artifact_type`
as a classification proxy in the meantime. Confirmed correctly classified: non-blocking for this Challenge,
legitimately blocking for Freeze (an implementer building the classification mechanism specifically would need
this resolved). Not misclassified.

---

## 34. RM-B6-02 challenge

```text
RM-B6-02 = NON_BLOCKING
```

Retrieved exactly: *"Application-layer code ... was not inspected in this session; it is therefore
unconfirmed whether any existing runner-orchestration or VIR/PGDR-integration code already relies on
`parent_execution_id` for retry/continuation/lineage behavior."* Test: does the matrix's *normative content*
depend on the answer? No — every requirement in §14 is a prohibition on future/ongoing reliance, independent
of whether legacy reliance is later discovered; if found, it becomes a divergence record, not a requirement
rewrite. Confirmed non-blocking for Challenge, correctly flagged as needing a code audit before Freeze (since
Freeze should not certify a requirement set as achievable without knowing whether it already conflicts with
running code). Not misclassified.

---

## 35. RM-B6-03 challenge

```text
RM-B6-03 = NON_BLOCKING
```

Retrieved exactly: *"Whether B4's `ExternalReference` primitive is reused for artifact source-reference
provenance ... or a new reference concept is needed remains an open choice."* Test: same as above — the
matrix's other 84 requirements do not depend on this choice; only REQ-B6-049/050's own promised deliverable
(a `BS-EA-05`-closing mechanism) is gated on it, and REQ-B6-052 already honestly declines to claim `BS-EA-05`
fully closed. Confirmed non-blocking for Challenge, correctly blocking for Freeze. Not misclassified.

---

## 36. EA-CI coverage audit

Recomputed from scratch by grepping every `EA-CI` citation in the committed file, rather than trusting the
matrix's self-reported "19/19."

| Invariant | Citing requirement(s) | Coverage |
|---|---|---|
| EA-CI01 | REQ-B6-001, 068 | FULL |
| EA-CI02 | REQ-B6-007, 067, 068 | FULL |
| EA-CI03 | REQ-B6-007, 009, 015, 067 | FULL |
| EA-CI04 | REQ-B6-016, 031, 033, 069 | FULL |
| EA-CI05 | REQ-B6-026 | FULL |
| EA-CI06 | REQ-B6-018, 019, 021, 056 | FULL |
| EA-CI07 | REQ-B6-024 only | PARTIAL — REQ-B6-023 (the more directly relevant multiplicity requirement) does not cite it |
| **EA-CI08** | **none** | **MISSING — substantively covered by REQ-B6-072 but never cited** |
| **EA-CI09** | **none** | **MISSING — same** |
| EA-CI10 | REQ-B6-014 | FULL |
| EA-CI11 | REQ-B6-031, 048, 056 | FULL |
| EA-CI12 | REQ-B6-062 | FULL |
| EA-CI13 | REQ-B6-015, 016, 060, 069 | FULL |
| EA-CI14 | — (retired, merged into EA-CI03) | FULL by design, correctly not cited independently |
| EA-CI15 | REQ-B6-016, 069 | FULL |
| EA-CI16 | REQ-B6-003, 041 | FULL |
| EA-CI17 | REQ-B6-006, 043 | FULL |
| EA-CI18 | REQ-B6-001, 002, 003, 006, 041 | FULL |
| EA-CI19 | REQ-B6-026 | FULL |

```text
RECOMPUTED ACTIVE EA-CI COVERAGE: 17/19 FULL, 1/19 PARTIAL (EA-CI07), 2/19 MISSING (EA-CI08, EA-CI09)
```

This directly contradicts the matrix's §32 self-report of `19/19`. The matrix's own coverage-statistics
section was not independently re-verified before publication — exactly the failure mode §48 of this challenge
exists to catch. See `RC-B6-04`.

---

## 37. BS-EA coverage audit

| Gap | Frozen disposition | Matrix resolution | Remaining phase | Assessment |
|---|---|---|---|---|
| BS-EA-01 | RESOLVED | REQ-B6-023–025 | Mechanism only | Accurate — matrix does not overclaim semantic resolution beyond what the WHAT already granted |
| BS-EA-02 | REPAIRED, ungoverned | REQ-B6-006, 043–045 | May resurface at WHAT level | Accurate — matrix correctly leaves this open |
| BS-EA-03 | Semantic core resolved, contract open | REQ-B6-035–042 | Closed at Requirements level | Mostly accurate — the matrix's own claim of full closure is slightly optimistic given the concurrency gap (`RC-B6-02`); the *scope/duplicate/conflict/retry* portions are genuinely closed, concurrency is not |
| BS-EA-04 | Partially addressed | REQ-B6-031–034 | Closed for existing 4 values | Accurate, modulo `RC-B6-01`'s SUPERSEDED canonical-authority gap |
| BS-EA-05 | OPEN | REQ-B6-049, 050, 052 | Still open | Accurate — matrix honestly does not claim full closure |
| BS-EA-06 | CLOSED FOR CPL'S WHAT | REQ-B6-050, 051 | Recorded closed | Accurate |

No case found where the matrix claims completion while leaving semantics genuinely open, **except** the
already-noted overstatement embedded in `BS-EA-03`'s closure claim (concurrency).

---

## 38. EA-WG coverage audit

`EA-WG-01` (registry vs. attribute mechanism) — correctly deferred to HOW via RM-B6-01, not silently pulled
into Requirements; the matrix confirms the *need* for a choice (REQ-B6-026) without making it. `EA-WG-02`
(unified vs. separate decision objects) — correctly deferred to HOW throughout §23 of the matrix; every
decision-required requirement (REQ-B6-076–079, 061) states *that* a decision is needed without prescribing
object shape. `EA-WG-03` (ExternalReference reuse) — correctly deferred via RM-B6-03, not silently resolved.
No violation of the "no HOW/DOMAIN INTEGRATION/PRODUCT question may be silently pulled into Requirements" rule
found anywhere.

---

## 39. EA-WRC-01/02 audit

```text
EA-WRC ACCOUNTING = PASS
```

Retrieved both findings directly from `CPL_EA_WHAT_RECHALLENGE_v0.1.md` §17 (re-fetched at its exact commit
for this challenge, not recalled): `EA-WRC-01` (§6a's negation list omits Asset/artifact though the mandate
named them, MINOR, non-blocking, "optional future documentation polish") and `EA-WRC-02` (`idempotency_key ≠
identity` in body prose only, not mirrored as a standalone `EA-CI` bullet, MINOR, non-blocking, same
disposition). Both are handled per their accepted, non-blocking disposition: `EA-WRC-01` closed operationally
by `REQ-B6-002`'s extension of identity-independence to Asset; `EA-WRC-02` closed operationally by
`REQ-B6-041`'s standalone restatement. Neither was silently ignored, neither was over-treated as blocking when
the Re-Challenge itself said it wasn't. PASS confirmed.

---

## 40. Requirement interaction contradictions

Systematically checked the seven named interaction categories:

- **Identity + idempotency:** REQ-B6-004 (default-new-unless-named-rule) and REQ-B6-036 (the one named rule)
  are consistent — REQ-B6-036 *is* the exception REQ-B6-004 anticipates. No contradiction.
- **Status + supersession:** REQ-B6-034's transition table (`VALIDATED → SUPERSEDED` only) is consistent with
  REQ-B6-057's coordinated-write requirement. No contradiction, though `RC-B6-01`'s canonical-authority gap
  sits adjacent to this pair.
- **Correction + immutability:** REQ-B6-062 (no rewriting historical execution) and REQ-B6-063/064 (append-
  only correction permitted) are consistent — correction is additive, not a rewrite. No contradiction.
- **Multiplicity + final artifact:** No requirement assumes a single final artifact; checked in §20. No
  contradiction.
- **Provenance + lineage exclusion:** REQ-B6-046–049 (provenance) never reference `parent_execution_id`;
  REQ-B6-043 excludes lineage inference from that specific field only. No overlap, no contradiction.
- **Decision ordering + failure handling:** REQ-B6-080 (atomicity) and REQ-B6-076–079 (decision-required) are
  consistent for admission, artifact registration, and correction/supersession — but the same pairing exposes
  the `REQ-B6-015`/`REQ-B6-077` contradiction for lifecycle transition specifically. **Genuine contradiction
  pair found:** `REQ-B6-015` × `REQ-B6-077`. Already filed as `RC-B6-03`.
- **Domain authority + artifact classification:** No requirement in §11 of the matrix references domain
  authority at all; no overlap, no contradiction.

**One genuine contradiction pair found: `REQ-B6-015` ↔ `REQ-B6-077`.** No others.

---

## 41. Completeness analysis

Checked the ten named potential-missing classes against the matrix, reporting only where a gap is logically
required by frozen semantics (not speculative):

- **Concurrency** — missing (`RC-B6-02`).
- **Duplicate conflict** — present (REQ-B6-037).
- **Nullability semantics** — mostly present via scattered NOT NULL/nullable statements; no single
  consolidated requirement, but no logical gap found (each nullable field's behavior is covered where it
  matters: idempotency_key at REQ-B6-039, hash pair at REQ-B6-020, initiator at REQ-B6-023).
- **Transition replay** (repeated identical transition request) — present (REQ-B6-010).
- **Supersession consistency** — present but incomplete (`RC-B6-01`).
- **Provenance cardinality** — implicitly fixed by schema (one execution owns N artifacts, enforced via
  singular FK); no logical gap, not filed.
- **Correction authority** — present (REQ-B6-079, cross-referencing REQ-B6-061), modulo the lifecycle-
  transition-specific authority question already filed as `RC-B6-03`.
- **Timestamp ordering** — partially present: `runner_executions_completed_at_chk` is preserved (REQ-B6-013)
  but its sibling `runner_executions_time_chk` (`completed_at >= started_at`) is not (`RC-B6-06`).
- **Stale update behavior** — not addressed; folded into the concurrency gap (`RC-B6-02`), since stale-update
  races and concurrent-insert races share the same missing mechanical-recovery requirement.
- **Partial-failure consistency** — present (REQ-B6-080, 081).

No speculative additions proposed. All flagged items above are already captured in the gap register (§43).

---

## 42. Implementation-neutrality analysis

```text
IMPLEMENTATION_NEUTRALITY = PASS
```

Checked for unnecessary prescription of database technology, SQL structure, exact table shape, ORM mechanism,
service class names, transaction implementation, API protocol, or storage backend. None found. The matrix
references PostgreSQL-specific facts (`runner_executions_idempotency_uq`, the CHECK constraints, the partial
index) only where governance explicitly requires acknowledging an existing enforced constraint — exactly the
exception this test permits — and never prescribes new technology choices. Verification methods reference
"real PostgreSQL" only implicitly (via `INTEGRATION TEST`/`STATIC SCHEMA INSPECTION` against the actual
migrations), consistent with governance's own requirement for real-database verification. PASS.

---

## 43. Challenge gap register

**RC-B6-01** — MAJOR
Description: `REQ-B6-057` requires `artifact_status = SUPERSEDED` and `supersedes_artifact_id` to be written
together but never designates which is canonical for read-time consistency checking or repair.
Affected: REQ-B6-057
Source: WHAT §16 (silent on artifact_status); schema (both fields, migration 012)
Blocking: NOT for Challenge; YES for Freeze
Failure mode: A future data-integrity check or repair procedure has no governance-designated ground truth to
repair toward if the two are ever found inconsistent despite the write-path constraint.
Required repair: Amend REQ-B6-057 to designate `supersedes_artifact_id` as canonical; `artifact_status =
SUPERSEDED` as a derived, verifiable projection; add an explicit consistency-check acceptance test.
Acceptance test: A query joining artifacts on `supersedes_artifact_id` against `artifact_status` finds zero
mismatches, and any found mismatch is repaired by recomputing status from the relation, never the reverse.

**RC-B6-02** — MAJOR
Description: No requirement governs concurrent-insert behavior when two requests race to submit the same
`(runner_type, idempotency_key)`.
Affected: §13 of the matrix (REQ-B6-035–042)
Source: WHAT §17 (BS-EA-03); schema (`runner_executions_idempotency_uq`)
Blocking: NOT for Challenge; YES for Freeze
Failure mode: Implementer either silently swallows the race correctly (matching intent by luck) or surfaces a
raw DB constraint-violation error to the caller, breaking REQ-B6-036's "SHALL retrieve ... rather than error"
guarantee under exactly the load condition idempotency exists to handle.
Required repair: New derived requirement — on unique-constraint violation at insert time, the losing writer
SHALL catch it and re-read the winning row, then apply REQ-B6-036/037's comparison against it.
Acceptance test: Concurrent-submission integration test with identical `(runner_type, idempotency_key,
case_id, asset_id, execution_purpose)` from two simultaneous callers yields exactly one canonical row and both
callers observe REQ-B6-036's retrieval outcome, never a raw error.

**RC-B6-03** — MAJOR
Description: `REQ-B6-015` and `REQ-B6-077` are in direct tension for runner-reported lifecycle transitions —
one says the report recording is the same act as governance, the other requires a separate decision record.
Affected: REQ-B6-015, REQ-B6-077
Source: WHAT §8, §9, §25; EA-CI03, EA-CI13
Blocking: NOT for Challenge; YES for Freeze
Failure mode: Authority collapse (`RUNNER REPORT = CANONICAL DECISION`) if REQ-B6-015's reading is taken
literally; unjustified extra approval gate if REQ-B6-077's reading is taken literally without REQ-B6-015's
carve-out.
Required repair: Rewrite REQ-B6-015 to clarify that the "same act" still constitutes a governed decision — a
lightweight, rule-bound acceptance ("CPL accepts a well-formed runner report as the trigger for a
representation-only transition") that satisfies REQ-B6-077's decision-record requirement automatically and
by-rule, distinct from execution admission's full authority evaluation (REQ-B6-076). This keeps a decision
record for every transition (satisfying REQ-B6-077 literally) while explaining why that record can be
generated automatically for runner-reported transitions without a human/authority approval step (satisfying
REQ-B6-015's original intent).
Acceptance test: Every `execution_status` transition, including runner-reported ones, has a traceable decision
record; a runner-reported transition's decision record is distinguishable in the audit trail from an
admission-type decision (different decision_type or equivalent), confirming it was rule-bound, not manually
approved.

**RC-B6-04** — MODERATE
Description: `EA-CI08` and `EA-CI09` are cited by zero requirements, contradicting the matrix's own "19/19"
coverage claim; substance is present in REQ-B6-072 but the explicit invariant linkage is missing.
Affected: REQ-B6-072
Source: WHAT §28 (EA-CI08, EA-CI09)
Blocking: NOT for Challenge; YES for Freeze
Failure mode: A future auditor trusting the matrix's self-reported coverage statistic would incorrectly
believe both invariants are traced.
Required repair: Add explicit `EA-CI08`/`EA-CI09` citations to REQ-B6-072; add one sentence explicitly stating
`CaseEvent ≠ RunnerArtifact`, since REQ-B6-072 as written addresses `Case`/`RunnerExecution` distinctness but
not `CaseEvent`/`RunnerArtifact` distinctness by name.
Acceptance test: Recomputed EA-CI coverage (per this challenge's §36 method) shows 19/19 FULL with no
requirement's citation found unsupported.

**RC-B6-05** — MINOR
Description: `REQ-B6-082` cites "WHAT §36," but the WHAT contains only §1–30.
Affected: REQ-B6-082
Source: none (citation defect, not a content defect)
Blocking: NOT for Challenge; YES for Freeze (traceability hygiene)
Failure mode: A future auditor attempting to verify this citation against the WHAT would find no such section
and might wrongly conclude the requirement is an orphan.
Required repair: Relabel the source to correctly reference the Requirements Construction Instruction's §36,
not the WHAT.
Acceptance test: Citation resolves to an actual document section.

**RC-B6-06** — MODERATE
Description: `runner_executions_time_chk` (`completed_at >= started_at`) is never classified or referenced.
Affected: REQ-B6-013 (its natural extension point)
Source: schema (migration 011)
Blocking: NOT for Challenge; YES for Freeze
Failure mode: An implementer or auditor has no governance record that this constraint is intentional and must
be preserved, unlike its sibling `runner_executions_completed_at_chk`.
Required repair: Extend REQ-B6-013 (or add a sibling requirement) naming and classifying this constraint
ALIGNED, same pattern as the existing one.
Acceptance test: Constraint is named in the matrix with an explicit preservation requirement and test.

**RC-B6-07** — MODERATE
Description: `schema_name`/`schema_version` (both `NOT NULL`, migration 012) have no dedicated governing
requirement despite being referenced as the basis for `VALIDATED`-status structural checking (REQ-B6-032).
Affected: REQ-B6-032 (dependency), classification requirements generally (§11 of the matrix)
Source: schema (migration 012)
Blocking: NOT for Challenge; YES for Freeze
Failure mode: "Structural validation" (REQ-B6-032's definition of `VALIDATED`) has no requirement defining
what `schema_name`/`schema_version` actually mean or how they're checked, making REQ-B6-032 partially
unverifiable as written.
Required repair: New derived requirement defining `schema_name`/`schema_version` as the declared payload
contract identifier/version pair against which structural validation is performed, and stating how a
`schema_name`/`schema_version` combination is registered as valid/known.
Acceptance test: A `VALIDATED` transition can be objectively tested against a named, versioned schema
definition, not left to implementer discretion.

**RC-B6-08** — MINOR
Description: REQ-B6-023's zero-artifact case names only "technical failure before output"; a `COMPLETED`
execution with zero artifacts by design (side-effect-only runner) is not explicitly named as permitted.
Affected: REQ-B6-023
Source: WHAT §11, §24 (BS-EA-01)
Blocking: NOT for Challenge; YES for Freeze (minor)
Failure mode: An implementer might wrongly treat a completed, artifact-less execution as anomalous rather than
a valid case, since only the failure-path zero-artifact scenario is named.
Required repair: Expand REQ-B6-023's case (a) to explicitly name both technical-failure and side-effect-only/
no-output as valid zero-artifact scenarios, for both non-terminal-failure and COMPLETED terminal states.
Acceptance test: Integration test confirms a COMPLETED execution with zero artifacts is accepted, not flagged.

**RC-B6-09** — MINOR
Description: REQ-B6-008 and REQ-B6-032 each bundle multiple independently verifiable per-enum-value
obligations into a single requirement ID.
Affected: REQ-B6-008, REQ-B6-032
Source: this challenge's own atomicity test (§7)
Blocking: NOT for Challenge; recommended, not mandatory, for Freeze
Failure mode: A verifier cannot report partial pass/fail per enum value under a single ID.
Required repair: Split each into one sub-requirement per enum value (7 + 4 = 11 new IDs replacing 2), or
adopt a lettered-suffix convention (REQ-B6-008a…g) if the sequential-ID discipline should be preserved.
Acceptance test: Each enum value's semantic mapping is independently testable and independently reportable.

**RC-B6-10** — MINOR
Description: FK `ondelete=RESTRICT` behavior on `case_id`, `asset_id`, `initiated_by_contact_id` (migration
011) is never classified, unlike `supersedes_artifact_id`'s RESTRICT (REQ-B6-058).
Affected: none directly — a substrate-classification gap, not tied to one existing requirement
Source: schema (migration 011)
Blocking: NOT for Challenge; YES for Freeze (minor)
Failure mode: No governance record confirms these RESTRICT behaviors are intentional B6-relevant facts (e.g.,
that a Case with executions cannot be deleted while they exist) rather than incidental implementation detail
subject to change.
Required repair: New derived requirement (or extension of REQ-B6-072/073/074) naming and classifying these
three RESTRICT behaviors ALIGNED.
Acceptance test: Attempting to delete a referenced Case/Asset/Contact while a RunnerExecution references it is
confirmed blocked, and this is documented as intentional B6-relevant behavior.

**RC-B6-11** — MODERATE
Description: No requirement states whether all three classification dimensions are mandatory at artifact
registration, nor distinguishes invalid/unsupported/contradictory/missing/optional as failure modes.
Affected: REQ-B6-026 (extension point), §11 of the matrix generally
Source: WHAT §11
Blocking: NOT for Challenge; YES for Freeze
Failure mode: REQ-B6-078 (artifact registration requires a governed decision) has no defined check for
classification completeness/validity to feed that decision.
Required repair: New derived requirement (or acceptance-criterion repair to REQ-B6-026) stating dimension
mandatoriness and the five-way validation-failure taxonomy from this challenge's §16.
Acceptance test: Registration of an artifact with a missing, invalid, unsupported, or self-contradictory
dimension value is deterministically accepted or rejected per an explicit rule, not implementer discretion.

**RC-B6-12** — MODERATE
Description: WHAT §23 explicitly frames adaptation of B5's five-category failure discipline as an open
Requirements-phase question; the matrix's failure-model requirements never state whether `SEMANTIC_REJECTION`,
`UNRESOLVED`, and `CONFLICT` apply to B6.
Affected: REQ-B6-066
Source: WHAT §23
Blocking: NOT for Challenge; YES for Freeze
Failure mode: A named, WHAT-flagged open question is left silently unaddressed rather than explicitly resolved
or explicitly re-deferred with reasoning.
Required repair: Expand REQ-B6-066 (or add a sibling requirement) to explicitly state whether each of the
three unaddressed B5 categories applies to B6, is merged into an existing category, or is deliberately
excluded, with reasoning for each.
Acceptance test: All five of B5's original categories have an explicit B6 disposition on record, not just the
two currently covered.

```text
TOTAL FINDINGS: 12
CRITICAL: 0
MAJOR: 3  (RC-B6-01, RC-B6-02, RC-B6-03)
MODERATE: 6  (RC-B6-04, RC-B6-06, RC-B6-07, RC-B6-11, RC-B6-12, and RC-B6-09 counted as MODERATE-leaning-MINOR)
MINOR: 3  (RC-B6-05, RC-B6-08, RC-B6-10)
```

---

## 44. Required repairs

Per §53's discipline, repairs are instructed here, not performed.

**R-B6-R01** — Affected: REQ-B6-057. Problem: no canonical-authority designation between `artifact_status =
SUPERSEDED` and `supersedes_artifact_id`. Required change: designate the relation canonical, status derived;
add consistency-check acceptance test. Source: RC-B6-01. Count change: none (amends existing requirement).

**R-B6-R02** — Affected: §13 (new). Problem: concurrent-insert race unaddressed. Required change: new
requirement specifying catch-and-retrieve behavior on constraint-violation race. Source: RC-B6-02. Count
change: +1 requirement.

**R-B6-R03** — Affected: REQ-B6-015. Problem: authority-collapse tension with REQ-B6-077. Required change:
rewrite to clarify automatic, rule-bound decision satisfies the decision-record requirement, distinguished
from admission-type decisions in the audit trail. Source: RC-B6-03. Count change: none (amends existing
requirement).

**R-B6-R04** — Affected: REQ-B6-072. Problem: EA-CI08/09 uncited despite substantive coverage. Required
change: add citations, add explicit CaseEvent≠RunnerArtifact sentence. Source: RC-B6-04. Count change: none.

**R-B6-R05** — Affected: REQ-B6-082. Problem: mislabeled source citation. Required change: correct label from
"WHAT §36" to the correct instruction reference. Source: RC-B6-05. Count change: none.

**R-B6-R06** — Affected: REQ-B6-013 (or new sibling). Problem: `runner_executions_time_chk` unclassified.
Required change: name and classify the constraint ALIGNED with a preservation requirement. Source: RC-B6-06.
Count change: +1 requirement (or 0 if folded into REQ-B6-013).

**R-B6-R07** — Affected: §11/§12 (new). Problem: schema_name/schema_version ungoverned. Required change: new
requirement defining the fields and their role in structural validation. Source: RC-B6-07. Count change: +1
requirement.

**R-B6-R08** — Affected: REQ-B6-023. Problem: COMPLETED+zero-artifact case not explicitly named. Required
change: expand case (a) to cover both failure-path and design-path zero-artifact scenarios. Source: RC-B6-08.
Count change: none.

**R-B6-R09** — Affected: REQ-B6-008, REQ-B6-032. Problem: multi-obligation bundling. Required change: split
into per-value sub-requirements. Source: RC-B6-09. Count change: +9 (2 requirements become 11).

**R-B6-R10** — Affected: substrate classification (new). Problem: three FK RESTRICT behaviors unclassified.
Required change: new requirement (or extension) naming and classifying them ALIGNED. Source: RC-B6-10. Count
change: +1 requirement (or 0 if folded into existing REQ-B6-072/073/074).

**R-B6-R11** — Affected: REQ-B6-026 (or new). Problem: classification mandatoriness/validation-taxonomy
undefined. Required change: new requirement or acceptance-criterion expansion. Source: RC-B6-11. Count
change: +1 requirement.

**R-B6-R12** — Affected: REQ-B6-066. Problem: B5's five-category adaptation left unaddressed despite being a
named WHAT-level open question. Required change: expand to explicitly disposition all five categories.
Source: RC-B6-12. Count change: none.

```text
Net requirement-count impact if all repairs applied: +11 to +12 (87 → approximately 98–99), depending on
whether R-B6-R09's split is taken literally and whether R-B6-R06/R10 are folded into existing requirements
or added as new ones. This is a repair-driven count change, not padding.
```

---

## 45. Final verdict

```text
PRIMARY VERDICT: REQUIREMENTS_REPAIR_REQUIRED
```

The matrix is structurally sound: no WHAT reinterpretation, no B3/B4/B5 regression, no governance conflict,
clean testability, clean implementation-neutrality, clean negative-boundary enforcement. The 12 findings are
all bounded, Requirements-level repairs — three of them (`RC-B6-01`, `02`, `03`) substantive enough to block
Freeze on their own, but none indicating the requirements *model* itself is unsound. This is exactly the
outcome a working adversarial challenge should produce against a generally solid first draft: real findings,
proportionate severity, no false rejection.

---

## 46. Freeze readiness

```text
REQUIREMENTS_FREEZE_READINESS = NOT_READY
```

Per §54's rule, Freeze readiness is only returned READY when the primary verdict is REQUIREMENTS_ACCEPTED and
all blocking secondary verdicts pass. Primary verdict here is REQUIREMENTS_REPAIR_REQUIRED, and
`AUTHORITY_BOUNDARY` returned FAIL — both independently sufficient to set NOT_READY.

---

## 47. Recommended next governance action

```text
B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1
(bounded repair of the 12 findings above, followed by a targeted re-challenge of only R-B6-R01 through R-B6-R12,
mirroring the WHAT phase's own repair → targeted re-challenge pattern)
```

---

## B6_EXECUTION_ARTIFACT_REQUIREMENT_CHALLENGE_v0

```text
GOVERNANCE BASELINE:
  6cf1892c720473094a4cab25aa0a2be7fcccae05

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

MIGRATION HEAD:
  026

REQUIREMENT MATRIX:
  REQ-B6-001..087

REQUIREMENT ID INTEGRITY:
  PASS

TRACEABILITY:
  REPAIR_REQUIRED (86/87 valid citations, 1 overclaim/mislabel, 0 orphans)

ATOMICITY:
  REPAIR_REQUIRED

TESTABILITY:
  PASS

AUTHORITY BOUNDARY:
  FAIL

RUNNEREXECUTION IDENTITY:
  PASS

IDEMPOTENCY CONTRACT:
  REPAIR_REQUIRED

parent_execution_id BOUNDARY:
  PASS

RUNNERARTIFACT IDENTITY:
  PASS

ARTIFACT CLASSIFICATION:
  REPAIR_REQUIRED

REQ-B6-057:
  REPAIR_REQUIRED

ARTIFACT MULTIPLICITY:
  PASS

PROVENANCE MODEL:
  PASS

HANDOFF BOUNDARY:
  PASS

INTEGRITY MODEL:
  PASS

HISTORY RECONSTRUCTABILITY:
  PASS

CANONICAL DECISION MODEL:
  REPAIR_REQUIRED

FAILURE MODEL:
  REPAIR_REQUIRED

NEGATIVE BOUNDARY STRENGTH:
  PASS

IMPLEMENTATION NEUTRALITY:
  PASS

RM-B6-01:
  NON_BLOCKING

RM-B6-02:
  NON_BLOCKING

RM-B6-03:
  NON_BLOCKING

EA-WRC ACCOUNTING:
  PASS

NEW CHALLENGE FINDINGS:
  12  (RC-B6-01 through RC-B6-12; 3 MAJOR, 6 MODERATE, 3 MINOR)

PRIMARY VERDICT:
  REQUIREMENTS_REPAIR_REQUIRED

REQUIRED REPAIRS:
  12  (R-B6-R01 through R-B6-R12)

REQUIREMENTS FREEZE READINESS:
  NOT_READY

REQUIREMENTS:
  NOT FROZEN

EXECUTION MANDATE:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

NEXT GOVERNANCE ACTION:
  B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1 (bounded repair of R-B6-R01..R12)
```

## 57. STOP

**STOP.** This artifact does not repair the matrix, does not produce v0.1, does not freeze requirements, does
not create an Execution Mandate or candidate branch, and makes no schema, migration, CPL, VIR, or PGDR code
changes.
