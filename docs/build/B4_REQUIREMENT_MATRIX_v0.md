# CPL — B4 Requirement Matrix v0

**System:** Common Product Layer — CPL
**Phase:** B4 — Assets + Relationships
**Artifact:** Requirement Matrix
**Version:** v0
**Status:** PRODUCED — PROPOSED FOR REQUIREMENT CHALLENGE
**Canonical baseline:** `main @ bfb3d16`
**Frozen source:** `B4_WHAT_GLOBAL_FREEZE_RE_CHALLENGE_v0.1.md`
**B4 WHAT status:** FROZEN
**Implementation authorization:** NONE

---

## 1. Purpose

This matrix converts the frozen B4 WHAT into atomic, testable, implementation-legible requirements.

It MUST preserve the frozen distinctions among:

```text
Asset
AssetIdentifier
AssetIdentityResolution
CanonicalAssetIdentityDecision
ExternalReference
DomainProjection
ContactAssetRelationship
CanonicalRelationshipDecision
```

and MUST NOT reopen:

```text
physical identity authority
canonical identity authority
merge semantics
survivor semantics
historical continuity
relationship identity
valid-time / decision-time
domain/CPL authority boundary
authorization boundary
```

---

# 2. Requirement families

The B4 requirements are grouped into:

```text
F01  Asset identity and continuity
F02  Asset creation
F03  AssetIdentifier lifecycle
F04  AssetIdentityResolution
F05  CanonicalAssetIdentityDecision
F06  Asset merge admission and execution
F07  Asset correction
F08  Survivor selection
F09  Dependency disposition
F10  ExternalReference
F11  DomainProjection
F12  ContactAssetRelationship identity
F13  Relationship authority and admission
F14  CanonicalRelationshipDecision
F15  Relationship temporal semantics
F16  Endpoint evolution
F17  Relationship idempotency
F18  Cardinality / compatibility / conflict
F19  Outcome and failure semantics
F20  Provenance and historical reconstruction
F21  Domain/CPL authority boundaries
F22  Cross-B3 compatibility
F23  Non-regression
F24  Verification and evidence
```

---

# 3. F01 — Asset identity and continuity

### REQ-B4-001

The system MUST represent an Asset as a persistent CPL identity distinct from the physical object it represents.

### REQ-B4-002

Every canonical Asset MUST possess a stable CPL `asset_id` or semantically equivalent internal identity.

### REQ-B4-003

An Asset MUST NOT derive its canonical identity solely from an external identifier.

### REQ-B4-004

A change to an AssetIdentifier MUST NOT, by itself, create a new Asset.

### REQ-B4-005

Removal, invalidation, replacement, or supersession of an AssetIdentifier MUST NOT, by itself, invalidate the Asset.

### REQ-B4-006

The system MUST preserve continuity of an Asset across mutable identifier changes where no authoritative physical-identity discontinuity has been established.

### REQ-B4-007

The system MUST support multiple candidate Asset representations existing simultaneously where physical identity remains unresolved.

### REQ-B4-008

AMBIGUOUS, CONTRADICTORY, UNRESOLVED, or failed identity resolution MUST NOT force canonical Asset convergence.

---

# 4. F02 — Asset creation

### REQ-B4-009

Asset resolution returning NOT_FOUND MUST NOT automatically create a new Asset.

### REQ-B4-010

Asset creation MUST require a separate governed creation admission.

### REQ-B4-011

Asset creation MUST preserve provenance sufficient to determine why and under which authority the Asset was created.

### REQ-B4-012

Repeated execution of the same governed Asset-creation request MUST NOT unintentionally create duplicate Assets.

### REQ-B4-013

Asset-creation idempotency MUST be based on governed request identity or equivalent execution identity, not merely similarity of supplied evidence.

### REQ-B4-014

A domain resolver MAY establish that no existing Asset has been resolved, but MUST NOT thereby acquire automatic canonical Asset-creation authority.

---

# 5. F03 — AssetIdentifier lifecycle

### REQ-B4-015

The system MUST support attaching multiple AssetIdentifiers to one Asset.

### REQ-B4-016

An AssetIdentifier MUST retain an identifier type or semantic classification sufficient for governed interpretation.

