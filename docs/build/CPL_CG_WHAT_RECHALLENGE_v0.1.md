# CPL — CASE GOVERNANCE
# WHAT RE-CHALLENGE v0.1

```text
Status:
  TARGETED RE-CHALLENGE

Target:
  docs/build/CPL_CG_WHAT_v0.1.md

Canonical target SHA:
  f53fce8f0c79aa3b5f041a964883ab8283671584

Source WHAT:
  docs/build/CPL_NEXT_BUILD_UNIT_WHAT_v0.md
  d3e1a883dcee7b357640159d2cbe85d23ac05755

First challenge:
  docs/build/CPL_CG_WHAT_CHALLENGE_v0.md
  8ec530e18a987fefa34c231e51c7b3261ef3d509

First challenge verdict:
  WHAT_REPAIR_REQUIRED

Repairs under re-challenge:
  REPAIR-01
  REPAIR-02
  REPAIR-03
  REPAIR-04
```

This artifact does NOT authorize B5 designation, WHAT freeze, requirements, architecture, schema modification, migration, implementation, candidate branch, or Execution Governance.

---

## 1. Re-challenge mandate

This is not a fresh unrestricted investigation. Case Governance's identity and the Case/Execution split survived the first challenge and are not reopened here except where the v0.1 repair itself exposes a genuine contradiction.

```text
Repair presence ≠ repair correctness.
Repair correctness ≠ WHAT acceptance.
```

Verified directly against the committed text at `f53fce8`, not against the developer's summary of it.

---

## 2. RC-01 — Execution pointer boundary

**Adversarial test A.** `Case.current_execution_id = E42`, `E42.status = FAILED`. May Case Governance infer "Case failed"?

Text (`§21a`) explicitly prohibits Case Governance from "interpret[ing] RunnerExecution status." Inferring "Case failed" from `E42.status = FAILED` is exactly an act of interpreting RunnerExecution status. **Blocked. Test A passes.**

**Adversarial test B.** `CaseEvent.execution_id = E17`. May Case Governance infer the CaseEvent or underlying domain assertion is valid merely because `E17` exists?

The text's invariant chain (`REFERENCE EXISTS ≠ REFERENCE IS GOVERNED ≠ REFERENCE IS SEMANTICALLY INTERPRETED`) is a three-part chain, not the four-part chain this mandate's own template proposes (`...≠ DOMAIN TRUTH IS ESTABLISHED`). Tested whether this narrower chain still closes the gap: the separate MUST-NOT item "derive domain truth from execution presence or outcome" independently covers exactly this case — existence (`E17` being present) is "presence," and inferring validity from it would be deriving domain truth from that presence. **Blocked, via a different clause than the mandate anticipated, but genuinely closed. Test B passes.**

