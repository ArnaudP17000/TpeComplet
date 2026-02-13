"""
Interface Graphique pour la Gestion des Terminaux de Paiement Électronique (T.P.E.)
Utilise Tkinter pour l'interface utilisateur
Version 1.5 - Filtre par type + Numéro de série TPE
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tpe_manager import (
    GestionnaireTPE, TPE, Regisseur, AccesBackoffice,
    TypeTPE, ConfigurationReseau, CarteCommercant
)
from auth_manager import AuthManager
import os


class TPEInterface:
    """Interface graphique principale pour la gestion des TPE"""
    
    # Modèles de TPE disponibles
    MODELES_TPE = [
        "Ingenico Desk 5000",
        "Ingenico Move 5000"
    ]
    
    def __init__(self, root, auth_manager):
        self.root = root
        self.auth_manager = auth_manager
        self.user_connecte = auth_manager.get_user_connecte()
        
        self.root.title(f"Gestion TPE - {self.user_connecte.prenom} {self.user_connecte.nom} ({self.user_connecte.role})")
        
        # Dimensionnement responsive - 90% de l'écran, centré
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        self.root.resizable(True, True)
        
        # Permettre le plein écran avec F11
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.end_fullscreen())
        self.fullscreen = False
        
        # Gestionnaire TPE
        self.gestionnaire = GestionnaireTPE()
        
        # Liste pour stocker les champs de cartes (avec numéro de série)
        self.cartes_entries = []
        
        # Configuration du style
        self.configurer_style()
        
        # Création de l'interface
        self.creer_interface()
        
        # Charger les données existantes si disponibles
        if os.path.exists("tpe_data.pkl"):
            try:
                self.gestionnaire.restaurer()
                self.rafraichir_liste()
            except Exception as e:
                messagebox.showwarning(
                    "Attention",
                    f"Impossible de charger les anciennes données.\n"
                    f"L'application va démarrer avec une base vide.\n\n"
                    f"Erreur: {str(e)}"
                )
        else:
            self.rafraichir_liste()
    
    def toggle_fullscreen(self):
        """Bascule en mode plein écran"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
    
    def end_fullscreen(self):
        """Quitte le mode plein écran"""
        self.fullscreen = False
        self.root.attributes('-fullscreen', False)
    
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
        # Menu
        self.creer_menu()
        
        # Titre principal avec info utilisateur
        titre_frame = ttk.Frame(self.root, padding="10")
        titre_frame.pack(fill=tk.X)
        
        # Info utilisateur connecté (à droite)
        user_info_frame = ttk.Frame(titre_frame)
        user_info_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            user_info_frame,
            text=f"👤 {self.user_connecte.prenom} {self.user_connecte.nom}",
            font=('Arial', 9)
        ).pack(side=tk.LEFT, padx=5)
        
        badge_color = "#28a745" if self.user_connecte.role == "admin" else "#007bff"
        badge_text = "ADMIN" if self.user_connecte.role == "admin" else "USER"
        
        badge_frame = tk.Frame(user_info_frame, bg=badge_color, padx=5, pady=2)
        badge_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            badge_frame,
            text=badge_text,
            font=('Arial', 8, 'bold'),
            fg='white',
            bg=badge_color
        ).pack()
        
        # Titre (à gauche)
        ttk.Label(
            titre_frame,
            text="🏦 Gestion des Terminaux de Paiement Électronique",
            style='Titre.TLabel'
        ).pack(side=tk.LEFT)
        
        # Frame principal avec deux colonnes
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuration du grid pour répartition 50/50
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Colonne gauche : Liste des TPE
        left_frame = ttk.LabelFrame(main_frame, text="Liste des TPE", padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.creer_liste_tpe(left_frame)
        
        # Colonne droite : Formulaire
        right_frame = ttk.LabelFrame(main_frame, text="Formulaire TPE", padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        self.creer_formulaire(right_frame)
        
        # Frame du bas : Boutons d'action
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.creer_boutons_action(bottom_frame)
    
    def creer_menu(self):
        """Crée la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        menu_fichier = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=menu_fichier)
        menu_fichier.add_command(label="📊 Export Excel", command=self.exporter_excel)
        menu_fichier.add_command(label="💾 Sauvegarder", command=self.sauvegarder)
        menu_fichier.add_command(label="📂 Restaurer", command=self.restaurer)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="🚪 Déconnexion", command=self.deconnexion)
        menu_fichier.add_command(label="❌ Quitter", command=self.root.quit)
        
        # Menu Utilisateur (seulement pour admin)
        if self.auth_manager.est_admin():
            menu_users = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Utilisateurs", menu=menu_users)
            menu_users.add_command(label="👥 Gérer les utilisateurs", command=self.gerer_utilisateurs)
            menu_users.add_command(label="➕ Nouvel utilisateur", command=self.ajouter_utilisateur)
            menu_users.add_command(label="📊 Statistiques utilisateurs", command=self.stats_users)
        
        # Menu Compte
        menu_compte = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Mon compte", menu=menu_compte)
        menu_compte.add_command(label="🔐 Changer mot de passe", command=self.changer_password)
        menu_compte.add_command(label="ℹ️ Mes informations", command=self.afficher_mes_infos)
        
        # Menu Aide
        menu_aide = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="?", menu=menu_aide)
        menu_aide.add_command(label="📈 Statistiques TPE", command=self.afficher_statistiques)
        menu_aide.add_command(label="ℹ️ À propos", command=self.a_propos)
    
    def creer_liste_tpe(self, parent):
        """Crée la liste des TPE avec filtre par type"""
        # Frame pour le filtre
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Type de TPE:").pack(side=tk.LEFT, padx=(0, 5))
        self.filtre_var = tk.StringVar(value="Tous")
        filtre_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.filtre_var,
            values=["Tous", "Move", "Desk"],
            state='readonly',
            width=15
        )
        filtre_combo.pack(side=tk.LEFT)
        filtre_combo.bind('<<ComboboxSelected>>', self.filtrer_tpe_liste)
        
        # Treeview pour afficher les TPE
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Colonnes MODIFIÉES (ajout colonne Cartes)
        colonnes = ('ShopID', 'Service', 'Régisseur', 'Modèle', 'Nb TPE', 'Type', 'Cartes')
        self.tree = ttk.Treeview(tree_frame, columns=colonnes, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        # En-têtes
        self.tree.heading('ShopID', text='ShopID')
        self.tree.heading('Service', text='Service')
        self.tree.heading('Régisseur', text='Régisseur')
        self.tree.heading('Modèle', text='Modèle TPE')
        self.tree.heading('Nb TPE', text='Nb TPE')
        self.tree.heading('Type', text='Type Connexion')
        self.tree.heading('Cartes', text='Cartes Commerçant')
        
        # Largeurs
        self.tree.column('ShopID', width=70)
        self.tree.column('Service', width=120)
        self.tree.column('Régisseur', width=130)
        self.tree.column('Modèle', width=130)
        self.tree.column('Nb TPE', width=60)
        self.tree.column('Type', width=110)
        self.tree.column('Cartes', width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind pour sélection
        self.tree.bind('<<TreeviewSelect>>', self.on_select_tpe)
        
        # Statistiques
        self.stats_label = ttk.Label(parent, text="", font=('Arial', 9))
        self.stats_label.pack(pady=(10, 0))
    
    def filtrer_tpe_liste(self, *args):
        """Filtre la liste par type de TPE (Move/Desk)"""
        filtre = self.filtre_var.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for tpe in self.gestionnaire.lister_tpes():
            # Filtrer par type
            modele = tpe.modele_tpe
            if filtre != "Tous":
                if filtre == "Move" and "Move" not in modele:
                    continue
                if filtre == "Desk" and "Desk" not in modele:
                    continue
            
            type_connexion = []
            if tpe.type_tpe.ethernet:
                type_connexion.append("Ethernet")
            if tpe.type_tpe.quatre_cinq_g:
                type_connexion.append("4/5G")
            
            nombre_tpe = getattr(tpe, 'nombre_tpe', 1)
            
            # Récupérer les cartes (avec compatibilité)
            cartes_str = ""
            if hasattr(tpe, 'cartes_commercant') and tpe.cartes_commercant:
                if isinstance(tpe.cartes_commercant[0], CarteCommercant):
                    # Nouvelle version
                    cartes_str = ", ".join([c.numero for c in tpe.cartes_commercant[:2]])
                    if len(tpe.cartes_commercant) > 2:
                        cartes_str += "..."
                else:
                    # Ancienne version (strings)
                    cartes_str = ", ".join([str(c) for c in tpe.cartes_commercant[:2]])
                    if len(tpe.cartes_commercant) > 2:
                        cartes_str += "..."
            
            self.tree.insert('', tk.END, values=(
                tpe.shop_id,
                tpe.service,
                f"{tpe.regisseur.prenom} {tpe.regisseur.nom}",
                tpe.modele_tpe,
                nombre_tpe,
                " + ".join(type_connexion),
                cartes_str
            ))
    
    def creer_formulaire(self, parent):
        """Crée le formulaire de saisie"""
        # Canvas avec scrollbar pour le formulaire
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configuration pour que les colonnes s'étirent
        scrollable_frame.grid_columnconfigure(0, weight=0, minsize=180)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas_window)
        
        # Variables de formulaire
        self.form_vars = {}
        
        row = 0
        
        # Service
        ttk.Label(scrollable_frame, text="Service *", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        self.form_vars['service'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['service']).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Régisseur
        ttk.Label(scrollable_frame, text="Régisseur *", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        
        ttk.Label(scrollable_frame, text="Prénom:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.form_vars['regisseur_prenom'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseur_prenom']).grid(row=row, column=1, sticky=tk.EW)
        row += 1
        
        ttk.Label(scrollable_frame, text="Nom:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.form_vars['regisseur_nom'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseur_nom']).grid(row=row, column=1, sticky=tk.EW)
        row += 1
        
        ttk.Label(scrollable_frame, text="Téléphone:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.form_vars['regisseur_tel'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseur_tel']).grid(row=row, column=1, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Régisseurs Suppléants
        ttk.Label(scrollable_frame, text="Régisseurs Suppléants", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        self.form_vars['regisseurs_suppleants'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['regisseurs_suppleants']).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Cartes Commerçant avec Numéro de série TPE
        ttk.Label(scrollable_frame, text="Cartes Commerçant * (avec N° série TPE)", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        
        # Frame pour les cartes
        self.cartes_frame = ttk.Frame(scrollable_frame)
        self.cartes_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 5))
        self.cartes_frame.grid_columnconfigure(1, weight=1)
        self.cartes_frame.grid_columnconfigure(3, weight=1)
        row += 1
        
        # Bouton ajouter carte
        btn_add_carte = ttk.Button(scrollable_frame, text="➕ Ajouter Carte", command=self.ajouter_champ_carte)
        btn_add_carte.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Initialiser avec une carte
        self.cartes_entries = []
        self.ajouter_champ_carte()
        
        # ShopID
        ttk.Label(scrollable_frame, text="ShopID (optionnel - auto si vide)", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        self.form_vars['shop_id'] = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['shop_id']).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Nombre de TPE
        ttk.Label(scrollable_frame, text="Nombre de TPE * (numérique)", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        self.form_vars['nombre_tpe'] = tk.StringVar(value="1")
        ttk.Entry(scrollable_frame, textvariable=self.form_vars['nombre_tpe']).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Modèle TPE (Liste déroulante)
        ttk.Label(scrollable_frame, text="Modèle de TPE *", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        self.form_vars['modele_tpe'] = tk.StringVar()
        self.modele_combo = ttk.Combobox(
            scrollable_frame, 
            textvariable=self.form_vars['modele_tpe'], 
            values=self.MODELES_TPE,
            state='readonly'
        )
        self.modele_combo.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Accès Backoffice
        ttk.Label(scrollable_frame, text="Accès Backoffice", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        
        self.form_vars['backoffice_actif'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Actif", variable=self.form_vars['backoffice_actif'], command=self.toggle_backoffice).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        ttk.Label(scrollable_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, padx=(10, 5))
        self.form_vars['backoffice_email'] = tk.StringVar()
        self.backoffice_email_entry = ttk.Entry(scrollable_frame, textvariable=self.form_vars['backoffice_email'], state='disabled')
        self.backoffice_email_entry.grid(row=row, column=1, sticky=tk.EW, pady=(0, 10))
        row += 1
        
        # Type de TPE
        ttk.Label(scrollable_frame, text="Type de TPE *", style='SousTitre.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
        row += 1
        
        self.form_vars['type_ethernet'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Ethernet", variable=self.form_vars['type_ethernet'], command=self.toggle_ethernet).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        self.form_vars['type_4_5g'] = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="4/5G", variable=self.form_vars['type_4_5g']).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Configuration Réseau (si Ethernet)
        self.config_reseau_frame = ttk.LabelFrame(scrollable_frame, text="Configuration Réseau (Ethernet)", padding="5")
        self.config_reseau_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        self.config_reseau_frame.grid_columnconfigure(1, weight=1)
        row += 1
        
        ttk.Label(self.config_reseau_frame, text="Adresse IP:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.form_vars['ip'] = tk.StringVar()
        self.ip_entry = ttk.Entry(self.config_reseau_frame, textvariable=self.form_vars['ip'], state='disabled')
        self.ip_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(self.config_reseau_frame, text="Masque:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.form_vars['masque'] = tk.StringVar()
        self.masque_entry = ttk.Entry(self.config_reseau_frame, textvariable=self.form_vars['masque'], state='disabled')
        self.masque_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(self.config_reseau_frame, text="Passerelle:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.form_vars['passerelle'] = tk.StringVar()
        self.passerelle_entry = ttk.Entry(self.config_reseau_frame, textvariable=self.form_vars['passerelle'], state='disabled')
        self.passerelle_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Boutons du formulaire
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="➕ Ajouter TPE", command=self.ajouter_tpe, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
        
        # Bouton Modifier/Supprimer seulement pour admin
        if self.auth_manager.est_admin():
            ttk.Button(btn_frame, text="✏️ Modifier TPE", command=self.modifier_tpe, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="🗑️ Supprimer TPE", command=self.supprimer_tpe, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🔄 Nouveau", command=self.vider_formulaire, style='Bouton.TButton').pack(side=tk.LEFT, padx=5)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # ID TPE sélectionné (pour modification)
        self.tpe_selectionne_id = None
    
    def ajouter_champ_carte(self):
        """Ajoute un champ de saisie pour une carte commerçant avec numéro de série"""
        if len(self.cartes_entries) >= 8:
            messagebox.showwarning("Limite atteinte", "Maximum 8 cartes commerçant")
            return
        
        row = len(self.cartes_entries)
        
        # Frame pour la carte
        carte_frame = ttk.Frame(self.cartes_frame)
        carte_frame.grid(row=row, column=0, columnspan=5, sticky=tk.EW, pady=2)
        carte_frame.grid_columnconfigure(1, weight=1)
        carte_frame.grid_columnconfigure(3, weight=1)
        
        # Label Carte
        label = ttk.Label(carte_frame, text=f"Carte {row + 1}{'*' if row == 0 else ''}:", width=8)
        label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # Entry Carte
        var_carte = tk.StringVar()
        entry_carte = ttk.Entry(carte_frame, textvariable=var_carte, width=15)
        entry_carte.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10))
        
        # Label N° Série
        label_serie = ttk.Label(carte_frame, text="N° Série:", width=8)
        label_serie.grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        # Entry N° Série
        var_serie = tk.StringVar()
        entry_serie = ttk.Entry(carte_frame, textvariable=var_serie, width=15)
        entry_serie.grid(row=0, column=3, sticky=tk.EW, padx=(0, 5))
        
        # Bouton supprimer (sauf pour la première carte)
        if row > 0:
            btn_remove = ttk.Button(
                carte_frame, 
                text="❌", 
                width=3,
                command=lambda: self.supprimer_champ_carte(carte_frame, var_carte, var_serie)
            )
            btn_remove.grid(row=0, column=4, sticky=tk.W)
        
        self.cartes_entries.append((carte_frame, var_carte, var_serie))
    
    def supprimer_champ_carte(self, frame, var_carte, var_serie):
        """Supprime un champ de carte"""
        if len(self.cartes_entries) <= 1:
            messagebox.showwarning("Attention", "Au moins une carte est requise")
            return
        
        # Trouver et supprimer
        for i, (f, vc, vs) in enumerate(self.cartes_entries):
            if f == frame:
                frame.destroy()
                self.cartes_entries.pop(i)
                break
        
        # Réorganiser les labels
        for i, (f, vc, vs) in enumerate(self.cartes_entries):
            for widget in f.winfo_children():
                if isinstance(widget, ttk.Label) and "Carte" in widget.cget("text"):
                    widget.config(text=f"Carte {i + 1}{'*' if i == 0 else ''}:")
                    break
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
        
        # Validation cartes commerçant
        cartes_valides = []
        for i, (frame, var_carte, var_serie) in enumerate(self.cartes_entries):
            carte_str = var_carte.get().strip()
            if i == 0 and not carte_str:
                messagebox.showerror("Erreur", "La première carte commerçant est obligatoire")
                return False
            if carte_str:
                if len(carte_str) > 50:
                    messagebox.showerror("Erreur", f"La carte commerçant {i+1} est trop longue (max 50 caractères)")
                    return False
                cartes_valides.append(carte_str)
        
        if not cartes_valides:
            messagebox.showerror("Erreur", "Au moins une carte commerçant est requise")
            return False
        
        # Validation ShopID (optionnel)
        shop_id_str = self.form_vars['shop_id'].get().strip()
        if shop_id_str:
            try:
                shop_id = int(shop_id_str)
                if shop_id < 0:
                    raise ValueError()
            except:
                messagebox.showerror("Erreur", "Le ShopID doit être un nombre positif ou vide (génération auto)")
                return False
        
        # Validation Nombre de TPE
        try:
            nombre_tpe = int(self.form_vars['nombre_tpe'].get())
            if nombre_tpe < 1:
                raise ValueError()
        except:
            messagebox.showerror("Erreur", "Le nombre de TPE doit être au minimum 1")
            return False
        
        # Validation modèle TPE
        if not self.form_vars['modele_tpe'].get():
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
    
    def get_cartes_commercant(self):
        """Récupère la liste des cartes commerçant avec numéros de série"""
        cartes = []
        for frame, var_carte, var_serie in self.cartes_entries:
            carte_str = var_carte.get().strip()
            serie_str = var_serie.get().strip() or None
            if carte_str:
                cartes.append(CarteCommercant(numero=carte_str, numero_serie_tpe=serie_str))
        return cartes
    
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
            
            # Récupérer les cartes avec numéros de série
            cartes = self.get_cartes_commercant()
            
            nombre_tpe_value = int(self.form_vars['nombre_tpe'].get())
            
            # ShopID
            shop_id_str = self.form_vars['shop_id'].get().strip()
            shop_id_value = int(shop_id_str) if shop_id_str else 0
            
            tpe = TPE(
                service=self.form_vars['service'].get().strip(),
                regisseur=regisseur,
                regisseurs_suppleants=self.form_vars['regisseurs_suppleants'].get().strip(),
                cartes_commercant=cartes,
                shop_id=shop_id_value,
                acces_backoffice=acces_backoffice,
                modele_tpe=self.form_vars['modele_tpe'].get(),
                type_tpe=type_tpe,
                nombre_tpe=nombre_tpe_value
            )
            
            if self.gestionnaire.ajouter_tpe(tpe):
                cartes_info = ", ".join([f"{c.numero} (SN: {c.numero_serie_tpe or 'N/A'})" for c in tpe.cartes_commercant])
                messagebox.showinfo("Succès", f"TPE ajouté avec succès !\nShopID: {tpe.shop_id}\nNombre de TPE: {tpe.nombre_tpe}\nCartes: {cartes_info}")
                self.rafraichir_liste()
                self.vider_formulaire()
                self.sauvegarder_auto()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout du TPE:\n{str(e)}")
    
    def modifier_tpe(self):
        """Modifie un TPE existant"""
        if not self.auth_manager.est_admin():
            messagebox.showerror("Accès refusé", "Seuls les administrateurs peuvent modifier les TPE")
            return
        
        if self.tpe_selectionne_id is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner un TPE à modifier")
            return
        
        if not self.valider_formulaire():
            return
        
        try:
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
            
            cartes = self.get_cartes_commercant()
            nombre_tpe_value = int(self.form_vars['nombre_tpe'].get())
            
            # ShopID
            shop_id_str = self.form_vars['shop_id'].get().strip()
            shop_id_value = int(shop_id_str) if shop_id_str else self.tpe_selectionne_id
            
            tpe = TPE(
                service=self.form_vars['service'].get().strip(),
                regisseur=regisseur,
                regisseurs_suppleants=self.form_vars['regisseurs_suppleants'].get().strip(),
                cartes_commercant=cartes,
                shop_id=shop_id_value,
                acces_backoffice=acces_backoffice,
                modele_tpe=self.form_vars['modele_tpe'].get(),
                type_tpe=type_tpe,
                nombre_tpe=nombre_tpe_value
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
        if not self.auth_manager.est_admin():
            messagebox.showerror("Accès refusé", "Seuls les administrateurs peuvent supprimer les TPE")
            return
        
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
        # Variables simples
        for key, var in self.form_vars.items():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            elif key == 'nombre_tpe':
                var.set('1')
            else:
                var.set('')
        
        # Réinitialiser les cartes
        for frame, var_carte, var_serie in self.cartes_entries:
            frame.destroy()
        self.cartes_entries = []
        self.ajouter_champ_carte()
        
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
            self.form_vars['shop_id'].set(str(tpe.shop_id))
            
            # Nombre de TPE
            nombre_tpe = getattr(tpe, 'nombre_tpe', 1)
            self.form_vars['nombre_tpe'].set(str(nombre_tpe))
            
            # Modèle TPE
            self.form_vars['modele_tpe'].set(tpe.modele_tpe)
            
            # Cartes commerçant avec numéros de série
            cartes = getattr(tpe, 'cartes_commercant', [])
            
            # Réinitialiser les cartes
            for frame, var_carte, var_serie in self.cartes_entries:
                frame.destroy()
            self.cartes_entries = []
            
            # Ajouter les cartes existantes
            if cartes:
                for carte in cartes:
                    self.ajouter_champ_carte()
                    if isinstance(carte, CarteCommercant):
                        self.cartes_entries[-1][1].set(carte.numero)
                        self.cartes_entries[-1][2].set(carte.numero_serie_tpe or '')
                    else:
                        # Ancienne version (string)
                        self.cartes_entries[-1][1].set(str(carte))
                        self.cartes_entries[-1][2].set('')
            
            # Si aucune carte, ajouter un champ vide
            if not self.cartes_entries:
                self.ajouter_champ_carte()
            
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
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for tpe in self.gestionnaire.lister_tpes():
            type_connexion = []
            if tpe.type_tpe.ethernet:
                type_connexion.append("Ethernet")
            if tpe.type_tpe.quatre_cinq_g:
                type_connexion.append("4/5G")
            
            nombre_tpe = getattr(tpe, 'nombre_tpe', 1)
            
            # Récupérer les cartes (avec compatibilité)
            cartes_str = ""
            if hasattr(tpe, 'cartes_commercant') and tpe.cartes_commercant:
                if isinstance(tpe.cartes_commercant[0], CarteCommercant):
                    # Nouvelle version
                    cartes_str = ", ".join([c.numero for c in tpe.cartes_commercant[:2]])
                    if len(tpe.cartes_commercant) > 2:
                        cartes_str += "..."
                else:
                    # Ancienne version (strings)
                    cartes_str = ", ".join([str(c) for c in tpe.cartes_commercant[:2]])
                    if len(tpe.cartes_commercant) > 2:
                        cartes_str += "..."
            
            self.tree.insert('', tk.END, values=(
                tpe.shop_id,
                tpe.service,
                f"{tpe.regisseur.prenom} {tpe.regisseur.nom}",
                tpe.modele_tpe,
                nombre_tpe,
                " + ".join(type_connexion),
                cartes_str
            ))
        
        stats = self.gestionnaire.statistiques()
        self.stats_label.config(
            text=f"📊 Total entrées: {stats['total_tpes']} | "
                 f"Total appareils: {stats.get('total_appareils', stats['total_tpes'])} | "
                 f"Ethernet: {stats['type_ethernet']} | "
                 f"4/5G: {stats['type_4_5g']} | "
                 f"Backoffice: {stats['backoffice_actifs']}"
        )
    
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
        
        messagebox.showinfo("Statistiques TPE", message)
    
    # ========================================
    # FONCTIONS D'AUTHENTIFICATION
    # ========================================
    
    def deconnexion(self):
        """Déconnexion de l'utilisateur"""
        reponse = messagebox.askyesno(
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?"
        )
        if reponse:
            self.auth_manager.deconnecter()
            messagebox.showinfo("Déconnexion", "Vous avez été déconnecté")
            self.root.destroy()
            # Relancer l'écran de connexion
            import login_gui
            root = tk.Tk()
            login_gui.LoginWindow(root, lambda auth: self.relancer_app(auth))
            root.mainloop()
    
    def relancer_app(self, auth_manager):
        """Relance l'application après reconnexion"""
        root = tk.Tk()
        app = TPEInterface(root, auth_manager)
        root.mainloop()
    
    def changer_password(self):
        """Fenêtre de changement de mot de passe"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Changer mon mot de passe")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Centrer
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Ancien mot de passe:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
        ancien_var = tk.StringVar()
        ttk.Entry(frame, textvariable=ancien_var, show="●", font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Nouveau mot de passe:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
        nouveau_var = tk.StringVar()
        ttk.Entry(frame, textvariable=nouveau_var, show="●", font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Confirmer mot de passe:", font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
        confirm_var = tk.StringVar()
        ttk.Entry(frame, textvariable=confirm_var, show="●", font=('Arial', 10)).pack(fill=tk.X, pady=(0, 20))
        
        def valider():
            ancien = ancien_var.get()
            nouveau = nouveau_var.get()
            confirm = confirm_var.get()
            
            if not ancien or not nouveau or not confirm:
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
                return
            
            if nouveau != confirm:
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
                return
            
            if len(nouveau) < 6:
                messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 6 caractères")
                return
            
            if self.auth_manager.modifier_password(self.user_connecte.username, ancien, nouveau):
                messagebox.showinfo("Succès", "Mot de passe modifié avec succès")
                dialog.destroy()
            else:
                messagebox.showerror("Erreur", "Ancien mot de passe incorrect")
        
        ttk.Button(frame, text="✅ Valider", command=valider).pack(fill=tk.X, ipady=5)
    
    def afficher_mes_infos(self):
        """Affiche les informations de l'utilisateur connecté"""
        user = self.user_connecte
        message = f"""👤 INFORMATIONS DU COMPTE

Nom d'utilisateur: {user.username}
Nom: {user.nom}
Prénom: {user.prenom}
Email: {user.email}
Rôle: {user.role.upper()}
Date de création: {user.date_creation}
Dernière connexion: {user.derniere_connexion or 'Première connexion'}
Statut: {'✅ Actif' if user.actif else '❌ Inactif'}
"""
        messagebox.showinfo("Mes informations", message)
    
    def gerer_utilisateurs(self):
        """Fenêtre de gestion des utilisateurs (admin seulement)"""
        if not self.auth_manager.est_admin():
            messagebox.showerror("Accès refusé", "Cette fonctionnalité est réservée aux administrateurs")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Gestion des utilisateurs")
        dialog.geometry("900x500")
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Liste des utilisateurs
        ttk.Label(frame, text="👥 Liste des utilisateurs", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        colonnes = ('Username', 'Nom', 'Prénom', 'Email', 'Rôle', 'Statut', 'Dernière connexion')
        tree = ttk.Treeview(tree_frame, columns=colonnes, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for col in colonnes:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Remplir la liste
        for user in self.auth_manager.lister_users():
            tree.insert('', tk.END, values=(
                user.username,
                user.nom,
                user.prenom,
                user.email,
                user.role.upper(),
                '✅ Actif' if user.actif else '❌ Inactif',
                user.derniere_connexion or 'Jamais'
            ))
        
        # Boutons d'action
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        def activer_desactiver():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Attention", "Sélectionnez un utilisateur")
                return
            
            username = tree.item(selection[0])['values'][0]
            
            if username == "admin":
                messagebox.showerror("Erreur", "Impossible de modifier le compte admin")
                return
            
            user = self.auth_manager.users[username]
            
            if user.actif:
                if self.auth_manager.desactiver_user(username):
                    messagebox.showinfo("Succès", f"Utilisateur {username} désactivé")
                    dialog.destroy()
                    self.gerer_utilisateurs()
            else:
                if self.auth_manager.activer_user(username):
                    messagebox.showinfo("Succès", f"Utilisateur {username} activé")
                    dialog.destroy()
                    self.gerer_utilisateurs()
        
        ttk.Button(btn_frame, text="✅/❌ Activer/Désactiver", command=activer_desactiver).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="➕ Nouvel utilisateur", command=lambda: [dialog.destroy(), self.ajouter_utilisateur()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Statistiques", command=lambda: self.stats_users()).pack(side=tk.LEFT, padx=5)
    
    def ajouter_utilisateur(self):
        """Fenêtre d'ajout d'utilisateur (admin seulement)"""
        if not self.auth_manager.est_admin():
            messagebox.showerror("Accès refusé", "Cette fonctionnalité est réservée aux administrateurs")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvel utilisateur")
        dialog.geometry("450x500")
        dialog.resizable(False, False)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="➕ CRÉER UN NOUVEL UTILISATEUR", font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Champs
        ttk.Label(frame, text="Nom d'utilisateur:").pack(anchor=tk.W, pady=(0, 5))
        username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=username_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Mot de passe:").pack(anchor=tk.W, pady=(0, 5))
        password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=password_var, show="●").pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Nom:").pack(anchor=tk.W, pady=(0, 5))
        nom_var = tk.StringVar()
        ttk.Entry(frame, textvariable=nom_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Prénom:").pack(anchor=tk.W, pady=(0, 5))
        prenom_var = tk.StringVar()
        ttk.Entry(frame, textvariable=prenom_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Email:").pack(anchor=tk.W, pady=(0, 5))
        email_var = tk.StringVar()
        ttk.Entry(frame, textvariable=email_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame, text="Rôle:").pack(anchor=tk.W, pady=(0, 5))
        role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(frame, textvariable=role_var, values=["admin", "user"], state="readonly")
        role_combo.pack(fill=tk.X, pady=(0, 20))
        
        def valider():
            username = username_var.get().strip()
            password = password_var.get()
            nom = nom_var.get().strip()
            prenom = prenom_var.get().strip()
            email = email_var.get().strip()
            role = role_var.get()
            
            if not all([username, password, nom, prenom, email, role]):
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
                return
            
            if len(password) < 6:
                messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 6 caractères")
                return
            
            if self.auth_manager.ajouter_user(username, password, role, nom, prenom, email):
                messagebox.showinfo("Succès", f"Utilisateur {username} créé avec succès")
                dialog.destroy()
            else:
                messagebox.showerror("Erreur", "Impossible de créer l'utilisateur (existe déjà ?)")
        
        ttk.Button(frame, text="✅ Créer l'utilisateur", command=valider).pack(fill=tk.X, ipady=8)
    
    def stats_users(self):
        """Affiche les statistiques utilisateurs"""
        stats = self.auth_manager.statistiques_users()
        
        message = f"""📊 STATISTIQUES UTILISATEURS

Total d'utilisateurs: {stats['total']}
Utilisateurs actifs: {stats['actifs']}
Utilisateurs inactifs: {stats['inactifs']}

Administrateurs: {stats['admins']}
Utilisateurs standard: {stats['users']}
"""
        messagebox.showinfo("Statistiques utilisateurs", message)
    
    def a_propos(self):
        """Affiche les informations À propos"""
        message = """🏦 TPE MANAGER v1.5

Gestion des Terminaux de Paiement Électronique

Fonctionnalités:
✅ Gestion complète des TPE
✅ Multi-cartes commerçant avec N° série (1-8)
✅ Filtre par type de TPE (Move/Desk)
✅ Interface responsive
✅ Export Excel
✅ Authentification multi-utilisateurs
✅ Gestion des droits (Admin/User)

Développé avec Python & Tkinter
© 2026 - Tous droits réservés
"""
        messagebox.showinfo("À propos", message)


def main():
    """Fonction principale avec authentification"""
    import login_gui
    
    def lancer_application(auth_manager):
        """Lance l'application principale après connexion"""
        root = tk.Tk()
        app = TPEInterface(root, auth_manager)
        root.mainloop()
    
    # Lancer l'écran de connexion
    root = tk.Tk()
    login_gui.LoginWindow(root, lancer_application)
    root.mainloop()


if __name__ == "__main__":
    main()