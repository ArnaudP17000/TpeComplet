#!/usr/bin/env python3
"""
Lanceur pour l'application de Gestion des TPE
Application de bureau - Interface graphique Tkinter
"""

import sys
import os

# Vérifier la version de Python
if sys.version_info < (3, 7):
    print("❌ Python 3.7 ou supérieur est requis")
    print(f"   Version actuelle: {sys.version}")
    sys.exit(1)

# Vérifier que openpyxl est installé
try:
    import openpyxl
except ImportError:
    print("❌ Dépendance manquante: openpyxl")
    print("   Installez les dépendances avec: pip install -r requirements.txt")
    sys.exit(1)

# Vérifier que tkinter est disponible
try:
    import tkinter
except ImportError:
    print("❌ Tkinter n'est pas installé")
    print("   Sur Ubuntu/Debian: sudo apt-get install python3-tk")
    print("   Sur Fedora: sudo dnf install python3-tkinter")
    print("   Sur macOS: Tkinter est inclus avec Python")
    sys.exit(1)

print("🚀 Lancement de l'application TPE Manager...")
print("   Application de bureau - Interface graphique")
print()

# Importer et lancer l'application
try:
    import tpe_gui
    tpe_gui.main()
except Exception as e:
    print(f"❌ Erreur lors du lancement: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
