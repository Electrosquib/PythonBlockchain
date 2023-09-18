import json
import rsa
import binascii
import requests
import hashlib
import datetime

class Miner:
    def __init__(self, num_zeros):
        self.url = "http://127.0.0.1:5000"
        self.num_zeroes = num_zeros
        

    def verify_transaction(self, transaction):
        """
        Authenticates a transaction based on the contents and public key of sender
        transaction (str): "{transaction: {...}, signature: {...}}"
        """
        # signature = transaction.split("signature\": \"")[1][:-2].encode("cp437")
        try:
            transaction = json.loads(transaction)
        except:
            pass
        message = transaction["transaction"]
        sender_pubkey = rsa.PublicKey.load_pkcs1("-----BEGIN RSA PUBLIC KEY-----\n"+message["sender"]+"\n-----END RSA PUBLIC KEY-----") #Gets public key from transaction info
        signature = binascii.unhexlify(transaction["signature"].encode("utf-8"))
        try:
            return bool(rsa.verify(json.dumps(message).encode("utf-8"), signature, sender_pubkey))
        except rsa.pkcs1.VerificationError:
            return False
        

    def check_for_double_spending(self, transaction, blockchain=None):
        """
        Returns a boolean indicating if sender has enough money to complete transaction (false - they dont have enough, true - they do)
        """
        transaction = json.loads(transaction)
        sender = transaction["transaction"]["sender"]
        amount = transaction["transaction"]["amount"]
        
        # Retrieve blockchain from API or parameter
        if not blockchain:
            blockchain = json.loads(requests.get(self.url+"/blockchain").text)
        self.blockchain = blockchain
        # Get a list of the sender's previous money transfers (if not block transaction)
        send_list = []
        for block in self.blockchain:
            for count, t in enumerate(self.blockchain[block]["transactions"]):
                if count != 0:
                    if t["transaction"]["sender"] == sender:
                        send_list.append(t["transaction"]["amount"])
        out = sum(send_list)

        # Get a list of the sender's previous receives
        receive_list = []
        for block in self.blockchain:
            for count, t in enumerate(self.blockchain[block]["transactions"]):
                if count != 1:
                    if t["transaction"]["recipient"] == sender:
                        receive_list.append(t["transaction"]["amount"])
                    
        inn = sum(receive_list)
        
        # Return boolean indicating if a transaction is valid
        balance = inn-out
        return balance - int(amount) > 0

    def proof_of_work(self, block, prevhash):
        old_block = block
        new_block = "["
        for t in block:
            new_block+=t+","
        new_block = new_block[:-1]+"]"
        block = new_block
        m = prevhash+block
        hash = hashlib.sha256(m.encode("utf-8")).hexdigest()
        num = 0
        while not hash.startswith("0"*self.num_zeroes):
            ma = m + str(num)
            hash = hashlib.sha256(ma.encode("utf-8")).hexdigest()
            num += 1
        num -= 1
        self.num = num
        old_block.append(num)
        self.pow_block = "["+''.join(str(e)+", " for e in old_block)[:-2]+"]"
        return num

    def mine_block(self, public_key):
        self.block = json.loads(requests.get(self.url+"/current-block").text)[:-1]
        time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        #signature = rsa.sign(json.dumps({"transaction": {"timestamp": time, "recipient":self.pubkey, "amount": "50"}}).encode("utf-8"), time, "SHA-256")
        new_block = [json.dumps({"transaction": {"timestamp": time, "recipient":public_key, "amount": "50"}, "signature": time})]
        for transaction in self.block:
            if self.verify_transaction(transaction) and self.check_for_double_spending(transaction):
                new_block.append(transaction)

        self.block = new_block
        pow = self.blockchain[str(len(self.blockchain))]["pow"]
        return self.proof_of_work(self.block, pow)

    def verify_block(self, block, blockchain):
        new_block = []
        block = block[0]
        removed = 0
        for count, transaction in enumerate(blockchain):
            # Verify transactions 
            if count != 0:
                if self.verify_transaction(transaction) and self.check_for_double_spending(transaction, blockchain):
                    # Check for duplicate transactions
                    if block.count(transaction) > 1:
                        new_block.append(transaction)
                    else:
                        block.remove(transaction)
                else:
                    removed += 1
            else:
                # reward_transaction = json.loads(transaction)
                # message = reward_transaction["transaction"]
                # ver = rsa.verify(json.dumps(message).encode("utf-8"), reward_transaction["signature"], message["timestamp"])
                # if ver:
                #     new_block.append(reward_transaction)
                print("Block Reward is valid")

        print(f"Removed {len(block)-1} Invalid Transactions")
        return new_block == block

    def post_block(self):
        return requests.post(self.url+"/add-block", data=self.pow_block)
