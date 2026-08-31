# CPL — B3 WHAT Freeze Challenge v0

**System:** Common Product Layer — CPL
**Build Phase:** B3 — Identity + Accounts
**Challenge target:** `B3_WHAT_CONSOLIDATION_AND_FREEZE_v0`
**Canonical baseline (as cited at challenge authoring time):** `main @ c79be8290b6015be990273dc054a984e9a655431`
**Decision space:** `FREEZE_ACCEPTED | REPAIR_REQUIRED`

> **Provenance note:** this challenge was authored citing `c79be82` as baseline. The actual `main` HEAD at the time this document was materialized is `f1a340c0a27f60d8cfd01a86db2ae435fadf4ce7` — the commit that recorded `B3_WHAT_CONSOLIDATION_AND_FREEZE_v0.md` itself, which is the exact document under challenge here. This does not affect the substance of the challenge, which evaluates the document's content rather than its commit identity, but is recorded for traceability rather than silently corrected.

---

## 1. Challenge standard

Ce challenge ne demande plus si B3 est une bonne conception en général. Cette question a déjà été traitée par les artefacts précédents et le Cross-Artifact Re-Challenge.

Le test est maintenant plus sévère :

> **Le WHAT B3 est-il suffisamment fermé pour que la Requirement Matrix puisse être produite sans devoir inventer une nouvelle décision de produit, d'autorité ou de sémantique ?**

Une imprécision relevant du HOW n'empêche pas le freeze.

Une obligation encore à transformer en exigence n'empêche pas le freeze.

En revanche, une décision sémantique encore nécessaire à la construction de la Requirement Matrix impose `REPAIR_REQUIRED`.

---

## 2. FC-01 — Canonical artifact set

Le Freeze Candidate identifie correctement :

```text
A1  Identity Object & Authority Map v0
A2  Identity Resolution State & Decision Model v0
A3  Service Boundary & Operation Contract v0.1
```

Il conserve également le Service Boundary v0 comme historique sans lui laisser d'autorité sémantique concurrente.

La règle :

```text
v0 preserved historically
v0.1 authoritative semantically
```

est suffisante.

**VERDICT: PASS**

---

## 3. FC-02 — Ten repair decisions

Les dix décisions issues du challenge sont explicitement reprises :

```text
F-B3-01 → F-B3-10
```

Je ne trouve ni disparition, ni inversion, ni affaiblissement d'une de ces décisions dans le Freeze Candidate.

En particulier, les quatre distinctions les plus susceptibles d'être réintroduites accidentellement sont protégées :

```text
PROVISIONAL ≠ Contact.status

resolution ≠ mutation

Account historical binding ≠ current authority

duplicate assessment ≠ merge authority
```

**VERDICT: PASS**

---

## 4. FC-03 — Mission closure

La mission est suffisamment bornée :

> governed actor identity semantics above the B2 persistence foundation.

Elle définit également ce que B3 n'est pas.

Cela empêche notamment la Requirement Matrix de transformer B3 en :

```text
authentication service
authorization platform
generic CRUD layer
Asset identity service
Case service
```

Aucune décision de mission essentielle ne reste ouverte.

**VERDICT: PASS**

---

## 5. FC-04 — Object ontology closure

Les distinctions nécessaires au B3 v1 sont établies :

```text
Contact
ContactPoint
Account
Evidence
Resolution Result
Duplicate Assessment
Merge Proposal
Merge Authorization
Historical Identity State
```

Il n'est pas nécessaire que chacune devienne une table, une classe ou un objet persistant.

C'est justement une décision du HOW.

L'ontologie fonctionnelle est suffisante pour produire des requirements.

**VERDICT: PASS**

---

## 6. FC-05 — Resolution semantics closure

Le système possède désormais une seule sémantique de résolution :

```text
multiple evidence types
        ↓
ONE resolution semantics
```

Les états épistémiques ne sont pas confondus avec les états des objets.

Et :

```text
resolution
≠
automatic mutation
```

est explicitement protégé.

La Requirement Matrix pourra donc spécifier les conditions et résultats sans inventer un nouveau modèle de résolution.

**VERDICT: PASS**

---

## 7. FC-06 — Primitive operation completeness

Les 14 primitives sont :

```text
CONTACT
01 get_contact
02 resolve_contact
03 create_contact

CONTACT POINT
04 add_contact_point
05 verify_contact_point
06 invalidate_contact_point
07 set_primary_contact_point

ACCOUNT
08 attach_account
09 resolve_authenticated_contact
10 disable_account
11 revoke_account

RECONCILIATION
12 detect_duplicate_contact
13 propose_merge
14 merge_contacts
```

Je les challenge sous trois angles.

**Coverage**

Chaque responsabilité déclarée de B3 dispose d'un point d'entrée sémantique.

**Duplication**

