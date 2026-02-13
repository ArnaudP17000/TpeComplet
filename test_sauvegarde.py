from tpe_manager import GestionnaireTPE, TPE, Regisseur, AccesBackoffice, TypeTPE

print("=== TEST SAUVEGARDE ===")

# Créer un gestionnaire
gestionnaire = GestionnaireTPE()

# Créer un TPE simple
regisseur = Regisseur(prenom="Test", nom="User", telephone="0601020304")
acces_backoffice = AccesBackoffice(actif=False)
type_tpe = TypeTPE(ethernet=False, quatre_cinq_g=True)

tpe = TPE(
    service="Service Test",
    regisseur=regisseur,
    regisseurs_suppleants="",
    cartes_commercant=[123456],
    shop_id=999,
    acces_backoffice=acces_backoffice,
    modele_tpe="Ingenico Desk 5000",
    type_tpe=type_tpe,
    nombre_tpe=1
)

print("✅ TPE créé")

# Ajouter au gestionnaire
if gestionnaire.ajouter_tpe(tpe):
    print("✅ TPE ajouté au gestionnaire")
else:
    print("❌ Échec ajout")

# Tenter la sauvegarde
print("\n📝 Tentative de sauvegarde...")
try:
    if gestionnaire.sauvegarder():
        print("✅ Sauvegarde réussie")
    else:
        print("❌ Sauvegarde échouée")
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

# Tenter le backup JSON
print("\n📝 Tentative de backup JSON...")
try:
    if gestionnaire.backup_json():
        print("✅ Backup JSON réussi")
    else:
        print("❌ Backup JSON échoué")
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

# Vérifier les fichiers
import os
if os.path.exists("tpe_data.pkl"):
    print("✅ Fichier tpe_data.pkl créé")
else:
    print("❌ Fichier tpe_data.pkl manquant")

if os.path.exists("tpe_backup.json"):
    print("✅ Fichier tpe_backup.json créé")
else:
    print("❌ Fichier tpe_backup.json manquant")