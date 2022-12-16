import hashlib
import json
import threading
import time
import uuid

class Block:
    def __init__(self, data, previous_hash):
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate the hash of the block"""
        sha = hashlib.sha256()
        sha.update(self.data.encode('utf-8') + self.previous_hash.encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self, node_id):
        self.node_id = node_id
        self.chain = [self.create_genesis_block()]
        self.peers = set()
        self.lock = threading.Lock()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        return Block("Genesis Block", "0")
    
    def add_block(self, data):
        """Add a new block to the chain"""
        with self.lock:
            previous_block = self.chain[-1]
            new_block = Block(data, previous_block.hash)
            self.chain.append(new_block)
    
    def verify_block(self, block):
        """Verify that the block is valid and correctly links to the previous block"""
        if block.hash != block.calculate_hash():
            return False
        if block.previous_hash != self.chain[-1].hash:
            return False
        return True
    
    def to_json(self):
        """Convert the blockchain to a JSON string"""
        blocks = []
        for block in self.chain:
            blocks.append(block.__dict__)
        return json.dumps({"blocks": blocks}, sort_keys=True, indent=4)
    
    def add_peer(self, peer):
        """Add a new peer to the set of known peers"""
        self.peers.add(peer)
    
    def broadcast(self, message):
        """Send a message to all known peers"""
        for peer in self.peers:
            peer.send_message(message)
    
    def receive_message(self, message):
        """Process a message received from a peer"""
        if message["type"] == "block":
            block = Block(message["data"], message["previous_hash"])
            if self.verify_block(block):
                self.add_block(block)
                self.broadcast({"type": "block", "data": block.data, "previous_hash": block.previous_hash})

class Peer:
    def __init__(self, node_id):
        self.node_id = node_id
        self.peers = set()
        self.received_messages = []
    
    def send_message(self, message):
        """Send a message to all known peers"""
        for peer in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((peer.host, peer.port))
                sock.sendall(json.dumps(message).encode())
            except Exception as e:
                print("Error sending message: {}".format(e))
            finally:
                sock.close()

    def add_peer(self, peer):
        """Add a new peer to the set of known peers"""
        self.peers.add(peer)
    
    def receive_message(self, message):
        """Process a message received from a peer"""
        self.received_messages.append(message)

class P2PNetwork:
    def __init__(self, node_id):
        self.node_id = node_id
        self.blockchain = Blockchain(node_id)
        self.peers = set()
        self.lock = threading.Lock()
    
    def add_peer(self, peer):
        """Add a new peer to the set of known peers"""
        with self.lock:
            self.peers.add(peer)
            self.blockchain.add_peer(peer)
    
    def broadcast(self, message):
        """Send a message to all known peers"""
        with self.lock:
            for peer in self.peers:
                peer.send_message(message)
    
    def receive_message(self, message):
        """Process a message received from a peer"""
        with self.lock:
            self.blockchain.receive_message(message)

def start_network(node_id):
    """Start a P2P network with the given node ID"""
    network = P2PNetwork(node_id)
    server = ServerThread(network)
    client = ClientThread(network)
    server.start()
    client.start()

def create_node(node_id, host, port):
    """Create a new node with the given ID and connect to the specified host and port"""
    peer = Peer(node_id)
    client = Client(host, port, peer)
    client.start()

class ServerThread(threading.Thread):
    def __init__(self, network):
        super().__init__()
        self.network = network
    
    def run(self):
        """Start the server"""
        server = Server(("0.0.0.0", 10000), self.network)
        server.serve_forever()

class ClientThread(threading.Thread):
    def __init__(self, network):
        super().__init__()
        self.network = network
    
    def run(self):
        """Start the client"""
        while True:
            time.sleep(10)
            self.network.broadcast({"type": "ping"})

class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, address, network):
        super().__init__(address, ServerHandler)
        self.network = network

class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """Handle incoming messages"""
        message = json.loads(self.request.recv(1024).decode())
        self.server.network.receive_message(message)

class Client:
    def __init__(self, host, port, peer):
        self.host = host
        self.port = port
        self.peer = peer
    

