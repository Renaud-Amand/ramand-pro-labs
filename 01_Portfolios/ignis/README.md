# 🚒 IGNIS — Système IA de transmission d'incidents industriels

> **Statut** : 🟡 Sprint 0 — En construction  
> **Stack** : Claude API · n8n · Supabase · LlamaParse · PWA  
> **Domaine** : Sécurité industrielle · Sites Seveso seuil haut

---

## Le problème — vécu sur le terrain

J'ai été pompier interne sur un site industriel classé Seveso seuil haut pendant 2 ans.

Quand une alarme se déclenchait, voilà ce qui se passait :

1. **Sonnerie dans la caserne.** L'équipe part.
2. **Radio.** "Fuite signalée zone 3." C'est tout.
3. **En route vers l'incident** — sans savoir le produit exact, la quantité, les risques, les accès disponibles.
4. **Le chef de garde, seul la nuit**, gère simultanément : son équipe sur le terrain, les appels à la direction en astreinte, l'accueil des pompiers du SDIS.
5. **Le SDIS arrive.** Briefing verbal au poste de garde. 5 à 15 minutes perdues. L'info est incomplète. L'interlocuteur est sous stress.

> **Le problème n'est pas l'absence d'information. C'est que l'information fiable arrive trop tard, de façon fragmentée, au moment où le stress cognitif est au maximum.**

---

## La solution — IGNIS

Un système IA qui, dès le déclenchement d'une alarme :

1. **Génère une fiche incident structurée en < 30 secondes**
   - Type d'incident · Produit · Quantité · Zone · Risques · EPI requis · Actions immédiates

2. **Diffuse simultanément** à tous les acteurs
   - Équipe interne · Direction en astreinte · **Tablette du chef d'agrès SDIS**

3. **Se met à jour en temps réel**
   - Le chef de garde modifie la situation → tout le monde reçoit la mise à jour horodatée

---

## Architecture

```
[Déclenchement alarme]
         │
         ▼
[IGNIS — Agent Claude]
         │
    ┌────┴──────────────────┐
    ▼                       ▼
[Génération fiche]    [RAG sur FDS — Supabase pgvector]
         │
    ┌────┴──────────────────────┐
    ▼           ▼               ▼
[Tablette SDIS] [SMS Direction] [Salle contrôle]
```

**Décisions clés :**
- **n8n** pour l'orchestration (pas de code requis, workflows visuels)
- **Claude API** pour la génération structurée et le RAG sur les FDS
- **PWA** pour l'interface SDIS (fonctionne sur toute tablette sans installation)
- **RAG plutôt que fine-tuning** : les FDS changent régulièrement, le RAG permet la mise à jour en temps réel

---

## Progression

| Sprint | Objectif | Statut |
|---|---|---|
| Sprint 0 | Setup environnement (Docker, n8n, Supabase, GitHub) | 🟡 En cours |
| Sprint 1 | Pipeline ingestion FDS (PDF → chunks → vectors) | ⬜ À faire |
| Sprint 2 | Génération fiche incident < 30 sec | ⬜ À faire |
| Sprint 3 | Diffusion multi-destinataires (SMS + webhook) | ⬜ À faire |
| Sprint 4 | Mises à jour temps réel | ⬜ À faire |
| Sprint 5 | Démo live + documentation complète | ⬜ À faire |

---

## Structure du projet

```
ignis/
├── README.md               → Cette page
├── docs/
│   ├── PRD.md              → Product Requirements Document complet
│   ├── roadmap.md          → Grandes phases de build
│   └── architecture.png    → Schéma Excalidraw (à venir)
├── workflows/              → Exports n8n (JSON) — ajoutés au fur et à mesure
└── prompts/                → System prompts de l'agent IGNIS documentés
```

---

## Pourquoi ce projet est unique

Aucun dev pur ne peut concevoir ça correctement sans avoir vécu l'environnement.

- **Le format de la fiche** est calqué sur les réflexes réels d'une intervention
- **La priorité des infos** (EPI en premier, actions ensuite) vient du terrain
- **Le mode dégradé offline** est pensé pour les zones à réseau instable — réalité des sites industriels
- **La contrainte ATEX** (zones explosives interdites aux smartphones) est intégrée dès la conception

---

## Suivi complet du projet

→ [PRD IGNIS sur Notion](https://www.notion.so/31e93a938f16818e8190d154adac0524)  
→ [Roadmap Technique](https://www.notion.so/31e93a938f1681bf9167d52cf8cf97de)  
→ [Sprint Board](https://www.notion.so/1549ca0ed2b2488e954c5183a01c71d6)

---

*Projet construit dans le cadre d'une reconversion vers l'architecture IA — [voir le profil complet](../../README.md)*