**Negative sweep** against all eight prohibited behaviors: interpret status (✓ blocked, item 1), interpret lifecycle (✓ covered by item 1's scope), derive Case authority from execution state (✓ blocked, item 2), gate Case transitions on execution semantics (✓ blocked, item 3), determine execution success/failure (✓ blocked, item 1 — success/failure is a status interpretation), interpret `parent_execution_id` (✓ blocked, item 5, explicit), correct/supersede RunnerExecution (✓ blocked, item 6), claim complete execution-history navigation (✓ blocked, item 4), derive domain truth from execution presence/outcome (✓ blocked, item 7). No clause found that reopens any of these.

**Local result:**

```text
REPAIR-01 CLOSED
```

*(Minor observation, non-blocking: the invariant chain in text is 3-part rather than 4-part; substantively closed via the separate MUST-NOT item, but a future revision could make the chain explicit for readability. Not required for this verdict.)*

---

## 3. RC-02 — Build-order justification

Searched `§4` specifically for residual `FK → dependency → build order` reasoning. Not found. The repaired text states the corrected chain (`SCHEMA DEPENDENCY ≠ SEMANTIC ≠ GOVERNANCE ≠ BUILD-ORDER DEPENDENCY`) and re-grounds the ordering in the `current_execution_id`/`CaseEvent.execution_id` boundary established by REPAIR-01, not in the `case_id` FK.

**Counterfactual test.** If `RunnerExecution.case_id` were not physically enforced as a FK, would the governance-boundary dependency still justify the ordering?

Yes — the repaired justification depends on the *existence of execution-reference columns on Case-family objects* (`current_execution_id`, `CaseEvent.execution_id`) requiring a governed boundary before Execution Governance can interpret them. This holds regardless of whether a FK constraint enforces referential integrity; even an unconstrained column pointing at execution identifiers would still require the same boundary discipline. **The repaired reasoning is grounded in semantics, not the database constraint — passes the counterfactual test.**

**Overcorrection test.** Does v0.1 claim schema dependencies are irrelevant? No — the text states "a database FK alone must never again be treated as sufficient evidence," which permits FK as *contributing* evidence while denying it as *sufficient* evidence. This is the correct, non-overcorrected position.

**Local result:**

```text
REPAIR-02 CLOSED
```

---

## 4. RC-03 — Asset anchoring

Verified `§9` states plainly: `Case.asset_id is NOT NULL`, therefore every currently representable Case is Asset-anchored; the prior "Contact / Asset / both" framing has been removed and replaced; `ASSET-OPTIONAL CASE: OUT OF SCOPE FOR THIS BUILD UNIT` is explicit; "Requirements for this Build Unit MUST NOT relax that constraint" is explicit.

**Adversarial test.** A consulting request concerns Contact Alice only, no Asset. Representable as a Case under v0.1?

Text directly states: "a Contact-only Case is not currently representable in the materialized schema." **Matches expected answer (NO).**

**Reverse test.** Does v0.1 incorrectly claim Contact is irrelevant? No — text explicitly states "Contacts may participate in, act within, initiate, or otherwise be associated with the Case through the Case governance model," preserving Contact's role while correctly scoping the Asset requirement.

**Local result:**

```text
REPAIR-03 CLOSED
```

---

## 5. RC-04 — GAP-01 through GAP-04

Testing not whether the gaps are *resolved* (they should not be) but whether each is explicitly visible, correctly bounded, and prevented from leaking accidental semantics.

**GAP-01 (Case consolidation).** Explicitly names the unresolved question. Explicitly states "No Case merge or consolidation semantics are authorized yet" and requires the question be resolved "before requirements may introduce" any of merge, survivor selection, consolidation, or supersession. No accidental authorization found. `SAME UNDERLYING MATTER ≠ SAME CPL CASE` present.

**GAP-02 (CaseEvent classification).** Explicitly names four candidate classes and states "These classes MUST NOT be silently conflated" and "The WHAT does not authorize `CaseEvent.payload` to become an untyped universal truth container." Tested the four example event types (`CASE_OPENED`, `DIAGNOSIS_REPORTED`, `REPAIR_REPORTED_COMPLETE`, `CASE_CLOSED`) against this text: none is pre-classified by the WHAT itself, and the WHAT does not collapse them into one undifferentiated bucket. Correctly exposed without premature resolution.

**GAP-03 (correction/supersession substrate).** Explicitly states current schema lacks this substrate, explicitly states "This is not assumed to be solvable only in service-layer logic," and explicitly disclaims mandating event sourcing, universal supersession, Case merge, or "any specific table shape." Tests both required negatives (no false promise of service-layer sufficiency; no premature mandate of a specific solution) pass.

**GAP-04 (ontology vocabulary).** Explicitly preserves `PHYSICAL TABLE NAME ≠ CANONICAL ONTOLOGY NAME`. Tested: does v0.1 accidentally rename Case already? No — every use of "Case" throughout the document remains the working term, with no alternate name substituted anywhere. Does it accidentally freeze "Case" as canonical merely because the table is named `cases`? No — the section explicitly poses the naming question as open and states "No renaming is authorized yet" without asserting the reverse (that "Case" is definitely NOT final) either. The gap remains genuinely open, not silently decided in either direction.

**Local result:**

```text
REPAIR-04 CLOSED
```

---

## 6. Non-regression

Independently confirmed via diff that the committed `v0.1` text is byte-identical to `v0` outside the eight sections the repair touched (header, §4, §9, §21a, §39a, invariants §40, §43a, §44). Since NR-01 through NR-04 test exclusively sections that were not touched by any repair, they trivially pass by construction — the same text that survived the first challenge is unchanged.

- **NR-01** (`Case ≠ world occurrence/workflow/RunnerExecution/domain truth/generic ticket`) — §6–8, §32–34 untouched. **PASS.**
- **NR-02** (`CaseParticipant ≠ ContactAssetRelationship`, `ROLE ≠ AUTHORITY ≠ PERMISSION ≠ IDENTITY`) — §12–13 untouched. **PASS.**
- **NR-03** (`WORLD EVENT ≠ DOMAIN ASSERTION ≠ CASE EVENT`, `CaseEvent ≠ Canonical Case Decision`, `request ≠ decision ≠ event`) — §15–16, §26–27 untouched. **PASS.**
- **NR-04** (`CASE STATUS ≠ DOMAIN STATE`) — §11 untouched. **PASS.**
- **NR-05** (execution-pointer repair must not imply Execution Governance is unnecessary) — §21a's own text states "without reunifying the two Build Units," and §37 (untouched) still names Execution Governance as the subsequent candidate, "NOT authorized for implementation." **PASS.**

```text
NON-REGRESSION PASS
```

---

## 7. Open-question discipline

```text
GAP-01  OPEN, OUT_OF_SCOPE for merge mechanics specifically
GAP-02  OPEN
GAP-03  OPEN
GAP-04  OPEN
Asset-optional Case  OUT_OF_SCOPE (decided)
```

For each: can requirements be written without inventing semantic policy?

- **GAP-01** — Yes. Case Governance's core requirements (identity, status, participants, events, decision discipline) do not depend on merge being decided; merge is explicitly excluded from this Build Unit's scope, not merely deferred within it.
- **GAP-02** — Yes, on inspection. The *semantic distinction itself* (world/domain/CPL-fact/decision-consequence) is already a frozen WHAT invariant (`CG-CI07`–`CG-CI09`, untouched, surviving from `v0`). What remains open is only the *representation mechanism* for that distinction — a HOW question properly left to requirements, not a WHAT-level gap that would force requirements to invent new semantics.
- **GAP-03** — Yes, on inspection. The *semantic obligation* (correction ≠ deletion, preserve reconstructable history — `CG-CI15`, untouched) is already frozen. Whether new schema is required to satisfy it is a legitimate requirements/HOW decision, directly mirroring how B4's own Requirement Challenge (`RM-B4-01`–`04`) decided new schema was needed without that being treated as a WHAT-level defect.
- **GAP-04** — Yes, on inspection, though this is the closest call of the four. Requirements can pragmatically use "Case" as the working term (matching the physical table name already in use) throughout the Requirement Matrix without that constituting a final semantic commitment — exactly as implementation code commonly uses a working name before a later, purely-cosmetic rename. This does not force requirements to invent WHAT semantics; it only defers a documentation-vocabulary decision.

All four gaps: **NON-BLOCKING.**

---

## 8. Freeze-readiness gate

```text
REPAIR-01 closed:                 YES
REPAIR-02 closed:                 YES
REPAIR-03 closed:                 YES
REPAIR-04 correctly incorporated: YES
NON_REGRESSION:                   PASS
Unresolved FREEZE-BLOCKING gap:   NONE
Case/Execution split coherent:    YES
Build Structure reopening needed: NO
```

All conditions for `WHAT_ACCEPTED` are met.

---

## 9. Final verdict

```text
WHAT_ACCEPTED
```

---

## 10. Output summary

```text
CPL_CG_WHAT_RECHALLENGE_v0.1
================================

TARGET:
  f53fce8f0c79aa3b5f041a964883ab8283671584

REPAIR-01:
  CLOSED

REPAIR-02:
  CLOSED

REPAIR-03:
  CLOSED

REPAIR-04:
  CLOSED

NON-REGRESSION:
  PASS

Case/Execution split:
  PRESERVED

Build Structure:
  PRESERVED

GAP-01:
  NON-BLOCKING

GAP-02:
  NON-BLOCKING

GAP-03:
  NON-BLOCKING

GAP-04:
  NON-BLOCKING

FINAL VERDICT:
  WHAT_ACCEPTED
```

---

## 11. Stop condition

**STOP.**

This re-challenge does not assign B5, does not freeze the WHAT, does not authorize requirements, does not authorize implementation.

`WHAT_ACCEPTED` means the repaired WHAT is **freeze-ready** — the next governance action is WHAT Freeze / Build Unit Admission. Only at that transition may naming move from `CPL_CG_...` to `B5_CASE_GOVERNANCE_...`.