### REQ-B4-017

An AssetIdentifier MUST retain provenance sufficient to identify its source or authority context where applicable.

### REQ-B4-018

The system MUST support an identifier being current/applicable without assuming permanence.

### REQ-B4-019

The system MUST support identifier supersession.

### REQ-B4-020

The system MUST support identifier invalidation.

### REQ-B4-021

The system MUST preserve historically applicable identifiers after replacement or invalidation.

### REQ-B4-022

Identifier equality MUST NOT independently establish SAME_PHYSICAL_ASSET.

### REQ-B4-023

A strong identifier match MUST be treated as identity evidence or a resolution hypothesis unless applicable domain authority has established stronger semantics.

### REQ-B4-024

Conflicting identifier evidence MUST NOT be silently resolved by deletion or arbitrary reassignment.

---

# 6. F04 — AssetIdentityResolution

### REQ-B4-025

The system MUST support a governed AssetIdentityResolution semantic object or equivalent durable representation.

### REQ-B4-026

AssetIdentityResolution MUST remain distinct from CanonicalAssetIdentityDecision.

### REQ-B4-027

The system MUST support resolution semantics equivalent to SAME_PHYSICAL_ASSET.

### REQ-B4-028

The system MUST support resolution semantics equivalent to NOT_SAME_PHYSICAL_ASSET.

### REQ-B4-029

The system MUST support AMBIGUOUS physical identity.

### REQ-B4-030

The system MUST support CONTRADICTORY physical identity evidence/determination.

### REQ-B4-031

The system MUST support UNRESOLVED physical identity.

### REQ-B4-032

Technical resolver failure MUST remain distinguishable from legitimate UNRESOLVED or AMBIGUOUS domain outcomes.

### REQ-B4-033

A resolution MUST retain provenance identifying the authority/source that produced the physical-identity determination.

### REQ-B4-034

A later resolution MAY supersede an earlier resolution without erasing the earlier resolution from historical reconstruction.

### REQ-B4-035

Generic CPL MUST NOT manufacture domain physical-identity truth from record similarity.

### REQ-B4-036

For automotive Assets, VIR authority over automotive physical-identity resolution MUST remain preservable and enforceable.

---

# 7. F05 — CanonicalAssetIdentityDecision

### REQ-B4-037

Every material mutation of current canonical Asset identity MUST be attributable to a durable CanonicalAssetIdentityDecision or semantically equivalent governed representation.

### REQ-B4-038

A CanonicalAssetIdentityDecision MUST have stable decision identity.

### REQ-B4-039

A CanonicalAssetIdentityDecision MUST identify the affected Asset identities.

### REQ-B4-040

A CanonicalAssetIdentityDecision MUST identify the supporting AssetIdentityResolution or equivalent admissible determination context.

### REQ-B4-041

A CanonicalAssetIdentityDecision MUST preserve decision authority/provenance.

### REQ-B4-042

A CanonicalAssetIdentityDecision MUST preserve decision time.

### REQ-B4-043

A CanonicalAssetIdentityDecision MUST preserve the resulting canonical effect.

### REQ-B4-044

A later canonical decision MUST be able to supersede the current effect of an earlier decision.

### REQ-B4-045

Supersession MUST NOT erase the historical existence of the superseded decision.

### REQ-B4-046

Unstructured runtime logging alone MUST NOT satisfy the durable canonical decision requirement.

---

# 8. F06 — Asset merge admission and execution

### REQ-B4-047

A positive physical-identity determination MUST be necessary for canonical Asset merge.

### REQ-B4-048

A positive physical-identity determination MUST NOT be sufficient by itself to force merge.

### REQ-B4-049

Canonical Asset merge MUST pass a distinct CPL merge-admission step or semantically equivalent governed admission.

### REQ-B4-050

Merge admission MUST be able to return HOLD where canonical execution is not yet safe.

### REQ-B4-051

AMBIGUOUS identity MUST prohibit merge.

### REQ-B4-052

CONTRADICTORY identity MUST prohibit merge unless the contradiction has been governedly resolved by applicable authority.

### REQ-B4-053

UNRESOLVED identity MUST prohibit merge.

### REQ-B4-054

