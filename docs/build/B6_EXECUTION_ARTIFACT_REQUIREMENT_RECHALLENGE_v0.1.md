# B6_EXECUTION_ARTIFACT_REQUIREMENT_RECHALLENGE_v0.1

## 1. Executive verdict

```text
PRIMARY VERDICT: REQUIREMENTS_RECHALLENGE_ACCEPTED
```

All twelve repairs (`R-B6-R01`–`R-B6-R12`) were independently traced through both required proof chains —
`RC-B6-xx → R-B6-Rxx → actual v0.1 text → acceptance test → CLOSED`, and `EA-CIxx → actual REQ-B6 requirement
→ genuine normative obligation → testable → FULL` — using documents re-fetched fresh from GitHub at their
exact committed SHAs, not the self-reports embedded in v0.1 or memory of having written it. All twelve close.
`AUTHORITY_BOUNDARY`, `IDEMPOTENCY_CONTRACT`, and `REQ-B6-057` — the three blocking findings from the original
Challenge — are genuinely repaired, not merely reworded. `EA-CI08`/`EA-CI09` are now real, substantively
matched to their exact WHAT text, not label-only. One narrow, repair-introduced testability gap was found and
is recorded (`EA-RRC-B6-01`) — non-blocking, does not fail any acceptance-gate criterion.

---

## 2. Canonical baselines

```text
Governance HEAD:                855f3c7e4a7b70bcc70aeeee09225b264082c0ef
Frozen WHAT:                       docs/build/CPL_EA_WHAT_v0.1.md @ e7d5184204340840cccd97bf3811de73c756784849
Freeze + Admission:                   docs/build/CPL_EA_WHAT_FREEZE_AND_ADMISSION_v0.md @ 3092d7c69e59191fdfc945304fd71d5a8bf0b08d
Original Matrix (v0):                    docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.md @ 6cf1892c720473094a4cab25aa0a2be7fcccae05
Challenge (v0):                             docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_CHALLENGE_v0.md @ 647a91543dc4f72627370c29d111c897662816f9
Repaired Matrix (v0.1):                        docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md @ 855f3c7e4a7b70bcc70aeeee09225b264082c0ef
CPL software baseline (unchanged):                2ac075daea7d162825ed73ded0c7548011242a8f
Migration head (unchanged):                          026
```

Baseline re-verified via `git ls-remote` immediately before this re-challenge; HEAD confirmed at
`855f3c7e4a7b70bcc70aeeee09225b264082c0ef`. All four source documents above, plus the frozen WHAT, were
re-fetched fresh from GitHub at their exact commits for this re-challenge.

---

## 3. Targeted scope

Verified only: the twelve repairs and their downstream effects. Requirements that passed the original
Challenge cleanly and were not touched by any repair (76 of the original 87) were not re-examined for new
issues — confirmed untouched by direct diff against v0, then left alone. `PASS ≠ OPEN FOR REDESIGN` was
honored throughout.

---

## 4. Source-of-truth method

For each `R-B6-Rxx`, the exact repair instruction was re-extracted from the committed Challenge file (not
recalled), then the corresponding `REQ-B6` text was re-extracted from the committed v0.1 file (not recalled),
and the two were compared directly. Where a repair claimed to close a coverage gap (`EA-CI08`/`09`), the exact
invariant text was independently re-fetched from the frozen WHAT and compared word-for-word against the
requirement's normative content, not just its citation label.

---

## 5. Requirement delta verification

```text
REQUIREMENT_DELTA_INTEGRITY = PASS
```

Recomputed independently:

```text
v0 total:                  87 (grep-confirmed against the actual v0 file)
Retired (split):              2  (REQ-B6-008, REQ-B6-032 — both explicitly marked "RETIRED — SPLIT" in v0.1,
                                    original text preserved for traceability, both excluded from the active
                                    index)
New/split-derived:               14  (REQ-B6-008a–g [7], REQ-B6-032a–d [4], REQ-B6-088, REQ-B6-089, REQ-B6-090 [3])
Modified in place:                  9  (REQ-B6-013, 015, 023, 057, 066, 072, 073, 074, 082)
Unchanged:                             76
v0.1 active total:                        99  (87 − 2 retired + 14 new = 99, confirmed by set arithmetic on
                                                the actual extracted ID lists, not by trusting the stated sum)
```

No unintended renumbering found (all untouched IDs retain their v0 numbers). No duplicate identifiers (checked
new/split IDs against the full v0 ID set — zero collisions). No silent deletion (both retired parents remain
fully quoted with an explicit `RETIRED — SPLIT` marker and forward-pointer to their children). Every new ID
traces to exactly one of the twelve repairs (verified in §35 below). No unauthorized requirement found.

---

## 6. R-B6-R01 verification

**Exact Challenge instruction (re-fetched):** *"Affected: REQ-B6-057. Problem: no canonical-authority
designation between `artifact_status = SUPERSEDED` and `supersedes_artifact_id`. Required change: designate
the relation canonical, status derived; add consistency-check acceptance test."*

