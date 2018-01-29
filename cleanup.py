"""A single node to mine blocks."""
import os
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SPOOL_DIR = "/var/spool/blockchain/"


class CleanupHandler(FileSystemEventHandler):
    """Event handler"""
    def on_created(self, event):
        filename = event.src_path
        sleep(1)
        os.remove(filename)


if __name__ == '__main__':
    observer = Observer()
    observer.schedule(CleanupHandler(), SPOOL_DIR)
    observer.start()
    while True:
        sleep(1)
