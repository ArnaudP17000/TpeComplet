from tpe_manager import TPE, Regisseur, AccesBackoffice, TypeTPE

# Test simple
regisseur = Regisseur(prenom="Test", nom="Test", telephone="0600000000")
acces = AccesBackoffice(actif=False)
type_tpe = TypeTPE(quatre_cinq_g=True)

tpe = TPE(
    service="Test",
    regisseur=regisseur,
    regisseurs_suppleants="",
    carte_commercant=123,
    shop_id=999,
    acces_backoffice=acces,
    modele_tpe="Test",
    type_tpe=type_tpe,
    nombre_tpe=5
)

print(f"✅ TPE créé avec nombre_tpe = {tpe.nombre_tpe}")