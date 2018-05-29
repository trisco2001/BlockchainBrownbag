class ConsensusEngine:
    def consensus(self, blockchain, other_chains):
        # Get the blocks from other nodes
        print("Found other {} chains".format(len(other_chains)))
        longest_chain = blockchain
        # If our chain isn't longest, then we store the longest chain
        for node, chain in other_chains.items():
            if len(longest_chain) < len(chain):
                print(
                    "Replacing blockchain with chain from node: {} ".format(
                        node))
                longest_chain = chain
        # If the longest chain isn't ours, then we stop mining and set
        # our chain to the longest one
        return longest_chain


class Transaction:
    def __init__(self, source: str, destination: str, amount: int):
        self.source = source
        self.destination = destination
        self.amount = amount




class TransactionEngine:
    def __init__(self):
        self.transactions = []

    def get_transactions(self):
        return list(self.transactions)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def reset_transactions(self):
        self.transactions.clear()


class ProofEngine:
    def generate_proof(self, last_proof_value):
        incrementor = last_proof_value + 1
        while not (incrementor % 9 == 0 and incrementor % last_proof_value == 0):
            incrementor += 1

        return incrementor


class NodeEngine:
    def __init__(self):
        self.nodes = []

    def set_nodes(self, nodes):
        self.nodes = nodes

    def get_nodes(self):
        return self.nodes

