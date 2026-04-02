# 🕵️ ShadowComm - Système de Communication Sécurisé

[cite_start]**Projet :** TPRE201 – Bachelor SIN 1ère année (2025-2026)[cite: 166, 299].  
[cite_start]**Agence :** ShadowComm — Spécialisée dans la communication cryptée pour agents infiltrés[cite: 94, 164].

---

## 📝 Présentation du Projet
[cite_start]ShadowComm est un prototype d'outil de communication interne sécurisé permettant aux espions de l'agence d'échanger des informations vitales sans risque d'interception[cite: 83, 170]. [cite_start]Le système repose sur une architecture robuste alliant sécurité des accès et chiffrement des données[cite: 90, 91].

## 🚀 Fonctionnalités Principales
* [cite_start]**Accès Sécurisé :** Inscription avec nom de code unique et mot de passe[cite: 98, 199].
* [cite_start]**Acceptation des règles :** Case à cocher obligatoire pour les règles de confidentialité avant l'inscription[cite: 99, 200].
* [cite_start]**Authentification Forte :** Connexion sécurisée avec sessions Flask (cookies)[cite: 101, 203].
* [cite_start]**Sécurité des données :** Hachage des mots de passe avec `bcrypt` pour éviter les fuites[cite: 104, 205].
* [cite_start]**Chat Chiffré :** Messagerie en temps réel affichant le nom de code, l'heure et le message déchiffré[cite: 110, 209].
* [cite_start]**Cryptographie César :** Utilisation d'un algorithme avec décalage fixe (Clé = 3) pour le stockage en base de données[cite: 145, 212].
* [cite_start]**Droit à l'oubli (RGPD) :** Suppression complète du compte et de tous les messages associés[cite: 121, 215].

## 🛠️ Stack Technique
* [cite_start]**Backend :** Python 3.x avec le framework **Flask**[cite: 134, 176].
* [cite_start]**POO :** Programmation Orientée Objet avec classes (`Agent`, `Message`), héritage et encapsulation[cite: 182, 216].
* [cite_start]**Base de données :** **SQLite3** avec requêtes préparées pour prévenir les injections SQL[cite: 115, 142].
* [cite_start]**Frontend :** HTML5 / CSS3 avec un thème sombre (noir, gris, rouge) et futuriste[cite: 128, 129].

## 📂 Structure du Projet
* `app.py` : Point d'entrée, configuration Flask et enregistrement des Blueprints.
* `/database` : Gestion de la base `shadowcomm.db` et script `db.py`.
* `/models` : Logique métier structurée en classes (User.py, Message.py).
* `/routes` : Blueprints Flask (auth_routes.py, chat_routes.py, main_routes.py).
* `/services` : Module `caesar_cipher.py` pour le chiffrement/déchiffrement.
* `/static` : Fichier `style.css` pour l'identité visuelle de l'agence.
* `/templates` : Interfaces HTML (Accueil, Connexion, Inscription, Chat).

## ⚙️ Installation et Lancement
1. [cite_start]**Environnement :** Créer un environnement virtuel : `python -m venv venv`[cite: 180].
2. **Dépendances :** Installer Flask et Bcrypt : `pip install flask bcrypt`.
3. [cite_start]**Initialisation :** Lancer `python database/db.py` pour créer les tables `users` et `messages`[cite: 116, 118].
4. **Exécution :** Lancer l'agence avec `python app.py`.

## 👥 Collaboration Git
[cite_start]Le projet respecte une structure de branches par fonctionnalité[cite: 154, 273]:
* `main` : Version stable.
* [cite_start]`feat/auth` : Authentification et inscription[cite: 155].
* [cite_start]`feat/chat` : Messagerie et interface[cite: 155].
* [cite_start]`feat/cesar` : Logique de chiffrement[cite: 155].

---
[cite_start]**Note :** Prototype fonctionnel livré pour évaluation selon les critères de l'agence ShadowComm[cite: 158, 274].