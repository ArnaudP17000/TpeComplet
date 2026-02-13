from tpe_manager import TPE, Regisseur, AccesBackoffice, TypeTPE, GestionnaireTPE

print("=== TEST AJOUT TPE ===")

# Créer un gestionnaire
gestionnaire = GestionnaireTPE()

# Créer un régisseur
regisseur = Regisseur(
    prenom="Jean",
    nom="Dupont",
    telephone="0601020304"
)

# Type de TPE
type_tpe = TypeTPE(
    ethernet=False,
    quatre_cinq_g=True,
    config_reseau=None
)

# Accès backoffice
acces_backoffice = AccesBackoffice(
    actif=False,
    email=None
)

# Créer le TPE
tpe = TPE(
    service="Test Service",
    regisseur=regisseur,
    regisseurs_suppleants="Marie Martin",
    carte_commercant=123456,
    shop_id=999,
    acces_backoffice=acces_backoffice,
    modele_tpe="Ingenico iWL250",
    type_tpe=type_tpe,
    nombre_tpe=3
)

print(f"✅ TPE créé: ShopID={tpe.shop_id}, Nombre TPE={tpe.nombre_tpe}")

# Ajouter au gestionnaire
if gestionnaire.ajouter_tpe(tpe):
    print("✅ TPE ajouté au gestionnaire avec succès")
else:
    print("❌ Échec de l'ajout")

# Vérifier
tpes = gestionnaire.lister_tpes()
print(f"📊 Nombre de TPE dans le gestionnaire: {len(tpes)}")

if len(tpes) > 0:
    print(f"✅ Premier TPE: ShopID={tpes[0].shop_id}, Nombre={tpes[0].nombre_tpe}")