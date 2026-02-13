from tpe_manager import GestionnaireTPE, TPE, Regisseur, AccesBackoffice, TypeTPE, ConfigurationReseau

print("Démarrage de la gestion des TPE...")

# Créer un gestionnaire
gestionnaire = GestionnaireTPE()

# Créer un régisseur
regisseur = Regisseur(
    prenom="Jean",
    nom="Dupont",
    telephone="0601020304"
)

# Créer un TPE simple (sans Ethernet)
type_tpe = TypeTPE(
    ethernet=False,
    quatre_cinq_g=True,
    config_reseau=None
)

acces_backoffice = AccesBackoffice(
    actif=True,
    email="jean.dupont@mairie.fr"
)

tpe = TPE(
    service="Service Comptabilité",
    regisseur=regisseur,
    regisseurs_suppleants="Marie Martin",
    carte_commercant=123456789,
    shop_id=1001,
    acces_backoffice=acces_backoffice,
    modele_tpe="Ingenico iWL250",
    type_tpe=type_tpe
)

# Ajouter le TPE
if gestionnaire.ajouter_tpe(tpe):
    print(f"✓ TPE ajouté avec succès - ShopID: {tpe.shop_id}")

# Afficher les statistiques
stats = gestionnaire.statistiques()
print(f"\nStatistiques:")
print(f"  Total TPE: {stats['total_tpes']}")

# Exporter en Excel
gestionnaire.exporter_excel("mes_tpe.xlsx")
print("\n✓ Export Excel créé: mes_tpe.xlsx")

# Sauvegarder
gestionnaire.sauvegarder()
print("✓ Sauvegarde créée: tpe_data.pkl")

print("\n🎉 Terminé !")