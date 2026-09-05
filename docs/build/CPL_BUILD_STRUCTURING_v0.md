# CPL — Build Structuring v0

## 0. Objet

Question à résoudre :

> **Étant donné le CPL effectivement construit après B4, quelles unités de construction restent nécessaires, quelles sont leurs dépendances, et laquelle constitue le prochain Build Unit admissible ?**

Ce travail ne produit ni WHAT, ni requirements, ni code.

Il produit une **structure de construction**.

```text
CPL target
    +
Materialized CPL
    +
Frozen invariants
    +
Authority boundaries
    +
Known capabilities
    +
Known missing capabilities
        ↓
BUILD STRUCTURING
        ↓
Remaining construction graph
        ↓
Next admissible Build Unit
```

---

# 1. État matériel de départ

Nous ne repartons surtout pas de la vision abstraite du CPL.

Nous partons de ce qui existe réellement.

### B1 — Repository & Environment

Le système possède son substrate d'exécution et de développement.

### B2 — Database Foundation

Le système possède sa persistance canonique et son infrastructure de migration.

### B3 — Identity

Le CPL sait désormais gouverner une identité canonique plutôt que simplement stocker des personnes/contacts.

### B4 — Assets + Relationships

Le CPL sait désormais représenter :

```text
Contact
Asset
ContactAssetRelationship
```

avec :

```text
identity
authority
resolution
canonical decisions
history
correction
supersession
current navigation
historical navigation
external references
domain projections
```

Nous avons donc franchi une frontière importante.

Le CPL n'est plus simplement :

```text
database + records
```

Il commence à être :

```text
governed canonical world
```

---

# 2. Le graphe actuellement matérialisé

Après B4, une représentation minimale est :

```text
                 Contact
                    │
                    │ governed relationship
                    ▼
                  Asset
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
 ExternalReference      DomainProjection
```

Autour de ces objets existent maintenant :

```text
Authority
Resolution
Canonical Decision
Correction
Supersession
History
Navigation
```

C'est beaucoup plus important que le simple inventaire des tables.

Nous avons construit les premières **primitives gouvernées du CPL**.

---

# 3. Ce que B4 révèle comme absence structurelle

Maintenant apparaît une question nouvelle.

Nous savons représenter :

> **qui / quoi est dans le système et certaines relations entre ces objets.**

Mais cela ne signifie pas encore que le CPL sait représenter :

> **ce qui arrive à ces objets.**

Considérons VIR/PGDR sans commencer à construire VIR/PGDR.

Une voiture peut maintenant être :

```text
Asset(vehicle)
```

et une personne :

```text
Contact
```

avec :

```text
Contact
   │
   └── owns / uses / ...
           │
           ▼
         Asset
```

Mais ensuite :

```text
vehicle inspected
vehicle diagnosed
vehicle repaired
vehicle transferred
vehicle insured
vehicle sold
vehicle damaged
vehicle updated
```

Que sont ces choses ?

Elles ne sont ni :

```text
Contact
Asset
Relationship
Identifier
ExternalReference
DomainProjection
```

Nous rencontrons une nouvelle catégorie ontologique.

---

# 4. Première candidate : occurrence / event / activity

On pourrait immédiatement l'appeler `Event`.

Je ne le ferais pas encore.

Parce que :

```text
repair
diagnosis
inspection
ownership transfer
registration
claim
maintenance
```

ne sont pas nécessairement du même type.

Certaines sont des événements.

Certaines sont des activités.

Certaines sont des procédures.

Certaines sont des changements d'état.

Certaines sont des décisions.

Nous devons donc conserver provisoirement une catégorie plus faible :

```text
Occurrence
```

au sens :

> quelque chose qui arrive, est effectué ou devient vrai dans le monde du CPL.

C'est une **candidate Build Unit**, pas encore B5.

---

# 5. Deuxième absence : state

B4 contient déjà implicitement du changement :

```text
CURRENT
SUPERSEDED
INVALIDATED
CORRECTED
```

Mais ce sont essentiellement des états de gouvernance des objets CPL.

Ils ne constituent pas nécessairement un modèle général de l'état d'un objet.

Exemple :

```text
Vehicle
   mileage = 83,000
   operational = true
   registration_status = active
```

Puis :

```text
repair
   ↓
Vehicle state changes
```

Nous avons donc potentiellement :

```text
Occurrence
     ↓
State transition
```

Mais attention : si nous créons un modèle générique `State` trop tôt, nous risquons de faire du CPL le propriétaire de vérités métier qui appartiennent aux domaines.

Cela heurterait directement notre invariant B4 :

> **DOMAIN DETERMINES DOMAIN TRUTH; CPL GOVERNS CANONICAL REPRESENTATION.**

Donc :

```text
Generic Domain State Engine
```

est probablement **interdit ou au minimum suspect**.

---

# 6. Troisième absence : provenance/evidence

B4 utilise déjà :

```text
evidence
authority
provenance
resolution
decision
```

Mais ces notions commencent maintenant à apparaître transversalement.

B3 en avait besoin.

B4 en a besoin.

Les futures occurrences en auront besoin.

