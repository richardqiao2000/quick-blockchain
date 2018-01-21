from time import time
import json
import hashlib
from uuid import uuid4
from textwrap import dedent
from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests
import sys

class Blockchain(object):
  def __init__(self):
    self.chain = []
    self.current_transactions = []
    # Create the genisis block
    self.new_block(previous_hash = 1, proof=100)
    self.nodes = set()

  def new_block(self, proof, previous_hash=None):
    """
    Create a new block in the Blockchain
    :param proof: <int> The proof given by the Proof of Work Algoorithm
    :param previous_hash: (Optional) <str> Hash of previous Block
    :return:  <dict> New Block
    """
    block = {
      'index': len(self.chain) + 1,
      'timestamp': time(),
      'transactions': self.current_transactions,
      'proof': proof,
      'previous_hash': previous_hash
    }
    self.current_transactions = []
    self.chain.append(block)
    return block


  def new_transaction(self, sender, recipient, amount):
    """
    Creates a new transaction to go into the next mined block
    :param sender:  <str> Address of the Sender
    :param recipient: <str> Address of the Recipient
    :param amount:  <str> Amount
    :return:  <int> The index of the Block that will hold this transaction
    """
    self.current_transactions.append({
      'sender': sender,
      'recipient': recipient,
      'amount': amount,
    })
    return self.last_block['index'] + 1

  @property
  def last_block(self):
    return self.chain[-1]

  @staticmethod
  def hash(block):
    """
    Create a SHA-256 hash of a Block
    :param block: <dict> Block
    :return:  <str>
    """
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

  def proof_of_work(self, last_proof):
    """
    Simple proof of work algorithm
     - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
     - p is the previous proof, and p' is the new proof
    :param last_proof: <int>
    :return:  <int>
    """
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
      proof += 1
    return proof

  def valid_proof(self, last_proof, proof):
    """
    Validate the proof: Does hash(last_proof, proof) contain 4 leading zeroes?
    :param last_proof: <int> Previous proof
    :param proof: <int> Current proof
    :return:  <bool> True if correct, False if not
    """
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"

  def register_node(self, address):
    """
    Add a new node to the list of nodes
    :param address: <str> address of node. eg: http://192.168.1.111:5000
    :return:  None
    """
    parse_url = urlparse(address)
    self.nodes.add(parse_url.netloc)

  def valid_chain(self, chain):
    """
    determine if a given blockchain is valid
    :param chain: <list> a blockchain
    :return:  <bool> True if valid, False if not
    """
    last_block = chain[0]
    current_index = 1
    while current_index < len(chain):
      block = chain[current_index]
      print(f'{last_block}')
      print(f'{block}')
      print("\n---------\n")
      if block['previous_hash'] != self.hash(last_block):
        return False
      if not self.valid_proof(last_block['proof'], block['proof']):
        return False
      last_block = block
      current_index += 1
    return True

  def resolve_conflicts(self):
    """
    this is our consesus algorithm, it resolves conflicts
    by replacing our chain with the longest one in the network.
    :return: <bool> True if our chain was replaced, False if not
    """
    neighbours = self.nodes
    new_chain = None
    max_length = len(self.chain)
    for node in neighbours:
      response = requests.get(f'http://{node}/chain')
      if response.status_code == 200:
        length = response.json()['length']
        chain = response.json()['chain']
        if length > max_length and self.valid_chain(chain):
          max_length = length
          new_chain = chain
    if new_chain:
      self.chain = new_chain
      return True
    return False




app = Flask(__name__)
node_identfifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
  last_block = blockchain.last_block
  last_proof = last_block['proof']
  proof = blockchain.proof_of_work(last_proof)
  blockchain.new_transaction(
    sender="0",
    recipient=node_identfifier,
    amount=1
  )
  previous_hash = blockchain.hash(last_block)
  block = blockchain.new_block(proof, previous_hash)
  response={
    'message': "New block forged",
    'index': block['index'],
    'transactions': block['transactions'],
    'proof': block['proof'],
    'previous_hash': block['previous_hash']
  }
  return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
  values = request.get_json()
  required = ['sender', 'recipient', 'amount']
  if not all(k in values for k in required):
    return 'Missing values', 400
  index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
  response = {'message': f'Transaction will be added to Block {index}'}
  return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
  response = {
    'chain': blockchain.chain,
    'length': len(blockchain.chain)
  }
  return jsonify(response), 200

"""
{
 "sender": "my address",
 "recipient": "someone else's address",
 "amount": 5
}
"""
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
  values = request.get_json()
  nodes = values.get('nodes')
  if nodes is None:
    return "Error: please supply a valid list of nodes", 400
  for node in nodes:
    blockchain.register_node(node)
  response = {
    'message': "New nodes have been added",
    'total_nodes': list(blockchain.nodes)
  }
  return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
  replaced = blockchain.resolve_conflicts()
  if replaced:
    response = {
      'message': 'Our chain was replaced',
      'new_chain': blockchain.chain
    }
  else:
    response = {
      'message': 'Our chain is authoritative',
      'chain': blockchain.chain
    }
  return jsonify(response), 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(sys.argv[1]))