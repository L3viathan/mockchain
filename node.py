"""A single node to mine blocks."""
import sys
import json
import random
from collections import deque, Counter
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from lib import (
    GENESIS,
    verify_block,
    try_block,
    _PARENT_HASH,
    _HASH,
    _INFO,
    REWARD,
)

SPOOL_DIR = "/var/spool/blockchain/"


def verify_blockchain(chain):
    """Verify that a blockchain is correct"""
    if chain[0] != GENESIS:
        return False
    for i in range(1, len(chain)-1):
        if not verify_block(chain[i]):
            return False
        if chain[i][_PARENT_HASH] != chain[i-1][_HASH]:
            return False
    return len(chain)


class SpoolHandler(FileSystemEventHandler):
    """Event handler"""
    def __init__(self, miner):
        self.miner = miner

    def on_created(self, event):
        filename = event.src_path
        if filename.endswith(".block"):
            with open(filename) as f:
                data = json.load(f)
                self.miner.block_queue.append(data)
        elif filename.endswith(".transaction"):
            with open(filename) as f:
                data = f.read()
                self.miner.transaction_queue.append(data)


class Miner:
    """A miner."""
    def __init__(self, name=str(random.randint(1, 1000))):
        self.name = name
        self.transaction_queue = deque()
        self.block_queue = deque()
        self.blockchain = [GENESIS]
        self.wallet = Counter()
        self.transactions = set()

    def run(self):
        """Run forever, trying to find blocks"""
        while True:
            if self.block_queue:
                self.handle_blocks()

            if self.transaction_queue:
                transaction = self.transaction_queue[0]
            else:
                transaction = ""

            transaction += "\n>{}>{}>{}\n".format(REWARD, self.name, random.random())
            block = try_block(
                self.blockchain[-1],
                transaction,
            )
            if block:
                print("Found a block:", block[_HASH])
                self.blockchain.append(block)
                self.send_blockchain()
                self.recalculate_wallet()

                if self.transaction_queue:
                    self.transaction_queue.popleft()

    def recalculate_wallet(self):
        self.wallet = Counter()
        self.transactions = set()
        for block in self.blockchain:
            for src, amount, tgt, extra in self.parse_transactions(block[_INFO]):
                if hash((src, amount, tgt, extra)) in self.transactions:
                    print("Skipping transaction")
                    continue
                if src:
                    self.wallet[src] -= amount
                self.wallet[tgt] += amount
                self.transactions.add(hash((src, amount, tgt, extra)))


    def parse_transactions(self, transaction):
        "sarnthil>100>L3viathan>extra"
        got_reward = False
        for line in transaction.split("\n"):
            try:
                source, amount, target, extra = line.split(">")
            except ValueError:
                continue
            amount = int(amount)
            if not (source or got_reward) and REWARD == amount:
                yield None, REWARD, target, extra
            elif self.wallet[source] >= amount:
                yield source, amount, target, extra

    def send_blockchain(self):
        """Send a mined block into spool (sending the entire blockchain)"""
        with open(SPOOL_DIR + self.blockchain[-1][_HASH] + ".block", "w") as f:
            json.dump(self.blockchain, f)

    def handle_blocks(self):
        """Empty the block queue, appending valid blocks"""
        while self.block_queue:
            chain = self.block_queue.pop()
            valid = verify_blockchain(chain)
            if valid:
                if valid > len(self.blockchain):
                    self.blockchain = chain
                    for block in self.blockchain:
                        if block[_INFO] in self.transaction_queue:
                            self.transaction_queue.remove(block[_INFO])
                    self.recalculate_wallet()
                self.print_wallet()
            else:
                print("Invalid blockchain found")
                print(chain)
                print(self.blockchain)

    def print_wallet(self):
        print("Wallet:")
        for who in self.wallet:
            print(who, self.wallet[who], sep="\t")
        print()


if __name__ == '__main__':
    miner = Miner(sys.argv[1])
    observer = Observer()
    observer.schedule(SpoolHandler(miner), SPOOL_DIR)
    observer.start()
    miner.run()