Technical failure MUST prohibit treating physical identity as positively established.

### REQ-B4-055

Identifier equality alone MUST NOT cause merge.

### REQ-B4-056

Human/admin privilege alone MUST NOT bypass merge admission.

### REQ-B4-057

A domain resolver MUST NOT directly execute canonical CPL Asset merge.

### REQ-B4-058

Canonical merge execution MUST be attributable to CPL canonical authority.

### REQ-B4-059

Canonical merge MUST preserve the losing Asset as historically reconstructable.

### REQ-B4-060

Canonical merge MUST NOT physically delete the losing Asset solely because it is no longer the current canonical representation.

---

# 9. F07 — Asset correction

### REQ-B4-061

The system MUST support governed correction of a previously accepted canonical Asset merge.

### REQ-B4-062

Asset correction MUST be based on a later admissible identity determination or equivalent authoritative basis.

### REQ-B4-063

Correction MUST create a new CanonicalAssetIdentityDecision or equivalent durable decision.

### REQ-B4-064

Correction MUST supersede the current canonical effect of the erroneous prior decision.

### REQ-B4-065

Correction MUST NOT erase the prior merge decision.

### REQ-B4-066

Correction MUST NOT erase the prior supporting resolution.

### REQ-B4-067

Correction MUST preserve historical evidence supporting the former governed state.

### REQ-B4-068

Where corrected physical identity requires separation, the system MUST be capable of restoring independent current canonical Asset representations.

### REQ-B4-069

Correction MUST NOT represent the historical merge as though it never occurred.

---

# 10. F08 — Survivor selection

### REQ-B4-070

Canonical Asset merge MUST identify a surviving current canonical Asset.

### REQ-B4-071

Where an already-governing canonical successor/survivor exists, that Asset MUST be the default survivor.

### REQ-B4-072

Where no existing governing survivor exists, an established canonical CPL Asset MUST take precedence over a later duplicate representation by default.

### REQ-B4-073

The default survivor MAY be overridden only where it is canonically inadmissible or an explicit governed CPL continuity rule requires another survivor.

### REQ-B4-074

Any survivor-selection override MUST preserve its reason in the CanonicalAssetIdentityDecision or equivalent governed provenance.

### REQ-B4-075

Survivor selection MUST NOT be based solely on UUID order, database insertion order, primary-key value, code convenience, or equivalent implementation artifact.

### REQ-B4-076

A domain identity resolver MUST NOT automatically acquire CPL survivor-selection authority.

### REQ-B4-077

If the governed survivor cannot yet be determined, canonical merge MUST be capable of remaining on HOLD.

---

# 11. F09 — Dependency disposition

### REQ-B4-078

Asset identity convergence MUST NOT automatically cause semantic convergence of dependent records.

### REQ-B4-079

Merge admission MUST evaluate dependency disposition sufficiently to determine whether canonical execution is safe.

### REQ-B4-080

The system MUST support semantic dependency dispositions equivalent to PRESERVE.

### REQ-B4-081

The system MUST support semantic dependency dispositions equivalent to REASSOCIATE_CURRENT where separately authorized.

### REQ-B4-082

The system MUST support SUPERSEDE where applicable.

### REQ-B4-083

The system MUST support RECONCILE where applicable.

### REQ-B4-084

The system MUST support HOLD for unresolved dependency treatment.

### REQ-B4-085

The system MUST support rejection due to unresolved structural conflict where applicable.

### REQ-B4-086

Historical dependency attribution MUST NOT be silently rewritten merely because current canonical Asset navigation changes.

---

# 12. F10 — ExternalReference

### REQ-B4-087

ExternalReference MUST remain semantically distinct from AssetIdentifier.

### REQ-B4-088

ExternalReference MUST preserve the external system/context to which it belongs.

### REQ-B4-089

ExternalReference MUST preserve the external identity/reference value or equivalent reference identity.

### REQ-B4-090

ExternalReference MUST preserve its historical CPL target.

### REQ-B4-091

An ExternalReference MUST NOT independently establish physical Asset identity.

### REQ-B4-092

An ExternalReference MUST NOT independently authorize Asset merge.

### REQ-B4-093

The system MUST support ExternalReference supersession or invalidation where applicable without erasing historical provenance.

