import hashlib
import json

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
    def __init__(self, nodes=[]):
        self.chain = [self.create_genesis_block()]
        self.nodes = nodes
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        return Block("Genesis Block", "0")
    
    def add_block(self, data):
        """Add a new block to the chain"""
        previous_block = self.chain[-1]
        new_block = Block(data, previous_block.hash)
        for node in self.nodes:
            if not node.verify_block(new_block):
                print("Block rejected by node: {}".format(node))
                return
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

class Node:
    def __init__(self, blockchain):
        self.blockchain = blockchain
    
    def verify_block(self, block):
        """Verify that the block is valid and correctly links to the previous block in the chain"""
        return self.blockchain.verify_block(block)
