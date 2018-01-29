"""A single node to mine blocks."""
from time import sleep
from watchdog.observers import Observer
from lib import SpoolHandler
from miner import Miner

SPOOL_DIR = "/var/spool/blockchain/"


class Listener(Miner):
    """Passive listener"""

    def run(self):
        """Run forever, trying to find blocks"""
        while True:
            if self.block_queue:
                self.handle_blocks()
            sleep(1)

    def print_wallet(self):
        print("Wallet:")
        for who in self.wallet:
            print(who, self.wallet[who], sep="\t")
        print()


if __name__ == '__main__':
    listener = Listener()
    observer = Observer()
    observer.schedule(SpoolHandler(listener), SPOOL_DIR)
    observer.start()
    listener.run()
