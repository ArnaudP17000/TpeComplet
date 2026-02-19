"""
⚠️ FICHIER OBSOLÈTE - NE PAS UTILISER
Ce fichier est une ancienne version de l'interface, remplacée par tpe_gui.py (v1.5).
Il sera supprimé lors d'un prochain nettoyage.
"""

"""
Interface Graphique pour la Gestion des Terminaux de Paiement Électronique (T.P.E.)
Utilise Tkinter pour l'interface utilisateur
Version 1.1 - Ajout du champ "Nombre de TPE"
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tpe_manager import (
    GestionnaireTPE, TPE, Regisseur, AccesBackoffice,
    TypeTPE, ConfigurationReseau
)
import os


class TPEInterface:
    """Interface graphique principale pour la gestion des TPE"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Terminaux de Paiement Électronique (T.P.E.)")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        
        # Gestionnaire TPE
        self.gestionnaire = GestionnaireTPE()
        
        # Charger les données existantes si disponibles
        if os.path.exists("tpe_data.pkl"):
            self.gestionnaire.restaurer()
        
        # Configuration du style
        self.configurer_style()
        
        # Création de l'interface
        self.creer_interface()
        
        # Rafraîchir la liste
        self.rafraichir_liste()
    
    def configurer_style(self):
        """Configure le style de l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs
        style.configure('Titre.TLabel', font=('Arial', 16, 'bold'), foreground='#0066CC')
        style.configure('SousTitre.TLabel', font=('Arial', 11, 'bold'))
        style.configure('Bouton.TButton', font=('Arial', 10))
        style.configure('Treeview', rowheight=25)
    
    def creer_interface(self):
        """Crée l'interface principale"""
        # Titre principal
        titre_frame = ttk.Frame(self.root, padding="10")
        titre_frame.pack(fill=tk.X)
        
        ttk.Label(
            titre_frame,
            text="🏦 Gestion des Terminaux de Paiement Électronique",
            style='Titre.TLabel'
        ).pack()
        
        # Frame principal avec deux colonnes
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Colonne gauche : Liste des TPE
        left_frame = ttk.LabelFrame(main_frame, text="Liste des TPE", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.creer_liste_tpe(left_frame)
        
        # Colonne droite : Formulaire
        right_frame = ttk.LabelFrame(main_frame, text="Formulaire TPE", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.creer_formulaire(right_frame)
        
        # Frame du bas : Boutons d'action
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.creer_boutons_action(bottom_frame)
    
    def creer_liste_tpe(self, parent):
        """Crée la liste des TPE"""
        # Frame pour la barre de recherche
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Recherche ShopID:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.rechercher_tpe_liste)
        ttk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT)
        
        # Treeview pour afficher les TPE
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Colonnes
        colonnes = ('ShopID', 'Service', 'Régisseur', 'Modèle', 'Nb TPE', 'Type')
        self.tree = ttk.Treeview(tree_frame, columns=colonnes, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # En-têtes
        self.tree.heading('ShopID', text='ShopID')
        self.tree.heading('Service', text='Service')
        self.tree.heading('Régisseur', text='Régisseur')
        self.tree.heading('Modèle', text='Modèle TPE')
        self.tree.heading('Nb TPE', text='Nb TPE')
        self.tree.heading('Type', text='Type Connexion')
        
        # Largeurs
        self.tree.column('ShopID', width=80)
        self.tree.column('Service', width=130)
        self.tree.column('Régisseur', width=130)
        self.tree.column('Modèle', width=100)
        self.tree.column('Nb TPE', width=60)
        self.tree.column('Type', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind pour sélection
        self.tree.bind('<<TreeviewSelect>>', self.on_select_tpe)
        
        # Statistiques
        self.stats_label = ttk.Label(parent, text="", font=('Arial', 9))
        self.stats_label.pack(pady=(10, 0))
    
    def creer_formulaire(self, parent):
        """Crée le formulaire de saisie"""
        # Canvas avec scrollbar pour le formulaire
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variables de formulaire
        self.form_vars = {}
        
        row = 0
        
        # Service
        ttk.Label(scrollable_frame, text="Service *", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.form_vars['service'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['service'], width=40).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Régisseur
        ttk.Label(scrollable_frame, text="Régisseur *", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(scrollable_frame, text="Prénom:").grid(row=row, column=0, sticky=tk.W)
        self.form_vars['regisseur_prenom'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseur_prenom'], width=40).grid(row=row, column=1, sticky=tk.EW)
        row += 1
        
        ttk.Label(scrollable_frame, text="Nom:").grid(row=row, column=0, sticky=tk.W)
        self.form_vars['regisseur_nom'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseur_nom'], width=40).grid(row=row, column=1, sticky=tk.EW)
        row += 1
        
        ttk.Label(scrollable_frame, text="Téléphone:").grid(row=row, column=0, sticky=tk.W)
        self.form_vars['regisseur_tel'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseur_tel'], width=40).grid(row=row, column=1, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Régisseurs Suppléants
        ttk.Label(scrollable_frame, text="Régisseurs Suppléants", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.form_vars['regisseurs_suppleants'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseurs_suppleants'], width=40).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Carte Commerçant
        ttk.Label(scrollable_frame, text="Carte Commerçant * (numérique)", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.form_vars['carte_commercant'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['carte_commercant'], width=40).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # ShopID
        ttk.Label(scrollable_frame, text="ShopID * (numérique unique)", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.form_vars['shop_id'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['shop_id'], width=40).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Nombre de TPE (NOUVEAU CHAMP)
        ttk.Label(scrollable_frame, text="Nombre de TPE * (numérique)", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.form_vars['nombre_tpe'] = tk.StringVar(value="1")
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['nombre_tpe'], width=40).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Modèle TPE
        ttk.Label(scrollable_frame, text="Modèle de TPE *", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        self.form_vars['modele_tpe'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['modele_tpe'], width=40).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Accès Backoffice
        ttk.Label(scrollable_frame, text="Accès Backoffice", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.form_vars['backoffice_actif'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Actif", variable=self.form_vars['backoffice_actif'], command=self.toggle_backoffice).grid(row=row, column=0, sticky=tk.W)
        row += 1
        
        ttk.Label(scrollable_frame, text="Email:").grid(row=row, column=0, sticky=tk.W)
        self.form_vars['backoffice_email'] = tk.StringVar()
        self.backoffice_email_entry = ttk.Entry(scrollable_frame, textvariable=self.form_vars['backoffice_email'], width=40, state='disabled')
        self.backoffice_email_entry.grid(row=row, column=1, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Type de TPE
        ttk.Label(scrollable_frame, text="Type de TPE *", style='SousTitre.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.form_vars['type_ethernet'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Ethernet", variable=self.form_vars['type_ethernet'], command=self.toggle_ethernet).grid(row=row, column=0, sticky=tk.W)
        row += 1
        
        self.form_vars['type_4_5g'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="4/5G", variable=self.form_vars['type_4_5g']).grid(row=row, column=0, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Configuration Réseau (si Ethernet)
        self.config_reseau_frame = ttk.LabelFrame(scrollable_frame, text="Configuration Réseau (Ethernet)", padding="5")
        self.config_reseau_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        ttk.Label(self.config_reseau_frame, text="Adresse IP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.form_vars['ip'] = tk.StringVar()
        self.ip_entry = ttk.Entry(self.config_reseau_frame, textvariable=self.form_vars['ip'], width=30, state='disabled')
        self.ip_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(self.config_reseau_frame, text="Masque:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.form_vars['masque'] = tk.StringVar()
        self.masque_entry = ttk.Entry(self.config_reseau_frame, textvariable=self.form_vars['masque'], width=30, state='disabled')
        self.masque_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(self.config_reseau_frame, text="Passerelle:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.form_vars['passerelle'] = tk.StringVar()
        self.passerelle_entry = ttk.Entry(self.config_reseau_frame, textvariable=self.form_vars['passerelle'], width=30, state='disabled')
        self.passerelle_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Boutons du formulaire
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="➕ Ajouter TPE", command=self.ajouter_tpe, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Modifier TPE", command=self.modifier_tpe, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Supprimer TPE", command=self.supprimer_tpe, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Nouveau", command=self.vider_formulaire, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ID TPE sélectionné (pour modification)
        self.tpe_selectionne_id = None
    
    def creer_boutons_action(self, parent):
        """Crée les boutons d'action principaux"""
        ttk.Button(parent, text="📊 Export Excel", command=self.exporter_excel, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(parent, text="💾 Sauvegarder", command=self.sauvegarder, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(parent, text="📂 Restaurer", command=self.restaurer, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(parent, text="📈 Statistiques", command=self.afficher_statistiques, width=20).pack(side=tk.LEFT, padx=5)
    
    def toggle_backoffice(self):
        """Active/désactive le champ email backoffice"""
        if self.form_vars['backoffice_actif'].get():
            self.backoffice_email_entry.config(state='normal')
        else:
            self.backoffice_email_entry.config(state='disabled')
            self.form_vars['backoffice_email'].set('')
    
    def toggle_ethernet(self):
        """Active/désactive les champs de configuration réseau"""
        if self.form_vars['type_ethernet'].get():
            self.ip_entry.config(state='normal')
            self.masque_entry.config(state='normal')
            self.passerelle_entry.config(state='normal')
        else:
            self.ip_entry.config(state='disabled')
            self.masque_entry.config(state='disabled')
            self.passerelle_entry.config(state='disabled')
            self.form_vars['ip'].set('')
            self.form_vars['masque'].set('')
            self.form_vars['passerelle'].set('')
    
    def valider_formulaire(self):
        """Valide les données du formulaire"""
        # Champs obligatoires
        if not self.form_vars['service'].get().strip():
            messagebox.showerror("Erreur", "Le service est obligatoire")
            return False
        
        if not self.form_vars['regisseur_prenom'].get().strip():
            messagebox.showerror("Erreur", "Le prénom du régisseur est obligatoire")
            return False
        
        if not self.form_vars['regisseur_nom'].get().strip():
            messagebox.showerror("Erreur", "Le nom du régisseur est obligatoire")
            return False
        
        if not self.form_vars['regisseur_tel'].get().strip():
            messagebox.showerror("Erreur", "Le téléphone du régisseur est obligatoire")
            return False
        
        # Validation carte commerçant
        try:
            carte = int(self.form_vars['carte_commercant'].get())
            if carte < 0:
                raise ValueError()
        except:
            messagebox.showerror("Erreur", "La carte commerçant doit être un nombre positif")
            return False
        
        # Validation ShopID
        try:
            shop_id = int(self.form_vars['shop_id'].get())
            if shop_id < 0:
                raise ValueError()
        except:
            messagebox.showerror("Erreur", "Le ShopID doit être un nombre positif")
            return False
        
        # Validation Nombre de TPE
        try:
            nombre_tpe = int(self.form_vars['nombre_tpe'].get())
            if nombre_tpe < 1:
                raise ValueError()
        except:
            messagebox.showerror("Erreur", "Le nombre de TPE doit être au minimum 1")
            return False
        
        if not self.form_vars['modele_tpe'].get().strip():
            messagebox.showerror("Erreur", "Le modèle de TPE est obligatoire")
            return False
        
        # Validation type connexion
        if not self.form_vars['type_ethernet'].get() and not self.form_vars['type_4_5g'].get():
            messagebox.showerror("Erreur", "Sélectionnez au moins un type de connexion (Ethernet ou 4/5G)")
            return False
        
        # Validation configuration réseau si Ethernet
        if self.form_vars['type_ethernet'].get():
            if not self.form_vars['ip'].get().strip() or \
               not self.form_vars['masque'].get().strip() or \
               not self.form_vars['passerelle'].get().strip():
                messagebox.showerror("Erreur", "La configuration réseau est obligatoire pour le type Ethernet")
                return False
        
        return True
    
    def ajouter_tpe(self):
        """Ajoute un nouveau TPE"""
        if not self.valider_formulaire():
            return
        
        try:
            # Créer les objets
            regisseur = Regisseur(
                prenom=self.form_vars['regisseur_prenom'].get().strip(),
                nom=self.form_vars['regisseur_nom'].get().strip(),
                telephone=self.form_vars['regisseur_tel'].get().strip()
            )
            
            config_reseau = None
            if self.form_vars['type_ethernet'].get():
                config_reseau = ConfigurationReseau(
                    adresse_ip=self.form_vars['ip'].get().strip(),
                    masque=self.form_vars['masque'].get().strip(),
                    passerelle=self.form_vars['passerelle'].get().strip()
                )
            
            type_tpe = TypeTPE(
                ethernet=self.form_vars['type_ethernet'].get(),
                quatre_cinq_g=self.form_vars['type_4_5g'].get(),
                config_reseau=config_reseau
            )
            
            acces_backoffice = AccesBackoffice(
                actif=self.form_vars['backoffice_actif'].get(),
                email=self.form_vars['backoffice_email'].get().strip() if self.form_vars['backoffice_actif'].get() else None
            )
            
            tpe = TPE(
                service=self.form_vars['service'].get().strip(),
                regisseur=regisseur,
                regisseurs_suppleants=self.form_vars['regisseurs_suppleants'].get().strip(),
                carte_commercant=int(self.form_vars['carte_commercant'].get()),
                shop_id=int(self.form_vars['shop_id'].get()),
                acces_backoffice=acces_backoffice,
                modele_tpe=self.form_vars['modele_tpe'].get().strip(),
                type_tpe=type_tpe,
                nombre_tpe=int(self.form_vars['nombre_tpe'].get())
            )
            
            if self.gestionnaire.ajouter_tpe(tpe):
                messagebox.showinfo("Succès", f"TPE ajouté avec succès !\nShopID: {tpe.shop_id}\nNombre de TPE: {tpe.nombre_tpe}")
                self.rafraichir_liste()
                self.vider_formulaire()
                self.sauvegarder_auto()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout du TPE:\n{str(e)}")
    
    def modifier_tpe(self):
        """Modifie un TPE existant"""
        if self.tpe_selectionne_id is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un TPE à modifier")
            return
        
        if not self.valider_formulaire():
            return
        
        try:
            # Créer les objets
            regisseur = Regisseur(
                prenom=self.form_vars['regisseur_prenom'].get().strip(),
                nom=self.form_vars['regisseur_nom'].get().strip(),
                telephone=self.form_vars['regisseur_tel'].get().strip()
            )
            
            config_reseau = None
            if self.form_vars['type_ethernet'].get():
                config_reseau = ConfigurationReseau(
                    adresse_ip=self.form_vars['ip'].get().strip(),
                    masque=self.form_vars['masque'].get().strip(),
                    passerelle=self.form_vars['passerelle'].get().strip()
                )
            
            type_tpe = TypeTPE(
                ethernet=self.form_vars['type_ethernet'].get(),
                quatre_cinq_g=self.form_vars['type_4_5g'].get(),
                config_reseau=config_reseau
            )
            
            acces_backoffice = AccesBackoffice(
                actif=self.form_vars['backoffice_actif'].get(),
                email=self.form_vars['backoffice_email'].get().strip() if self.form_vars['backoffice_actif'].get() else None
            )
            
            tpe = TPE(
                service=self.form_vars['service'].get().strip(),
                regisseur=regisseur,
                regisseurs_suppleants=self.form_vars['regisseurs_suppleants'].get().strip(),
                carte_commercant=int(self.form_vars['carte_commercant'].get()),
                shop_id=int(self.form_vars['shop_id'].get()),
                acces_backoffice=acces_backoffice,
                modele_tpe=self.form_vars['modele_tpe'].get().strip(),
                type_tpe=type_tpe,
                nombre_tpe=int(self.form_vars['nombre_tpe'].get())
            )
            
            if self.gestionnaire.modifier_tpe(self.tpe_selectionne_id, tpe):
                messagebox.showinfo("Succès", "TPE modifié avec succès !")
                self.rafraichir_liste()
                self.vider_formulaire()
                self.sauvegarder_auto()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification du TPE:\n{str(e)}")
    
    def supprimer_tpe(self):
        """Supprime un TPE"""
        if self.tpe_selectionne_id is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un TPE à supprimer")
            return
        
        reponse = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le TPE ShopID {self.tpe_selectionne_id} ?")
        if reponse:
            if self.gestionnaire.supprimer_tpe(self.tpe_selectionne_id):
                messagebox.showinfo("Succès", "TPE supprimé avec succès !")
                self.rafraichir_liste()
                self.vider_formulaire()
                self.sauvegarder_auto()
    
    def vider_formulaire(self):
        """Vide tous les champs du formulaire"""
        for key, var in self.form_vars.items():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            elif key == 'nombre_tpe':
                var.set('1')
            else:
                var.set('')
        
        self.tpe_selectionne_id = None
        self.toggle_backoffice()
        self.toggle_ethernet()
    
    def on_select_tpe(self, event):
        """Charge les données du TPE sélectionné dans le formulaire"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        shop_id = int(item['values'][0])
        
        tpe = self.gestionnaire.rechercher_tpe(shop_id)
        if tpe:
            self.tpe_selectionne_id = shop_id
            
            # Remplir le formulaire
            self.form_vars['service'].set(tpe.service)
            self.form_vars['regisseur_prenom'].set(tpe.regisseur.prenom)
            self.form_vars['regisseur_nom'].set(tpe.regisseur.nom)
            self.form_vars['regisseur_tel'].set(tpe.regisseur.telephone)
            self.form_vars['regisseurs_suppleants'].set(tpe.regisseurs_suppleants)
            self.form_vars['carte_commercant'].set(str(tpe.carte_commercant))
            self.form_vars['shop_id'].set(str(tpe.shop_id))
            self.form_vars['nombre_tpe'].set(str(getattr(tpe, 'nombre_tpe', 1)))  # ⭐ CORRECTION ICI
            self.form_vars['modele_tpe'].set(tpe.modele_tpe)
            self.form_vars['backoffice_actif'].set(tpe.acces_backoffice.actif)
            self.form_vars['backoffice_email'].set(tpe.acces_backoffice.email or '')
            self.form_vars['type_ethernet'].set(tpe.type_tpe.ethernet)
            self.form_vars['type_4_5g'].set(tpe.type_tpe.quatre_cinq_g)
            
            if tpe.type_tpe.config_reseau:
                self.form_vars['ip'].set(tpe.type_tpe.config_reseau.adresse_ip)
                self.form_vars['masque'].set(tpe.type_tpe.config_reseau.masque)
                self.form_vars['passerelle'].set(tpe.type_tpe.config_reseau.passerelle)
            else:
                self.form_vars['ip'].set('')
                self.form_vars['masque'].set('')
                self.form_vars['passerelle'].set('')
            
            self.toggle_backoffice()
            self.toggle_ethernet()
    
    def rafraichir_liste(self):
        """Rafraîchit la liste des TPE"""
        # Vider la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Remplir avec les TPE
        for tpe in self.gestionnaire.lister_tpes():
            type_connexion = []
            if tpe.type_tpe.ethernet:
                type_connexion.append("Ethernet")
            if tpe.type_tpe.quatre_cinq_g:
                type_connexion.append("4/5G")
            
            self.tree.insert('', tk.END, values=(
                tpe.shop_id,
                tpe.service,
                f"{tpe.regisseur.prenom} {tpe.regisseur.nom}",
                tpe.modele_tpe,
                getattr(tpe, 'nombre_tpe', 1),  # Gestion des anciennes données
                " + ".join(type_connexion)
            ))
        
        # Mettre à jour les statistiques
        stats = self.gestionnaire.statistiques()
        self.stats_label.config(
            text=f"📊 Total entrées: {stats['total_tpes']} | "
                 f"Total appareils: {stats.get('total_appareils', stats['total_tpes'])} | "
                 f"Ethernet: {stats['type_ethernet']} | "
                 f"4/5G: {stats['type_4_5g']} | "
                 f"Backoffice: {stats['backoffice_actifs']}"
        )
    
    def rechercher_tpe_liste(self, *args):
        """Filtre la liste par ShopID"""
        recherche = self.search_var.get().strip()
        
        # Vider la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Remplir avec les TPE filtrés
        for tpe in self.gestionnaire.lister_tpes():
            if not recherche or recherche in str(tpe.shop_id):
                type_connexion = []
                if tpe.type_tpe.ethernet:
                    type_connexion.append("Ethernet")
                if tpe.type_tpe.quatre_cinq_g:
                    type_connexion.append("4/5G")
                
                self.tree.insert('', tk.END, values=(
                    tpe.shop_id,
                    tpe.service,
                    f"{tpe.regisseur.prenom} {tpe.regisseur.nom}",
                    tpe.modele_tpe,
                    getattr(tpe, 'nombre_tpe', 1),
                    " + ".join(type_connexion)
                ))
    
    def exporter_excel(self):
        """Exporte les TPE en Excel"""
        fichier = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="tpe_export.xlsx"
        )
        
        if fichier:
            if self.gestionnaire.exporter_excel(fichier):
                messagebox.showinfo("Succès", f"Export Excel réussi !\nFichier: {fichier}")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'export Excel")
    
    def sauvegarder(self):
        """Sauvegarde les données"""
        if self.gestionnaire.sauvegarder():
            self.gestionnaire.backup_json()
            messagebox.showinfo("Succès", "Sauvegarde réussie !")
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde")
    
    def sauvegarder_auto(self):
        """Sauvegarde automatique après chaque action"""
        self.gestionnaire.sauvegarder()
        self.gestionnaire.backup_json()
    
    def restaurer(self):
        """Restaure les données depuis un fichier"""
        fichier = filedialog.askopenfilename(
            filetypes=[("Pickle files", "*.pkl"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if fichier:
            if fichier.endswith('.json'):
                succes = self.gestionnaire.restaurer_json(fichier)
            else:
                succes = self.gestionnaire.restaurer(fichier)
            
            if succes:
                messagebox.showinfo("Succès", "Restauration réussie !")
                self.rafraichir_liste()
                self.vider_formulaire()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la restauration")
    
    def afficher_statistiques(self):
        """Affiche les statistiques détaillées"""
        stats = self.gestionnaire.statistiques()
        
        message = f"""📊 STATISTIQUES DES TPE
        
Total d'entrées: {stats['total_tpes']}
Total d'appareils: {stats.get('total_appareils', stats['total_tpes'])}

Types de connexion:
  • Ethernet: {stats['type_ethernet']}
  • 4/5G: {stats['type_4_5g']}

Accès Backoffice actifs: {stats['backoffice_actifs']}
"""
        
        messagebox.showinfo("Statistiques", message)


def main():
    """Fonction principale"""
    root = tk.Tk()
    app = TPEInterface(root)
    root.mainloop()


if __name__ == "__main__":
    main()