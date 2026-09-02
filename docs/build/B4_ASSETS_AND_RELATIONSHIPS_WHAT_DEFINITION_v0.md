# CPL — B4 Assets + Relationships — WHAT Definition v0

**System:** Common Product Layer — CPL
**Build Phase:** B4 — Assets + Relationships
**Artifact:** WHAT Definition
**Version:** v0
**Canonical baseline:** `main @ 63bc38a`

---

## 1. Mission

B4 doit transformer les structures persistantes créées en B2 autour de :

```text
Asset
AssetIdentifier
ContactAssetRelationship
VehicleDetail
AssetIdentityResolution
ExternalReference
```

en une capacité CPL gouvernée de représentation, identification, rattachement et continuité des Assets.

La question fondamentale devient :

> Quel Asset CPL représente cet objet du monde réel, comment est-il identifié, comment ses identifiants et spécialisations sont-ils rattachés, et comment les relations entre Contacts et Assets sont-elles établies sans confondre observation, identité, possession, usage ou autorité ?

---

## 2. B4 n'est pas un registre automobile

Même si CPL possède déjà :

```text
automotive.vehicle_details
```

B4 doit rester générique.

Donc :

```text
Asset
≠ Vehicle
```

Un véhicule est une spécialisation possible de `Asset`.

Plus tard, CPL doit pouvoir supporter aussi :

```text
property
machine
solar installation
battery
drone
industrial equipment
documented physical object
other domain assets
```

sans redéfinir l'identité Asset.

---

## 3. Objet central de B4

Comme pour B3, l'objet central n'est probablement pas simplement la table `Asset`.

C'est :

```text
ASSET RESOLUTION
```

c'est-à-dire :

```text
Observed Asset Evidence
        ↓
Existing CPL Asset ?
        ↓
MATCH / NO MATCH / AMBIGUOUS / CONFLICTING
```

puis :

```text
existing Asset
    ↓
attach identifier / specialization / relationship

new Asset
    ↓
controlled creation
```

B4 doit donc construire au-dessus du modèle persistant B2 un Asset Identity Boundary.

---

## 4. Distinction fondamentale

B4 doit préserver :

```text
Asset
≠
AssetIdentifier
≠
ExternalReference
≠
Domain Projection
≠
ContactAssetRelationship
```

Exemples :

```text
VIN
≠ Vehicle

license plate
≠ Vehicle

serial number
≠ Machine

land registry reference
≠ Property

VehicleDetail
≠ Asset

owner relationship
≠ Asset identity
```

Ces objets peuvent contribuer à identifier ou décrire un Asset, mais aucun ne doit automatiquement devenir l'Asset lui-même.

---

## 5. Asset as canonical object

`Asset` doit être le point canonique CPL représentant l'objet persistent.

Conceptuellement :

```text
Real-world object
      ↓
CPL Asset
      ↓
├── identifiers
├── domain projections
├── relationships
├── identity resolutions
└── external references
```

L'identité canonique CPL reste :

```text
asset_id
```

Les identifiants externes sont des preuves ou clés de résolution.

---

## 6. Types d'Asset

B4 doit permettre au minimum la distinction :

```text
GENERIC
AUTOMOTIVE
```

si c'est ce que B2 a déjà établi.

Mais B4 ne doit pas figer CPL sur ces deux seuls domaines si le schema permet une extension.

Le principe est :

> Asset type specialise behaviour; it does not redefine canonical Asset identity.

---

## 7. AssetIdentifier semantics

`AssetIdentifier` représente un identifiant observable ou attribué.

Exemples possibles :

```text
VIN
registration / license plate
serial number
manufacturer identifier
internal fleet identifier
registry identifier
domain-specific identifier
```

Mais :

```text
identifier value
≠
automatically unique real-world object
```

La sémantique dépend :

```text
identifier_type
issuer / namespace
jurisdiction
validity period
confidence / evidence
status
```

si ces dimensions sont supportées ou requises.

---

## 8. Identifiers change over time

Un Asset peut avoir :

```text
multiple identifiers
```

et certains peuvent :

```text
change
expire
be replaced
be corrected
be disputed
```

Exemple évident :

```text
license plate
```

peut changer alors que :

```text
vehicle
```