Par exemple :

```text
Garage
   ↓
Inspection report
   ↓
diagnosis
   ↓
repair
```

Il faut distinguer :

```text
something happened
        ≠
someone says it happened
        ≠
evidence that it happened
        ≠
CPL representation of it
```

Cela peut devenir une primitive transversale.

Mais encore une fois, ne concluons pas qu'il faut immédiatement un `Evidence B5`.

---

# 7. Quatrième absence : actor / role / authority

B3/B4 utilisent déjà `AuthorityContext`.

Mais à mesure que le système devient opérationnel, nous rencontrerons :

```text
Contact
Organization
System
Domain Resolver
Administrator
Service
Runner
External Institution
```

qui peuvent agir sous différents rôles.

Un même Contact pourrait être :

```text
owner
driver
technician
advisor
representative
```

Le rôle n'est pas l'identité.

Et :

```text
Role ≠ Authority
Authority ≠ Permission
Permission ≠ Relationship
```

Nous pouvons donc anticiper un autre nœud structurel.

---

# 8. Cinquième absence : organization / account / participation

Notre progression canonique historique comprenait :

```text
User
 ↓
Contact
 ↓
Account status
 ↓
Registered vehicles
```

Mais B3/B4 ont volontairement commencé plus profondément, par l'identité canonique.

Il reste potentiellement des primitives comme :

```text
Organization
Membership
Account
Participation
```

Cependant, attention à ne pas confondre :

```text
CPL primitive
```

et :

```text
business application concern
```

`Account`, par exemple, peut être nécessaire au produit sans nécessairement être une primitive ontologique centrale du CPL.

---

# 9. On commence donc à voir plusieurs candidats

À ce stade :

```text
Current CPL
    │
    ├── Identity
    ├── Asset
    └── Relationship
            │
            ▼
       missing structures
            │
    ┌───────┼────────┬──────────┬────────────┐
    ▼       ▼        ▼          ▼            ▼
Occurrence State  Evidence   Actor/Role   Organization
```

Mais cette liste **n'est pas encore un Build Plan**.

Il faut trouver leurs dépendances.

---

# 10. Analyse des dépendances

Prenons `State`.

Pour gouverner un changement d'état, nous devons généralement savoir :

```text
what object?
what changed?
when?
according to whom?
based on what?
```

Cela donne :

```text
Identity/Object
     +
Occurrence
     +
Authority/Provenance
        ↓
State transition representation
```

Donc `State` semble dépendre d'autres primitives.

Il est probablement trop tôt pour en faire le prochain Build Unit.

---

Prenons `Organization`.

Une Organization possède probablement :

```text
identity
relationships
roles
possibly assets
```

Nous avons déjà Identity et Relationships.

Mais il faudra peut-être Role/Participation avant de modéliser correctement :

```text
Contact ── member_of ── Organization
```

Donc Organization n'est pas nécessairement la prochaine dépendance fondamentale.

---

Prenons `Evidence`.

Evidence peut exister indépendamment d'Occurrence :

```text
VIN document
identity evidence
ownership document
```

B3/B4 en utilisent déjà conceptuellement.

Mais une Evidence primitive générique risque de devenir extrêmement abstraite.

Nous devons déterminer si elle est réellement nécessaire comme objet canonique ou simplement comme structure attachée aux décisions.

---

Prenons `Occurrence`.

Une occurrence peut être minimale :

```text
Occurrence
    id
    type
    involved canonical objects
    source/domain
    valid time
    recorded time
    provenance
```

Elle peut exister sans moteur générique d'état.

Et elle permet ensuite :

```text
Occurrence
   ├── evidence
   ├── participants
   ├── projections
   └── consequences
```

Cela en fait une candidate structurellement intéressante.

---

# 11. Première découverte de Build Structuring

Nous pouvons maintenant commencer à dessiner un graphe de dépendances plutôt qu'une liste :

```text
              Identity
                 │
                 │
        ┌────────┴────────┐
        ▼                 ▼
      Asset          Relationship
        \                 /
         \               /
          └───────┬─────┘
                  ▼
             Occurrence
                  │
          ┌───────┼─────────┐
          ▼       ▼         ▼
       Evidence  Role    State/Change
          │       │         │
          └───────┼─────────┘
                  ▼
          richer domain flows
```

Je ne considère pas encore ce graphe comme démontré.

Mais il produit une hypothèse forte :

> **Occurrence pourrait être la prochaine primitive structurelle nécessaire après Identity + Asset + Relationship.**

---

# 12. Mais il manque une dimension essentielle

Une occurrence relie souvent plusieurs objets :

```text
Contact
   │
   │ performs
   ▼
Repair
   │
   │ concerns
   ▼
Vehicle
```

Si nous modélisons simplement ceci comme :

```text
ContactAssetRelationship
```

nous perdons l'occurrence.

Et si nous faisons :

```text
Contact ── relationship ── Repair
Repair ── relationship ── Asset
```

alors `Relationship` devient un mécanisme universel de graphe, ce que B4 n'a précisément **pas** autorisé.

B4 a construit :

