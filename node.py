"""A single node to mine blocks."""
import sys
import json
import random
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from lib import GENESIS, verify_block, try_block, _PARENT_HASH, _HASH, _INFO

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

    def run(self):
        """Run forever, trying to find blocks"""
        while True:
            if self.block_queue:
                self.handle_blocks()
            elif self.transaction_queue:
                block = try_block(
                    self.blockchain[-1],
                    self.transaction_queue[0],
                )
                if block:
                    print("I found it!")
                    self.blockchain.append(block)
                    self.send_blockchain()
                    self.transaction_queue.popleft()
            else:
                block = try_block(self.blockchain[-1], "gimme money")
                if block:
                    print("I found it!")
                    self.blockchain.append(block)
                    self.send_blockchain()

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
                print(self.blockchain)
            else:
                print("Invalid blockchain found")
                print(chain)
                print(self.blockchain)


if __name__ == '__main__':
    miner = Miner(sys.argv[1])
    observer = Observer()
    observer.schedule(SpoolHandler(miner), SPOOL_DIR)
    observer.start()
    miner.run()