### REQ-B4-094

After Asset merge, current navigation MAY resolve an ExternalReference through the canonical successor while preserving the historical target originally referenced by the external system.

### REQ-B4-095

External-system rebinding MUST remain distinguishable from CPL canonical navigation.

---

# 13. F11 — DomainProjection

### REQ-B4-096

A DomainProjection MUST remain semantically distinct from canonical Asset identity.

### REQ-B4-097

A DomainProjection MUST reference or otherwise be bound to a canonical/historical Asset identity.

### REQ-B4-098

A DomainProjection MUST NOT become a parallel canonical Asset identity.

### REQ-B4-099

The system MUST preserve provenance sufficient to identify the domain authority responsible for projection truth where applicable.

### REQ-B4-100

The system MUST support DomainProjection update/supersession while preserving required history.

### REQ-B4-101

Conflicting DomainProjections MUST NOT be arbitrarily resolved by generic CPL.

### REQ-B4-102

DomainProjection conflict MAY cause Asset merge admission to HOLD where canonical execution would otherwise become unsafe.

### REQ-B4-103

Applicable domain authority MUST retain authority over substantive projection reconciliation.

---

# 14. F12 — ContactAssetRelationship identity

### REQ-B4-104

ContactAssetRelationship MUST be treated as a first-class governed CPL object.

### REQ-B4-105

A ContactAssetRelationship MUST possess stable logical identity or semantically equivalent durable continuity.

### REQ-B4-106

Relationship logical identity MUST NOT be defined solely by the current canonical Contact, current canonical Asset, and relationship type.

### REQ-B4-107

Relationship logical identity MUST survive Contact canonical merge/correction.

### REQ-B4-108

Relationship logical identity MUST survive Asset canonical merge/correction.

### REQ-B4-109

Relationship status change MUST NOT itself create a new logical relationship unless governed semantics explicitly require it.

### REQ-B4-110

Historical Contact and Asset endpoints under which the relationship was established MUST remain reconstructable.

---

# 15. F13 — Relationship authority and admission

### REQ-B4-111

Relationship evidence MUST remain distinct from relationship authority.

### REQ-B4-112

Authenticated Contact identity MUST NOT automatically validate a ContactAssetRelationship claim.

### REQ-B4-113

Self-asserted relationship evidence MUST be admissible only where applicable policy permits it.

### REQ-B4-114

Relationship admission MUST evaluate applicable evidence and authority context.

### REQ-B4-115

The system MUST support relationship admission outcomes that do not force canonical establishment.

### REQ-B4-116

Generic CPL MUST NOT invent domain-specific relationship truth where the relationship semantic authority belongs to a domain.

### REQ-B4-117

Relationship-type semantics MUST retain identifiable semantic authority/namespace context or equivalent ownership metadata.

### REQ-B4-118

Arbitrary free-text relationship labels MUST NOT acquire canonical semantic authority without governed type semantics.

### REQ-B4-119

Domain adapters MAY supply governed relationship semantics/evidence but MUST NOT silently bypass CPL canonical relationship admission.

---

# 16. F14 — CanonicalRelationshipDecision

### REQ-B4-120

Every material canonical relationship mutation MUST be attributable to a durable CanonicalRelationshipDecision or semantically equivalent governed representation.

### REQ-B4-121

A CanonicalRelationshipDecision MUST have durable decision identity.

### REQ-B4-122

A CanonicalRelationshipDecision MUST identify the affected ContactAssetRelationship.

### REQ-B4-123

A CanonicalRelationshipDecision MUST preserve relationship semantic type/context.

### REQ-B4-124

A CanonicalRelationshipDecision MUST preserve supporting evidence or provenance references.

### REQ-B4-125

A CanonicalRelationshipDecision MUST preserve applicable authority/admission context.

### REQ-B4-126

A CanonicalRelationshipDecision MUST preserve decision time.

### REQ-B4-127

A CanonicalRelationshipDecision MUST preserve its valid-time effect where applicable.

### REQ-B4-128

A CanonicalRelationshipDecision MUST support supersession linkage or semantically equivalent decision-history continuity.

### REQ-B4-129

The system MUST distinguish relationship decisions equivalent to ESTABLISH.