reste le même.

Donc B4 doit distinguer :

```text
stable identity
vs
mutable identifiers
```

C'est un invariant fondamental.

---

## 9. Asset resolution

Le mécanisme conceptuel doit être :

```text
Asset Evidence
      ↓
Identifier lookup
      +
Domain evidence
      +
Existing resolutions
      ↓
Asset Resolution
```

et produire au minimum :

```text
MATCHED
NOT_FOUND
AMBIGUOUS
CONFLICTING
UNRESOLVED
```

Nous devons probablement réutiliser la discipline épistémique de B3, sans nécessairement copier exactement ses objets ou API.

---

## 10. Asset creation

Comme avec Contact :

```text
NOT_FOUND
≠
automatically CREATE Asset
```

Il faut distinguer :

```text
resolve_asset
```

et :

```text
create_asset
```

La création doit nécessiter :

```text
creation authority
sufficient creation context
absence of blocking conflict
asset type
provenance
```

---

## 11. AssetIdentityResolution

B2 possède déjà un objet :

```text
AssetIdentityResolution
```

B4 doit donc probablement en faire une pièce centrale plutôt que créer une seconde sémantique parallèle.

La question devient : que représente exactement une AssetIdentityResolution ?

Candidate definition :

> A persisted conclusion or assessment linking observed asset evidence to an Asset, with status, confidence, provenance and historical supersession.

Il faudra vérifier cela contre le schema B2 lors de l'Authority Map.

---

## 12. Current resolution pointer

B2 a prévu un concept de :

```text
current_asset_resolution
```

ou équivalent.

B4 doit en définir la sémantique :

```text
historical resolutions
      ↓
one current authoritative resolution pointer
```

mais :

```text
current
≠
history rewritten
```

Une nouvelle résolution ne doit pas effacer les précédentes.

---

## 13. Domain projection

`VehicleDetail` nous donne déjà le pattern :

```text
Asset
  ↓
VehicleDetail
```

La projection de domaine doit rester :

```text
specialized description of Asset
```

et non :

```text
parallel Asset identity
```

Donc :

```text
VehicleDetail.asset_id
```

doit référencer l'identité canonique Asset.

---

## 14. Projection lifecycle

Il faut prévoir qu'un Asset peut :

```text
acquire a domain projection
update projection facts
retain projection history where required
```

Mais B4 ne doit pas nécessairement devenir un système complet de versioning de toutes les données domaine.

À ce stade, il doit au minimum établir la frontière :

```text
Asset identity
vs
Asset domain detail
```

---

## 15. ContactAssetRelationship

C'est probablement le second objet majeur de B4.

Il représente non pas l'identité de l'Asset, mais :

```text
Contact
   ↕
Asset
```

avec une sémantique de relation.

Exemples :

```text
OWNER
USER
DRIVER
LESSEE
MANAGER
BENEFICIARY
RESPONSIBLE_PARTY
```

selon le vocabulaire réel autorisé par B2.

Le type de relation devra être vérifié contre le schema existant.

---

## 16. Relationship is not ownership

Une erreur majeure serait de considérer :

```text
ContactAssetRelationship
=
ownership
```

alors qu'il peut représenter plusieurs formes de lien.

Donc :

```text
relationship type
```

est essentiel.

Et même :

```text
OWNER
```

est un fait relationnel à une période donnée, pas une caractéristique intrinsèque permanente de l'Asset.

---

## 17. Relationship temporality

Les relations doivent pouvoir être temporelles :

```text
Contact A owns Asset
T1 → T2

Contact B owns same Asset
T2 →
```

ou :

```text
Contact A = owner
Contact B = driver
Contact C = manager
simultaneously
```

Donc B4 doit préserver :

```text
relationship identity
relationship type
effective period
current/historical status
```

selon ce que B2 supporte déjà.

---

## 18. Current relationship uniqueness

B2 possède déjà des contraintes sur certaines relations actives.

B4 doit donner leur sens.

Par exemple, une contrainte peut signifier :

```text
one current active OWNER relationship
```

mais cela ne signifie pas nécessairement :

```text
one Contact relationship total
```

Le service B4 doit comprendre la différence entre :

```text
historical relationship
current relationship
different relationship types
```