```text
ContactAssetRelationship
```

pas :

```text
GenericEverythingRelationship
```

C'est crucial.

---

# 13. Nouvelle frontière

Nous découvrons donc probablement :

```text
Structural Relationship
```

versus

```text
Participation in Occurrence
```

Exemple :

```text
Alice OWNS Vehicle
```

est une relation relativement durable.

Alors que :

```text
Garage PERFORMS Repair
Vehicle SUBJECT_OF Repair
Alice REQUESTS Repair
```

sont des participations à une occurrence.

Cela suggère :

```text
Relationship
    ≠
Occurrence Participation
```

Cette distinction pourrait devenir un invariant important du prochain WHAT.

---

# 14. Ce que le prochain Build Unit ne doit probablement PAS être

Nous pouvons déjà éliminer plusieurs candidats comme prochaine unité immédiate :

```text
NOT VIR
NOT PGDR
NOT billing
NOT workflow engine
NOT generic state machine
NOT authorization engine
NOT social graph
NOT frontend
NOT Organization ecosystem
```

Ils sont soit trop hauts dans la pile, soit trop spécifiques, soit dépendants de primitives encore absentes.

---

# 15. Candidate Build Structure

À ce stade, je proposerais provisoirement :

```text
B1  Repository / Environment
 ↓
B2  Database Foundation
 ↓
B3  Identity
 ↓
B4  Asset + Relationship
 ↓
BU-CANDIDATE-1
    Occurrence + Participation
 ↓
BU-CANDIDATE-2
    Evidence / Assertion / Provenance
 ↓
BU-CANDIDATE-3
    Role / Acting Capacity
 ↓
BU-CANDIDATE-4
    State / Transition Representation
 ↓
higher CPL capabilities
```

Mais je ne gèlerais surtout pas cet ordre.

Pourquoi ?

Parce que `Evidence` et `Role` pourraient être des dépendances de `Occurrence`, plutôt que des successeurs.

---

# 16. Le vrai problème de structuration apparaît

Nous devons déterminer si :

```text
Occurrence
    requires
Evidence + Role
```

ou si :

```text
Occurrence
    can exist minimally
        ↓
Evidence + Role enrich it later
```

C'est exactement le type de question que **HANNIBAL doit résoudre avant SPR**.

Autrement, nous retomberions dans :

> « Ça ressemble à un bon B5, construisons-le. »

Ce que nous cherchons justement à éviter.

---

# 17. Proposition de graphe à challenger

Je retiendrais comme **Build Structuring Hypothesis v0** :

```text
                 B3 Identity
                     │
                     ▼
             B4 Asset/Relationship
                     │
                     ▼
          ┌──────────────────────┐
          │ Occurrence Kernel    │
          │ + Participation      │
          └──────────────────────┘
              │       │       │
              ▼       ▼       ▼
          Evidence   Role    State
              │       │       │
              └───────┼───────┘
                      ▼
             Domain Operations
                      │
             ┌────────┼────────┐
             ▼        ▼        ▼
            VIR      PGDR     other
```

Mais avec trois questions bloquantes :

```text
HBS-Q01
Can Occurrence exist canonically without a generalized Evidence primitive?

HBS-Q02
Can Participation be governed without first introducing a generalized
Actor/Role model?

HBS-Q03
Does a CPL Occurrence represent something that happened in the world,
or only the CPL's governed representation/assertion that it happened?
```

**Q03 est la plus importante.**

Parce que si nous disons :

```text
Occurrence = thing that happened
```

nous faisons potentiellement du CPL une autorité sur la réalité.

Alors que B4 nous a appris à distinguer :

```text
physical identity determination
        ≠
canonical representation
```

Le même principe devrait probablement devenir :

```text
WORLD OCCURRENCE
        ≠
DOMAIN DETERMINATION / ASSERTION
        ≠
CPL CANONICAL REPRESENTATION
```

Et là nous retrouvons exactement notre problème ontologique général : **la représentation ne doit jamais acquérir silencieusement le statut de réalité.**

---

# 18. Premier résultat HANNIBAL

Je m'arrêterais donc **avant de déclarer Occurrence = B5**.

Nous avons suffisamment progressé pour produire :

```text
CPL_BUILD_STRUCTURING_v0

Current build frontier:
  Identity + Asset + Relationship

Leading next-unit candidate:
  Occurrence + Participation

Status:
  CANDIDATE
  NOT ADMITTED

Blocking structural questions:
  HBS-Q01 Evidence dependency
  HBS-Q02 Role/Actor dependency
  HBS-Q03 World/Assertion/Representation boundary

Next action:
  BUILD STRUCTURE CHALLENGE
```

C'est exactement ce que nous voulions obtenir en introduisant HANNIBAL : **pour la première fois, le prochain `B` n'est pas choisi parce qu'il paraît logique. Il doit être admis par la structure de construction.**

Et je pense que le prochain mouvement doit être un **CPL Build Structure Challenge v0**, pas encore un WHAT. C'est ce challenge qui doit essayer de détruire l'hypothèse `Occurrence + Participation` et, si elle survit, déterminer ses prérequis réels.