### REQ-B4-130

The system MUST distinguish relationship decisions equivalent to END.

### REQ-B4-131

The system MUST distinguish relationship decisions equivalent to CORRECT.

### REQ-B4-132

The system MUST distinguish relationship decisions equivalent to SUPERSEDE.

---

# 17. F15 — Relationship temporal semantics

### REQ-B4-133

The system MUST distinguish relationship valid time from CPL decision time where retroactive establishment or correction is possible.

### REQ-B4-134

A relationship MAY become canonically established after its valid-from time.

### REQ-B4-135

A later decision MAY correct a previously represented valid-time interval.

### REQ-B4-136

Correction of valid time MUST NOT erase the earlier decision-time history.

### REQ-B4-137

END MUST remain semantically distinct from CORRECT.

### REQ-B4-138

CORRECT MUST remain semantically distinct from SUPERSEDE.

### REQ-B4-139

Ending a relationship MUST preserve the historical period during which it was considered valid.

### REQ-B4-140

A relationship later proven never valid MUST NOT be represented merely as though it ended at discovery time.

### REQ-B4-141

The WHAT requirement to preserve valid-time/decision-time semantics MUST NOT require a specific bitemporal database architecture.

---

# 18. F16 — Endpoint evolution

### REQ-B4-142

Contact canonical evolution MUST NOT silently rewrite historical ContactAssetRelationship Contact endpoints.

### REQ-B4-143

Asset canonical evolution MUST NOT silently rewrite historical ContactAssetRelationship Asset endpoints.

### REQ-B4-144

Current relationship navigation MAY resolve through current canonical Contact successors.

### REQ-B4-145

Current relationship navigation MAY resolve through current canonical Asset successors.

### REQ-B4-146

Current canonical navigation MUST remain distinguishable from historical endpoint attribution.

### REQ-B4-147

If endpoint canonical correction occurs, current relationship navigation MUST be capable of following the corrected topology without recreating relationship history from scratch.

### REQ-B4-148

Endpoint evolution alone MUST NOT semantically establish, end, correct, or supersede a ContactAssetRelationship.

### REQ-B4-149

Any true semantic relationship mutation triggered by endpoint evolution MUST require a separate governed CanonicalRelationshipDecision.

---

# 19. F17 — Relationship idempotency

### REQ-B4-150

Repeated execution of the same governed relationship-establishment operation MUST NOT create duplicate logical establishment state.

### REQ-B4-151

Relationship-establishment idempotency MUST use governed request/operation identity or semantically equivalent stable execution identity.

### REQ-B4-152

Same Contact, same Asset, and same relationship type MUST NOT alone define idempotent equivalence.

### REQ-B4-153

Two relationships with identical current endpoints/type but different governed establishment events MAY remain distinct.

### REQ-B4-154

Different valid-time periods MUST NOT automatically collapse into one relationship merely because endpoints and type match.

---

# 20. F18 — Cardinality / compatibility / conflict

### REQ-B4-155

Generic CPL MUST NOT impose one universal cardinality rule for all ContactAssetRelationship types.

### REQ-B4-156

Relationship cardinality MUST be governed by applicable type/domain semantics.

### REQ-B4-157

Relationship coexistence compatibility MUST be governed by applicable type/domain semantics.

### REQ-B4-158

Multiple simultaneous same-type relationships MUST NOT automatically be treated as contradictory.

### REQ-B4-159

Where applicable semantics establish exclusivity, incompatible simultaneous relationships MUST be representable as conflicting/contradictory.

### REQ-B4-160

Relationship evidence conflict MUST NOT be resolved by generic recency, confidence, insertion order, or developer preference unless applicable authority policy explicitly authorizes such precedence.

### REQ-B4-161

Unresolved relationship contradiction MUST permit governed non-resolution rather than forced mutation.

---

# 21. F19 — Outcome and failure semantics

### REQ-B4-162

B4 MUST distinguish successful domain determinations from technical execution success/failure.

### REQ-B4-163

B4 MUST distinguish governed non-resolution from technical failure.

### REQ-B4-164

B4 MUST support semantic outcome equivalent to NOT_FOUND where appropriate.

### REQ-B4-165

