import hashlib
import time
import json
import os
from uuid import uuid4
from flask import Flask, jsonify, request # Ajout de Flask

# --- CONFIGURATION GLOBALE ET ID DU NŒUD ---
NODE_ID = str(uuid4()).replace('-', '')
BLOCK_DATA_DIR = 'blockchain_data' # Répertoire de sauvegarde des blocs

# --- CLASSE BLOCK ---
class Block:
    """Représente un bloc dans la chaîne."""
    def __init__(self, index, transactions, previous_hash, nonce=0, timestamp=None):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calcule le hachage SHA-256 du bloc."""
        # Utilisation de to_dict(include_hash=False) pour une représentation stable du contenu
        block_content = self.to_dict(include_hash=False) 
        block_string = json.dumps(block_content, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, difficulty):
        """Implémente la Proof of Work (Minage)."""
        target_prefix = '0' * difficulty
        
        while self.hash[:difficulty] != target_prefix:
            self.nonce += 1
            self.hash = self.calculate_hash()
            
        return self.hash

    def to_dict(self, include_hash=True):
        """Retourne la représentation en dictionnaire pour le stockage/réseau."""
        block_dict = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
        }
        if include_hash:
            block_dict['hash'] = self.hash
        return block_dict

    @staticmethod
    def from_dict(block_dict):
        """Crée une instance Block à partir d'un dictionnaire."""
        return Block(
            index=block_dict['index'],
            transactions=block_dict['transactions'],
            previous_hash=block_dict['previous_hash'],
            nonce=block_dict['nonce'],
            timestamp=block_dict['timestamp']
        )


# --- CLASSE BLOCKCHAIN ---
class Blockchain:
    """Gère l'ensemble de la chaîne de blocs et les transactions."""
    def __init__(self, difficulty=4):
        self.chain = []
        self.transactions_en_attente = []
        self.nodes = set()
        self.difficulty = difficulty
        
        os.makedirs(BLOCK_DATA_DIR, exist_ok=True)
        
        if not self._load_chain():
            self.create_genesis_block()

    # --- Méthodes de Persistance ---
    def _save_block(self, block):
        """Sauvegarde un bloc sur le disque."""
        filename = os.path.join(BLOCK_DATA_DIR, f'block_{block.index}.json')
        with open(filename, 'w') as f:
            json.dump(block.to_dict(), f, indent=4)
        print(f"Bloc {block.index} sauvegardé sur le disque.")

    def _load_chain(self):
        """Charge les blocs existants depuis le disque."""
        block_files = sorted([f for f in os.listdir(BLOCK_DATA_DIR) if f.startswith('block_') and f.endswith('.json')])
        if not block_files:
            return False

        temp_chain = []
        for filename in block_files:
            filepath = os.path.join(BLOCK_DATA_DIR, filename)
            with open(filepath, 'r') as f:
                block_dict = json.load(f)
                block = Block.from_dict(block_dict)
                
                # Vérification de l'intégrité (PoW + Hachage)
                if block.hash != block_dict.get('hash'): 
                    print(f"ATTENTION: Bloc {block.index} corrompu sur le disque. Hachage invalide.")
                    return False
                temp_chain.append(block)
                
        self.chain = temp_chain
        if len(self.chain) > 0:
            print(f"Chaîne chargée avec succès. Taille actuelle: {len(self.chain)}")
            return True
        return False

    def create_genesis_block(self):
        """Crée le premier bloc (Genesis Block) et le sauvegarde."""
        genesis_block = Block(0, transactions=[], previous_hash="0")
        genesis_block.proof_of_work(self.difficulty)
        self.chain.append(genesis_block)
        self._save_block(genesis_block)
        print(f"Bloc Genesis créé par le Nœud {NODE_ID[:8]}...")
        
    def get_latest_block(self):
        """Retourne le dernier bloc de la chaîne."""
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        """Crée une nouvelle transaction et l'ajoute à la liste d'attente."""
        self.transactions_en_attente.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.get_latest_block().index + 1

    def mine_block(self):
        """Mine le nouveau bloc en incluant toutes les transactions en attente."""
        if not self.transactions_en_attente and len(self.chain) > 1:
            return None

        # Récompense du mineur
        self.new_transaction(sender="0", recipient=NODE_ID, amount=1)
        
        latest_block = self.get_latest_block()
        new_block = Block(latest_block.index + 1, self.transactions_en_attente, latest_block.hash)
        
        print(f"Minage du bloc {new_block.index} en cours...")
        new_block.proof_of_work(self.difficulty)
        
        # Ajout à la chaîne et sauvegarde
        self.chain.append(new_block)
        self._save_block(new_block) 
        self.transactions_en_attente = []
        return new_block
    
    def is_chain_valid(self, chain_to_validate=None):
        """Vérifie l'intégrité de la chaîne."""
        if chain_to_validate is None:
            chain_to_validate = self.chain
            
        for i in range(1, len(chain_to_validate)):
            current_block = chain_to_validate[i]
            previous_block = chain_to_validate[i-1]

            if current_block.hash != current_block.calculate_hash():
                print(f"Validation Échouée: Hachage du bloc {i} invalide.")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"Validation Échouée: Lien de chaîne rompu au bloc {i}.")
                return False
                
            target_prefix = '0' * self.difficulty
            if current_block.hash[:self.difficulty] != target_prefix:
                 print(f"Validation Échouée: PoW non respecté au bloc {i}.")
                 return False

        return True

    def resolve_conflicts(self, other_chain):
        """Règle de Consensus: La chaîne la plus longue et valide est retenue."""
        max_length = len(self.chain)
        
        if len(other_chain) > max_length and self.is_chain_valid(other_chain):
            self.chain = other_chain
            return True
        
        return False

