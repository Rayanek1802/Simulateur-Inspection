# Simulateur Inspection

Interface d'évaluation pour instructeurs simulateur permettant la gestion et l'évaluation des séances de formation.

## Fonctionnalités

- Création de séances d'évaluation
- Prise de notes en temps réel
- Association automatique des notes aux OBs
- Calcul automatique des notes HOW MANY & HOW OFTEN
- Génération de rapports de séance

## Structure du Projet

```
.
├── backend/            # API FastAPI
│   ├── app/           # Code source backend
│   ├── tests/         # Tests unitaires
│   └── requirements.txt
└── frontend/          # Application React
    └── src/          # Code source frontend
```

## Installation

### Backend (Python 3.8+)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Unix
# ou
.\venv\Scripts\activate  # Sur Windows
pip install -r requirements.txt
```

### Frontend (Node.js 16+)

```bash
cd frontend
npm install
```

## Démarrage

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm start
```

## Compétences Évaluées

- PRO (Application of Procedures & Compliance with Regulations)
- COM (Communication)
- FPA (Flight Path Management – Automation)
- FPM (Flight Path Management – Manual Control)

## Système de Notation

### HOW MANY (% d'OBs observées)
- ≥ 80% : 1
- ≥ 60% : 2
- ≥ 40% : 3
- ≥ 20% : 4
- < 20% : 5

### HOW OFTEN (fréquence moyenne)
- ≥ 5 fois : 1
- 4 fois : 2
- 3 fois : 3
- 2 fois : 4
- 1 ou 0 fois : 5 