B4 MUST support semantic outcome equivalent to AMBIGUOUS where appropriate.

### REQ-B4-166

B4 MUST support semantic outcome equivalent to CONTRADICTORY where appropriate.

### REQ-B4-167

B4 MUST support semantic outcome equivalent to UNRESOLVED where appropriate.

### REQ-B4-168

B4 MUST support semantic outcome equivalent to HOLD where canonical mutation cannot safely proceed.

### REQ-B4-169

B4 MUST support governed rejection outcomes such as INVALID, UNAUTHORIZED, or REJECTED where applicable.

### REQ-B4-170

Database/network/internal execution failure MUST NOT be silently represented as NOT_FOUND, AMBIGUOUS, CONTRADICTORY, or UNRESOLVED.

### REQ-B4-171

A successful resolver call returning AMBIGUOUS MUST remain distinguishable from a failed resolver call.

---

# 22. F20 — Provenance and historical reconstruction

### REQ-B4-172

The system MUST preserve sufficient provenance to reconstruct why the current canonical Asset representation exists.

### REQ-B4-173

The system MUST preserve sufficient provenance to reconstruct why the current canonical relationship interpretation exists.

### REQ-B4-174

The system MUST preserve superseded AssetIdentityResolutions.

### REQ-B4-175

The system MUST preserve superseded CanonicalAssetIdentityDecisions.

### REQ-B4-176

The system MUST preserve superseded CanonicalRelationshipDecisions.

### REQ-B4-177

The system MUST preserve historically relevant AssetIdentifier attribution.

### REQ-B4-178

The system MUST preserve historically relevant ExternalReference targets.

### REQ-B4-179

The system MUST preserve historically relevant relationship endpoints.

### REQ-B4-180

A later correction MUST NOT erase historical evidence merely because that evidence is no longer accepted as establishing current truth.

### REQ-B4-181

Current canonical navigation and historical attribution MUST be jointly reconstructable.

---

# 23. F21 — Domain/CPL authority boundaries

### REQ-B4-182

Generic CPL MAY request domain physical-identity resolution.

### REQ-B4-183

Generic CPL MAY consume domain physical-identity resolution.

### REQ-B4-184

Generic CPL MAY persist AssetIdentityResolution results.

### REQ-B4-185

Generic CPL MAY evaluate whether a domain identity determination is admissible for canonical action.

### REQ-B4-186

Generic CPL MUST NOT implicitly acquire the authority that produces domain physical-identity determinations.

### REQ-B4-187

For automotive, VIR MUST remain able to act as automotive physical-identity resolution authority without acquiring CPL canonical mutation authority.

### REQ-B4-188

A domain resolver result MUST NOT bypass CPL merge admission.

### REQ-B4-189

A domain resolver MUST NOT directly select the CPL survivor unless an explicit CPL continuity policy separately authorizes that input.

### REQ-B4-190

Domain Projection truth MUST remain owned by applicable domain authority.

### REQ-B4-191

Relationship semantic truth MAY remain domain-owned while CPL governs canonical relationship continuity.

### REQ-B4-192

Generic CPL MUST NOT invent resolver precedence where domain authority policy has not established it.

---

# 24. F22 — Cross-B3 compatibility

### REQ-B4-193

B4 MUST remain compatible with B3 canonical Contact merge semantics.

### REQ-B4-194

B4 MUST remain compatible with B3 Contact correction semantics.

### REQ-B4-195

B4 MUST preserve historical Contact endpoint identity after Contact canonical merge.

### REQ-B4-196

B4 current relationship navigation MUST be capable of resolving through current B3 canonical Contact identity.

### REQ-B4-197

B4 MUST NOT require B3 to rewrite historical Contact identity in order to support relationship continuity.

### REQ-B4-198

Contact merge and Asset merge MAY coexist without changing the logical identity of the existing ContactAssetRelationship.

### REQ-B4-199

Corrections to Contact and Asset canonical topology MUST remain independently composable with relationship decision history.

---

# 25. F23 — Non-regression

### REQ-B4-200

B4 implementation MUST preserve all accepted B1 behavior.

### REQ-B4-201

B4 implementation MUST preserve all accepted B2 behavior.

### REQ-B4-202

