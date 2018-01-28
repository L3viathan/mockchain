"""
Common functions
"""
import random
from hashlib import sha256

_PARENT_HASH, _INFO, _FILLER, _HASH = range(4)
REWARD = 10

N = 5


def block_hash(*args):
    """
    Calculate a hash of a block or of a parent hash, info, filler.
    """
    if len(args) == 1:
        block = args[0]
        parent_hash = block[_PARENT_HASH]
        info = block[_INFO]
        filler = block[_FILLER]
    else:
        parent_hash, info, filler = args
    m = sha256()
    m.update(parent_hash.encode("utf-8"))
    m.update(info.encode("utf-8"))
    m.update(filler.encode("utf-8"))
    return m.hexdigest()


def try_block(parent, info):
    """Make a single try of finding a block."""
    filler = str(random.random())
    bhash = block_hash(parent[_HASH], info, filler)
    if bhash[:N] == "0"*N:
        return [parent[_HASH], info, filler, bhash]


def find_block(parent, info):
    """Mine for blocks until finding one."""
    while True:
        block = try_block(parent, info)
        if block:
            return block


def verify_block(block):
    """Verify a block (make sure the hash matches)"""
    if not block[_HASH].startswith("0"*N):
        return False
    return block[_HASH] == block_hash(block)


GENESIS = [
    "Nothing",
    "Am Anfang war das Wort",
    "0.49688992381305275",
    "00000007ab34dc09d01261286b544cd00ca4639acdfbcd9f16ab6204908f63ab",
]