---

## 19. Relationship authority

B4 doit répondre :

> Qui a le droit d'affirmer qu'un Contact est lié à un Asset ?

Ce n'est pas nécessairement le Contact lui-même.

Sources possibles :

```text
authenticated declaration
registry evidence
contract evidence
system import
operator assertion
domain runner evidence
previous CPL state
```

Donc :

```text
relationship evidence
≠
relationship authority
```

comme en B3.

---

## 20. Relationship establishment

Une opération future :

```text
attach_contact_to_asset
```

ne doit pas simplement écrire une FK.

Elle doit établir :

```text
Contact exists
Asset exists
relationship type valid
authority present
evidence/provenance present where required
no conflicting active relationship
```

---

## 21. Relationship termination

Les relations ne doivent pas être supprimées pour représenter leur fin.

Il faut plutôt :

```text
ACTIVE
   ↓
ENDED / INACTIVE
```

ou équivalent supporté par B2.

L'histoire doit rester interprétable.

---

## 22. ExternalReference

ExternalReference doit rester distinct de AssetIdentifier.

Probable distinction :

```text
AssetIdentifier
→ identifies the Asset itself

ExternalReference
→ references the Asset/Contact/etc. in another system/context
```

Par exemple :

```text
VIN
= identifier

CRM vehicle record ID
= external reference
```

Il faudra le figer explicitement.

---

## 23. AssetIdentifier vs ExternalReference challenge

Une règle candidate :

```text
Identifier:
  claim about what the Asset IS / how it is identified

ExternalReference:
  claim about where/how the Asset is represented elsewhere
```

Cette distinction est importante car elle affecte :

```text
uniqueness
resolution authority
conflict handling
historical preservation
```

---

## 24. Asset identity conflict

B4 doit prévoir le cas :

```text
VIN A → Asset 1
registration X → Asset 2
new evidence says VIN A + registration X same vehicle
```

Résultat :

```text
CONFLICTING
```

pas :

```text
silently merge Asset 1 and Asset 2
```

Nous aurons probablement besoin, plus tard, d'un mécanisme de reconciliation Asset analogue à B3, mais il faut déterminer si Asset merge appartient réellement à B4.

---

## 25. Asset merge — question ouverte majeure

C'est probablement le premier vrai point de challenge B4.

Deux Assets CPL peuvent représenter le même objet réel.

Exemple :

```text
Asset A created from plate
Asset B created from VIN
later discovered same vehicle
```

Que fait CPL ?

Options :

```text
A. B4 supports Asset merge/reconciliation
B. B4 detects duplicate Asset but merge deferred
C. AssetIdentityResolution handles this without object merge
```

Je ne figerais pas encore la réponse.

Cette question doit être étudiée avant la Requirement Matrix.

---

## 26. Asset identity lifecycle

B4 doit probablement distinguer :

```text
ACTIVE
MERGED?
ARCHIVED?
BLOCKED?
```

selon les états réellement présents dans B2.

Il ne faut pas inventer de nouveaux states avant inspection du modèle canonique.

---

## 27. Operations candidates

Première surface candidate :

```text
Asset
  get_asset
  resolve_asset
  create_asset

Identifiers
  add_asset_identifier
  invalidate_asset_identifier
  resolve_by_identifier

Domain projection
  attach_asset_projection
  get_asset_projection

Relationships
  attach_contact_asset_relationship
  end_contact_asset_relationship
  get_current_asset_relationships
  get_contact_assets

Resolution
  record_asset_identity_resolution
  set_current_asset_resolution

Reconciliation
  (possiblement)
  detect_duplicate_asset
  propose_asset_merge
  merge_assets
  (ce dernier bloc reste UNRESOLVED)
```

---

## 28. B4 must not own downstream diagnostics

B4 ne doit pas faire :

```text
vehicle diagnostics
PGDR reasoning
VIR lookup execution
repair recommendations
vehicle health computation
motorization analysis
DTC analysis
```

Ces systèmes peuvent consommer Asset.

B4 ne devient pas leur moteur.

---

## 29. VIR relation

VIR pourra produire :

```text
vehicle evidence
identifiers
projection data
```

B4 pourra consommer ces résultats.

Mais :