B4 implementation MUST preserve all accepted B3 behavior.

### REQ-B4-203

B4 MUST NOT regress `/health`.

### REQ-B4-204

B4 MUST NOT regress `/ready`.

### REQ-B4-205

B4 MUST NOT regress PostgreSQL persistence behavior.

### REQ-B4-206

B4 MUST NOT regress accepted transaction/session semantics.

### REQ-B4-207

B4 MUST NOT rewrite accepted migrations `001–021`.

### REQ-B4-208

Any B4 schema evolution MUST be forward-only after migration `021`.

### REQ-B4-209

Existing B1/B2/B3 tests MUST NOT be weakened merely to make B4 pass.

---

# 26. F24 — Verification and evidence

### REQ-B4-210

Every B4 requirement MUST be mapped to at least one verification/evidence path before implementation acceptance.

### REQ-B4-211

The implementation MUST provide positive tests for successful B4 behavior.

### REQ-B4-212

The implementation MUST provide negative tests for prohibited B4 behavior.

### REQ-B4-213

The implementation MUST test ambiguity and contradiction paths.

### REQ-B4-214

The implementation MUST test technical failure separately from governed non-resolution.

### REQ-B4-215

The implementation MUST test merge admission HOLD behavior.

### REQ-B4-216

The implementation MUST test wrong-merge correction and historical preservation.

### REQ-B4-217

The implementation MUST test survivor-selection precedence.

### REQ-B4-218

The implementation MUST test survivor-selection override provenance.

### REQ-B4-219

The implementation MUST test identifier replacement without Asset discontinuity.

### REQ-B4-220

The implementation MUST test cloned/duplicated strong identifier without automatic merge.

### REQ-B4-221

The implementation MUST test ExternalReference historical target preservation through Asset merge.

### REQ-B4-222

The implementation MUST test conflicting DomainProjection behavior without generic CPL domain adjudication.

### REQ-B4-223

The implementation MUST test relationship co-existence where policy allows it.

### REQ-B4-224

The implementation MUST test relationship conflict where policy establishes incompatibility.

### REQ-B4-225

The implementation MUST test relationship END separately from CORRECT.

### REQ-B4-226

The implementation MUST test retroactive relationship correction while preserving prior decision history.

### REQ-B4-227

The implementation MUST test valid-time and decision-time reconstructability.

### REQ-B4-228

The implementation MUST test relationship idempotent replay.

### REQ-B4-229

The implementation MUST test that similar relationship content does not automatically imply idempotent identity.

### REQ-B4-230

The implementation MUST test Contact endpoint canonical evolution.

### REQ-B4-231

The implementation MUST test Asset endpoint canonical evolution.

### REQ-B4-232

The implementation MUST test simultaneous Contact and Asset endpoint evolution.

### REQ-B4-233

The implementation MUST test endpoint correction after prior relationship decisions.

### REQ-B4-234

The implementation MUST test that relationship state does not automatically grant authorization.

### REQ-B4-235

The implementation MUST test that domain resolver output cannot directly mutate canonical CPL Asset topology.

### REQ-B4-236

The implementation MUST test that generic CPL can consume a domain resolution without becoming the producer of domain truth.

### REQ-B4-237

The implementation MUST test historical evidence continuity after supersession/correction.

### REQ-B4-238

The implementation MUST test clean installation/package execution from the canonical B4 build baseline.

### REQ-B4-239

The implementation MUST test migration from the accepted B3 database state through the B4 head.

### REQ-B4-240

The implementation MUST execute the complete B1/B2/B3/B4 regression suite against real PostgreSQL for acceptance evidence.

---

# 27. Requirement count

The initial B4 Requirement Matrix contains:

```text
REQ-B4-001 → REQ-B4-240
```

**240 requirements.**

No requirement above authorizes implementation yet.

---

# 28. Requirement-to-WHAT family map

