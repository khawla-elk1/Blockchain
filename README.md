 🔗
Introduction
Ce projet est une implémentation éducative et fonctionnelle d'une Mini-Blockchain développée en Python. Il simule le comportement d'un nœud de réseau décentralisé, intégrant les trois piliers fondamentaux de la technologie blockchain :

Immuabilité via le hachage cryptographique (SHA-256).

Sécurité via un mécanisme de consensus (Proof of Work).

Réseau et interaction via une API Web (Flask).

Ce prototype met l'accent sur la sécurité des données et le fonctionnement d'une architecture distribuée.

⚙️ Architecture du Projet
Le projet est structuré autour de deux classes principales et d'un serveur d'API :

1. Classes Core (Block et Blockchain)
Block : Contient l'index, le timestamp, la liste des transactions, le hachage du bloc précédent (previous_hash), et le nonce (nombre utilisé pour le minage).

Blockchain : Gère la chaîne de blocs (le registre), la file d'attente des transactions non validées (transactions_en_attente), le mécanisme de Proof-of-Work, et la persistance des données sur disque (blockchain_data/).

2. API Réseau (Flask)
Une API REST permet à des clients externes (utilisateurs, autres nœuds) d'interagir avec ce nœud via HTTP, simulant un réseau décentralisé.

🚀 Démarrage Rapide
Prérequis
Python 3.x

Les packages Flask et requests.

1. Installation des Dépendances
Ouvrez votre terminal dans le répertoire du projet et exécutez :

Bash

pip install Flask requests
2. Lancement du Nœud Serveur
Lancez le script principal. Laissez ce terminal ouvert, car il héberge le serveur du nœud :

Bash

python mini_blockchain.py
Le serveur démarrera sur le port 5000 (ex: http://127.0.0.1:5000/).

💻 Utilisation de l'API (Endpoints)
L'interaction avec la blockchain se fait via les endpoints HTTP. L'outil recommandé pour les tests est Postman (ou curl via le terminal).

1. Créer une Nouvelle Transaction (Méthode POST)
Ajoute une transaction à la liste d'attente (transactions_en_attente).

Endpoint : /transactions/new

Méthode : POST

Corps de la requête (JSON) :

JSON

{
    "sender": "Khawla",
    "recipient": "EMSI",
    "amount": 100
}
2. Miner le Prochain Bloc (Méthode GET)
Déclenche le processus de Proof of Work (PoW) pour valider toutes les transactions en attente.

Endpoint : /mine

Méthode : GET

Action : Le nœud résout le puzzle PoW, ajoute le bloc à la chaîne, et s'attribue la récompense de minage.

3. Afficher la Chaîne Complète (Méthode GET)
Permet de synchroniser la chaîne ou d'inspecter l'état du registre.

Endpoint : /chain

Méthode : GET

🛡️ Sécurité et Immuabilité
1. Rôle du Hachage (Sécurité)
Chaque bloc contient le hachage du bloc précédent. Si un attaquant modifie une seule transaction dans un bloc ancien, le hachage de ce bloc change. La vérification ultérieure de la chaîne échoue immédiatement, car le lien cryptographique est rompu.

2. Rôle du Proof-of-Work (Économie/Résistance)
Le minage oblige le nœud à effectuer un travail de calcul coûteux (trouver un nonce pour que le hachage commence par 0000). Pour falsifier une transaction, l'attaquant devrait refaire le PoW pour le bloc falsifié ET pour tous les blocs suivants, rendant l'attaque impraticable sans un pouvoir de calcul majoritaire (l'attaque des 51%).

🛠️ Contribution
Ce projet est conçu comme un prototype éducatif. Les contributions pour le rendre plus robuste, notamment en ajoutant un algorithme de Consensus complet (utilisation de l'endpoint /nodes/register et resolve_conflicts), sont les bienvenues !

Développé par : Khawla El Khassibi (Étudiant, 5ème année EMSI - Marrakech)