# --- INTÉGRATION FLASK ET ENDPOINTS API ---

app = Flask(__name__)
blockchain_instance = None 


@app.route('/mine', methods=['GET'])
def mine_api():
    """Endpoint: Lance le minage."""
    mined_block = blockchain_instance.mine_block()
    
    if mined_block:
        response = {
            'message': "Nouveau bloc Forgé et ajouté à la chaîne.",
            'block': mined_block.to_dict()
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': "Aucune transaction en attente. Pas de minage."}), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction_api():
    """Endpoint: Soumet une nouvelle transaction à la file d'attente."""
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Erreur: Champs manquants (sender, recipient, amount)', 400

    index = blockchain_instance.new_transaction(values['sender'], values['recipient'], values['amount'])
    
    response = {'message': f'La transaction sera ajoutée au Bloc {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    """Endpoint: Affiche la chaîne complète."""
    chain_data = [block.to_dict() for block in blockchain_instance.chain]

    response = {
        'chain': chain_data,
        'length': len(chain_data),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """Endpoint: Enregistre de nouveaux nœuds pour la découverte réseau."""
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return "Erreur: Veuillez fournir une liste de nœuds valides.", 400

    for node in nodes:
        blockchain_instance.nodes.add(node)
        
    response = {
        'message': 'Nouveaux nœuds enregistrés',
        'total_nodes': list(blockchain_instance.nodes),
    }
    return jsonify(response), 201

# --- LANCEMENT DU SERVEUR ---

if __name__ == "__main__":
    # La blockchain est initialisée ici
    blockchain_instance = Blockchain(difficulty=4) 
    
    print("\n" + "=" * 60)
    print("SERVEUR DE NŒUD BLOCKCHAIN ACTIF (EMSI Prototype)")
    print(f"ID du Nœud: {NODE_ID[:8]} | Chaîne : {len(blockchain_instance.chain)} blocs")
    print("URLs d'accès : http://0.0.0.0:5000/")
    print("Endpoints: /chain (GET), /mine (GET), /transactions/new (POST)")
    print("=" * 60)
    
    # Lancement du serveur (accessible depuis l'extérieur du réseau local grâce à '0.0.0.0')
    app.run(host='0.0.0.0', port=5000)