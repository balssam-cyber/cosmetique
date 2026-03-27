# CosmoERP - ERP Cosmétique Manufacturing

Système ERP complet pour une entreprise de fabrication cosmétique.

## Structure des apps

- **rnd/** — R&D : Produits, Formulations, Ingrédients, Tests de stabilité
- **production/** — Production : Lots de fabrication, Matières premières, Contrôle qualité
- **stock/** — Stock : Matières, Lots, Mouvements, Alertes
- **purchase/** — Achats : Fournisseurs, Bons de commande, Réceptions
- **sales/** — Ventes : Clients, Commandes, Expéditions, Rapports
- **regulatory/** — Réglementaire : Conformité, RSP, BPF, CPNP, Étiquettes
- **dashboard/** — Tableau de bord : Vue unifiée, Alertes

## Installation

### 1. Prérequis

```bash
Python 3.10+
pip
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate.bat     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations

```bash
python manage.py makemigrations rnd production stock purchase sales regulatory dashboard
python manage.py migrate
```

### 5. Créer un superutilisateur

```bash
python manage.py createsuperuser
# username: admin
# password: admin123
```

### 6. Charger les données de démonstration

```bash
python manage.py create_sample_data
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

Accéder à l'application : http://127.0.0.1:8000

---

## Comptes utilisateurs (après create_sample_data)

| Utilisateur    | Mot de passe | Rôle                |
|----------------|-------------|---------------------|
| admin          | admin123    | Superadmin          |
| scientist1     | cosmo2024   | Scientifique R&D    |
| lab_manager1   | cosmo2024   | Responsable Labo    |
| operator1      | cosmo2024   | Opérateur production|
| warehouse1     | cosmo2024   | Responsable entrepôt|
| purchase1      | cosmo2024   | Responsable achats  |
| regulatory1    | cosmo2024   | Réglementaire       |
| qc1            | cosmo2024   | Technicien CQ       |
| ceo1           | cosmo2024   | PDG                 |

---

## API REST

Accès API : http://127.0.0.1:8000/api/

| Endpoint                      | Description              |
|-------------------------------|--------------------------|
| /api/rnd/products/            | Produits R&D             |
| /api/rnd/formulations/        | Formulations             |
| /api/rnd/ingredients/         | Ingrédients              |
| /api/rnd/stability-tests/     | Tests stabilité          |
| /api/production/batches/      | Lots de production       |
| /api/production/qc-checks/    | Contrôles qualité        |
| /api/stock/materials/         | Matières/Produits        |
| /api/stock/lots/              | Lots de stock            |
| /api/stock/movements/         | Mouvements de stock      |
| /api/purchase/orders/         | Bons de commande         |
| /api/purchase/suppliers/      | Fournisseurs             |
| /api/sales/orders/            | Commandes vente          |
| /api/sales/customers/         | Clients                  |
| /api/regulatory/compliance/   | Conformité               |
| /api/regulatory/safety-reports/| Rapports RSP           |
| /api/dashboard/summary/       | Résumé dashboard         |
| /api/dashboard/alerts/        | Alertes actives          |

---

## Administration Django

http://127.0.0.1:8000/admin/

---

## Fonctionnalités clés

- **Déduction automatique** des stocks lors du lancement d'un lot de production (FIFO par date d'expiration)
- **Mise à jour automatique** du stock lors des réceptions (achats) et expéditions (ventes)
- **Alertes temps réel** : stock faible, lots expirants, échecs CQ, échéances réglementaires
- **Contrôles qualité** liés aux lots de production avec résultat global
- **Conformité réglementaire** : RSP, BPF, CPNP, étiquettes
- **Rapports ventes** par produit et par client
- **API REST** complète avec filtres, pagination, authentification

---

## Structure du projet

```
cosmo_erp/
├── cosmo_erp/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── rnd/            # R&D
│   ├── production/     # Production
│   ├── stock/          # Stock
│   ├── purchase/       # Achats
│   ├── sales/          # Ventes
│   ├── regulatory/     # Réglementaire
│   └── dashboard/      # Tableau de bord
├── templates/          # Templates globaux
├── static/             # Fichiers statiques
├── fixtures/           # Données de test
├── requirements.txt
└── manage.py
```
