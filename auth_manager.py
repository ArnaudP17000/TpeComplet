"""
Module d'Authentification pour TPE Manager
Gestion des utilisateurs et connexions sécurisées
Version 1.0
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Classe représentant un utilisateur"""
    username: str
    password_hash: str
    role: str  # 'admin' ou 'user'
    nom: str
    prenom: str
    email: str
    date_creation: str
    derniere_connexion: str = None
    actif: bool = True
    
    def to_dict(self):
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'date_creation': self.date_creation,
            'derniere_connexion': self.derniere_connexion,
            'actif': self.actif
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class AuthManager:
    """Gestionnaire d'authentification"""
    
    def __init__(self, fichier_users: str = "users.json"):
        self.fichier_users = fichier_users
        self.users: Dict[str, User] = {}
        self.user_connecte: Optional[User] = None
        self.charger_users()
        
        # Créer un admin par défaut si aucun utilisateur n'existe
        if not self.users:
            self.creer_admin_defaut()
    
    def hash_password(self, password: str) -> str:
        """Hash le mot de passe avec SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def creer_admin_defaut(self):
        """Crée un compte admin par défaut"""
        admin = User(
            username="admin",
            password_hash=self.hash_password("admin123"),
            role="admin",
            nom="Administrateur",
            prenom="Système",
            email="admin@tpe.local",
            date_creation=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            actif=True
        )
        self.users["admin"] = admin
        self.sauvegarder_users()
    
    def ajouter_user(self, username: str, password: str, role: str, nom: str, prenom: str, email: str) -> bool:
        """Ajoute un nouvel utilisateur"""
        try:
            if username in self.users:
                return False
            
            if role not in ['admin', 'user']:
                return False
            
            user = User(
                username=username,
                password_hash=self.hash_password(password),
                role=role,
                nom=nom,
                prenom=prenom,
                email=email,
                date_creation=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                actif=True
            )
            
            self.users[username] = user
            self.sauvegarder_users()
            return True
            
        except Exception as e:
            return False
    
    def authentifier(self, username: str, password: str) -> bool:
        """Authentifie un utilisateur"""
        try:
            if username not in self.users:
                return False
            
            user = self.users[username]
            
            if not user.actif:
                return False
            
            password_hash = self.hash_password(password)
            
            if user.password_hash != password_hash:
                return False
            
            # Connexion réussie
            user.derniere_connexion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.user_connecte = user
            self.sauvegarder_users()
            
            return True
            
        except Exception as e:
            return False
    
    def deconnecter(self):
        """Déconnecte l'utilisateur actuel"""
        self.user_connecte = None
    
    def est_admin(self) -> bool:
        """Vérifie si l'utilisateur connecté est admin"""
        return self.user_connecte and self.user_connecte.role == 'admin'
    
    def est_connecte(self) -> bool:
        """Vérifie si un utilisateur est connecté"""
        return self.user_connecte is not None
    
    def get_user_connecte(self) -> Optional[User]:
        """Retourne l'utilisateur connecté"""
        return self.user_connecte
    
    def modifier_password(self, username: str, ancien_password: str, nouveau_password: str) -> bool:
        """Modifie le mot de passe d'un utilisateur"""
        try:
            if username not in self.users:
                return False
            
            user = self.users[username]
            
            # Vérifier l'ancien mot de passe
            if user.password_hash != self.hash_password(ancien_password):
                return False
            
            # Modifier le mot de passe
            user.password_hash = self.hash_password(nouveau_password)
            self.sauvegarder_users()
            
            return True
            
        except Exception as e:
            return False
    
    def desactiver_user(self, username: str) -> bool:
        """Désactive un utilisateur"""
        try:
            if username not in self.users:
                return False
            
            if username == "admin":
                return False
            
            self.users[username].actif = False
            self.sauvegarder_users()
            
            return True
            
        except Exception as e:
            return False
    
    def activer_user(self, username: str) -> bool:
        """Active un utilisateur"""
        try:
            if username not in self.users:
                return False
            
            self.users[username].actif = True
            self.sauvegarder_users()
            
            return True
            
        except Exception as e:
            return False
    
    def lister_users(self) -> List[User]:
        """Retourne la liste de tous les utilisateurs"""
        return list(self.users.values())
    
    def sauvegarder_users(self) -> bool:
        """Sauvegarde les utilisateurs dans un fichier JSON"""
        try:
            data = {
                'users': {username: user.to_dict() for username, user in self.users.items()},
                'date_sauvegarde': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.fichier_users, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            return False
    
    def charger_users(self) -> bool:
        """Charge les utilisateurs depuis le fichier JSON"""
        try:
            if not Path(self.fichier_users).exists():
                return False
            
            with open(self.fichier_users, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.users = {
                username: User.from_dict(user_data) 
                for username, user_data in data['users'].items()
            }
            
            return True
            
        except Exception as e:
            return False
    
    def statistiques_users(self) -> dict:
        """Retourne des statistiques sur les utilisateurs"""
        total = len(self.users)
        actifs = sum(1 for u in self.users.values() if u.actif)
        admins = sum(1 for u in self.users.values() if u.role == 'admin')
        users = sum(1 for u in self.users.values() if u.role == 'user')
        
        return {
            'total': total,
            'actifs': actifs,
            'inactifs': total - actifs,
            'admins': admins,
            'users': users
        }