```text
VIR
≠ B4
```

B4 ne doit pas internaliser le moteur VIR.

---

## 30. PGDR relation

PGDR doit recevoir un Asset stable ou une référence compatible.

B4 doit donc rendre possible :

```text
Contact
   ↓ relationship
Asset
   ↓ specialization
VehicleDetail
   ↓
PGDR case
```

sans faire PGDR lui-même.

---

## 31. B4 outcome

À la sortie de B4, CPL doit être capable de répondre :

```text
What Asset is this?
Do we already know this object?
Which identifiers belong to it?
Which identifiers are current, historical or conflicting?
Which external references point to it?
Which domain projection describes it?
Which Contacts are related to it?
In what role?
Which relationships are current?
Which are historical?
What evidence established those relationships?
What is the current identity resolution?
What historical resolutions existed?
```

---

## 32. Preliminary B4 operation families

Je proposerais six familles :

```text
B4-O1  Asset Retrieval / Creation
B4-O2  Asset Identity Resolution
B4-O3  Asset Identifier Lifecycle
B4-O4  Domain Projection
B4-O5  Contact–Asset Relationships
B4-O6  Asset Reconciliation
```

Mais B4-O6 doit être challengé avant freeze.

---

## 33. Core invariants candidates

**B4-I01 — Asset is canonical**
An AssetIdentifier does not replace Asset.

**B4-I02 — Identifier is evidence**
An identifier contributes to Asset identity but does not automatically own it.

**B4-I03 — Mutable identifier ≠ mutable Asset identity**
Changing an external identifier does not automatically create a new Asset.

**B4-I04 — Resolution precedes creation where identity evidence exists**
B4 must avoid uncontrolled duplicate Asset creation.

**B4-I05 — Domain projection is specialization**
VehicleDetail does not become a parallel canonical vehicle identity.

**B4-I06 — Relationship ≠ identity**
Contact–Asset relationship does not define the Asset itself.

**B4-I07 — Relationship history survives**
Ending or changing a relationship does not erase historical association.

**B4-I08 — Relationship authority is governed**
Evidence or declaration alone does not necessarily authorize the relationship.

**B4-I09 — Current and historical identity conclusions are distinct**
A current resolution does not erase previous resolutions.

**B4-I10 — ExternalReference ≠ AssetIdentifier**
Cross-system reference and identity-bearing identifier remain distinguishable.

**B4-I11 — Domain systems do not own CPL Asset identity**
VIR, PGDR and future systems contribute evidence or consume Asset; they do not redefine CPL identity independently.

---

## 34. B4 scope candidate

### B4 IN

```text
canonical Asset retrieval
Asset controlled creation
Asset identity resolution
AssetIdentifier lifecycle
ExternalReference semantics relevant to Asset identity
current/historical Asset resolution
domain projection binding
Contact–Asset relationship lifecycle
relationship authority/evidence semantics
relationship current/history semantics
identity conflict detection
```

### B4 OUT

```text
VIR implementation
PGDR implementation
diagnostic reasoning
authentication
authorization platform
frontend
Case lifecycle
Runner execution
vehicle repair logic
generic CRM
billing
notifications
```

### B4 UNRESOLVED

```text
Asset merge / duplicate reconciliation execution
```

---

## 35. First canonical B4 definition candidate

> B4 — Assets + Relationships is the CPL capability that establishes canonical persistent Assets from governed identity evidence; manages identifiers, external references, domain projections and current/historical identity resolutions; and governs temporally meaningful relationships between Contacts and Assets without allowing mutable identifiers, domain systems or relationship assertions to become independent CPL Asset identity authority.

---

## 36. Critical next question

Avant de produire l'équivalent du B3 Authority Map, il faut fermer la principale question structurelle de B4 :

> Est-ce que B4 doit seulement détecter qu'Asset A et Asset B semblent représenter le même objet, ou doit-il aussi posséder l'autorité de les fusionner ?

Cette décision affecte :

```text
Asset lifecycle
AssetIdentityResolution
identifiers
VehicleDetail
ContactAssetRelationships
Cases
Runner history
ExternalReferences
PGDR/VIR continuity
```

**End of `CPL — B4 Assets + Relationships — WHAT Definition v0`**
