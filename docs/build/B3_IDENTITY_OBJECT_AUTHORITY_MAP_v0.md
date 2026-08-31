# CPL — B3 Identity Object & Authority Map v0

**System:** VIR PGDR # COMMON PRODUCT LAYER — CPL
**Phase:** B3 — Identity + Accounts (WHAT, pre-Requirement-Matrix)
**Version:** v0
**Canonical starting point:** `main` @ `4b83425828a2e8fd08bec568fc8937a830396ec4`
**Depends on:** B2 persistent structures (`cpl.contacts`, `cpl.contact_points`, `cpl.accounts`)
**Status:** ONTOLOGICAL — precedes Requirement Matrix and Execution Mandate

---

## 0. Purpose

Avant de produire une Requirement Matrix pour B3, ce document répond,
pour chaque objet identitaire, à quatre questions fixes :

```text
1. What does it represent?
2. Who may create it?
3. Who may modify it — and what counts as modification vs. new evidence?
4. What can it never prove alone?
```

La quatrième question est la plus importante. C'est elle qui empêche
qu'un objet acquière, par accumulation silencieuse d'usage, une
autorité qu'il n'a jamais été conçu pour porter — c'est exactement le
mode de défaillance que la Section 8 du WHAT Definition (`External
identity ↛ CPL identity`) cherche à interdire structurellement.

Les objets traités : **Observed Identity Evidence**, **Contact
Resolution**, **Contact**, **ContactPoint**, **Account**, **Merge /
MergeCandidate**. Une synthèse d'autorité clôt le document.

---

## 1. Observed Identity Evidence

### Represents
Un fait brut, non interprété, reçu par CPL au sujet d'un acteur —
une adresse email saisie, un `subject` OAuth renvoyé par un provider,
une déclaration de nom, une référence externe. C'est la matière
première de toute résolution ; ce n'est pas encore une structure
persistée dans B2.

### Who may create it
N'importe quelle source amont autorisée à parler à CPL : un flux
d'enregistrement, un callback d'authentification, un import, une
observation VIR/PGDR future. La création d'evidence n'exige **aucune**
autorité identitaire — c'est précisément pour ça qu'elle ne peut rien
prouver seule.

### Who may modify it
Elle n'est pas modifiable. Une evidence est un fait daté et sourcé ;
si le fait change (un email est corrigé), c'est une **nouvelle**
evidence, pas une mutation de l'ancienne. C'est la même discipline que
B2 applique à `ContactPoint.valid_from` / `valid_until` plutôt qu'à un
`UPDATE` destructif — l'historique d'evidence doit rester
reconstituable.

### What it can never prove alone
- Qu'elle correspond à un `Contact` existant.
- Qu'elle justifie la création d'un `Contact`.
- Qu'elle est exacte (une déclaration n'est pas une vérification —
  voir `ContactPoint.verification_status`).
- Qu'elle provient d'un acteur unique et cohérent dans le temps.

C'est un input à la résolution, jamais une identité.

---

## 2. Contact Resolution

### Represents
Ce n'est pas un objet persisté — c'est **le processus gouverné** qui
transforme de l'evidence en une décision typée :

```text
ResolvedContact
CreatedContact
ContactNotFound
AmbiguousContactResolution
ConflictingIdentityEvidence
```

C'est l'objet central de B3 identifié en Section 3 du WHAT Definition.
Son rôle exact est d'être le seul point du système où de l'evidence
peut légitimement produire — ou refuser de produire — une décision
identitaire.

