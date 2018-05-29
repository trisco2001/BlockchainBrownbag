import json
from json import JSONEncoder

import requests

from flask import Flask
from flask import request
from datetime import datetime

from Microblock.Models.block import Block
from Microblock.Server.consensus import NodeEngine, TransactionEngine, ProofEngine, ConsensusEngine, Transaction


class BlockchainEngine(object):
    def __init__(
            self,
            consensus_engine: ConsensusEngine,
            proof_engine: ProofEngine,
            transaction_engine: TransactionEngine,
            node_engine: NodeEngine):
        self.node_engine = node_engine
        self.transaction_engine = transaction_engine
        self.proof_engine = proof_engine
        self.consensus_engine = consensus_engine
        self.blockchain = [self.create_genesis_block()]

    def get_chain(self, find_consensus):
        if find_consensus:
            other_chains = self.find_new_chains()
            self.blockchain = self.consensus_engine.consensus(self.blockchain, other_chains)
        return self.blockchain

    def append(self, mined_block: Block):
        self.blockchain.append(mined_block)

    def create_genesis_block(self):
        # Manually construct a block with
        # index zero and arbitrary previous hash
        proof = self.proof_engine.generate_proof(1)
        genesis_block_data = {
            "proof-of-work": proof,
            "transactions": list(self.transaction_engine.get_transactions())
        }
        return Block(0, datetime.now(), genesis_block_data, "0")

    def find_new_chains(self):
        # Get the blockchains of every other node
        other_chains = {}
        print("Searching peer nodes: {} ".format(self.node_engine.get_nodes()))
        for node_url in self.node_engine.get_nodes():
            chain = None
            try:
                chain = requests.get(node_url + "/blocks")
            except:
                print('Unable to retrieve chain from peer {}'.format(
                    node_url))
                print('Chain: '.format(chain))
            if chain:
                node_chain = []
                # Chains will be returned as json, convert them to objects
                c = json.loads(chain.content.decode('utf-8'))
                for block in c:
                    node_chain.append(Block(
                        block['index'],
                        block['timestamp'],
                        block['data'],
                        block['hash']))
                other_chains[node_url] = node_chain
        return other_chains


class Server:
    def __init__(
            self,
            consensus_engine: ConsensusEngine,
            transaction_engine: TransactionEngine,
            blockchain_engine: BlockchainEngine,
            proof_engine: ProofEngine,
            node_engine: NodeEngine):
        self.node_engine = node_engine
        self.proof_engine = proof_engine
        self.blockchain_engine = blockchain_engine
        self.transaction_engine = transaction_engine
        self.consensus_engine = consensus_engine
        self.node = Flask(__name__)
        self.miner_address = "1234"

    def register(self):
        @self.node.route('/transaction', methods=['POST'])
        def transaction():
            if request.method == 'POST':
                new_txion = request.get_json()
                transaction = Transaction(source=new_txion['from'], destination=new_txion['to'], amount=new_txion['amount'])
                self.transaction_engine.add_transaction(transaction)
                return "Transaction Submission Successful"

        @self.node.route('/mine', methods=['GET'])
        def mine():
            blockchain = self.blockchain_engine.get_chain(find_consensus=True)
            # Get the last proof of work
            last_block = blockchain[len(blockchain) - 1]
            last_proof = last_block.data['proof-of-work']
            # Find the proof of work for the current block being mined
            # Note: The program will hang here until a new
            #       proof of work is found
            proof = self.proof_engine.generate_proof(last_proof)
            # Once we find a valid proof of work, we know we can mine a block so
            # we reward the miner by adding a transaction
            transaction = Transaction(source="network", destination=self.miner_address, amount=1)
            self.transaction_engine.add_transaction(transaction)
            # Now we can gather the data needed to create the new block
            new_block_data = {
                "proof-of-work": proof,
                "transactions": self.transaction_engine.get_transactions()
            }

            new_block_index = last_block.index + 1
            new_block_timestamp = datetime.now()
            last_block_hash = last_block.hash
            # Empty transaction list
            self.transaction_engine.reset_transactions()
            # Now create the new block!
            mined_block = Block(
                new_block_index,
                new_block_timestamp,
                new_block_data,
                last_block_hash
            )
            self.blockchain_engine.append(mined_block)

            def encode_object(z):
                if isinstance(z, Transaction):
                    return (z.source, z.destination, z.amount)
                else:
                    return JSONEncoder.default(JSONEncoder(), o=z)
            # Let the client know we mined a block
            return json.dumps({
                "index": new_block_index,
                "timestamp": str(new_block_timestamp),
                "data": new_block_data,
                "hash": last_block_hash
            }, default=encode_object)

        @self.node.route('/blocks', methods=['GET'])
        def get_blocks():
            chain_to_send = self.blockchain_engine.get_chain(find_consensus=False)
            chain_to_send = list(map(lambda b: {
                "index": b.index,
                "timestamp": str(b.timestamp),
                "data": b.data,
                "hash": b.hash
            }, chain_to_send))
            chain_to_send = json.dumps(chain_to_send, indent=2)
            return chain_to_send

        @self.node.route('/nodes', methods=['POST', 'GET'])
        def nodes():
            if request.method == 'POST':
                self.node_engine.set_nodes(request.get_json())
                return "Node List Updated"
            elif request.method == 'GET':
                return json.dumps(self.node_engine.get_nodes(), indent=2)

    def run(self, arguments):
        self.register()
        self.node.run(host=arguments.hostname, port=arguments.port)