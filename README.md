# Mockchain

Simple spool-based blockchain simulation


## Requirements

- Install the `watchdog` package (`pip3 install -r requirements.txt`).
- Create the folder `/var/spool/blockchain` and give yourself the rights necessary to write to it.


## Usage

You can run any number of miners and any number of listeners. Miners try to find blocks, while listeners just passively consume the blockchain and display the current "wallet".

Starting a miner requires you to give it a name:

    python3 miner.py miner1

A listener doesn't need a name:

    python3 listener.py

You can then cause transactions by creating `.transaction` files in `/var/spool/blockchain`:

    echo "miner1>100>miner2>foobar" >/var/spool/blockchain/foobar.transaction

This will cause 100 $currency to be transfered from miner1 to miner2, assuming they have sufficient funds.

There is a third script that you can run (once is enough):

    python3 cleanup.py

This will periodically remove transaction and block files.

## To Do

- Signed transactions