Aucune primitive n'est manifestement redondante.

**Hidden missing primitive**

Je ne trouve pas d'opération indispensable dont l'absence obligerait la Requirement Matrix à inventer une nouvelle primitive.

Notamment, l'absence de :

```text
find_or_create_contact
```

est volontaire : c'est une composition.

Et l'absence de :

```text
authorize_merge()
```

comme primitive B3 est cohérente : `AUTHORIZE_MERGE` est une autorité consommée par le système, pas nécessairement une opération produite par B3.

**VERDICT: PASS**

**Freeze consequence**

Le nombre 14 devient donc structurel.

Ajouter une 15e primitive après freeze nécessitera normalement un WHAT Change Request.

---

## 8. FC-07 — Authority closure

Les classes d'autorité sont suffisamment distinguées :

```text
READ_IDENTITY
RESOLVE_IDENTITY
CREATE_CONTACT

MANAGE_CONTACT_POINT
VERIFY_CONTACT_POINT

ATTACH_ACCOUNT
MANAGE_ACCOUNT

ASSESS_DUPLICATE
PROPOSE_MERGE
AUTHORIZE_MERGE
EXECUTE_MERGE
```

Le point critique est le merge.

Le système impose :

```text
ASSESS
 ↓
PROPOSE
 ↓
AUTHORIZE
 ↓
EXECUTE
```

Il n'est donc plus possible pour la Requirement Matrix de transformer un score ou une détection en autorisation.

**VERDICT: PASS**

---

## 9. FC-08 — Verification boundary

La frontière est correctement fermée :

```text
external verification mechanism
          ↓
verification assertion
          ↓
B3 admissibility
          ↓
ContactPoint state transition
```

Il reste à déterminer dans la Requirement Matrix ce qu'une assertion admissible doit satisfaire.

C'est précisément une requirement.

Il n'est pas nécessaire de choisir maintenant :

```text
OTP provider
email provider
signature format
verification API
```

**VERDICT: PASS**

---

## 10. FC-09 — Account semantics

La hiérarchie :

```text
ACTIVE
PENDING
DISABLED
REVOKED
```

possède désormais une conséquence d'autorité suffisamment claire.

En particulier :

```text
DISABLED / REVOKED
→ historical evidence
→ no silent current resolution authority
```

Le rebinding incompatible est également sorti du CRUD et placé dans la reconciliation boundary.

La Requirement Matrix n'a pas besoin d'inventer la signification fondamentale d'un Account.

**VERDICT: PASS**

---

## 11. FC-10 — Merge semantics closure

C'est le domaine le plus dangereux du B3 WHAT ; il mérite donc un challenge spécifique.

Les propriétés désormais établies sont :

```text
merge is directional
source is preserved
source remains historically interpretable
merge is not deletion
no blind FK rewrite
related-object semantics matter
conflict may block merge
unsafe reconciliation blocks completion
partial misleading merge state forbidden
assessment does not authorize merge
```

Cela constitue une sémantique de merge suffisamment fermée.

**VERDICT: PASS**

---

## 12. FC-11 — Relationship-family issue

Le Freeze Candidate transmet à la Requirement Matrix cinq familles :

```text
Accounts
ContactPoints
ContactAssetRelationships
CaseParticipants
ExternalReferences
```

avec quatre classifications possibles :

```text
preserve historical relationship
reassociate current relationship
reject conflicting reconciliation
defer outside B3 authority
```

Question du challenge :

> Est-ce que choisir entre ces quatre comportements est encore une décision WHAT ?

Dans ce cas, non, à condition que la matrice ne puisse pas inventer une cinquième sémantique incompatible.

Le WHAT a déjà établi le principe :

> history must be preserved and unsafe reconciliation must block merge.

La matrice peut donc déterminer le comportement précis de chaque relation comme transformation normative de ce principe.

**VERDICT: PASS**

**Freeze constraint:** les quatre catégories constituent l'espace autorisé de classification.

---

## 13. FC-12 — Transaction semantics

Le WHAT exige :

```text
successful coherent merge
```

ou :

```text
no surviving misleading partial merge
```

Il ne choisit pas :

```text
transaction isolation
locking
savepoints
SQL strategy
```

C'est exactement le bon niveau.

**VERDICT: PASS**

---

## 14. FC-13 — Idempotency

Le WHAT définit le résultat requis :

> replay must not unintentionally multiply identity state.

Il ne prescrit pas son mécanisme.

C'est suffisant pour produire des requirements puis des tests.

**VERDICT: PASS**

---

## 15. FC-14 — Concurrency

Même analyse.

Le WHAT identifie les classes de race et impose la préservation des invariants sans choisir :

```text
row locking
optimistic locking
SERIALIZABLE
advisory locks
```

**VERDICT: PASS**

---

## 16. FC-15 — Provenance

