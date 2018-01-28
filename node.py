"""A single node to mine blocks."""
import json
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from lib import GENESIS, verify_block, try_block, _PARENT_HASH, _HASH, _INFO

transaction_queue = deque()
block_queue = deque()
blockchain = [GENESIS]
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
    def on_created(self, event):
        filename = event.src_path
        if filename.endswith(".block"):
            with open(filename) as f:
                data = json.load(f)
                block_queue.append(data)
        elif filename.endswith(".transaction"):
            with open(filename) as f:
                data = f.read()
                transaction_queue.append(data)


def send_blockchain():
    """Send a mined block into spool (sending the entire blockchain)"""
    with open(SPOOL_DIR + blockchain[-1][_HASH] + ".block", "w") as f:
        json.dump([list(block) for block in blockchain], f)


def handle_blocks():
    """Empty the block queue, appending valid blocks"""
    global blockchain
    while block_queue:
        chain = block_queue.pop()
        valid = verify_blockchain(chain)
        if valid:
            if valid > len(blockchain):
                blockchain = chain
                for block in blockchain:
                    if block[_INFO] in transaction_queue:
                        transaction_queue.remove(block[_INFO])
            print(blockchain)
        else:
            print("Invalid blockchain found")
            print(chain)
            print(blockchain)


def run():
    """Run forever, trying to find blocks"""
    while True:
        if block_queue:
            handle_blocks()
        elif transaction_queue:
            block = try_block(blockchain[-1], transaction_queue[0])
            if block:
                print("I found it!")
                blockchain.append(block)
                send_blockchain()
                transaction_queue.popleft()
        else:
            block = try_block(blockchain[-1], "gimme money")
            if block:
                print("I found it!")
                blockchain.append(block)
                send_blockchain()


if __name__ == '__main__':
    observer = Observer()
    observer.schedule(SpoolHandler(), SPOOL_DIR)
    observer.start()
    run()