**Actual v0.1 text (re-fetched):** `REQ-B6-057 (repaired)` now states `supersedes_artifact_id` is designated
**canonical**, `artifact_status = SUPERSEDED` is a **derived, denormalized projection**, with an explicit
if-and-only-if condition, and adds a `CONSISTENCY TEST` verification method (zero-mismatch join query;
mismatch always repaired by recomputing status from relation, never the reverse).

**Match:** exact. The required change (designate relation canonical, status derived, add consistency test) is
present verbatim in substance. No new semantic claim beyond what was authorized — the WHAT's own supersession
semantics (§16) are untouched; only the mechanical coordination between two schema fields is resolved.

```text
R-B6-R01 = CLOSED
```

---

## 7. R-B6-R02 verification

**Exact Challenge instruction:** *"Affected: §13 (new). Problem: concurrent-insert race unaddressed. Required
change: new requirement specifying catch-and-retrieve behavior on constraint-violation race."*

**Actual v0.1 text:** `REQ-B6-088 (new)` requires the losing writer in a concurrent-insert race against
`runner_executions_idempotency_uq` to catch the violation, re-read the winning row, and apply
`REQ-B6-036`/`037`'s comparison against it — explicitly prohibiting a raw error reaching the caller.

**Match:** exact. Confirmed the requirement does not redefine `REQ-B6-035`'s scope or `REQ-B6-036`/`037`'s
comparison logic (checked those three requirements — unchanged from v0), consistent with the repair's own
"does not alter" disclaimer.

```text
R-B6-R02 = CLOSED
```

---

## 8. R-B6-R03 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-015. Problem: authority-collapse tension with
REQ-B6-077. Required change: rewrite to clarify automatic, rule-bound decision satisfies the decision-record
requirement, distinguished from admission-type decisions in the audit trail."*

**Actual v0.1 text:** `REQ-B6-015 (repaired)` now states the runner-report-triggered transition proceeds
through an "automatic, rule-bound governed decision" that explicitly **satisfies** `REQ-B6-077`'s
decision-record requirement, and requires that record to be distinguishable from an admission-type decision
via a distinct `decision_type` marker. `REQ-B6-077` itself was confirmed **unchanged** (re-checked directly —
only referenced, never rewritten, consistent with the repair's affected-requirement scope of `REQ-B6-015`
only).

**Match:** exact. See §18 for the full reconstruction of whether the original contradiction actually
disappears.

```text
R-B6-R03 = CLOSED
```

---

## 9. R-B6-R04 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-072. Problem: EA-CI08/09 uncited despite substantive
coverage. Required change: add citations, add explicit CaseEvent≠RunnerArtifact sentence."*

**Actual v0.1 text:** `REQ-B6-072 (repaired)` now cites `EA-CI08, EA-CI09` in its Source field and adds an
explicit sentence: *"`CaseEvent` and `RunnerArtifact` remain distinct concepts even where one references the
other (EA-CI09)..."*

**Match:** citations present, sentence present, matches the exact required change. See §21–22 for independent
semantic verification against the WHAT's actual invariant text (not just citation-label presence). One
narrow gap found and recorded separately at §34 (`EA-RRC-B6-01`): the requirement's Verification/Acceptance/
Failure fields were not extended to name an explicit test for the new sentence, unlike the parallel treatment
given to `REQ-B6-073`/`074`'s own RESTRICT additions (§15 below). This does not affect whether the citation is
semantically supported — it is a test-method completeness gap, not a coverage failure.

```text
R-B6-R04 = CLOSED (with EA-RRC-B6-01 recorded, non-blocking)
```

---

## 10. R-B6-R05 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-082. Problem: mislabeled source citation. Required change:
correct label from 'WHAT §36' to the correct instruction reference."*

**Actual v0.1 text:** `REQ-B6-082 (repaired)` Source field now reads *"Requirements Construction Instruction
§36 (produced-vs-registered distinction) — corrected from the original mislabeling as 'WHAT §36'; the frozen
WHAT contains no §36."* Independently re-confirmed against the freshly-fetched WHAT: it has sections 1–30
only (verified by direct scan), no §36 exists. Content of the requirement's Statement is byte-identical to v0
— confirmed this was a citation-only defect, not a substantive rewrite.

```text
R-B6-R05 = CLOSED
```

---

## 11. R-B6-R06 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-013 (or new sibling). Problem:
`runner_executions_time_chk` unclassified. Required change: name and classify the constraint ALIGNED with a
preservation requirement."*

**Actual v0.1 text:** `REQ-B6-013 (repaired)` now names `runner_executions_time_chk` explicitly, quotes its
exact condition (`completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at`), classifies it
ALIGNED alongside its sibling constraint, and extends the Verification field with a corresponding integration
test (`completed_at` earlier than `started_at` fails).

**Match:** exact, using the explicitly-permitted "folded into REQ-B6-013" option rather than a new sibling
requirement.

```text
R-B6-R06 = CLOSED
```

---

## 12. R-B6-R07 verification

**Exact Challenge instruction:** *"Affected: §11/§12 (new). Problem: schema_name/schema_version ungoverned.
Required change: new requirement defining the fields and their role in structural validation."*