### Who may create it
Seul un composant B3-A (Contact Resolution) explicitement autorisé
peut invoquer une résolution. Aucune couche amont (B4, un futur
service d'auth, un import batch) ne doit pouvoir contourner la
résolution pour écrire directement un `contact_id` dans ses propres
structures.

### Who may modify it
Une résolution n'est pas modifiable après coup — elle est un
événement, pas un état. Si la même evidence est réévaluée plus tard
(nouvelle donnée disponible), c'est une **nouvelle** résolution, avec
son propre horodatage et son propre résultat, potentiellement
différent du précédent.

### What it can never prove alone
- Qu'une résolution `AmbiguousContactResolution` doit être
  automatiquement tranchée — l'ambiguïté est un état légitime, pas une
  erreur à corriger silencieusement.
- Qu'un `ConflictingIdentityEvidence` autorise une fusion — voir
  Section 6 (Merge), qui exige une autorité séparée.
- Qu'une résolution répétée avec succès équivaut à une vérification —
  la résolution répond « qui est-ce probablement », pas « est-ce
  prouvé ».

---

## 3. Contact

### Represents
L'identité CPL persistante d'un acteur, `PERSON` ou `ORGANIZATION` —
la structure `cpl.contacts` que B2 a matérialisée : `contact_id`,
`contact_type`, `contact_status`, `merged_into_id`, `record_version`.
C'est l'ancrage stable auquel B4 pourra plus tard rattacher des
Assets.

### Who may create it
Uniquement le résultat d'une `Contact Resolution` explicitement
autorisée à créer (voir Section 10 du WHAT Definition : explicit /
implicit / provisional creation). Jamais une écriture directe issue
d'un import, d'un provider externe, ou d'une observation VIR/PGDR.

### Who may modify it
- `display_name`, `first_name`, `last_name` : modifiables par des
  processus B3 autorisés, avec `updated_at` et `record_version`
  incrémentés (optimistic concurrency, déjà posée en B2).
- `contact_status` : transitions gouvernées uniquement — en
  particulier le passage à `MERGED` n'est légitime que via le
  mécanisme de Merge (Section 6), jamais par une mise à jour libre.
- `contact_id` : immuable, toujours.

### What it can never prove alone
- Qu'il est authentifiable — un `Contact` n'a pas de mot de passe, pas
  de session ; c'est `Account` qui porte cette relation.
- Qu'il est joignable — c'est `ContactPoint` qui porte les moyens de
  contact, et seulement ceux qui sont `VERIFIED`.
- Qu'il est unique dans le système — B2 prévoit explicitement
  `contacts_merged_target_required_chk` précisément parce que la
  duplication est un état anticipé, pas une anomalie impossible.
- Qu'il représente un acteur réel vérifié — un `Contact` peut être
  `provisional` (Section 10) sans qu'aucune vérification n'ait encore
  eu lieu.

---

## 4. ContactPoint

### Represents
Un canal de contact observable — `EMAIL` ou `PHONE` — rattaché à un
`Contact`, avec son propre cycle de vérification :
`verification_status` (`UNVERIFIED`, `PENDING`, `VERIFIED`, `FAILED`,
`REVOKED`), `is_primary`, `valid_from`/`valid_until`. C'est de
l'evidence de contact *devenue persistante*, mais elle reste
distincte de l'identité elle-même — Section 2 du WHAT Definition
l'affirme explicitement : `email ≠ Contact`.

### Who may create it
Tout processus B3-B autorisé, rattaché à un `Contact` déjà résolu ou
créé. Un `ContactPoint` ne peut jamais exister sans `contact_id` —
c'est la contrainte `contact_points_contact_fk` de B2, déjà vérifiée
(`N05 — reject orphan ContactPoint`).

### Who may modify it
- Le passage `UNVERIFIED → PENDING → VERIFIED` (ou `FAILED`) suit un
  protocole de vérification propre à B3-B, pas une simple mise à jour
  de champ.
- `is_primary` : au plus un `ContactPoint` actif par
  `(contact_id, point_type)` — déjà contraint en B2 via l'index
  unique partiel `contact_points_one_active_primary_idx`.
- La révocation (`REVOKED`) ferme le canal sans le supprimer —
  l'historique reste consultable, exactement comme B2 le prévoit.

### What it can never prove alone
- Qu'il appartient réellement à l'acteur déclaré — un email
  `UNVERIFIED` est une simple affirmation.
- Qu'un `ContactPoint` `VERIFIED` prouve l'identité complète du
  `Contact` — il prouve seulement la possession du canal à un instant
  donné.
- Qu'il reste valide indéfiniment — la vérification a une portée
  temporelle, pas une garantie permanente (d'où `valid_until`).

---

## 5. Account

### Represents
Le rattachement d'une identité fournie par un système
d'authentification externe (`auth_provider`, `provider_subject_id`) à
un `Contact` CPL — structure B2 `cpl.accounts`, avec
`account_status` (`PENDING`, `ACTIVE`, `DISABLED`, `REVOKED`) et la
contrainte d'unicité `(auth_provider, provider_subject_id)`.

### Who may create it
Un processus B3-C (`attach_account`), toujours en résolvant d'abord
un `Contact` — jamais en laissant le provider externe dicter
directement l'identité CPL. C'est l'invariant central de la Section 8
du WHAT Definition :

```text
External identity → evidence → CPL Account → relation → CPL Contact
        (jamais l'inverse)
```

### Who may modify it
- `account_status` : transitions gouvernées
  (`disable_account`, `revoke_account`) — la Section 11 du WHAT
  Definition l'affirme explicitement : la suppression physique n'est
  pas le mécanisme normal de révocation.
- `last_authenticated_at` : mis à jour à chaque authentification
  réussie, sans changer d'autorité.
- Le lien `contact_id` d'un `Account` ne devrait normalement **jamais**
  changer une fois attaché — un ré-attachement à un autre `Contact`
  est un événement d'identité majeur, pas une mise à jour de routine,
  et devrait suivre une gouvernance au moins aussi stricte qu'un merge.

### What it can never prove alone
- Que le `Contact` associé est correct — un `Account` peut être
  attaché par erreur ; c'est justement pour ça que le lien
  `contact_id` doit rester rare à modifier plutôt que trivialement
  réassignable.
- Qu'il représente une personne réelle unique — un même acteur peut
  avoir plusieurs `Account` (plusieurs providers) légitimement
  rattachés au même `Contact`, comme le prévoit déjà B2 (aucune
  contrainte d'unicité `Contact ↔ Account` un-à-un).
- Que `ACTIVE` signifie authentifié *maintenant* — c'est un état de
  rattachement, pas une session ; B3 exclut explicitement les
  sessions et le JWT (Section 14 du WHAT Definition).

---

## 6. Merge / MergeCandidate

### Represents
`MergeCandidate` est une **détection** — un signal que deux `Contact`
pourraient représenter le même acteur. `Merge` est l'**exécution
gouvernée** de la réconciliation. La Section 5 du WHAT Definition
insiste : `MergeCandidate ≠ Contact merged` ; ce sont deux autorités
distinctes.

### Who may create it (MergeCandidate)
Tout processus B3-D (`detect_duplicate_contact`) peut *proposer* un
candidat. La détection est peu coûteuse en autorité — elle ressemble
à l'Evidence de la Section 1 : elle peut être produite largement,
précisément parce qu'elle ne décide rien seule.

### Who may create it (Merge exécuté)
Seule une autorité de réconciliation explicitement habilitée
(`merge_contacts`) peut transformer un `MergeCandidate` en fusion
réelle. C'est l'endroit du système où l'erreur est la plus coûteuse —
Section 13 du WHAT Definition liste ce qu'une fusion doit préserver :
`source Contact, target Contact, reason, evidence, authority, time,
previous relationships, previous accounts, previous contact points,
traceability`.

### Who may modify it
Une fusion exécutée n'est pas modifiable — elle est déjà, par
construction, un événement historique irréversible dans son
occurrence (même si `contact_status = MERGED` peut théoriquement être
contesté par une gouvernance ultérieure, ce serait une nouvelle
décision, pas une correction de l'ancienne). B2 a déjà posé le socle
mécanique exact :

```text
contacts_not_self_merged_chk
  (merged_into_id <> contact_id)

contacts_merged_target_required_chk
  (contact_status = 'MERGED' ⇒ merged_into_id IS NOT NULL)
```

et B3 doit construire la sémantique gouvernée *au-dessus*, pas la
recréer.

### What it can never prove alone
- Qu'un `MergeCandidate` à haute confiance doit être fusionné
  automatiquement — la confiance de détection et l'autorité
  d'exécution restent séparées par conception.
- Qu'une fusion exécutée efface le besoin de traçabilité — au
  contraire, c'est l'endroit où la traçabilité est la plus critique.
- Que fusionner deux `Contact` fusionne silencieusement leurs
  `Account` et `ContactPoint` sans décision explicite sur les
  conflits (deux `ContactPoint` `is_primary` du même type, par
  exemple, ne peuvent pas coexister après fusion sans arbitrage).

---

## 7. Authority Synthesis

| Objet | Autorité de création | Autorité de modification | Ne prouve jamais seul |
|---|---|---|---|
| Observed Identity Evidence | N'importe quelle source amont | Immuable (nouvelle evidence, pas de mutation) | Une identité CPL |
| Contact Resolution | Composant B3-A uniquement | Immuable (nouvelle résolution) | Qu'une ambiguïté doit être tranchée |
| Contact | Résultat d'une résolution autorisée | B3, transitions gouvernées, jamais `MERGED` hors merge | Authentifiabilité, joignabilité, unicité, réalité vérifiée |
| ContactPoint | B3-B, toujours rattaché à un Contact | Cycle de vérification propre, jamais suppression physique | Possession réelle, validité permanente |
| Account | B3-C, après résolution d'un Contact | États gouvernés ; lien `contact_id` rarement réassigné | Exactitude du rattachement, unicité de personne, session active |
| MergeCandidate | Large (détection B3-D) | Immuable une fois exécuté | Que la détection = l'autorisation |

### Direction d'autorité globale

```text
Observed Identity Evidence
        ↓ (jamais suffisant seul)
Contact Resolution
        ↓ (décision typée, gouvernée)
Contact  ←—————— Account (via attach, jamais l'inverse)
   ↕
ContactPoint (evidence de contact, jamais l'identité elle-même)
   ↕
MergeCandidate → [autorité séparée] → Merge exécuté
```

Aucune flèche ne remonte silencieusement. Un provider externe, un
`ContactPoint`, ou une détection de doublon peuvent tous *proposer*,
jamais *décider* seuls.

---

## 8. Ce que ce document ferme

Avec cette carte, les huit objets listés en Section 19 du WHAT
Definition ont chacun une réponse explicite aux quatre questions
fixées en Section 0. Ce qui reste délibérément **non fermé**, et
appartient à la Requirement Matrix à venir :

```text
- les seuils de confiance exacts de Contact Resolution
- le format précis des règles de détection de MergeCandidate
- les rôles/acteurs système autorisés à invoquer chaque fonction B3-A/B/C/D
- les schémas de payload pour chaque type de sortie (ResolvedContact, etc.)
- les cas limites de fusion (conflits ContactPoint primary, comptes multiples)
```

Ce document ne prescrit pas encore *comment* implémenter ces
mécanismes — il fixe *qui a le droit de décider quoi*, pour que
l'implémentation ne puisse pas, par accident, inverser une direction
d'autorité.

**End of `CPL — B3 Identity Object & Authority Map v0`**
