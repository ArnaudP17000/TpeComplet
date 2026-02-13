# Module de Gestion des T.P.E. (Terminaux de Paiement Électronique)

## 📋 Description

Application de bureau Python (Tkinter) pour la gestion complète des Terminaux de Paiement Électronique.

**Note importante:** Cette application est une application de bureau native qui s'exécute directement sur votre machine. Elle ne nécessite pas Docker ni de serveur web.

## 🚀 Installation et Démarrage

### 1. Prérequis
- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### 2. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancement de l'application

```bash
python tpe_gui.py
```

L'application s'ouvrira dans une fenêtre de bureau avec une interface graphique complète.

## 📊 Fonctionnalités

### ✅ Champs de gestion
- **Service**: Zone de saisie texte
- **Régisseur**: Prénom, Nom, Téléphone
- **Régisseurs Suppléants**: Zone de saisie texte
- **Carte Commerçant**: Champ numérique
- **ShopID**: Champ numérique (identifiant unique)
- **Accès Backoffice**: Case à cocher + champ email
- **Modèle de TPE**: Champ alphanumérique
- **Type de TPE**: 
  - Case à cocher Ethernet
  - Case à cocher 4/5G
  - Si Ethernet: champs IP, Masque DNS, Passerelle

### 🔧 Fonctions principales

#### 1. Gestion des TPE
```python
from tpe_manager import GestionnaireTPE

gestionnaire = GestionnaireTPE()

# Ajouter un TPE
gestionnaire.ajouter_tpe(tpe)

# Rechercher un TPE
tpe = gestionnaire.rechercher_tpe(shop_id=1001)

# Modifier un TPE
gestionnaire.modifier_tpe(shop_id=1001, nouveau_tpe)

# Supprimer un TPE
gestionnaire.supprimer_tpe(shop_id=1001)

# Lister tous les TPE
tpes = gestionnaire.lister_tpes()
```

#### 2. Export Excel (.xlsx)
```python
# Export au format Excel
gestionnaire.exporter_excel("mon_export.xlsx")
```

Le fichier Excel généré contient:
- En-têtes formatés avec couleur et style
- Toutes les données structurées
- Colonnes auto-ajustées
- Format professionnel

#### 3. Sauvegarde et Restauration
```python
# Sauvegarde binaire (pickle) - rapide et efficace
gestionnaire.sauvegarder("ma_sauvegarde.pkl")
gestionnaire.restaurer("ma_sauvegarde.pkl")

# Sauvegarde JSON - lisible et portable
gestionnaire.backup_json("mon_backup.json")
gestionnaire.restaurer_json("mon_backup.json")
```

#### 4. Statistiques
```python
stats = gestionnaire.statistiques()
# Retourne: total_tpes, type_ethernet, type_4_5g, backoffice_actifs
```

## 💻 Exemple d'utilisation

```python
from tpe_manager import (
    GestionnaireTPE, TPE, Regisseur, AccesBackoffice,
    TypeTPE, ConfigurationReseau
)

# 1. Créer un gestionnaire
gestionnaire = GestionnaireTPE()

# 2. Créer un régisseur
regisseur = Regisseur(
    prenom="Jean",
    nom="Dupont",
    telephone="0601020304"
)

# 3. Configurer le réseau (si Ethernet)
config_reseau = ConfigurationReseau(
    adresse_ip="192.168.1.100",
    masque="255.255.255.0",
    passerelle="192.168.1.1"
)

# 4. Définir le type de TPE
type_tpe = TypeTPE(
    ethernet=True,
    quatre_cinq_g=False,
    config_reseau=config_reseau
)

# 5. Configurer l'accès backoffice
acces_backoffice = AccesBackoffice(
    actif=True,
    email="jean.dupont@entreprise.fr"
)

# 6. Créer le TPE
tpe = TPE(
    service="Service Comptabilité",
    regisseur=regisseur,
    regisseurs_suppleants="Marie Martin, Pierre Durand",
    carte_commercant=123456789,
    shop_id=1001,
    acces_backoffice=acces_backoffice,
    modele_tpe="Ingenico iWL250",
    type_tpe=type_tpe
)

# 7. Ajouter le TPE
gestionnaire.ajouter_tpe(tpe)

# 8. Exporter
gestionnaire.exporter_excel("tpe_export.xlsx")

# 9. Sauvegarder
gestionnaire.sauvegarder()
```

## 🔒 Validations incluses

- ✅ Validation des adresses IP (format et plages)
- ✅ Validation des emails
- ✅ Vérification de l'unicité des ShopID
- ✅ Validation des champs numériques
- ✅ Configuration réseau obligatoire si Ethernet sélectionné
- ✅ Gestion des erreurs complète

## 📁 Structure des fichiers

```
.
├── tpe_manager.py          # Module principal
├── exemple_utilisation.py  # Exemples d'utilisation
├── requirements.txt        # Dépendances Python
├── README.md              # Ce fichier
├── tpe_data.pkl           # Sauvegarde binaire (généré)
├── tpe_backup.json        # Sauvegarde JSON (généré)
└── tpe_export.xlsx        # Export Excel (généré)
```

## 🎯 Points forts du module

1. **Architecture orientée objet**: Code structuré et maintenable
2. **Validation robuste**: Tous les champs sont validés
3. **Double système de sauvegarde**: Pickle (rapide) et JSON (lisible)
4. **Export Excel professionnel**: Formatage et mise en page
5. **Gestion d'erreurs complète**: Toutes les opérations sont sécurisées
6. **Documentation complète**: Docstrings et commentaires
7. **Type hints**: Code moderne avec annotations de types
8. **Extensible**: Facile d'ajouter de nouvelles fonctionnalités

## 🧪 Tests

Pour tester le module:

```bash
python exemple_utilisation.py
```

Cela créera:
- 3 TPE d'exemple
- Un export Excel
- Des fichiers de sauvegarde
- Affichera les statistiques

## 📞 Support

Module créé selon les spécifications demandées pour la gestion des TPE.
Toutes les fonctionnalités requises sont implémentées et testées.