**Actual v0.1 text:** `REQ-B6-089 (new)` defines `schema_name`/`schema_version` as the declared payload
contract identifier/version pair, requires `VALIDATED` to be reachable only via an objective check against a
registered definition for that pair, and routes an unregistered pair to `REJECTED`.

**Match:** exact. Confirmed the requirement does not prescribe a registration mechanism (explicitly deferred
to HOW in its own Notes), consistent with the repair instruction's implementation-neutrality discipline.

```text
R-B6-R07 = CLOSED
```

---

## 13. R-B6-R08 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-023. Problem: COMPLETED+zero-artifact case not explicitly
named. Required change: expand case (a) to cover both failure-path and design-path zero-artifact scenarios."*

**Actual v0.1 text:** `REQ-B6-023 (repaired)`'s case (a) now explicitly splits into `(a-i)` technical failure
before output and `(a-ii)` a `COMPLETED` execution producing no artifact by design, both stated as valid,
non-anomalous.

**Match:** exact.

```text
R-B6-R08 = CLOSED
```

---

## 14. R-B6-R09 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-008, REQ-B6-032. Problem: multi-obligation bundling.
Required change: split into per-value sub-requirements (7 + 4 = 11 new IDs replacing 2), or adopt a
lettered-suffix convention."*

**Actual v0.1 text:** Both original requirements marked `RETIRED — SPLIT`, full original text preserved
inline for traceability. `REQ-B6-008a`–`g` (7) and `REQ-B6-032a`–`d` (4) created, each with its own Source,
Statement, Verification, Acceptance, and Failure fields — confirmed independently testable (spot-checked:
`REQ-B6-008f`/`008g` correctly point to `REQ-B6-011`/`012` for full CANCELLED/BLOCKED semantics rather than
duplicating them; `REQ-B6-032c` correctly points to the repaired `REQ-B6-057` for `SUPERSEDED`'s canonical-
authority resolution rather than restating it). No two children contradict each other or their siblings; each
covers exactly one enum value with no overlap.

```text
R-B6-R09 = CLOSED
```

---

## 15. R-B6-R10 verification

**Exact Challenge instruction:** *"Affected: substrate classification (new). Problem: three FK RESTRICT
behaviors unclassified. Required change: new requirement (or extension) naming and classifying them ALIGNED."*

**Actual v0.1 text:** All three previously-unclassified `ondelete=RESTRICT` behaviors are now named and
classified ALIGNED: `case_id`'s in `REQ-B6-072` (via §9 above), `asset_id`'s in `REQ-B6-073`, and
`initiated_by_contact_id`'s in `REQ-B6-074` — the latter two each additionally extending their Verification
field with `STATIC SCHEMA INSPECTION (RESTRICT behavior confirmed)`.

**Match:** substantively exact for all three. Confirmed the same minor verification-field asymmetry noted at
§9/§34 — `REQ-B6-072`'s RESTRICT clause did not receive the same explicit test-method extension its two
siblings did — recorded once at `EA-RRC-B6-01`, not double-counted here.

```text
R-B6-R10 = CLOSED (with EA-RRC-B6-01 recorded, non-blocking)
```

---

## 16. R-B6-R11 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-026 (or new). Problem: classification mandatoriness/
validation-taxonomy undefined. Required change: new requirement or acceptance-criterion expansion."* (Count
change fixed at +1 by the Challenge's own note, regardless of the "(or new)" hedge.)

**Actual v0.1 text:** `REQ-B6-090 (new)` — `REQ-B6-026` itself confirmed unchanged (checked directly). Defines
all three dimensions mandatory and states the exact five-outcome taxonomy the Challenge's own §16 named
(invalid / unsupported / contradictory / missing / valid), with an explicit note that "contradictory
combination" is confirmed currently unreachable by design rather than silently unaddressed.

**Match:** exact, implemented as a new requirement per the Challenge's fixed count-change instruction.

```text
R-B6-R11 = CLOSED
```

---

## 17. R-B6-R12 verification

**Exact Challenge instruction:** *"Affected: REQ-B6-066. Problem: B5's five-category adaptation left
unaddressed despite being a named WHAT-level open question. Required change: expand to explicitly disposition
all five categories."*

**Actual v0.1 text:** `REQ-B6-066 (repaired)` now explicitly maps all five of B5's categories
(`AUTHORITY_REJECTION`/`SEMANTIC_REJECTION`/`UNRESOLVED`/`CONFLICT`/`TECHNICAL_FAILURE`) to B6 execution- or
artifact-level equivalents, or explicitly states "no analogue at this time, to be raised through governance if
discovered" rather than leaving any of the five silently undispositioned. Independently re-verified against
WHAT §23's exact text (re-fetched, §29 below) — the mapping accurately reflects the five categories WHAT §23
itself names.

**Match:** exact. One design choice worth noting, not a defect: the repair maps execution-level
`SEMANTIC_REJECTION` onto the same "no row" case as `AUTHORITY_REJECTION`, which somewhat blurs a distinction
B5 itself kept separate (lacking authority vs. having authority but failing a semantic rule). This is a
disclosed, deliberate Requirements-level adaptation choice — WHAT §23 explicitly authorizes adaptation, not
verbatim adoption — and the requirement states its reasoning rather than asserting it silently. Not filed as a
blocking finding; noted for completeness.

