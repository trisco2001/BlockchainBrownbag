from argparse import ArgumentParser

from Microblock.Server.consensus import ConsensusEngine, NodeEngine, ProofEngine, TransactionEngine
from Microblock.Server.server import Server, BlockchainEngine

parser = ArgumentParser()
parser.add_argument("hostname")
parser.add_argument("port")
arguments = parser.parse_args()

transaction_engine = TransactionEngine()
proof_engine = ProofEngine()
node_engine = NodeEngine()
consensus_engine = ConsensusEngine()

blockchain_engine = BlockchainEngine(
    consensus_engine,
    proof_engine,
    transaction_engine,
    node_engine)

server = Server(
    consensus_engine,
    transaction_engine,
    blockchain_engine,
    proof_engine,
    node_engine
)

server.run(arguments)