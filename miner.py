"""A single node to mine blocks."""
import sys
import json
import random
from collections import deque, Counter
from watchdog.observers import Observer
from lib import (
    GENESIS,
    verify_blockchain,
    try_block,
    _HASH,
    _INFO,
    REWARD,
    SpoolHandler,
)

SPOOL_DIR = "/var/spool/blockchain/"


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
        pass

    def print_blockchain(self):
        for i, block in enumerate(self.blockchain):
            print(i, block)


if __name__ == '__main__':
    miner = Miner(sys.argv[1])
    observer = Observer()
    observer.schedule(SpoolHandler(miner), SPOOL_DIR)
    observer.start()
    try:
        miner.run()
    except KeyboardInterrupt:
        pass
    finally:
        miner.print_blockchain()
