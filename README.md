# PythonBlockchain
A proof of concept blockchain written from scratch in Python. It hosts an API which both clients and miners use to create and verify transactions.
Required Modules:
    - flask
    - rsa
    - datetime
    - binascii
    - requests

Instructions:
    1: Run the main API
        a) Run "python Blockchain.py" in a terminal window running in this directory
        b) Will not work if there is another service running on http://127.0.0.1:5000
        c) Only works with http, not https
    2: Run the client API
        a) Run "python Client.py" in a terminal window running in this directory
        b) Follow on-screen instructions on how to generate a new key-pair or use a pre-built one (billy, bob, or jenny)
        c) Select option to perform in the CLI menu
    3: Mine block 
        a) After a number of transactions have been executed, they need to be verified and a PoW has to be created. This ensures that as long as the 
            network consists of at least 51% honest mining nodes, the system will be secure. 
        b) Run "miner_client.py" to mine the current block

Note: New blocks must be mined for currency to be introduced into the system.