Le WHAT exige la récupérabilité de :

```text
operation
actor/requester
evidence
authority
decision
mutation
time
```

Il ne choisit pas le stockage.

Cela suffit pour la Requirement Matrix.

**VERDICT: PASS**

---

## 17. FC-16 — Proposal persistence subtlety

Le Re-Challenge avait identifié :

```text
identity-state mutation
≠
governance/evidence artifact persistence
```

Le Freeze Candidate reprend explicitement cette distinction.

Ainsi :

```text
propose_merge
```

peut ne pas modifier l'identité tout en produisant éventuellement une représentation persistante du proposal.

La Requirement Matrix peut préciser l'obligation de durabilité sans transformer `propose_merge` en merge.

**VERDICT: PASS**

---

## 18. FC-17 — Semantic outcomes

Le WHAT préserve :

```text
SUCCESS
MATCHED
NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
PROVISIONAL
REJECTED
INVALID
ALREADY_EXISTS
ALREADY_MERGED
NO_CHANGE
EXECUTION_FAILURE
```

Il autorise la Requirement Matrix à déterminer leur applicabilité primitive par primitive.

C'est suffisant.

Il serait prématuré de figer maintenant des HTTP codes ou exception classes.

**VERDICT: PASS**

---

## 19. FC-18 — B2/B3 boundary

Le Freeze Candidate affirme :

```text
B2 = persistence foundation
B3 = governed identity semantics above B2
```

et interdit implicitement de considérer toute mutation techniquement possible en B2 comme une opération autorisée B3.

Il exige également B2 non-regression.

C'est la frontière nécessaire.

**VERDICT: PASS**

---

## 20. FC-19 — Scope exclusion closure

Les exclusions sont explicites et suffisamment nombreuses pour empêcher le scope creep principal :

```text
authentication
passwords
OAuth implementation
OTP
sessions
JWT
RBAC implementation
frontend
Asset identity
Case lifecycle
Runner execution
VIR
PGDR
bulk merge
automatic probabilistic merge
ML/LLM-authorized merge
etc.
```

Une Requirement Matrix qui réintroduirait l'un de ces éléments violerait le freeze.

**VERDICT: PASS**

---

## 21. FC-20 — Requirement transformation surface

Les 20 RMO sont :

```text
RMO-01  Object retrieval
RMO-02  Resolution semantics
RMO-03  Contact creation
RMO-04  ContactPoint lifecycle
RMO-05  Verification assertion admissibility
RMO-06  Account binding
RMO-07  Account-state authority
RMO-08  Duplicate assessment
RMO-09  Merge proposal
RMO-10  Merge authorization
RMO-11  Merge execution
RMO-12  Historical preservation
RMO-13  Related-object reconciliation
RMO-14  Transaction integrity
RMO-15  Idempotency
RMO-16  Concurrency
RMO-17  Provenance
RMO-18  Boundary preservation
RMO-19  B2 non-regression
RMO-20  Semantic failure outcomes
```

Collectivement, elles couvrent les obligations identifiées pendant le challenge.

Je ne trouve pas de domaine essentiel nécessitant un RMO-21 avant freeze.

**VERDICT: PASS**

---

## 22. FC-21 — Requirement Matrix authority

La matrice reçoit suffisamment d'autorité pour préciser :

```text
preconditions
outcomes
evidence admissibility
conflicts
relationship behavior
non-regression
replay behavior
concurrent forbidden states
recoverable provenance
```

Mais elle ne reçoit pas l'autorité pour changer :

```text
mission
ontology
primitive boundary
resolution model
authority hierarchy
merge semantics
scope
```

Cette distinction est exploitable.

**VERDICT: PASS**

---

## 23. FC-22 — HOW contamination test

Je cherche maintenant les décisions qui auraient été gelées trop tôt.

Le document laisse explicitement ouverts :

```text
REST/RPC
endpoint paths
serialization
Pydantic layout
query strategy
locking
transaction isolation
idempotency mechanism
provenance storage
logging
repository pattern
service classes
module structure
deployment
```

Je ne trouve pas de choix technologique substantiel accidentellement transformé en invariant WHAT.

Les références à `Contact.status = MERGED` et `merged_into_id` ne constituent pas ici une nouvelle architecture : elles s'appuient sur la fondation B2 déjà acceptée et expriment la sémantique de l'état existant.

**VERDICT: PASS**

---

## 24. FC-23 — Developer decision leakage

Test critique :

> Si nous donnons le WHAT gelé + Requirement Matrix à un développeur, devra-t-il encore décider lui-même ce que signifie B3 ?

Sur les points fondamentaux : non.

Il pourra décider comment réaliser :

```text
locking
queries
service structure
serialization
transaction mechanics
```

mais pas décider arbitrairement :