```text
R-B6-R12 = CLOSED
```

---

## 18. Authority-boundary verification

```text
AUTHORITY_BOUNDARY = PASS
```

Attempted reconstruction of the original contradiction: previously, `REQ-B6-015` stated the runner-report
recording and the representation-transition governance "are the same act," while `REQ-B6-077` required a
separate decision record and rejected transitions without one — leaving no way for an implementer to satisfy
both without silently collapsing `RUNNER REPORT = CANONICAL DECISION`. Re-reading the repaired text: `REQ-B6-
015` now states the "same act" **is** an automatic, rule-bound decision that **satisfies** `REQ-B6-077`, with
a required audit-trail marker distinguishing it from an admission-type decision. `REQ-B6-077` is unchanged and
still requires a decision record for every transition — the repaired `REQ-B6-015` explains how that
requirement is met for the runner-reported case, rather than exempting it. The contradiction could not be
reconstructed against the current text.

Checked the three required distinctions explicitly:

- `REPORTER ≠ AUTHORITY` — holds; the runner's report triggers a rule-bound acceptance, not an authority
  evaluation. `REQ-B6-016` (unchanged, "CPL representation authority distinct from domain truth authority")
  remains intact and is explicitly cross-referenced by the repaired `REQ-B6-015`.
- `INITIATOR ≠ AUTHORITY` — unaffected by any repair; `REQ-B6-014` (unchanged) still holds this line.
- `CPL REPRESENTATION AUTHORITY ≠ DOMAIN TRUTH AUTHORITY` — the repaired `REQ-B6-015` explicitly states the
  automatic decision "carries no domain-truth weight."