```text
REQ-B4-001 → 014
  Asset continuity / creation

REQ-B4-015 → 024
  AssetIdentifier

REQ-B4-025 → 036
  AssetIdentityResolution

REQ-B4-037 → 046
  CanonicalAssetIdentityDecision

REQ-B4-047 → 060
  Asset merge

REQ-B4-061 → 069
  Asset correction

REQ-B4-070 → 077
  Survivor selection

REQ-B4-078 → 086
  Dependency disposition

REQ-B4-087 → 095
  ExternalReference

REQ-B4-096 → 103
  DomainProjection

REQ-B4-104 → 110
  Relationship identity

REQ-B4-111 → 119
  Relationship authority

REQ-B4-120 → 132
  CanonicalRelationshipDecision

REQ-B4-133 → 141
  Relationship time/lifecycle

REQ-B4-142 → 149
  Endpoint evolution

REQ-B4-150 → 154
  Relationship idempotency

REQ-B4-155 → 161
  Cardinality/conflict

REQ-B4-162 → 171
  Outcomes/failures

REQ-B4-172 → 181
  Provenance/history

REQ-B4-182 → 192
  Domain/CPL boundaries

REQ-B4-193 → 199
  B3 compatibility

REQ-B4-200 → 209
  Non-regression

REQ-B4-210 → 240
  Verification/evidence
```

---

# 29. Requirement authority rule

The Requirement Matrix MAY make the frozen WHAT testable.

It MUST NOT modify the frozen WHAT.

If any requirement challenge concludes that satisfying a requirement requires changing:

```text
B4 object ontology
authority allocation
survivor semantics
merge/correction semantics
relationship identity
valid-time/decision-time
historical preservation
domain/CPL boundary
```

the result MUST be:

```text
WHAT_CONFLICT
```

not silent requirement repair.

---

# 30. Challenge targets

Before this matrix can freeze, the Requirement Challenge must test at least:

```text
RC-B4-REQ-01
Are all 240 requirements traceable to frozen B4 WHAT?

RC-B4-REQ-02
Has any requirement accidentally invented HOW?

RC-B4-REQ-03
Are any frozen WHAT semantics missing requirements?

RC-B4-REQ-04
Do survivor requirements implement the frozen precedence correctly?

RC-B4-REQ-05
Do operation requirements preserve domain/CPL identity authority?

RC-B4-REQ-06
Are merge/correction requirements complete?

RC-B4-REQ-07
Are dependency disposition requirements testable?

RC-B4-REQ-08
Are ExternalReference and DomainProjection semantics sufficiently testable?

RC-B4-REQ-09
Is relationship identity independently testable from endpoints?

RC-B4-REQ-10
Are CanonicalRelationshipDecision obligations complete?

RC-B4-REQ-11
Can valid-time/decision-time semantics be verified without prescribing storage architecture?

RC-B4-REQ-12
Are idempotency requirements under-specified or over-specified?

RC-B4-REQ-13
Are conflict/cardinality rules appropriately policy-driven?

RC-B4-REQ-14
Are technical failure and governed non-resolution completely separated?

RC-B4-REQ-15
Are provenance/history obligations acceptance-testable?

RC-B4-REQ-16
Is B3 compatibility complete?

RC-B4-REQ-17
Are B1/B2/B3 non-regression requirements sufficient?

RC-B4-REQ-18
Can implementation acceptance be determined without inventing additional normative semantics?
```

---

# 31. Challenge outcome contract

Allowed outcomes:

```text
REQUIREMENTS_ACCEPTED

REPAIR_REQUIRED

WHAT_CONFLICT
```

`REQUIREMENTS_ACCEPTED` authorizes Requirement Matrix freeze.

It does **not** authorize B4 implementation.

---

# 32. Governance status

```text
B4 WHAT
  FROZEN

B4 Requirement Matrix v0
  PRODUCED
  240 requirements
  PROPOSED FOR REQUIREMENT CHALLENGE

B4 Requirement Matrix
  NOT YET FROZEN

B4 Execution Mandate
  NOT AUTHORIZED

B4 Implementation
  NOT AUTHORIZED
```

---

# 33. Next artifact

The next governance artifact is:

```text
B4_REQUIREMENT_CHALLENGE_v0.md
```

It must challenge `REQ-B4-001 → REQ-B4-240` against the frozen B4 WHAT and produce either:

```text
REQUIREMENTS_ACCEPTED
REPAIR_REQUIRED
WHAT_CONFLICT
```

**END — CPL B4 Requirement Matrix v0**