```text
what identity means
what Account authority means
whether resolution mutates
whether duplicate means merge
whether source Contact survives
whether disabled Account resolves
whether external verification belongs to B3
```

C'est précisément le résultat recherché.

**VERDICT: PASS**

---

## 25. FC-24 — Change-control test

Le document établit une règle essentielle :

```text
contradiction with frozen WHAT
        ↓
WHAT CHANGE REQUEST
```

et interdit de cacher ce changement sous :

```text
requirement refinement
developer interpretation
test repair
DevOps correction
```

C'est suffisant pour maintenir le freeze après son adoption.

**VERDICT: PASS**

---

## 26. Findings

Après challenge complet :

```text
BLOCKING FINDINGS      = 0
MAJOR FINDINGS         = 0
WHAT REPAIR FINDINGS   = 0
```

Trois contraintes doivent néanmoins être transportées explicitement vers la Requirement Matrix :

**FC-O01**
The 14-operation primitive set is frozen.
Any addition/removal requires WHAT reopening.

**FC-O02**
Related-object reconciliation must classify each relevant
relationship family within the authorized semantic space:
PRESERVE / REASSOCIATE / REJECT-CONFLICT / DEFER.

**FC-O03**
Requirement refinement must remain implementation-neutral
unless a mechanism is demonstrably necessary to satisfy
a frozen semantic obligation.

Ce sont des freeze obligations, pas des réparations.

---

## 27. Freeze Challenge Matrix

| Challenge | Result |
|---|---|
| Canonical artifact set | PASS |
| F-B3-01 → F-B3-10 preservation | PASS |
| Mission closure | PASS |
| Object ontology | PASS |
| Resolution semantics | PASS |
| 14 primitive coverage | PASS |
| Authority model | PASS |
| Verification boundary | PASS |
| Account semantics | PASS |
| Merge semantics | PASS |
| Relationship reconciliation boundary | PASS |
| Transaction semantics | PASS |
| Idempotency | PASS |
| Concurrency | PASS |
| Provenance | PASS |
| Proposal persistence distinction | PASS |
| Semantic outcomes | PASS |
| B2/B3 boundary | PASS |
| Scope exclusions | PASS |
| 20 RMO coverage | PASS |
| Requirement Matrix authority | PASS |
| HOW contamination | PASS |
| Developer decision leakage | PASS |
| Change control | PASS |

**24 / 24 PASS**

---

## 28. Final Freeze Decision

```text
FREEZE_ACCEPTED
```

The B3 WHAT is sufficiently complete, internally coherent, bounded and implementation-independent to be transformed into a Requirement Matrix without requiring downstream actors to invent unresolved B3 product semantics.

Therefore:

```text
B3 WHAT CONSOLIDATION
    ACCEPTED

B3 WHAT FREEZE
    ACCEPTED

B3 WHAT
    FROZEN

Blocking WHAT findings
    NONE

Further B3 WHAT repair
    NOT REQUIRED

B3 Requirement Matrix
    AUTHORIZED FOR PRODUCTION

B3 Execution Mandate
    NOT YET AUTHORIZED

B3 Implementation
    NOT AUTHORIZED
```

---

## 29. Frozen B3 WHAT Boundary

Effective upon governance recording of this freeze, the following are frozen:

```text
B3 mission
B3 v1 scope
B3 exclusions

canonical B3 WHAT artifact set

F-B3-01 → F-B3-10

object/authority distinctions
one-resolution semantics
resolution/mutation separation

14 primitive operations

verification boundary
Account authority semantics

reconciliation authority ladder
merge directionality
source preservation
no blind FK rewrite
merge conflict semantics
transactional outcome obligation

idempotency obligation
concurrency obligation
provenance obligation

semantic outcome distinctions

20 RMO families

Requirement Matrix authority
HOW boundary
Build boundary
change-control mechanism
```

---

## 30. Authorized transition

We can now make the transition that was previously prohibited:

```text
B3 WHAT
   │
   │  FREEZE_ACCEPTED
   ▼
╔══════════════════════════╗
║      WHAT FROZEN         ║
╚══════════════════════════╝
             │
             ▼
     REQUIREMENT TRANSFORMATION
             │
             ▼
   B3 REQUIREMENT MATRIX
```

But not yet:

```text
Requirement Matrix
       ╳
       ▼
Implementation
```

There remains another governance boundary:

```text
Requirement Matrix
       ↓
challenge / verification
       ↓
Execution Mandate
════════════════════
   BUILD BOUNDARY
════════════════════
       ↓
implementation
```

**FINAL VERDICT: FREEZE_ACCEPTED**

Cette fois, le mot FROZEN est justifié : nous avons séparé ce qui ne peut plus être modifié sans réouverture du WHAT de ce que la Requirement Matrix a précisément pour fonction de déterminer.

**End of `CPL — B3 WHAT Freeze Challenge v0`**