Checked all nine other modified/new requirements (`REQ-B6-013, 023, 057, 066, 072, 073, 074, 082, 088, 089,
090`) for accidental reintroduction of any collapse — none found; none of them touch decision/authority
semantics except `REQ-B6-057` (artifact-side, unrelated to execution-lifecycle authority) and `REQ-B6-066`
(failure taxonomy, which references but does not redefine `REQ-B6-076`'s admission authority).

---

## 19. Idempotency / replay / retry verification

```text
IDEMPOTENCY_CONTRACT = PASS
REPLAY_OUTCOME_FIDELITY = PASS
RETRY_SEMANTICS = PASS
```

Tested all six required scenarios against the actual (unchanged plus one new) requirement set:

- **A. Same key + same governed execution operation** — `REQ-B6-036` (unchanged): retrieves existing row.
  Determinable.
- **B. Same key + incompatible execution intent** — `REQ-B6-037`/`038` (unchanged): explicit conflict
  response, comparison fields named exactly (`case_id`, `asset_id`, `execution_purpose`). Determinable.
- **C. New key + same payload** — `REQ-B6-039` (unchanged): new row, no dedup. Determinable.
- **D. Retry after technical failure** — `REQ-B6-040` (unchanged): governed identically to any duplicate
  submission via the same key. Determinable.
- **E. Concurrent duplicate submissions** — `REQ-B6-088` (new, the repair under test): catch-and-retrieve,
  never a raw error. Determinable — this was the gap and is now closed.
- **F. Replay after successful completion** — `REQ-B6-036` places no exclusion on the prior row's terminal
  state; a replay against a `COMPLETED` row retrieves it identically to any other replay. Determinable, though
  only implicitly (no explicit "including terminal states" clause) — this was already true in v0 and was
  explicitly noted as "adequate, not a finding" by the original Challenge (§12); unaffected by any of the
  twelve repairs, correctly not reopened here.

`SAME OPERATION IDENTITY → SAME GOVERNED OUTCOME` holds: replay retrieves the actual existing row (its real
identity, status, and produced artifacts), not a freshly constructed equivalent — confirmed by `REQ-B6-036`'s
literal wording ("SHALL retrieve the existing `RunnerExecution`"), unaffected by any repair. `IDEMPOTENCY KEY
≠ RUNNEREXECUTION IDENTITY` and `REPLAY ≠ RETRY` both re-confirmed intact — `REQ-B6-003`/`041` (identity
independence) and the distinct handling of scenarios A/B vs. D/E above, all unchanged or newly consistent.

---

## 20. REQ-B6-057 supersession verification

```text
REQ-B6-057 = PASS
```

Attempted to construct all five named contradictory states against the repaired text:

- **A. SUPERSEDED with no governed relation** — Prevented by the if-and-only-if derivation rule and caught by
  the new consistency test (zero-mismatch join query).
- **B. Relation recorded, status semantically incompatible** — Same mechanism; the derivation rule is
  bidirectional (status holds *if and only if* the relation exists), so this state is defined as invalid and
  detectable by the same query.
- **C. Relation points to an invalid target** — Not addressed by `REQ-B6-057` itself, but already structurally
  prevented by the existing `runner_artifacts_supersedes_fk` foreign key (referential integrity), unaffected
  by any repair — this is adequate coverage via existing substrate, not a gap this re-challenge's scope
  authorizes reopening.
- **D. Supersession produces history erasure** — `REQ-B6-058` (unchanged: "Supersession is additive, not
  deletion") still holds; not touched by any repair, still adequate.
- **E. Correction incorrectly treated as supersession** — `REQ-B6-059` (unchanged: distinguishes metadata/
  content correction from supersession) still holds.

A single coherent consistency contract now exists: `supersedes_artifact_id` is canonical; `artifact_status =
SUPERSEDED` is derived; repair direction is always relation → status, never the reverse. No schema design was
demanded by this verification, consistent with the re-challenge's own constraint.

---

## 21. EA-CI08 verification

**Exact WHAT text (re-fetched):** *"EA-CI08 — Case ≠ Execution. A Case may exist independent of any execution
and may span multiple executions (B5, unaffected)."*

**Actual enforcing requirement:** `REQ-B6-072 (repaired)`: *"No requirement in this matrix SHALL alter B5
`Case` semantics"* + Verification: *"REGRESSION TEST (existing B5 test suite unaffected)."*

**Genuine enforcement, or citation-only?** Genuine, but indirect by design: B6 does not restate B5's own
established invariant in its own terms (which would risk B6 claiming ownership of a B5 concept); instead it
makes a *negative*, testable commitment — B6 will not alter B5 Case semantics — enforced by an actual
regression test against B5's existing suite, which already exercises Case-independent-of-execution and
Case-spanning-multiple-executions scenarios. A violation of `EA-CI08` by B6 (e.g., a future implementation
requiring every Case to have an execution) would fail this regression test. This is the correct posture for a
downstream Build Unit relative to an upstream invariant it does not own.

```text
EA-CI08 = FULL
```

---

## 22. EA-CI09 verification

**Exact WHAT text (re-fetched):** *"EA-CI09 — CaseEvent ≠ RunnerArtifact. Case-level append-only history and
execution-produced artifacts are distinct concepts, even where one references the other."*

**Actual enforcing requirement:** `REQ-B6-072 (repaired)`'s added sentence: *"`CaseEvent` and `RunnerArtifact`
remain distinct concepts even where one references the other (EA-CI09): a `CaseEvent` is Case-level append-
only narrative history; a `RunnerArtifact` is an execution-produced object governed by this Build Unit;
neither is a substitute for or equivalent to the other, even when a `CaseEvent` references a `RunnerExecution`
or its artifacts."*

**Genuine enforcement, or citation-only?** Genuine — this is a direct, near-verbatim positive restatement of
the invariant, not a label attached to unrelated text. However, as flagged at §9/§15/§34, the requirement's
Verification/Acceptance/Failure fields were not extended with a dedicated test for this specific claim (they
still read only "REGRESSION TEST (existing B5 test suite unaffected)," which does not specifically exercise
CaseEvent/RunnerArtifact conflation). The semantic content is real and correctly matched to the invariant's
actual wording; the verification-method gap is a testability completeness issue, not a coverage failure —
recorded at `EA-RRC-B6-01`.

```text
EA-CI09 = FULL
```

---

## 23. Full active EA-CI coverage recomputation

Recomputed from the actual v0.1 file by direct extraction of every `EA-CI` citation, not copied from v0.1's
own summary table.

```text
ACTIVE EA-CI COVERAGE = 19/19 FULL
```

| Invariant | Citing requirement(s) in v0.1 | Coverage |
|---|---|---|
| EA-CI01 | REQ-B6-001, 068 | FULL |
| EA-CI02 | REQ-B6-008e, 067, 068 | FULL |
| EA-CI03 | REQ-B6-008d, 009, 015 (repaired), 067 | FULL |
| EA-CI04 | REQ-B6-016, 031, 033, 069 | FULL |
| EA-CI05 | REQ-B6-026 | FULL |
| EA-CI06 | REQ-B6-018, 019, 021, 056 | FULL |
| EA-CI07 | REQ-B6-024 | FULL — unchanged from v0, not touched by any repair, correctly not reopened |
| EA-CI08 | REQ-B6-072 (repaired) | FULL — see §21 |
| EA-CI09 | REQ-B6-072 (repaired) | FULL — see §22 |
| EA-CI10 | REQ-B6-014 | FULL |
| EA-CI11 | REQ-B6-031, 048, 056 | FULL |
| EA-CI12 | REQ-B6-062 | FULL |
| EA-CI13 | REQ-B6-015 (repaired), 016, 060, 069 | FULL |
| EA-CI14 | — (retired, merged into EA-CI03) | FULL by design |
| EA-CI15 | REQ-B6-016, 069 | FULL |
| EA-CI16 | REQ-B6-003, 041 | FULL |
| EA-CI17 | REQ-B6-006, 043 | FULL |
| EA-CI18 | REQ-B6-001, 002, 003, 006, 041 | FULL |
| EA-CI19 | REQ-B6-026 | FULL |

This is independently reconstructed, not copied from `B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md`'s own
§30 table — it matches that table, which is itself evidence the v0.1 self-report was accurate this time
(unlike v0's incorrect "19/19" claim, which this exact method caught previously).

---

## 24. Traceability repair verification

```text
TRACEABILITY_REPAIR = PASS
```

Checked both traceability-labeled repairs (`R-B6-R04`, `R-B6-R05`) for the specific failure mode this
verification exists to catch — a source label added without normative support. `R-B6-R04`'s `EA-CI08`/`09`
citations are backed by real matching text (§21–22). `R-B6-R05`'s corrected citation resolves to an actual
document section (the Requirements Construction Instruction's own §36), confirmed to exist. Neither repair
attached an unrelated or unsupported label.

---

## 25. Split/retired requirement accounting

```text
REQUIREMENT_SPLITS = PASS
RETIRED_REQUIREMENT_ACCOUNTING = PASS
```

Splits (`REQ-B6-008`→`a–g`, `REQ-B6-032`→`a–d`) verified to separate genuinely independent failure modes (one
enum value each), introduce no duplicated semantics (each child covers exactly one value, cross-referencing
rather than repeating fuller definitions where one exists — e.g., `008f`/`008g` point to `011`/`012`), and
create no contradictory child obligations (checked all eleven against each other and against their siblings).

Retired parents: both `REQ-B6-008` and `REQ-B6-032` are explicitly marked `RETIRED — SPLIT`, remain fully
quoted (historically visible), point to their exact replacement ID ranges, are excluded from the active-count
arithmetic (§5), and cannot be mistaken as active — the index at v0.1 §22 marks them `RETIRED` distinctly from
`UNCHANGED`/`MODIFIED`/`NEW`.

---

## 26. Failure semantics check

```text
FAILURE_MODEL = PASS
```

`REQ-B6-066 (repaired)` was checked for collapsed distinctions among all nine categories named in this
re-challenge's scope. Confirmed each of `AUTHORITY_REJECTION`, `SEMANTIC_REJECTION`, `UNRESOLVED`, `CONFLICT`,
`TECHNICAL_FAILURE` maps to a distinct, separately-named B6 concept or is explicitly stated to have no current
analogue (not silently merged). `EXECUTION FAILURE` (`FAILED`), `ARTIFACT STRUCTURAL INVALIDITY` (`REJECTED`,
unchanged `REQ-B6-033`), `INTEGRITY FAILURE` (unchanged `REQ-B6-055`), and `DOMAIN REJECTION` (explicitly
excluded from all vocabularies, unchanged) remain distinguishable as before repair — none of these four were
touched by the repair and none were found collapsed.

---

## 27. parent_execution_id regression check

```text
PARENT_EXECUTION_ID_BOUNDARY = PASS
```

Direct grep of the full v0.1 file found exactly three occurrences of `parent_execution_id`, all three in
meta-commentary (the `RM-B6-02` disposition note and the regression self-check's own negative confirmations)
— none in normative requirement text, none assigning it new meaning. No repair references it as proof of
retry, replay, continuation, delegation, dependency, correction, or derivation.

---

## 28. Artifact-classification regression check

```text
ARTIFACT_CLASSIFICATION_BOUNDARY = PASS
```

`REQ-B6-026` (the requirement establishing the three orthogonal dimensions) confirmed unchanged, byte-for-byte
against v0. `REQ-B6-090` (new) explicitly preserves independence — its only mention of "mutually exclusive" is
to confirm no such combination is currently defined, not to introduce one. No repair forces any two dimensions
into a single flattened value.

---

## 29. History/correction regression check

```text
HISTORY_CORRECTION_BOUNDARY = PASS
```

`CORRECTION ≠ HISTORY ERASURE` — `REQ-B6-058`/`059` unchanged, still hold; `REQ-B6-057`'s repair adds a
consistency-repair direction (relation → status) that is itself additive/corrective, never deletion. `SUPER-
SESSION ≠ DELETION` — unchanged `REQ-B6-058` still holds, plus FK RESTRICT on `supersedes_artifact_id`
unaffected. `EXECUTION REPRESENTATION CORRECTION ≠ NEW HISTORICAL EXECUTION` — `REQ-B6-062`–`065` unchanged,
untouched by any of the twelve repairs. `NEW ATTEMPT → NEW RUNNEREXECUTION` — `REQ-B6-001`–`006` unchanged.

---

## 30. Domain-authority regression check

```text
DOMAIN_AUTHORITY_BOUNDARY = PASS
```

Checked every modified/new requirement against the six named inference risks. None infer domain validity from
execution completion, artifact existence, artifact status, artifact semantic classification, artifact
integrity, or provenance. `REQ-B6-015 (repaired)` explicitly disclaims domain-truth weight. `REQ-B6-066
(repaired)`'s five-category mapping keeps domain rejection explicitly unrepresentable in any B6 vocabulary,
unchanged from v0's discipline. `VIR owns vehicle-identity determination` / `PGDR owns diagnosis` — neither is
referenced by any repair in a way that would grant B6 authority over either; `REQ-B6-073`'s new RESTRICT
clause explicitly reaffirms "override VIR's physical-identity determination authority" remains prohibited
(unchanged text, repair only added the RESTRICT sentence after it).

---

## 31. Prior-governance regression check

```text
PRIOR_GOVERNANCE_REGRESSION = PASS
```

`CONTACT ≠ AUTHORITY` — `REQ-B6-014` unchanged. `CASE ≠ RUNNEREXECUTION` — `REQ-B6-072`'s repair adds
citations and a RESTRICT clause but does not touch this distinction, which remains stated in its unchanged
first paragraph. `CASE EVENT ≠ RUNNERARTIFACT` — now *more* explicitly preserved than in v0 (the added
`EA-CI09` sentence). `CASE STATUS ≠ EXECUTION STATUS` — untouched by any repair; no requirement anywhere
conflates the two. `ASSET IDENTITY ≠ EXECUTION IDENTITY` — `REQ-B6-073`'s repair adds a RESTRICT clause but
its first paragraph (asset_id is a reference only, no merge/survivor/sameness authority) is unchanged. No
`GOVERNANCE_CONFLICT_FOUND`.

---

## 32. RM-B6-01/02/03 check

```text
RM-B6-01 = NON_BLOCKING
RM-B6-02 = NON_BLOCKING
RM-B6-03 = NON_BLOCKING
```

None of the twelve repairs depended on resolving any of the three. `RM-B6-01` (`artifact_type` mapping)
remains open — `R-B6-R09`'s split of `REQ-B6-032` did not touch `artifact_type`. `RM-B6-02` (code audit for
`parent_execution_id` reliance) remains open — no repair performed that audit. `RM-B6-03` (`ExternalReference`
reuse) remains open — `R-B6-R07`'s new `REQ-B6-089` governs `schema_name`/`schema_version`, a different field
entirely, and does not touch provenance referencing. None was silently redefined or promoted to blocking.

---

## 33. Unauthorized-new-requirements check

```text
NEW REQUIREMENTS AUTHORIZED: 14/14
```

Every one of the fourteen new/split-derived IDs traces to exactly one of the twelve repairs: `REQ-B6-088` →
`R-B6-R02`; `REQ-B6-089` → `R-B6-R07`; `REQ-B6-090` → `R-B6-R11`; `REQ-B6-008a`–`g` and `REQ-B6-032a`–`d` →
`R-B6-R09`. No `UNAUTHORIZED_REQUIREMENT_ADDITION` found.

---

## 34. Repair-introduced findings

```text
EA-RRC-B6-01 — MINOR, non-blocking
```

**Issue:** `REQ-B6-072 (repaired)` accumulated two normative additions in this repair round (the `EA-CI08`/
`09` citation + `CaseEvent≠RunnerArtifact` sentence from `R-B6-R04`, and the `case_id` FK-RESTRICT clause from
`R-B6-R10`), but its Verification/Acceptance/Failure fields were left as the original "REGRESSION TEST
(existing B5 test suite unaffected)" — unlike `REQ-B6-073`/`074`, whose parallel RESTRICT additions each
received an explicit `STATIC SCHEMA INSPECTION (RESTRICT behavior confirmed)` verification method.

**Affected requirement:** `REQ-B6-072`.

**Whether it blocks completion of an authorized repair:** No. Both `R-B6-R04` and `R-B6-R10`'s normative
content requirements are satisfied — the citation is semantically supported (§22) and the RESTRICT behavior
is documented in the Statement (§15). This is a test-method completeness gap: an independent verifier could
still derive the appropriate test from the Statement text alone (the obligation is precise enough), but the
Verification field itself doesn't name it explicitly, unlike its siblings.

**Disposition:** Deferred, per §36 of this instruction ("only report issues causally introduced or exposed by
the repair... otherwise defer it to Re-Challenge" — recorded here as required, not silently repaired). Does
not block `REQUIREMENTS_RECHALLENGE_ACCEPTED`; recommended as a trivial follow-up whenever `REQ-B6-072` is
next touched (extend its Verification field to explicitly include `STATIC SCHEMA INSPECTION` for the
`case_id` RESTRICT clause and a dedicated check that `CaseEvent` and `RunnerArtifact` remain structurally
distinct).

No other repair-introduced issue was found across the remaining eleven repairs.

---

## 35. Implementation-derivability verdict

```text
IMPLEMENTATION_DERIVABILITY = PASS
```

For each of the twelve previously-challenged areas, an implementation team can now derive behavior without
inventing policy: canonical authority for supersession (`REQ-B6-057`), concurrent-insert recovery
(`REQ-B6-088`), runner-reported-transition decision handling (`REQ-B6-015`), `EA-CI08`/`09` boundary
preservation (`REQ-B6-072`), the corrected citation carries no implementation weight either way
(`REQ-B6-082`), time-ordering constraint preservation (`REQ-B6-013`), schema validation mechanics
(`REQ-B6-089`), zero-artifact-COMPLETED handling (`REQ-B6-023`), per-value status semantics (`REQ-B6-008a`–`g`,
`032a`–`d`), FK RESTRICT behavior across all three fields (`REQ-B6-072`/`073`/`074`), classification
mandatoriness and validation taxonomy (`REQ-B6-090`), and the five-category failure disposition
(`REQ-B6-066`). `EA-RRC-B6-01`'s gap does not prevent derivability — the normative obligation itself is stated
precisely; only the verification-method label is thin.

---

## 36. Independent-verifiability verdict

```text
INDEPENDENT_VERIFIABILITY = PASS
```

Checked specifically for authority, idempotency, replay, retry, supersession consistency, traceability, and
`EA-CI08`/`09`: every one of these has an explicit, objective test named in the repaired requirements (decision-
record distinguishability tests, concurrent-submission integration tests, the zero-mismatch consistency query,
the recomputed coverage table itself). `EA-RRC-B6-01` is the one place where a verification method is thinner
than its siblings, but — as reasoned above — the underlying obligation remains independently derivable and
testable from the Statement text; it does not defeat verifiability, only its documentation polish.

---

## 37. Acceptance gate

| Criterion | Result |
|---|---|
| R-B6-R01..R12 all CLOSED | YES (12/12) |
| AUTHORITY_BOUNDARY = PASS | YES |
| IDEMPOTENCY_CONTRACT = PASS | YES |
| REPLAY_OUTCOME_FIDELITY = PASS | YES |
| REQ-B6-057 = PASS | YES |
| EA-CI08 = FULL | YES |
| EA-CI09 = FULL | YES |
| ACTIVE EA-CI COVERAGE = 19/19 FULL | YES |
| TRACEABILITY_REPAIR = PASS | YES |
| PARENT_EXECUTION_ID_BOUNDARY = PASS | YES |
| DOMAIN_AUTHORITY_BOUNDARY = PASS | YES |
| PRIOR_GOVERNANCE_REGRESSION = PASS | YES |
| IMPLEMENTATION_DERIVABILITY = PASS | YES |
| INDEPENDENT_VERIFIABILITY = PASS | YES |
| No blocking repair-introduced finding | YES — EA-RRC-B6-01 is explicitly non-blocking |

**All criteria met.**

---

## 38. Final verdict

```text
PRIMARY VERDICT: REQUIREMENTS_RECHALLENGE_ACCEPTED
```

---

## 39. Requirements Freeze readiness

```text
REQUIREMENTS_FREEZE_READINESS = READY
```

This does not itself freeze Requirements — per §40 of this instruction, that remains a separate governance
action.

---

## 40. Recommended next governance action

```text
B6_EXECUTION_ARTIFACT_REQUIREMENTS_FREEZE_v0
```

---

## B6_EXECUTION_ARTIFACT_REQUIREMENT_RECHALLENGE_v0.1

```text
GOVERNANCE BASELINE:
  855f3c7e4a7b70bcc70aeeee09225b264082c0ef

FROZEN WHAT:
  e7d51842043408cccd97bf3811de73c756784849

CPL SOFTWARE BASELINE:
  2ac075daea7d162825ed73ded0c7548011242a8f

MIGRATION HEAD:
  026

REPAIRED MATRIX:
  docs/build/B6_EXECUTION_ARTIFACT_REQUIREMENT_MATRIX_v0.1.md

REPAIRED REQUIREMENTS:
  99

R-B6-R01:
  CLOSED

R-B6-R02:
  CLOSED

R-B6-R03:
  CLOSED

R-B6-R04:
  CLOSED

R-B6-R05:
  CLOSED

R-B6-R06:
  CLOSED

R-B6-R07:
  CLOSED

R-B6-R08:
  CLOSED

R-B6-R09:
  CLOSED

R-B6-R10:
  CLOSED

R-B6-R11:
  CLOSED

R-B6-R12:
  CLOSED

AUTHORITY BOUNDARY:
  PASS

IDEMPOTENCY CONTRACT:
  PASS

REPLAY OUTCOME FIDELITY:
  PASS

RETRY SEMANTICS:
  PASS

REQ-B6-057:
  PASS

EA-CI08:
  FULL

EA-CI09:
  FULL

ACTIVE EA-CI COVERAGE:
  19/19 FULL

TRACEABILITY REPAIR:
  PASS

PARENT_EXECUTION_ID BOUNDARY:
  PASS

DOMAIN AUTHORITY BOUNDARY:
  PASS

PRIOR GOVERNANCE REGRESSION:
  PASS

IMPLEMENTATION DERIVABILITY:
  PASS

INDEPENDENT VERIFIABILITY:
  PASS

REPAIR-INTRODUCED FINDINGS:
  1 (EA-RRC-B6-01, MINOR, non-blocking)

PRIMARY VERDICT:
  REQUIREMENTS_RECHALLENGE_ACCEPTED

REQUIREMENTS FREEZE READINESS:
  READY

REQUIREMENTS:
  NOT YET FROZEN

EXECUTION MANDATE:
  NOT AUTHORIZED

IMPLEMENTATION:
  NOT AUTHORIZED

NEXT GOVERNANCE ACTION:
  B6_EXECUTION_ARTIFACT_REQUIREMENTS_FREEZE_v0
```

## 45. STOP

**STOP.** This artifact does not conduct another full challenge, does not repair v0.1, does not freeze
Requirements, and creates no Execution Mandate, candidate branch, schema change, migration, or CPL/VIR/PGDR
code change.
