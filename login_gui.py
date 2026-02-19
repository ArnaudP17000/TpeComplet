"""
Interface de Connexion pour TPE Manager
Écran de login avant l'application principale
Version 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from auth_manager import AuthManager


class LoginWindow:
    """Fenêtre de connexion"""
    
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback
        self.auth_manager = AuthManager()
        
        self.root.title("TPE Manager - Connexion")
        self.root.geometry("480x400")
        self.root.resizable(False, False)
        self.root.configure(bg='#F0F4F8')
        
        # Centrer la fenêtre
        self.centrer_fenetre()
        
        # Créer l'interface
        self.creer_interface()
        
        # Bind Enter pour valider
        self.root.bind('<Return>', lambda e: self.connexion())
    
    def centrer_fenetre(self):
        """Centre la fenêtre à l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def toggle_password_visibility(self):
        """Affiche ou masque le mot de passe"""
        if self.password_visible:
            self.password_entry.config(show="●")
            self.password_visible = False
        else:
            self.password_entry.config(show="")
            self.password_visible = True
    
    def creer_interface(self):
        """Crée l'interface de connexion"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = tk.Frame(self.root, padding=30, bg='#F0F4F8')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        titre_label = tk.Label(
            main_frame,
            text="🏦 TPE Manager",
            font=('Arial', 20, 'bold'),
            foreground='#0066CC',
            bg='#F0F4F8'
        )
        titre_label.pack(pady=(0, 10))
        
        sous_titre_label = tk.Label(
            main_frame,
            text="Gestion des Terminaux de Paiement",
            font=('Arial', 10),
            bg='#F0F4F8'
        )
        sous_titre_label.pack(pady=(0, 15))
        
        # Séparateur
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=(0, 20))
        
        # Frame du formulaire
        form_frame = tk.Frame(main_frame, bg='#F0F4F8')
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nom d'utilisateur
        tk.Label(form_frame, text="Nom d'utilisateur:", font=('Arial', 10), bg='#F0F4F8').pack(anchor=tk.W, pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, font=('Arial', 11))
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        self.username_entry.focus()
        
        # Mot de passe
        tk.Label(form_frame, text="Mot de passe:", font=('Arial', 10), bg='#F0F4F8').pack(anchor=tk.W, pady=(0, 5))
        
        # Frame pour le mot de passe avec bouton de visibilité
        password_frame = tk.Frame(form_frame, bg='#F0F4F8')
        password_frame.pack(fill=tk.X, pady=(0, 25))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="●", font=('Arial', 11))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bouton pour afficher/masquer le mot de passe
        self.password_visible = False
        self.btn_toggle_password = tk.Button(
            password_frame,
            text="👁",
            command=self.toggle_password_visibility,
            font=('Arial', 10),
            width=3,
            relief=tk.FLAT,
            bg='#F0F4F8',
            cursor='hand2'
        )
        self.btn_toggle_password.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bouton de connexion (utilise tk.Button pour coloration)
        self.btn_connexion = tk.Button(
            form_frame,
            text="🔓 Se connecter",
            command=self.connexion,
            font=('Arial', 11, 'bold'),
            bg='#0066CC',
            fg='white',
            activebackground='#0052A3',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            pady=10
        )
        self.btn_connexion.pack(fill=tk.X)
        
        # Label de version discret
        tk.Label(main_frame, text="TPE Manager v1.5", font=('Arial', 7), foreground='#AAAAAA', bg='#F0F4F8').pack(side=tk.BOTTOM, pady=(10, 0))
    
    def connexion(self):
        """Tente la connexion"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Désactiver le bouton pendant la vérification
        self.btn_connexion.config(state='disabled', text="Connexion en cours...")
        self.root.update()
        
        # Authentifier
        if self.auth_manager.authentifier(username, password):
            user = self.auth_manager.get_user_connecte()
            messagebox.showinfo(
                "Connexion réussie",
                f"Bienvenue {user.prenom} {user.nom} !\nRôle: {user.role.upper()}"
            )
            
            # Fermer la fenêtre de login et lancer l'application
            self.root.destroy()
            self.on_success_callback(self.auth_manager)
        else:
            messagebox.showerror(
                "Erreur de connexion",
                "Nom d'utilisateur ou mot de passe incorrect"
            )
            self.password_var.set('')
            self.password_entry.focus()
            self.btn_connexion.config(state='normal', text="🔓 Se connecter")


def main():
    """Test de la fenêtre de connexion"""
    def on_success(auth_manager):
        pass
    
    root = tk.Tk()
    app = LoginWindow(root, on_success)
    root.mainloop()


if __name__ == "__main__":
    main()